# V58 — Three prespecified tests, with fair controls and electrical stress

English report: report.html. Earlier revisions are preserved.

Lineage: the V40/V51 learned-memory configuration of the neuron/shared-state architecture, not V52's aggregate fly workload. 256 main neurons, 80 inhibitory neurons, 16 scalar states. The compact solver retains equivalent grouped branches of the full twelve-compartment model.

Main source: src/model40.py, src/engine40.py, src/engine40_compact.py.
Task/perturbations: src/experiment58.py. Training: src/calibrate58.py. Fresh tests: src/test58.py.
Electrical source: ngspice/lib/; executed decks: ngspice/benches/.

Dependencies: Python 3, numpy, scipy, numba, matplotlib; ngspice 46 for electrical tests.
Reference environment: /tmp/wave-v7-env/bin/python with PYTHONPATH=/tmp/wave-v50-deps.
The local runner also adds its own src directory to PYTHONPATH.

## Re-run without overwriting delivered results

    python3 run.py

Creates runs/<UTC timestamp>/ and copies the self-contained sources, parent constructor dependency tree, config, references and circuit libraries there. Full calibration, freeze, fresh evaluation and circuit tests execute in that new folder. Equivalent seeded reproduction is not a new statistical holdout. For a new scientific revision, predeclare new seeds and a new revision folder before evaluation.

For just regenerating figures/report, do this in a copied folder:

    python3 src/analyze58.py
    python3 src/cost58.py
    python3 src/plot58.py
    python3 src/report58.py

## Result boundaries

- 12 candidates/family on training, top 3 on separate validation. Freeze all six final memory-set weights before fresh test histories.
- 384 nominal/intervention episodes, 1,584 stress episodes, 14 ngspice transients.
- Hidden scalar state, no wave decoder. All behavioral scores use neuronal spikes.
- Paired probes have bit-identical current input from 60 ms onward; only earlier history-port identity changes.
- All selected configurations have reader emission OFF: this is writer-population → shared state → reader-population, not evidence that reciprocal reader emission is beneficial.
- Circuit and behavioral noise/offset levels are engineering assumptions; no PDK noise or measured process statistics.
- Model mismatch is uncompensated variation after ideal training/calibration.
- Energy is a conditional event-budget calculation; no measured supply energy or DRAM counters.
- Additional files after the source freeze are analysis, plotting, reporting and verification; the frozen model/training/test sources and weights remain unchanged.
