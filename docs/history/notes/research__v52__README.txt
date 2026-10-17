# V52 — Physical dynamics as computation

Question: can a neuron–continuous-state SoC reduce the cost of repeatedly replaying neural perturbation experiments, where per-neuron spiking trajectories are the required output?

Open `report.html`. It embeds an actual simulation replay and an interactive physical-cost calculator. All three figures have PNG, editable SVG and vector PDF exports in `figures/`.

## Main model

- `model_source/model40.py`: unchanged V40-lineage construction and run interface, copied from V51.
- `model_source/engine40.py`: full 12-compartment spiking kernel, copied unchanged from V51. V51 adds a normalization option that is disabled here.
- `parent/` and `config/`: local frozen dependencies/configuration.
- `src/calibrated_workload.py`: application configuration. Type-aggregate ER4d/EPG counts map to weighted recurrent events; the chip is not redefined as a fly brain.
- `src/causal_probe.py`: fresh matched causal experiments.
- `src/physics52.py`: SI-unit design scenarios and all physical assumptions.

The particular successful V40 lineage is a nonrotating scalar continuous-state network, not an established oscillatory-wave advantage. Its local emission and feedback path remain in the neuronal kernel. The continuous state is not fed to the task output.

## Data and limitations

Dataset: male-cns:v1.0, type explorer snapshot 2026-09-09. Sources are saved locally with SHA-256 in `data/PROVENANCE.json`. Four published type-to-type totals are real; the per-cell graph is a **uniform-block approximation**. There are 26 ER4d and 46 EPG representative instances, without individual biological IDs. Signs derive from the presynaptic type. This is not a neuron-resolved FlyWire reconstruction and not validated against physiology.

Conductance formula: for directed type pair a→b, every possible non-self pair receives `count(a,b)/number_of_pairs * .02` in `rr`. The inherited kernel multiplies `rr` by `.01`, then `8`, before synaptic-filter injection. This is a fixed engineering scale. The old provenance phrase “normalized by mean incoming counts” should be read as a metadata wording error: the implemented formula normalizes by possible pairs, not each postsynaptic total.

The inherited learned associative-memory route is disabled in this workload. Plasticity, adaptation efficacy and learning energy are not evaluated. The full array contains 256 main cells + 80 inhibitory cells; 72 main cells are driven, others have disabled soma thresholds. All main filter/dendrite banks are nevertheless budgeted physically.

## Protocol and results

- First failed low-drive calibration and evaluation: `PROTOCOL.json`, `results/freeze.json`, original 523xx NPZ files. Most mapped cells were silent. Preserved unchanged. Initial refinement correlation is undefined (JSON NaN) due zero variance; it is not claimed as a pass.
- New pilot 52501, training 52511, validation 52611. Candidates 20/40/80; validation freezes 20. Fresh test 52701–52708 in `experiments/calibrated/`.
- Unchanged parameters, expanded causal follow-up 52901–52908: `experiments/causal/`. Six conditions × eight seeds = 48 episodes, each 500 biological ms.
- Numerical refinement 52801, 0.25 vs 0.125 ms: correlation .9044 in 10-ms spike bins, .2917 per-neuron count MAE. This is not exact event-time convergence.
- Warm host benchmark: 3 repeats on each of the eight same-input seeds, wave tracing disabled; all outputs checked against saved spikes. No host power measurement.

Only input spikes, static circuit parameters and prespecified interventions drive the dynamics. No target labels, numerical wave decoder or task-aware output correction is used. The graphical wave display is a numerical diagnostic and not included in chip output or its readout budget.

## Physics scenarios

The central case uses 0.2-pF state capacitance, 1 V, 300 K, subthreshold slope factor 1.5, 30× bias/topology overhead, 50-µW fixed overhead, 20-pJ local/event delivery and 20-pJ interface bit energy. 100-Mbit/s link, 20-µs reset, 6-bit recurrent weights, 16-bit routing entries, 100-pJ conductance program operation amortized over 1,000 episodes.

`gm = C*a/tau_bio`; `Ibias ≈ n*UT*gm`; integrate bias power for `Tbio/a`. Energy includes bias, event delivery, I/O, fixed overhead, reset and amortized programming. All numbers are **design scenarios**. No PDK, SPICE transistor netlist or silicon characterization is present. A 30× multiplier is not a calibrated transistor implementation. Leakage, parasitics, nonlinear gain and mismatch could change feasibility. Full ADC tracing, active learning, uncharacterized calibration and total transistor/routing area need separate measurements.

Digital comparison: selected continuous scalar states × numerical steps × effective energy per update, plus the same scenario event/I/O costs. This is not measured DRAM traffic or a benchmark against a named CPU/GPU/neuromorphic chip. Event-driven digital algorithms can reduce updates. The compiled host wall time is a separate measured reference, without power claims.

## Reproduction

Copy this entire revision to a **new folder** before running scripts that write results. Previous revisions and failed experiments must remain intact.

Dependencies: Python 3.11, NumPy, SciPy, Numba, BeautifulSoup4, lxml, Matplotlib. The session used `/tmp/wave-v7-env/bin/python`; Numba dependencies under `/tmp/wave-v50-deps`.

```
OPENBLAS_NUM_THREADS=1 python src/calibrated_workload.py
OPENBLAS_NUM_THREADS=1 python src/causal_probe.py
OPENBLAS_NUM_THREADS=1 python src/benchmark_host.py
OPENBLAS_NUM_THREADS=1 python src/physics52.py
MPLBACKEND=Agg OPENBLAS_NUM_THREADS=1 python src/report52.py
python src/build_page.py
python src/verify52.py
```

No download is necessary to reproduce the saved type-aggregate workload. The frozen source HTML is included. Full individual adjacency is intentionally not claimed.

## Design target

At assumed 100× acceleration: ~5.19 ms and ~2.74 µJ per 500-ms replay, with low/high energy scenarios ~0.34/29.05 µJ. This is ~17× faster than the present compiled Mac implementation and ~12.5× less energy than the **assumed** 1-pJ/update digital reference. The advantage changes sign below ~0.038 pJ/effective update in the central case. For live sensors, acquisition time cannot be accelerated.

The current application demonstrates response sensitivity to perturbation, not superior biological fidelity. Feedback-off leaves intact spikes unchanged but alters many lesion responses. Existing accelerated analog systems such as BrainScaleS-2 are relevant comparators, so this chip is not the only possible solution.
