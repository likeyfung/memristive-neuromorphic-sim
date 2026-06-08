"""
Vectorised ion-diffusion memristor crossbar array.

Physical model (per device):

    dw/dt = η₀ · sinh(V/V₀) · f(w) − w/τ_diff + ξ(t)

where
    w ∈ [0,1]       normalised filament state (0 = fully reset, 1 = set)
    f(w) = (1−w)    if ion_flux > 0 (SET direction — growth limiting)
    f(w) = w        if ion_flux < 0 (RESET direction — dissolution limiting)
    τ_diff          diffusion time constant  →  controls volatility
    ξ(t)            Gaussian filament noise ∝ √dt

Conductance (nonlinear, matching ECM/VCM measurement data):
    G = G_off + (G_on − G_off) · w²

Reference: Strukov et al. (2008), Waser & Aono (2007), ion-hopping drift model.
"""

import numpy as np


class MemristorArray:
    """
    N_rows × N_cols vectorised memristor crossbar.

    All device states are stored as numpy arrays so every operation
    (ODE step, conductance read, STDP update) is fully vectorised.
    """

    def __init__(self, n_rows: int, n_cols: int,
                 G_on: float, G_off: float,
                 tau_diff: float, eta0: float, V0: float,
                 noise_amp: float = 0.0, seed: int = 42):
        self.n_rows    = n_rows
        self.n_cols    = n_cols
        self.G_on      = G_on
        self.G_off     = G_off
        self.tau_diff  = tau_diff
        self.eta0      = eta0
        self.V0        = V0
        self.noise_amp = noise_amp
        self.rng       = np.random.default_rng(seed)

        # filament state matrix  w ∈ [0, 1]
        self.w = self.rng.uniform(0.01, 0.05, (n_rows, n_cols))

        # STDP eligibility traces
        self.pre_trace  = np.zeros(n_cols)
        self.post_trace = np.zeros(n_rows)

    # ── device physics ────────────────────────────────────────────────────────

    def step(self, V_matrix: np.ndarray, dt: float) -> None:
        """
        Euler step of the ion-diffusion ODE for every device in the array.

        Parameters
        ----------
        V_matrix : (n_rows, n_cols)  voltage across each device
        dt       : float             time step [s]
        """
        # ion hopping  — clamped for numerical stability
        ion_flux = self.eta0 * np.sinh(np.clip(V_matrix / self.V0, -20, 20))

        # growth-limiting factor (prevents w from going outside [0,1])
        f_w = np.where(ion_flux >= 0, 1.0 - self.w, self.w)

        # ODE: drift + diffusion (volatility)
        dw = ion_flux * f_w - self.w / self.tau_diff
        self.w += dw * dt

        # filament stochastic noise
        if self.noise_amp > 0.0:
            self.w += (self.noise_amp
                       * self.rng.standard_normal((self.n_rows, self.n_cols))
                       * np.sqrt(dt))

        np.clip(self.w, 0.0, 1.0, out=self.w)

    def diffuse(self, dt: float) -> None:
        """Apply only the spontaneous diffusion term (read-path degradation)."""
        self.w *= np.exp(-dt / self.tau_diff)

    # ── conductance & forward pass ────────────────────────────────────────────

    @property
    def G(self) -> np.ndarray:
        """Conductance matrix [n_rows × n_cols] in Siemens."""
        return self.G_off + (self.G_on - self.G_off) * self.w ** 2

    def forward(self, v_in: np.ndarray) -> np.ndarray:
        """
        Crossbar dot product  I_out = G @ v_in.

        Parameters
        ----------
        v_in : (n_cols,)  input voltage vector

        Returns
        -------
        i_out : (n_rows,)  output current vector
        """
        return self.G @ v_in

    # ── STDP learning ─────────────────────────────────────────────────────────

    def update_traces(self, pre_spikes: np.ndarray, post_spikes: np.ndarray,
                      tau_plus: float, tau_minus: float, dt: float) -> None:
        """
        Decay eligibility traces and accumulate new spikes.
        Called every time step during training.
        """
        # Traces clamped to [0,1]: prevents runaway LTD when neurons fire
        # at very high rates (e.g. 500 Hz → unbounded trace destroys weights).
        self.pre_trace  = np.clip(
            self.pre_trace  + (-self.pre_trace  / tau_plus  + pre_spikes)  * dt, 0.0, 1.0)
        self.post_trace = np.clip(
            self.post_trace + (-self.post_trace / tau_minus + post_spikes) * dt, 0.0, 1.0)

    def apply_stdp(self, pre_spikes: np.ndarray, post_spikes: np.ndarray,
                   A_plus: float, A_minus: float) -> None:
        """
        Hebbian STDP conductance update:
          LTP  (post fires): Δw +=  A_plus  · x_pre  (outer product)
          LTD  (pre  fires): Δw −=  A_minus · x_post (outer product)
        Maps to physical SET/RESET pulses in the crossbar.
        """
        dw_ltp = A_plus  * np.outer(post_spikes,              self.pre_trace)
        dw_ltd = A_minus * np.outer(self.post_trace, pre_spikes)
        self.w += dw_ltp - dw_ltd
        np.clip(self.w, 0.0, 1.0, out=self.w)

    # ── utilities ─────────────────────────────────────────────────────────────

    def mean_conductance(self) -> float:
        return float(self.G.mean())

    def reset_state(self, low: float = 0.01, high: float = 0.05) -> None:
        self.w[:]           = self.rng.uniform(low, high, (self.n_rows, self.n_cols))
        self.pre_trace[:]   = 0.0
        self.post_trace[:]  = 0.0
