"""
Global parameters for the Recurrent Memristive Neuromorphic System simulation.
All values in SI units unless noted.
"""

# ── Time ─────────────────────────────────────────────────────────────────────
DT     = 1e-4    # s  (0.1 ms time step, 10 kHz)
T_SIM  = 5.0     # s  total simulation duration

# ── Network dimensions ────────────────────────────────────────────────────────
N_INPUT = 32     # input encoding neurons
N_HC    = 64     # hippocampal reservoir units
N_PFC   = 32     # prefrontal cortex working-memory units
N_OFC   = 16     # orbitofrontal cortex value units
N_EC    = 16     # entorhinal cortex grid units (4×4)

# ── Physics ───────────────────────────────────────────────────────────────────
TEMP    = 310.0       # K  body temperature
KB      = 1.38e-23    # J/K
Q_ELEM  = 1.60e-19    # C
KT_Q    = KB * TEMP / Q_ELEM   # ~0.0267 V thermal voltage

# ── Volatile memristor  (Hippocampus — short-term)  ──────────────────────────
# Ion-diffusion dominant; fast spontaneous decay.
VOL = dict(
    G_on      = 1e-4,    # S  ON-state conductance
    G_off     = 1e-9,    # S  OFF-state conductance
    tau_diff  = 0.05,    # s  diffusion decay (50 ms → volatile)
    eta0      = 2e-3,    # ion hopping rate prefactor [s⁻¹V⁻¹]
    V0        = 0.08,    # V  characteristic hopping voltage
    noise_amp = 0.005,   # filament stochastic noise amplitude
)

# ── Semi-volatile memristor  (OFC — medium retention) ────────────────────────
SEMIVOL = dict(
    G_on      = 1e-4,
    G_off     = 1e-9,
    tau_diff  = 0.50,    # s  (500 ms)
    eta0      = 8e-4,
    V0        = 0.12,
    noise_amp = 0.002,
)

# ── Non-volatile memristor  (PFC — long-term) ────────────────────────────────
NONVOL = dict(
    G_on      = 1e-4,
    G_off     = 1e-9,
    tau_diff  = 1e6,     # s  effectively permanent
    eta0      = 3e-4,
    V0        = 0.18,
    noise_amp = 0.0,
)

# ── LIF neuron layer ──────────────────────────────────────────────────────────
LIF = dict(
    tau_m   = 0.020,   # s  membrane time constant
    V_rest  = -0.070,  # V
    V_th    = -0.055,  # V  spike threshold
    V_reset = -0.080,  # V  post-spike reset
    R_m     = 1e8,     # Ω  membrane resistance
    t_ref   = 0.002,   # s  refractory period
)

# ── STDP ─────────────────────────────────────────────────────────────────────
STDP = dict(
    A_plus    = 0.030,   # strong enough to overcome volatile diffusion
    A_minus   = 0.025,
    tau_plus  = 0.020,   # s
    tau_minus = 0.020,   # s
)

# ── Oscillation frequencies ───────────────────────────────────────────────────
FREQ = dict(
    theta = 8.0,    # Hz  hippocampal theta
    gamma = 40.0,   # Hz  PFC gamma
    swr   = 150.0,  # Hz  sharp-wave ripple
    grid  = 4.0,    # Hz  EC grid oscillation base
)

# ── Reward / neuromodulation ──────────────────────────────────────────────────
REWARD = dict(
    gamma_td  = 0.95,   # TD discount factor
    alpha_td  = 0.01,   # TD learning rate
    dopamine  = 1.0,    # baseline neuromodulation gain
)

# ── Spike encoding ───────────────────────────────────────────────────────────
V_SPIKE_WRITE = 0.15   # V  write pulse per spike (STDP)
V_SPIKE_READ  = 0.05   # V  read pulse — strong enough to drive LIF, weak enough not to set memristor
