"""
Gate Controller
===============
Implements the Software Modules & Gate Control layer:

  DMN/PCC Network Coordination  — synchronisation pulses and consolidation
  Neuromodulation               — global dopamine/ACh gating
  Reward / TD-Error             — prioritisation feedback

This layer orchestrates signal flow between HC, PFC, OFC, and EC modules,
mirroring the top-level control block in the proposal architecture diagram.
"""

import numpy as np
import config


class GateController:
    """
    Coordinates all four brain-region modules each time step.
    """

    def __init__(self, dt: float = config.DT):
        self.dt = dt

        # Neuromodulation state
        self.dopamine   = config.REWARD["dopamine"]   # 0–2 scale
        self.ach        = 1.0    # acetylcholine (attention gate)

        # DMN/PCC synchronisation
        self._dmn_phase = 0.0
        self._dmn_freq  = 0.10   # Hz  slow cortical oscillation (DMN)
        self._sync_gain = 0.3    # how strongly DMN modulates consolidation

        # Consolidation state
        self._consolidation_active = False
        self._consol_timer         = 0.0
        self._consol_duration      = 0.100   # s

        # TD-error from OFC feeds back here
        self._last_td_error = 0.0

        # History for monitoring
        self.dopamine_history  = []
        self.sync_history      = []

    # ── neuromodulation ───────────────────────────────────────────────────────

    def update_dopamine(self, td_error: float) -> float:
        """
        Phasic dopamine release proportional to positive TD-error.
        Dips below baseline on negative TD-error (aversion).
        """
        self._last_td_error = td_error
        # tonic + phasic component
        self.dopamine += self.dt * (
            -self.dopamine / 0.200          # return-to-baseline (τ = 200 ms)
            + max(td_error, 0.0) * 2.0      # phasic burst on reward
            - max(-td_error, 0.0) * 0.5     # dip on punishment
        )
        self.dopamine = float(np.clip(self.dopamine, 0.2, 3.0))
        self.dopamine_history.append(self.dopamine)
        return self.dopamine

    def ach_attention(self, novelty: float) -> float:
        """
        ACh gate increases with stimulus novelty (boosts learning rate).
        novelty ∈ [0, 1]
        """
        self.ach = float(np.clip(0.5 + 1.5 * novelty, 0.3, 2.0))
        return self.ach

    # ── DMN/PCC synchronisation ───────────────────────────────────────────────

    def dmn_sync_signal(self) -> float:
        """
        Returns a slow sinusoidal synchronisation signal.
        Used to gate hippocampal replay → PFC consolidation.
        """
        self._dmn_phase += 2 * np.pi * self._dmn_freq * self.dt
        sync = 0.5 + 0.5 * np.sin(self._dmn_phase)
        self.sync_history.append(sync)
        return float(sync)

    def trigger_consolidation(self) -> None:
        """Manually trigger a consolidation event (HC → PFC transfer)."""
        self._consolidation_active = True
        self._consol_timer         = 0.0

    # ── main orchestration step ───────────────────────────────────────────────

    def step(self,
             hc, pfc, ofc, ec,
             input_spikes: np.ndarray,
             reward: float = 0.0,
             position: np.ndarray | None = None) -> dict:
        """
        Orchestrate one simulation time step across all modules.

        Parameters
        ----------
        hc, pfc, ofc, ec : module objects
        input_spikes     : (N_INPUT,) external input
        reward           : scalar reward signal
        position         : optional (2,) spatial position for EC

        Returns
        -------
        dict with: hc_out, pfc_out, ofc_out, ec_out, td_error, dopamine
        """
        # ── 1. EC: state-space coordinates ───────────────────────────────────
        hc_theta = float(np.sin(hc._theta_phase) * 0.5 + 0.5)
        ec_out = ec.step(position=position, hc_theta_input=hc_theta)

        # ── 2. DMN sync signal ────────────────────────────────────────────────
        sync = self.dmn_sync_signal()

        # ── 3. HC: hippocampal reservoir ──────────────────────────────────────
        # consolidation: during high DMN sync, HC replays to PFC
        replay_mode = (sync > 0.8) and self._consolidation_active
        hc_out = hc.step(input_spikes,
                         modulation=self.dopamine,
                         replay_mode=replay_mode)

        # ── 4. PFC: working memory ────────────────────────────────────────────
        # HC→PFC projection (first N_PFC neurons of HC activity)
        hc_to_pfc = hc_out[:config.N_PFC]
        pfc_out   = pfc.step(input_spikes,
                             modulation=self.ach,
                             hc_signal=hc_to_pfc)

        # ── 5. OFC: value / reward ────────────────────────────────────────────
        ofc_out, td_error = ofc.step(input_spikes,
                                     reward=reward,
                                     modulation=self.dopamine)

        # ── 6. Update neuromodulation from TD-error ───────────────────────────
        self.update_dopamine(td_error)

        # ── 7. Consolidation timer ────────────────────────────────────────────
        if self._consolidation_active:
            self._consol_timer += self.dt
            if self._consol_timer >= self._consol_duration:
                self._consolidation_active = False

        return dict(
            hc_out    = hc_out,
            pfc_out   = pfc_out,
            ofc_out   = ofc_out,
            ec_out    = ec_out,
            td_error  = td_error,
            dopamine  = self.dopamine,
            sync      = sync,
        )

    # ── novelty detection ─────────────────────────────────────────────────────

    @staticmethod
    def compute_novelty(current_spikes: np.ndarray,
                        wm_trace: np.ndarray) -> float:
        """
        Novelty = 1 − cosine similarity between current input and WM trace.
        High novelty → increase ACh → boost HC encoding.
        """
        a = current_spikes.astype(float)
        b = wm_trace[:len(a)]
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
        return float(1.0 - np.dot(a, b) / denom)
