# V13 — circuit feasibility and loaded wave memory

This revision preserves the V11/V12 neuron–wave engine and adds circuit mapping,
whole-model time scaling, mismatch/trim scenarios, global-port loading experiments,
and ideal ngspice checks. Earlier revisions are unchanged.

From this directory, using Python with NumPy:

```sh
python src/study.py
python src/loaded_ports.py
python src/circuit_check.py
python src/report.py
```

The circuit check requires ngspice (the script currently selects
`/opt/homebrew/bin/ngspice`). Scripts regenerate this revision's result files;
copy this folder to a new revision before changing experiments.

Open `report.html`. Raw numerical results are in `results/`; SPICE input,
transient output and logs are in `circuits/`. `circuits/wave_blocks.va` contains
behavioral Verilog-A equations, not compiled or PDK-qualified transistor circuits.

`src/model.py` is the full array engine, `src/tiles.py` the neuron,
`src/compact.py` the equivalent aggregated filter implementation, and
`src/design.py` the physical mapping and acceleration wrapper.
