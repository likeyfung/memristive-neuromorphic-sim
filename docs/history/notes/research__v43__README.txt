# V43 — V42 navigation audit

Open `report.html` for figures and an interactive replay of recorded rate activity. Read `ASSESSMENT.md` for model/code distinctions and primary-source references.

The Desktop V42 package is untouched. `original/` is a local copy used for reproduction; `src/validate.py` implements matched-input testing using that copy, with no mutable imports from other research revisions. `PROTOCOL.json` fixes settings and seeds. `results/` contains all raw seed-level results and replay trajectories.

Run using NumPy/Matplotlib in the existing environment:

```bash
export MPLBACKEND=Agg
export MPLCONFIGDIR=/tmp/wave-v43-mpl
export XDG_CACHE_HOME=/tmp/wave-v43-cache
/tmp/wave-v7-env/bin/python research/v43/original/run.py reproduce
/tmp/wave-v7-env/bin/python research/v43/src/validate.py
/tmp/wave-v7-env/bin/python research/v43/src/checks.py
/tmp/wave-v7-env/bin/python research/v43/src/figures.py
/tmp/wave-v7-env/bin/python research/v43/src/report.py
```

Validation refuses to overwrite existing `audit.json`. For a new experiment, copy this entire revision to a fresh folder and use a fresh results directory. `checks.py` additionally verifies the supplied Desktop source remains unchanged. The animation is recorded simulation playback, not live fly or biological activity. No V42 wave implementation, Cadence model or connectome dataset was present in the supplied package.
