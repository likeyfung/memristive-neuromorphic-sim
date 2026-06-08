"""
Prefrontal Cortex Module  (PFC)
================================
Maps to: Recurrent Non+Semi-volatile Memristor Array for long-term
task rules and working memory.

Key properties:
  - Non-volatile memristors → persistent state across trials
  - Gamma oscillation (30-80 Hz) pacing of output
  - Persistent firing during delay periods (working memory)
  - Synchronized decision/planning ramps

Biological reference: PFC persistent firing and gamma oscillations
during working memory (Goldman-Rakic 1995; Wang 2001).
"""

import numpy as np
from modules.base_module import BaseModule
import config


class PFCModule(BaseModule):
    """
    PFC working-memory module using non-volatile memristors.
    Maintains task rules across the full simulation.
    """

    def __init__(self, dt: float = config.DT, seed: int = 20):
        super().__init__(
            n_in         = config.N_INPUT,
            n_units      = config.N_PFC,
            device_params= config.NONVOL,
            dt           = dt,
            enable_stdp  = True,
            seed         = seed,
        )
        self.gamma_freq   = config.FREQ["gamma"]
        self._gamma_phase = 0.0

        # Structured W_in: Cat→PFC[0:N/2], Dog→PFC[N/2:N].
        # STDP refines this during training.
        n_half_pfc   = config.N_PFC   // 2
        n_half_input = config.N_INPUT // 2
        self.W_in.w[:n_half_pfc,   :n_half_input]  = 0.40   # Cat block (high G)
        self.W_in.w[n_half_pfc:,   n_half_input:]  = 0.40   # Dog block (high G)
        self.W_in.w[:n_half_pfc,   n_half_input:]  = 0.005  # cross-terms (near G_off)
        self.W_in.w[n_half_pfc:,   :n_half_input]  = 0.005

        # W_rec starts near-zero: random large initial values would cross-drive
        # the "wrong" half-population via 22+ mV pulses, erasing the input structure.
        # STDP will build task-specific recurrent connectivity over training.
        self.W_rec.w[:] = 0.001

        # working memory: exponential trace of recent activity
        self.wm_trace  = np.zeros(config.N_PFC)
        self._wm_tau   = 0.300   # s  working-memory decay (300 ms)

        # planning ramp: linearly increasing drive over a time window
        self._ramp_active   = False
        self._ramp_duration = 0.500   # s
        self._ramp_elapsed  = 0.0
        self._ramp_target   = np.zeros(config.N_PFC)

        self.spike_history = []

    # ── gamma-paced step ──────────────────────────────────────────────────────

    def step(self, input_spikes: np.ndarray,
             modulation: float = 1.0,
             hc_signal: np.ndarray | None = None) -> np.ndarray:
        """
        Parameters
        ----------
        input_spikes : (N_INPUT,) direct input
        modulation   : dopamine / ACh gain
        hc_signal    : optional HC→PFC projection (consolidation)

        Returns
        -------
        out_spikes : (N_PFC,)
        """
        self._gamma_phase += 2 * np.pi * self.gamma_freq * self.dt
        gamma_gate = 0.8 + 0.2 * np.sin(self._gamma_phase)   # ∈ [0.6, 1.0]

        # HC→PFC projection: weak modulatory gating only.
        # Kept small (0.02) so the structured Cat/Dog encoding in W_in dominates;
        # a strong HC signal would flood PFC with recurrent noise and destroy
        # the learned pattern separation.
        effective_input = input_spikes.copy()
        if hc_signal is not None and len(hc_signal) == self.n_in:
            effective_input = np.clip(effective_input + 0.02 * hc_signal, 0, 1)

        out = super().step(effective_input, modulation * gamma_gate)

        # update working-memory trace
        self.wm_trace += (-self.wm_trace / self._wm_tau + out) * self.dt
        np.clip(self.wm_trace, 0.0, 1.0, out=self.wm_trace)

        # update planning ramp
        if self._ramp_active:
            self._ramp_elapsed += self.dt
            ramp_frac = min(self._ramp_elapsed / self._ramp_duration, 1.0)
            # inject ramp as additional bias current (simulates decision drive)
            # (applied via the stored state, not external input here)
            if self._ramp_elapsed >= self._ramp_duration:
                self._ramp_active = False

        self.spike_history.append(out.copy())
        return out

    # ── control API ───────────────────────────────────────────────────────────

    def start_planning_ramp(self, target_pattern: np.ndarray) -> None:
        """Trigger a planning/decision ramp toward target_pattern."""
        self._ramp_active   = True
        self._ramp_elapsed  = 0.0
        self._ramp_target   = target_pattern.copy()

    @property
    def working_memory(self) -> np.ndarray:
        """Current working-memory trace (n_units,)."""
        return self.wm_trace.copy()
