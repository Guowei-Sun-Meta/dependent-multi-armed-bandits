"""Experiment 8a: Open Bandit Dataset feasibility check (uniform-random logs only).

Usage (from the repo root; data unzipped into data/obd/open_bandit_dataset/):
    .venv/bin/python -I experiments/oct10_runs/code/obd_feasibility.py

For each campaign (all, men, women) of the uniform-random logs:
1. Support and chronology: rows, items, positions, time range, propensities.
2. Is there a ranking to learn? Item click rates (CTR) against their sampling error: a
   method-of-moments random-effects variance tau^2, and split-half reliability (days 1-3 against
   days 4-7: the split the calibrated instance would use for graph and truth).
3. Position effects.
4. Do item click rates move over time beyond binomial noise? Pearson dispersion of item x bin
   click counts against the expectation n_ib * p_i * f_b (item and bin main effects), for daily
   and 6-hour bins, with a parametric-bootstrap null; lag-1 autocorrelation of standardized
   item-day residuals.
5. Audience-response graph support: clicks per item x user_feature_0 segment.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "obd" / "open_bandit_dataset" / "random"
RESULTS = Path(__file__).resolve().parents[1] / "results" / "obd_feasibility"
RNG = np.random.default_rng(20261010)


def load(campaign):
    df = pd.read_csv(DATA / campaign / f"{campaign}.csv",
                     usecols=["timestamp", "item_id", "position", "click", "propensity_score", "user_feature_0"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="ISO8601")
    df["day"] = (df["timestamp"] - df["timestamp"].min().normalize()).dt.days
    df["bin6h"] = df["day"] * 4 + df["timestamp"].dt.hour // 6
    return df


def random_effects(clicks, imps):
    p = clicks / imps
    pbar = clicks.sum() / imps.sum()
    samp = (pbar * (1 - pbar) / imps).mean()
    tau2 = max(p.var(ddof=1) - samp, 0.0)
    return float(pbar), float(np.sqrt(tau2)), float(np.sqrt(samp)), float(tau2 / (tau2 + samp))


def dispersion(df, bin_col, n_boot=200):
    """Pearson chi^2 / df of item x bin clicks given item and bin main effects (Poisson approx.)."""
    g = df.groupby(["item_id", bin_col]).agg(n=("click", "size"), k=("click", "sum")).reset_index()
    items = g.item_id.unique()
    bins = g[bin_col].unique()
    # Fit multiplicative main effects by iterative proportional fitting on the expected counts.
    p = g.groupby("item_id").k.sum() / g.groupby("item_id").n.sum()
    f = pd.Series(1.0, index=bins)
    for _ in range(50):
        e = g.n * g.item_id.map(p) * g[bin_col].map(f)
        f = f * (g.k.groupby(g[bin_col]).sum() / e.groupby(g[bin_col]).sum())
        e = g.n * g.item_id.map(p) * g[bin_col].map(f)
        p = p * (g.k.groupby(g.item_id).sum() / e.groupby(g.item_id).sum())
    e = (g.n * g.item_id.map(p) * g[bin_col].map(f)).to_numpy()
    k = g.k.to_numpy()
    dof = len(g) - len(items) - len(bins) + 1
    stat = float(((k - e) ** 2 / e).sum() / dof)
    # Parametric bootstrap under no item x bin interaction (binomial draws at the fitted rates).
    rate = np.clip(e / g.n.to_numpy(), 0, 1)
    null = []
    for _ in range(n_boot):
        kb = RNG.binomial(g.n.to_numpy(), rate)
        null.append(((kb - e) ** 2 / e).sum() / dof)
    null = np.array(null)
    resid = (k - e) / np.sqrt(e)
    g["resid"] = resid
    return stat, float(np.quantile(null, 0.95)), float((null >= stat).mean()), g


def lag1(g, bin_col):
    piv = g.pivot(index=bin_col, columns="item_id", values="resid").sort_index()
    a, b = piv.iloc[:-1].to_numpy().ravel(), piv.iloc[1:].to_numpy().ravel()
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[m], b[m])[0, 1])


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    summary, items_out = {}, []
    for campaign in ("all", "men", "women"):
        df = load(campaign)
        out = {"rows": int(len(df)), "items": int(df.item_id.nunique()),
               "positions": sorted(int(x) for x in df.position.unique()),
               "start": str(df.timestamp.min()), "end": str(df.timestamp.max()),
               "days": int(df.day.max() + 1), "clicks": int(df.click.sum()),
               "ctr": float(df.click.mean()),
               "propensities": sorted(round(float(x), 6) for x in df.propensity_score.unique())[:5]}
        it = df.groupby("item_id").click.agg(["sum", "size"])
        out["clicks_per_item"] = {"median": float(it["sum"].median()), "min": int(it["sum"].min()),
                                  "max": int(it["sum"].max())}
        pbar, tau, se, rel = random_effects(it["sum"].to_numpy(), it["size"].to_numpy())
        out["item_ctr"] = {"mean": pbar, "between_item_sd": tau, "mean_sampling_se": se,
                           "reliability_of_7day_ctr": rel, "sd_over_se": tau / se if se else None}
        # Split-half: days 1-3 (graph / calibration) against days 4-7 (truth).
        a = df[df.day < 3].groupby("item_id").click.agg(["sum", "size"])
        b = df[df.day >= 3].groupby("item_id").click.agg(["sum", "size"])
        j = a.join(b, lsuffix="_a", rsuffix="_b").dropna()
        ra, rb = j.sum_a / j.size_a, j.sum_b / j.size_b
        _, _, _, rel_b = random_effects(j.sum_b.to_numpy(), j.size_b.to_numpy())
        out["split_half"] = {"pearson": float(np.corrcoef(ra, rb)[0, 1]),
                             "spearman": float(ra.rank().corr(rb.rank())),
                             "reliability_days4to7": rel_b,
                             "top_item_same": bool(ra.idxmax() == rb.idxmax())}
        # Gap structure in the "truth" (days 4-7): gaps of the top 10 to the best, in SE units.
        se_b = np.sqrt(rb * (1 - rb) / j.size_b)
        top = rb.sort_values(ascending=False)
        out["truth_gaps"] = {"best_ctr": float(top.iloc[0]),
                             "gap_to_2nd": float(top.iloc[0] - top.iloc[1]),
                             "gap_to_5th": float(top.iloc[0] - top.iloc[min(4, len(top) - 1)]),
                             "median_se_days4to7": float(se_b.median())}
        pos = df.groupby("position").click.agg(["mean", "size"])
        out["position_ctr"] = {int(k): float(v) for k, v in pos["mean"].items()}
        for bin_col in ("day", "bin6h"):
            stat, q95, pval, g = dispersion(df, bin_col)
            out[f"dispersion_{bin_col}"] = {"pearson_over_df": stat, "null_q95": q95, "p_value": pval,
                                            "lag1_resid_autocorr": lag1(g, bin_col),
                                            "median_clicks_per_item_bin": float(g.k.median())}
        seg = df.groupby(["item_id", "user_feature_0"]).click.sum()
        out["segments_user_feature_0"] = {"segments": int(df.user_feature_0.nunique()),
                                          "median_clicks_per_item_segment": float(seg.median()),
                                          "share_item_segments_with_ge5_clicks": float((seg >= 5).mean())}
        summary[campaign] = out
        it = it.assign(campaign=campaign, ctr=it["sum"] / it["size"]).reset_index()
        items_out.append(it.rename(columns={"sum": "clicks", "size": "impressions"}))
        print(campaign, json.dumps(out, indent=1), flush=True)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=1))
    pd.concat(items_out).to_csv(RESULTS / "item_ctr.csv", index=False)


if __name__ == "__main__":
    main()
