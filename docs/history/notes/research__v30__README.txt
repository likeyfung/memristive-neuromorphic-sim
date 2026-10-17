# V30: separate memory, adaptation and attention experiments

The implemented inference model is `src/runtime30.py`; `src/hybrid.py` supplies hard-spike forward simulation with surrogate derivatives for host training. `src/reference.py` uses the independently implemented compartment/coupler path for checks. All imports and checkpoints are local to this revision. V29 is preserved.

The three tracks deliberately have different frozen checkpoints. `baseline/` preserves V29's working choice and attention starting points. Each timestamped `results/` run contains separate `memory/`, `adaptation/`, `attention/`, `biology/` and `verification/` folders. A memory or attention model has frozen conductances; an online model has a frozen initial checkpoint and learning rule but changes designated input conductances after feedback.

Reproduce from the project root using the existing Python environment:

```bash
export OPENBLAS_NUM_THREADS=1
/tmp/wave-v7-env/bin/python research/v30/src/new_run30.py
/tmp/wave-v7-env/bin/python research/v30/src/check_eligibility30.py
/tmp/wave-v7-env/bin/python research/v30/src/memory30.py
/tmp/wave-v7-env/bin/python research/v30/src/memory_stress30.py
/tmp/wave-v7-env/bin/python research/v30/src/delay_diagnostic30.py
/tmp/wave-v7-env/bin/python research/v30/src/adaptation30.py
/tmp/wave-v7-env/bin/python research/v30/src/attention30.py
/tmp/wave-v7-env/bin/python research/v30/src/cell30.py
/tmp/wave-v7-env/bin/python research/v30/src/verification30.py
/tmp/wave-v7-env/bin/python research/v30/src/cost30.py
MPLCONFIGDIR=/tmp/wave-v30-mpl /tmp/wave-v7-env/bin/python research/v30/src/report30.py
```

Memory, adaptation, attention and isolated-cell characterization can run independently after creating the run. Verification requires completed adaptation and memory/stress runs. Report generation requires every track. Each track refuses to overwrite an existing folder. `new_run30.py` creates a new timestamped run; it does not overwrite previous results. The optional delay diagnostic describes frozen predictions and never selects a checkpoint.

Required libraries: NumPy, PyTorch, Matplotlib and Markdown. NumPy/PyTorch simulation uses float64; resource tables state float32 equivalents as a separate accounting convention. The scripts do not run Cadence, a PDK, transistor circuits or measured hardware benchmarks.

The final cell characterization uses network-matched AMPA/NMDA decays of 3.5/30 ms. The first generic-cell 5/80-ms run is retained in `biology_default_kinetics/`. A derived relearning label was corrected to require successful acquisition of both the reversal and the return; original summary metadata are retained in `adaptation/label_metadata_original/`. Neither correction changed task predictions or test-selected parameters.
