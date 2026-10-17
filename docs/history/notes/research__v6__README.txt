# Wave Cognition v6

This revision preserves all previous models. Create v7 for future changes; do not overwrite v6 after delivery.

## Deliverables

- `Wave_Cognition_v6_Research_Report.docx`: editable 14-page report, with six figures, captions and references.
- `report.html`: browser version of the same report.
- `src/model.js`: frozen v5 behavioral engine for historical cognitive fixture export.
- `src/eeg_core.cpp`: v6 application model; distinct from the v5 task engine and from the ngspice circuit.
- `results/eeg-scores.json`: 69 classifier score records, some reusing the same simulated features.
- `results/audit.json`: paired effects, feature equivalence, input/weight hashes and circuit check.
- `results/reference-check.json`: explicit individual-synapse reference versus compiled pooling.
- `circuit/results.json`, `circuit/matrix-results.json`: executed behavioral circuit results.
- `circuit/cadence/`: unexecuted Spectre wave-port decks and 128 cognitive ablation specifications.

## Evidence boundaries

Real UCI EEG data, software predictions, CPU timings and ngspice traces were generated. Spectre was unavailable; no PDK, transistor circuit, silicon energy or ASIC latency was measured. The ngspice neuron macro is normalized and differs from the voltage model used in the EEG and historical tasks. The 64-node circuit test has waves only, whereas the 4,096-node EEG model has both layers.

The main benchmark runs six gain-calibration simulations and 36 primary scale simulations, plus nine ablations and six robustness simulations. Three wiring seeds are not three participants. The EEG recording is single-session, with chronological train/validation/test and marked class distribution shift. The 4,096-neuron wave improvement is small and conditional; the random forest is stronger on this test block.

## Reproduce in a new revision folder

Install Python with numpy, scipy, scikit-learn and matplotlib, a C++17 compiler, ngspice, and Node for historical fixture export. `versions.json` records the measured environment. Commands below assume this folder as working directory; run in a copied new revision if preserving the delivered results.

```sh
clang++ -O3 -std=c++17 src/eeg_core.cpp -o src/eeg_core
python3 src/prepare_eeg.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 src/eeg_bench.py
OPENBLAS_NUM_THREADS=1 python3 src/reference_check.py
python3 src/circuit_bench.py
python3 src/circuit_matrix.py
python3 src/wave_circuit_scale.py
python3 src/cpu_benchmark.py
python3 src/audit_v6.py
node src/export_cadence.js
python3 src/cadence_deck.py
python3 src/figures.py
python3 src/report.py
```

The report authoring script requires python-docx. DOCX rendering used Codex's bundled document renderer and LibreOffice. Source data are the UCI EEG Eye State dataset, Oliver Roesler (2013), DOI 10.24432/C57G7J, CC BY 4.0. The original archive and its SHA-256 are stored under sources and results/eeg-data.json. No labels are passed into either dynamical simulator.

`eeg_bench.py` caches completed simulation features by configuration. To change model equations or parameters, use a new revision and clear that new revision's old cache before rerunning. Do not treat an old feature file as evidence for modified code.

The compact ZIP omits large EEG feature binaries, redundant weights, QA page images and compiled executables. Those raw files remain in this full revision directory and can be regenerated from the included code and data.
