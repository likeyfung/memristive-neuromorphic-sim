# V12: RAM and latency comparison

V11 is preserved. `src/model.py` and `src/tiles.py` are exact V11 copies. `src/compact.py` implements matched shared-filter state aggregation.

Read `CONCLUSION.md` or `report.html`. No superiority graphs were generated because a matched ASIC advantage was not established.

Dependencies: Python 3, NumPy, ngspice. Local Python: `/tmp/wave-v7-env/bin/python`; ngspice: `/opt/homebrew/bin/ngspice`.

From this directory:

```sh
python src/benchmark.py
```

From `circuits/`:

```sh
ngspice -b characterize.cir
```

Then from the revision directory:

```sh
python src/analyze_circuit.py
python src/conclusion.py
```

`results/benchmark.json` contains matched timings, spike events and errors for nine runs per implementation. Memory figures distinguish actual float64 state arrays from a hypothetical float32 logical-traffic ledger. Neither is a DRAM hardware-counter measurement.

`circuits/characterization.dat` contains actual ngspice transient samples. The circuit uses ideal controlled sources and lumped transfer-function RC fixtures, not PDK devices or a transistor-level array. No supply energy or silicon advantage is claimed.
