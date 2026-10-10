"""Figures for the WWW 2027 correlated-arms paper (PDF for LaTeX and PNG for review).

Usage (from the repo root):
    .venv/bin/python -I experiments/paper_figures.py

Writes research/correlated_arms/figures/fig{1..5}_*.{pdf,png} from saved results only.
Colour by role, fixed across figures: iid = neutral gray, spatial only = orange,
temporal only = aqua, spatiotemporal or certified = blue (first three slots of the
reference categorical palette, documented to pass all-pairs colour-blind checks in
light mode). Aqua is below 3:1 contrast on white, so every aqua series is labelled directly.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KR = ROOT / "research" / "kuairec_graphs" / "results"
ST = ROOT / "research" / "st_toy" / "results"
OUT = ROOT / "research" / "correlated_arms" / "figures"

BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
FAMILY_COLOR = {"iid": GRAY, "spatial only": ORANGE, "temporal only": AQUA, "spatiotemporal": BLUE}

plt.rcParams.update({
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "pdf.fonttype": 42,
    "figure.dpi": 150, "savefig.bbox": "tight",
})


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=220 if ext == "png" else None)
    plt.close(fig)


def fig1_alignment() -> None:
    """Which web graphs encode correlated long-run appeal: real graph against its rewiring."""
    d = pd.read_csv(KR / "alignment_summary_R1_k10.csv")
    real = d[d.null == "real"].set_index("graph")
    rew = d[d.null == "rewired"].set_index("graph")
    real = real[real.isolated < 0.5 * real.nodes]
    order = real.sort_values(["axis", "edge_corr_dc"], ascending=[True, True]).index
    fig, ax = plt.subplots(figsize=(3.4, 3.3))
    y = np.arange(len(order))
    ax.hlines(y, rew.loc[order, "edge_corr_dc"], real.loc[order, "edge_corr_dc"], color=GRID, lw=2)
    ax.scatter(rew.loc[order, "edge_corr_dc"], y, s=22, color=GRAY, zorder=3, label="Rewired null")
    ax.scatter(real.loc[order, "edge_corr_dc"], y, s=22, color=BLUE, zorder=3, label="Real graph")
    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.set_xlabel("Personal-taste correlation of neighbours\n(activity and popularity removed)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=7.5, handletextpad=0.2)
    ax.set_title("Collaborative graphs carry taste", loc="left", color=INK)
    save(fig, "fig1_graph_alignment")


def fig2_pooling_tails() -> None:
    """Uncertified pooling helps the median user but has a heavy tail (Setting A, I-mf)."""
    r = pd.read_csv(KR / "setting_a_runs.csv")
    col = "regret@20000"
    ts = r[r.policy == "ts"].set_index("user")[col]
    rows = [
        ("UCB1", (r.policy == "ucb"), GRAY),
        ("Spectral TS, λ=10", (r.policy == "spectral_ts") & (r.graph == "I-mf") & (r.param.astype(str) == "10.0"), ORANGE),
        ("SP-UCB, no certificate", (r.policy == "sp_ucb") & (r.graph == "I-mf") & (r.param == "none"), ORANGE),
        ("SP-UCB, oracle certificate", (r.policy == "sp_ucb") & (r.graph == "I-mf") & (r.param == "oracle"), BLUE),
    ]
    fig, ax = plt.subplots(figsize=(3.4, 1.9))
    for k, (label, mask, color) in enumerate(rows):
        x = (r[mask].set_index("user")[col] / ts).dropna().to_numpy()
        lo, med, hi = np.quantile(x, [0.1, 0.5, 0.9])
        ax.hlines(k, lo, hi, color=color, lw=2)
        ax.scatter([med], [k], s=26, color=color, zorder=3)
        ax.text(hi * 1.08, k, f"90th pct {hi:.1f}×", va="center", fontsize=7, color=MUTED)
    ax.set_xscale("log")
    ax.axvline(1, color=MUTED, lw=0.8, ls="--")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r_[0] for r_ in rows])
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Regret relative to Thompson sampling (median, 10th–90th pct.)")
    ax.set_title("Uncertified pooling: good median, heavy tail", loc="left", color=INK)
    ax.set_xlim(0.2, 60)
    save(fig, "fig2_pooling_tails")


def fig3_certificates() -> None:
    """Certificates under persistence with bursty exposure (blocks of 25): validity and regret."""
    parts = [pd.read_csv(ST / "coverage_runs_scalar.csv")]
    if (ST / "coverage_runs_plugin.csv").exists():
        parts.append(pd.read_csv(ST / "coverage_runs_plugin.csv"))
    d = pd.concat(parts)
    d = d[(d.batch == 25) & d.policy.isin(["sp_ucb_iid", "sp_ucb_st1", "sp_ucb_st2"])]
    d = d.drop_duplicates(["config", "phi", "seed", "policy"])
    series = [("sp_ucb_iid", "iid certificate", ORANGE, "o"),
              ("sp_ucb_st1", "B1′ (independent shocks)", BLUE, "s"),
              ("sp_ucb_st2", "B1″ (correlated shocks)", AQUA, "^")]
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.1))
    for config, ls in (("independent", "-"), ("correlated", ":")):
        for pol, label, color, marker in series:
            s = d[(d.config == config) & (d.policy == pol)]
            if s.empty:
                continue
            g = s.groupby("phi").agg(viol=("any_violation", "mean"), reg=("regret", "mean"))
            lab = f"{label}, {config}" if config == "independent" or pol != "sp_ucb_st1" else None
            axes[0].plot(g.index, 100 * g.viol, ls=ls, color=color, marker=marker, ms=4, lw=1.6, label=lab)
            axes[1].plot(g.index, g.reg, ls=ls, color=color, marker=marker, ms=4, lw=1.6)
    axes[0].set_ylabel("Runs with a violated\ncertificate (%)")
    axes[1].set_ylabel("Mean regret (T = 5,000)")
    for ax in axes:
        ax.set_xlabel("Persistence φ")
        ax.set_xticks([0, 0.5, 0.9, 0.97])
    axes[0].set_title("Standard certificates fail under persistence", loc="left", color=INK)
    axes[1].set_title("Valid certificates at similar regret", loc="left", color=INK)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, -0.18))
    fig.text(0.99, -0.2, "solid: independent shocks · dotted: correlated shocks", ha="right", fontsize=7, color=MUTED)
    save(fig, "fig3_certificates_under_persistence")


def fig4_toy() -> None:
    """Fluctuation channel, controlled: dynamic regret by policy family (main toy configuration)."""
    s = pd.read_csv(ST / "summary.csv")
    s = s[s.config == "main"]
    keep = {"st_ps": "ST predictive sampling", "st_ucbm2": "ST UCB (2 sd)", "spectral_ucb": "SpectralUCB",
            "ucb": "UCB1", "ar_ps": "AR predictive sampling", "ts": "Thompson sampling",
            "st_ts": "ST state-TS", "st_greedy": "ST greedy"}
    s = s[s.policy.isin(keep)].sort_values("dynamic_regret_per_round", ascending=False)
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    y = np.arange(len(s))
    colors = [FAMILY_COLOR[f] for f in s.family]
    ax.barh(y, s.dynamic_regret_per_round, xerr=1.96 * s.se, color=colors, height=0.62,
            error_kw={"lw": 0.8, "ecolor": MUTED})
    floor = s.innovation_floor.iloc[0]
    ax.axvline(floor, color=INK, lw=0.9, ls="--")
    ax.text(floor + 0.02, len(s) - 0.4, "lower bound", fontsize=7, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([keep[p] for p in s.policy])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Dynamic regret per round")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in FAMILY_COLOR.values()]
    ax.legend(handles, FAMILY_COLOR.keys(), fontsize=6.5, loc="lower right", handlelength=1)
    ax.set_title("Model the dynamics, explore what persists", loc="left", color=INK)
    save(fig, "fig4_toy_fluctuation_channel")


def fig5_daily() -> None:
    """Fluctuation channel on KuaiRec daily: full against sparse fit-window history."""
    full = pd.concat([pd.read_csv(KR / "daily_runs.csv"), pd.read_csv(KR / "daily_runs_extra.csv")])
    sparse = pd.read_csv(KR / "daily_runs_sparse.csv")
    f = full.groupby("policy").regret_per_day.mean()
    sp = sparse.groupby("policy").regret_per_day.mean()
    rows = [("Model, greedy", f.get("dr1_greedy"), sp.get("sh_greedy"), BLUE),
            ("Model, UCB 1 sd", f.get("dr1_ucbm1"), sp.get("sh_ucbm1"), BLUE),
            ("Model, predictive sampling", f.get("st_jps"), sp.get("sh_jps"), BLUE),
            ("iid Thompson sampling", f.get("ts_iid"), sp.get("sh_tsiid"), GRAY)]
    fig, ax = plt.subplots(figsize=(3.4, 1.9))
    for k, (label, a, b, color) in enumerate(rows):
        ax.plot([a, b], [k, k], color=GRID, lw=2)
        ax.scatter([a], [k], s=24, color=color, zorder=3, marker="o")
        ax.scatter([b], [k], s=24, facecolor="white", edgecolor=color, zorder=3, marker="o", lw=1.4)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows])
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Regret per day (10 slots, logit completion rate)")
    ax.scatter([], [], s=24, color=BLUE, label="full history")
    ax.scatter([], [], s=24, facecolor="white", edgecolor=BLUE, label="sparse history")
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title("KuaiRec daily: modelling persistence pays", loc="left", color=INK)
    save(fig, "fig5_kuairec_daily")


if __name__ == "__main__":
    fig1_alignment()
    fig2_pooling_tails()
    fig3_certificates()
    fig4_toy()
    fig5_daily()
    print("figures written to", OUT)
