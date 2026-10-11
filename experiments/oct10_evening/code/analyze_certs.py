"""Tables for experiment 3b (certificates_real.py), plus the certificate-width diagnostic.

Usage (from the repo root):
    .venv/bin/python -I experiments/oct10_evening/code/analyze_certs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import certificates_real as cr  # noqa: E402

RESULTS = HERE.parent / "results" / "certificates_real"


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(c - h, 0), c + h


def share(s):
    k, n = int(s.sum()), int(s.count())
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({lo:.2f}–{hi:.2f})"


def widths(seeds=5):
    """Median arm interval width after 365 and 730 days of random 5-article slates (known model):
    B1'' plug-in, the log-determinant ellipsoid, and the posterior sd (no anytime correction)."""
    c = cr.cal()
    mu, labels, coef, E, Q = c["mu"], c["labels"], c["coef"], c["E"], c["Q"]
    N = len(mu)
    members = [np.flatnonzero(labels == j) for j in range(labels.max() + 1)]
    eps = np.array([np.ptp(mu[m]) for m in members])
    rows = []
    for s in range(seeds):
        Y = mu + cr.simulate(100 + s, 730, "resample", coef, E, Q)
        st = cr.InnovationAR(coef, Q, 1 / N)
        rng = np.random.default_rng(s)
        for t in range(730):
            for a in rng.choice(N, 5, replace=False):
                st.observe(int(a), Y[t, a])
            st.propagate()
            if t + 1 in (365, 730):
                lo, hi, _ = cr.plugin_bounds(st, members, eps, 0.05)
                Jinv = np.linalg.inv(st.J)
                beta = np.sqrt(np.linalg.slogdet(st.J)[1] - N * np.log(1 / N) + 2 * np.log(1 / 0.05)) + 1.0
                sd = np.sqrt(np.diag(Jinv))
                rows.append({"seed": s, "day": t + 1, "plugin_B1pp": np.median(hi - lo),
                             "ellipsoid": np.median(2 * beta * sd), "pointwise_2sd": np.median(4 * sd),
                             "beta": beta})
    w = pd.DataFrame(rows).groupby("day").median().drop(columns="seed").reset_index()
    w["spread_of_means_sd"] = mu.std()
    w["gap_best_to_2nd"] = np.sort(mu)[-1] - np.sort(mu)[-2]
    return w


def main():
    d = pd.read_csv(RESULTS / "runs.csv")
    out = ["# Experiment 3b: certified pooling in worlds calibrated to Wikipedia attention", "",
           "30 articles (5 per community), AR(7) fitted on 2022–2023, horizon 730 days, 100 worlds per cell. "
           "`violation`: any arm or component upper bound below its target on some day (95% Wilson). "
           "`best out`: successive elimination dropped the best article. Regret is mean regret over 730 days "
           "(rescaled log-views, slate of k).", ""]
    rows = []
    for (noise, policy, k, learner), g in d.groupby(["noise", "policy", "k", "learner"]):
        rows.append({"innovations": noise, "policy": {"sp": "SP-UCB", "se": "elimination"}[policy], "k": k,
                     "learner": learner, "violation": share(g.any_violation),
                     "best out": share(g.best_eliminated.astype(bool)) if policy == "se" else "",
                     "regret@730": f"{g['regret@730'].mean():.0f}", "active at end": f"{g.active_at_end.mean():.1f}"})
    out += [pd.DataFrame(rows).to_markdown(index=False), ""]
    w = widths()
    w.to_csv(RESULTS / "widths.csv", index=False)
    out += ["## Why the valid certificates never decide: interval widths", "",
            "Median arm interval width with the true model, random 5-article slates, 5 worlds. Means lie in "
            "[0, 1]. `pointwise_2sd` is ±2 posterior sd with no anytime or simultaneity correction.", "",
            w.round(4).to_markdown(index=False), ""]
    (RESULTS / "tables.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
