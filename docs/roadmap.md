# Next experiments

[Back to the project](../README.md)

The next stage should connect the demonstrated memory mechanism to measurable implementation requirements while preserving the experimental controls that made the current results interpretable.

| Priority | Concrete next step | Evidence needed to advance |
|---|---|---|
| Circuit feasibility | Characterize leakage, mismatch, detector offset, and local coupling using transistor-level models and a documented process | Stable behavior over declared corners, with reproducible circuit files and calibration costs |
| Energy comparison | Include supply currents, routing, fanout, configuration, and readout in matched implementations | Measured or validated simulated energy per successful task, with equal task quality and latency constraints |
| Model robustness | Test new memories, broader input distributions, and independently generated holdouts | Prespecified comparisons and uncertainty over independent memory sets |
| Useful online adaptation | Separate context inference from reward credit; compare plasticity on/off during reversal and retention | Learning curves, recovery time, retained associations, and update costs |
| Biological relevance | Fit a declared neural dataset and predict held-out neuronal responses or perturbations | Out-of-sample neural predictions beyond an engineered synthetic task |
| Neural-interface applications | Define a specific recording, decoding, or stimulation task with appropriate data and controls | Application-specific evidence; synthetic pattern completion alone is insufficient |

Every new model revision belongs in a new numbered directory. Failed experiments remain part of the record. Frozen-inference experiments freeze all settings before new tests; online-learning experiments freeze the learning-rule settings while allowing only specified post-response updates. Behavioral scoring continues to use downstream neuronal activity, with direct shared-state decoding labeled as a separate diagnostic.

Dynamic-state equivalents, synaptic weight storage, logical updates, host runtime, and physical energy will be reported separately.
