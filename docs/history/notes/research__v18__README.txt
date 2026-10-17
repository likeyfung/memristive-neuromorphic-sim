# V18: clean routes and learned wave-conditioned evidence gates

Previous revisions are preserved. Model files are local to this revision. The
input.npz file is an exact copy of V17's dataset. No new test examples are claimed.

Run from this directory with Python 3, NumPy, scikit-learn:

```
OPENBLAS_NUM_THREADS=1 python src/run.py
python src/check.py results/TIMESTAMP
python src/lag_check.py results/TIMESTAMP
python src/report.py results/TIMESTAMP
```

Each run creates a fresh timestamped folder. The report is preserved there and
shown at this revision's report.html. The V17 code used for
workload utilities is copied as src/reference.py; actual neuron/wave imports
resolve to this revision's local engine.

Changes:
- Only B's soma spikes emit into the shared wave mesh. A and C emission is zero.
- A->C event links remain active, with the same input mapping and weight as V17.
- Additive feedback is disabled in this diagnostic to isolate multiplicative
  wave gating. Only C's basal synaptic evidence receives a learned gate.
- The gate is sigmoid(a_i I_k + b_i Q_k + c_i), evaluated from the filtered LOCAL
  I/Q state. It multiplies filtered basal synaptic drive after the inherited
  local nonlinear synaptic term, before dendritic integration.
- C neurons have fixed complementary context preferences; learned coefficients
  come from supervised local wave->context fitting on training streams only.
  Labels are never supplied to the model during inference.
- A six-setting pilot searches local frequency, decay and a common coupling
  magnitude. Individual edge phases and synaptic weights are not trained.

The pilot uses 16 training and 8 validation streams at dt=.125 ms, choosing mean
local context validation accuracy, not test accuracy or end-task accuracy.
Gate coefficients are then refitted using all 64 training streams at dt=.0625 ms.
Readouts use 64 training/32 validation streams; test contains 32 full streams.
Main results are conditional on this one known benchmark split. Earlier V17 test
results have already been seen; independent future data are needed to validate
any improvement after this iterative development.

This clean diagnostic intentionally removes the C->wave return path. It is not
an evaluation of the richest fully recurrent population-wave-population loop.
EMIT_OFF, SPIKE_OFF, COUPLER_OFF, WAVE_OFF, GATE_OFF and shuffled-gate controls
probe the new representation. Digital reference is unchanged from V17.

No transistor gate circuit, fixed-point precision, ASIC power or physical latency
is measured. Logistic coefficients may require large physical gains; units,
headroom, noise, coefficient quantization and area need circuit characterization.
