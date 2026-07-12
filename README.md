# Recurrent Memristive Neuromorphic System

A Python simulation of a **recurrent neuromorphic circuit** built from ion-diffusion memristors. This is a **hardware physics simulation** — not a cognitive or AI model. It models the actual electrical and material behaviour of memristor crossbar arrays, and shows how different physical retention properties (volatile, semi-volatile, non-volatile) naturally give rise to distinct computational roles without any software workaround.

The four crossbar modules are named after brain regions not because the simulation models the brain, but because each memristor type physically exhibits the same retention timescale as its biological counterpart:

| Crossbar | Named after | Physical property | τ_diff |
|----------|-------------|-------------------|--------|
| HC | Hippocampus | **Volatile** — ions diffuse back quickly | 50 ms |
| PFC | Prefrontal Cortex | **Non-volatile** — ions locked in place | ∞ |
| OFC | Orbitofrontal Cortex | **Semi-volatile** — intermediate retention | 500 ms |
| EC | Entorhinal Cortex | **Fixed oscillatory** — no plasticity | — |

The benchmark task (Delayed Match-to-Sample) is used purely to verify that the hardware physics are correct: the volatile crossbar correctly forgets during the delay period, while the non-volatile crossbar correctly retains the pattern — this is a test of the memristor ODEs, not a demonstration of machine learning or cognition.

---

## Architecture Overview

```
 External Input (spike pattern)
        │
        ▼
 ┌──────────────────────────────────────────────────────┐
 │              Gate Controller (DMN/PCC)               │
 │  Dopamine · ACh · TD-error · Synchronisation pulses  │
 └──┬──────────┬───────────┬──────────┬─────────────────┘
    │          │           │          │
    ▼          ▼           ▼          ▼
 ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
 │  HC  │  │ PFC  │  │ OFC  │  │  EC  │
 │Volat.│  │Non-V.│  │Semi-V│  │Fixed │
 │τ=50ms│  │  τ=∞ │  │τ=500 │  │Grid  │
 └──────┘  └──────┘  └──────┘  └──────┘
    │          │           │          │
    └──────────┴───────────┴──────────┘
                     │
                     ▼
              Linear Decoder
           (ridge regression)
                     │
                     ▼
              Task Output
           (Cat / Dog label)
```

### The Four Modules

| Module | Brain Region | Memristor Type | τ_diff | Role |
|--------|-------------|----------------|--------|------|
| **HC** | Hippocampus | Volatile | 50 ms | Short-term reservoir; SWR/theta replay |
| **PFC** | Prefrontal Cortex | Non-volatile | ∞ | Working memory; gamma-paced task rules |
| **OFC** | Orbitofrontal Cortex | Semi-volatile | 500 ms | Value/reward; TD-error learning |
| **EC** | Entorhinal Cortex | Oscillatory (fixed) | — | Grid-cell state-space representation |

---

## Memristor Device Physics

Every device implements the **ion-diffusion ODE**:

```
dw/dt = η₀ · sinh(V/V₀) · f(w) − w/τ_diff + ξ(t)
```

| Symbol | Meaning |
|--------|---------|
| `w ∈ [0,1]` | Normalised filament state |
| `η₀` | Ion hopping rate prefactor |
| `V₀` | Characteristic hopping voltage |
| `f(w) = 1−w` (SET) / `w` (RESET) | Growth-limiting factor |
| `τ_diff` | Diffusion time constant (controls volatility) |
| `ξ(t)` | Gaussian filament noise ∝ √dt |

Conductance follows a nonlinear mapping matching ECM/VCM measurement data:

```
G = G_off + (G_on − G_off) · w²
```

**Volatile behaviour** (HC, τ=50 ms): weights decay during quiescent periods, providing short-term memory that naturally fades — correct physics confirmed in simulation.  
**Non-volatile** (PFC, τ=10⁶ s): weights persist permanently, storing task rules across all trials.

---

## Learning Rule: Online STDP

Spike-timing-dependent plasticity implemented as eligibility traces on each crossbar:

```
LTP  (post fires):  Δw +=  A₊ · x_pre   (outer product)
LTD  (pre  fires):  Δw −=  A₋ · x_post  (outer product)
```

Traces are **clamped to [0, 1]** to prevent runaway LTD at high firing rates.  
Diffusion is applied **only during quiescent periods** (no input AND no output spikes), making the learning rate biologically consistent: SET pulses during spiking overcome diffusion.

---

## Neuromodulation

| Signal | Source | Effect |
|--------|--------|--------|
| **Dopamine** | OFC TD-error | Scales all module gains; phasic burst on reward |
| **Acetylcholine (ACh)** | Novelty detection | Boosts HC encoding gain on unfamiliar stimuli |
| **DMN/PCC sync** | Slow oscillator (0.1 Hz) | Gates HC→PFC consolidation pulses |
| **TD-error δ** | `δ = r + γV(s') − V(s)` | Modulates OFC conductance updates |

---

## Step-by-Step Simulation Pipeline

### 1 · Build the System

```python
from modules import HCModule, PFCModule, OFCModule, ECModule
from gate_control import GateController
from synthesis import SpikeGenerator

hc   = HCModule()    # volatile,     τ=50 ms
pfc  = PFCModule()   # non-volatile, τ=∞
ofc  = OFCModule()   # semi-volatile, τ=500 ms
ec   = ECModule()    # fixed oscillatory grid
ctrl = GateController()
sg   = SpikeGenerator(n_neurons=32, dt=1e-4)
```

### 2 · Generate Synthetic Spike Data

The `SpikeGenerator` produces biologically-plausible spike trains:

```
Pattern 0  "Cat"  →  neurons  0–15 fire at 35 Hz  (theta-modulated)
Pattern 1  "Dog"  →  neurons 16–31 fire at 35 Hz
Background →  all neurons at 3 Hz Poisson
```

Oscillatory modulations applied:
- **Theta** (8 Hz): gates HC input windows
- **Gamma** (40 Hz): paces PFC output
- **SWR** (150 Hz): bursts during HC consolidation
- **Grid** (4 Hz): drives EC state-space oscillations

### 3 · Delayed Match-to-Sample (DMS) Training

Each trial (250 ms total):

```
│← 100 ms →│← 100 ms →│← 50 ms →│← — ms →│
│  SAMPLE   │   DELAY   │  TEST    │  ITI   │
│ Cat/Dog   │ (blank)   │ Cat/Dog  │        │
```

- **Sample**: pattern presented → HC encodes → STDP trains PFC W_in
- **Delay**: HC volatile weights decay (correct physics!); PFC holds working memory via non-volatile W_rec
- **Test**: test stimulus presented → decoder reads PFC activity → predict Cat or Dog
- **ITI**: inter-trial interval; neuromodulation returns to baseline

The trainer runs all phases via a single coordinated call:

```python
trainer = STDPTrainer(hc, pfc, ofc, ec, ctrl, sg)
data = trainer.train_dms(n_steps=50_000)   # 5 s simulation
```

### 4 · Gate Controller Orchestration

Each time step:

1. **EC** generates grid-cell coordinates (spatial state-space)
2. **DMN sync** signal gates HC→PFC consolidation
3. **HC** processes input with SWR/theta modulation
4. **PFC** receives input + weak HC signal (0.02×), updates working memory trace
5. **OFC** computes value estimate and TD-error δ
6. **Dopamine** updated from δ; ACh updated from novelty

### 5 · Fit the Decoder

After training, a **ridge-regression readout** is fitted on labeled timesteps (sample + test phases only — delay/ITI excluded to avoid class-imbalance bias):

```python
decoder = Decoder(n_pfc=32, n_hc=64, n_classes=2)
decoder.fit(pfc_activity[labeled], hc_activity[labeled], labels[labeled])
```

PFC representation after training:

| Phase | PFC[0:16] (Cat neurons) | PFC[16:32] (Dog neurons) |
|-------|------------------------|--------------------------|
| Cat   | **0.024** (high)       | 0.005 (low)              |
| Dog   | 0.004 (low)            | **0.025** (high)         |

### 6 · Evaluate

```python
eval_result = decoder.evaluate_dms(data)
print(f"Accuracy: {eval_result['accuracy']:.0%}")   # → 100% on 10 trials
```

---

## Results

| Metric | Value |
|--------|-------|
| Simulation time | 5.0 s (50,000 steps at dt=0.1 ms) |
| DMS trials | 10 |
| Decoder accuracy | **100%** |
| HC replay post-training | 0 activity — volatile τ=50 ms correctly decays |
| PFC Cat/Dog separation | 0.024 vs 0.005 (first half) |

The HC replay showing **zero** activity after training is **physically correct**: volatile memristors with τ=50 ms cannot hold patterns across the seconds-long gap between training and replay evaluation. This matches biological observation — hippocampal replay requires active reactivation (sharp-wave ripples during sleep/rest), not passive retention.

---

## Installation & Usage

```bash
git clone https://github.com/likeyfung/memristive-neuromorphic-sim
cd memristive-neuromorphic-sim
pip install -r requirements.txt
python main.py
```

Output: `simulation_results.png` — a 4-row summary figure showing:
- HC, PFC, OFC spike rasters with DMS phase shading (Sample/Delay/Test)
- TD-error δ over time (reward/punishment episodes)
- EC 4×4 grid-cell map
- Per-trial accuracy and running accuracy curve

---

## File Structure

```
simulation/
├── config.py                   All physical & network parameters (SI units)
├── devices/
│   └── memristor_array.py      Vectorised ion-diffusion ODE crossbar (numpy)
├── modules/
│   ├── base_module.py          LIF neuron layer + STDP skeleton
│   ├── hc_module.py            Volatile reservoir + SWR/theta oscillations
│   ├── pfc_module.py           Non-volatile working memory + gamma pacing
│   ├── ofc_module.py           Semi-volatile value/reward + TD learning
│   └── ec_module.py            Fixed oscillatory grid-cell state space
├── synthesis/
│   └── spike_generator.py      Poisson / theta / SWR / DMS task schedule
├── gate_control/
│   └── controller.py           DMN/PCC sync · dopamine · ACh · TD-error
├── training/
│   └── stdp_trainer.py         Self-supervised DMS training loop
├── evaluation/
│   └── decoder.py              Ridge-regression readout + accuracy metrics
├── main.py                     Full pipeline + plotting
└── requirements.txt
```

---

## Key Design Decisions

**Why volatile diffusion only during quiescence?**  
Biologically, ion SET pulses during spiking overcome diffusive RESET. If diffusion is applied on every step regardless, STDP cannot accumulate — weights decay 60× faster than they are built. The quiescent gate ensures physically consistent plasticity.

**Why clamp STDP traces to [0, 1]?**  
At 500 Hz firing rates, unclamped traces reach values of ~10, causing LTD to wipe clean any stored pattern within one trial. Clamping models the saturation of biological calcium-based STDP cascades.

**Why initialise PFC W_rec near zero?**  
Random W_rec at w≈0.03 drives 22 mV pulses between neuron populations — enough to collapse Cat/Dog selectivity in one recurrent step. Starting W_rec near G_off lets STDP build task-specific connectivity from scratch without the random cross-talk.

---

## Comparison with Spaun / Neural Engineering Framework (NEF)

This simulation is often confused with cognitive brain models. The table below clarifies where it sits relative to the Spaun model (Eliasmith et al., 2012) and the Neural Engineering Framework (Eliasmith & Anderson, 2003) that underlies it.

| Dimension | NEF / Spaun | This simulation |
|-----------|-------------|-----------------|
| **Goal** | Model what computations the brain performs and how spiking neurons implement them | Model what physical memristor devices actually do when wired as a crossbar |
| **Level** | Functional / cognitive (top-down + bottom-up hybrid) | Device physics (bottom-up only) |
| **Representation** | High-dimensional semantic pointers — vectors that compress symbolic concepts (e.g. `BLUE ⊛ SQUARE`) | Raw conductance states `w ∈ [0,1]` and spike rasters — no symbolic structure |
| **Memory mechanism** | Gated integrator networks with feedback loops; weights computed analytically via decoders | Memory IS the device physics: non-volatile τ=∞ retains, volatile τ=50 ms forgets — no gating needed |
| **Connection weights** | Derived analytically from neural tuning curves (encoders/decoders) so that the population computes a target function | Physical conductances set by ion-diffusion ODE + STDP; no analytical derivation |
| **Learning** | Weights pre-computed offline or via supervised learning then converted to spiking form; some online adaptive BG | Online STDP directly modifying memristor filament states in real time |
| **Action selection / control** | Cortico-basal ganglia-thalamic loop implemented in spiking neurons (winner-take-all via BG inhibitory outputs) | Software gate controller (dopamine, ACh, DMN sync signals) — not implemented in neurons |
| **Task scope** | 8–12 cognitive tasks: digit recognition, list memory, counting, question answering, fluid induction, motor control | Single DMS task used only as a physics verification check |
| **Scale** | 2.5–6.6 million neurons | 128 LIF neurons total across all four crossbars |
| **Decoder** | Part of the neural circuit (NEF decoders weighted into connection matrices) | External ridge regression fitted after training — not part of the circuit |
| **Biological claim** | Claims to reproduce behavioural and neurological data observed in human participants | Claims only that device physics (τ_diff) matches biological retention timescales; makes no behavioural claims |

### What this simulation shares with NEF/Spaun

- **LIF neurons**: both use Leaky Integrate-and-Fire dynamics
- **STDP**: both incorporate spike-timing-dependent plasticity (Spaun uses it in the adaptive basal ganglia component)
- **Modular structure**: both separate memory, action/control, and sensory encoding into distinct modules
- **DMS task**: Spaun also performs delayed match-to-sample as one of its working memory benchmarks — but via semantic pointer binding in a gated integrator, not via memristor retention physics

### The key conceptual difference

In Spaun, **memory is a software construct** — a gated recurrent attractor network whose weights are analytically derived so the population holds a semantic pointer stable over time. The system can forget because a gate signal is removed.

In this simulation, **memory is a material property** — the non-volatile PFC crossbar holds a pattern because ions are physically locked in place (τ=10⁶ s), and the volatile HC crossbar forgets because ions physically diffuse back (τ=50 ms). No gate signal is needed; the physics does it automatically.

---

## References

1. Portner et al. (2025). Actor–critic networks with analogue memristors. *Nature Machine Intelligence*.
2. Hong & Lieber (2019). Novel electrode technologies for neural recordings. *Nature Reviews Neuroscience*.
3. Lewerenz et al. (2024). Versatile nanoscale three-terminal memristive switch. *ACS Nano*.
4. Midya et al. (2025). Artificial transneurons emulate neuronal activity. *Nature Communications*.
5. Zhao et al. (2023). Tracking neural activity from the same cells during the entire adult life of mice. *Nature Neuroscience*.
6. Fu et al. (2017). Highly scalable multichannel mesh electronics. *PNAS*.
7. Liu et al. (2022). Decoding cognition from spontaneous neural activity. *Nature Reviews Neuroscience*.
