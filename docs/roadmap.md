# Open questions

The current result is a memory mechanism in simulation. The next experiments need to establish whether it remains useful when the circuit and task assumptions become less favorable.

| Question | Next experiment | Evidence needed |
|---|---|---|
| Circuit feasibility | Characterize leakage, mismatch, detector offset, and local coupling using transistor-level models and a documented process | Stable behavior over declared corners, with reproducible circuit files and calibration costs |
| Energy comparison | Include supply currents, routing, fanout, configuration, and readout in matched implementations | Measured or validated simulated energy per successful task, with equal task quality and latency constraints |
| Model robustness | Test new memories, broader input distributions, and independently generated holdouts | Prespecified comparisons and uncertainty over independent memory sets |
| Useful online adaptation | Separate context inference from reward credit; compare plasticity on/off during reversal and retention | Learning curves, recovery time, retained associations, and update costs |
| Biological relevance | Fit a declared neural dataset and predict held-out neuronal responses or perturbations | Out-of-sample neural predictions beyond an engineered synthetic task |
| Neural-interface applications | Define a specific recording, decoding, or stimulation task with appropriate data and controls | Application-specific evidence; synthetic pattern completion alone is insufficient |

The immediate hardware question is whether a local state can retain useful history at an acceptable leakage and bias cost. A small writer/state/reader circuit would allow these measurements before committing to a larger array. Calibration and the cost of coupling belong in the energy comparison.

V58 tests acquisition followed by frozen recall. Online adaptation needs separate reversal, recovery, and retention experiments, with plasticity-on/off comparisons. The unsuccessful selection experiments in V25–V28 remain relevant to that work.

New experiments will use separate revision directories and fresh holdouts. In online experiments, learning-rule settings are fixed in advance and only specified post-response weight updates are permitted. Behavioral evaluation continues to use neuronal activity; direct decoding of internal state remains a diagnostic.
