# Wave Cognition v7

Preserved revision: phase-addressed event/wave memory with trained reciprocal couplers.

Open `report.html` for the illustrated report or `Wave_Cognition_v7.docx` for Word. Read `CIRCUIT_SPEC.md` for the complete behavioral block specification and proposed transistor implementation. No measured ASIC energy or power is claimed. The transformer-on-ASIC case is unimplemented and explicitly marked as such.

## Replay without overwriting this revision

Copy this directory to a fresh numbered revision before running scripts that regenerate results. Every script resolves its own revision directory from its file path. Do not change the archived v6 model or root src/model.js.

Tested computation environment: Python 3.11, PyTorch 2.14.0, NumPy, Matplotlib, ngspice 46; Apple M4 Pro host. This session used an isolated `/tmp/wave-v7-env` environment with PyTorch, not a global install. Training uses CPU only and one PyTorch thread. Transistor sizing requires your Cadence installation and foundry PDK; neither is bundled.

From a copied revision directory, using a Python environment with the dependencies:

```sh
python src/bench.py
python src/coupling_controls.py
python src/extended.py
python src/diagnostics.py
python src/circuit_verify.py
python src/block_library.py
python src/figures.py
```

Run sequentially for timing reproducibility. `bench.py` trains 18 models and takes several minutes, with 256-node matrix-exponential differentiation dominating runtime. Repeated timing will vary with host scheduling. Circuit scripts require ngspice on PATH. `src/report.py` uses python-docx and renders the saved metrics to Word/HTML; document rendering for visual QA was performed with the Codex bundled document runtime.

## Evidence files

- `results/scores.json`: clean performance, frozen ablations, training logs and unoptimized full-simulator timings.
- `results/extended.json`: exact compact digital equivalence, paired-noise retention, compact CPU timing and lower-bound symbolic read.
- `results/coupling-controls.json`: strength-only and phase-only training at 64 nodes.
- `results/diagnostics.json`: counterfactual query, phase jitter, dropped emissions and damped-unitarity error.
- `results/timing.json`: warmed-up transformer CPU measurements and tensor sizes.
- `results/circuit-verification.json`: 16 learned 64-node read-phase ngspice comparisons.
- `results/block-check.json`: hierarchical neuron/local-wave feedback test.
- `results/*.pt`: frozen test episodes, checkpoints and compiled coupler operators.
- `circuit/*.cir`, `circuit/*.txt`: executable behavioral circuits and actual traces.
- `figures/`: seven SVG/PNG figures with captions.
- `results/manifest.json`: hashes of source and evidence files.

The trained task uses ideal coherent write packets and a signed current readout. It does not instantiate every synapse and dendrite across the array. The single-neuron circuit test and the read-phase array test validate different parts of the design. The algorithm is a synthetic associative-memory demonstration; it is not a physiological recording, LLM or general cognitive model.

The zero temporal-RAM ASIC proposal still needs analog state, configuration storage, reference distribution, control and I/O. The compact digital implementation uses only 32/64 bytes of dynamic state at 8/16 keys; a symbolic solution needs 8/16 payload bits. Hardware comparisons must include these strong baselines.
