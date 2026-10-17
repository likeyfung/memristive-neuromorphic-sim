# V20: train, calibrate, freeze, test

Run `OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/experiment.py` from this folder. Each execution creates a timestamped results folder. Earlier revisions remain unchanged.

The unchanged V19 topology has 256 reduced 12-compartment neurons, 16 shared WaveTiles, 1,024 local recurrent spike connections and 256 interpopulation spike connections. External integer presynaptic events enter AMPA/NMDA filters, dendrites and somata. Population soma spikes excite their own local oscillator; intertile waves pass through reciprocal couplers. Local phase-sensitive feedback modulates neurons. The global source remains off.

V20 calibrates eight parameter presets independently for hybrid, spike-only and leaky-feedback models. One preset reproduces the V19 selected parameters; seven are seeded sparse-activity candidates. This is a limited random search, not a comprehensive optimization. No recurrent synaptic learning, BPTT, STDP or learned topology is implemented. Training consists of operating-point calibration and ridge readout fitting.

Input gain scales released conductance after valid integer event injection, independently of recurrent event weights. E/I ratio scales inhibitory recurrence; AMPA/NMDA decay, wave feedback, frequency and damping vary. The topology, input contact map and phase preferences remain identical.

Task: independent binary symbols on two channels, refreshed every 20 ms and encoded into four Poisson spike channels. At symbol boundaries, neuron-derived 20-ms filtered spike outputs reconstruct two channels at six delays (0–100 ms) and classify the product of current channel 0 and previous channel 1. Six initial symbols are discarded. This is synthetic temporal decoding, not EEG or a brain-cognition demonstration.

Eight streams train readouts; four independent streams select ridge regularization and operating points. The selection objective is memory score / 12 + nonlinear accuracy + 0.1 min(PR / 32,1) - max(rate - 60,0) / 300. PR is calculated on standardized training neuron traces. Every model gets the same search budget. Selected models are refitted at 0.0625 ms. Serialized parameters, scalers and readouts are hashed and frozen before generating 24 test streams. The final test is never used to retune the model.

Memory score is a finite set of held-out lag reconstruction scores: sum max(0,R²) across 12 targets. This is not total information capacity or bits of RAM, and clipping introduces positive selection bias. PR is covariance participation ratio, not a count of neurons with meaningful semantics. A fixed 20-ms readout trace itself supplies memory and is included in every neuron-readout comparison.

Leaky control disables both rotation and neighbor wave coupling; it is a local nonoscillatory feedback control, not a frequency-only or equal-active-state control. Causal ablations retain hybrid parameters AND its frozen readout, whereas independently calibrated baselines are separate comparisons. Confidence intervals resample complete streams.

Software runtime is measured host simulation time, not circuit latency. No ASIC power, energy, area, RAM traffic or speedup has been measured. Analog state and programmed weights are storage. A waveform emulation in software does not establish an advantage over an optimized digital task algorithm.
