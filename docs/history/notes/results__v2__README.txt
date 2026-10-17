# Neuron–wave simulation v2

Updated to match the user's clarified hierarchy and feedback paths. This is a behavioral model, not a transistor-level reproduction. The earlier simplified model's results are archived under `results/v1/` and must not be interpreted as results of this architecture.

## Implemented architecture

- One 2 × 4 array of eight neuron blocks, each with its own independent wave resonator.
- Default: **8 individual synapses per dendrite, 3 dendrites per soma**. That is 24 synapses per neuron and 192 in the array. Counts are adjustable to 5–10 synapses per dendrite and 2–5 dendrites per soma. Three dendrites is an illustrative choice for the user's “a few.”
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
omega_i = 2π f [1 + 0.025(i mod 4)] / 1000
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

The pulse protocol supplies a seven-event burst on **each dendrite** of N0 and N4 from 100 to 160 ms, cycling through individual synaptic addresses. Each dendrite of every neuron receives a weaker four-event probe at 700–730 ms. Consequently total event count changes with dendrite count; changing architecture is not a matched-input comparison. Within an ablation batch, exact event lists are identical.

The memory protocol keeps total event rate per neuron at `35 ± 25u` Hz, then assigns each event to a random valid dendrite and synapse. It uses a seeded independent input in 100 ms bins. Spreading the same event budget over multiple dendrites changes excitation compared with v1; results are not directly comparable.

Optional feed-forward spike links run along each row with weight 0.3 and delay 1 ms, targeting dendrite 1 / synapse 0. These illustrative connections are not specified by the user's circuit drawing. Disable Spike forwarding to isolate wave communication.

The four mode presets are local self-feedback, local traveling wave, global drive plus local coupling, and spike-only. Presets enable both feedback targets; individual switches customize them. Changes apply with **Run matched trials**. Select a neuron, dendrite and individual synapse to inspect internal states; the snapshot slider inspects an existing run. The detailed neuron schematic explicitly displays synapse fan-in, dendritic convergence, soma, gray wave block and coupler. Individual conductances are stored only when `recordSynapses` is enabled (the interactive run enables it).

The wave heatmap saturates visually at ±0.8 and the wave traces display ±1; the numerical engine does not clamp waves. Conductance plots show the selected individual synapse, before the NMDA voltage block. The diagram's blue/orange paths identify spike/emission and wave feedback; gray boxes are local wave blocks and neutral dark/light squares are couplers.

Nine matched trials: selected settings; wave off; all feedback off; dendritic feedback off; soma feedback off; all couplers off; neighbor connections off; emission off; phase shuffle. Metrics are spike count, wave RMS over 400–650 ms, and soma-voltage RMS difference from spike-only. Neither higher firing nor nonzero wave RMS is a task-performance score.

## Reproducibility and checks

```
node tests/model.test.js
node src/run.js '{"dendrites":3,"synapsesPerDendrite":8}' > results/trajectory.json
python3 src/benchmark.py --node node
python3 src/build.py
```

Dependencies: Node.js; Python/NumPy for the benchmark. The inline view has no network requests or external libraries. `src/model.js` is shared by the UI and headless runner. `src/build.py` embeds it into `src/view.html` and writes the result into this task's visualization directory; adjust its output path when moving projects.

Fifteen checks cover addressed synapse isolation, configurable fan-in, both feedback targets, whole-coupler blockade, neighbor isolation, determinism, ablations, and numerical behavior. The isolated-wave test excludes the later probe, since that probe can legitimately excite remote neurons' own waves. Default timestep is 0.1 ms; the wave equation uses RK4, neural voltages use an explicit update, and receptor states decay exponentially. At 0.05 ms, default pulse spike counts agree and maximum sampled wave difference is approximately 0.014. This is one operating-point convergence check, not a global bound. The master coupler and all-feedback ablations exactly recover the baseline neural trajectory under their tested inputs.

The memory pilot uses independent 16-second train/validation/test seeds, a 1-second washout, 100 ms input bins, train-only scaling, and validation-selected ridge penalties. Delay labels describe the time since the target bin ended. It tests eight filtered-spike features and 24 spike-plus-wave feature slots, with wave-off slots zeroed. Each condition has separately fitted readout coefficients. Extra usable wave features remain a capacity confound; this is not a matched physical state/energy budget test.

Current outputs are `results/memory.md` and `results/memory.json`. The rerun with v2 does not establish useful delayed-input decoding or an advantage: the full model's tested R² values are negative. Prior v1 figures are retained only as historical results. No parameter tuning was performed against these held-out results. Routing accuracy and nonlinear computation benchmarks are not yet implemented.

This model does not establish silicon feasibility, prior-art novelty, brain cognition mechanisms or reductions in RAM/data movement/energy. Needed for circuit mapping: receptor transient responses, dendrite/soma biases and gain curves, local wave and coupler transfer functions, feedback polarities, physical time scaling, noise and PVT data. The software uses digital memory to represent all states.
