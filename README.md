# Wave Cognition

Spiking neural models of memory and context-dependent recall.

This project studies how a neural circuit can use earlier experience to determine which stored pattern it recalls. The working hypothesis is that recurrent synaptic connections store associations, while slower local states influence which neuronal population becomes active when a partial cue arrives.

The work began with simulations of memristive retention and recurrent neural modules. It has since moved toward a model with dendritic integration, local inhibition, learned recurrent connections, and coupled continuous states. The original implementation is in this repository; the later experiments are described in the [research notes](docs/research-history.md).

## Current work

The latest experiment, V58, uses 256 main neurons, 80 inhibitory neurons, and 16 local continuous states. Pairs of trials receive different early histories followed by identical inputs. Recall is scored from the activity of feature neurons that were not directly stimulated by the partial cue.

Across six independently acquired memory sets, the spatially coupled model reached a mean F1 of 0.943. An equally calibrated spike-broadcast control reached the same score. The spatial model emitted 25.8% fewer spikes, and performed better under the specified combined mismatch, leakage, and noise condition. Erasing the shared state or disabling its feedback disrupted recall.

The useful result is the separation between learned content and the state that controls access to it. Whether that separation provides a hardware advantage remains an open question: fewer simulated spikes do not by themselves establish lower power. The selected configuration is nonoscillatory, despite the project's earlier focus on waves.

See the [V58 methods and results](docs/results-v58.md) for controls, uncertainty, and [aggregate data](docs/evidence/v58-summary.json).

## Running the original model

The Python code at the repository root implements the earlier memristive model, including population coding, a spiking basal-ganglia gate, delayed matching, and temporal-order tasks.

```bash
git clone https://github.com/likeyfung/memristive-neuromorphic-sim.git
cd memristive-neuromorphic-sim
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

`main.py` runs the tasks and writes `simulation_results.png`. Model parameters are in [`config.py`](config.py); device equations and neural modules are in [`devices/`](devices/) and [`modules/`](modules/). The [original notes](docs/history/original-memristive-readme.md) describe that implementation in more detail.

The newer V58 source, trained weights, and detailed trial records are not included in this public version. Running the root code does not reproduce the V58 results.

## Research notes

- [Model](docs/architecture.md) — neurons, local state, learning, and the proposed circuit implementation.
- [Development history](docs/research-history.md) — how the model changed, including failed experiments and separate branches.
- [V58 experiment](docs/results-v58.md) — the current memory task and its controls.
- [Open questions](docs/roadmap.md) — circuit measurements, adaptation, and biological validation still needed.
- [Archive and verification](docs/publication-scope.md) — available material and checks on the preserved results.

The work is currently at the simulation and behavioral-circuit stage. Transistor-level validation and measurements from fabricated hardware remain to be done.
