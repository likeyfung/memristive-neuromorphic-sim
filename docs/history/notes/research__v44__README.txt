# V44: ASIC necessity and robustness experiment

- Main model: `src/model.py`
- Frozen protocol: `PROTOCOL.json`
- Reproduction and CPU timings: `src/experiment.py`
- Numerical/provenance checks: `src/checks.py`
- Report: `report.html`
- Raw data and environment: `results/summary.json`, `results/robustness.json`, `results/timing.json`
- Standalone figures: `figures/` (PNG/PDF/SVG)

The Desktop V42 and research V43 are preserved. All model imports are local. The model is the supplied reduced rate motif, not a new implementation of the unavailable parent V42 ASIC. No optimization or test-set tuning is performed.

From the workspace root:

```bash
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/wave-v44-mpl XDG_CACHE_HOME=/tmp/wave-v44-cache
/tmp/wave-v7-env/bin/python research/v44/src/experiment.py
/tmp/wave-v7-env/bin/python research/v44/src/checks.py
/tmp/wave-v7-env/bin/python research/v44/src/figures.py
/tmp/wave-v7-env/bin/python research/v44/src/report.py
```

The experiment refuses to overwrite existing summary results. Use a new copied revision and fresh results folder for a new run. Runtime depends on the machine and load; the saved values are measured CPU wall-clock data, not ASIC latency or energy.
