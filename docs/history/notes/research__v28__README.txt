# V28 — Input learning, neuronal information and failed selection

Completed: equal-budget training of original and afferent-separated wiring; frozen fresh evaluation; independent NumPy spike checks; causal interventions; a separately frozen offline decision diagnostic. No online-adaptation success or ASIC energy advantage is claimed. V27 and older revisions are preserved.

## Results and interpretation

Both selected networks score 50% on 64 fresh reversal trials and choose the same positive ensemble every time. The mean signed selection score improves from 0.0421 to 0.0897 with separated afferents, but the losing class never crosses the zero decision boundary. The paired accuracy difference is zero. This is a stronger class-specific diagnosis than simply saying training failed.

On the original evaluation, mean raw neuronal scores are 0.112 versus 0.196 for the original mapping, and 0.096 versus 0.275 for separated afferents, under negative versus positive targets. Both contexts therefore influence neuronal firing, but both produce the same winner. Improved average margin is not sufficient: future objectives should monitor each class, penalize the worst class, and test balanced choice, not only average signed score.

The present search uses eight fixed training histories. Neither selected network exceeds 50% actual training accuracy. Thus the immediate problem appears before generalization, within this finite optimizer search. This does not prove structural unreachability.

## Offline diagnostic: information reaches neurons

After seeing the all-one-ensemble result, we designed a post hoc diagnostic using only the scalar score from neuronal spikes. We fit one decision threshold on the original eight training histories, saved the threshold and timestamp, then generated a DIFFERENT 64-trial holdout, seed 28995. It is not the holdout used for the main result.

| Mapping | Diagnostic training accuracy | New-holdout threshold diagnostic | Actual ensemble choice on same holdout |
|---|---:|---:|---:|
| Original | 100% | 73.4375% | 50% |
| Separated | 87.5% | 85.9375% | 50% |

This is an offline diagnostic, not a new behavioral circuit and not a wave decoder. No I/Q enters it. It shows that changing the decision boundary extracts useful context information from neuronal activity. The threshold is not implemented by downstream spiking neurons in this revision, so 85.9% must not be advertised as chip task performance or continual learning.

The diagnostic does not settle whether the correct fix is choice-layer synapses, inhibitory balance, selector calibration, a better loss/optimizer or another mechanism. It also does not prove all-one selection is the only barrier to the new attention task.

## Causality and current input

On eight paired trials, equalizing other history-bearing states while retaining the wave leaves mean context-dependent spike differences of 0.598 (original) and 0.595 (separated). Erasing the wave as well, or disabling feedback, makes those matched-context responses identical. Behavioral accuracy remains 50%. Thus the wave causally changes neuronal responses, but this does not establish correct selection.

These strict controls clear synapse, dendrite, soma, refractory, delayed-event, emission, detector and inhibitory states at probe time. They are artificial isolating interventions, not normal behavior. The wave-retained reference receives the same reset.

In the new diagnostic holdout's first eight trials, removing the probe reduces mean counted spikes per neuron from 0.734 to 0.074 (original) and 0.685 to 0.071 (separated). Current input is therefore important to activity, but the task's correct label still depends only on past context. This is not yet context-dependent selection BETWEEN current information streams.

## What was trained and checked

256 neurons, 16 WaveTiles, 12 reduced compartments/neuron, eight contact slots/compartment. Wave writer, emission gains, feedback phases/gains, couplers, inhibition, thresholds and topology remain fixed. Only effective input conductances and excitatory recurrent conductances are trained, bounded to [0.2,2]. Old wiring trains one gain per active branch; separated wiring trains one per active branch/source. Conductances are expanded back to contact arrays for simulation. Inhibitory recurrent weights stay fixed.

The separated mapping assigns two contact slots per afferent, with 3x input gain to match the original six contacts/source at initialization. Both mappings produce identical initial spikes on the training histories. This gain choice is not a free circuit benefit and needs current/charge characterization.

Per mapping: two independently trained learning rates (0.04 and 0.12), 32 Adam updates each, identical initial operating point and minibatch order. Four trials/batch; eight fixed training histories (seed 28101), sixteen validation histories (28201). Same validation selection rule and equal number of checkpoint evaluations. Best validation accuracy, then signed score, selects the frozen model. Both choose learning rate 0.12, update 32. This is a limited supervised capacity experiment, not local biological learning.

Main fresh set: seed 28991, 64 trials, generated after both models were frozen. Bootstrap intervals resample sixteen four-trial groups to preserve matched-pair structure. The [50%,50%] accuracy intervals reflect exactly two correct trials in every group for a constant choice; they do not imply absence of uncertainty across other topologies or trained models.

The hard-spike surrogate-gradient simulator matches NumPy output spike counts exactly on eight main-test trials per mapping. This validates checked forward behavior, not the surrogate derivative as a true gradient or convergence across time steps. Main time step: 0.125 ms.

## Verification correction

The completed training script originally asserted conductance bounds on the entire padded contact array. Separated wiring stores zeros at unused contacts, causing a false failure after results had already been saved. All active contacts are within [0.2,2]. The original source snapshot, assertion, results and log are preserved. verification_correction.json reports active-contact checks, immutable weight hashes and causal checks. No trained parameter, result or test label was changed. The source check is corrected for future reproduction.

## Missing circuit mechanisms: a staged design, not a combined theory

Miller, Fiete and Jensen do not propose one identical theory or require our specific I/Q circuit. The following links between their work and this chip are engineering interpretations. Successful chip behavior would test those implemented mechanisms; it would not establish consciousness or validate all three research programs.

### Miller: flexible effective connectivity

Miller and colleagues propose that waves organize multifunctional neural ensembles, with slower rhythms influencing where and when sensory processing occurs. MIT's account explicitly identifies this as a theory needing further tests of analog computation. The design implication is to measure context-dependent transmission of current information through neurons, not merely context decodability. [Miller laboratory / Picower account, 2026](https://picower.mit.edu/news/cognition-and-consciousness-arise-analog-computations-says-new-theory).

Our model has hidden waves and a causal feedback path. It lacks demonstrated switching of the useful pathway and a task that requires it. The next task should contain two independent concurrent evidence streams, a delayed cue selecting relevance, and conflicting evidence. The output must depend on the selected evidence, not cue identity. Measure effective sensory-to-output transfer under each context, same-wave/different-input preservation and wave/feedback/coupler interventions.

The live oscillator setting is 5 Hz with a 120 ms envelope decay, not an implemented alpha/beta-to-gamma hierarchy. The 80 ms probe is only 0.4 of its carrier cycle. A future phase-routing experiment must vary arrival phase and delay and report time-resolved spikes; an integrated spike-count difference alone does not establish phase-window computation. Frequency bands must not be added simply to resemble an EEG spectrum.

### Jensen: selective inhibition, not uniform suppression

Jensen and Mazaheri propose routing by inhibiting irrelevant pathways, with alpha-related inhibitory windows regulating processing. This motivates testing timed, pathway-selective inhibition; it does not imply every slow oscillator is attention. [Jensen & Mazaheri, 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2990626/).

Our network already has inhibitory neurons and a population inhibitory pool. What is missing is demonstrated, trained selective competition that permits either candidate ensemble to win. More common inhibition can silence both candidates without switching either one. Test separately addressable soma/proximal and dendritic inhibitory ports, driven by neural activity and local wave projections. A conductance port should use I_inh = g_inh(t)(E_inh - V), with nonnegative g_inh; it changes both current and effective membrane time constant. Present inhibition is an additive normalized current.

A candidate wave-to-inhibition circuit can use a_i I_k + b_i Q_k followed by a bounded nonnegative transconductance. It needs no numerical phase extraction or symbolic wave decoder. Phase-sensitive inhibitory windows must be measured through spike timing and sensory transfer; they must not encode the target label. Add this only after testing whether ordinary balanced choice calibration solves the current offset problem.

### Fiete: dynamics that restore useful state

Khona and Fiete describe recurrent attractor/integrator mechanisms for maintaining state, correcting perturbations and integrating noisy cues. Their review also emphasizes trade-offs involving capacity and robustness. An oscillator ring-down is not automatically an error-correcting attractor. [Khona & Fiete, 2022](https://www.nature.com/articles/s41583-022-00642-0).

The isolated wave layer here is a damped linear coupled system; with emission removed its state decays toward zero. Recurrence in the full neuron–wave loop could create richer dynamics, but this has not been established. Test state recovery after a brief perturbation, response to partial cues, controlled replacement of old context, and distance to a matched unperturbed trajectory. Preserve fine neuronal representations while using wave modes for shared context. Do not add regenerative gain without checking for runaway activity or a single rigid attractor that prevents switching.

### Pyramidal neurons: function matters more than compartment count

The current tile has AMPA/NMDA-shaped filters, a voltage-dependent NMDA factor, compartment integration, threshold/reset and refractory timing. Twelve numerical compartments are not twelve anatomical dendritic branches. The live model does not implement a biophysical back-propagating action potential, regenerative apical calcium plateau or burst-coupling mechanism. External and recurrent spike contacts currently enter basal compartments; apical compartments mainly receive wave feedback.

Experiments in layer-5 pyramidal neurons show interaction between dendritic and axonal initiation zones and associated changes in firing patterns. This motivates a circuit test of basal evidence plus apical context, including relative timing and inhibition. It is not evidence that this reduced model already reproduces those neurons. [Larkum et al., 2001](https://physoc.onlinelibrary.wiley.com/doi/10.1111/j.1469-7793.2001.0447a.x).

If a dendritic coincidence experiment is needed after selection calibration, add a switchable apical regenerative state and an explicit local soma-spike-to-apical event path. Compare basal alone, apical alone, coincident input and delayed input; measure spikes, bursts, recovery and inhibition. Keep the baseline model alongside it. A new plateau state changes circuit area/power and may make learning harder if it saturates.

### Field generation and plasticity

The present operating source is a signed, learned population spike-emission sum. Real extracellular potentials involve transmembrane currents and geometry; synaptic currents are important contributors, with other ionic and spike-related sources. Current-source taps should therefore be an independently calibrated later experiment, not a claim that a capacitor-voltage proxy is an LFP. [Buzsaki, Anastassiou & Koch, 2012](https://www.nature.com/articles/nrn3241).

Fast gating changes instantaneous efficacy; it need not rewrite the stored conductance. Maintain separate variables for nonvolatile G, temporary inhibition/gating and local eligibility. Later reward updates G from activity-dependent eligibility after a response. Credit assignment, exploration and retention remain to be demonstrated; adding physiological detail is not a substitute for that learning test.

## Recommended next controlled revision

1. Keep separated afferents, wave hardware and neuron count. Test a balanced neuronal choice mechanism using spike inputs only. First try calibrated existing selection/competition parameters with a class-balanced margin loss, reporting both class accuracies. Avoid a permanent software correction of the answer.
2. If an explicit response population is needed, connect selected neurons to it through real weighted event synapses, dendrites and somas, with reciprocal inhibition. Train these synaptic associations while holding the context representation stable. No wave I/Q readout. Report the added neurons and parameters as an architectural extension.
3. Once either action can be selected on a held-out set, move to the cue-selects-current-evidence task. Only then test learning-time exploration, eligibility/reward rules, reversal and retention; continually changing all mechanisms would hide the cause of improvement.
4. Test pathway-specific wave/inhibitory gating and dendritic coincidence one at a time against the simpler winning choice circuit, with an equally trained nonoscillatory control. Do not add every biological mechanism in one revision.
5. Measure physical latency, energy and storage only using a characterized circuit. Include eligibility, routing queues, analog capacitors, conductance programming, feedback and readout. Biological inspiration alone does not establish an advantage over digital hardware.

## Reproduce

    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v28/src/train_compare.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v28/src/finalize_diagnostics.py
    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v28/src/decision_diagnostic.py
    MPLCONFIGDIR=/tmp/wave-v28-mpl /tmp/wave-v7-env/bin/python research/v28/src/report_results.py

Each training run creates a new timestamped folder. Finalize and diagnostic scripts apply to active.txt's run. The diagnostic threshold is frozen before its separate fresh holdout. No prior model or old result is overwritten.
