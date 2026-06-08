"""
STDP Trainer
============
Manages the self-supervised, adaptive training loop on the memristive modules.

Training follows the proposal's pipeline:
  1. Encode recording data (or synthetic spikes) as voltage pulses
  2. Feed through HC → PFC → OFC → EC modules
  3. STDP updates conductances in real time
  4. After training: freeze non-volatile (PFC) weights; volatile (HC) decay naturally

The trainer also implements the DMS task schedule from SpikeGenerator.
"""

import numpy as np
from typing import Callable
import config


class STDPTrainer:
    """
    Runs the full self-supervised training loop.
    """

    def __init__(self, hc, pfc, ofc, ec, controller, spike_gen,
                 dt: float = config.DT):
        self.hc         = hc
        self.pfc        = pfc
        self.ofc        = ofc
        self.ec         = ec
        self.ctrl       = controller
        self.spike_gen  = spike_gen
        self.dt         = dt

        # metrics
        self.loss_history    = []      # decoder reconstruction loss
        self.reward_history  = []
        self.step_count      = 0

    # ── DMS training ─────────────────────────────────────────────────────────

    def train_dms(self, n_steps: int,
                  callback: Callable | None = None) -> dict:
        """
        Run Delayed Match-to-Sample training for n_steps steps.

        Returns
        -------
        dict: hc_spikes, pfc_spikes, ofc_spikes, ec_activity, rewards, td_errors
        """
        sg = self.spike_gen
        schedule = sg.dms_schedule(n_steps)
        phase_map = self._build_phase_map(schedule, n_steps)

        # pre-allocate recording arrays
        hc_rec  = np.zeros((n_steps, config.N_HC))
        pfc_rec = np.zeros((n_steps, config.N_PFC))
        ofc_rec = np.zeros((n_steps, config.N_OFC))
        ec_rec  = np.zeros((n_steps, config.N_EC))
        rewards = np.zeros(n_steps)
        td_errs = np.zeros(n_steps)

        sample_pattern = 0    # last presented sample
        reward_pending = False

        for step in range(n_steps):
            t     = step * self.dt
            phase, pid = phase_map[step]

            # ── generate input spikes for this phase ──────────────────────────
            if phase == "sample":
                spikes = sg.pattern_spikes(pid, t, noise=0.05)   # low noise → clean Cat/Dog encoding
                sample_pattern = pid
                reward = 0.0

            elif phase == "delay":
                wm = self.pfc.working_memory
                spikes = sg.delay_activity(t, wm_pattern=wm)
                reward = 0.0
                # trigger consolidation mid-delay
                if self.ctrl._consol_timer == 0.0:
                    self.ctrl.trigger_consolidation()

            elif phase == "test":
                spikes = sg.pattern_spikes(pid, t, noise=0.08)   # slightly noisier test
                # reward: 1 if test matches sample, -1 otherwise
                reward = 1.0 if (pid == sample_pattern) else -1.0
                reward_pending = True

            else:   # iti
                spikes = sg.delay_activity(t)
                reward = 0.0

            # ── one coordinated forward step ──────────────────────────────────
            result = self.ctrl.step(self.hc, self.pfc, self.ofc, self.ec,
                                    spikes, reward=reward)

            hc_rec[step]  = result["hc_out"]
            pfc_rec[step] = result["pfc_out"]
            ofc_rec[step] = result["ofc_out"]
            ec_rec[step]  = result["ec_out"]
            rewards[step] = reward
            td_errs[step] = result["td_error"]

            # novelty-based ACh modulation
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
        )

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_phase_map(schedule, n_steps):
        """Build per-step (phase, pattern_id) lookup."""
        phase_map = [("iti", None)] * n_steps
        for (phase, start, end, pid) in schedule:
            for s in range(start, min(end, n_steps)):
                phase_map[s] = (phase, pid)
        return phase_map

    def freeze_pfc(self) -> None:
        """Disable PFC STDP after training (weights are non-volatile)."""
        self.pfc.enable_stdp = False

    def evaluate_replay(self, n_steps: int = 500) -> np.ndarray:
        """
        Run replay-only mode (no external input) and return HC activity.
        Used to check if learned sequences can be self-generated.
        """
        activity = []
        dummy = np.zeros(config.N_INPUT)
        for step in range(n_steps):
            hc_out = self.hc.step(dummy, modulation=1.0, replay_mode=True)
            activity.append(hc_out.copy())
        return np.array(activity)
