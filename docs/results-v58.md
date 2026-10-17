# V58: history-dependent recall

V58 tests whether earlier events can select a later neuronal response when the present input is held fixed. It also compares spatially coupled state with local-state controls and examines sensitivity to modeled electrical disturbances.

The [aggregate results](evidence/v58-summary.json) are public. Source, weights, and trial-level records remain in the local archive; see the [archive notes](publication-scope.md).

## Method

Three model families receive the same twelve-candidate training budget. The top three candidates in each family are evaluated on separate validation histories. Each selected model acquires six final memory sets. Weights, settings, and relevant source files are then frozen before evaluation histories are generated.

Each causal condition has eight episodes per memory set, with delays of 350 or 950 ms. Within a context pair, inputs from 60 ms onward are identical, including the partial cue. The earlier context is the only input difference. F1 measures pattern completion in reader-neuron spikes, excluding the features directly supplied in the cue.

The nominal and intervention cohort contains 384 episodes and 192 pairs. The stress cohort contains 1,584 episodes across three model families and eleven conditions, with two device draws per memory set. Confidence intervals bootstrap the six memory sets rather than individual queries.

## Recall and interventions

| Condition | Mean F1 | 95% interval |
|---|---:|---:|
| Spatial coupling, intact | 0.943 | 0.860–0.994 |
| Spike broadcast with local state | 0.943 | 0.860–0.994 |
| Isolated local state | 0.000 | 0.000–0.000 |
| Spatial coupling, state erased | 0.000 | 0.000–0.000 |
| Spatial coupling, feedback disabled | 0.000 | 0.000–0.000 |
| Spatial coupling, state held at zero | 0.000 | 0.000–0.000 |
| Fast neuronal reset, state retained | 0.887 | 0.727–0.985 |
| Fast neuronal reset, state erased | 0.000 | 0.000–0.000 |

The intact spatial model completed 42 of 48 patterns exactly and selected the correct ensemble in 46 of 48 episodes. Both contexts were correct in 23 of 24 matched pairs.

The broadcast control ties nominal recall. The intervention results therefore support a causal role for shared state and its feedback within the spatial model, rather than an accuracy advantage over every alternative. Retaining state after a fast neuronal reset also supports substantial recovery, whereas erasing both removes that recovery.

## Stress and event counts

Under combined modeled mismatch, leakage, and noise, mean F1 was 0.6234 for spatial coupling and 0.4937 for spike broadcast. The paired difference was 0.1296, with a 95% interval of 0.0685–0.1898. Several individual stress conditions tied; the stronger thermal-noise condition had a small negative point estimate for the spatial advantage. The result is specific to the tested disturbance model and six independent memory sets.

At equal observed nominal recall, the spatial model emitted 25.8% fewer total spikes and 75.0% fewer writer spikes. Recurrent contact deliveries were slightly higher. Translating these counts into energy requires the cost of coupling, routing, fanout, bias, calibration, and readout. No supply-energy saving has been measured.

## Electrical checks

Fourteen ngspice transients tested a small writer/state/receiver loop under ideal, feedback-off, mismatch, injected-noise, leakage, and combined conditions. All outputs were finite, though combined disturbances substantially changed receiver spike counts across draws.

These checks use behavioral circuit blocks and assumed parameters. They do not validate a full memory task in transistor-level hardware. The small number of disturbance draws is also insufficient to estimate manufacturing yield.

## Interpretation

The experiment shows that a constrained synthetic neural circuit can recall different stored content after different histories, even when its present inputs match. Learned recurrent connections and the state-dependent access path have distinguishable roles in that result.

The selected state is nonoscillatory, and the task uses engineered populations and synthetic histories. Establishing biological relevance or a hardware advantage requires further experiments. The [open questions](roadmap.md) describe those next steps; the [archive notes](publication-scope.md) record integrity and smoke checks performed on the preserved implementation.
