# V48 — Programmable Silicon Neuron–Wave Fabric

Core: src/fabric.py. Optional connectivity adapters: workloads/configurations.py. Full circuit abstraction: ARCHITECTURE.md. Report: report.html.

No fly-specific roles exist in the core. Default: 256 neurons × 12 dendrites × 8 input contacts; 16 shared WaveTiles. The fabric persists between step() calls. Wave state is internal and never part of observe() behavioral output.

Requires Python, NumPy and Matplotlib. Copy this revision into a new folder before rerunning scripts that write results:

```
python src/validate.py
python src/spike_smoke.py
MPLBACKEND=Agg python src/report.py
```

The checkpoint in results/ is a trusted local Python pickle; never load an untrusted pickle. FlyWire data is the unchanged V45/V47 graph and remains an optional workload. No fabricated chip or measured energy advantage is supplied.
