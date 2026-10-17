# Open questions

The current result is a memory mechanism in simulation. The next experiments need to establish whether it remains useful when the circuit and task assumptions become less favorable.

## Leakage and calibration

The first hardware question is whether a local state can retain useful history at an acceptable leakage and bias cost. A small writer/state/reader circuit would allow measurements of retention, detector offset, coupling, and mismatch before committing to a larger array. Calibration effort belongs in that comparison, including how often recalibration is needed.

## Energy at matched task performance

Fewer spikes are encouraging, but the coupled state has its own cost. A meaningful comparison needs supply currents, event routing, fanout, configuration, and readout on both sides, at matched accuracy and timing constraints. Dynamic state, stored weights, logical updates, and measured energy should remain separate quantities.

## Adaptation beyond acquisition

V58 acquires associations and then freezes them. Useful online adaptation would need to survive reversal, recover after a change in context, and retain earlier associations. That experiment should compare plasticity on and off and report learning curves and update costs. The failed selection and credit-assignment experiments in V25–V28 are relevant starting points.

## Broader inputs and neural data

The synthetic task makes the causal comparison clean, but uses engineered populations and a narrow family of histories. New tests should vary memory content and input statistics, with settings chosen before evaluation. A biological application would also need a defined recording dataset and predictions of held-out neural activity or perturbation responses.

A decoding or stimulation application needs its own task and controls. Pattern completion in the present model is not yet evidence for memory restoration in a person.

New experiments will use separate revision directories and fresh holdouts. In online experiments, learning-rule settings are fixed in advance and only specified post-response weight updates are permitted. Behavioral evaluation continues to use neuronal activity; direct decoding of internal state remains a diagnostic.
