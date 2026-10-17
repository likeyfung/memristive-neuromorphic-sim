# V17 — concurrent dual-route streaming workload

This revision preserves V15's neuron and wave equations and tests a new network
mapping and workload. It does not use Python replay time as analog ASIC latency.

From this folder (Python + NumPy + scikit-learn):

```
OPENBLAS_NUM_THREADS=1 python src/bench.py
python src/workload.py results/TIMESTAMP
python src/diagnose.py results/TIMESTAMP
python src/global_check.py results/TIMESTAMP
python src/report.py results/TIMESTAMP
```

Each benchmark writes a fresh timestamped run. The report is also preserved in
that run; the revision landing report displays it. Earlier revisions remain
unchanged.

128 independent synthetic 500 ms streams: 64 train, 32 validation, 32 test.
Features and contexts change at separate random dwell times. Distractors and
context dropouts overlap continuous evidence. Decoder labels are never passed to
the physical model. Nine readouts per stream at 100,150,...500 ms. No dynamics
reset between decisions. Readout counters integrate the preceding 50 ms.

An A evidence population sends soma spikes to C over explicit event links.
A disjoint B context population emits into the wave mesh; C's neurons receive
local wave feedback. A also emits waves, so there can be alternate information
paths. The global source is off to test population-generated context without
external reference. This is not a claim that a global port is unnecessary.

The numerical solver splits coupled updates at dt=0.0625 ms; this approximates
concurrent dynamics, not a sequential clocked analog-chip architecture. A
half-step check on four independent test streams is reported.

Only C's six spike counters feed a trained linear readout. No wave or membrane
oracle. Analog weights and feedback phases are fixed, not trained. Spike links
use weight 0.6 (V16's disabled links had weight 0.04): this deliberate mapping
change gives the A→C pathway meaningful input strength and is not a measured
transistor parameter. Global/feedback parameters are saved in raw configuration.

A digital control maintains 12 leaky states (four channels at 30/100/250 ms) and
trains a static quadratic-feature readout. Both models see the same event stream
and decision deadlines. Compute replay time, logical state capacity, and
conditional update-energy arithmetic are reported separately. No measured
hybrid-chip power, physical area, or decision latency is available.
