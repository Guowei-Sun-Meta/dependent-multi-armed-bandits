"""Figures for the WWW 2027 correlated-arms paper (PDF for LaTeX and PNG for review).

Usage (from the repo root):
    .venv/bin/python -I experiments/paper_figures.py

Writes research/claude_opus_10_09/figures/fig{1..6}_*.{pdf,png} from saved results only.
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
OUT = ROOT / "research" / "claude_opus_10_09" / "figures"

BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
PHI_POS = {0.0: 0, 0.5: 1, 0.9: 2, 0.97: 3}  # evenly spaced persistence levels
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
    """Within the UCB family: SP-UCB without and with an (oracle) certificate, relative to UCB1."""
    r = pd.read_csv(KR / "setting_a_runs.csv")
    col = "regret@20000"
    ucb = r[r.policy == "ucb"].set_index("user")[col]
    graphs = ["I-mf", "I-coeng", "I-tag", "I-cat", "I-coauthor"]
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    for k, g in enumerate(graphs):
        for off, cert, color, label in ((-0.15, "none", ORANGE, "No certificate"), (0.15, "oracle", BLUE, "Oracle certificate")):
            x = (r[(r.policy == "sp_ucb") & (r.graph == g) & (r.param == cert)].set_index("user")[col] / ucb).dropna()
            lo, med, hi = np.quantile(x, [0.1, 0.5, 0.9])
            ax.hlines(k + off, lo, hi, color=color, lw=2)
            ax.scatter([med], [k + off], s=22, color=color, zorder=3, label=label if k == 0 else None)
    ax.set_xscale("log")
    ax.axvline(1, color=MUTED, lw=0.8, ls="--")
    ax.text(1.04, len(graphs) - 0.45, "UCB1", fontsize=7, color=MUTED)
    ax.set_yticks(range(len(graphs)))
    ax.set_yticklabels(graphs)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("SP-UCB / UCB1 regret per user\n(median, 10th–90th percentile)")
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.0, -0.32), ncol=2)
    ax.set_title("No certificate: lower median, wider spread", loc="left", color=INK)
    save(fig, "fig2_pooling_tails")


def fig3_certificates() -> None:
    """Certificates under persistence with bursty exposure (blocks of 25): validity and regret."""
    d = pd.read_csv(ST / "coverage_runs_plugin.csv")  # all certificates on identical shuffled worlds
    d = d[(d.batch == 25) & d.policy.isin(["sp_ucb_iid", "sp_ucb_st1", "sp_ucb_st2"])]
    d = d.drop_duplicates(["config", "phi", "seed", "policy"])
    series = [("sp_ucb_iid", "iid certificate", ORANGE, "o"),
              ("sp_ucb_st1", "B1′ scalar (valid for independent shocks)", BLUE, "s"),
              ("sp_ucb_st2", "B1″ plug-in (valid for both)", AQUA, "^")]
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.1))
    for config, ls in (("independent", "-"), ("correlated", ":")):
        for pol, label, color, marker in series:
            s = d[(d.config == config) & (d.policy == pol)]
            if s.empty:
                continue
            g = s.groupby("phi").agg(viol=("any_violation", "mean"), reg=("regret", "mean"))
            g.index = [PHI_POS[v] for v in g.index]
            lab = label if config == "independent" else None
            axes[0].plot(g.index, 100 * g.viol, ls=ls, color=color, marker=marker, ms=4, lw=1.6, label=lab)
            axes[1].plot(g.index, g.reg, ls=ls, color=color, marker=marker, ms=4, lw=1.6)
    axes[0].set_ylabel("Runs with a violated\ncertificate (%)")
    axes[1].set_ylabel("Mean regret (T = 5,000)")
    for ax in axes:
        ax.set_xlabel("Persistence φ")
        ax.set_xticks(list(PHI_POS.values()))
        ax.set_xticklabels([str(v) for v in PHI_POS])
    axes[0].set_title("iid certificates fail as persistence grows", loc="left", color=INK)
    axes[1].set_title("Valid certificates, comparable regret", loc="left", color=INK)
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
    ax.legend(handles, FAMILY_COLOR.keys(), fontsize=7, loc="upper left", bbox_to_anchor=(-0.05, -0.2),
              ncol=4, handlelength=1, columnspacing=0.8)
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
