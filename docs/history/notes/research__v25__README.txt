# V25 — Where should local synaptic learning act?

V24 and earlier versions are preserved. V25 copies the successful V24 writer and the V23 controlled selector into local checkpoints, then compares local learning rules without changing wave hardware or adding a wave decoder.

## What changes

Compare three plasticity locations:

1. Input AMPA/NMDA contact conductances.
2. Excitatory recurrent spike conductances, including existing local and interpopulation edges.
3. Both sets.

Inhibitory recurrent weights remain fixed. No connections are added or removed. The 256 neurons, 16 WaveTiles, emission coefficients/gain, neighbor couplers, feedback settings, frequency/decay, thresholds and population-inhibition parameters stay fixed. Local plasticity can change which population activity subsequently excites W, and how wave-influenced activity propagates through the spike network.

## Eligibility and feedback

The reference eligibility uses local pre/post traces (20 ms): pre-trace × post-event potentiation and 0.5 × post-trace × pre-event depression. Recurrent pre-events use the actual delayed arrival, not the original source firing time. Compare this with the same rule multiplied by a local branch-activity factor `d_plus/(0.1+d_plus)` evaluated from the dendritic state before the integration step. The factor applies at the appropriate contact/target branch. It is a reduced engineering voltage gate, not an anatomical calcium model.

There is **no explicit W multiplier**. Wave feedback affects dendrites and firing; those local quantities affect eligibility. No wave phase, hidden context label or current rule enters the predictor or the eligibility rule.

Compare eligibility decay constants 100 and 300 ms. Reward arrives 20 ms after the response. Eligibility is divided by 10 and clipped to [-1,1]. Candidate learning rate is 0.05, with conductance decay toward initialization of 0.0001 per experience; bounds [0.2,2]. Reward is ±1 correctness minus its preceding exponentially running baseline (update rate 0.05). This tests location, local dendritic information and timing while retaining the same scalar credit signal. It is not a complete search over credit-assignment mechanisms.

## Development → validation → freeze → new streams

Twelve candidates: three locations × two rules × two eligibility lifetimes. All candidates receive the same 72-experience calibration stream (24 original, 24 reversed, 24 original-return). Keep the top two candidates per plasticity location, then evaluate them on an independent 72-experience validation stream starting from the same initial conductances. Select one per location by mean pre-update accuracy across the three phases.

Freeze learning rules and all wave/selector settings before generating three new 144-experience test streams (48 experiences per phase). Each stream begins from the same pretrained conductances. Test the selected three rules, plasticity off, the V24 input-only rule (eta .02, tau100), and an independent random-modulator control with the best validation configuration. The random control is a fixed-rule ablation, not a separately calibrated competitor. The V24 rule is a historical reference, not an equally searched learner.

The digital reference remains an online three-weight logistic learner of spike-count contrasts, with learning rate .2, starting from zero weights. It predicts before target feedback. It is an algorithmic reference with different features and initial knowledge, not a hardware-matched competitor. Recurrent topology/training seed is fixed; the three fresh streams vary stimulus histories. Stream variation does not establish robustness to fabrication mismatch or topology seeds.

Mean development accuracy is the declared selection objective. It can favor retaining the original mapping because that rule occurs twice; report reversal and return separately rather than treating the selection objective as comprehensive adaptive performance. No candidate is retuned after test results are observed.

## Task and interpretation

Inputs remain presynaptic spike histories: 60-ms cue, silence to 140 ms, then an 80-ms probe. Neuronal output is the fixed EA−EB ensemble spike difference. Paired trials repeat the same current probe across opposite contexts. The reversal changes the desired mapping without announcing a rule identifier to the network.

Neural/wave/eligibility states reset between experiences. Conductances and reward baselines persist. This is episodic online adaptation; it does not demonstrate uninterrupted continuous sensor processing. Eight no-update original-rule probes are reused at checkpoints for each stream. Retention is interpretable only alongside reversal learning: retaining an old mapping while failing to acquire the new one is not successful continual learning.

## Causal and numerical checks

The revised recurrent-delivery implementation is checked against the V24 baseline: identical neuronal output, total spikes and input eligibility in a one-episode comparison. This is a regression check, not a full timestep-convergence study.

After learning, retain only W at probe onset by clearing neuronal/synaptic/delay/inhibitory state and emission/detector filters. Compare retained W, strict wave erase and strict feedback-off on matched probes. Also compare eligibility with feedback enabled/disabled at fixed learned weights. The latter confirms influence through neural activity, not that wave-dependent eligibility improves learning.

Saved checkpoints permit checking frozen control, immutable inhibitory edges and unselected plasticity locations. The fresh-stream experiment checks finite/bounded conductances and exact strict-ablation equalities. No online timestep-convergence, device-noise or PDK verification is claimed.

## Physical storage and programming

Input plasticity needs the input eligibility/pre/post traces; recurrent plasticity can use source-neuron pre traces and one eligibility per edge. Dense logical allocations, excluding existing neuron/wave state and modulation:

| Plasticity location | Additional trace scalars | Float32 equivalent |
|---|---:|---:|
| Input only | 49,408 | 197,632 bytes |
| Recurrent only | 1,792 | 7,168 bytes |
| Both | 50,944 | 203,776 bytes |

These counts describe a possible allocation after omitting unused diagnostics. The simulator computes both kinds for analysis. Inhibitory eligibility entries are allocated but zero; shared afferents and sparse connectivity could permit further compression. Equivalent bytes do not equal required SRAM, physical capacitor area, or measured DRAM transactions.

Report actual entries changing by more than 1e-9 normalized units and total conductance variation. Programming pulse quantization, memristor endurance, energy and analog trace leakage/noise remain unmodeled. No energy or latency advantage is inferred from these experiments.

## Reproduce

From this folder:

```
OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/learning.py
XDG_CACHE_HOME=/tmp/wave-v25-cache MPLCONFIGDIR=/tmp/wave-v25-mpl OPENBLAS_NUM_THREADS=1 /tmp/wave-v7-env/bin/python src/report_v25.py
```

Runs create fresh timestamped folders. The model imports only local dependencies. `selector.pkl` and `writer.pkl` are fixed local checkpoint copies. `protocol.json`, development results, frozen rules, test inputs, per-experience responses, synaptic checkpoints and diagnostics are saved. D/S field-source detail, explicit wave-gated plasticity, more neurons and on-chip training are not added in this revision.
