"""Experiment 6: two theory instances.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct10_runs/code/theory_instances.py b2 --seeds 100 --jobs 3
    .venv/bin/python -I experiments/oct10_runs/code/theory_instances.py b3

b2 (false elimination and lasting regret). Certified successive elimination on the coverage.py
world (best arm 0.55 in component 0, next component 0.25-0.35) with AR(1) persistence phi and
bursty exposure (the selected arm is held for `batch` rounds). iid against B1'' (known
dynamics) certificates. Records whether the best arm is eliminated, when, and the regret path
at fixed checkpoints; a simulation of the mechanism, not a proof of a lower bound.

b3 (slate contrast information). Two arms observed n times, either simultaneously (a slate of
two, n rounds) or staggered (alternating, 2n rounds). Exact variance of the contrast of sample
means from the full covariance, against (i) the long-run prediction
(Omega_ii + Omega_jj - 2 Omega_ij) / n and (ii) the (1 - rho) shortcut. Cases cover equal,
unequal-variance and heterogeneous-persistence pairs; a Monte Carlo check confirms one case.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "simulations" / "certificates_under_persistence" / "code"))
import coverage as cv  # noqa: E402

RESULTS = HERE.parent / "results" / "theory_instances"
CHECKPOINTS = (1000, 2000, 5000, 10000, 20000)


def b2_run(task):
    phi, seed, policy, batch, T = task
    t0 = time.time()
    mu, labels, C, q, Y = cv.world(cv.SEED + 10_000 + seed, phi, "independent", T, shuffle=True)
    members = [np.flatnonzero(labels == c) for c in range(cv.COMP)]
    N = cv.N
    st = cv.InnovationRegression(phi, q * C, C, alpha=1.0 / N) if policy == "se_st2" else None
    sigma2 = 1.0 + cv.R_OBS ** 2
    delta = 0.05
    ell = np.log(2 * (N + cv.COMP) * T / delta)
    active = np.ones(N, bool)
    n, s = np.zeros(N), np.zeros(N)
    Nc, Sc = np.zeros(cv.COMP), np.zeros(cv.COMP)
    best = int(np.argmax(mu))
    reg = np.zeros(T)
    out_at = -1
    a = 0
    for t in range(T):
        if t % batch == 0:
            if policy == "se_iid":
                rad = np.sqrt(2 * sigma2 * ell / np.maximum(n, 1))
                lo = np.where(n > 0, s / np.maximum(n, 1) - rad, -np.inf)
                hi = np.where(n > 0, s / np.maximum(n, 1) + rad, np.inf)
                pool = np.where(Nc > 0, Sc / np.maximum(Nc, 1) + np.sqrt(2 * sigma2 * ell / np.maximum(Nc, 1)) + cv.EPS, np.inf)
            else:
                lo, hi, pool = cv.plugin_bounds(st, members, delta)
            best_lo = lo[active].max()
            for c, m in enumerate(members):
                if min(hi[m].max(), pool[c]) < best_lo:
                    active[m] = False
            active &= ~(hi < best_lo)
            if not active.any():
                active[int(np.argmax(hi))] = True
            if not active[best] and out_at < 0:
                out_at = t
            cand = np.flatnonzero(active)
            a = int(cand[np.argmin(n[cand])])
        y = Y[t, a]
        n[a] += 1
        s[a] += y
        Nc[labels[a]] += 1
        Sc[labels[a]] += y
        if st is not None:
            st.observe(a, y)
        reg[t] = mu[best] - mu[a]
    cum = np.cumsum(reg)
    row = {"phi": phi, "seed": seed, "policy": policy, "batch": batch, "best_eliminated": out_at >= 0,
           "best_eliminated_at": out_at, "regret_rate_last_2000": float(reg[-2000:].mean()),
           "seconds": round(time.time() - t0, 2)}
    for c in CHECKPOINTS:
        if c <= T:
            row[f"regret@{c}"] = float(cum[c - 1])
    return row


def b2(seeds, jobs, T):
    RESULTS.mkdir(parents=True, exist_ok=True)
    tasks = [(phi, s, p, b, T) for phi in (0.0, 0.9, 0.97) for b in (1, 10, 25, 100) for s in range(seeds)
             for p in ("se_iid", "se_st2")]
    tasks.sort(key=lambda x: (x[2] != "se_st2", x[3]))
    t0 = time.time()
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(b2_run, tasks, chunksize=4))
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "b2_runs.csv", index=False)
    print(f"b2: {len(df)} runs in {time.time() - t0:.0f}s")


# ---------------------------------------------------------------- b3

def cross_cov(phi_i, phi_j, c_ij, h):
    """Cov(z_i,t, z_j,t+h) for AR(1)s with innovation covariance c_ij, h >= 0."""
    return c_ij * phi_j ** h / (1 - phi_i * phi_j)


def contrast_var(phis, sds, rho, n, design, r=0.1):
    """Exact Var(ybar_1 - ybar_2) for n observations of each arm."""
    p1, p2 = phis
    s1, s2 = sds
    q1, q2 = s1 ** 2 * (1 - p1 ** 2), s2 ** 2 * (1 - p2 ** 2)
    c12 = rho * np.sqrt(q1 * q2)
    if design == "simultaneous":
        t1 = t2 = np.arange(n)
    else:
        t1, t2 = 2 * np.arange(n), 2 * np.arange(n) + 1
    lag11 = np.abs(t1[:, None] - t1[None, :])
    lag22 = np.abs(t2[:, None] - t2[None, :])
    S11 = s1 ** 2 * p1 ** lag11 + r ** 2 * np.eye(n)
    S22 = s2 ** 2 * p2 ** lag22 + r ** 2 * np.eye(n)
    d = t2[None, :] - t1[:, None]  # time of arm-2 obs minus arm-1 obs
    S12 = np.where(d >= 0, cross_cov(p1, p2, c12, np.abs(d)), cross_cov(p2, p1, c12, np.abs(d)))
    w = np.full(n, 1 / n)
    return float(w @ S11 @ w + w @ S22 @ w - 2 * w @ S12 @ w)


def long_run(phis, sds, rho, r=0.1):
    p1, p2 = phis
    s1, s2 = sds
    q1, q2 = s1 ** 2 * (1 - p1 ** 2), s2 ** 2 * (1 - p2 ** 2)
    O11 = q1 / (1 - p1) ** 2 + r ** 2
    O22 = q2 / (1 - p2) ** 2 + r ** 2
    O12 = rho * np.sqrt(q1 * q2) / ((1 - p1) * (1 - p2))
    return O11, O22, O12


def b3():
    RESULTS.mkdir(parents=True, exist_ok=True)
    cases = {"equal": ((0.9, 0.9), (1.0, 1.0)), "unequal_sd": ((0.9, 0.9), (1.0, 2.0)),
             "hetero_phi": ((0.9, 0.5), (1.0, 1.0)), "equal_iid": ((0.0, 0.0), (1.0, 1.0))}
    rows = []
    for name, (phis, sds) in cases.items():
        for rho in (0.0, 0.3, 0.6, 0.9):
            for n in (7, 30, 365):
                O11, O22, O12 = long_run(phis, sds, rho)
                pred = (O11 + O22 - 2 * O12) / n
                base = (O11 + O22) / n
                for design in ("simultaneous", "staggered"):
                    v = contrast_var(phis, sds, rho, n, design)
                    v0 = contrast_var(phis, sds, 0.0, n, design)
                    rows.append({"case": name, "phi1": phis[0], "phi2": phis[1], "sd1": sds[0], "sd2": sds[1],
                                 "rho": rho, "n": n, "design": design, "var_exact": v,
                                 "var_longrun_pred": pred if design == "simultaneous" else np.nan,
                                 "ratio_to_rho0": v / v0, "one_minus_rho": 1 - rho,
                                 "longrun_ratio": pred / base})
    df = pd.DataFrame(rows)
    # Monte Carlo check of the exact formula: equal case, rho = 0.6, n = 30, both designs.
    rng = np.random.default_rng(7)
    mc = []
    for design in ("simultaneous", "staggered"):
        phis, sds, rho, n = (0.9, 0.9), (1.0, 1.0), 0.6, 30
        L = np.linalg.cholesky(np.array([[1, rho], [rho, 1]]) * (1 - 0.81))
        vals = []
        for _ in range(20000):
            z = np.linalg.cholesky(np.array([[1, rho], [rho, 1]])) @ rng.standard_normal(2)
            steps = n if design == "simultaneous" else 2 * n
            zs = np.empty((steps, 2))
            for t in range(steps):
                zs[t] = z
                z = 0.9 * z + L @ rng.standard_normal(2)
            ys = zs + 0.1 * rng.standard_normal(zs.shape)
            if design == "simultaneous":
                vals.append(ys[:, 0].mean() - ys[:, 1].mean())
            else:
                vals.append(ys[0::2, 0].mean() - ys[1::2, 1].mean())
        mc.append({"design": design, "mc_var": float(np.var(vals)),
                   "exact_var": contrast_var(phis, sds, rho, n, design)})
    df.to_csv(RESULTS / "b3_contrast.csv", index=False)
    pd.DataFrame(mc).to_csv(RESULTS / "b3_montecarlo_check.csv", index=False)
    print(pd.DataFrame(mc))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["b2", "b3"])
    ap.add_argument("--seeds", type=int, default=100)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--horizon", type=int, default=20000)
    a = ap.parse_args()
    b2(a.seeds, a.jobs, a.horizon) if a.which == "b2" else b3()
