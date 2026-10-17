# V40 — Distributed neural memory under endogenous modulation

**Behavioral research release. No measured ASIC, human-brain recording or consciousness claim.**

Start with `REPORT.md`, `ARCHITECTURE.md` and `RESULTS.json`. The primary cohort tests a spatially organized neuronal circuit. A separately frozen supplementary cohort tests recurrent read-current strength on partial-cue completion. V39's relative-phase task is preserved in the original supplied archive, not relabelled as this new task.

## Install and check

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py verify
python run.py test
python run.py replay --stage primary --seed 40611 --index 0
python run.py replay --stage content --seed 41011 --index 0
```

`verify` hashes the release files and checks the two pre-test freezes. `test` actually reruns examples and source/symmetry controls, rather than only reading old pass flags. JIT compilation occurs on the first neural call. `replay` prints actual new metrics and checks exact saved spike bins. Dependence-version differences may affect exact floating-point replay; `results/environment.json` records the tested installation.

A C compiler (`cc`) is needed only to build and compare the compact digital reference during the full primary protocol. No internet, PDK or proprietary simulator is required for the numeric replay.

## Non-overwriting full numerical reproduction

```bash
python run.py reproduce --output ../V40_new_run
```

This reruns the delivered deterministic development, validation, primary, stress and supplementary protocols in a new directory. Repeating those same histories is reproduction, not an independent confirmation. The command rejects an existing output directory. Figure/report rendering can be run separately from `src/plot40.py` and `src/report40.py` once numeric outputs exist.

## Active implementation

- `src/model40.py`: validated geometry, endogenous local source map, regional graph and compact/full forward interface.
- `src/engine40.py`: inherited full 12-compartment behavioral kernel plus the scalar modulation interface.
- `src/engine40_compact.py`: exact basal-group symmetry reduction to six independent compartments per main neuron.
- `src/tasks40.py`: input generator, never called inside the neuronal dynamics.
- `src/evaluate40.py`: fixed-weight paired comparisons and digital Python/C agreement.
- `src/content_gain40.py`: supplementary read-current search; `confirm_content40.py`: fresh confirmation.
- `src/digital40.c`: bit-packed event-driven exemplar reference.
- `src/audit40.py`: sources, spatial isolation, recurrent content and inhibitory controls.
- `src/refine40.py`, `src/refine_content40.py`: numerical-step and backend checks.

## Interpretation boundaries

The neuron count remains 336; it is not demonstrated to be minimal. Source signs, anatomical regions and feature addresses are designed. Local association acquisition still uses externally separated learning/recall modes and resets fast state between exposures. There is no online end-to-end reward learner, autonomous episode segmentation, learned temporal-sequence generator or world-model planner.

The compact digital reference learns observed templates and context from the same external events. It knows task port semantics and exposure boundaries. It is permitted an efficient algorithm; it is not forced to numerically emulate the neural circuit. Its state/weight payload is not its complete program memory. CPU timing is host execution, not analog-chip latency. Conditional energy calculations refer to a same-dynamics emulator, not to that small task-aware algorithm.

`history/spatial_mapping_failure/` retains a superseded initial run whose intended regions did not match the inherited tile ordering. The failed locality checks led to correction and entirely new test seeds. None of those obsolete scores is used as the corrected spatial result.
