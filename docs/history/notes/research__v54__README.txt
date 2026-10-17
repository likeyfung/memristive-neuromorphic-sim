# V54 — V52 mapped to a complete behavioral circuit

This folder preserves V52 and adds an electrical implementation in a new revision. The main entry is **`ngspice/benches/full_replay.cir`**. It includes the complete **256 main-neuron + 80 inhibitory-neuron + 16 local-state** array and **5,112 recurrent contacts** from V52's frozen workload.

The silicon-neuron/WaveTile architecture remains generic. ER4d/EPG names occur only in the frozen connection/input configuration. In that workload 72 main neurons are driven and other main soma thresholds are disabled; their circuits remain instantiated. V52's associative-memory learning route is disabled, so this package does not introduce or claim a newly working learning circuit.

## What is implemented

- Independent weighted event contacts; per-branch AMPA/NMDA rise/decay filters.
- Twelve physical-state dendritic compartments per main neuron, voltage-dependent NMDA factor, trunk integration and inhibitory shunting.
- Integrating soma, threshold comparator, reset, refractory one-shot and optional spike-triggered adaptation.
- Actual spiking PV / SST-A / SST-B / VIP-A / VIP-B cells per tile.
- Local soma-event emission, scalar continuous gm-C state, local detector, reciprocal nearest-neighbor coupling and inhibitory feedback.
- Preserved 2-ms biological event transport delay, modeled as an ideal delay channel.
- Independent EMIT_EN, WAVE_EN, COUP_EN, FB_EN and REC_EN controls.
- Optional external global coupler block, disabled and excluded from the matched V52 configuration.

## Main files

| File | Purpose |
|---|---|
| `ngspice/lib/neuro54.lib` | Leaf `.subckt` circuits: synapse, dendrite, soma, trace, couplers, event contact/delay |
| `ngspice/lib/neurons54.lib` | Full 12-compartment neuron and five-cell inhibitory tile |
| `ngspice/v52_full_fabric.inc` | Complete array, per-contact weights and all routes |
| `ngspice/benches/full_replay.cir` | 500 biological ms / 5 electrical ms whole-array replay |
| `ngspice/benches/loop_on.cir` | Small inspectable source → neighbor → inhibitory feedback → neuron example |
| `cadence/neuro54.va` | Verilog-A leaf blocks with electrical state and currents |
| `cadence/neurons54.scs` | Spectre hierarchical neuron and inhibitory wrappers |
| `cadence/full_replay.scs` | Complete Spectre run deck |
| `cadence/veriloga/*/veriloga.va` | Per-cell Verilog-A views, including optional structural wrappers |
| `CIRCUIT_SPEC.md` | Pins, equations, scales, assumptions and mapping details |
| `results/validation.json` | Analytic checks, causal tests and preserved coarse timing failure |
| `report.html` | Figures and measured circuit-test results |

## Run ngspice without overwriting results

From this folder:

```bash
python3 run.py --suite blocks
python3 run.py --suite smoke
python3 run.py --suite full --timeout 0
```

Each command copies the circuit to a new `runs/<UTC timestamp>/` directory and saves logs/traces there. `blocks` runs analytic and closed-loop tests; `smoke` also instantiates the whole array for 30 biological ms; `full` adds the 500-ms replay. The full 500-ms SPICE run did not finish within the recorded 25-minute bring-up budget. The default runner timeout is 900 wall seconds per deck; `--timeout 0` explicitly allows an unlimited run. The full SPICE run is much slower than the Python kernel. Simulator wall time is not chip latency.

The delivered circuits were run with ngspice 46, including XSPICE `oneshot` and KLU. Analysis needs Python, NumPy and SciPy. To validate a new run:

```bash
python3 src/verify_circuits.py --results runs/<timestamp>/results
```

The coarse loop deck uses 250-ns maximum step. The precision decks use 25 ns and 12.5 ns; the original failed coarse spike-timing check is retained. Use tighter steps to assess event timing. Whole-array bring-up is not full-array timestep convergence.

## Run in Cadence / Spectre

See `cadence/README.md`. Start with `soma.scs`, then the full array. Spectre was not installed on this machine, so the Cadence files are supplied but not compiler/runtime validated here. The ngspice library does not require a Verilog-A compiler.

## Abstraction boundary

This is a **behavioral electrical circuit**, not a fabricated chip or transistor netlist. Capacitors, leaks, reciprocal conductances and current sums are explicit; NMDA nonlinearity, transconductors, comparators, monostables and programming/routing functions are behavioral. No foundry PDK, rails, headroom limits, mismatch/noise corners, parasitic extraction or calibrated supply current is modeled. Do not calculate a silicon energy advantage from these ideal source currents.

V52 uses a nonoscillatory scalar shared state. The package preserves that mode instead of silently adding I/Q oscillation. A future oscillatory extension should be a separate validated configuration.

The reference uses discrete instantaneous event increments and timestep-quantized threshold/reset. This circuit uses continuous integration, finite charge pulses and event-triggered reset. Equivalent equations do **not** imply identical network spike trains. See the saved comparison before transferring any V52 task score.

Earlier models/results are unchanged. Frozen Python dependencies are under `reference/`; all generation and simulation files in this revision are self-contained.

## Simulation-only V52 reduction

`python3 run.py --suite reduced` runs a workload-specific ideal-equation reduction. It keeps all 72 active main cells, all 80 inhibitory cells, all 16 state tiles and the 5,112 recurrent contacts. Inactive main cells cannot emit or affect other states. Within each active cell, one recurrent-input branch remains distinct from the other three equally driven branches; opposing/apical identical branches are grouped. The full twelve-compartment circuit remains the primary hardware model.

This reduction is valid only under the checked frozen inputs, branch time constants and absence of learning/mismatch. It is not a reduction of physical die area. `results/reduction_checks.json` records the full/reduced neuron and short-array comparisons. `ngspice/benches/reduced_replay.cir` is the more practical deck for the configured workload; its status is reported separately from the unreduced deck.

Completed electrical replay: the simulation-only reduced netlist ran 500 biological ms in 127.6 host seconds. It produced 599 main-neuron spikes versus the frozen Python reference's 561, with 10-ms binned correlation 0.8960 and per-cell total-count MAE 0.5278 spikes. This is a port-fidelity measurement, not exact equivalence to Python or a task accuracy claim. Continuous-time finite-pulse/reset semantics differ from the discrete reference. See `results/full_array_comparison.json` and `results/reduced_replay_status.json`.

The reduced model's equivalence is to the **ideal full electrical equations**, under the documented symmetry constraints. It does not establish transistor-level equivalence, noise equivalence, physical area reduction or exact equivalence to the Python integrator.
