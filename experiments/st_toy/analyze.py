"""Summarize the spatiotemporal toy: regret per round by policy and configuration, and a figure.

Usage (from the repo root, after toy.py):
    .venv/bin/python -I experiments/st_toy/analyze.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from toy import CONFIGS, SEED, World  # noqa: E402

RESULTS = Path(__file__).resolve().parents[2] / "research" / "st_toy" / "results"
FAMILY = {
    "ucb": "iid", "ts": "iid", "swucb": "iid",
    "spectral_ucb": "spatial only", "spectral_ts": "spatial only",
    "ar_ts": "temporal only", "ar_twostep": "temporal only",
    "st_greedy": "spatiotemporal", "st_ts": "spatiotemporal", "st_ucb": "spatiotemporal",
    "st_twostep": "spatiotemporal",
}
COLORS = {"iid": "#9aa3ad", "spatial only": "#e08a2c", "temporal only": "#3b9a5a", "spatiotemporal": "#2a6fdb"}


def innovation_floor(config: str, seed: int, draws: int = 200_000) -> float:
    """Per-round lower bound on dynamic regret for any causal policy (known means and past states):
    E max_i (mu_i + Z_i), Z ~ N(0, Gamma)  minus  the same with Z ~ N(0, Gamma - Q).
    Here Gamma = C (unit marginal variance) and Q = q C."""
    w = World(seed=SEED + seed, T=1, **CONFIGS[config])
    rng = np.random.default_rng(seed)
    Lc = np.linalg.cholesky(w.C)
    Z = rng.standard_normal((draws, w.N)) @ Lc.T
    full = (w.mu + Z).max(axis=1).mean()
    past = (w.mu + np.sqrt(1 - w.q) * Z).max(axis=1).mean()
    return float(full - past)


def main() -> None:
    runs = pd.read_csv(RESULTS / "runs.csv")
    T = max(int(c.split("@")[1]) for c in runs.columns if c.startswith("dyn@") and runs[c].notna().all())
    runs["dyn_per_round"] = runs[f"dyn@{T}"] / T
    runs["mu_per_round"] = runs[f"mu@{T}"] / T
    rows = []
    for (config, policy), d in runs.groupby(["config", "policy"]):
        x, y = d.dyn_per_round.to_numpy(), d.mu_per_round.to_numpy()
        se = x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else np.nan
        rows.append({"config": config, "policy": policy, "family": FAMILY[policy], "seeds": len(x),
                     "dynamic_regret_per_round": x.mean(), "se": se, "mean_regret_per_round": y.mean()})
    s = pd.DataFrame(rows)
    # Paired difference against the best non-model baseline (TS) per seed.
    ts = runs[runs.policy == "ts"].set_index(["config", "seed"]).dyn_per_round
    runs["vs_ts"] = runs.dyn_per_round.to_numpy() / ts.reindex(pd.MultiIndex.from_frame(runs[["config", "seed"]])).to_numpy()
    s = s.merge(runs.groupby(["config", "policy"]).vs_ts.mean().rename("ratio_to_ts").reset_index())
    floors = {(c, sd): innovation_floor(c, sd) for c, sd in runs[["config", "seed"]].drop_duplicates().itertuples(index=False)}
    floor = pd.Series(floors).groupby(level=0).mean()
    s["innovation_floor"] = s.config.map(floor)
    s.to_csv(RESULTS / "summary.csv", index=False)

    lines = [f"Regret per round at T = {T:,} (mean over seeds; standard error in brackets). Dynamic regret is "
             "against the full-current-state oracle; mean regret against the best long-run mean.", ""]
    for config, d in s.groupby("config", sort=False):
        lines += [f"**{config}** (innovation lower bound: {floor[config]:.3f} per round)", "",
                  "| Policy | Uses | Dynamic regret / round | Ratio to TS | Mean regret / round |",
                  "| --- | --- | ---: | ---: | ---: |"]
        for _, r in d.sort_values("dynamic_regret_per_round").iterrows():
            lines.append(f"| {r.policy} | {r.family} | {r.dynamic_regret_per_round:.3f} [{r.se:.3f}] "
                         f"| {r.ratio_to_ts:.3f} | {r.mean_regret_per_round:.3f} |")
        lines.append("")
    text = "\n".join(lines)
    (RESULTS / "summary.md").write_text(text)
    print(text)

    configs = list(s.config.unique())
    fig, axes = plt.subplots(1, len(configs), figsize=(4.2 * len(configs), 4.2), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, config in zip(axes, configs):
        d = s[s.config == config].sort_values("dynamic_regret_per_round", ascending=False)
        ax.barh(d.policy, d.dynamic_regret_per_round, xerr=1.96 * d.se,
                color=[COLORS[f] for f in d.family], error_kw={"lw": 0.8})
        ax.set_title(config, fontsize=10)
        ax.set_xlabel("Dynamic regret per round")
        ax.spines[["top", "right"]].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLORS.values()]
    fig.legend(handles, COLORS.keys(), loc="lower center", ncol=4, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(RESULTS / "regret.png", dpi=160)


if __name__ == "__main__":
    main()
