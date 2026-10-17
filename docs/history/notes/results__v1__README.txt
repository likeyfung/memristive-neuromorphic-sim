# Neuron–wave behavioral simulation

This prototype follows the two-layer architecture on page 2 of **Likey 改過.pdf**. It is an executable hypothesis model, not a transistor-level reproduction or a claim of a first silicon implementation.

The interactive simulation appears in the task conversation. Its source is `src/view.html`; the numerical engine is `src/model.js`. The same engine runs the automated checks and memory experiment. No network calls, training service, or external datasets are needed by the simulation.

## Architecture and explicit assumptions

Eight light-blue neuron blocks form a 2 × 4 array. Each contains two dendritic compartments, AMPA-like and NMDA-like synapses on each compartment, one threshold/reset soma, and a separate two-coordinate local wave resonator.

| Circuit path from your description | Behavioral implementation |
|---|---|
| `pre_event` / presynaptic event line | Events add equal amounts to each receptor's rise and decay states; their difference produces a conductance transient. |
| Local neuron → local wave, `I_emit` | An emitted soma spike adds an impulse to its own resonator coordinate `p`. |
| Neighbor wave line through local couplers | Reciprocal nearest-neighbor coupling on a 2 × 4 lattice. There is no direct neighbor-wave injection into dendrite or soma. |
| Global wave bus → local couplers | A common 20 Hz sinusoidal drive enters each wave resonator's coupling input. It never directly drives the neural compartments. |
| Local wave → neuron, `I_fb` | The local coordinate `x` modulates only its own soma input, through a bounded transfer function. |
| Vertical readout bus → mux / buffer / ADC | Passive observation in this model. No analog load, multiplexing delay, quantization, ADC power, or back-action is simulated. |

**Interpretation of the drawing:** the vertical blue lines on page 2 are explicitly labeled *Readout Bus*. The incoming presynaptic event line is separate. The waveform coupler and readout should not be conflated.

**Coupler assumption:** local `I_emit` drives the local resonator separately; neighboring/global waves enter only through that node's coupler. Neighbor conductance depends on the local states at both ends, so a middle node changes transmission. This bounded reciprocal transfer function is an assumption pending your circuit schematic. It does not purport to model a specific transistor coupler.

**Spike connectivity assumption:** optional weak feed-forward spikes travel along each row, N0 → N1 → N2 → N3 and N4 → N5 → N6 → N7, with a 1 ms delay and weight 0.3. The slide does not specify synaptic weights. Turn off *Spike forwarding* to isolate the wave communication path. The blue incoming markers in the schematic show presynaptic events; the forwarding matrix is specified here rather than displayed as another overlapping graph.

## State equations and units

Time is in milliseconds; soma and dendritic potentials are in mV. Conductances are normalized to dendritic leak. Wave coordinates are dimensionless. These are model units, not measured chip voltages/currents or physical time scaling.

Each synapse has four decaying states `(a_decay, a_rise, n_decay, n_rise)`. An input of weight `w` adds `w` to all four. Between events they decay exponentially. Conductances are:

```
gA = 1.0 × (a_decay − a_rise) / peak_normalizer(0.5, 5)
gN = 0.65 × (n_decay − n_rise) / peak_normalizer(4, 80)
B(D) = 1 / [1 + exp(−0.062 D) / 3.57]
12 dD_b/dt = (−65 − D_b) + [gA_b + gN_b B(D_b)](0 − D_b)
             + 0.25 (V − D_b)
20 dV/dt = (−65 − V) + 0.8 (D_0 − V) + 0.8 (D_1 − V)
           + beta tanh(x)
```

`beta tanh(x)` is zero whenever wave or feedback is disabled. Threshold is −52 mV, reset is −60 mV, and refractory time is 3 ms. Conductance reversal is 0 mV. A soma spike is an event, not a modeled action-potential waveform. The NMDA voltage dependence is a biological-style approximation; it is not fitted to your NMDA silicon path. Independent AMPA/NMDA time constants and voltage dependence follow the general conductance-model approach described in [Gerstner et al., Neuronal Dynamics, §3.1](https://neuronaldynamics.epfl.ch/online/Ch3.S1.html); numerical parameter choices here are illustrative.

Each wave block has independent states `(x_i, p_i)`:

```
omega_i = 2π f [1 + 0.025(i mod 4)] / 1000
K_ij = K [1 + 0.4 tanh((x_i + x_j)/2)]
C_i = Σ_neighbors K_ij (x_j − x_i)
G(t) = A_global sin(2π f_global t / 1000 + phase)
dx_i/dt = omega_i p_i
dp_i/dt = −omega_i x_i − 2 gamma p_i + omega_i [C_i + G(t)]
p_i ← p_i + 0.38                    on local soma spike
```

Defaults: local base frequency 12 Hz; global frequency 20 Hz; `gamma = 0.004 /ms`; `K = 0.55`; `beta = 11 mV`; global amplitude 0.55 when enabled. There is a small fixed frequency gradient; it is an illustrative heterogeneity, not measured mismatch. The state-dependent coupler remains positive over the UI range. Inputs are superposed before the local nonlinear feedback, allowing interference without making oscillators the neuron nodes.

An isolated undriven resonator is damped, with approximate amplitude time constant `1/gamma = 250 ms`. “Self-generated” means spike-excited ringing in this version, not an autonomous limit-cycle oscillator. Between spikes, its continuous state evolves independently. If your circuit is a self-sustained oscillator, replace this resonator with its measured nonlinear dynamics.

No wave amplitude clamp is used in the engine. The heatmap clips color intensity at ±0.8, and the wave trace displays ±1; these are display ranges only. The AMPA/NMDA plot sums the two branches' conductances before NMDA voltage gating.

## Four modes and causal controls

- **Local self-feedback:** isolated local wave blocks, local emission and feedback on, global drive off.
- **Local traveling wave:** local emission, feedback and neighbor coupling on, global drive off.
- **Global wave + local coupling:** global drive, local emission, feedback and neighbor coupling on. This mode includes both sources; disable emission to study a purely global drive.
- **Spike only:** wave state clamped to zero, retaining AMPA/NMDA, dendrites, soma and the same input.

Independent controls additionally disable the neurons, emission, feedback, coupling, global drive or spike forwarding. Controls apply when **Run matched trials** is pressed; the snapshot slider and neuron selection inspect the last completed run. Every trial starts from the same resting neural and zero wave states. Selecting a mode sets its switches; subsequent changes customize that mode.

**Neuron off** holds the entire neural layer at rest, while wave dynamics remain active. From zero initial wave state this needs a global drive to show activity. **Wave off** eliminates both local wave coordinates, including global forcing. **Feedback off** retains the evolving wave state but removes its effect on the neurons. It should give exactly the same neural trajectory as wave off under the same external events.

The phase-shuffled comparison rotates every `(x_i,p_i)` independently once at 350 ms using a fixed seed. Each local `x_i²+p_i²` is preserved at the intervention. This is a phase-space operation, not a claim that total coupled-network energy is conserved: inter-node coupling energy can change. Global drive phase and amplitudes are unchanged. It is a one-time intervention, not repeated phase noise, and is only informative when nonzero wave state is present.

The global-phase slider changes only the external sinusoid's phase, with a fixed amplitude/frequency. Because starting from rest with different forcing phase changes the transient, use an adequate settling period before interpreting it as a steady-state phase-routing test.

## Inputs and interpretation

The pulse protocol applies seven events at 10 ms intervals from 100 through 160 ms to N0 and N4, then leaves a silent interval. All nodes receive four weaker events from 700 through 730 ms. The heatmap shows spatial wave displacement, with soma spikes overlaid. Selecting a neuron exposes its two wave coordinates, soma/dendrite voltages, and receptor conductances.

The default pulse run produces **two spikes in both full and wave-off conditions**. The full model retains a wave RMS of about 0.0300 in 400–650 ms and changes the soma trajectory by about 0.1356 mV RMS relative to wave-off. This demonstrates internal state and feedback in this model, not improved task performance. Slow NMDA and dendritic states are already retained in the baseline; any memory claim must improve on those states.

The changing-input protocol uses a seed-fixed piecewise-uniform signal in 100 ms bins, converted into independent event streams. Rates are `35 ± 25 u` Hz depending on row. The input is generated before each matched comparison and is not regenerated by different internal spike activity.

## Reproduce checks and the memory pilot

Requirements: Node.js, Python 3, and NumPy. The interactive view requires no npm install.

```bash
node tests/model.test.js
node src/run.js '{"wave":true,"global":false}' > results/trajectory.json
python3 src/benchmark.py --node node
python3 src/build.py
```

`build.py` emits the self-contained inline simulation in this task's visualization directory. Set its `out` path if moving the project. Files `src/view.html` and `src/model.js` are the editable sources; do not separately edit the embedded engine.

The engine integrates wave dynamics with RK4 and neural voltages with an explicit timestep; receptor decays are exponential. Event timing is quantized to the timestep. Default dt is 0.1 ms; comparisons use identical discretization. Eleven tests cover determinism, ablation invariants, isolation/propagation, phase intervention, finite states at UI gain extremes, and timestep halving. At the default pulse settings, the maximum wave-coordinate difference between 0.1 and 0.05 ms sampled trajectories is about 0.00142; spike counts match. This is a local convergence check, not a guarantee across all parameter choices.

The memory pilot uses independent fixed train/validation/test seeds (101/202/303), each 16 seconds, a 1-second washout and 100 ms bins. A linear ridge decoder reconstructs a past input bin. “100 ms delay” means the target bin ended 100 ms before readout, i.e. its contents are 100–200 ms old. Hyperparameters are selected using only validation data. Test data is never used to fit normalization or coefficients. The ridge fitting procedure and input are matched, but each condition is allowed its own trained coefficients and selected ridge strength.

Two readouts are reported: eight filtered spike rates; and the same rates plus 16 wave coordinates. The latter uses a fixed 24-slot layout in all conditions, with wave-off slots set to zero. This still adds usable state capacity when enabled. A stronger study should include an equal-state-budget alternative reservoir and matched readout costs. Reporting spike-only readouts helps separate feedback effects from merely observing extra state.

See `results/memory.md` and `results/memory.json`. The initial result does **not** establish a robust advantage: at 100 ms delay the spike-readout R² is approximately 0.074 with full coupling versus 0.047 without waves, but performance at 200 and 400 ms is below the test-mean baseline. Direct wave readout does not improve this pilot. One split cannot establish statistical significance. No selection of parameters was performed using these benchmark results.

## What this does and does not establish

The prototype supplies controllable candidate mechanisms for independent continuous state, local feedback, neighbor transmission and phase interventions. It does not establish novelty, biological cognition mechanisms, reliable routing/computation gains, physical memory lifetime, power savings or reduced RAM/data movement on a chip. The software itself stores all simulated states in digital memory. No noise, PVT variation, parasitics, transistor saturation, coupling delays, driver loading or physical energy measurement is included.

To map this to silicon, the next necessary inputs are the resonator/coupler transfer functions or netlists, AMPA/NMDA pulse responses, dendrite/soma bias and threshold curves, the `I_emit` and `I_fb` polarities/gains, actual connectivity, and biological-to-chip time scaling. A causal benefit on silicon would demonstrate a computational mechanism in this platform; evidence about brain cognition requires additional biological experiments. “First” requires a separate prior-art review.
