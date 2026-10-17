# V10: circuit-oriented spike/wave co-computation

Open `report.html` for measured results and figures; read `DESIGN_V10.md` for architecture, equations, future Verilog-A ports, and limitations.

Model: `src/model_v10.py`, full neuron tile: `src/tiles.py`.
Recommended final profiles: `results/sequential_optimized_configs.json` (load = 0.01/ms at 8×8, 0.04/ms at 16×16 and 32×32). The earlier common-load profiles remain in `results/recommended_configs.json`.
The CircuitConfig defaults intentionally keep the unloaded reference for reproducing the optimization history. Use the recommended profile explicitly for the loaded design. `checkpoints/unloaded/` preserves the initial v10 model. V9 and earlier revisions are untouched.

Quick run (creates a fresh timestamped result folder):

```sh
python run_v10.py --side 8 --seed 801
```

Example:

```python
import json, sys
sys.path.insert(0, 'src')
from model_v10 import CircuitConfig
from experiment import run
config = CircuitConfig(**json.load(open('results/sequential_optimized_configs.json'))['8'])
result = run(side=8, cfg=config, seed=701)
print(result['accuracy'], result['answers'])
```

Run from this directory with Python 3, NumPy and Matplotlib. The local environment used here is `/tmp/wave-v7-env/bin/python`.

Reproduce the stages in order:

```sh
python src/bench.py
python src/calibrate.py
python src/load_probe.py
python src/final_bench.py
python src/scale_load_search.py
python src/validate_recommended.py
python src/verify.py
python src/export_trace.py
python src/report.py
```

Results:

- `bench.json`: unloaded reference, scale, state interventions, delay and stress probes.
- `calibration_search.json`, `selected_configs.json`, `calibrated_test.json`: bounded coupling/phase calibration and held-out nominal evaluation.
- `load_search.json`, `sequential_test.json`: output-load search and first two-query validation at 8×8.
- `recommended_configs.json`: profiles with selected coupling and a common 0.01/ms output load.
- `final_bench.json`, `final_sequential.json`: final common-load nominal, causal, stress and sequential tests.
- `scale_load_search.json`, `scale_load_test.json`, `sequential_optimized_configs.json`: separate scale-specific output-load experiment; do not conflate these profiles with the common-load stress benchmark.
- `recommended_validation.json`: final sequential validation with timing jitter, seeds 701–703.
- `verification.json`: numerical and interface checks, including the unloaded repeated-query failure.
- `demo_trace.json`: actual sampled 8×8 loaded trajectory used for plots.
- `manifest.json`: hashes and environment.

Times and currents/voltages are normalized behavioral-model quantities. No transistor-level or measured silicon results, hardware speedup, total RAM elimination, or unique computational advantage are claimed. A 1,024-tile experiment still stores only two items. Held-out seeds vary timing or engineering perturbations; the logical truth table is enumerated during calibration.
