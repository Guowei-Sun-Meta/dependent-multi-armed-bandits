"""Render Phase 1 alignment results: summary tables (markdown) and Figure 1.

Usage (from the repo root, after alignment.py):
    .venv/bin/python -I experiments/kuairec/code/render_alignment.py [--model R1] [--k 10]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import RESULTS  # noqa: E402

NULL_COLORS = {"real": "#2a6fdb", "rewired": "#9aa3ad", "er": "#d4d8dd"}


def table(summary: pd.DataFrame) -> str:
    real = summary[summary.null == "real"].set_index("graph")
    rew = summary[summary.null == "rewired"].set_index("graph")
    lines = [
        "| Graph | Side | Edges | Quotient (real / rewired) | Personal-taste edge corr. (real / random) "
        "| Choice cost @λ=1 (real / rewired) | Choice cost @λ=10 (real / rewired) |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for g, r in real.sort_values(["axis", "quotient_median"]).iterrows():
        n = rew.loc[g]
        lines.append(
            f"| {g} | {r.axis} | {r.edges:,} | {r.quotient_median:.3f} / {n.quotient_median:.3f} "
            f"| {r.edge_corr_dc:.3f} / {r.random_pair_corr_dc:.3f} "
            f"| {r['choice_regret@1']:.3f} / {n['choice_regret@1']:.3f} "
            f"| {r['choice_regret@10']:.3f} / {n['choice_regret@10']:.3f} |"
        )
    return "\n".join(lines)


def k_table(model: str) -> str:
    frames = [pd.read_csv(p) for p in sorted(RESULTS.glob(f"alignment_summary_{model}_k*.csv"))]
    if not frames:
        return ""
    d = pd.concat(frames)
    d = d[d.null == "real"]
    q = d.pivot(index="graph", columns="k", values="quotient_median")
    c = d.pivot(index="graph", columns="k", values="edge_corr_dc")
    ks = sorted(q.columns)
    head = "| Graph | " + " | ".join(f"Quotient k={k}" for k in ks) + " | " + " | ".join(
        f"Personal corr. k={k}" for k in ks) + " |"
    lines = [head, "| --- |" + " ---: |" * (2 * len(ks))]
    for g in q.sort_values(ks[len(ks) // 2]).index:
        lines.append(f"| {g} | " + " | ".join(f"{q.loc[g, k]:.3f}" for k in ks) + " | "
                     + " | ".join(f"{c.loc[g, k]:.3f}" for k in ks) + " |")
    return "\n".join(lines)


def figure(signals: pd.DataFrame, summary: pd.DataFrame, path: Path) -> None:
    real = summary[summary.null == "real"].sort_values(["axis", "quotient_median"])
    real = real[real.isolated < 0.5 * real.nodes]  # near-empty graphs (U-soc) stay in the table only
    graphs = real.graph.tolist()
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(graphs) + 1.2))
    for i, g in enumerate(graphs):
        for j, null in enumerate(["real", "rewired", "er"]):
            q = signals[(signals.graph == g) & (signals.null == null)].quotient.to_numpy()
            if len(q) == 0:
                continue
            lo, mid, hi = np.quantile(q, [0.1, 0.5, 0.9])
            y = i + (j - 1) * 0.22
            ax.plot([lo, hi], [y, y], color=NULL_COLORS[null], lw=2)
            ax.plot(mid, y, "o", color=NULL_COLORS[null], ms=5, label=null if i == 0 else None)
    ax.axvline(1.0, color="#555", lw=0.8, ls="--")
    ax.set_yticks(range(len(graphs)))
    ax.set_yticklabels(graphs)
    ax.invert_yaxis()
    ax.set_xlabel("Smoothness quotient (median, 10th-90th percentile); 1 = no better than random")
    ax.legend(frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)


def main(model: str, k: int) -> None:
    summary = pd.read_csv(RESULTS / f"alignment_summary_{model}_k{k}.csv")
    signals = pd.read_csv(RESULTS / f"alignment_signals_{model}_k{k}.csv.gz")
    text = table(summary) + "\n\nNeighbour-count sensitivity:\n\n" + k_table(model) + "\n"
    (RESULTS / f"alignment_table_{model}_k{k}.md").write_text(text)
    figure(signals, summary, RESULTS / f"alignment_quotients_{model}_k{k}.png")
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="R1", choices=["R1", "R2", "R3"])
    ap.add_argument("--k", type=int, default=10)
    a = ap.parse_args()
    main(a.model, a.k)
