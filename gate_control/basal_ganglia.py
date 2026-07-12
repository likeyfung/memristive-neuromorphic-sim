"""
Spiking Basal Ganglia (BG) for action selection.

Implements the direct pathway of the cortico-basal ganglia-thalamic loop:

  Cortex → strD1 →(−) GPi ← STN(tonic) → (−) Thalamus → action

Four cognitive actions (winner-take-all via focused disinhibition):
  0 : ENCODE   — new stimulus arriving, encode into HC
  1 : MAINTAIN — no new stimulus, PFC holds working memory
  2 : COMPARE  — test stimulus against stored PFC pattern
  3 : RESET    — inter-trial interval, clear transient states

Circuit logic:
  GPi is tonically active and tonically suppresses the thalamus.
  When a cortical utility signal makes strD1 fire for action i,
  D1[i] inhibits GPi[i] → GPi[i] goes silent → thalamus[i] is released
  and fires. This "focused disinhibition" selects exactly one action.

Biological reference: Frank et al. (2001); Mink (1996); Middleton & Strick (2000).
"""

import numpy as np
from modules.base_module import LIFLayer
import config

# ── BG topology constants ─────────────────────────────────────────────────────
N_ACTIONS = 4    # ENCODE, MAINTAIN, COMPARE, RESET
N_PER     = 16   # LIF neurons per action per population (strD1, GPi, thalamus)

# Calibrated to config.LIF threshold current:
# I_th = (V_th − V_rest) / R_m = (−0.055 − (−0.070)) / 1e8 = 1.5e-7 A
_I_TH = (config.LIF["V_th"] - config.LIF["V_rest"]) / config.LIF["R_m"]

# strD1: utility [0, 1] → input current above threshold
D1_SCALE   = _I_TH * 4.0    # drives D1 to fire at ~50–100 Hz for utility ≈ 1

# GPi: tonic excitatory drive (active without D1 inhibition)
GPi_TONIC  = _I_TH * 2.0    # fires at moderate rate spontaneously

# D1 → GPi inhibitory weight (per unit of smoothed D1 rate trace)
# Trace steady state ≈ rate × dt = 50 Hz × 1e-4 = 0.005.
# Need D1_GPi_W × 0.005 ≥ GPi_TONIC = 2 × I_th
# → D1_GPi_W ≥ 400 × I_th.  Set to 700 × I_th for reliable suppression.
D1_GPi_W   = _I_TH * 700.0  # = 1.05e-4 A per unit trace

# Thalamus: bias to fire when GPi is suppressed
THAL_BIAS  = _I_TH * 1.8    # just above threshold; fires when GPi is off

# GPi → thalamus inhibitory weight (same scale as D1→GPi)
GPi_THAL_W = _I_TH * 700.0

# Exponential trace filter: τ = 10 ms smooths noisy single-step spike counts
_ALPHA = 1.0 - config.DT / 0.010   # ≈ 0.99 per step (10 kHz simulation)


class SpikingBasalGanglia:
    """
    Spiking BG: replaces the Python if/else gate control with a spiking
    circuit that reads neural utility signals and selects actions via
    the strD1 → GPi → Thalamus disinhibition pathway.
    """

    ACTIONS = ["ENCODE", "MAINTAIN", "COMPARE", "RESET"]

    def __init__(self, dt: float = config.DT):
        self.dt = dt

        # Three LIF populations, each with N_ACTIONS × N_PER neurons.
        # Neurons [i*N_PER : (i+1)*N_PER] correspond to action i.
        self.strD1 = LIFLayer(N_ACTIONS * N_PER, dt)
        self.gpi   = LIFLayer(N_ACTIONS * N_PER, dt)
        self.thal  = LIFLayer(N_ACTIONS * N_PER, dt)

        # Per-action smoothed firing rate traces
        self.d1_trace   = np.zeros(N_ACTIONS)
        self.gpi_trace  = np.zeros(N_ACTIONS)
        self.thal_trace = np.zeros(N_ACTIONS)

        # History for analysis and plotting
        self.action_history  : list[int]         = []
        self.utility_history : list[np.ndarray]  = []

    def step(self, utility: np.ndarray) -> tuple[int, np.ndarray]:
        """
        One BG time step.

        Parameters
        ----------
        utility : (N_ACTIONS,) action desirability in [0, 1], derived from
                  neural population activity (not from explicit phase labels)

        Returns
        -------
        selected : int           index of selected action
        thal_out : (N_ACTIONS,) smoothed thalamic firing rates
        """
        # ── strD1: fire proportional to utility ──────────────────────────────
        I_d1   = np.repeat(utility * D1_SCALE, N_PER)
        d1_sp  = self.strD1.step(I_d1)
        d1_rate = d1_sp.reshape(N_ACTIONS, N_PER).mean(axis=1)
        self.d1_trace = _ALPHA * self.d1_trace + (1.0 - _ALPHA) * d1_rate

        # ── GPi: tonic minus D1 inhibition ───────────────────────────────────
        gpi_net = np.clip(GPi_TONIC - D1_GPi_W * self.d1_trace, -1e-4, 1e-4)
        I_gpi   = np.repeat(gpi_net, N_PER)
        gpi_sp  = self.gpi.step(I_gpi)
        gpi_rate = gpi_sp.reshape(N_ACTIONS, N_PER).mean(axis=1)
        self.gpi_trace = _ALPHA * self.gpi_trace + (1.0 - _ALPHA) * gpi_rate

        # ── Thalamus: bias minus GPi inhibition (disinhibition = selection) ──
        thal_net = np.clip(THAL_BIAS - GPi_THAL_W * self.gpi_trace, -1e-4, 1e-4)
        I_thal   = np.repeat(thal_net, N_PER)
        thal_sp  = self.thal.step(I_thal)
        thal_rate = thal_sp.reshape(N_ACTIONS, N_PER).mean(axis=1)
        self.thal_trace = _ALPHA * self.thal_trace + (1.0 - _ALPHA) * thal_rate

        selected = int(np.argmax(self.thal_trace))
        self.action_history.append(selected)
        self.utility_history.append(utility.copy())

        return selected, self.thal_trace

    @property
    def selected_action_name(self) -> str:
        if not self.action_history:
            return "NONE"
        return self.ACTIONS[self.action_history[-1]]

    def get_utility_array(self) -> np.ndarray:
        """Return full utility history as (T, N_ACTIONS) array."""
        if not self.utility_history:
            return np.zeros((0, N_ACTIONS))
        return np.array(self.utility_history)

    def get_action_array(self) -> np.ndarray:
        """Return action history as (T,) integer array."""
        return np.array(self.action_history, dtype=int)
