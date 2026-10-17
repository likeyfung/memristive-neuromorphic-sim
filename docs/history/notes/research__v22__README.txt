# V22 — Hidden wave state and neuronal ensemble selection

The task output has **no access to I/Q, phase or amplitude**. It is the fixed spike-activity difference of two overlapping neuronal ensembles. No task-output classifier is trained. The 256-neuron, 16-WaveTile topology and individual conductances are retained.

## Sequential experiment

1. Start from copied V21 learned conductances, keep spike-only emission, disable the old multiplicative evidence gate, and add one optional inhibitory population state per tile. Train synaptic magnitudes, individual feedback gains and phases directly on the ensemble objective. Compare competition strengths 0, 0.3 and 0.8.
2. Freeze that selection network, then characterize all eight DEND/SOMA/SPIKE emission switch combinations on validation histories. Do not retrain the selection network separately for the current-source combinations. This is a controlled source study, not proof of globally optimal coefficients.
3. A current-source combination can become the primary configuration only if stage A achieves validation signed selection >0.1 and ensemble accuracy ≥65%. Otherwise spike-only remains primary, and the additional sources are exploratory rather than an adopted fix for failed selection.
4. Freeze all parameters and source calibration before generating new test histories. Test natural context selection and strict matched-probe interventions.

An earlier pilot was stopped before any fresh test because the source normalization unintentionally weakened legacy spike emission. Its directory and log are retained with `STOPPED_PILOT.json`. The corrected run checks exact spike-only charge equivalence.

## Task

A 60-ms presynaptic context cue is followed by an 80-ms silent interval. A probe arrives at 140 ms and lasts 80 ms. In each group of four trials, each of two probe patterns is byte-identical across opposite contexts. Cue realization/rate varies by history. Target ensembles are specified before training: E_A contains neuron indices modulo 4 in {0,1}, E_B in {1,2}. Each contains 128 neurons; 64 overlap.

The behavioral score uses only post-probe neuron spikes:

`S = (mean spikes in E_A − mean spikes in E_B) / (mean spikes in E_A + mean spikes in E_B + epsilon)`.

Signed selection is mean(context × S). Accuracy counts correct signs; ties and silence are incorrect. Nonzero ensemble differences alone do not establish successful context selection: the difference must have the intended sign and change appropriately across contexts.

Training uses 24 histories, validation 16 histories, and fresh test 64 histories (16 independent four-trial groups). Confidence intervals resample entire four-trial groups. This is a small synthetic contextual-selection study, not a test of human cognition, lifelong adaptation or general attention.

## Learning and competition

Six SPSA updates per competition setting perturb input-contact log-conductances (shared perturbation direction within each branch), individual recurrent log-magnitudes, individual feedback log-gains and phases. The loss uses actual ensemble spike output, an excess-firing penalty and a silence penalty. Conductances themselves remain individually valued; perturbations share structure to limit search complexity. This is supervised, host-side black-box parameter training, not biological STDP or an implemented on-chip learning engine. It is a limited training budget and is not convergence of the best possible learning rule.

Within each block, a decaying population spike trace recruits inhibitory current, in addition to the existing sparse inhibitory synapses. τ_I=10 ms. Wave input remains phase-sensitive additive membrane/dendritic current with neuron-specific gain/phase and fixed soma threshold. The old extra sigmoid synaptic gate is disabled to isolate competition rather than introduce another gating formula.

## Current-source definitions and limits

DEND_EMIT_EN, SOMA_EMIT_EN and SPIKE_EMIT_EN control three taps. D and S are **step-average normalized capacitor charging currents**, CΔV/Δt with C=1, computed from the compartment integration updates. Soma current is measured before reset/refractory clamping; the discrete spike/reset-related pulse is accounted separately as P. Synaptic drive affects the charging current through the existing integration equations. D uses a fixed signed projection: positive basal branches, negative tuft/trunk branches. This is a stated geometry-like engineering convention, not anatomical calibration.

These are NOT raw dendritic-voltage emissions. They are also NOT a full extracellular forward model: ionic currents, capacitances, return-current geometry, extracellular conductivity and morphology are not independently fitted. Net charging current does not equal a complete biological LFP source. An interpretation as tissue field voltage would need an explicit current-balance/geometry model.

Source scales come only from training activity. Enabled channels are RMS-normalized relative to the spike source, with a 1/√(number enabled) factor; spike-only mode exactly preserves the previous emission charge. Spike RMS uses the model's sampled impulse convention at the calibration timestep. RMS equality is not equal energy or biological dominance. A winning source mask would mean best observed validation configuration under this calibration, not that those currents dominate in the brain.

## Causal interventions

Natural trials preserve all neuronal and wave history. Stronger diagnostic interventions at probe time first equalize neuronal/synaptic/refractory/inhibitory/delay states, clear emission and detector filters, and retain only the history-dependent wave state. Then:

- Equalized: same neuronal state and same probe, different retained wave histories.
- Erase: additionally set W to zero once at the probe.
- FB off: disconnect feedback while allowing retained waves to evolve.
- Scramble: rotate each tile's wave phase with a fixed random spatial pattern, preserving amplitude at the intervention.
- Same wave: impose a common wave state across each four-trial group, while probes still differ.

These are artificial causal interventions, not proposed normal biological operations. Clearing W alone in a natural trial would leave other neural memories, so disappearance of the natural-history effect is not assumed. The response decoder never reads W; wave snapshots are recorded solely to verify interventions.

## Reproduction

```
OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/experiment.py
OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/verify.py
OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/report.py
```

Run from this directory. Every run creates a new timestamped result directory. Reproduction uses fixed seeds; additional tuning requires a different holdout in a later revision. Earlier revisions are unchanged. `initial_conductances.npz` is a local copy, so this revision does not import V21's mutable sources or weights.

## Hardware scope

The added competition uses 16 additional dynamic states (64 bytes at an assumed float32 digital equivalent). The analog implementation would store these states physically, but their bias/current costs are not measured. No chip energy, latency or RAM advantage is established here. `circuit/field_ports.va` supplies behavioral current-summing and inhibitory-port sketches. It has not been compiled or verified in Cadence and has no transistor/PDK power model.

## Sources and interpretation

- Miller, Brincat & Roy (2026), *Analog Cognition and Consciousness*, DOI 10.1523/JNEUROSCI.0711-26.2026, PMID 42618509: https://pubmed.ncbi.nlm.nih.gov/42618509/
- Buzsáki, Anastassiou & Koch (2012), *The origin of extracellular fields and currents*: https://www.nature.com/articles/nrn3241
- Miller group's account of theta phase/spatial working-memory readout, linking the original study: https://picower.mit.edu/news/radar-brain-wave-sweeps-cortical-region-read-out-information-held-working-memory

The publication record and institute account were accessible; the original 2026 full text and the Neuron article were not retrieved successfully in this session. The simulator implements a testable engineering interpretation of the user's requested mechanism, not verification of Miller's theory or biological equivalence.
