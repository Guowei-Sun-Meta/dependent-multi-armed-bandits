"""Experiment 3a: variance inflation of block means on real Wikipedia attention.

Usage (from the repo root):
    .venv/bin/python -I experiments/oct10_runs/code/inflation.py

Does a b-day block of consecutive observations carry less information about an article's level
than b iid days would, and does a prefix fit predict how much? For each article,
x_t = log(1 + views_t). Fit on 2022-2023 (prefix), observe on 2024-2025 (test).

Inflation(b) = Var(mean of a b-day block) / (Var(x_t) / b); 1 means iid.
- observed: non-overlapping b-day blocks in the test window, after removing the article's test
  mean (variant "level"), or also the prefix-estimated weekday profile (variant "weekday").
- predicted from the prefix, with the full autocovariance formula
      Var(xbar_b) = gamma(0)/b [1 + 2 sum_{h<b} (1 - h/b) rho(h)],
  using (i) the AR(1) shortcut rho(h) = rho(1)^h, (ii) the ACF implied by OLS AR(7) and AR(20)
  fits, and (iii) the empirical prefix ACF.
Caveat: the panels were selected retrospectively on 2022-2025 completeness and popularity
(experiment 1 fixes this); this is a diagnostic of the dynamics, not policy evidence.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "experiments" / "wikipedia" / "data"
RESULTS = Path(__file__).resolve().parents[1] / "results" / "inflation"
BLOCKS = (1, 3, 7, 14, 28)


def inflation_from_acf(rho, b):
    h = np.arange(1, b)
    return 1 + 2 * ((1 - h / b) * rho[h]).sum() if b > 1 else 1.0


def acf(x, H):
    x = x - x.mean()
    g0 = (x * x).mean()
    return np.array([1.0] + [(x[h:] * x[:-h]).mean() / g0 for h in range(1, H + 1)])


def ar_fit_acf(x, p, H):
    """OLS AR(p) on demeaned x; return the implied ACF up to lag H (via a long simulation-free
    Yule-Walker recursion on the impulse response)."""
    x = x - x.mean()
    X = np.column_stack([x[p - k - 1:len(x) - k - 1] for k in range(p)])
    y = x[p:]
    a, *_ = np.linalg.lstsq(X, y, rcond=None)
    # Stationarity check: companion matrix spectral radius.
    comp = np.zeros((p, p))
    comp[0] = a
    if p > 1:
        comp[1:, :-1] = np.eye(p - 1)
    radius = float(np.abs(np.linalg.eigvals(comp)).max())
    if radius >= 0.999:
        return None, radius
    L = 3000
    psi = np.zeros(L)
    psi[0] = 1.0
    for t in range(1, L):
        psi[t] = sum(a[k] * psi[t - 1 - k] for k in range(min(p, t)))
    g = np.array([(psi[: L - h] * psi[h:]).sum() for h in range(H + 1)])
    return g / g[0], radius


def block_inflation(x, b):
    m = len(x) // b
    if m < 8:
        return np.nan
    blocks = x[: m * b].reshape(m, b).mean(1)
    return float(blocks.var(ddof=1) / (x.var(ddof=1) / b))


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    H = max(BLOCKS)
    for panel in ("one_domain", "six_domains"):
        v = pd.read_csv(DATA / panel / "views.csv", index_col=0)
        v.index = pd.to_datetime(v.index.astype(str), format="%Y%m%d")
        X = np.log1p(v)
        pre, test = X[X.index.year <= 2023], X[X.index.year >= 2024]
        for art in X.columns:
            xp, xt = pre[art].to_numpy(), test[art].to_numpy()
            wd_p = pre[art].groupby(pre.index.weekday).mean()
            wd_p = wd_p - wd_p.mean()
            variants = {"level": (xp - xp.mean(), xt - xt.mean())}
            xp2 = xp - wd_p.reindex(pre.index.weekday).to_numpy()
            xt2 = xt - wd_p.reindex(test.index.weekday).to_numpy()
            variants["weekday"] = (xp2 - xp2.mean(), xt2 - xt2.mean())
            for var, (a, b_) in variants.items():
                r_emp = acf(a, H)
                r_ar1 = r_emp[1] ** np.arange(H + 1)
                r7, rad7 = ar_fit_acf(a, 7, H)
                r20, rad20 = ar_fit_acf(a, 20, H)
                for b in BLOCKS:
                    rows.append({"panel": panel, "article": art, "variant": var, "b": b,
                                 "rho1_prefix": r_emp[1], "observed": block_inflation(b_, b),
                                 "pred_ar1": inflation_from_acf(r_ar1, b),
                                 "pred_ar7": inflation_from_acf(r7, b) if r7 is not None else np.nan,
                                 "pred_ar20": inflation_from_acf(r20, b) if r20 is not None else np.nan,
                                 "pred_empirical_acf": inflation_from_acf(r_emp, b),
                                 "ar20_radius": rad20})
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "per_article.csv", index=False)
    preds = ["pred_ar1", "pred_ar7", "pred_ar20", "pred_empirical_acf"]
    summ = df.groupby(["panel", "variant", "b"]).agg(
        articles=("observed", "count"), rho1_median=("rho1_prefix", "median"),
        observed_median=("observed", "median"), observed_q25=("observed", lambda s: s.quantile(.25)),
        observed_q75=("observed", lambda s: s.quantile(.75)),
        **{f"{p}_median": (p, "median") for p in preds}).reset_index()
    # Calibration: median log ratio observed / predicted, and share of articles under-predicted.
    for p in preds:
        lr = np.log(df["observed"] / df[p])
        df[f"lr_{p}"] = lr
        df[f"under_{p}"] = df["observed"] > df[p]
    cal = df[df.b > 1].groupby(["panel", "variant", "b"]).agg(
        **{f"median_obs_over_{p[5:]}": (f"lr_{p}", lambda s: float(np.exp(s.median()))) for p in preds},
        **{f"share_underpredicted_{p[5:]}": (f"under_{p}", "mean") for p in preds}).reset_index()
    summ.to_csv(RESULTS / "summary.csv", index=False)
    cal.to_csv(RESULTS / "calibration.csv", index=False)
    pd.set_option("display.width", 250)
    print(summ.round(2).to_string())
    print(cal.round(2).to_string())


if __name__ == "__main__":
    main()
