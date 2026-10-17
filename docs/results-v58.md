# V58: evidence and interpretation

[Back to the project](../README.md) · [Public aggregate statistics](evidence/v58-summary.json)

V58 asks three prespecified questions: does earlier history select a later neuronal ensemble; how does spatial state coupling compare with equally calibrated local controls; and how sensitive is the result to modeled electrical disturbances?

## Experimental design

Three families receive equal 12-candidate training searches; the top three candidates per family are assessed on separate validation histories. Each family acquires six final memory sets, saves its learned weights, and freezes the relevant sources and settings before new evaluation histories are generated. Test results are not used to retune the system.

The causal cohort has eight episodes per memory set and condition, at 350 and 950 ms delays. Earlier history differs across paired contexts, but inputs from 60 ms onward, including the partial cue, are identical. The output is measured from reader-neuron spikes. F1 scores pattern completion after excluding directly cued features; ensemble-selection accuracy and exact completion are separate metrics.

There are 384 nominal/intervention episodes and 192 corresponding pairs. The stress cohort has 1,584 episodes across three families and eleven conditions, with two device draws per memory set. Intervals bootstrap the six memory sets. This is a small number of independent clusters and does not characterize a manufacturing yield distribution.

## Nominal and causal results

| Configuration | Mean F1 | 95% cluster-bootstrap interval | Interpretation |
|---|---:|---:|---|
| Spatial, intact | 0.943 | 0.860–0.994 | Learned content recalled under history-dependent access |
| Spike broadcast with local state | 0.943 | 0.860–0.994 | Equal observed nominal performance |
| Isolated local state | 0.000 | 0.000–0.000 | Cannot deliver remote context in this setup |
| Spatial, shared state erased | 0.000 | 0.000–0.000 | The tested state intervention disrupts recall |
| Spatial, feedback disabled | 0.000 | 0.000–0.000 | The state-to-neuron feedback path is causally necessary here |
| Spatial, state held at zero | 0.000 | 0.000–0.000 | Continued state suppression also disrupts recall |
| Fast neuronal reset, shared state retained | 0.887 | 0.727–0.985 | Retained state supports substantial recovery in this diagnostic |
| Fast neuronal reset and shared-state erase | 0.000 | 0.000–0.000 | Removing both eliminates that recovery |

The intact spatial circuit has 42/48 exact completions, 46/48 correct ensemble selections, and both contexts correct in 23/24 matched pairs. These measures answer different questions and should not be substituted for one another.



## Stress and event counts

Under the combined engineering stress model, mean F1 is **0.6234** for spatial coupling and **0.4937** for spike broadcast. The paired difference is **0.1296**, with 95% cluster-bootstrap interval **0.0685–0.1898**. Several other stress conditions tie, and a stronger thermal-noise condition has a small negative point estimate for the spatial advantage. The full condition table remains in the local research archive; the main comparisons are included in the [public aggregate summary](evidence/v58-summary.json).

At equal observed nominal recall, the spatial circuit emits **25.8% fewer total spikes** and **75.0% fewer writer spikes** than broadcast. Recurrent contact deliveries are slightly higher, so this is not a reduction in every operation category. Converting events to joules requires routing, fanout, bias, calibration, and readout costs. The [public aggregate summary](evidence/v58-summary.json) explicitly marks energy verification as false; the detailed cost assumptions remain in the local archive.



## Electrical evidence

Fourteen ngspice transients test a small writer/state/receiver loop under ideal, feedback-off, mismatch, injected-noise, leakage, and combined conditions. All recorded transients are finite. Combined disturbances substantially change receiver spike counts across draws. These are behavioral circuit blocks with assumed parameters, not transistor-level PDK validation or a full memory-task circuit validation.

The electrical summaries, netlists, logs, and raw transients remain in the local research archive. This documentation release publishes their aggregate findings, rather than the detailed artifacts.

## Reproducibility and evidence boundaries

The preserved local source freeze contains 85 hashed source/configuration files, including learned weights and inherited model dependencies. During publication preparation, all 85 files were checked against the original hashes. Full/compact, neutral-kernel, and passive-noise smoke checks passed; one electrical deck reproduced its archived event counts. The complete source/data package is not included in this documentation release. Historical V40 had a broader solver comparison; that historical coverage is not relabeled as a new V58 validation cohort.

This evidence supports history-dependent neural selection and specific causal mechanisms in a constrained synthetic task. It does not establish an oscillatory-wave necessity, universal superiority to digital algorithms, brain identity restoration, clinical memory improvement, or measured ASIC efficiency.
