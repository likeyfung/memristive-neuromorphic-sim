"""
Synthetic spike-train generator with NEF population coding.

Encoding follows the Neural Engineering Framework (Eliasmith & Anderson 2003):
  - Each concept (Cat, Dog, ...) is a random unit vector in SP_DIM-dimensional
    space called a semantic pointer.
  - Each input neuron has a random preferred direction (encoder) in the same space.
  - Firing rate = base + peak * relu(encoder_i · semantic_pointer)
  - Two concepts with different semantic pointers produce distinct, decodable
    population patterns without any hardcoded neuron assignments.

Tasks supported:
  - DMS  (Delayed Match-to-Sample)
  - TOJ  (Temporal Order Judgment)
"""

import numpy as np

SP_DIM = 16   # dimensionality of semantic pointer space


class SpikeGenerator:
    """Generates NEF-encoded neural spike trains."""

    def __init__(self, n_neurons: int, dt: float, seed: int = 0,
                 sp_dim: int = SP_DIM):
        self.n      = n_neurons
        self.dt     = dt
        self.sp_dim = sp_dim
        self.rng    = np.random.default_rng(seed)

        # NEF encoder matrix: each row is a random unit vector (preferred direction).
        # Neuron i fires strongly when the current stimulus aligns with encoders[i].
        raw           = self.rng.standard_normal((n_neurons, sp_dim))
        norms         = np.linalg.norm(raw, axis=1, keepdims=True)
        self.encoders = raw / np.maximum(norms, 1e-8)   # (n, sp_dim) unit rows

        # Semantic pointer registry: concept_id → D-dim unit vector
        self._sp: dict[int, np.ndarray] = {}
        self._register(0)   # Cat
        self._register(1)   # Dog

    # ── concept registration ──────────────────────────────────────────────────

    def _register(self, concept_id: int) -> np.ndarray:
        v = self.rng.standard_normal(self.sp_dim)
        v /= np.linalg.norm(v)
        self._sp[concept_id] = v
        return v

    def register_concept(self, concept_id: int | None = None) -> int:
        """
        Register a new concept. No circuit changes needed — the spiking
        network automatically produces a new population pattern for any
        registered semantic pointer.
        """
        if concept_id is None:
            concept_id = max(self._sp) + 1 if self._sp else 0
        self._register(concept_id)
        return concept_id

    def get_semantic_pointer(self, concept_id: int) -> np.ndarray:
        """Return the semantic pointer vector for a registered concept."""
        return self._sp[concept_id].copy()

    # ── NEF population coding ─────────────────────────────────────────────────

    def nef_rates(self, concept_id: int,
                  peak_rate: float = 40.0,
                  base_rate: float = 3.0) -> np.ndarray:
        """
        NEF tuning-curve rates for a given concept.

        rate_i = base + peak · max(0, encoders[i] · sp[concept_id])

        Neurons with preferred directions aligned to the concept's semantic
        pointer fire near peak_rate; orthogonal neurons fire at base_rate.
        Since Cat and Dog semantic pointers are approximately orthogonal
        (random unit vectors in R^16), they produce largely non-overlapping
        activity patterns — decodable without hardcoded neuron assignments.
        """
        sp         = self._sp[concept_id]
        similarity = self.encoders @ sp             # (n,) ∈ [-1, 1]
        return base_rate + peak_rate * np.clip(similarity, 0.0, 1.0)

    # ── primitive generators ──────────────────────────────────────────────────

    def poisson(self, rates: np.ndarray) -> np.ndarray:
        """Inhomogeneous Poisson spikes from per-neuron firing rates [Hz]."""
        probs = 1.0 - np.exp(-rates * self.dt)
        return (self.rng.random(self.n) < probs).astype(float)

    def theta_modulated(self, base_rates: np.ndarray,
                        t: float, theta_freq: float = 8.0) -> np.ndarray:
        """Poisson spikes amplitude-modulated by theta oscillation."""
        mod = 0.5 + 0.5 * np.cos(2 * np.pi * theta_freq * t + np.pi)
        return self.poisson(base_rates * (0.2 + 1.6 * mod))

    def gamma_burst(self, base_rates: np.ndarray,
                    t: float, gamma_freq: float = 40.0) -> np.ndarray:
        """Poisson spikes paced by gamma oscillation (PFC)."""
        mod = 0.5 + 0.5 * np.cos(2 * np.pi * gamma_freq * t)
        return self.poisson(base_rates * (0.3 + 1.4 * mod))

    def sharp_wave_ripple(self, active_neurons: np.ndarray,
                          t: float, ripple_freq: float = 150.0,
                          peak_rate: float = 80.0) -> np.ndarray:
        """SWR event: high-frequency burst in a subset of neurons."""
        ripple_mod = max(0.0, np.sin(2 * np.pi * ripple_freq * t))
        rates = np.where(active_neurons, peak_rate * ripple_mod, 2.0)
        return self.poisson(rates)

    # ── cognitive pattern generators ──────────────────────────────────────────

    def pattern_spikes(self, pattern_id: int,
                       t: float, noise: float = 0.1) -> np.ndarray:
        """
        Generate NEF-encoded spike train for a given concept.

        Replaces the old hardcoded Cat=neurons 0-15 / Dog=neurons 16-31
        scheme. Now each neuron's firing rate is determined by its preferred
        direction relative to the concept's semantic pointer. Adding a third
        concept (Bird, Noise, etc.) requires only register_concept() — no
        changes to the circuit.

        Parameters
        ----------
        pattern_id : int   registered concept id (0=Cat, 1=Dog, ...)
        t          : float current time for theta modulation
        noise      : float fraction of neurons with added background noise
        """
        rates = self.nef_rates(pattern_id, peak_rate=40.0, base_rate=3.0)

        n_noise   = int(self.n * noise)
        noise_idx = self.rng.choice(self.n, n_noise, replace=False)
        rates[noise_idx] = np.maximum(rates[noise_idx], 10.0)

        return self.theta_modulated(rates, t)

    def delay_activity(self, t: float,
                       wm_pattern: np.ndarray | None = None) -> np.ndarray:
        """Low-rate spontaneous activity during delay period."""
        rates = np.full(self.n, 2.0)
        if wm_pattern is not None:
            rates += 8.0 * wm_pattern[:self.n]
        return self.poisson(rates)

    def swr_event(self, replay_pattern: np.ndarray, t: float) -> np.ndarray:
        """Sharp-wave ripple encoding a stored pattern."""
        active = replay_pattern > 0.5
        return self.sharp_wave_ripple(active, t, ripple_freq=150.0)

    # ── task schedules ────────────────────────────────────────────────────────

    def dms_schedule(self, total_steps: int
                     ) -> list[tuple[str, int, int, int | None]]:
        """
        Delayed Match-to-Sample (DMS) trial schedule.

        Returns list of (phase, start_step, end_step, pattern_id).
        """
        dt        = self.dt
        t_sample  = int(0.100 / dt)
        t_delay   = int(0.200 / dt)
        t_test    = int(0.100 / dt)
        t_iti     = int(0.100 / dt)
        trial_len = t_sample + t_delay + t_test + t_iti

        schedule: list = []
        step  = 0
        trial = 0
        while step + trial_len <= total_steps:
            sample_id  = trial % 2
            match_test = self.rng.random() < 0.5
            test_id    = sample_id if match_test else (1 - sample_id)

            schedule.append(("sample", step,                      step + t_sample,              sample_id))
            schedule.append(("delay",  step + t_sample,           step + t_sample + t_delay,    None))
            schedule.append(("test",   step + t_sample + t_delay, step + t_sample + t_delay + t_test, test_id))
            schedule.append(("iti",    step + t_sample + t_delay + t_test,
                             step + trial_len, None))
            step  += trial_len
            trial += 1

        return schedule

    def toj_schedule(self, total_steps: int
                     ) -> list[tuple[str, int, int, int | None, int]]:
        """
        Temporal Order Judgment (TOJ) trial schedule.

        Two stimuli are presented back-to-back. After a blank gap, the
        system must report which appeared first — testing temporal order
        memory, not just identity. HC's volatile memory (τ=50 ms) naturally
        provides this: stim_a's imprint decays during stim_b, creating an
        asymmetric HC pattern that encodes order.

        Each trial (350 ms total):
          stim_a (100 ms) → stim_b (100 ms) → blank (50 ms) → iti (100 ms)

        Returns list of (phase, start, end, pattern_id, toj_label):
          toj_label = 0  Cat appeared first (stim_a=Cat, stim_b=Dog)
          toj_label = 1  Dog appeared first (stim_a=Dog, stim_b=Cat)
        """
        dt        = self.dt
        t_a       = int(0.100 / dt)
        t_b       = int(0.100 / dt)
        t_blank   = int(0.050 / dt)
        t_iti     = int(0.100 / dt)
        trial_len = t_a + t_b + t_blank + t_iti

        schedule: list = []
        step  = 0
        trial = 0
        while step + trial_len <= total_steps:
            if trial % 2 == 0:
                a_id, b_id, label = 0, 1, 0   # Cat first
            else:
                a_id, b_id, label = 1, 0, 1   # Dog first

            schedule.append(("stim_a", step,           step + t_a,                a_id,  label))
            schedule.append(("stim_b", step + t_a,     step + t_a + t_b,          b_id,  label))
            schedule.append(("blank",  step + t_a + t_b,
                             step + t_a + t_b + t_blank, None, label))
            schedule.append(("iti",    step + t_a + t_b + t_blank,
                             step + trial_len, None, label))
            step  += trial_len
            trial += 1

        return schedule
