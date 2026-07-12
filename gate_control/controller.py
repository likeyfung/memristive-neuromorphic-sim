"""
Gate Controller
===============
Implements the Software Modules & Gate Control layer:

  Spiking Basal Ganglia    — winner-take-all action selection via disinhibition
  Neuromodulation          — global dopamine/ACh gating
  Reward / TD-Error        — prioritisation feedback
  DMN/PCC sync             — hippocampal consolidation timing

The BG receives utility signals derived from current neural population activity
(not from explicit phase labels) and selects which of four actions to execute:
  ENCODE   — route input strongly to HC
  MAINTAIN — enable HC replay for PFC consolidation
  COMPARE  — route both input and PFC pattern to OFC
  RESET    — return neuromodulators to baseline

This layer orchestrates signal flow between HC, PFC, OFC, and EC modules.
"""

import numpy as np
import config
from gate_control.basal_ganglia import SpikingBasalGanglia


class GateController:
    """
    Coordinates all four brain-region modules each time step.
    Action selection is performed by a spiking Basal Ganglia circuit.
    """

    def __init__(self, dt: float = config.DT):
        self.dt = dt

        # Neuromodulation state
        self.dopamine = config.REWARD["dopamine"]
        self.ach      = 1.0

        # Spiking Basal Ganglia: replaces Python if/else action selection
        self.bg = SpikingBasalGanglia(dt=dt)

        # Smoothed input spike rate (τ = 10 ms) — input to BG utility computation
        self._input_rate_smooth = 0.0
        self._input_alpha       = 1.0 - dt / 0.010   # ≈ 0.99

        # DMN/PCC synchronisation
        self._dmn_phase = 0.0
        self._dmn_freq  = 0.10   # Hz
        self._sync_gain = 0.3

        # Consolidation state
        self._consolidation_active = False
        self._consol_timer         = 0.0
        self._consol_duration      = 0.100

        self._last_td_error = 0.0

        self.dopamine_history = []
        self.sync_history     = []

    # ── neuromodulation ───────────────────────────────────────────────────────

    def update_dopamine(self, td_error: float) -> float:
        """Phasic dopamine release from TD-error; dips below baseline on punishment."""
        self._last_td_error = td_error
        self.dopamine += self.dt * (
            -self.dopamine / 0.200
            + max(td_error, 0.0) * 2.0
            - max(-td_error, 0.0) * 0.5
        )
        self.dopamine = float(np.clip(self.dopamine, 0.2, 3.0))
        self.dopamine_history.append(self.dopamine)
        return self.dopamine

    def ach_attention(self, novelty: float) -> float:
        """ACh gate increases with stimulus novelty."""
        self.ach = float(np.clip(0.5 + 1.5 * novelty, 0.3, 2.0))
        return self.ach

    # ── DMN/PCC synchronisation ───────────────────────────────────────────────

    def dmn_sync_signal(self) -> float:
        """Slow sinusoidal signal gating HC→PFC consolidation."""
        self._dmn_phase += 2 * np.pi * self._dmn_freq * self.dt
        sync = 0.5 + 0.5 * np.sin(self._dmn_phase)
        self.sync_history.append(sync)
        return float(sync)

    def trigger_consolidation(self) -> None:
        """Manually trigger a consolidation event (also triggered by BG MAINTAIN)."""
        self._consolidation_active = True
        self._consol_timer         = 0.0

    # ── BG utility computation ────────────────────────────────────────────────

    def _compute_utility(self, input_spikes: np.ndarray, pfc) -> np.ndarray:
        """
        Derive action utilities from current neural population activity.

        No explicit phase labels are used — the BG infers the appropriate
        action from neural signals alone:

          input_presence ≈ 1  →  stimulus is currently being presented
          wm_strength    ≈ 1  →  PFC is holding a working memory pattern

        The four utility signals map cleanly to DMS task phases:
          Sample  : input_presence ≈ 1, wm_strength ≈ 0  → ENCODE wins
          Delay   : input_presence ≈ 0, wm_strength ≈ 1  → MAINTAIN wins
          Test    : input_presence ≈ 1, wm_strength ≈ 1  → COMPARE wins
          ITI     : input_presence ≈ 0, wm_strength ≈ 0  → RESET wins
        """
        # Normalise to [0, 1].
        # At 40 Hz peak with half the neurons tuned: mean rate ≈ 0.002 spikes/step.
        # PFC WM trace at 50 Hz: steady-state per neuron ≈ 0.0015.
        inp = float(np.clip(self._input_rate_smooth / 0.0025, 0.0, 1.0))
        wm  = float(np.clip(pfc.wm_trace.mean() / 0.0015, 0.0, 1.0))

        return np.array([
            inp * (1.0 - wm),         # ENCODE
            wm  * (1.0 - inp),        # MAINTAIN
            inp * wm,                 # COMPARE
            (1.0 - inp) * (1.0 - wm), # RESET
        ], dtype=float)

    # ── main orchestration step ───────────────────────────────────────────────

    def step(self,
             hc, pfc, ofc, ec,
             input_spikes: np.ndarray,
             reward: float = 0.0,
             position: np.ndarray | None = None) -> dict:
        """
        Orchestrate one simulation time step across all modules.

        The spiking BG selects the current action, which modulates routing:
          ENCODE   → HC gets boosted modulation, no replay
          MAINTAIN → HC replay enabled (if consolidation active + DMN sync high)
          COMPARE  → standard routing (PFC pattern + new input both active)
          RESET    → modulations reduced toward baseline

        Parameters
        ----------
        hc, pfc, ofc, ec : module objects
        input_spikes     : (N_INPUT,) external input
        reward           : scalar reward signal
        position         : optional (2,) spatial position for EC
        """
        # ── 0. Update smoothed input rate (BG utility signal) ─────────────────
        self._input_rate_smooth = (
            self._input_alpha * self._input_rate_smooth
            + (1.0 - self._input_alpha) * float(input_spikes.mean())
        )

        # ── 1. BG action selection ─────────────────────────────────────────────
        utility = self._compute_utility(input_spikes, pfc)
        action, thal_out = self.bg.step(utility)

        # Map action index to routing modifiers
        # ENCODE=0, MAINTAIN=1, COMPARE=2, RESET=3
        hc_mod_boost = 1.3 if action == 0 else 1.0
        bg_replay     = (action == 1)
        ofc_boost     = 1.2 if action == 2 else 1.0
        global_scale  = 0.7 if action == 3 else 1.0

        # ── 2. EC: state-space coordinates ────────────────────────────────────
        hc_theta = float(np.sin(hc._theta_phase) * 0.5 + 0.5)
        ec_out   = ec.step(position=position, hc_theta_input=hc_theta)

        # ── 3. DMN sync signal ─────────────────────────────────────────────────
        sync = self.dmn_sync_signal()

        # ── 4. HC: hippocampal reservoir ───────────────────────────────────────
        # BG MAINTAIN action enables replay when DMN sync is high.
        # BG ENCODE action boosts HC gain for stronger encoding.
        replay_mode = bg_replay and self._consolidation_active and (sync > 0.8)
        hc_out = hc.step(
            input_spikes,
            modulation = self.dopamine * hc_mod_boost * global_scale,
            replay_mode = replay_mode,
        )

        # ── 5. PFC: working memory ─────────────────────────────────────────────
        hc_to_pfc = hc_out[:config.N_PFC]
        pfc_out   = pfc.step(
            input_spikes,
            modulation = self.ach * global_scale,
            hc_signal  = hc_to_pfc,
        )

        # ── 6. OFC: value / reward ─────────────────────────────────────────────
        ofc_out, td_error = ofc.step(
            input_spikes,
            reward     = reward,
            modulation = self.dopamine * ofc_boost * global_scale,
        )

        # ── 7. Update neuromodulation from TD-error ────────────────────────────
        self.update_dopamine(td_error)

        # ── 8. Consolidation timer ─────────────────────────────────────────────
        if self._consolidation_active:
            self._consol_timer += self.dt
            if self._consol_timer >= self._consol_duration:
                self._consolidation_active = False

        return dict(
            hc_out   = hc_out,
            pfc_out  = pfc_out,
            ofc_out  = ofc_out,
            ec_out   = ec_out,
            td_error = td_error,
            dopamine = self.dopamine,
            sync     = sync,
            bg_action   = action,
            bg_utility  = utility,
            bg_thal_out = thal_out,
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
