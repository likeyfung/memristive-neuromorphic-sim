# Wave Cognition

Spiking neural models of memory and context-dependent recall.

![Wave Cognition research architecture](docs/assets/architecture.svg)

This project studies how a neural circuit can use earlier experience to determine which stored pattern it recalls. The working hypothesis is that recurrent synaptic connections store associations, while slower local states influence which neuronal population becomes active when a partial cue arrives.

The work began with simulations of memristive retention and recurrent neural modules. It has since moved toward a model with dendritic integration, local inhibition, learned recurrent connections, and coupled continuous states. The original implementation is in this repository; the later experiments are described in the [research notes](docs/research-history.md).

## Current work

The latest experiment, V58, uses 256 main neurons, 80 inhibitory neurons, and 16 local continuous states. Pairs of trials receive different early histories followed by identical inputs. Recall is scored from the activity of feature neurons that were not directly stimulated by the partial cue.

| V58 observation | Result | Interpretation |
|---|---:|---|
| Nominal partial-cue recall | **0.943 mean F1** | Six independently acquired memory sets; 48 episodes per condition |
| Equally calibrated spike-broadcast control | **0.943 mean F1** | The control ties nominal recall |
| Shared-state erase / feedback disabled | **0.000 mean F1** | These interventions disrupt recall in the tested spatial circuit |
| Combined modeled stress | **0.623 vs. 0.494 F1** | Spatial coupling performs better than broadcast under this specified stress model |
| Nominal emitted-spike count | **25.8% fewer** | Fewer simulated spikes at equal observed recall; not a power measurement |

The useful result is the separation between learned content and the state that controls access to it. Whether that separation provides a hardware advantage remains an open question: fewer simulated spikes do not by themselves establish lower power. The selected configuration is nonoscillatory, despite the project's earlier focus on waves.

See the [V58 methods and results](docs/results-v58.md) for controls, uncertainty, and [aggregate data](docs/evidence/v58-summary.json).

## Model

| Component | Role |
|---|---|
| Learned recurrent connections | Store associations acquired during exposure |
| Writer neurons | Drive local continuous states with earlier event history |
| Neighbor coupling | Distribute the influence of local state |
| Dendritic and inhibitory pathways | Regulate which reader population responds |
| Reader-neuron spikes | Express the completed pattern |

## Research history

| Stage | Focus |
|---|---|
| Original memristive model | Retention, recurrence, gating, and temporal tasks |
| V1–V21 | Neuron/state coupling, circuit loading, and matched comparisons |
| V22–V30 | Neuronal output, learning, and failures of ensemble selection |
| Recovered V32–V40 lineage | Learned memory and history-dependent access |
| V42–V49 branches | Anatomical connectivity, navigation, and fabric studies |
| V50–V58 | Causal memory experiments and electrical feasibility |

The [development history](docs/research-history.md) follows these branches and records the unsuccessful experiments as well as the results that carried forward.

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

| Notes | Contents |
|---|---|
| [Model](docs/architecture.md) | Neurons, local state, learning, and circuit implementation |
| [Development history](docs/research-history.md) | Model revisions, branches, and unsuccessful experiments |
| [V58 experiment](docs/results-v58.md) | Methods, controls, results, and uncertainty |
| [Open questions](docs/roadmap.md) | Circuit measurements, adaptation, and biological validation |
| [Archive and verification](docs/publication-scope.md) | Available records and checks on preserved results |

The work is currently at the simulation and behavioral-circuit stage. Transistor-level validation and measurements from fabricated hardware remain to be done.
