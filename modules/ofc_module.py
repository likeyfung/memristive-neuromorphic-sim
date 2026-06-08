"""
Orbitofrontal Cortex Module  (OFC)
====================================
Maps to: Recurrent Semi-volatile Memristor Array for value update and reward.

Key properties:
  - Semi-volatile (τ_diff = 500 ms) → reward signal persists across trials
  - TD (temporal-difference) learning for value estimation
  - Hidden-state inference from partial observations
  - Firing modulation under uncertainty

Biological reference: OFC reward coding and value update
(Schoenbaum et al. 2009; Padoa-Schioppa 2011).
"""

import numpy as np
from modules.base_module import BaseModule
import config


class OFCModule(BaseModule):
    """
    OFC value / reward module with TD-error learning.
    """

    def __init__(self, dt: float = config.DT, seed: int = 30):
        super().__init__(
            n_in         = config.N_INPUT,
            n_units      = config.N_OFC,
            device_params= config.SEMIVOL,
            dt           = dt,
            enable_stdp  = True,
            seed         = seed,
        )
        rp = config.REWARD
        self.gamma_td  = rp["gamma_td"]
        self.alpha_td  = rp["alpha_td"]
        self.dopamine  = rp["dopamine"]

        # Value function estimate V(s)
        self.V_state   = 0.0
        self.V_prev    = 0.0

        # TD-error history
        self.td_errors = []

        # Uncertainty signal (entropy of output distribution)
        self._entropy_history = []

        self.spike_history = []

    # ── TD learning ───────────────────────────────────────────────────────────

    def compute_td_error(self, reward: float, V_next: float) -> float:
        """
        δ = r + γ·V(s') − V(s)
        Updates internal value estimate.
        """
        delta = reward + self.gamma_td * V_next - self.V_state
        self.V_state += self.alpha_td * delta
        self.td_errors.append(delta)
        return delta

    def _activity_to_value(self, spikes: np.ndarray) -> float:
        """Map population activity → scalar value estimate."""
        return float(spikes.mean())

    # ── uncertainty modulation ────────────────────────────────────────────────

    def _firing_entropy(self, rates: np.ndarray) -> float:
        """Shannon entropy of normalised firing rates (uncertainty proxy)."""
        p = rates + 1e-8
        p = p / p.sum()
        return float(-np.sum(p * np.log(p)))

    # ── main step ─────────────────────────────────────────────────────────────

    def step(self, input_spikes: np.ndarray,
             reward: float = 0.0,
             modulation: float = 1.0) -> tuple[np.ndarray, float]:
        """
        Parameters
        ----------
        input_spikes : (N_INPUT,) state encoding spikes
        reward       : scalar reward signal from environment
        modulation   : global neuromodulation

        Returns
        -------
        out_spikes : (N_OFC,)
        td_error   : float
        """
        # dopamine modulates gain (high reward → high gain → stronger plasticity)
        dopa_gain = modulation * (1.0 + 0.5 * max(reward, 0.0))

        out = super().step(input_spikes, dopa_gain)

        V_next = self._activity_to_value(out)
        td_err = self.compute_td_error(reward, V_next)

        # TD-error modulates STDP via dopamine: scale conductance updates
        # (positive TD-error → LTP boost; negative → LTD boost)
        if td_err > 0:
            self.W_in.w *= (1.0 + 0.01 * td_err)
        else:
            self.W_in.w *= (1.0 + 0.005 * td_err)
        np.clip(self.W_in.w, 0.0, 1.0, out=self.W_in.w)

        entropy = self._firing_entropy(out)
        self._entropy_history.append(entropy)
        self.spike_history.append(out.copy())

        return out, td_err

    @property
    def value_estimate(self) -> float:
        return self.V_state

    @property
    def mean_td_error(self) -> float:
        if not self.td_errors:
            return 0.0
        return float(np.mean(np.abs(self.td_errors[-100:])))
