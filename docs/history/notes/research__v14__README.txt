# V14 reproduction

Full current model: `src/shared.py` (shared wave array), `src/model.py`
(inherited coupler/configuration definitions), `src/compact.py` (filter
aggregation), `src/tiles.py` (neuron circuits as normalized equations).

Dependencies: Python 3, NumPy. From this directory:

```sh
OPENBLAS_NUM_THREADS=1 python src/run.py
# Use the timestamped output directory printed by the command above:
python src/population_test.py results/YOUR_TIMESTAMP
python src/convergence.py results/YOUR_TIMESTAMP
python src/report.py results/YOUR_TIMESTAMP
```

Each main execution saves in a fresh timestamped folder. Supplementary scripts
write inside the explicitly selected run. The report script writes a report in
that run and updates this revision's `report.html` to show the selected run.
Earlier revision folders are never modified.

Benchmarks use identical seeded input schedules and weights across each causal
ablation. Main scaling runs disable the global source and open its coupler;
the phase experiment explicitly enables it as a controlled intervention.
R=1 reproduces the inherited model exactly in the regression check.
No transistor, noise, training, EEG, task-accuracy or hardware-power result is
implied. Wall time is Python host time only.
