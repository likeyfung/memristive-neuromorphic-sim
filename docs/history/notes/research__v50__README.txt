# V50 — V40 circuit plus optional local recurrent regulation

Canonical circuit lineage: recovered V40, not V48/V49. Sources and local parent dependencies were copied from V40. The inherited V40 result archive is now `v40_results/`; its report is `V40_REPORT.html`. Those are historical evidence, not V50 results. The original copied MANIFEST/RESULTS and run.py describe V40; use the V50-specific files below for this revision.

Main interface: src/model40.py. Full kernel: src/engine40.py. Compact equivalent kernel: src/engine40_compact.py. Experiment: src/experiment50.py. New report: report.html. New protocol: PROTOCOL50.json.

The only neuronal-dynamics addition is a local activity sensor per tile:

    h_k ← h_k exp(-dt/100ms) + sum delayed local spikes ×1000/(100ms×population size)
    recurrent_read_current ← original_current / (1 + alpha h_k/20Hz)

Only learned recurrent read currents are scaled. Synaptic weights, sensory encoding, dendrites, somas, inhibitory populations, emission and wave coupling are preserved. Sensor uses local spike history, no labels or target. Alpha=0 removes its influence exactly. Sixteen added scalar sensors and corresponding analog division/gain-control circuitry would have cost; this is not a characterized transistor design.

This is a V42-inspired finite-time regulation experiment, not V42's instantaneous rate mean or a claim of identical algorithms. Normalization during acquisition is off, preserving V40 local association learning; inference gain is selected on validation. Existing episode resets and externally separated learn/recall modes remain.

Training/validation: one independently generated memory set each; alpha0/0.1/0.5; selection by validation F1 then fewer spikes. New test: four memory sets, four queries each. This limited search does not establish a global optimum. A separate moving sensory-input/dropout probe checks input compatibility; it is not heading estimation, steering, or closed-loop navigation. No new learned navigation weights are invented.

Reproduction: copy this revision to a new directory first. Requires NumPy, SciPy, Numba and Matplotlib. Run:

    OPENBLAS_NUM_THREADS=1 python src/experiment50.py
    MPLBACKEND=Agg python src/report50.py

Host execution is not ASIC latency. No energy advantage or biological fidelity is inferred.

## Preserved protocol correction
The first new cohort used an incorrect acquisition wrapper: recurrence remained ON and inference parameters were reused for acquisition. That run is retained in history50/acquisition_protocol_error and is excluded from conclusions. The corrected experiment calls the inherited experiment40.acquire/trials functions directly, restoring recurrence-OFF acquisition and V40's acquisition parameters. It uses wholly new train/validation/test seeds50501/50601/50701–50704 and sensory-probe seed50801. The circuit kernel was not changed after observing the failed cohort.
