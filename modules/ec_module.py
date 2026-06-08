"""
Entorhinal Cortex Module  (EC)
================================
Maps to: Structured Analog Oscillatory Array as Grid-like Representation
for State-Space.

Key properties:
  - Oscillatory analog array — no learning (fixed grid structure)
  - 4×4 grid of place/grid cells with periodic firing fields
  - Multi-scale spatial encoding (different spacing per row)
  - Theta-modulated (6-10 Hz) input from HC
  - Outputs spatial coordinates for cognitive mapping

Biological reference: Moser et al. grid cells (2008 Science);
Hafting et al. (2005 Nature).
"""

import numpy as np
import config


class ECModule:
    """
    Entorhinal cortex grid-cell array.

    Implemented as a structured analog oscillator — no memristor plasticity;
    the grid structure is intrinsic.  EC feeds state-space coordinates to
    PFC and HC.
    """

    GRID_SIZE = 4   # 4×4 grid

    def __init__(self, dt: float = config.DT, seed: int = 40):
        self.n_units = config.N_EC          # 16
        self.dt      = dt
        self.rng     = np.random.default_rng(seed)

        g = self.GRID_SIZE

        # Grid spacings — each row has a different spatial scale
        # (mimics multi-scale grid modules in MEC)
        self._spacings = np.array([0.3 + 0.1 * i for i in range(g)])

        # Grid orientations (radians)
        self._orientations = np.linspace(0, np.pi / 3, g)

        # Preferred phases for each cell in the 4×4 grid
        self._phases = self.rng.uniform(0, 2 * np.pi, (g, g))

        # Oscillation phases (maintained continuously)
        self._osc_phases = self.rng.uniform(0, 2 * np.pi, (g, g))

        # Theta and grid oscillation frequencies
        self._theta_freq = config.FREQ["theta"]
        self._grid_freq  = config.FREQ["grid"]

        # Current state
        self.activity    = np.zeros(self.n_units)
        self._theta_phase = 0.0

        self.spike_history = []

    # ── grid-cell firing ──────────────────────────────────────────────────────

    def _grid_rate(self, position: np.ndarray) -> np.ndarray:
        """
        Compute instantaneous grid-cell firing rates for a 2D position.

        Uses the standard three-wave cosine model (Moser et al.):
            r(x) = [cos(k1·x) + cos(k2·x) + cos(k3·x)] / 3

        Parameters
        ----------
        position : (2,) current x, y position in [0, 1]²

        Returns
        -------
        rates : (4, 4) firing rate map, values in [0, 1]
        """
        x, y = position
        g = self.GRID_SIZE
        rates = np.zeros((g, g))

        for row in range(g):
            lam = self._spacings[row]        # grid spacing
            theta0 = self._orientations[row] # orientation

            # Three wave vectors at 60° separation
            kvecs = [(2 * np.pi / lam * np.array([
                np.cos(theta0 + n * np.pi / 3),
                np.sin(theta0 + n * np.pi / 3)
            ])) for n in range(3)]

            pos_vec = np.array([x, y])
            for col in range(g):
                phase = self._phases[row, col]
                activation = sum(
                    np.cos(k @ pos_vec - phase) for k in kvecs
                ) / 3.0
                rates[row, col] = max(0.0, (activation + 1.0) / 2.0)

        return rates

    # ── oscillatory modulation ────────────────────────────────────────────────

    def _oscillatory_modulation(self) -> np.ndarray:
        """
        Theta × grid oscillation coupling.
        Each cell has its own oscillation phase (interference model).
        """
        theta_mod = 0.5 + 0.5 * np.sin(self._theta_phase)
        cell_osc  = 0.5 + 0.5 * np.sin(self._osc_phases)
        return theta_mod * cell_osc   # (4, 4)

    # ── main step ─────────────────────────────────────────────────────────────

    def step(self, position: np.ndarray | None = None,
             hc_theta_input: float = 0.0) -> np.ndarray:
        """
        Parameters
        ----------
        position       : (2,) x,y cognitive position estimate.
                         If None, uses internal oscillator state.
        hc_theta_input : HC theta-power modulation (0-1)

        Returns
        -------
        activity : (N_EC,) EC population activity
        """
        # advance oscillator phases
        self._theta_phase  += 2 * np.pi * self._theta_freq * self.dt
        self._osc_phases   += 2 * np.pi * self._grid_freq  * self.dt

        osc_mod = self._oscillatory_modulation()

        if position is not None:
            grid_rates = self._grid_rate(position)
        else:
            # self-generated drift in state space (internal navigation)
            t = len(self.spike_history) * self.dt
            auto_pos = np.array([
                0.5 + 0.3 * np.sin(2 * np.pi * 0.3 * t),
                0.5 + 0.3 * np.cos(2 * np.pi * 0.2 * t),
            ])
            grid_rates = self._grid_rate(auto_pos)

        # theta-phase modulation from HC
        theta_boost = 1.0 + 0.5 * hc_theta_input
        activity = (grid_rates * osc_mod * theta_boost).flatten()
        np.clip(activity, 0.0, 1.0, out=activity)

        self.activity = activity
        self.spike_history.append(activity.copy())
        return activity

    @property
    def grid_map(self) -> np.ndarray:
        """Current activity reshaped as 4×4 grid."""
        return self.activity.reshape(self.GRID_SIZE, self.GRID_SIZE)

    def reset(self) -> None:
        self.activity[:] = 0.0
        self._theta_phase = 0.0
