"""Tables for the chronological KuaiRec daily experiment (daily_chrono.py).

Usage (from the repo root):
    .venv/bin/python -I experiments/oct10_evening/code/analyze_daily.py

Unit = panel x test window (15). Seeds are averaged within a unit. Contrasts are paired within
units, as relative differences in mean regret, with 95% intervals from a two-level bootstrap:
resample the 3 windows, then the 5 panels within each resampled window (panels differ across
windows). Intervals that cross zero mean inconclusive, not equal.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path(__file__).resolve().parents[1] / "results" / "daily_chrono"
B = 4000
RNG = np.random.default_rng(20261010)


def unit_means(d):
    d = d.copy()
    d["window"] = d.unit.str.extract(r"_F(\d+)_")[0].astype(int)
    return d.groupby(["window", "unit", "k", "policy"]).regret_per_slot_day.mean().unstack("policy")


def boot_ratio(U, a, b):
    """Relative difference mean(a)/mean(b) - 1 over units, two-level bootstrap."""
    wins = U.index.get_level_values("window").unique().to_numpy()
    groups = {w: U.xs(w, level="window") for w in wins}
    est = U[a].mean() / U[b].mean() - 1
    stats = []
    for _ in range(B):
        ws = RNG.choice(wins, size=len(wins))
        num = den = 0.0
        for w in ws:
            g = groups[w]
            idx = RNG.integers(len(g), size=len(g))
            num += g[a].to_numpy()[idx].sum()
            den += g[b].to_numpy()[idx].sum()
        stats.append(num / den - 1)
    lo, hi = np.quantile(stats, [0.025, 0.975])
    wins_a = float((U[a] < U[b]).mean())
    return est, lo, hi, wins_a


def main():
    d = pd.read_csv(RESULTS / "test_runs.csv")
    meta = pd.read_csv(RESULTS / "units.csv")
    tuned = pd.read_json(RESULTS / "tuned.json", typ="series")
    M = unit_means(d)
    out = ["# KuaiRec daily slot, chronological protocol: tables", "",
           "Regret per slot per day (logit complete-play rate), mean over 15 panel-window units "
           "(5 seeds averaged within each unit). Lower is better.", ""]
    rows = []
    for k, g in M.groupby(level="k"):
        r = g.mean().sort_values()
        for pol, v in r.items():
            rows.append({"k": k, "policy": pol, "regret": round(v, 4),
                         "÷ ts_iid": round(v / r["ts_iid"], 3), "÷ static": round(v / r["static"], 3)})
    out += [pd.DataFrame(rows).to_markdown(index=False), ""]
    contrasts = [("st_ucb", "ts_iid", "joint filter (graph) vs iid TS"),
                 ("ar_ucb", "ts_iid", "temporal-only filter vs iid TS"),
                 ("st_ucb", "ar_ucb", "graph vs temporal-only (same UCB)"),
                 ("st_ucb", "st_ucb_rewired", "real vs rewired prefix graph"),
                 ("st_ucb", "st_ucb_nograph", "graph vs common factor only"),
                 ("st_ucb", "ewma", "joint filter vs EWMA (forgetting)"),
                 ("st_ucb", "dts", "joint filter vs discounted TS (forgetting)"),
                 ("ar_ucb", "ewma", "temporal-only filter vs EWMA"),
                 ("st_ucb", "last_value", "joint filter (UCB) vs last value"),
                 ("st_greedy", "last_value", "joint filter (greedy) vs last value"),
                 ("st_greedy", "ewma", "joint filter (greedy) vs EWMA"),
                 ("ewma", "ts_iid", "EWMA vs iid TS"),
                 ("dts", "ts_iid", "discounted TS vs iid TS")]
    rows = []
    for k, g in M.groupby(level="k"):
        g = g.droplevel("k")
        for a, b, lab in contrasts:
            est, lo, hi, w = boot_ratio(g, a, b)
            verdict = "a better" if hi < 0 else "b better" if lo > 0 else "inconclusive"
            rows.append({"k": k, "contrast": lab, "a": a, "b": b, "relative diff (a/b − 1)": f"{est:+.1%}",
                         "95% interval": f"{lo:+.1%} to {hi:+.1%}", "units a wins": f"{w:.0%}", "verdict": verdict})
    out += ["## Paired contrasts", "", pd.DataFrame(rows).to_markdown(index=False), ""]
    per_w = M.groupby(level=["k", "window"]).mean()[["ts_iid", "static", "ewma", "dts", "ar_ucb", "st_ucb",
                                                     "st_ucb_rewired"]].round(4).reset_index()
    out += ["## By window (mean over panels)", "", per_w.to_markdown(index=False), "",
            "## Tuned on the development window (days 20–30)", "", tuned.to_frame("value").to_markdown(), "",
            f"Unavailable picks (chosen video with no plays that day), all test runs: "
            f"{int(d.unavailable_picks.sum())} of {int(len(d) * 11)}+ slot-days.", "",
            "## Units", "", meta.to_markdown(index=False), ""]
    (RESULTS / "tables.md").write_text("\n".join(out))
    print("\n".join(out[:80]))


if __name__ == "__main__":
    main()
