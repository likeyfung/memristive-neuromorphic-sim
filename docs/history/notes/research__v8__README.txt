# Wave Cognition v8

This revision replaces v7's ideal wave write and read interfaces with an explicit neuron-tile behavioral simulation. The trained v7 wave engine and coupler checkpoints are frozen unchanged.

Start with `report.html`, then `DESIGN.md` and `src/neuron_wave.py`.

## Model and resources

- 64 or 256 wave sites, with two opponent neuron tiles per site: 128 or 512 neurons.
- Each neuron: 24 stochastic AMPA/NMDA contacts, three dendritic compartments and a threshold/reset/refractory soma.
- Soma spikes drive a finite local emission-current pulse with fixed polarity.
- A finite-bandwidth local wave detector drives dendrite and soma feedback.
- The answer is determined only by output-population spike counts. Ties/silence are failures.
- All inter-node wave transfer uses the frozen phase-selective couplers.
- No coupling retraining, transistor implementation, ASIC energy measurement or real-world BCI claim.

## Reproduce in a new folder

Preserve v8. Copy it to a new numbered revision before regenerating outputs. Scripts resolve their revision folder from their own path and do not import a mutable shared model.

Dependencies used: Python 3.11, NumPy, SciPy, PyTorch 2.14.0, Matplotlib. The session used `/tmp/wave-v7-env/bin/python`. That temporary environment is not a permanent dependency; another environment with these libraries can run the code.

From the copied revision:

```sh
python src/bench.py
python src/retention.py
python src/verify.py
python src/demo.py
python src/demo_html.py
python src/export_stimuli.py
python src/report.py
```

The main suite has 90 runs, 256 episodes each, 15 conditions, two scales and three stimulus/release seeds. The three seeds do not represent independent coupling training. Couplers use v7 seed 1. Main time step is 0.125 ms. Runtime is minutes on the current host; wall times are simulation profiling, not chip latency.

`src/verify.py` additionally compares copied files with sibling v7 when run from the full project. If replaying a standalone package without v7, compare the saved SHA256 hashes in `results/verification.json` instead or restore the sibling v7 archive. Core model and benchmarks are self-contained.

## Evidence

- `results/bench.json`: all per-episode predictions, targets and output spike counts, conditions and configuration.
- `results/stimuli-*.npz`: exact presynaptic event times and release masks for the nominal benchmark.
- `results/demo.json`: eight counterfactual queries on one unchanged input episode.
- `results/trace-8.json`, `trace-16.json`: complete illustrative trajectories from held-out episodes.
- `results/retention.json`: separate 128-episode hold-duration tests.
- `results/verification.json`: engine/checkpoint preservation, zero-release test and time-step sensitivity.
- `results/pilot-*`: preliminary calibration/coarse-step results, not report evidence.
- `frozen/*.pt`: trained and fixed-wave checkpoints copied from v7.
- `figures/*.svg` and `*.png`: publication-style plots; captions in `figures/captions.json`.

Trace columns: time_ms, read_stage, selected_presynaptic_event, AMPA_difference_mean, NMDA_difference_mean, source_dendrite_mean, source_soma, source_spike, source_wave_I, output_wave_I, positive_read_dendrite_mean, positive_read_soma, positive_read_spike, positive_read_count, negative_read_soma, negative_read_spike, negative_read_count. Source trace during the read interval is diagnostic bookkeeping; the active source-neuron state is transferred to the reader bank. Output traces remain live. Wave coordinates are diagnostic and never enter the spike-count decoder.

## Interpretation

The wave-off neuron-only control is a matched disconnection test: this task topology has no alternate synaptic source-to-output route. It is not an optimized standalone neuron-only model. Fixed-wave failure partly reflects weak margins under a common neuronal threshold. These are causal controls, not proof of universal superiority.

Signed inputs use a conventional ON/OFF event encoder. The coherent reference remains ideal, and normalized voltage/current gains are not PDK-calibrated. Bidirectional operation is staged: write emission, hold, then feedback read with emission off. A physical chip still requires configuration memory, bias/reference distribution, output collection and input/output circuits.
