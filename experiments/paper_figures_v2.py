"""Figures for the revised long paper (research/claude_opus_10_09_v2), one per theory-to-evidence bridge.

Usage (from the repo root, after experiments/deepdive.py):
    .venv/bin/python -I experiments/paper_figures_v2.py

f1 alignment            Q1: which graphs encode correlated appeal
f2 pooling_bridge       Q2: certified gain vs rejectable share; uncertified failures by mechanism
f3 b2_bridge            Q3: B2's predicted miscoverage vs observed violations; regret by certificate
f4 toy_curves           Q4: benchmark learning curves
f5 synthesis            Q4: exploration vs observations per arm; shock correlation along graphs
f6 wikipedia_multi      Q4: graph conditions on the six-community panel
Colour by role (same as experiments/paper_figures.py): iid gray, mean channel only orange,
persistence only aqua, both channels / certified blue.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_figures as pf  # noqa: E402  (styles, colours, rcParams)
from paper_figures import AQUA, BLUE, GRAY, GRID, INK, MUTED, ORANGE, plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "research" / "claude_opus_10_09_v2"
AN = V2 / "analysis"
OUT = V2 / "figures"
ST = ROOT / "research" / "st_toy" / "results"
PHI_POS = {0.0: 0, 0.5: 1, 0.9: 2, 0.97: 3}


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=220 if ext == "png" else None)
    plt.close(fig)


def f1() -> None:
    pf.OUT = OUT
    pf.fig1_alignment()
    for ext in ("pdf", "png"):
        (OUT / f"fig1_graph_alignment.{ext}").replace(OUT / f"f1_alignment.{ext}")


def f2() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.5))
    ax = axes[0]
    for cert, share, color, label, off in (("oracle", "rejectable_oracle", BLUE, "Oracle certificate", -0.08),
                                           ("energy", "rejectable_energy", ORANGE, "Energy certificate", 0.08)):
        m = pd.read_csv(AN / f"certified_instances_{cert}.csv")
        m["bin"] = pd.cut(m[share], [-0.01, 0.2, 0.4, 0.6, 0.8, 1.0])
        g = m.groupby("bin", observed=True).ratio
        x = np.array([iv.mid for iv in g.median().index])
        ax.errorbar(x + off * 0.1, g.median(), yerr=[g.median() - g.quantile(0.25), g.quantile(0.75) - g.median()],
                    fmt="o-", color=color, ms=4, lw=1.6, capsize=0, label=label)
    ax.axhline(1, color=MUTED, lw=0.8, ls="--")
    ax.set_xlabel("Share of suboptimal components rejectable\n(certified width below gap)")
    ax.set_ylabel("SP-UCB / UCB1 regret (median, IQR)")
    ax.set_title("Certified gains follow the theorem", loc="left", color=INK)
    ax.legend(fontsize=7, loc="lower left")
    ax = axes[1]
    u = pd.read_csv(AN / "uncertified_instances.csv")
    rng = np.random.default_rng(0)
    for k, (top, label) in enumerate(((True, "Optimal component\nis top by average"),
                                      (False, "Optimal component\nis not top"))):
        y = u[u.optimal_component_top == top].ratio.to_numpy()
        ax.scatter(np.log10(y), k + rng.uniform(-0.18, 0.18, len(y)), s=6, color=GRAY if top else ORANGE, alpha=0.6, lw=0)
        med, p90 = np.median(y), np.quantile(y, 0.9)
        ax.plot([np.log10(med)] * 2, [k - 0.3, k + 0.3], color=INK, lw=1.6)
        ax.text(np.log10(p90), k + 0.42, f"90th pct {p90:.2f}×", fontsize=7, color=MUTED, ha="center", va="top")
        ax.plot([np.log10(p90)] * 2, [k - 0.22, k + 0.22], color=MUTED, lw=1)
    ax.axvline(0, color=MUTED, lw=0.8, ls="--")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Optimal\ncomponent\ntop by avg.", "Optimal\ncomponent\nnot top"])
    ax.set_xticks([-1, -0.5, 0, 0.5])
    ax.set_xticklabels(["0.1×", "0.32×", "1×", "3.2×"])
    ax.set_xlabel("Uncertified SP-UCB / UCB1 regret")
    ax.grid(axis="y", visible=False)
    ax.invert_yaxis()
    ax.set_title("Uncertified pooling fails by dilution", loc="left", color=INK)
    fig.subplots_adjust(wspace=0.45)
    save(fig, "f2_pooling_bridge")


def f3() -> None:
    b2 = pd.read_csv(AN / "b2_prediction_vs_observed.csv")
    d = pd.read_csv(ST / "coverage_runs_plugin.csv")
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.4))
    ax = axes[0]
    ind = b2[b2.shocks == "independent"].sort_values("phi")
    cor = b2[b2.shocks == "correlated"].sort_values("phi")
    x = [PHI_POS[v] for v in ind.phi]
    ax.plot(x, 100 * ind["B2 per-check miscoverage"], "--", color=INK, lw=1.4, marker="D", ms=4,
            label="B2 prediction, per check")
    ax.plot(x, 100 * ind["iid runs violated (blocks)"], "-", color=ORANGE, lw=1.8, marker="o", ms=4,
            label="iid certificate, runs violated")
    ax.plot(x, 100 * cor["iid runs violated (blocks)"], ":", color=ORANGE, lw=1.8, marker="o", ms=4)
    ax.plot(x, 100 * ind["B1'' runs violated (blocks)"], "-", color=AQUA, lw=1.8, marker="^", ms=4,
            label="B1″ certificate, runs violated")
    ax.set_ylabel("Percent")
    ax.set_title("B2 predicts when iid certificates fail", loc="left", color=INK)
    ax.legend(fontsize=6.8, loc="upper left")
    ax = axes[1]
    for config, ls in (("independent", "-"), ("correlated", ":")):
        for pol, label, color, marker in (("sp_ucb_iid", "iid", ORANGE, "o"), ("sp_ucb_st1", "B1′ scalar", BLUE, "s"),
                                          ("sp_ucb_st2", "B1″ plug-in", AQUA, "^")):
            s = d[(d.config == config) & (d.policy == pol) & (d.batch == 25)].groupby("phi").regret.mean()
            ax.plot([PHI_POS[v] for v in s.index], s, ls=ls, color=color, marker=marker, ms=4, lw=1.6,
                    label=label if config == "independent" else None)
    ax.set_ylabel("Mean regret (T = 5,000)")
    ax.set_title("Valid certificates at comparable regret", loc="left", color=INK)
    ax.legend(fontsize=6.8, loc="upper left")
    for ax in axes:
        ax.set_xticks(list(PHI_POS.values()))
        ax.set_xticklabels([str(v) for v in PHI_POS])
        ax.set_xlabel("Persistence φ (exposure in blocks of 25)")
    fig.text(0.99, -0.13, "solid: independent shocks · dotted: correlated shocks", ha="right", fontsize=7, color=MUTED)
    save(fig, "f3_b2_bridge")


def f4() -> None:
    c = pd.read_csv(AN / "toy_learning_curves.csv")
    floors = pd.read_csv(ST / "summary.csv").groupby("config").innovation_floor.first()
    series = [("st_ps", "ST predictive sampling", BLUE, "-"), ("st_ucbm2", "ST UCB (2 sd)", BLUE, "--"),
              ("st_greedy", "ST greedy", BLUE, ":"), ("ar_ps", "AR predictive sampling", AQUA, "-"),
              ("spectral_ucb", "SpectralUCB", ORANGE, "-"), ("ucb", "UCB1", GRAY, "-"), ("ts", "Thompson sampling", GRAY, "--")]
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.6), sharey=True)
    for ax, cfg, title in ((axes[0], "main", "Correlated shocks (main)"), (axes[1], "no_spatial", "Independent shocks")):
        x = c[c.configuration == cfg]
        for key, label, color, ls in series:
            ax.plot(x["t / N"], x[key], ls=ls, color=color, lw=1.6, marker="o", ms=3, label=label)
        ax.axhline(floors[cfg], color=INK, lw=0.9, ls="--")
        ax.text(20, floors[cfg] + 0.04, "lower bound", ha="right", fontsize=7, color=INK)
        ax.set_xscale("log")
        ax.set_xticks([1, 2.5, 5, 10, 20])
        ax.set_xticklabels(["1", "2.5", "5", "10", "20"])
        ax.set_xlabel("Observations per arm so far (t / N)")
        ax.set_title(title, loc="left", color=INK)
    axes[0].set_ylabel("Dynamic regret per round")
    axes[0].legend(fontsize=6.5, loc="upper left", bbox_to_anchor=(0.0, -0.3), ncol=4)
    save(fig, "f4_toy_curves")


def f5() -> None:
    e = pd.read_csv(AN / "exploration_vs_horizon.csv")
    short = {"Benchmark (100 arms, AR(20))": "Bench-\nmark", "Wikipedia, one domain": "Wiki\n1 domain",
             "Wikipedia, six domains": "Wiki\n6 domains", "KuaiRec daily, full history": "KuaiRec\nfull hist.",
             "KuaiRec daily, sparse history": "KuaiRec\nsparse hist."}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    x = np.arange(len(e))
    ax.scatter(x - 0.12, e["PS / greedy"], s=34, color=BLUE, marker="o", zorder=3, label="Predictive sampling (heavy)")
    ax.scatter(x + 0.12, e["UCB 1 sd / greedy"], s=34, color=AQUA, marker="s", zorder=3, label="UCB, 1 sd (mild)")
    ax.axhline(1, color=MUTED, lw=0.8, ls="--")
    ax.set_xticks(x)
    labels = []
    for _, r in e.iterrows():
        gap = "\n" if np.isnan(r["10th-11th gap"]) else f"\ngap {r['10th-11th gap']:.2f}"
        labels.append(f"{short[r.environment]}\n{r['observations per arm in horizon']:.0f}/arm{gap}")
    ax.set_xticklabels(labels, fontsize=6.5)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Regret relative to greedy")
    ax.set_title("How much to explore", loc="left", color=INK)
    ax.legend(fontsize=6.8, loc="upper left")
    ax = axes[1]
    panels = ["KuaiRec\ndaily", "Wikipedia\none domain", "Wikipedia\nsix domains"]
    vals = {"Graph edges": [0.071, 0.256, 0.273], "Rewired edges": [0.068, 0.250, 0.051], "All pairs": [0.042, 0.218, 0.051]}
    colors = {"Graph edges": BLUE, "Rewired edges": GRAY, "All pairs": "#c9c8c3"}
    w = 0.26
    for k, (lab, v) in enumerate(vals.items()):
        ax.bar(np.arange(3) + (k - 1) * w, v, width=w - 0.02, color=colors[lab], label=lab)
    ax.set_xticks(range(3))
    ax.set_xticklabels(panels, fontsize=7.5)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Mean shock correlation")
    ax.set_ylim(0, 0.36)
    ax.set_title("Links carry community shocks", loc="left", color=INK)
    ax.legend(fontsize=6.8, loc="upper left", handlelength=1)
    fig.subplots_adjust(wspace=0.35)
    save(fig, "f5_synthesis")


def f6() -> None:
    path = AN / "wikipedia_multi_graph_effect.csv"
    if not path.exists():
        return
    g = pd.read_csv(path)
    name = {"st_greedy": "Greedy, hyperlinks", "st_greedy_block": "Greedy, community blocks",
            "st_greedy_rewired": "Greedy, rewired", "st_jps": "Pred. sampling, hyperlinks",
            "st_jps_block": "Pred. sampling, blocks"}
    color = {"st_greedy": BLUE, "st_greedy_block": "#7aa9e6", "st_greedy_rewired": GRAY, "st_jps": BLUE,
             "st_jps_block": "#7aa9e6"}
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    y = np.arange(len(g))
    ax.errorbar(100 * g.relative, y, xerr=196 * g["standard error"] / (g["mean difference"] / g.relative),
                fmt="none", ecolor=MUTED, lw=1)
    ax.scatter(100 * g.relative, y, s=30, color=[color[p] for p in g.policy], zorder=3)
    ax.axvline(0, color=MUTED, lw=0.8, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels([name[p] for p in g.policy])
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Change in regret against the\ncommon-factor covariance (%, 95% CI)")
    ax.set_title("Six communities: small decision effect", loc="left", color=INK)
    save(fig, "f6_wikipedia_multi")


if __name__ == "__main__":
    f1()
    f2()
    f3()
    f4()
    f5()
    f6()
    print("figures written to", OUT)
