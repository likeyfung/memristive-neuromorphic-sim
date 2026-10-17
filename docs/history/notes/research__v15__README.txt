# V15: heterogeneous feedback and factorial causality

V14's shared WaveTile topology is retained. `src/shared.py` adds I/Q detection,
per-neuron phase/gain, and independent basal/apical/soma gains in `src/tiles.py`.
Default coefficients recover homogeneous real-wave feedback. Tests use explicit
heterogeneous coefficients; these are illustrative, not trained.

From this folder, Python 3 with NumPy:

```
OPENBLAS_NUM_THREADS=1 python src/run.py
python src/report.py results/TIMESTAMP_PRINTED_BY_RUN
```

Every run creates a fresh timestamped directory. Reports preserve that run's
results while updating this revision's landing report. Previous revisions are
unchanged. No global drive, transistor simulation, learned task or power result
is implied. Wave state transplantation and EMIT-off probe are explicit causal
interventions; the natural-continuation control leaves EMIT on.

Biological current-based emission remains future work. The wave compresses
population context intentionally; individual identity remains in separate neuron
and synaptic states. Read report.html for scientific interpretation and limits.
