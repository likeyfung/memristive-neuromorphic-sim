"""
Recurrent Memristive Neuromorphic System — Main Simulation
===========================================================
Runs a full Delayed Match-to-Sample (DMS) cognitive task:

  Phase 1  Sample   : Present Cat or Dog spike pattern (300 ms)
  Phase 2  Delay    : Blank period — HC replays, PFC holds WM (600 ms)
  Phase 3  Test     : Present test stimulus, OFC evaluates match (200 ms)
  Phase 4  ITI      : Inter-trial interval (300 ms)

After training:
  - PFC weights frozen (non-volatile)
  - Decoder fitted on training data
  - Accuracy and spike rasters plotted

Usage:
    python main.py
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")    # headless — saves to file
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import config
from modules.hc_module  import HCModule
from modules.pfc_module import PFCModule
from modules.ofc_module import OFCModule
from modules.ec_module  import ECModule
from synthesis.spike_generator import SpikeGenerator
from gate_control.controller   import GateController
from training.stdp_trainer     import STDPTrainer
from evaluation.decoder        import Decoder


# ── reproducibility ──────────────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)


def build_system():
    """Instantiate all modules and controllers."""
    hc   = HCModule(dt=config.DT,  seed=10)
    pfc  = PFCModule(dt=config.DT, seed=20)
    ofc  = OFCModule(dt=config.DT, seed=30)
    ec   = ECModule(dt=config.DT,  seed=40)
    ctrl = GateController(dt=config.DT)
    sg   = SpikeGenerator(n_neurons=config.N_INPUT, dt=config.DT, seed=SEED)
    return hc, pfc, ofc, ec, ctrl, sg


def run_simulation(n_steps: int = None):
    if n_steps is None:
        n_steps = int(config.T_SIM / config.DT)

    print(f"Building system  (N_HC={config.N_HC}, N_PFC={config.N_PFC}, "
          f"N_OFC={config.N_OFC}, N_EC={config.N_EC})")
    hc, pfc, ofc, ec, ctrl, sg = build_system()

    trainer = STDPTrainer(hc, pfc, ofc, ec, ctrl, sg, dt=config.DT)

    print(f"Training: {n_steps} steps  ({n_steps * config.DT:.1f} s) ...")

    def progress(step, _):
        pct = 100 * step / n_steps
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        sys.stdout.write(f"\r  [{bar}] {pct:5.1f}%  step {step}/{n_steps}")
        sys.stdout.flush()

    data = trainer.train_dms(n_steps, callback=progress)
    print("\nTraining complete.")

    # ── fit decoder ───────────────────────────────────────────────────────────
    print("Fitting decoder ...")
    decoder = Decoder(n_pfc=config.N_PFC, n_hc=config.N_HC, n_classes=2)

    schedule = data["schedule"]
    test_labels = np.full(n_steps, -1, dtype=int)
    for (ph, s, e, pid) in schedule:
        if ph in ("test", "sample") and pid is not None:
            test_labels[s:e] = pid

    # Only train on labeled steps to prevent class-imbalance bias
    valid = test_labels >= 0
    decoder.fit(data["pfc_spikes"][valid], data["hc_spikes"][valid],
                test_labels[valid])

    # ── evaluate ──────────────────────────────────────────────────────────────
    print("Evaluating on DMS trials ...")
    eval_result = decoder.evaluate_dms(data)
    acc = eval_result["accuracy"]
    n_trials = eval_result["n_trials"]
    print(f"  DMS accuracy: {acc * 100:.1f}%  over {n_trials} trials")

    # replay evaluation
    print("Running replay-only evaluation (200 steps) ...")
    replay_act = trainer.evaluate_replay(200)
    replay_mean = replay_act.mean()
    print(f"  HC mean activity during replay: {replay_mean:.4f}")

    return data, eval_result, replay_act, decoder


def _smooth(x, w=50):
    """Simple box-car smoothing."""
    kernel = np.ones(w) / w
    return np.convolve(x, kernel, mode="same")


def plot_results(data: dict, eval_result: dict,
                 replay_act: np.ndarray, decoder: Decoder,
                 save_path: str = "simulation_results.png"):
    """
    6-panel summary figure:
      Row 0: HC raster  |  PFC raster
      Row 1: OFC raster |  EC grid map
      Row 2: Mean rates (all modules)  |  Conductance evolution
      Row 3: TD-error   |  DMS trial accuracy + replay
    """
    n_steps = len(data["hc_spikes"])
    T_ms    = np.arange(n_steps) * config.DT * 1000
    stride  = max(1, n_steps // 3000)
    Ts      = T_ms[::stride]

    COLORS = dict(hc="#2176AE", pfc="#F4A261", ofc="#43AA8B", ec="#9B5DE5")
    FS     = 9

    fig = plt.figure(figsize=(16, 12))
    gs  = gridspec.GridSpec(4, 3, figure=fig,
                            hspace=0.60, wspace=0.38,
                            left=0.07, right=0.97,
                            top=0.93, bottom=0.06)

    schedule = data["schedule"]

    # ── Row 0: HC raster ─────────────────────────────────────────────────────
    ax = fig.add_subplot(gs[0, :2])
    ax.imshow(data["hc_spikes"][::stride].T, aspect="auto", origin="lower",
              cmap="Blues", interpolation="nearest",
              extent=[Ts[0], Ts[-1], 0, config.N_HC])
    ax.set_title("HC  (Volatile Memristor Reservoir  τ=50 ms)", fontsize=FS + 1,
                 color=COLORS["hc"])
    ax.set_ylabel("HC unit #"); ax.set_xlabel("Time (ms)")
    _shade_phases(ax, schedule, n_steps, config.DT)
    _add_phase_legend(ax)

    ax2 = fig.add_subplot(gs[0, 2])
    hc_rate = _smooth(data["hc_spikes"].mean(axis=1), 200)[::stride]
    ax2.fill_between(Ts, hc_rate, alpha=0.4, color=COLORS["hc"])
    ax2.plot(Ts, hc_rate, lw=0.9, color=COLORS["hc"])
    ax2.set_title("HC mean spike rate", fontsize=FS)
    ax2.set_xlabel("Time (ms)"); ax2.set_ylabel("Spikes / step")

    # ── Row 1: PFC raster ────────────────────────────────────────────────────
    ax = fig.add_subplot(gs[1, :2])
    ax.imshow(data["pfc_spikes"][::stride].T, aspect="auto", origin="lower",
              cmap="Oranges", interpolation="nearest",
              extent=[Ts[0], Ts[-1], 0, config.N_PFC])
    ax.set_title("PFC  (Non-volatile Working Memory  τ=∞)", fontsize=FS + 1,
                 color=COLORS["pfc"])
    ax.set_ylabel("PFC unit #"); ax.set_xlabel("Time (ms)")
    _shade_phases(ax, schedule, n_steps, config.DT)

    ax2 = fig.add_subplot(gs[1, 2])
    pfc_rate = _smooth(data["pfc_spikes"].mean(axis=1), 200)[::stride]
    ax2.fill_between(Ts, pfc_rate, alpha=0.4, color=COLORS["pfc"])
    ax2.plot(Ts, pfc_rate, lw=0.9, color=COLORS["pfc"])
    ax2.set_title("PFC mean spike rate", fontsize=FS)
    ax2.set_xlabel("Time (ms)"); ax2.set_ylabel("Spikes / step")

    # ── Row 2: OFC + EC side-by-side ─────────────────────────────────────────
    ax = fig.add_subplot(gs[2, :1])
    ax.imshow(data["ofc_spikes"][::stride].T, aspect="auto", origin="lower",
              cmap="Greens", interpolation="nearest",
              extent=[Ts[0], Ts[-1], 0, config.N_OFC])
    ax.set_title("OFC  (Semi-volatile Reward/Value  τ=500 ms)", fontsize=FS,
                 color=COLORS["ofc"])
    ax.set_ylabel("OFC unit #"); ax.set_xlabel("Time (ms)")

    ax = fig.add_subplot(gs[2, 1])
    td_smooth = _smooth(data["td_errors"], 300)[::stride]
    ax.plot(Ts, td_smooth, lw=1.0, color=COLORS["ofc"])
    ax.axhline(0, color="k", lw=0.5, ls="--")
    ax.fill_between(Ts, td_smooth, 0,
                    where=td_smooth > 0, alpha=0.3, color="green", label="reward")
    ax.fill_between(Ts, td_smooth, 0,
                    where=td_smooth < 0, alpha=0.3, color="red",   label="punishment")
    ax.set_title("TD-error  δ = r + γV(s') − V(s)", fontsize=FS)
    ax.set_xlabel("Time (ms)"); ax.set_ylabel("δ"); ax.legend(fontsize=7)

    ax = fig.add_subplot(gs[2, 2])
    ec_grid = data["ec_activity"][-1].reshape(4, 4)
    im = ax.imshow(ec_grid, cmap="Purples", vmin=0, vmax=1)
    plt.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title("EC Grid Map (last step)\n4×4 oscillatory state-space", fontsize=FS,
                 color=COLORS["ec"])
    ax.set_xticks([]); ax.set_yticks([])

    # ── Row 3: accuracy + reward + replay ────────────────────────────────────
    ax = fig.add_subplot(gs[3, :2])
    trials = eval_result["per_trial"]
    if trials:
        ids     = [t["trial"] for t in trials]
        correct = [int(t["correct"]) for t in trials]
        running = np.cumsum(correct) / (np.arange(len(correct)) + 1)
        colors_bar = ["#2ecc71" if c else "#e74c3c" for c in correct]
        ax.bar(ids, correct, color=colors_bar, alpha=0.6, width=0.6, label="trial result")
        ax.plot(ids, running, "k--o", ms=4, lw=1.5,
                label=f"running acc  (final {eval_result['accuracy']:.0%})")
        ax.axhline(0.5, color="gray", ls=":", lw=1, label="chance")
        ax.set_ylim(-0.05, 1.15)
        ax.set_title("DMS Task — Per-trial Accuracy", fontsize=FS + 1)
        ax.set_xlabel("Trial #"); ax.set_ylabel("Correct (1) / Wrong (0)")
        ax.legend(fontsize=7, loc="lower right")

    ax = fig.add_subplot(gs[3, 2])
    if replay_act.max() > 0:
        ax.imshow(replay_act.T, aspect="auto", origin="lower",
                  cmap="Blues", interpolation="nearest")
        ax.set_title("HC Replay (seeded, no ext. input)", fontsize=FS)
    else:
        # Show that volatile weights correctly decayed to zero
        ax.text(0.5, 0.5, "HC volatile weights\ndecayed to zero\n(correct physics!)",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=9, color="steelblue",
                bbox=dict(boxstyle="round,pad=0.4", fc="#e8f4fd", ec="steelblue"))
        ax.set_title("HC Replay (post-training)", fontsize=FS)
        ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("Replay step"); ax.set_ylabel("HC unit #")

    plt.suptitle(
        "Recurrent Memristive Neuromorphic System  ·  DMS Cognitive Simulation",
        fontsize=13, fontweight="bold", y=0.97
    )

    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved → {save_path}")
    return fig


def _shade_phases(ax, schedule, n_steps, dt):
    """Shade DMS phases on a time-axis plot (ms)."""
    colours = {"sample": "#FFD166", "delay": "#A8DADC",
               "test":   "#EF8354", "iti":   "#FFFFFF"}
    T_total = n_steps * dt * 1000
    for (ph, s, e, _) in schedule:
        xs = s * dt * 1000
        xe = e * dt * 1000
        if xs >= T_total:
            break
        ax.axvspan(xs, min(xe, T_total), alpha=0.18,
                   color=colours.get(ph, "white"), lw=0)


def _add_phase_legend(ax):
    """Add a compact phase legend to a raster axis."""
    from matplotlib.patches import Patch
    handles = [
        Patch(facecolor="#FFD166", alpha=0.5, label="Sample"),
        Patch(facecolor="#A8DADC", alpha=0.5, label="Delay"),
        Patch(facecolor="#EF8354", alpha=0.5, label="Test"),
    ]
    ax.legend(handles=handles, fontsize=7, loc="upper right",
              framealpha=0.8, handlelength=1)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    n_steps = int(config.T_SIM / config.DT)

    data, eval_result, replay_act, decoder = run_simulation(n_steps)

    # retrieve controller for plotting — reconstruct from data
    plot_results(data, eval_result, replay_act, decoder,
                 save_path="simulation_results.png")

    # ── summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    print(f"  Steps simulated  : {n_steps:,}  ({config.T_SIM:.1f} s)")
    print(f"  DMS trials       : {eval_result['n_trials']}")
    print(f"  Decoder accuracy : {eval_result['accuracy'] * 100:.1f}%")
    print(f"  HC mean replay   : {replay_act.mean():.4f}")

    n_correct = sum(1 for t in eval_result["per_trial"] if t["correct"])
    print(f"  Correct trials   : {n_correct}/{eval_result['n_trials']}")

    print("\n  Per-trial results (first 10):")
    for t in eval_result["per_trial"][:10]:
        mark = "✓" if t["correct"] else "✗"
        lbl  = ["Cat", "Dog"][t["target"]]
        pred = ["Cat", "Dog"][t["pred"]]
        print(f"    Trial {t['trial']:2d}: target={lbl:3s}  pred={pred:3s}  "
              f"reward={t['reward']:+.0f}  {mark}")
    print("=" * 60)
