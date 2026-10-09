"""Render Phase 1 alignment results: a summary table (markdown) and Figure 1.

Usage (from the repo root, after alignment.py):
    .venv/bin/python -I experiments/kuairec/render_alignment.py [--model R1]
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
        "| Graph | Side | Edges | Isolated | Quotient (real / rewired) | Edge corr. (real / random pairs) | Top-1 kept @λ=1 (real / rewired) | Choice regret @λ=1 (real / rewired) |",
        "| --- | --- | ---: | ---: | --- | --- | --- | --- |",
    ]
    for g, r in real.sort_values(["axis", "quotient_median"]).iterrows():
        n = rew.loc[g]
        lines.append(
            f"| {g} | {r.axis} | {r.edges:,} | {r.isolated:,} | {r.quotient_median:.3f} / {n.quotient_median:.3f} "
            f"| {r.edge_corr:.3f} / {r.random_pair_corr:.3f} | {r['top1_kept@1']:.3f} / {n['top1_kept@1']:.3f} "
            f"| {r['choice_regret@1']:.3f} / {n['choice_regret@1']:.3f} |"
        )
    return "\n".join(lines)


def figure(signals: pd.DataFrame, summary: pd.DataFrame, path: Path) -> None:
    real = summary[summary.null == "real"].sort_values(["axis", "quotient_median"])
    real = real[real.isolated < 0.5 * real.nodes]  # near-empty graphs (U-soc) stay in the table only
    graphs = real.graph.tolist()
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(graphs) + 1.2))
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


def main(model: str) -> None:
    summary = pd.read_csv(RESULTS / f"alignment_summary_{model}.csv")
    signals = pd.read_csv(RESULTS / f"alignment_signals_{model}.csv.gz")
    (RESULTS / f"alignment_table_{model}.md").write_text(table(summary) + "\n")
    figure(signals, summary, RESULTS / f"alignment_quotients_{model}.png")
    print(table(summary))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="R1", choices=["R1", "R2", "R3"])
    main(ap.parse_args().model)
