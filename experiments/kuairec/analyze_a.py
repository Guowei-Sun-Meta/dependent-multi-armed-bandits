"""Summarize Setting A: regret by policy and graph, and per-instance graph diagnostics.

Usage (from the repo root, after setting_a.py):
    .venv/bin/python -I experiments/kuairec/analyze_a.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import RESULTS  # noqa: E402

BOOT = 2000
SEED = 20261009


def boot_ci(x: np.ndarray, rng) -> tuple[float, float]:
    means = rng.choice(x, size=(BOOT, len(x))).mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def main() -> None:
    rng = np.random.default_rng(SEED)
    runs = pd.read_csv(RESULTS / "setting_a_runs.csv")
    insts = pd.read_csv(RESULTS / "setting_a_instances.csv")
    T = max(int(c.split("@")[1]) for c in runs.columns if c.startswith("regret@") and runs[c].notna().all())
    col = f"regret@{T}"
    ts = runs[runs.policy == "ts"].set_index("user")[col]
    runs["ratio_ts"] = runs[col].to_numpy() / ts.reindex(runs.user).to_numpy()

    rows = []
    for (policy, graph, param), d in runs.groupby(["policy", "graph", "param"], sort=False):
        lo, hi = boot_ci(d.ratio_ts.to_numpy(), rng)
        rows.append({
            "policy": policy, "graph": graph, "param": param, "users": len(d),
            f"mean_{col}": d[col].mean(), "ratio_to_ts": d.ratio_ts.mean(), "ci_low": lo, "ci_high": hi,
            "share_beats_ts": float((d.ratio_ts < 1).mean()),
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(RESULTS / "setting_a_summary.csv", index=False)

    diag = insts.groupby("graph").agg(
        quotient=("quotient", "median"),
        energy_to_gap10=("energy_to_gap10", "median"),
        rejectable_oracle=("rejectable_oracle", "mean"),
        rejectable_energy=("rejectable_energy", "mean"),
    ).reset_index()
    diag.to_csv(RESULTS / "setting_a_diagnostics.csv", index=False)

    lines = [f"Regret at T = {T:,} relative to Bernoulli Thompson sampling (mean over users; 95% bootstrap CI).", "",
             "| Policy | Graph | Parameter | Regret ratio to TS | 95% CI | Share of users beating TS |",
             "| --- | --- | --- | ---: | --- | ---: |"]
    for _, r in summary.iterrows():
        lines.append(f"| {r.policy} | {r.graph} | {r.param} | {r.ratio_to_ts:.3f} | {r.ci_low:.3f} to {r.ci_high:.3f} "
                     f"| {r.share_beats_ts:.2f} |")
    lines += ["", "Per-instance graph diagnostics (300-video graphs; medians or means over users):", "",
              "| Graph | Quotient | Energy-to-gap (10th) | Share of components rejectable, oracle cert. "
              "| Share rejectable, energy cert. |", "| --- | ---: | ---: | ---: | ---: |"]
    for _, r in diag.sort_values("quotient").iterrows():
        lines.append(f"| {r.graph} | {r.quotient:.3f} | {r.energy_to_gap10:.1f} | {r.rejectable_oracle:.2f} "
                     f"| {r.rejectable_energy:.2f} |")
    text = "\n".join(lines) + "\n"
    (RESULTS / "setting_a_table.md").write_text(text)
    print(text)

    # Figure: regret ratio to TS per graph, one marker per policy variant.
    graphs = [g for g in summary.graph.unique() if g != "-"]
    variants = summary[summary.graph != "-"][["policy", "param"]].drop_duplicates().values.tolist()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    width = 0.8 / len(variants)
    cmap = plt.get_cmap("tab20")
    for j, (policy, param) in enumerate(variants):
        d = summary[(summary.policy == policy) & (summary.param == param)].set_index("graph").reindex(graphs)
        x = np.arange(len(graphs)) + (j - len(variants) / 2) * width
        ax.errorbar(x, d.ratio_to_ts, yerr=[d.ratio_to_ts - d.ci_low, d.ci_high - d.ratio_to_ts], fmt="o", ms=4,
                    color=cmap(j), label=f"{policy} {param}")
    ucb = summary[summary.policy == "ucb"].ratio_to_ts.iloc[0]
    ax.axhline(1.0, color="#555", lw=0.8, ls="--")
    ax.axhline(ucb, color="#c44", lw=0.8, ls=":")
    ax.text(len(graphs) - 0.5, ucb, " UCB1", color="#c44", va="center", fontsize=8)
    ax.set_xticks(range(len(graphs)))
    ax.set_xticklabels(graphs)
    ax.set_ylabel(f"Regret at T={T:,} / Thompson sampling")
    ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper left", bbox_to_anchor=(0, -0.12))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(RESULTS / "setting_a_regret.png", dpi=160)


if __name__ == "__main__":
    main()
