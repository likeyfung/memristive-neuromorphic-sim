# V16: benchmark the preserved V15 engine

The neuron and wave engine is copied unchanged from V15. This folder adds a
synthetic context-dependent spike decoder and digital streaming controls.

Run from this folder with Python, NumPy and scikit-learn:

```
OPENBLAS_NUM_THREADS=1 python src/bench.py
python src/report.py results/TIMESTAMP_PRINTED_BY_BENCH
```

Every benchmark creates a new timestamped result folder. Training: 128 trials;
validation: 64; held-out test: 128. Models and regularization are selected using
training/validation only. Hardware parameters are illustrative and fixed.
Input events are saved with latent variables and targets for reproduction.
The encoder reads only events, never those labels.

The task is a binary context-dependent action decoder: an earlier noisy cue
specifies whether a later probe maps to action 0 or action 1. Target = cue XOR
probe. Balanced intervening spikes are distractors. It is a synthetic mechanism
benchmark, not recorded neural data, EEG or a clinical BCI benchmark.

Readout uses actual per-neuron spike counts from 100 to 140 ms. No direct wave
readout. Only a linear classifier is trained; no claim that the fixed coupling
or phase configuration is optimized. All causal ablations use identical input
trains and synaptic mapping. Two evaluations are reported: an independently
refitted readout and the frozen full-model readout.

CPU timing excludes acquisition of the 140 ms stream, training, disk I/O and
input loading. V15 timing includes dense integration and input expansion; the
counter baseline operates event by event. Wall time is host software time,
not an ASIC measurement. Float32 state accounting is a capacity scenario,
not a test of quantized accuracy. The executable simulator uses float64.
