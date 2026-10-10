"""Summarize Setting B (user graphs) and Setting A v2 (KL bounds, calibrated certificates).

Usage (from the repo root):
    .venv/bin/python -I experiments/kuairec/analyze_b.py [--b-tag ""] [--b-tag _large] [--a2]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import RESULTS  # noqa: E402


def final_col(df: pd.DataFrame) -> str:
    cols = [c for c in df.columns if c.startswith("regret@") and df[c].notna().all()]
    return max(cols, key=lambda c: int(c.split("@")[1]))


def summarize_b(tag: str) -> str:
    runs = pd.read_csv(RESULTS / f"setting_b_runs{tag}.csv")
    col = final_col(runs)
    T = int(col.split("@")[1])
    key = ["instance"]
    ts = runs[runs.policy == "ts_ind"].set_index(key)[col]
    kl = runs[runs.policy == "klucb_ind"].set_index(key)[col]
    runs["ratio_ts_ind"] = runs[col].to_numpy() / ts.reindex(runs.instance).to_numpy()
    runs["ratio_klucb_ind"] = runs[col].to_numpy() / kl.reindex(runs.instance).to_numpy()
    g = runs.groupby(["policy", "graph", "param"], sort=False)
    s = g.agg(instances=(col, "size"), regret=(col, "mean"),
              ratio_ts=("ratio_ts_ind", "mean"), ratio_ts_min=("ratio_ts_ind", "min"),
              ratio_ts_max=("ratio_ts_ind", "max"), ratio_kl=("ratio_klucb_ind", "mean")).reset_index()
    s.to_csv(RESULTS / f"setting_b_summary{tag}.csv", index=False)
    n, K = int(runs.users.iloc[0]), int(runs.arms.iloc[0])
    lines = [f"Setting B{tag}: {n} users x {K} videos, T = {T:,} arrivals ({T / n:.0f} per user, "
             f"{T / n / K:.1f} per user-video pair); {s.instances.max()} instances.", "",
             "Ratios are per instance, then averaged; min and max over instances in brackets.", "",
             "| Policy | Graph | Parameter | Mean regret | Ratio to per-user TS [min, max] | Ratio to per-user KL-UCB |",
             "| --- | --- | --- | ---: | --- | ---: |"]
    for _, r in s.iterrows():
        lines.append(f"| {r.policy} | {r.graph} | {r.param} | {r.regret:,.0f} | {r.ratio_ts:.3f} "
                     f"[{r.ratio_ts_min:.3f}, {r.ratio_ts_max:.3f}] | {r.ratio_kl:.3f} |")
    return "\n".join(lines)


def summarize_a2() -> str:
    runs = pd.read_csv(RESULTS / "setting_a2_runs.csv")
    insts = pd.read_csv(RESULTS / "setting_a2_instances.csv")
    col = final_col(runs)
    T = int(col.split("@")[1])
    key = ["user", "rep"]

    def base(policy, param):
        d = runs[(runs.policy == policy) & (runs.param.astype(str) == param)].set_index(key)[col]
        return d.reindex(pd.MultiIndex.from_frame(runs[key])).to_numpy()

    runs["ratio_ts"] = runs[col].to_numpy() / base("ts", "-")
    runs["ratio_klucb_ell"] = runs[col].to_numpy() / base("klucb", "ell")
    g = runs.groupby(["policy", "graph", "param"], sort=False)
    s = g.agg(instances=(col, "size"), ratio_ts=("ratio_ts", "mean"), median_ts=("ratio_ts", "median"),
              p90_ts=("ratio_ts", lambda x: x.quantile(0.9)), beats_ts=("ratio_ts", lambda x: (x < 1).mean()),
              ratio_kl=("ratio_klucb_ell", "mean"), p90_kl=("ratio_klucb_ell", lambda x: x.quantile(0.9))
              ).reset_index()
    s.to_csv(RESULTS / "setting_a2_summary.csv", index=False)
    lines = [f"Setting A v2: 300 videos per instance, T = {T:,}; {s.instances.max()} instances "
             "(users x video subsets).", "",
             "| Policy | Graph | Parameter | Ratio to TS (mean / median / 90th pct.) | Share beating TS "
             "| Ratio to KL-UCB at fixed level (mean / 90th pct.) |",
             "| --- | --- | --- | --- | ---: | --- |"]
    for _, r in s.iterrows():
        lines.append(f"| {r.policy} | {r.graph} | {r.param} | {r.ratio_ts:.3f} / {r.median_ts:.3f} / {r.p90_ts:.2f} "
                     f"| {r.beats_ts:.2f} | {r.ratio_kl:.3f} / {r.p90_kl:.2f} |")
    cert = [c[len("valid_"):] for c in insts.columns if c.startswith("valid_")]
    lines += ["", "Certificates (means over instances and graphs):", "",
              "| Certificate | Share of components valid | Share of suboptimal components rejectable | Mean width |",
              "| --- | ---: | ---: | ---: |"]
    for c in cert:
        lines.append(f"| {c} | {insts[f'valid_{c}'].mean():.2f} | {insts[f'rejectable_{c}'].mean():.2f} "
                     f"| {insts[f'mean_width_{c}'].mean():.3f} |")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--b-tag", action="append", default=[])
    ap.add_argument("--a2", action="store_true")
    a = ap.parse_args()
    for tag in a.b_tag:
        text = summarize_b(tag)
        (RESULTS / f"setting_b_table{tag}.md").write_text(text + "\n")
        print(text, "\n")
    if a.a2:
        text = summarize_a2()
        (RESULTS / "setting_a2_table.md").write_text(text + "\n")
        print(text)
