# V45 — real connectivity, explicit spiking blocks

Main implementation: `src/model.py`. Architecture: `DESIGN.md`. Results: `report.html`.

The imported graph is female FAFB v783, not the male fly connectome. Neuron IDs, directed anatomical counts and predicted transmitters are real; physiological parameters, angular tuning and motor mapping are engineering assumptions.

## Reproduce without overwriting this frozen revision

Copy the entire folder to a new revision or timestamped directory first. Run there, with Python, NumPy and Matplotlib installed:

```
python src/import_connectome.py
OPENBLAS_NUM_THREADS=1 python src/experiment.py
OPENBLAS_NUM_THREADS=1 python src/extra_validation.py
MPLBACKEND=Agg python src/report.py
python src/checks.py
```

Import uses included public source exports. Experiment performs train/validation selection before testing. It writes results into its own copied directory; do not rerun in the frozen historical folder. No imported mutable prior-revision models.

Read `results/frozen.json`, `PROTOCOL.json` and `data/PROVENANCE.json` for configuration, hashes and data assumptions. Figure PNG/SVG/PDF files are in `figures/`.

## Interpretation

This revision does not pass navigation, useful learning, precise spike-timing convergence, biological response validation, or physical energy/latency acceptance. Same-step event accumulation is a numerical consistency check, not biological validation. The Verilog-A files are uncompiled block sketches and are not a complete ASIC.
