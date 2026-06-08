"""
Synthetic spike-train generator.

Produces biologically-plausible spike patterns for:
  - Poisson spike trains (background / general firing)
  - Theta-modulated sequences (HC, 8 Hz)
  - Gamma bursts (PFC, 40 Hz)
  - Sharp-wave ripples (SWR, 150 Hz)
  - Population patterns for cognitive tasks (Cat / Dog / Noise)

All rates in Hz; output is a binary spike vector at each time step.
"""

import numpy as np


class SpikeGenerator:
    """Generates synthetic neural spike trains."""

    def __init__(self, n_neurons: int, dt: float, seed: int = 0):
        self.n  = n_neurons
        self.dt = dt
        self.rng = np.random.default_rng(seed)

        self._base_rate = np.full(n_neurons, 5.0)   # Hz baseline

    # ── primitive generators ──────────────────────────────────────────────────

    def poisson(self, rates: np.ndarray) -> np.ndarray:
        """
        Inhomogeneous Poisson spikes from per-neuron firing rates [Hz].
        Returns binary (0/1) spike vector.
        """
        probs = 1.0 - np.exp(-rates * self.dt)
        return (self.rng.random(self.n) < probs).astype(float)

    def theta_modulated(self, base_rates: np.ndarray,
                        t: float, theta_freq: float = 8.0) -> np.ndarray:
        """
        Poisson spikes amplitude-modulated by a theta oscillation.
        Neurons fire preferentially near the trough (standard HC model).
        """
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
        """
        SWR event: high-frequency burst in a subset of neurons.
        active_neurons: boolean mask of which neurons participate.
        """
        ripple_mod = max(0.0, np.sin(2 * np.pi * ripple_freq * t))
        rates = np.where(active_neurons, peak_rate * ripple_mod, 2.0)
        return self.poisson(rates)

    # ── cognitive pattern generators ──────────────────────────────────────────

    def pattern_spikes(self, pattern_id: int,
                       t: float, noise: float = 0.1) -> np.ndarray:
        """
        Generate spikes encoding a discrete cognitive pattern.

        Pattern layout (N_INPUT = 32 assumed):
          pattern 0 ("Cat"): neurons  0-15 active  (~30 Hz)
          pattern 1 ("Dog"): neurons 16-31 active  (~30 Hz)
          Background:  all neurons at ~5 Hz

        Parameters
        ----------
        pattern_id : int   0 = Cat, 1 = Dog
        t          : float current time for oscillation pacing
        noise      : float fraction of neurons with added background noise

        Returns
        -------
        spikes : (n,) binary spike vector
        """
        rates = np.full(self.n, 3.0)    # background

        half = self.n // 2
        if pattern_id == 0:             # Cat: first half
            rates[:half] = 35.0
        elif pattern_id == 1:           # Dog: second half
            rates[half:] = 35.0

        # add noise spikes from random neurons
        n_noise = int(self.n * noise)
        noise_idx = self.rng.choice(self.n, n_noise, replace=False)
        rates[noise_idx] = np.maximum(rates[noise_idx], 10.0)

        # theta-phase modulation
        return self.theta_modulated(rates, t)

    def delay_activity(self, t: float,
                       wm_pattern: np.ndarray | None = None) -> np.ndarray:
        """
        Low-rate spontaneous activity during delay period.
        Optionally biased by working-memory pattern.
        """
        rates = np.full(self.n, 2.0)
        if wm_pattern is not None:
            rates += 8.0 * wm_pattern[:self.n]
        return self.poisson(rates)

    def swr_event(self, replay_pattern: np.ndarray, t: float) -> np.ndarray:
        """
        Sharp-wave ripple encoding a stored pattern.
        replay_pattern: (n,) binary mask of reactivated neurons.
        """
        active = replay_pattern > 0.5
        return self.sharp_wave_ripple(active, t, ripple_freq=150.0)

    # ── task schedule ─────────────────────────────────────────────────────────

    def dms_schedule(self, total_steps: int
                     ) -> list[tuple[str, int, int, int | None]]:
        """
        Delayed Match-to-Sample (DMS) trial schedule.

        Returns list of (phase, start_step, end_step, pattern_id):
          "sample"  — present sample stimulus
          "delay"   — blank delay
          "test"    — present test stimulus (same or different)
          "iti"     — inter-trial interval
        """
        dt       = self.dt
        t_sample = int(0.100 / dt)   # 100 ms
        t_delay  = int(0.200 / dt)   # 200 ms
        t_test   = int(0.100 / dt)   # 100 ms
        t_iti    = int(0.100 / dt)   # 100 ms
        trial_len = t_sample + t_delay + t_test + t_iti

        schedule = []
        step = 0
        trial = 0
        while step + trial_len <= total_steps:
            sample_id  = trial % 2               # alternate Cat / Dog
            match_test = self.rng.random() < 0.5
            test_id    = sample_id if match_test else (1 - sample_id)

            schedule.append(("sample", step,                    step + t_sample,  sample_id))
            schedule.append(("delay",  step + t_sample,         step + t_sample + t_delay, None))
            schedule.append(("test",   step + t_sample + t_delay,
                             step + t_sample + t_delay + t_test,  test_id))
            schedule.append(("iti",    step + t_sample + t_delay + t_test,
                             step + trial_len,  None))
            step  += trial_len
            trial += 1

        return schedule
