# Corrected V10 topology — V11

V10 is preserved. This self-contained revision replaces its phase-query gates with explicit global waveform coupling and uses spike trains as neural information inputs.

- Model: `src/model.py`
- Neuron: `src/tiles.py`
- Specification: `DESIGN.md`
- Results and figures: `report.html`

Run from this directory with Python, NumPy and Matplotlib:

```sh
python run.py --side 8
python run.py --side 16 --global-off
```

Each run creates a timestamped result directory. `--global-off` grounds the global source while leaving its coupling load connected.

Reproduce verification and figures:

```sh
python src/test_model.py
python src/feedback_check.py
python src/report.py
```

The local interpreter used is `/tmp/wave-v7-env/bin/python`.

Default dt is 0.0625 ms. `archive/model_coarse.py` and `results/coarse_*.json` preserve the coarse 0.25 ms prototype; `results/convergence.json` records the four-step comparison. The archived model uses the unchanged tile implementation in `src/tiles.py`.

No query-based recall score, transistor simulation, silicon energy advantage, or total RAM elimination is claimed for this revision. Read the report's scope and numerical limitations.
