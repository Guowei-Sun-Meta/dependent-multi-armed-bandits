"""LinUCB and linear Thompson sampling on item embeddings, KuaiRec Setting A v2.

Usage (from the repo root; needs data/kuairec_cache):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct12_baselines/code/lin_setting_a.py --jobs 5

The founding WWW bandit baseline (Li et al., WWW 2010) pools across arms through features
rather than a graph. Each video's context is its leakage-free I-mf embedding (PureSVD from
non-evaluation users, 64 dimensions), row-normalized, optionally projected onto the instance's
top-d principal directions, plus an intercept. Bernoulli rewards; ridge prior lambda = 1.
- lints (sigma): posterior N(A^-1 b, sigma^2 A^-1), one draw per round.
- linucb (alpha): x'theta_hat + alpha * sqrt(x' A^-1 x).
- kerts (tau2, with s2 = 4 tau2): hybrid model mean_i = x_i'beta + gamma_i (Li et al.'s hybrid
  idea; here as a Gaussian prior over item means with covariance tau2 I + s2 X X', centred on the
  platform average 0.18), noise variance 0.25, marginal Thompson sampling (as Spectral TS in
  setting_a.py). It is the feature-based counterpart of graph-based Spectral TS.
Hyperparameters (sigma or alpha, and d) are tuned on 30 tuning users (one subset each), then
frozen and run on the 360 test instances of Setting A v2. Instances and common random numbers
reproduce kuairec/code/setting_a2.py exactly, so results pair with its runs.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "kuairec" / "code"))
import setting_a2 as a2  # noqa: E402

RESULTS = HERE.parent / "results"
K, T = 300, 20000
POLICIES = ("lints", "linucb", "kerts")
GRID = [("lints", s, d) for s in (0.1, 0.25, 0.5) for d in (16, 64)] + \
       [("linucb", a, d) for a in (0.1, 0.25, 0.5, 1.0) for d in (16,)] + \
       [("kerts", tau2, d) for tau2 in (0.005, 0.02, 0.05) for d in (16, 64)]


def instance(u_idx, rep):
    feats, M, tune_users, _ = a2.cached()
    rng = np.random.default_rng(a2.SEED + 1000 * rep + u_idx)
    avail = np.flatnonzero(~np.isnan(M[u_idx]))
    nodes = np.sort(rng.choice(avail, size=K, replace=False))
    mu = M[u_idx, nodes].astype(np.float64)
    U = rng.random((K, T))
    X = feats["I-mf"][1][nodes].astype(np.float64)
    return mu, U, X


def design(X, d):
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    if d < X.shape[1]:
        Xc = X - X.mean(0)
        _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
        X = X @ Vt[:d].T
    return np.hstack([X, np.ones((len(X), 1))])


def run(task):
    u_idx, rep, policy, param, d = task
    t0 = time.time()
    mu, U, X0 = instance(u_idx, rep)
    X = design(X0, d)
    p = X.shape[1]
    if policy == "kerts":
        return run_kerts(u_idx, rep, param, d, mu, U, X, t0)
    Ainv = np.eye(p)
    b = np.zeros(p)
    n = np.zeros(K, dtype=int)
    rng = np.random.default_rng([a2.SEED, u_idx, rep, d, int(param * 1000)])
    best = mu.max()
    reg = np.zeros(T)
    for t in range(T):
        theta = Ainv @ b
        if policy == "lints":
            L = np.linalg.cholesky((Ainv + Ainv.T) / 2 + 1e-12 * np.eye(p))
            score = X @ (theta + param * (L @ rng.standard_normal(p)))
        else:
            score = X @ theta + param * np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", X, Ainv, X), 0))
        a = int(np.argmax(score))
        r = float(U[a, n[a]] < mu[a])
        n[a] += 1
        x = X[a]
        Ax = Ainv @ x
        Ainv -= np.outer(Ax, Ax) / (1 + x @ Ax)
        b += r * x
        reg[t] = best - mu[a]
    cum = np.cumsum(reg)
    row = {"user": u_idx, "rep": rep, "policy": policy, "param": param, "d": d,
           "seconds": round(time.time() - t0, 1)}
    for c in a2.CHECKPOINTS:
        if c <= T:
            row[f"regret@{c}"] = float(cum[c - 1])
    return row


def run_kerts(u_idx, rep, tau2, d, mu, U, X, t0):
    noise = 0.25
    P = tau2 * np.eye(K) + 4 * tau2 * (X @ X.T) / X.shape[1]
    m = np.full(K, 0.18)
    n = np.zeros(K, dtype=int)
    rng = np.random.default_rng([a2.SEED, u_idx, rep, d, int(tau2 * 1e4), 7])
    best = mu.max()
    reg = np.zeros(T)
    for t in range(T):
        score = m + np.sqrt(np.maximum(np.diag(P), 0)) * rng.standard_normal(K)
        a = int(np.argmax(score))
        r = float(U[a, n[a]] < mu[a])
        n[a] += 1
        col = P[:, a].copy()
        denom = noise + col[a]
        m += col * (r - m[a]) / denom
        P -= np.outer(col, col) / denom
        reg[t] = best - mu[a]
    cum = np.cumsum(reg)
    row = {"user": u_idx, "rep": rep, "policy": "kerts", "param": tau2, "d": d,
           "seconds": round(time.time() - t0, 1)}
    for c in a2.CHECKPOINTS:
        if c <= T:
            row[f"regret@{c}"] = float(cum[c - 1])
    return row


def main(jobs, n_tune, n_users, subsets):
    RESULTS.mkdir(parents=True, exist_ok=True)
    _, _, tune_users, test_users = a2.cached()
    t0 = time.time()
    tune_tasks = [(int(u), 0, pol, prm, d) for u in tune_users[:n_tune] for pol, prm, d in GRID]
    with ProcessPoolExecutor(jobs) as ex:
        tune = pd.DataFrame(list(ex.map(run, tune_tasks, chunksize=2)))
    tune.to_csv(RESULTS / "lin_setting_a_tuning.csv", index=False)
    best = {}
    for pol in POLICIES:
        g = tune[tune.policy == pol].groupby(["param", "d"])["regret@20000"].mean()
        prm, d = g.idxmin()
        best[pol] = {"param": float(prm), "d": int(d), "tuning_mean_regret": float(g.min())}
    (RESULTS / "lin_setting_a_tuned.json").write_text(json.dumps(best, indent=1))
    print("tuned:", best, f"{time.time() - t0:.0f}s", flush=True)
    test_tasks = [(int(u), rep, pol, best[pol]["param"], best[pol]["d"])
                  for rep in range(subsets) for u in test_users[:n_users] for pol in POLICIES]
    with ProcessPoolExecutor(jobs) as ex:
        test = pd.DataFrame(list(ex.map(run, test_tasks, chunksize=2)))
    test.to_csv(RESULTS / "lin_setting_a_runs.csv", index=False)
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("--tune-users", type=int, default=30)
    ap.add_argument("--users", type=int, default=120)
    ap.add_argument("--subsets", type=int, default=3)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    if a.pilot:
        _, _, tu, te = a2.cached()
        for task in [(int(te[0]), 0, "kerts", 0.02, 16), (int(te[0]), 0, "kerts", 0.005, 64)]:
            print(run(task))
    else:
        main(a.jobs, a.tune_users, a.users, a.subsets)
