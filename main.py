"""
Recurrent Memristive Neuromorphic System — Main Simulation
===========================================================

Demonstrates the system as a cognitive model via three key additions:

  Change 1 — NEF population coding
    Input neurons fire according to tuning curves (encoder · semantic_pointer),
    not hardcoded Cat/Dog neuron assignments. Any new concept is added by
    registering a new semantic pointer; no circuit changes needed.

  Change 2 — Spiking Basal Ganglia
    Action selection (ENCODE / MAINTAIN / COMPARE / RESET) is performed by a
    spiking strD1 → GPi → Thalamus circuit driven by neural utility signals,
    not Python if/else logic.

  Change 3 — Second task (TOJ)
    After DMS training, the system runs Temporal Order Judgment on the same
    circuit with no architecture changes, demonstrating generalisation.

Usage:
    python main.py
"""

import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch

import config
from modules.hc_module  import HCModule
from modules.pfc_module import PFCModule
from modules.ofc_module import OFCModule
from modules.ec_module  import ECModule
from synthesis.spike_generator import SpikeGenerator
from gate_control.controller   import GateController
from training.stdp_trainer     import STDPTrainer
from evaluation.decoder        import Decoder

SEED = 42
np.random.seed(SEED)

COLORS = dict(hc="#2176AE", pfc="#F4A261", ofc="#43AA8B", ec="#9B5DE5",
              encode="#4CAF50", maintain="#2196F3",
              compare="#FF9800", reset="#9E9E9E")
ACTION_COLORS = [COLORS["encode"], COLORS["maintain"],
                 COLORS["compare"], COLORS["reset"]]
ACTION_NAMES  = ["ENCODE", "MAINTAIN", "COMPARE", "RESET"]


def build_system():
    hc   = HCModule(dt=config.DT,  seed=10)
    pfc  = PFCModule(dt=config.DT, seed=20)
    ofc  = OFCModule(dt=config.DT, seed=30)
    ec   = ECModule(dt=config.DT,  seed=40)
    ctrl = GateController(dt=config.DT)
    sg   = SpikeGenerator(n_neurons=config.N_INPUT, dt=config.DT, seed=SEED)
    return hc, pfc, ofc, ec, ctrl, sg


def _progress(label):
    def callback(step, _):
        n_steps = step   # approximation; used only for display
        bar = "█" * min(20, step // 2500) + "░" * max(0, 20 - step // 2500)
        sys.stdout.write(f"\r  [{bar}] {label}  step {step:,}")
        sys.stdout.flush()
    return callback


def run_simulation(n_steps: int | None = None):
    if n_steps is None:
        n_steps = int(config.T_SIM / config.DT)

    print(f"Building system  (N_HC={config.N_HC}, N_PFC={config.N_PFC}, "
          f"N_OFC={config.N_OFC}, N_EC={config.N_EC})")
    hc, pfc, ofc, ec, ctrl, sg = build_system()
    trainer = STDPTrainer(hc, pfc, ofc, ec, ctrl, sg, dt=config.DT)

    # ── DMS training ───────────────────────────────────────────────────────────
    print(f"\nPhase 1 — DMS training: {n_steps:,} steps ({n_steps * config.DT:.1f} s)")
    dms_data = trainer.train_dms(n_steps, callback=_progress("DMS"))
    print("\nDMS training complete.")

    # ── fit DMS decoder ────────────────────────────────────────────────────────
    print("Fitting DMS decoder ...")
    decoder_dms = Decoder(n_pfc=config.N_PFC, n_hc=config.N_HC, n_classes=2)

    schedule    = dms_data["schedule"]
    test_labels = np.full(n_steps, -1, dtype=int)
    for (ph, s, e, pid) in schedule:
        if ph in ("test", "sample") and pid is not None:
            test_labels[s:e] = pid
    valid = test_labels >= 0
    decoder_dms.fit(dms_data["pfc_spikes"][valid],
                    dms_data["hc_spikes"][valid],
                    test_labels[valid])

    dms_eval = decoder_dms.evaluate_dms(dms_data)
    print(f"  DMS accuracy: {dms_eval['accuracy'] * 100:.1f}%  "
          f"over {dms_eval['n_trials']} trials")

    # ── HC replay evaluation ───────────────────────────────────────────────────
    print("Running HC replay evaluation ...")
    replay_act = trainer.evaluate_replay(200)
    print(f"  HC mean activity (replay): {replay_act.mean():.4f}")

    # ── TOJ training on the same system ────────────────────────────────────────
    n_toj = n_steps // 2
    print(f"\nPhase 2 — TOJ training: {n_toj:,} steps ({n_toj * config.DT:.1f} s)")
    toj_data = trainer.train_toj(n_toj, callback=_progress("TOJ"))
    print("\nTOJ training complete.")

    # ── fit TOJ decoder on blank-window activity ───────────────────────────────
    print("Fitting TOJ decoder ...")
    decoder_toj = Decoder(n_pfc=config.N_PFC, n_hc=config.N_HC, n_classes=2)

    toj_sched  = toj_data["schedule"]
    toj_labels_arr = toj_data["toj_labels"]
    blank_mask = toj_labels_arr >= 0
    if blank_mask.sum() > 0:
        decoder_toj.fit(toj_data["pfc_spikes"][blank_mask],
                        toj_data["hc_spikes"][blank_mask],
                        toj_labels_arr[blank_mask])

    toj_eval = decoder_toj.evaluate_toj(toj_data)
    print(f"  TOJ accuracy: {toj_eval['accuracy'] * 100:.1f}%  "
          f"over {toj_eval['n_trials']} trials")

    return dms_data, dms_eval, toj_data, toj_eval, replay_act, decoder_dms


# ── plotting helpers ──────────────────────────────────────────────────────────

def _smooth(x, w=50):
    return np.convolve(x, np.ones(w) / w, mode="same")


def _shade_phases(ax, schedule, n_steps, dt):
    colours = {"sample": "#FFD166", "delay": "#A8DADC",
               "test":   "#EF8354", "iti":   "#FFFFFF"}
    T_total = n_steps * dt * 1000
    for (ph, s, e, *_) in schedule:
        xs = s * dt * 1000
        xe = e * dt * 1000
        if xs >= T_total:
            break
        ax.axvspan(xs, min(xe, T_total), alpha=0.18,
                   color=colours.get(ph, "white"), lw=0)


def _shade_toj(ax, schedule, n_steps, dt):
    colours = {"stim_a": "#FFD166", "stim_b": "#2176AE",
               "blank":  "#A8DADC", "iti":    "#FFFFFF"}
    T_total = n_steps * dt * 1000
    for (ph, s, e, *_) in schedule:
        xs = s * dt * 1000
        xe = e * dt * 1000
        if xs >= T_total:
            break
        ax.axvspan(xs, min(xe, T_total), alpha=0.25,
                   color=colours.get(ph, "white"), lw=0)


def _phase_legend(ax):
    handles = [Patch(facecolor="#FFD166", alpha=0.5, label="Sample"),
               Patch(facecolor="#A8DADC", alpha=0.5, label="Delay"),
               Patch(facecolor="#EF8354", alpha=0.5, label="Test")]
    ax.legend(handles=handles, fontsize=7, loc="upper right",
              framealpha=0.8, handlelength=1)


def _toj_legend(ax):
    handles = [Patch(facecolor="#FFD166", alpha=0.6, label="Stim A"),
               Patch(facecolor="#2176AE", alpha=0.4, label="Stim B"),
               Patch(facecolor="#A8DADC", alpha=0.6, label="Blank")]
    ax.legend(handles=handles, fontsize=7, loc="upper right",
              framealpha=0.8, handlelength=1)


# ── main figure ───────────────────────────────────────────────────────────────

def plot_results(dms_data, dms_eval, toj_data, toj_eval, replay_act,
                 save_path="simulation_results.png"):
    """
    5-row summary figure:
      Row 0: HC raster (DMS)  |  PFC raster (DMS)
      Row 1: OFC raster       |  TD-error  |  EC grid map
      Row 2: BG action selection (DMS) — spiking BG vs phase ground truth
      Row 3: DMS per-trial accuracy  |  HC replay
      Row 4: TOJ HC raster   |  TOJ accuracy
    """
    n_steps = len(dms_data["hc_spikes"])
    T_ms    = np.arange(n_steps) * config.DT * 1000
    stride  = max(1, n_steps // 3000)
    Ts      = T_ms[::stride]

    FS = 9

    fig = plt.figure(figsize=(17, 15))
    gs  = gridspec.GridSpec(5, 3, figure=fig,
                            hspace=0.65, wspace=0.38,
                            left=0.07, right=0.97,
                            top=0.94, bottom=0.05)

    schedule = dms_data["schedule"]

    # ── Row 0: HC raster + PFC raster ────────────────────────────────────────
    ax = fig.add_subplot(gs[0, :2])
    ax.imshow(dms_data["hc_spikes"][::stride].T, aspect="auto", origin="lower",
              cmap="Blues", interpolation="nearest",
              extent=[Ts[0], Ts[-1], 0, config.N_HC])
    ax.set_title("HC  (Volatile τ=50 ms)  ·  NEF-encoded input", fontsize=FS + 1,
                 color=COLORS["hc"])
    ax.set_ylabel("HC unit #")
    _shade_phases(ax, schedule, n_steps, config.DT)
    _phase_legend(ax)

    ax2 = fig.add_subplot(gs[0, 2])
    hc_rate = _smooth(dms_data["hc_spikes"].mean(axis=1), 200)[::stride]
    ax2.fill_between(Ts, hc_rate, alpha=0.4, color=COLORS["hc"])
    ax2.plot(Ts, hc_rate, lw=0.9, color=COLORS["hc"])
    ax2.set_title("HC mean spike rate", fontsize=FS)
    ax2.set_xlabel("Time (ms)"); ax2.set_ylabel("Spikes/step")

    # ── Row 1: OFC raster + TD-error + EC grid ────────────────────────────────
    ax = fig.add_subplot(gs[1, 0])
    ax.imshow(dms_data["ofc_spikes"][::stride].T, aspect="auto", origin="lower",
              cmap="Greens", interpolation="nearest",
              extent=[Ts[0], Ts[-1], 0, config.N_OFC])
    ax.set_title("OFC  (Semi-volatile τ=500 ms)", fontsize=FS, color=COLORS["ofc"])
    ax.set_ylabel("OFC unit #"); ax.set_xlabel("Time (ms)")

    ax = fig.add_subplot(gs[1, 1])
    td = _smooth(dms_data["td_errors"], 300)[::stride]
    ax.plot(Ts, td, lw=1.0, color=COLORS["ofc"])
    ax.axhline(0, color="k", lw=0.5, ls="--")
    ax.fill_between(Ts, td, 0, where=td > 0, alpha=0.3, color="green", label="reward")
    ax.fill_between(Ts, td, 0, where=td < 0, alpha=0.3, color="red",   label="punish")
    ax.set_title("TD-error  δ = r + γV(s') − V(s)", fontsize=FS)
    ax.set_xlabel("Time (ms)"); ax.set_ylabel("δ"); ax.legend(fontsize=7)

    ax = fig.add_subplot(gs[1, 2])
    ec_grid = dms_data["ec_activity"][-1].reshape(4, 4)
    im = ax.imshow(ec_grid, cmap="Purples", vmin=0, vmax=1)
    plt.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title("EC Grid Map (last step)", fontsize=FS, color=COLORS["ec"])
    ax.set_xticks([]); ax.set_yticks([])

    # ── Row 2: BG action selection vs DMS phase ground truth ─────────────────
    ax = fig.add_subplot(gs[2, :2])
    bg_acts  = dms_data["bg_actions"]
    bg_utils = dms_data["bg_utilities"]

    # Plot utility signals as stacked area (thin lines)
    Ts_bg = T_ms[::stride]
    for i, (name, col) in enumerate(zip(ACTION_NAMES, ACTION_COLORS)):
        u = _smooth(bg_utils[:, i], 200)[::stride]
        ax.plot(Ts_bg, u + i * 0.05, lw=0.8, color=col, alpha=0.7, label=name)

    # Overlay selected action as colored dots
    sel_t   = T_ms[::20]
    sel_act = bg_acts[::20]
    for i, col in enumerate(ACTION_COLORS):
        mask = sel_act == i
        if mask.any():
            ax.scatter(sel_t[mask], np.full(mask.sum(), 0.85 + i * 0.04),
                       s=1.5, color=col, alpha=0.6)

    _shade_phases(ax, schedule, n_steps, config.DT)
    ax.set_title("Spiking BG  ·  utility signals + selected action (dots)",
                 fontsize=FS + 1)
    ax.set_ylabel("Utility")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=7, ncol=4, loc="upper left")

    ax3 = fig.add_subplot(gs[2, 2])
    # Compare BG action vs phase ground truth
    phase_to_gt = {"sample": 0, "delay": 1, "test": 2, "iti": 3}
    gt_actions  = np.full(n_steps, 3, dtype=int)
    for (ph, s, e, *_) in schedule:
        if ph in phase_to_gt:
            gt_actions[s:e] = phase_to_gt[ph]
    # Fraction of steps where BG agrees with ground truth phase
    match = (bg_acts == gt_actions).astype(float)
    ax3.plot(Ts, _smooth(match, 500)[::stride], color="navy", lw=1.2)
    ax3.axhline(0.25, color="gray", ls=":", lw=1, label="chance")
    ax3.set_ylim(0, 1.1)
    ax3.set_title("BG–phase agreement", fontsize=FS)
    ax3.set_xlabel("Time (ms)"); ax3.set_ylabel("Fraction correct")
    ax3.legend(fontsize=7)

    # ── Row 3: DMS accuracy + HC replay ──────────────────────────────────────
    ax = fig.add_subplot(gs[3, :2])
    trials  = dms_eval["per_trial"]
    if trials:
        ids     = [t["trial"] for t in trials]
        correct = [int(t["correct"]) for t in trials]
        running = np.cumsum(correct) / (np.arange(len(correct)) + 1)
        ax.bar(ids, correct,
               color=["#2ecc71" if c else "#e74c3c" for c in correct],
               alpha=0.6, width=0.6)
        ax.plot(ids, running, "k--o", ms=4, lw=1.5,
                label=f"running acc (final {dms_eval['accuracy']:.0%})")
        ax.axhline(0.5, color="gray", ls=":", lw=1, label="chance")
        ax.set_ylim(-0.05, 1.15)
        ax.set_title("DMS — Per-trial Accuracy  (NEF encoding + spiking BG)",
                     fontsize=FS + 1)
        ax.set_xlabel("Trial #"); ax.set_ylabel("Correct (1) / Wrong (0)")
        ax.legend(fontsize=7, loc="lower right")

    ax = fig.add_subplot(gs[3, 2])
    if replay_act.max() > 0:
        ax.imshow(replay_act.T, aspect="auto", origin="lower",
                  cmap="Blues", interpolation="nearest")
        ax.set_title("HC Replay (no ext. input)", fontsize=FS)
    else:
        ax.text(0.5, 0.5, "HC volatile weights\ndecayed to zero\n(correct physics!)",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=9, color="steelblue",
                bbox=dict(boxstyle="round,pad=0.4", fc="#e8f4fd", ec="steelblue"))
        ax.set_title("HC Replay (post-training)", fontsize=FS)
        ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel("Replay step"); ax.set_ylabel("HC unit #")

    # ── Row 4: TOJ — HC raster + accuracy ────────────────────────────────────
    n_toj  = len(toj_data["hc_spikes"])
    T_toj  = np.arange(n_toj) * config.DT * 1000
    str_t  = max(1, n_toj // 3000)
    Ts_toj = T_toj[::str_t]

    ax = fig.add_subplot(gs[4, :2])
    ax.imshow(toj_data["hc_spikes"][::str_t].T, aspect="auto", origin="lower",
              cmap="Blues", interpolation="nearest",
              extent=[Ts_toj[0], Ts_toj[-1], 0, config.N_HC])
    ax.set_title("TOJ — HC raster  (stim_a → stim_b → blank)  "
                 "· same circuit, new task", fontsize=FS + 1,
                 color=COLORS["hc"])
    ax.set_ylabel("HC unit #"); ax.set_xlabel("Time (ms)")
    _shade_toj(ax, toj_data["schedule"], n_toj, config.DT)
    _toj_legend(ax)

    ax = fig.add_subplot(gs[4, 2])
    toj_trials = toj_eval["per_trial"]
    if toj_trials:
        t_ids   = [t["trial"] for t in toj_trials]
        t_corr  = [int(t["correct"]) for t in toj_trials]
        t_run   = np.cumsum(t_corr) / (np.arange(len(t_corr)) + 1)
        ax.bar(t_ids, t_corr,
               color=["#2ecc71" if c else "#e74c3c" for c in t_corr],
               alpha=0.6, width=0.6)
        ax.plot(t_ids, t_run, "k--o", ms=4, lw=1.5,
                label=f"TOJ acc ({toj_eval['accuracy']:.0%})")
        ax.axhline(0.5, color="gray", ls=":", lw=1, label="chance")
        ax.set_ylim(-0.05, 1.15)
        ax.set_title("TOJ — Per-trial Accuracy\n(temporal order of Cat vs Dog)",
                     fontsize=FS)
        ax.set_xlabel("Trial #"); ax.set_ylabel("Correct")
        ax.legend(fontsize=7, loc="lower right")
    else:
        ax.text(0.5, 0.5, "No TOJ trials", ha="center", va="center",
                transform=ax.transAxes, fontsize=9)
        ax.set_title("TOJ Accuracy", fontsize=FS)

    plt.suptitle(
        "Recurrent Memristive Neuromorphic System  ·  Cognitive Model\n"
        "NEF population coding  +  Spiking Basal Ganglia  +  DMS & TOJ tasks",
        fontsize=12, fontweight="bold", y=0.98
    )

    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved → {save_path}")
    return fig


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    n_steps = int(config.T_SIM / config.DT)

    results = run_simulation(n_steps)
    dms_data, dms_eval, toj_data, toj_eval, replay_act, decoder_dms = results

    plot_results(dms_data, dms_eval, toj_data, toj_eval, replay_act,
                 save_path="simulation_results.png")

    print("\n" + "=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    print(f"  DMS steps        : {len(dms_data['hc_spikes']):,}")
    print(f"  TOJ steps        : {len(toj_data['hc_spikes']):,}")
    print(f"  DMS accuracy     : {dms_eval['accuracy'] * 100:.1f}%  "
          f"({dms_eval['n_trials']} trials)")
    print(f"  TOJ accuracy     : {toj_eval['accuracy'] * 100:.1f}%  "
          f"({toj_eval['n_trials']} trials)")
    print(f"  HC mean replay   : {replay_act.mean():.4f}")

    print("\n  DMS per-trial (first 10):")
    for t in dms_eval["per_trial"][:10]:
        mark = "✓" if t["correct"] else "✗"
        lbl  = ["Cat", "Dog"][t["target"]]
        pred = ["Cat", "Dog"][t["pred"]]
        print(f"    Trial {t['trial']:2d}: target={lbl}  pred={pred}  "
              f"reward={t['reward']:+.0f}  {mark}")

    print("\n  TOJ per-trial (first 10):")
    for t in toj_eval["per_trial"][:10]:
        mark  = "✓" if t["correct"] else "✗"
        order = ["Cat→Dog", "Dog→Cat"][t["target"]]
        ppred = ["Cat→Dog", "Dog→Cat"][t["pred"]]
        print(f"    Trial {t['trial']:2d}: order={order}  pred={ppred}  {mark}")
    print("=" * 60)
