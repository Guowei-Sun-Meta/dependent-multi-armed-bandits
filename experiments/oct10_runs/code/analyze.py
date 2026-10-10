"""Tables for the 10 October runs: robustness (4), theory instances (6), OBD pooling (8b).

Usage (from the repo root):
    .venv/bin/python -I experiments/oct10_runs/code/analyze.py
Writes results/<experiment>/tables.md. Shares carry 95% Wilson intervals; regrets are
means with standard errors over seeds.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path(__file__).resolve().parents[1] / "results"


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def share(s):
    k, n = int(s.sum()), int(s.count())
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({lo:.2f}–{hi:.2f})" if k else f"0/{n} (0–{hi:.2f})"


def md(df):
    return df.to_markdown(index=False) if hasattr(df, "to_markdown") else df.to_string(index=False)


def robustness():
    f = RESULTS / "robustness" / "runs.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    out = ["# Experiment 4: certificates with estimated and misspecified dynamics", "",
           "Share of runs with any certificate violation (an arm or component upper bound below its "
           "target at some round), 95% Wilson interval. SP-UCB checks every round; successive "
           "elimination (SE) checks at decisions. For SE, `best out` is the share of runs that "
           "eliminated the best arm.", ""]
    order = ["known", "fit365", "fit100", "fit100_cons", "phi_bias", "ignore_corr", "t3", "ar7_as_ar1"]
    for config in ("independent", "correlated"):
        for batch in sorted(d.batch.unique()):
            sub = d[(d.config == config) & (d.batch == batch)]
            out.append(f"## {config} shocks, exposure batch {batch}")
            out.append("")
            rows = []
            for policy in ("sp_ucb_st2", "se_st2", "sp_ucb_iid", "se_iid"):
                for cond in order:
                    s = sub[(sub.policy == policy) & (sub.condition == cond)]
                    if s.empty:
                        continue
                    r = {"policy": policy, "condition": cond}
                    for phi, g in s.groupby(s.phi.fillna(-1)):
                        lab = "AR(7)" if phi < 0 or cond == "ar7_as_ar1" else f"φ={phi:g}"
                        r[f"{lab} violation"] = share(g.any_violation)
                        if policy.startswith("se"):
                            r[f"{lab} best out"] = share(g.best_eliminated.astype(bool))
                        r[f"{lab} regret"] = f"{g.regret.mean():.0f}"
                        if policy.endswith("st2") and cond.startswith("fit"):
                            r[f"{lab} φ̂"] = f"{g.phi_learner.median():.3f}"
                    rows.append(r)
            out.append(md(pd.DataFrame(rows).fillna("")))
            out.append("")
    (RESULTS / "robustness" / "tables.md").write_text("\n".join(out))
    print("\n".join(out[:60]))


def theory():
    f = RESULTS / "theory_instances" / "b2_runs.csv"
    out = ["# Experiment 6: theory instances", ""]
    if f.exists():
        d = pd.read_csv(f)
        out += ["## B2: false elimination and lasting regret", "",
                "Certified successive elimination, known dynamics for `se_st2` (B1''). "
                "`best out`: share of runs that eliminated the best arm (95% Wilson). "
                "`late rate`: mean per-round regret over the last 2,000 of 20,000 rounds; "
                "a positive late rate is linear regret.", ""]
        rows = []
        for (phi, batch, pol), g in d.groupby(["phi", "batch", "policy"]):
            elim = g[g.best_eliminated]
            rows.append({"φ": phi, "batch": batch, "policy": pol, "best out": share(g.best_eliminated),
                         "median time out": f"{elim.best_eliminated_at.median():.0f}" if len(elim) else "",
                         "regret@2k": f"{g['regret@2000'].mean():.0f}", "regret@20k": f"{g['regret@20000'].mean():.0f}",
                         "late rate (all)": f"{g.regret_rate_last_2000.mean():.3f}",
                         "late rate | best out": f"{elim.regret_rate_last_2000.mean():.3f}" if len(elim) else ""})
        out += [md(pd.DataFrame(rows)), ""]
    f = RESULTS / "theory_instances" / "b3_contrast.csv"
    if f.exists():
        d = pd.read_csv(f)
        out += ["## B3: slate contrast information", "",
                "Variance of the contrast of two arms' sample means at shock correlation ρ, relative to "
                "ρ = 0 (smaller is better), n = 365 observations of each arm. `1−ρ` is the shortcut; "
                "`long-run` uses (Ω_ii + Ω_jj − 2Ω_ij) / (Ω_ii + Ω_jj).", ""]
        s = d[d.n == 365]
        piv = s.pivot_table(index=["case", "rho"], columns="design", values="ratio_to_rho0").reset_index()
        lr = s[s.design == "simultaneous"].set_index(["case", "rho"])[["one_minus_rho", "longrun_ratio"]].reset_index()
        piv = piv.merge(lr, on=["case", "rho"]).round(3)
        piv = piv.rename(columns={"one_minus_rho": "1−ρ", "longrun_ratio": "long-run"})
        out += [md(piv), ""]
        s7 = d[(d.design == "simultaneous")].copy()
        s7["exact / long-run"] = s7.var_exact / s7.var_longrun_pred
        p2 = s7[s7.rho == 0.6].pivot_table(index="case", columns="n", values="exact / long-run").round(3).reset_index()
        out += ["Finite-n exact variance over the long-run prediction (simultaneous, ρ = 0.6). "
                "Below 1: the long-run formula overstates the variance of short persistent runs.", "",
                md(p2), ""]
        mc = pd.read_csv(RESULTS / "theory_instances" / "b3_montecarlo_check.csv").round(4)
        out += ["Monte Carlo check (equal pair, φ = 0.9, ρ = 0.6, n = 30, 20,000 draws):", "", md(mc), ""]
    (RESULTS / "theory_instances" / "tables.md").write_text("\n".join(out))
    print("\n".join(out))


def obd():
    f = RESULTS / "obd_pooling" / "runs.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    inst = pd.read_csv(RESULTS / "obd_pooling" / "instance.csv")
    out = ["# Experiment 8b: certified pooling on Open Bandit Dataset click rates", "",
           "Semi-synthetic: true means are day 4–7 click rates; components and the prefix certificate "
           "use days 1–3 only. Regret in clicks lost against always showing the best item; blocks of 100 "
           "impressions per decision. Mean ± standard error over seeds.", "", "## Instance", "",
           md(inst.round(5)), ""]
    cps = [c for c in ("regret@500000", "regret@1000000", "regret@2000000") if c in d.columns]
    for camp, g in d.groupby("campaign"):
        base = g[g.policy == "klucb_ell"].set_index("seed")["regret@2000000"]
        rows = []
        for (p, gr, w), h in g.groupby(["policy", "graph", "width"], sort=False):
            r = {"policy": p, "graph": gr, "width": w}
            for c in cps:
                r[c.replace("regret@", "T=")] = f"{h[c].mean():.0f} ± {h[c].std(ddof=1) / np.sqrt(len(h)):.0f}"
            ratio = h.set_index("seed")["regret@2000000"] / base
            r["÷ klucb_ell (paired)"] = f"{ratio.mean():.2f}"
            r["p90 ÷ klucb_ell"] = f"{ratio.quantile(.9):.2f}"
            r["best share, last 10%"] = f"{h.best_share_last_10pct.mean():.2f}"
            rows.append(r)
        out += [f"## Campaign: {camp}", "", md(pd.DataFrame(rows)), ""]
    (RESULTS / "obd_pooling" / "tables.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    theory()
    robustness()
    obd()
