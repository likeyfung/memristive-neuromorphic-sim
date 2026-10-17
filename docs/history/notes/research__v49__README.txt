# V49 — FlyWire as a workload on a generic silicon fabric

Core `src/fabric.py` is copied unchanged from V48. Optional FlyWire mapping is in `workloads/configurations.py`. The chip has no fly cell roles.

This study calibrates incoming excitatory/inhibitory conductance budgets separately while preserving edge signs and connectivity. It compares the original count-proportional mapping with the calibrated mapping under equal search budgets. It is circuit operating-point calibration, not a newly trained cognitive algorithm.

Train seed49101, validation49201, frozen selection, four fresh test histories49301–49304. Inputs are independent 20Hz contact events, a 100ms dropout and resumption. These are synthetic probes on real anatomical connectivity, not recorded fly stimuli. Perturbation lowers bias for physical WaveTile0 for50ms; this is hyperpolarization, not guaranteed spike silencing. Refinement uses separate seeds49401/49402 and identical millisecond event inputs at dt0.125/0.0625ms.

400ms trials and four test histories are exploratory architecture diagnostics. Participation ratio is estimated from40 bins and therefore limited by sample size. No navigation, learned memory, biological fidelity, task superiority or chip power/latency claim follows from firing/recovery statistics.

Copy the folder before rerunning:
```
OPENBLAS_NUM_THREADS=1 python src/experiment.py
MPLBACKEND=Agg python src/report.py
```
Requires NumPy and Matplotlib. All model/data dependencies are local to this revision. Previous versions remain unchanged.
