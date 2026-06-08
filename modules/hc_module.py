"""
Hippocampal Module  (HC)
========================
Maps to: Volatile Memristor Array as Recurrent Reservoir + oscillatory loops.

Key properties:
  - Volatile (τ_diff = 50 ms) → short-term memory, natural decay
  - Recurrent reservoir dynamics → sequence replay
  - Sharp-wave ripple (SWR, ~150 Hz) modulation during consolidation
  - Theta-phase (8 Hz) gating of input windows
  - CA1/CA2 sub-populations (first/second half of units)

Biological reference: HC sequence replay and sharp-wave ripples
(Liu et al. 2022 Nat Rev Neurosci; Zhao et al. 2023 Nat Neurosci).
"""

import numpy as np
from modules.base_module import BaseModule
import config


class HCModule(BaseModule):
    """
    Hippocampal recurrent reservoir using volatile memristors.
    """

    def __init__(self, dt: float = config.DT, seed: int = 10):
        super().__init__(
            n_in         = config.N_INPUT,
            n_units      = config.N_HC,
            device_params= config.VOL,
            dt           = dt,
            enable_stdp  = True,
            seed         = seed,
        )
        # CA1 / CA2 split (first half / second half)
        self.n_ca1 = config.N_HC // 2
        self.n_ca2 = config.N_HC - self.n_ca1

        # SWR oscillator state
        self._swr_phase = 0.0
        self._theta_phase = 0.0
        self.swr_freq   = config.FREQ["swr"]
        self.theta_freq = config.FREQ["theta"]

        # replay buffer: stores recent output spikes for sequence consolidation
        replay_len = int(0.200 / dt)   # 200 ms replay window
        self._replay_buf = np.zeros((replay_len, config.N_HC))
        self._buf_ptr    = 0

        # Spike history for rate estimation
        self.spike_history = []

    # ── oscillatory modulation ────────────────────────────────────────────────

    def _oscillation_gain(self) -> float:
        """
        Combined theta-phase gate × SWR modulation.
        Returns a gain ∈ [0.5, 2.0] that multiplicatively scales input current.
        """
        theta_gate = 0.75 + 0.25 * np.sin(self._theta_phase)
        swr_boost  = 1.0  + 0.5  * np.sin(self._swr_phase) ** 2
        return float(theta_gate * swr_boost)

    # ── main step ─────────────────────────────────────────────────────────────

    def step(self, input_spikes: np.ndarray,
             modulation: float = 1.0,
             replay_mode: bool = False) -> np.ndarray:
        """
        Parameters
        ----------
        input_spikes : (N_INPUT,) external spike input
        modulation   : neuromodulation gain (dopamine)
        replay_mode  : if True, inject replay signal instead of external input

        Returns
        -------
        out_spikes : (N_HC,)
        """
        # advance oscillation phases
        self._theta_phase += 2 * np.pi * self.theta_freq * self.dt
        self._swr_phase   += 2 * np.pi * self.swr_freq   * self.dt

        osc_gain = self._oscillation_gain()

        if replay_mode:
            # Seed recurrent drive from replay buffer (theta-compressed replay).
            # Overwrites _prev_out so the recurrent array sees stored activity.
            replay_idx = (self._buf_ptr - 1) % len(self._replay_buf)
            self._prev_out = self._replay_buf[replay_idx].copy()
            effective_input = np.zeros(self.n_in)
        else:
            effective_input = input_spikes

        out = super().step(effective_input, modulation * osc_gain)

        # store to replay buffer
        self._replay_buf[self._buf_ptr % len(self._replay_buf)] = out
        self._buf_ptr += 1

        self.spike_history.append(out.copy())
        return out

    # ── CA sub-populations ────────────────────────────────────────────────────

    @property
    def ca1_activity(self) -> np.ndarray:
        return self._prev_out[:self.n_ca1]

    @property
    def ca2_activity(self) -> np.ndarray:
        return self._prev_out[self.n_ca1:]

    def get_replay_sequence(self, n_steps: int) -> np.ndarray:
        """Return the last n_steps of the replay buffer as (n_steps, N_HC)."""
        out = []
        for i in range(n_steps):
            idx = (self._buf_ptr - n_steps + i) % len(self._replay_buf)
            out.append(self._replay_buf[idx])
        return np.array(out)
