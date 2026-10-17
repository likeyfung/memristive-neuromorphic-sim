# V47
Main model: src/model.py. Physical architecture: DESIGN.md. Summary: report.html.

Preserve this revision. Copy this whole folder to a new timestamped directory before rerunning scripts (they write results).

```
clang -O3 -shared -fPIC src/events.c -o src/events.dylib
OPENBLAS_NUM_THREADS=1 python src/benchmark.py
MPLBACKEND=Agg python src/report.py
```
Requires Python, NumPy, Matplotlib and a C compiler. The compiled library is platform-specific and must be rebuilt on another platform. It only accelerates event delivery. All models use the included real connectome; no mutable earlier-revision imports.

This is a unified neuron–wave architecture, not a CPU/GPU split. No manufactured ASIC or measured physical energy/latency is supplied. Earlier V46 synthetic benchmark claims are retained for context but not counted as V47 evidence.
