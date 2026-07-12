"""
STDP Trainer
============
Manages the self-supervised, adaptive training loop on the memristive modules.

Training pipeline:
  1. Encode synthetic spikes (via NEF population coding)
  2. Feed through HC → PFC → OFC → EC modules with online STDP
  3. BG selects action each step from neural utility signals
  4. After DMS training: freeze non-volatile PFC weights
  5. Run TOJ training on the same system to test generalisation

Tasks:
  train_dms()  — Delayed Match-to-Sample
  train_toj()  — Temporal Order Judgment
"""

import numpy as np
from typing import Callable
import config


class STDPTrainer:
    """Runs the full self-supervised training loop."""

    def __init__(self, hc, pfc, ofc, ec, controller, spike_gen,
                 dt: float = config.DT):
        self.hc        = hc
        self.pfc       = pfc
        self.ofc       = ofc
        self.ec        = ec
        self.ctrl      = controller
        self.spike_gen = spike_gen
        self.dt        = dt

        self.loss_history   = []
        self.reward_history = []
        self.step_count     = 0

    # ── DMS training ─────────────────────────────────────────────────────────

    def train_dms(self, n_steps: int,
                  callback: Callable | None = None) -> dict:
        """
        Run Delayed Match-to-Sample training for n_steps steps.

        Records HC, PFC, OFC, EC activity, TD-errors, rewards, and the
        BG action selected at each step (for comparing BG decisions against
        the explicit phase ground truth).

        Returns
        -------
        dict: hc_spikes, pfc_spikes, ofc_spikes, ec_activity, rewards,
              td_errors, schedule, bg_actions, bg_utilities
        """
        sg       = self.spike_gen
        schedule = sg.dms_schedule(n_steps)
        phase_map = self._build_phase_map(schedule, n_steps)

        hc_rec    = np.zeros((n_steps, config.N_HC))
        pfc_rec   = np.zeros((n_steps, config.N_PFC))
        ofc_rec   = np.zeros((n_steps, config.N_OFC))
        ec_rec    = np.zeros((n_steps, config.N_EC))
        rewards   = np.zeros(n_steps)
        td_errs   = np.zeros(n_steps)
        bg_acts   = np.full(n_steps, -1, dtype=int)
        bg_utils  = np.zeros((n_steps, 4))

        sample_pattern = 0

        for step in range(n_steps):
            t     = step * self.dt
            phase, pid = phase_map[step]

            if phase == "sample":
                spikes = sg.pattern_spikes(pid, t, noise=0.05)
                sample_pattern = pid
                reward = 0.0

            elif phase == "delay":
                wm     = self.pfc.working_memory
                spikes = sg.delay_activity(t, wm_pattern=wm)
                reward = 0.0
                if self.ctrl._consol_timer == 0.0:
                    self.ctrl.trigger_consolidation()

            elif phase == "test":
                spikes = sg.pattern_spikes(pid, t, noise=0.08)
                reward = 1.0 if (pid == sample_pattern) else -1.0

            else:   # iti
                spikes = sg.delay_activity(t)
                reward = 0.0

            result = self.ctrl.step(self.hc, self.pfc, self.ofc, self.ec,
                                    spikes, reward=reward)

            hc_rec[step]   = result["hc_out"]
            pfc_rec[step]  = result["pfc_out"]
            ofc_rec[step]  = result["ofc_out"]
            ec_rec[step]   = result["ec_out"]
            rewards[step]  = reward
            td_errs[step]  = result["td_error"]
            bg_acts[step]  = result["bg_action"]
            bg_utils[step] = result["bg_utility"]

            novelty = self.ctrl.compute_novelty(spikes, self.pfc.working_memory)
            self.ctrl.ach_attention(novelty)

            self.step_count += 1
            if callback is not None and step % 500 == 0:
                callback(step, result)

        return dict(
            hc_spikes   = hc_rec,
            pfc_spikes  = pfc_rec,
            ofc_spikes  = ofc_rec,
            ec_activity = ec_rec,
            rewards     = rewards,
            td_errors   = td_errs,
            schedule    = schedule,
            bg_actions  = bg_acts,
            bg_utilities = bg_utils,
        )

    # ── TOJ training ──────────────────────────────────────────────────────────

    def train_toj(self, n_steps: int,
                  callback: Callable | None = None) -> dict:
        """
        Run Temporal Order Judgment (TOJ) training for n_steps steps.

        Two stimuli are presented in sequence (stim_a → stim_b). The system
        must report which appeared first, exploiting HC's volatile memory:
        stim_a's imprint in HC decays during stim_b, creating an asymmetric
        population pattern that encodes temporal order.

        No new architecture is added — the same HC/PFC/OFC/EC system generalises
        to this second task via the same NEF representations learned during DMS.

        Returns
        -------
        dict: same keys as train_dms plus 'toj_labels'
        """
        sg       = self.spike_gen
        schedule = sg.toj_schedule(n_steps)
        phase_map = self._build_toj_phase_map(schedule, n_steps)

        hc_rec   = np.zeros((n_steps, config.N_HC))
        pfc_rec  = np.zeros((n_steps, config.N_PFC))
        ofc_rec  = np.zeros((n_steps, config.N_OFC))
        ec_rec   = np.zeros((n_steps, config.N_EC))
        rewards  = np.zeros(n_steps)
        td_errs  = np.zeros(n_steps)
        labels   = np.full(n_steps, -1, dtype=int)
        bg_acts  = np.full(n_steps, -1, dtype=int)
        bg_utils = np.zeros((n_steps, 4))

        for step in range(n_steps):
            t               = step * self.dt
            phase, pid, lbl = phase_map[step]

            if phase in ("stim_a", "stim_b"):
                spikes = sg.pattern_spikes(pid, t, noise=0.05)
                reward = 0.0
                if lbl >= 0:
                    labels[step] = lbl

            elif phase == "blank":
                spikes = sg.delay_activity(t)
                reward = 0.0
                if lbl >= 0:
                    labels[step] = lbl

            else:   # iti
                spikes = sg.delay_activity(t)
                reward = 0.0

            result = self.ctrl.step(self.hc, self.pfc, self.ofc, self.ec,
                                    spikes, reward=reward)

            hc_rec[step]   = result["hc_out"]
            pfc_rec[step]  = result["pfc_out"]
            ofc_rec[step]  = result["ofc_out"]
            ec_rec[step]   = result["ec_out"]
            rewards[step]  = reward
            td_errs[step]  = result["td_error"]
            bg_acts[step]  = result["bg_action"]
            bg_utils[step] = result["bg_utility"]

            novelty = self.ctrl.compute_novelty(spikes, self.pfc.working_memory)
            self.ctrl.ach_attention(novelty)

            self.step_count += 1
            if callback is not None and step % 500 == 0:
                callback(step, result)

        return dict(
            hc_spikes    = hc_rec,
            pfc_spikes   = pfc_rec,
            ofc_spikes   = ofc_rec,
            ec_activity  = ec_rec,
            rewards      = rewards,
            td_errors    = td_errs,
            schedule     = schedule,
            toj_labels   = labels,
            bg_actions   = bg_acts,
            bg_utilities = bg_utils,
        )

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_phase_map(schedule, n_steps):
        """Build per-step (phase, pattern_id) lookup for DMS."""
        phase_map = [("iti", None)] * n_steps
        for (phase, start, end, pid) in schedule:
            for s in range(start, min(end, n_steps)):
                phase_map[s] = (phase, pid)
        return phase_map

    @staticmethod
    def _build_toj_phase_map(schedule, n_steps):
        """Build per-step (phase, pattern_id, toj_label) lookup for TOJ."""
        phase_map = [("iti", None, -1)] * n_steps
        for (phase, start, end, pid, label) in schedule:
            for s in range(start, min(end, n_steps)):
                phase_map[s] = (phase, pid, label)
        return phase_map

    def freeze_pfc(self) -> None:
        """Disable PFC STDP after training (weights are non-volatile)."""
        self.pfc.enable_stdp = False

    def evaluate_replay(self, n_steps: int = 500) -> np.ndarray:
        """
        Run replay-only mode (no external input) and return HC activity.
        Checks if learned sequences can be self-generated.
        """
        activity = []
        dummy = np.zeros(config.N_INPUT)
        for _ in range(n_steps):
            hc_out = self.hc.step(dummy, modulation=1.0, replay_mode=True)
            activity.append(hc_out.copy())
        return np.array(activity)
