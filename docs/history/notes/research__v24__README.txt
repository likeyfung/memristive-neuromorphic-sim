# V24 — Writer learning with a frozen neuronal selector

This revision preserves V23 and trains the upstream spike→wave writer. The behavioral output remains the same fixed overlapping-ensemble neuronal spike difference; no wave vector enters a task decoder.

## Architecture and scope

- 256 neurons, each with 12 reduced dendritic compartments and 8 allocated contacts/compartment; 16 shared WaveTiles.
- The selector is copied from V23's successful controlled-state experiment, **not** from its unsuccessful natural-history retraining.
- Feedback phases/gains, all synaptic conductances, recurrent connectivity/weights, thresholds and competition parameters remain frozen.
- Train 256 signed emission coefficients, one emission-gain multiplier and 24 reciprocal-neighbor coupling multipliers.
- Keep original local frequency, decay and I/Q emission projection fixed. No externally supplied phase/context signal and no imposed wave initial condition during the task. All states start at zero.
- Input context is solely a presynaptic spike history. Its effect must emerge from neuron activity and emission. Neighbor wave transfer occurs only through existing couplers; the global source stays off.

A programmable signed emission coefficient represents a differential current-steering interface. It is not a negative synaptic resistance. The physical implementation and energy of that interface are not transistor-validated. Coefficients belong to individual neurons within the shared tile, not to external context labels. They remain fixed during testing, including probe time; no oracle switches them according to the requested answer.

Emission weights apply **only to emission**. The inhibitory population sum stays unweighted and unchanged. A stopped pilot accidentally shared the projection with inhibition; it was stopped before any test and is preserved with STOPPED_PILOT.json. Its data are excluded.

## Training without a target wave phase

1. Run 32 training histories through the frozen baseline. From cue-period neuronal spike activity, estimate each neuron's supervised context contrast. Remove each population's common weighted cue activity. This initializes writer coefficients; context supervision is used only during host training.
2. Test 12 initial writer candidates on an 8-trial training batch: two polarities, gains 1/2/4, coupling multipliers .25/1. Select by downstream neuronal objective, not by desired I/Q coordinates.
3. Run eight population-based search generations, eight candidates each, taking the mean of the best three. Every generation uses a new training-history batch. Retain bounded coefficients/gains/couplers.
4. Validate the current candidate on 16 separate histories each generation. Select by neuronal selection with firing/amplitude/silence penalties. Freeze before generating 64 fresh test histories.

Objective: signed ensemble selection − .002 max(rate−30 Hz,0) − 2 max(peak |W|−.5,0) − .05 silent-trial fraction. Emission coefficients are bounded [-2,2], emission gain [.25,4], and neighbor multipliers [.25,2]. These normalized bounds are engineering assumptions, not a physical operating-voltage or energy specification.

There is **no target wave phase, wave separation loss, or wave decoder**. The objective uses actual post-probe neuronal spikes. Training is external and supervised; it is not biological local learning, STDP, or continual adaptation. It is also a limited one-seed search, not proof of optimality. Synaptic conductance training is intentionally omitted to isolate writer changes from changes in the spike computation.

The coupler retains its reciprocal conjugate edge relation. Its linear generator is skew-Hermitian; with intrinsic decay the unforced wave subsystem is dissipative. This does not establish stability of every nonlinear closed-loop operating condition or passivity of a transistor realization.

## Task and controls

Context cue 0–60 ms; silent interval to 140 ms; probe 140–220 ms. Each four-trial group has two different probes, each repeated byte-identically under opposite contexts. EA and EB each include 128 prescribed neurons, overlapping on 64. S=(mean EA spikes − mean EB spikes)/(mean EA spikes + mean EB spikes + epsilon). Correct sign defines correct ensemble; ties/silence count incorrect. Preferential activity is weaker than exclusive winner-take-all selection.

Natural interventions: erase W once at probe onset, disable feedback at probe onset, scramble phase, replace signed emission with absolute coefficients, shuffle coefficients across neurons, disable wave couplers. These are frozen-model interventions, not independently retrained competitor models.

Strict isolation: at probe onset clear neuronal/synaptic/refractory/event-delay/inhibitory states plus emission/detector filters, retaining only W. Compare retained W, erased W, disconnected feedback, and a common W across paired histories. Continuing emission remains enabled; identical neuronal inputs/states regenerate identical waves after erase. Natural erase retains other neuronal memories and therefore need not erase all history dependence.

Intervals bootstrap the 16 independent four-trial groups. Single topology/training seed and a small synthetic task limit generalization. Compare the baseline and trained writer on the SAME V24 holdout, not percentages from V23's different test set. No matched trained nonoscillatory control is included, so these results cannot establish oscillatory superiority over other continuous-state systems.

## Hardware and adaptation

281 writer parameters require programmable settings: 562 bytes at an assumed 16-bit digital equivalent, not physical area or measured RAM traffic. The learned settings also require current steering, coupling control and programming. Existing synaptic weights, feedback settings and dynamic physical state remain storage.

No chip power/energy/latency, memristor-device or Cadence benchmark is performed. Simulation duration is not ASIC latency. Do not infer human-like cognition, adaptive experience, or superior energy efficiency from this test.

Continual learning remains a separate milestone. Even if selection improves, a local eligibility/modulation rule would require its own learning/retention/reversal and programming-cost tests. Extra D/S current sources remain deferred; inherited D/S taps are only normalized capacitor charging-current components, not a complete extracellular field model.

## Reproduction

From this folder:

```
OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/writer.py
XDG_CACHE_HOME=/tmp/wave-v24-cache MPLCONFIGDIR=/tmp/wave-v24-mpl OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/report_v24.py
```

Every experiment creates a timestamped results folder. `selector.pkl` is the frozen local V23 checkpoint. `latest.txt` identifies the completed V24 run. Model dependencies are local; inherited `experiment.py` supplies construction/task utilities rather than the V24 entry point. Weights, protocol, development metrics, test inputs and response arrays are saved.

## Added online adaptation experiment

The user's subsequent instruction brings adaptation forward rather than requiring a perfect fixed writer first. `src/online.py` therefore runs a **separate online cohort** after the writer study. The writer results above still use frozen synapses; the following experiment explicitly permits conductance updates.

Each experience contains the original 220-ms cue/delay/probe sequence. Neural, wave and eligibility states reset at the next experience; synaptic conductances and reward baseline persist. This is episodic online learning, not yet uninterrupted continuous sensor processing.

At each allocated input contact, a pre trace decays with 20-ms time constant; each neuron has a 20-ms post trace. Eligibility decays with 100-ms time constant and accumulates `pre_trace * post_spike − 0.5 * post_trace * pre_event`. Reward is delivered 20 ms after the response; eligibility decays during that delay. The normalized eligibility is `clip(e/10, -1, 1)`. Synapses update by `ΔG=.02*M*e_used − .0001*(G−G_initial)`, clipped to [0.2,2]. M is ±1 correct/incorrect reward minus its prior running baseline, with baseline update rate .05. Wave does not directly enter the learning rule in this first test.

Three independent networks receive identical experience streams: local plasticity, plasticity off, and an independent random-modulator control. A compact digital online logistic reference receives three features derived from event counters (bias, cue-channel contrast, probe-channel contrast), predicts first, and updates three weights from the same post-response target feedback. It does not access W or a hidden context label as an inference feature. It uses a different learning rule/representation; this is an algorithmic reference, not a chip-to-chip comparison or matched parameter-count comparison.

The rule schedule is 48 original-rule experiences, 48 reversed-rule experiences, then 48 original-rule experiences again. The current rule is NOT given to either predictor. All learning hyperparameters were fixed before the new stream was generated; there is no test-based hyperparameter search. Performance is measured **before** each update. At four checkpoints, eight fixed original-rule probes are evaluated without updates. These reused probes assess retention but are a small diagnostic sample, not new independent trials at every checkpoint.

Measure per-phase performance, block-of-eight learning curves, first 16-trial window reaching 75% (or 'not reached'), retention and logical parameter changes. A contradictory rule reversal tests adaptation and recovery; it does not establish general catastrophic forgetting across distinct tasks. One stream lacks seed-level confidence intervals. Synapse changes alone establish implementation of the update mechanism, not useful biological adaptation.

Dense allocation of eligibility/pre traces requires 24,576 eligibility values + 24,576 pre traces + 256 post traces = 49,408 dynamic scalars, or 197,632 bytes at float32, plus reward modulation. This is an uncompressed logical allocation; shared afferents may allow physical compression. Programming counts count entries changing by more than 1e-9 normalized units, not measured device writes. No pulse quantization, endurance, physical energy, RAM transaction or power measurement is included. Retention-probe activity is excluded from training update totals.

Reproduce online adaptation before building the report:

```
OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/online.py
```

`online_latest.txt` points to its separately saved results. Plasticity is biologically inspired engineering; no claim of biological fidelity is made.
