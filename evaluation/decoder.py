"""
Decoder
=======
Reads the population activity of each module and produces task outputs.

Uses ridge regression (analytically solved) to fit linear readout weights
from concatenated PFC + HC activity to class labels.

Supports two tasks:
  evaluate_dms()  — identity decoding (Cat vs Dog)
  evaluate_toj()  — temporal order decoding (which stimulus came first)
"""

import numpy as np
from typing import Sequence


class Decoder:
    """Linear population-vector decoder with ridge-regression readout weights."""

    def __init__(self, n_pfc: int, n_hc: int, n_classes: int = 2, seed: int = 99):
        self.n_pfc     = n_pfc
        self.n_hc      = n_hc
        self.n_classes = n_classes
        self.rng       = np.random.default_rng(seed)

        self.W_pfc = self.rng.normal(0, 0.1, (n_classes, n_pfc))
        self.W_hc  = self.rng.normal(0, 0.1, (n_classes, n_hc))

        self.predictions: list = []
        self.targets    : list = []

    # ── fitting ───────────────────────────────────────────────────────────────

    def fit(self, pfc_activity: np.ndarray,
            hc_activity: np.ndarray,
            labels: np.ndarray,
            alpha: float = 1e-3) -> None:
        """
        Fit linear readout weights via ridge regression.

        W = (X^T X + αI)^{-1} X^T Y

        Parameters
        ----------
        pfc_activity : (T, n_pfc)
        hc_activity  : (T, n_hc)
        labels       : (T,) integer class labels
        alpha        : L2 regularisation coefficient
        """
        Y = np.zeros((len(labels), self.n_classes))
        for i, lbl in enumerate(labels):
            if lbl is not None and 0 <= int(lbl) < self.n_classes:
                Y[i, int(lbl)] = 1.0

        X      = np.concatenate([pfc_activity, hc_activity], axis=1)
        n_feat = X.shape[1]
        A      = X.T @ X + alpha * np.eye(n_feat)
        B      = X.T @ Y
        W_all  = np.linalg.solve(A, B).T    # (n_classes, n_feat)

        self.W_pfc = W_all[:, :self.n_pfc]
        self.W_hc  = W_all[:, self.n_pfc:]

    # ── decoding ──────────────────────────────────────────────────────────────

    def decode(self, pfc_spikes: np.ndarray,
               hc_spikes: np.ndarray) -> tuple[int, np.ndarray]:
        """Decode class from population activity."""
        logits = self.W_pfc @ pfc_spikes + self.W_hc @ hc_spikes
        return int(np.argmax(logits)), logits

    def decode_batch(self, pfc_activity: np.ndarray,
                     hc_activity: np.ndarray) -> np.ndarray:
        """Decode a full (T, n) activity matrix → (T,) predictions."""
        logits = pfc_activity @ self.W_pfc.T + hc_activity @ self.W_hc.T
        return np.argmax(logits, axis=1)

    # ── evaluation metrics ────────────────────────────────────────────────────

    @staticmethod
    def accuracy(predictions: np.ndarray, targets: np.ndarray) -> float:
        mask = targets >= 0
        if mask.sum() == 0:
            return 0.0
        return float((predictions[mask] == targets[mask]).mean())

    @staticmethod
    def pattern_similarity(decoded_activity: np.ndarray,
                           target_pattern: np.ndarray) -> float:
        """Cosine similarity between decoded vector and target."""
        a = decoded_activity.astype(float)
        b = target_pattern.astype(float)
        denom = np.linalg.norm(a) * np.linalg.norm(b) + 1e-8
        return float(np.dot(a, b) / denom)

    # ── DMS evaluation ────────────────────────────────────────────────────────

    def evaluate_dms(self, training_data: dict) -> dict:
        """
        Evaluate on DMS training run. Extracts test-phase windows,
        averages activity per trial, and computes accuracy.
        """
        schedule   = training_data["schedule"]
        pfc_spikes = training_data["pfc_spikes"]
        hc_spikes  = training_data["hc_spikes"]
        rewards    = training_data["rewards"]

        test_phases = [(s, e, pid) for (ph, s, e, pid) in schedule
                       if ph == "test" and pid is not None]

        per_trial    = []
        pfc_test_all = []
        hc_test_all  = []
        labels_all   = []

        for i, (ts, te, test_pid) in enumerate(test_phases):
            pfc_w = pfc_spikes[ts:te].mean(axis=0)
            hc_w  = hc_spikes[ts:te].mean(axis=0)
            pred, logits = self.decode(pfc_w, hc_w)

            per_trial.append(dict(
                trial   = i,
                target  = test_pid,
                pred    = pred,
                correct = (pred == test_pid),
                reward  = rewards[ts:te].max(),
                logits  = logits,
            ))
            pfc_test_all.append(pfc_w)
            hc_test_all.append(hc_w)
            labels_all.append(test_pid)

        if per_trial:
            pred_arr = self.decode_batch(np.array(pfc_test_all),
                                         np.array(hc_test_all))
            acc = self.accuracy(pred_arr, np.array(labels_all))
        else:
            acc = 0.0

        return dict(accuracy=acc, per_trial=per_trial, n_trials=len(per_trial))

    # ── TOJ evaluation ────────────────────────────────────────────────────────

    def evaluate_toj(self, toj_data: dict) -> dict:
        """
        Evaluate Temporal Order Judgment accuracy.

        Reads HC + PFC activity during the blank window (after both stimuli
        have been presented). HC's volatile memory (τ=50 ms) retains a
        time-decaying trace: stim_a's imprint is weaker than stim_b's,
        creating an asymmetric pattern that encodes which came first.
        The ridge-regression decoder reads this asymmetry to predict order.

        Requires the decoder to have been fitted on TOJ blank-window activity
        before calling this method (call fit() with blank-phase data and
        toj_labels first).
        """
        schedule   = toj_data["schedule"]
        pfc_spikes = toj_data["pfc_spikes"]
        hc_spikes  = toj_data["hc_spikes"]

        blank_phases = [(s, e, label)
                        for (ph, s, e, pid, label) in schedule
                        if ph == "blank"]

        per_trial  = []
        pfc_all    = []
        hc_all     = []
        lbl_all    = []

        for i, (bs, be, label) in enumerate(blank_phases):
            pfc_w = pfc_spikes[bs:be].mean(axis=0)
            hc_w  = hc_spikes[bs:be].mean(axis=0)
            pred, logits = self.decode(pfc_w, hc_w)

            per_trial.append(dict(
                trial   = i,
                target  = label,
                pred    = pred,
                correct = (pred == label),
                logits  = logits,
            ))
            pfc_all.append(pfc_w)
            hc_all.append(hc_w)
            lbl_all.append(label)

        if per_trial:
            pred_arr = self.decode_batch(np.array(pfc_all), np.array(hc_all))
            acc      = self.accuracy(pred_arr, np.array(lbl_all))
        else:
            acc = 0.0

        return dict(accuracy=acc, per_trial=per_trial, n_trials=len(per_trial))
