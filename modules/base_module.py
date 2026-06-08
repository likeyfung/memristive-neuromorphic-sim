"""
Base classes shared by all brain-region modules.

LIFLayer  — vectorised leaky integrate-and-fire neuron population.
BaseModule — memristor crossbar + LIF readout + STDP skeleton.
"""

import numpy as np
from devices.memristor_array import MemristorArray
import config


class LIFLayer:
    """
    Vectorised leaky integrate-and-fire population.

    Membrane dynamics:
        dV/dt = -(V - V_rest)/τ_m + R_m · I_in / τ_m

    Spike: V ≥ V_th  →  output spike, V ← V_reset, enter refractory.
    """

    def __init__(self, n_units: int, dt: float, **overrides):
        p = {**config.LIF, **overrides}
        self.n       = n_units
        self.dt      = dt
        self.tau_m   = p["tau_m"]
        self.V_rest  = p["V_rest"]
        self.V_th    = p["V_th"]
        self.V_reset = p["V_reset"]
        self.R_m     = p["R_m"]
        self.t_ref   = p["t_ref"]

        self.V_m     = np.full(n_units, p["V_rest"])
        self.ref_cnt = np.zeros(n_units)   # refractory countdown [s]
        self.spikes  = np.zeros(n_units, dtype=float)

    def step(self, I_in: np.ndarray) -> np.ndarray:
        """
        Advance one time step.

        Parameters
        ----------
        I_in : (n_units,) input currents [A]

        Returns
        -------
        spikes : (n_units,) binary spike vector
        """
        refractory = self.ref_cnt > 0.0
        self.ref_cnt = np.maximum(0.0, self.ref_cnt - self.dt)

        dV = (-(self.V_m - self.V_rest) + self.R_m * I_in) / self.tau_m * self.dt
        self.V_m = np.where(refractory, self.V_reset, self.V_m + dV)

        fired = self.V_m >= self.V_th
        self.V_m[fired]     = self.V_reset
        self.ref_cnt[fired] = self.t_ref
        self.spikes         = fired.astype(float)
        return self.spikes

    def reset(self) -> None:
        self.V_m[:]     = self.V_rest
        self.ref_cnt[:] = 0.0
        self.spikes[:]  = 0.0


class BaseModule:
    """
    Generic neuromorphic module with:
      - W_in  : input memristor array         (n_units × n_in)
      - W_rec : recurrent memristor array     (n_units × n_units)
      - lif   : LIF output layer              (n_units)
      - Online STDP for both arrays
    """

    def __init__(self, n_in: int, n_units: int,
                 device_params: dict, dt: float,
                 enable_stdp: bool = True, seed: int = 0):
        self.n_in        = n_in
        self.n_units     = n_units
        self.dt          = dt
        self.enable_stdp = enable_stdp

        sp = config.STDP
        self.A_plus    = sp["A_plus"]
        self.A_minus   = sp["A_minus"]
        self.tau_plus  = sp["tau_plus"]
        self.tau_minus = sp["tau_minus"]

        self.W_in  = MemristorArray(n_units, n_in,    **device_params, seed=seed)
        self.W_rec = MemristorArray(n_units, n_units, **device_params, seed=seed + 1)
        self.lif   = LIFLayer(n_units, dt)

        self._prev_out = np.zeros(n_units)

    # ── forward ───────────────────────────────────────────────────────────────

    def step(self, input_spikes: np.ndarray,
             modulation: float = 1.0) -> np.ndarray:
        """
        One simulation step.

        Parameters
        ----------
        input_spikes : (n_in,)  pre-synaptic binary spike vector
        modulation   : float    global neuromodulation gain (dopamine/ACh)

        Returns
        -------
        out_spikes : (n_units,)  post-synaptic spike vector
        """
        V_in  = input_spikes   * config.V_SPIKE_READ
        V_rec = self._prev_out * config.V_SPIKE_READ

        I_in  = self.W_in.forward(V_in)
        I_rec = self.W_rec.forward(V_rec)
        I_tot = (I_in + I_rec) * modulation

        out_spikes = self.lif.step(I_tot)

        if self.enable_stdp:
            self._stdp_step(input_spikes, out_spikes)

        self._prev_out = out_spikes.copy()

        # Diffusion (volatility) only fires during quiescent periods.
        # Biologically: SET pulses during spiking overcome diffusion;
        # diffusion dominates only when the circuit is silent.
        # Non-volatile arrays (tau_diff=1e6) are unaffected regardless.
        quiescent = (input_spikes.sum() == 0) and (out_spikes.sum() == 0)
        if quiescent:
            self.W_in.diffuse(self.dt)
            self.W_rec.diffuse(self.dt)

        return out_spikes

    # ── STDP ─────────────────────────────────────────────────────────────────

    def _stdp_step(self, pre: np.ndarray, post: np.ndarray) -> None:
        self.W_in.update_traces(pre, post, self.tau_plus, self.tau_minus, self.dt)
        self.W_in.apply_stdp(pre, post, self.A_plus, self.A_minus)

        self.W_rec.update_traces(self._prev_out, post,
                                 self.tau_plus, self.tau_minus, self.dt)
        self.W_rec.apply_stdp(self._prev_out, post, self.A_plus, self.A_minus)

    # ── utilities ─────────────────────────────────────────────────────────────

    def reset(self) -> None:
        self.lif.reset()
        self._prev_out[:] = 0.0

    @property
    def firing_rate(self) -> np.ndarray:
        """Instantaneous (single-step) firing rate proxy."""
        return self._prev_out

    def mean_conductance_in(self) -> float:
        return self.W_in.mean_conductance()

    def mean_conductance_rec(self) -> float:
        return self.W_rec.mean_conductance()
