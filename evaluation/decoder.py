"""
Decoder
=======
Reads the population activity of each module and produces task outputs.

Implements the evaluation framework from the proposal:
  - Spike pattern → class label (Cat / Dog)
  - Population vector decoding
  - Comparison of decoder output vs. ground-truth pattern
  - Accuracy and processing-flow metrics
"""

import numpy as np
from typing import Sequence


class Decoder:
    """
    Linear population-vector decoder with optional learned readout weights.
    """

    def __init__(self, n_pfc: int, n_hc: int, n_classes: int = 2, seed: int = 99):
        self.n_pfc      = n_pfc
        self.n_hc       = n_hc
        self.n_classes  = n_classes
        self.rng        = np.random.default_rng(seed)

        # readout weight matrices (trained by linear regression on training data)
        # initialised randomly; call fit() after training
        self.W_pfc = self.rng.normal(0, 0.1, (n_classes, n_pfc))
        self.W_hc  = self.rng.normal(0, 0.1, (n_classes, n_hc))

        # result accumulators
        self.predictions  = []
        self.targets      = []

    # ── fitting ───────────────────────────────────────────────────────────────

    def fit(self, pfc_activity: np.ndarray,
            hc_activity: np.ndarray,
            labels: np.ndarray,
            alpha: float = 1e-3) -> None:
        """
        Fit linear readout weights (ridge regression).

        Parameters
        ----------
        pfc_activity : (T, n_pfc) training activity
        hc_activity  : (T, n_hc)  training activity
        labels       : (T,) integer class labels
        alpha        : float  L2 regularisation
        """
        # one-hot encode labels
        Y = np.zeros((len(labels), self.n_classes))
        for i, lbl in enumerate(labels):
            if lbl is not None and 0 <= int(lbl) < self.n_classes:
                Y[i, int(lbl)] = 1.0

        # combined feature matrix
        X = np.concatenate([pfc_activity, hc_activity], axis=1)   # (T, n_pfc+n_hc)
        n_feat = X.shape[1]

        # ridge regression:  W = (X^T X + αI)^{-1} X^T Y
        A = X.T @ X + alpha * np.eye(n_feat)
        B = X.T @ Y
        W_all = np.linalg.solve(A, B).T    # (n_classes, n_feat)

        self.W_pfc = W_all[:, :self.n_pfc]
        self.W_hc  = W_all[:, self.n_pfc:]

    # ── decoding ──────────────────────────────────────────────────────────────

    def decode(self, pfc_spikes: np.ndarray,
               hc_spikes: np.ndarray) -> tuple[int, np.ndarray]:
        """
        Decode class from population activity.

        Returns
        -------
        pred_class : int  argmax of logit vector
        logits     : (n_classes,) raw decoder outputs
        """
        logits = self.W_pfc @ pfc_spikes + self.W_hc @ hc_spikes
        return int(np.argmax(logits)), logits

    def decode_batch(self, pfc_activity: np.ndarray,
                     hc_activity: np.ndarray) -> np.ndarray:
        """Decode a full (T, n) activity matrix → (T,) predictions."""
        logits = (pfc_activity @ self.W_pfc.T
                  + hc_activity @ self.W_hc.T)
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
        """
        Cosine similarity between decoded population vector and target.
        Measures how well the chip reconstructs the input pattern.
        """
        a = decoded_activity.astype(float)
        b = target_pattern.astype(float)
        denom = np.linalg.norm(a) * np.linalg.norm(b) + 1e-8
        return float(np.dot(a, b) / denom)

    def evaluate_dms(self, training_data: dict) -> dict:
        """
        Evaluate decoder on the DMS training run.

        Extracts test-phase windows from the schedule and computes
        accuracy, pattern similarity, and per-trial results.
        """
        schedule    = training_data["schedule"]
        pfc_spikes  = training_data["pfc_spikes"]
        hc_spikes   = training_data["hc_spikes"]
        rewards     = training_data["rewards"]

        test_phases  = [(s, e, pid) for (ph, s, e, pid) in schedule
                        if ph == "test" and pid is not None]
        sample_phases = [(s, e, pid) for (ph, s, e, pid) in schedule
                         if ph == "sample" and pid is not None]

        per_trial = []
        labels_all = []
        pfc_test_all = []
        hc_test_all  = []

        for i, (ts, te, test_pid) in enumerate(test_phases):
            # average activity over test window
            pfc_window = pfc_spikes[ts:te].mean(axis=0)
            hc_window  = hc_spikes[ts:te].mean(axis=0)

            pred, logits = self.decode(pfc_window, hc_window)
            trial_reward = rewards[ts:te].max()

            per_trial.append(dict(
                trial    = i,
                target   = test_pid,
                pred     = pred,
                correct  = (pred == test_pid),
                reward   = trial_reward,
                logits   = logits,
            ))
            labels_all.append(test_pid)
            pfc_test_all.append(pfc_window)
            hc_test_all.append(hc_window)

        if per_trial:
            pfc_arr  = np.array(pfc_test_all)
            hc_arr   = np.array(hc_test_all)
            lbl_arr  = np.array(labels_all)
            pred_arr = self.decode_batch(pfc_arr, hc_arr)
            acc      = self.accuracy(pred_arr, lbl_arr)
        else:
            acc = 0.0

        return dict(
            accuracy    = acc,
            per_trial   = per_trial,
            n_trials    = len(per_trial),
        )
