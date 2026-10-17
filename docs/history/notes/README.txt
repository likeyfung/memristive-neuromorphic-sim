# Neuron–wave simulation v5 — causal tasks and 4,096-node tests

The latest [illustrated report](research/v5/report.html) contains seven captioned scientific figures, causal memory/selection tests, explicit wave-coupler routing, phase-controlled logic and scale checks. [Full methods](research/v5/REPORT.md), [raw trials](research/v5/results/trials.csv), and [audit](research/v5/results/audit.json) are included.

The model demonstrates deliberately engineered wave-assisted tasks; matched continuous-state controls also succeed. The 4,096-neuron task is replication scaling, while a separate 4,096-node lattice tests connected propagation. Hardware energy remains unmeasured. The v4 interactive interface below remains an exploratory tool, separate from the new scripted task assays.

---

# Neuron–wave simulation v4 — 64 to 1,024 neurons

Default display: **8 × 8 = 64 neurons**. The same engine runs 256 and 1,024 neurons. Each neuron has 8 individually addressed AMPA/NMDA synapses per dendrite, 3 dendrites per soma, and a local wave block with coupler-mediated dendritic and somatic feedback.

The completed research testbench includes **66 task simulations**, multipath interference checks, time-step refinement, digital delay-line baselines, state-count controls, and causal ablations. Read [the full specification and results](research/REPORT.md) or open [the self-contained illustrated report](research/report.html). All task data are in `research/results/random-context/`; plots are in `research/figures/`.

**Current conclusion:** short-delay information is sometimes more accessible in wave states, but this untrained network has not demonstrated superiority over the digital baseline, robust selection/XOR, or hardware energy savings. Small gains are sensitive to the integration step. The paper's final metadata were verified and the full author preprint v3 was read; the final publisher full text was inaccessible.

The interactive pulse demonstration uses 0.1 ms steps, recurrent weight 0.08 and local decay approximately 167 ms. The main task sweep uses 0.2 ms, with 64-neuron checks at 0.1 and 0.05 ms. Model defaults retain some older settings for regression compatibility; benchmark and UI overrides are explicit in their sources. Archived v1–v3 results are not the new benchmark.

## Implemented architecture

- One configurable rectangular array of neuron blocks, each with its own independent wave resonator.
- Default: **8 individual synapses per dendrite, 3 dendrites per soma**. That is 24 synapses per neuron and 1,536 in the default array. Counts are adjustable to 5–10 synapses per dendrite and 2–5 dendrites per soma. Three dendrites is an illustrative choice for the user's “a few.”
- Each synapse has its own AMPA and NMDA rise/decay states and individually addressed events `(time, neuron, dendrite, synapse, weight)`. Inputs sum locally at their assigned dendrite, then dendritic voltages feed one threshold soma.
- The gray local wave block feeds back to **both dendritic integration and soma integration**, with independently controlled gains and switches. Dendrite–soma electrical coupling means a perturbation at one compartment can subsequently influence the other even when its direct wave feedback is off.
- All modeled wave-transfer ports pass through an explicitly ablatable coupler: neighboring waves, global drive, local spike-to-wave emission, and local wave feedback. This is a conservative implementation of “all local and global wave transfer through the coupler.” Exact physical port placement and circuit transfer functions remain to be fitted.
- **All wave couplers off** blocks every transfer port. It does not delete internal oscillator state: an already excited resonator would continue free damped evolution. The UI reruns from zero initial wave state, so couplers-off trials remain at zero.
- **Neighbor connections off** only disconnects the neighbor-wave graph. Local emission/feedback and the global drive can still pass through the local coupler.
- The vertical readout bus is passive. ADC loading, sampling delays and power are not simulated.

The coupler's master enable currently applies to all nodes; per-node failures and per-port analog gains are not yet UI controls. Local feedback passes through the coupler but does not create a separate network state variable. The wave coordinates remain independent of the soma/dendritic states.

## Behavioral equations

Time: ms. Neural potential: mV. Conductance: normalized to dendritic leak. Wave coordinates: arbitrary normalized units. No physical chip time scaling is inferred.

For synapse k on dendrite b of neuron i, every addressed event adds its weight to four independent exponentially decaying states. AMPA rise/decay constants are 0.5/5 ms; NMDA rise/decay constants are 4/80 ms. Differences are peak-normalized, with peak factors 1.0 for AMPA and 0.65 for NMDA. Individual weights are carried on events; learning/plasticity is not implemented. Each synapse has the same kinetics in this first version.

```
GA_ib = Σ_k gA_ibk
GN_ib = Σ_k gN_ibk
B(D) = 1 / [1 + exp(−0.062 D) / 3.57]
12 dD_ib/dt = (−65 − D_ib) + [GA_ib + GN_ib B(D_ib)] (0 − D_ib)
              + 0.25 (V_i − D_ib) + F_Di
20 dV_i/dt = (−65 − V_i) + (1.6 / number_of_dendrites) Σ_b (D_ib − V_i) + F_Si
F_Di = enabled_dendrite_feedback × coupler(betaD tanh(x_i))
F_Si = enabled_soma_feedback × coupler(beta tanh(x_i))
```

Default `betaD = 8 mV`, `beta = 11 mV`. Total soma–dendrite gain is held at 1.6 when the branch count changes; this is a modeling choice, not a measured circuit property. Threshold is −52 mV, reset −60 mV, refractory period 3 ms. Only spike events are modeled, not action-potential voltage shapes. The general receptor formulation follows [Neuronal Dynamics §3.1](https://neuronaldynamics.epfl.ch/online/Ch3.S1.html); selected parameters are illustrative rather than fitted biological or silicon values.

```
omega_i = 2π f [1 + 0.075(i mod columns) / max(1, columns − 1)] / 1000
K_ij = K [1 + 0.4 tanh((x_i + x_j)/2)]
C_i = Σ_neighbors K_ij (x_j − x_i)
G(t) = A_global sin(2π f_global t / 1000 + phase)
dx_i/dt = omega_i p_i
dp_i/dt = −omega_i x_i − 2 gamma p_i + omega_i coupler(C_i + G(t))
p_i ← p_i + coupler(0.38)       on local spike, when emission is enabled
```

`coupler(q)` returns q when wave/coupler enables are on, zero otherwise. Neighbor coupling and global drive have additional independent switches. The nonlinear reciprocal neighbor transfer is a hypothesis for state-dependent coupling; the master port gate is ideal, instantaneous and unity-gain. Defaults are local base frequency 12 Hz, global drive 20 Hz with amplitude 0.55, K=0.55, gamma=0.004/ms. The isolated resonator is damped, not a self-sustained limit cycle; it can retain a decaying state after excitation. No physical energy claim follows from these equations.

Phase shuffle rotates each local `(x,p)` pair once at 350 ms while preserving that pair's squared norm. Coupling energy need not be conserved. It is not a reset and not repeated phase noise. The global-phase control changes the phase of the external sinusoid; initial transients should be excluded in a steady-state phase experiment.

## Inputs, display and controls

The pulse protocol supplies a seven-event burst on **each dendrite** of all neurons in the leftmost column from 100 to 160 ms, cycling through individual synaptic addresses. Each dendrite of every neuron receives a weaker four-event probe at 700–730 ms. Consequently total event count changes with dendrite count; changing architecture is not a matched-input comparison. Within an ablation batch, exact event lists are identical.

The memory protocol keeps total event rate per neuron at `35 ± 25u` Hz, then assigns each event to a random valid dendrite and synapse. It uses a seeded independent input in 100 ms bins. Spreading the same event budget over multiple dendrites changes excitation compared with v1; results are not directly comparable.

The default **recurrent spike graph** gives each target six distinct incoming presynaptic neurons (1,536 directed links at N=256), excluding self-connections. One source per target forms a closed ring; the remaining sources are seeded pseudorandom connections. Each input uses a separate synaptic slot, distributed across dendrites. Defaults: weight 0.3, delay 1 ms. These are excitatory AMPA/NMDA connections; there is no inhibitory population or plasticity in this version. Their exact topology and weights are illustrative, not taken from the circuit drawing. Disable Recurrent spike network to isolate external input plus wave dynamics.

The **wave graph is separate**: four-neighbor rectangular lattice with open boundaries, 480 undirected edges at 16 × 16. Turning off wave coupling does not delete spike links, and turning off recurrent spikes does not delete wave edges. The local frequency gradient spans the same 7.5% across a row at every size.

The four mode presets are local self-feedback, local traveling wave, global drive plus local coupling, and spike-only. Presets enable both feedback targets; individual switches customize them. Changes apply with **Run matched trials**. Select a neuron, dendrite and individual synapse to inspect internal states; the snapshot slider inspects an existing run. The array view shows wave state in each cell, recent soma spikes as dots, and only the selected neuron’s outgoing spike links to keep the graph readable. The population field averages adjacent neuron IDs into at most 128 lanes and labels this aggregation explicitly. Node selection retains unaggregated internal traces. The detailed neuron schematic explicitly displays synapse fan-in, dendritic convergence, soma, gray wave block and coupler. The interactive run logs delivered events and reconstructs individual receptor traces analytically for the selected neuron. This avoids storing all individual synapses at every timestamp. The headless engine can still record all synapses with `recordSynapses:true`.

The wave heatmap saturates visually at ±0.8 and the wave traces display ±1; the numerical engine does not clamp waves. Conductance plots show the selected individual synapse, before the NMDA voltage block. The diagram's blue/orange paths identify spike/emission and wave feedback; gray boxes are local wave blocks and neutral dark/light squares are couplers.

Nine matched trials: selected settings; wave off; all feedback off; dendritic feedback off; soma feedback off; all couplers off; neighbor connections off; emission off; phase shuffle. Metrics are spike count, wave RMS over 400–650 ms, and soma-voltage RMS difference from spike-only. Neither higher firing nor nonzero wave RMS is a task-performance score.

## Reproducibility and checks

```sh
node tests/model.test.js
node research/src/mechanisms.js
node research/src/run-benchmarks.js main
node research/src/run-benchmarks.js ablations
node research/src/run-benchmarks.js gains
node research/src/run-benchmarks.js convergence
node research/src/run-benchmarks.js fine
python3 research/src/analyze.py
python3 research/src/write-report.py
python3 src/build.py
```

Dependencies: Node.js, Python, NumPy, SciPy, Matplotlib and Markdown. The inline simulation makes no network requests and shares `src/model.js` with all headless experiments. See `research/REPORT.md` for data partitions, controls, numerical limitations, literature and measured scores. The older `src/benchmark.py` remains an archived-style pilot; it is not the source of the v4 figures.

Twenty regression checks pass, and the dedicated mechanism tests verify coupler blockade, disconnected paths, linear superposition and reference-integrator agreement. All 66 task simulations produced finite features. Halving the integration step changes small task gains; this is recorded as a limitation, not hidden by the finite-state checks.

`research/results/manifest.json` records the model hash and dataset validation. Benchmark scripts skip existing run files, so changed experiments must use a fresh result directory. The illustrated report embeds its images and can be opened offline. The inline view's short-pulse protocol is separate from the task experiments.

This model does not establish silicon feasibility, prior-art novelty, biological cognition mechanisms or reductions in RAM/data movement/energy. Circuit mapping needs receptor transients, dendrite/soma biases, coupler transfer functions, physical time scaling, noise and PVT data. The software uses digital memory to represent its states.
