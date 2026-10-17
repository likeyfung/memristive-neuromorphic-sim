# V27 structural audit and next learning design

V26 is preserved. This folder contains a self-contained copy of its model, a new structural audit, and an experimentally checked afferent-separation candidate. It is NOT a completed V27 adaptation benchmark. No trained reversal, continual-learning or ASIC advantage is claimed here.

## Main diagnosis

The broad neuron–wave concept has not been disproved. The implementation mixes three problems: representing context, selecting an ensemble, and assigning reward credit to a synapse. The present task also conflates context identity with the correct answer. Larger arrays or more training cannot by themselves resolve these ambiguities.

## 1. Independent stored conductances do not guarantee independent control

In the inherited input mapping, every selected channel drives the same first six contacts on a selected branch. The input drive is proportional to:

    [sum_s G(n,d,s)] * [sum_c mask(c,n,d) * input_c(t)]

All six conductances multiply the same mixture. Training cannot independently strengthen channel A and weaken channel B on a branch that receives both. This is an exact linear dependency before the dendritic nonlinearity. Recurrence and other branches can still discriminate inputs: this does not prove whole-network incapacity.

Measured on the actual fixed topology:

- 7,254 active input-contact parameters.
- 1,209 independent branch gains; 6,045 redundant parameter directions in this input mapping.
- 380 of 1,209 active branches receive multiple channels.
- Equalizing the six active conductances to their branch mean leaves all baseline output spikes unchanged on four new diagnostic trials.

These are input-map ranks, not effective neural state dimension or memory capacity. Repeated contacts from the same presynaptic source are allowed and can be useful physically. The restriction is that different sources share those same contacts before weighting. With identical linear synaptic kernels, duplicates alone do not provide independent computational degrees of freedom.

Implemented candidate: retain eight slots per branch, allocate two to each of four possible afferent channels, preserve which channels reach each branch. Repeated contacts still share a source, while different sources have separate conductances. The candidate has 3,304 active contacts and 1,652 independent input gains, about 36.6% more independent input gains. This is not a new neuron count or a measured area saving.

Charge-matched initialization uses three times the old input gain because two contacts replace six for each channel. This requires an engineering current/charge scaling choice and is not a free hardware benefit. Four diagnostic trials match original spikes exactly and final wave states exactly. A single-channel conductance perturbation changes only that channel's input gain. Future optimization must implement eligibility on these separate afferent contacts as well.

## 2. The benchmark does not require current sensory information

The target in the current code is context, or negative context after reversal. The current feature changes probe spikes but never changes the target. This is a valid delayed-context selection test, but it is insufficient to establish selective attention to current information. A context register can solve the label without using the probe feature.

The proposed next task is delayed context-dependent selection between two simultaneous evidence streams. A past cue specifies which stream is relevant; after a variable delay, two independently randomized spike streams arrive together. The selected stream's value determines the response. Across balanced examples, context alone and current evidence without context must each be insufficient. Include conflicting evidence, variable rate, timing jitter, distractors and novel delays on held-out trials.

The behavioral readout remains downstream neuronal spikes. Wave state is hidden. Context is allowed to change effective dendritic/neural routing, not supply an answer bit to a software classifier.

## 3. Reversing meaning is different from reversing a sensory representation

V24 aligned a signed population emission map to a selector. V26 freezes that map, feedback phases/gains, inhibition and topology while asking positive input/recurrent conductances to reverse which fixed ensemble wins. This can require a coordinated change in population activity against the old mapping. It is a plausible difficulty, not a demonstrated impossibility. The positivity and lower bound 0.2 also prevent deleting connections or changing their sign.

There are two distinct adaptation questions:

- Can experience change which neural response is useful for an otherwise stable context representation?
- Can experience also change how histories generate contextual wave dynamics?

Do not require a wave representation to reverse just because a reward convention changes. First isolate action/selection plasticity with stable context dynamics. Then separately test writer plasticity using a changed history-to-context relationship. If a separate response population is needed, it must receive real presynaptic spikes through synapses/dendrites/soma; it must not receive numerical I/Q or context labels. Additional neurons are a later controlled extension, not implemented here.

The first retry should use afferent-separated contacts with existing neurons, not simultaneously add a response layer, plastic couplers, new field sources and homeostasis.

## 4. Eligibility is not automatically credit assignment

The V25 rule uses pre/post or dendritic correlations multiplied by reward minus a running baseline. It identifies active synapses, but does not establish that their activity caused reward to improve. A wrong active ensemble can be depressed without creating a sufficiently active alternative. The system has noisy input histories, but no explicit action exploration rule tied to a reward-gradient estimator. Deterministic somas are not inherently a problem; purposeful small perturbations can be restricted to learning if required.

A simple mathematical diagnostic illustrates a possible stall: under constant reward -1 and baseline learning rate 0.05, the modulator magnitude falls from 1 on trial 1 to 0.00623 on trial 100. This is expected baseline behavior, not evidence that a reward baseline should be removed. A learner needs alternative actions and reward-dependent variation to exploit. This calculation is not a measurement of what happened in every V25 trial.

Next learning comparison, after a reachable supervised reference exists:

- Existing local eligibility rule as the baseline.
- Activity/perturbation eligibility paired with delayed reward-minus-predicted-reward, with controlled exploration during training.
- A neuron-specific teaching signal diagnostic to determine whether global credit is the bottleneck. This diagnostic must be labeled externally supervised and never presented as autonomous biological learning.

Wave affects dendritic/membrane activity; activity affects eligibility. No explicit wave decoder or symbolic wave-to-weight target is added. Eligibility traces, reward baselines, write pulses and any exploration circuit all have state and energy costs and must be accounted for.

## 5. The supervised failure is not a capacity theorem

V26 used two starts, 32 updates each, four-trial batches and surrogate gradients. The original-start optimizer visits each of 32 training trials four times. This is a useful bounded diagnostic, not exhaustive or necessarily strong enough to settle reachability. Forward equivalence to NumPy validates spike simulation on checked cases; it does not validate a surrogate derivative as the true gradient of a discontinuous network.

For the next diagnostic, start with a few fixed diverse training histories and test whether the allowed weights can fit them at all. Record margins, silent trials, gradient-to-finite-perturbation agreement and saturation. Compare equal-budget search on old versus separated afferents. A successful training fit with poor validation implies a different problem from inability to fit training examples. Optimize branch/channel effective parameters rather than six redundant copies, then map the values to physical conductances.

Do not add conductance sign changes. Compare a near-off positive-conductance option separately only if suppression is shown to be binding. Hardware feasibility of bounds is not calibrated in this model.

## Sequential experiment plan

1. Completed: audit afferent rank, preserve old operating point, verify isolated channel control. No task optimization yet.
2. Pending: matched supervised capacity comparison, old vs separated input wiring, same neuron/wave count, new training/validation histories. Report original selection and reversal separately. Freeze before generating a new test set.
3. Pending: context-dependent evidence-selection task. Train jointly on current information and historical relevance, without any wave readout. Require successful neural routing before calling this attention-like computation.
4. Pending: local online adaptation with exploration/credit controls. Freeze learning hyperparameters, deliver reinforcement only after the response, measure reversal learning curves, relearning and forgetting. No fresh-test tuning.
5. Pending: distinguish fast context switching from slow synaptic learning. Test two familiar signaled contexts without modifying weights, then an unsignaled rule change with online plasticity. Fast states currently reset each episode; continuous carry-over needs its own later test.
6. Pending: energy and area accounting only after behavior is useful. Compare matched accuracy/response quality and include conductances, all neuron/wave states, eligibility, routing, feedback and update circuitry. A digital ASIC can keep state locally too; avoided software array updates are not automatically avoided DRAM accesses.

## Causal controls and success criteria

Use identical current spike trains with different histories. Measure neural ensemble recruitment and the actual selected evidence, not only spike-count change. Erase wave state after the cue, disable feedback while retaining the wave, and test plasticity-off and reward-shuffled controls. Wave erasure alone leaves neuronal history, so separately reset other history-bearing states for an isolating intervention and report its artificial nature.

Also compare an independently trained, state/port-matched nonoscillatory control with equal search budget. A successful hybrid does not establish that oscillation, phase or spatial coupling was essential. Use phase/coupling perturbations with matched amplitude where possible and preserve reported negative controls.

Before claiming adaptation, require improvement with experience on new streams relative to frozen weights; before claiming attention, require the response to follow the selected current stream under conflicting input; before claiming wave advantage, require matched controls. No consciousness claim follows from these engineering tests.

## Reproduction and provenance

    OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python research/v27/src/audit.py

Each audit writes a timestamped results directory with JSON measurements, exact responses, routing masks and source hashes. The copied V26 scripts/checkpoints are support material; old version names in their comments refer to provenance. Run audit.py for this version's completed experiment. The inherited training scripts have not been rerun or claimed as V27 training.

## References

Gerstner et al. (2018), Eligibility Traces and Plasticity on Behavioral Time Scales. Supports eligibility plus delayed modulatory factors, not the correctness of this particular update rule: https://www.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2018.00053/full

Bellec et al. (2020), A solution to the learning dilemma for recurrent networks of spiking neurons. A computational reference separating eligibility traces and learning signals, not a claim that the present chip implements e-prop: https://www.nature.com/articles/s41467-020-17236-y

The numerical findings above come from the local audit and V26 sources, not from these neuroscience references.
