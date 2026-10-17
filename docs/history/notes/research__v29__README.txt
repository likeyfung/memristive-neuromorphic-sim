# V29 reproduction

See DESIGN.md for the circuit equations, switches, staged protocol and hardware limits. Results are generated from real runs; report.html is built after the experiments and checks finish. Earlier revisions are unchanged.

From the project root:

    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/run_stages.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/reference.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/cell_tests.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/continued_control.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/verify_stages.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/attention_task.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/task_sanity.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v29/src/attention_diagnostics.py
    XDG_CACHE_HOME=/tmp/wave-v29-cache MPLCONFIGDIR=/tmp/wave-v29-mpl /tmp/wave-v7-env/bin/python research/v29/src/report_v29.py

run_stages.py creates a fresh timestamped directory. Other scripts use latest.txt/active.txt to inspect that run. attention_task.py does not proceed unless fresh wave_balance accuracy is at least 75% in each class. If it does proceed, it creates an attention subdirectory, uses separate development seeds and freezes before generating new tests. A second invocation requires a new run rather than overwriting an existing attention experiment.

The network forward implementation is hybrid.py. The independent NumPy path is reference.py using the local tiles.py and inherited coupler implementation. biology.py defines the bAP/plateau parameters and NumPy state update. The full model remains local to this folder.

Training is host-supervised. The newly calibrated soma currents and inhibition settings are physical model parameters, not an external decision threshold. No actual supply energy, transistor latency, memristor endurance, morphology-specific voltage field or biological continual-learning mechanism is measured in V29.
