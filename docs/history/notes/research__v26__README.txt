# V26 — Synapse-only supervised reachability diagnostic

V25 and earlier versions are preserved. The goal is to ask whether the existing plastic synapses can reverse the neuronal behavior while keeping wave writer, couplers and selector fixed, before blaming local learning alone.

## What stays fixed and what can vary

Input conductances on active contacts and excitatory recurrent magnitudes can vary within exactly [0.2,2], the V25 bounds. Inactive input contacts and inhibitory recurrent weights remain at initialization. Both local and existing interpopulation excitatory recurrence are already included; adding recurrent plasticity would not be a new extension beyond this search.

The local writer checkpoint, emission coefficients/gain, couplers, wave phases/frequency/decay, feedback phases/gains, thresholds, inhibition and topology are fixed. There is no explicit W→weight-update gate, wave target or behavioral wave decoder. The output remains the fixed neuronal ensemble spike difference.

## Stronger supervised optimization

A PyTorch forward implementation reproduces the hard-spike dynamics. Spike derivatives use a fast-sigmoid surrogate for optimization; the forward spikes remain discrete. Full temporal backpropagation uses checkpointing. Adam optimizes synapses, with two initializations and 32 updates each, learning rate .04, gradient-norm clip 1. The first initialization is the original conductance state; the second perturbs allowed conductances before projection to bounds.

Training histories: seed26110, 32 trials. Validation: seed26200, 16 trials, checked every four updates. Select primarily by reversal accuracy, with signed reversal selection as a tie breaker. The training loss rewards reversed neuronal ensemble selection and adds a small spike-count penalty. It does not average A→B→A accuracy and cannot earn a high score merely by retaining A.

A preliminary development run had surrogate gradient norms around 1e8–1e10 and no validation improvement. It was stopped before generating a fresh test. Its log and surrogate source are preserved. The corrected run reduces derivative amplitude tenfold, leaving all forward equations unchanged; resulting gradient norms are much smaller. This adjustment used development behavior, not test data.

The surrogate derivative is 1/[2(1+|x/0.1|)^2], where x is distance from threshold. This is an optimization approximation, not the true derivative of discontinuous spikes or a biological learning mechanism. Gradient clipping and finite search budget do not turn this into a global optimizer.

## Freeze and fresh verification

Freeze the selected conductances before generating seed26991's 64 fresh trials. Run both original and optimized conductances in the original NumPy simulation. Verify the optimized PyTorch forward spike outputs against NumPy on eight fresh trials. The saved baseline forward regression also compares one original-parameter episode.

A constructive success would require ≥75% fresh reversal accuracy and positive signed selection. The run did not meet this gate. Therefore:

- It did not establish a successful reversed mapping using these synapses.
- It did not prove the allowed parameter space is incapable of reversal.
- It did not isolate poor local credit assignment as the sole cause of V25's failure.

The 31.25% fresh reversal accuracy remains below chance for this balanced task. The increase over the same-test baseline of15.625% weakens the original preference; it is not successful adaptation. Original and reversed accuracy need not sum to100% because ties/silence are counted incorrect.

## Local versus supervised update directions

At the original G, compute mean local updates across training histories for pre/post100ms, dendritic100ms and dendritic300ms rules, all with learning rate .05 and reward-minus-running-baseline modulation. Parameters stay fixed while collecting these counterfactual mean update directions. Project each proposed update into the allowed conductance bounds, then compare its cosine with the optimized endpoint displacement from the same original G.

This is a comparison with a finite optimizer displacement, not a true loss gradient, unique optimum, or successful target direction. The second optimizer restart may begin away from G0, but the endpoint displacement used in this diagnostic is measured from G0, as are the local updates. A one-experience mean update is much smaller than a multi-update optimizer displacement; their norms are not directly comparable training budgets.

Four validation trials evaluate the effect of one mean local step. These probes are a small diagnostic, not a new generalization test. They slightly improve signed reversal scores but do not reverse any of those four decisions.

Parallel contacts in a branch receive identical afferent events, so some individual-weight differences are behaviorally redundant. The report also projects contact displacements onto their shared-contact mean before recomputing cosine. Neither raw nor projected alignment proves that the local rule can learn the desired task.

## Interpretation of suppression and learning

Reduced firing is not automatically synaptic weakening. Activity/timing and modulation determine the update in these models. Prolonged activity reduction can also recruit compensatory homeostatic scaling in biological preparations. V26 adds no unconditional low-firing depression and no homeostatic rule. V25 already used reward minus a running baseline; that is not introduced as a new V26 mechanism.

The intended interpretation stays W→neuronal excitability/activity→eligibility→synaptic change→future population/wave dynamics. W is an engineering context/selection state, not demonstrated consciousness.

## Scope of the next decision

Do not conclude “unreachable, therefore expand hardware” from this finite negative search. A stronger search, a different optimizer/surrogate, or a carefully isolated G+emission-gain comparison could be the next diagnostic. Any expanded-parameter result must be reported separately with new development/test data. No such expansion is performed here.

Online adaptation, return learning and update-cost objectives are not re-evaluated in V26: this is the preceding static capacity diagnostic. V25 remains the current online-adaptation result. No ASIC energy, latency, RAM-traffic, transistor or memristor measurements are made.

## Reproduce

From this folder:

```
OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/reachability.py
XDG_CACHE_HOME=/tmp/wave-v26-cache MPLCONFIGDIR=/tmp/wave-v26-mpl OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/report_v26.py
```

The completed timestamped folder contains development records, frozen weights, fresh inputs/outputs, local update arrays, checks and report figures. The previous stopped development run is separate and excluded. Model dependencies and checkpoints are local copies.

## References

- Turrigiano et al. (1998), Activity-dependent scaling of quantal amplitude in neocortical neurons: https://www.nature.com/articles/36103 . Supports the distinction between suppressed firing and an unconditional weakening rule; it does not validate this simulator.
- Gerstner et al. (2018), Eligibility Traces and Plasticity on Behavioral Time Scales: https://www.frontiersin.org/journals/neural-circuits/articles/10.3389/fncir.2018.00053/full . Background for local eligibility plus modulation, not evidence that V26 implements brain learning.
