# V19: modular recurrent spike–wave reservoir

New revision; earlier models and results are preserved. `src/reservoir.py` is
the current model, `src/tiles.py` supplies synapse/dendrite/soma integration.

256 neurons form 16 populations of 16 neurons, each sharing one I/Q WaveTile.
Each neuron has four local outgoing recurrent edges (one ring edge plus three
random edges) and one outgoing event edge to a neighboring population. There
are 1,024 local and 256 inter-population edges, no autapses. 192 neurons have
excitatory outgoing synapses; 64 have inhibitory outgoing connections. Signs
are consistent per source. This is a chosen circuit abstraction, not an exact
anatomical cell-type ratio.

Excitatory recurrent arrivals are summed by neuron AND dendritic branch using
a sparse matrix, then injected into AMPA/NMDA states. Inhibitory arrivals use a
separate positive 5 ms current state delivered through inhibitory integration
paths. This avoids clipping negative events in excitatory filters. Delays are
2 ms. Multiple presynaptic sources correctly sum at a shared target.

Every population emits into its wave state; local waves feed back onto every
population. Feedback includes bounded additive current and a multiplicative
basal-evidence gate 2*sigmoid(aI+bQ), neutral at zero wave. Phases/gains are fixed
random settings. Neighbor waves use reciprocal I/Q couplers. Global source is
off. Event and wave networks operate throughout the stream.

Inputs are now distributed fixed random contact projections into the modular
population; the A/B/C feedforward roles are removed. All neurons' 20 ms filtered
spike traces feed a trained linear readout. The readout filter state is extra
storage/circuitry; no direct wave-state oracle is used.

Run with Python 3, NumPy, SciPy and scikit-learn:

```
OPENBLAS_NUM_THREADS=1 python src/run.py
OPENBLAS_NUM_THREADS=1 python src/refine.py results/TIMESTAMP
OPENBLAS_NUM_THREADS=1 python src/check.py results/TIMESTAMP
python src/diagnose_fine.py results/TIMESTAMP
python src/report.py results/TIMESTAMP
```

Each main run creates a new timestamped directory. Supplemental runs write into
the selected result folder. Four reservoir presets are selected using eight
training and eight validation streams at dt=.25 ms; main training uses 64
streams and validation 32, test 32. The dataset is the unchanged V17 synthetic
benchmark, not independent new data. Only readout weights are fitted; recurrent
weights/input masks are fixed. No BPTT, STDP, FORCE or e-prop is implemented.

The original .125 ms benchmark had substantial prediction sensitivity when the
step was halved. Refined .0625 ms comparisons and a .03125 ms check are reported
separately. Do not treat coarse results as numerically validated performance.
The simple nonoscillatory control also opens spatial couplers and has an
undriven Q state, so it changes more than frequency alone.

This is a normalized functional simulation, not a transistor schematic or a
hardware energy/latency demonstration. High firing rates, analog headroom,
configuration storage, routing, precision and stability require further work.
