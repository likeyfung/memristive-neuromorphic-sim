# V51 — Causal division of content and access

A fresh six-memory-set replication on the preserved V40/V50 circuit, normalization OFF. No test-driven tuning. Code and parent dependencies are local. Seeds and source freeze in PROTOCOL.json. This is a behavioral-simulation study, not an ASIC measurement or proof of novelty.

Same learned weights/events within each paired intervention. Six neural conditions plus a task-aware digital exemplar reference. Delays350/950ms, four queries each per memory set:48 queries/condition. Confidence intervals bootstrap the six independent memory sets, not individual queries.

Digital comparator uses known task port semantics and acquisition boundaries; these conveniences are disclosed. It is not a same-dynamics emulator. C/Python comparator equivalence is checked on every trial. One full/compact neural regression is checked in this study; historical V40 tested96.

Copy this folder to a new directory before rerunning scripts that write results:

    OPENBLAS_NUM_THREADS=1 python src/study51.py
    MPLBACKEND=Agg python src/report51.py

Dependencies: NumPy, SciPy, Numba, Matplotlib, C compiler. Reference execution in this session used /tmp/wave-v7-env/bin/python with PYTHONPATH=/tmp/wave-v50-deps. No Cadence/PDK/device characterization is present.

Physical cost figure uses only conditional scalar-refresh budgets for7680 selected compact filter/dendrite states. It excludes additional states and routing/I/O on both sides; it is not total system power or saved RAM traffic. Events can support efficient digital implementations too.
