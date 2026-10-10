"""Setting A v2: one user, K videos, an item graph on those videos; fairer baselines and
calibrated certificates.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/kuairec/setting_a2.py \
        --users 120 --subsets 3 --horizon 20000 --jobs 7

Changes from setting_a.py (v1):
- KL-based confidence bounds (Bernoulli), removing the sigma = 0.5 handicap of UCB1:
  klucb (level log t, the usual practical index) and klucb_ell (fixed level
  ell = log(2(K+M)T/delta), the same level the certified policy uses).
- sp_klucb: SP-UCB with KL bounds for both the arm and the pooled component index. The
  Chernoff bound in KL form holds for averages of independent [0, 1] rewards with
  different means, so the pooled bound stays valid for the average of pulled arms' means.
- Calibrated certificates: a component's width is the q-quantile (q = 0.9 or 0.5), over
  the tuning users, of that component's within-component range of true means. It uses
  only other users' data, as a platform calibrating on historical users would.
- shrink_ts: Gaussian TS on the complete graph, a graph-free shrinkage control.
- Several video subsets per user.
"""

from __future__ import annotations

import argparse
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import RESULTS, load_eval  # noqa: E402
from graphs import build, load_features, rewire, scaled_laplacian  # noqa: E402
from setting_a import certificates, partition, run_spectral, run_ts  # noqa: E402

SEED = 20261009
COMPONENTS = 20
QUANTILES = (0.9, 0.5)
GRAPH_NAMES = ("I-mf", "I-coeng", "I-tag", "I-mf~rewired")
CHECKPOINTS = (100, 500, 1000, 2000, 5000, 10000, 20000, 50000)


# ---------------------------------------------------------------- KL bounds


def kl_bern(p, q):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    q = np.clip(q, 1e-12, 1 - 1e-12)
    return p * np.log(p / q) + (1 - p) * np.log((1 - p) / (1 - q))


def kl_upper(phat, n, level, iters: int = 30):
    """Largest q >= phat with n * kl(phat, q) <= level; +inf where n = 0. Vectorized."""
    phat, n = np.asarray(phat, float), np.asarray(n, float)
    lo, hi = phat.copy(), np.ones_like(phat)
    for _ in range(iters):
        mid = (lo + hi) / 2
        ok = n * kl_bern(phat, mid) <= level
        lo = np.where(ok, mid, lo)
        hi = np.where(ok, hi, mid)
    return np.where(n > 0, lo, np.inf)


# ---------------------------------------------------------------- policies


def run_klucb(mu, U, T, fixed_level=None):
    K = len(mu)
    n, s = np.zeros(K), np.zeros(K)
    regret, best = np.zeros(T), mu.max()
    idx = np.full(K, np.inf)
    for t in range(T):
        if fixed_level is None:
            idx = kl_upper(s / np.maximum(n, 1), n, np.log(max(t, 1)))
        a = int(np.argmax(idx))
        s[a] += U[a, int(n[a])] < mu[a]
        n[a] += 1
        if fixed_level is not None:
            idx[a] = kl_upper(s[a:a + 1] / n[a], n[a:a + 1], fixed_level)[0]
        regret[t] = best - mu[a]
    return regret


def run_sp_klucb(mu, U, T, labels, widths, level, warm=False):
    """SP-UCB with KL bounds. If `widths` is callable, the first K rounds pull every arm once
    and the widths are then computed from those warm-up rewards (charged to regret)."""
    K, C = len(mu), labels.max() + 1
    members = [np.flatnonzero(labels == c) for c in range(C)]
    n, s = np.zeros(K), np.zeros(K)
    Nc, Sc = np.zeros(C), np.zeros(C)
    arm_up = np.full(K, np.inf)
    pool_up = np.full(C, np.inf)
    regret, best = np.zeros(T), mu.max()
    n_init = K if callable(widths) else C
    for t in range(T):
        if callable(widths) and t == K:
            widths = widths(s.sum() / n.sum())
        if t < n_init:
            a = t if n_init == K else int(members[t][0])
        else:
            best_val, a = -np.inf, -1
            for c in range(C):
                m = members[c]
                i = m[np.argmax(arm_up[m])]
                val = min(arm_up[i], pool_up[c] + widths[c])
                if val > best_val:
                    best_val, a = val, int(i)
        r = float(U[a, int(n[a])] < mu[a])
        c = labels[a]
        n[a] += 1
        s[a] += r
        Nc[c] += 1
        Sc[c] += r
        arm_up[a] = kl_upper(np.array([s[a] / n[a]]), np.array([n[a]]), level)[0]
        pool_up[c] = kl_upper(np.array([Sc[c] / Nc[c]]), np.array([Nc[c]]), level)[0]
        regret[t] = best - mu[a]
    return regret


def complete_laplacian(K: int) -> sp.csr_matrix:
    return sp.csr_matrix((K * np.eye(K) - np.ones((K, K))) / (K - 1))


def calibrated_user(M_tune: np.ndarray, labels: np.ndarray, q: float, k: int = 100):
    """Per-user calibration: the q-quantile of within-component ranges over the k tuning users
    whose average reward on these videos is closest to the user's warm-up average."""
    C = labels.max() + 1
    levels = np.nanmean(M_tune, axis=1)
    ranges = np.stack([np.nanmax(M_tune[:, labels == c], 1) - np.nanmin(M_tune[:, labels == c], 1)
                       for c in range(C)], axis=1)

    def widths(level_hat: float) -> np.ndarray:
        near = np.argsort(np.abs(levels - level_hat))[:k]
        return np.nanquantile(ranges[near], q, axis=0)
    return widths


def calibrated(M_tune: np.ndarray, labels: np.ndarray, q: float) -> np.ndarray:
    """q-quantile over tuning users of each component's within-component range."""
    C = labels.max() + 1
    out = np.zeros(C)
    for c in range(C):
        sub = M_tune[:, labels == c]
        rng = np.nanmax(sub, axis=1) - np.nanmin(sub, axis=1)
        out[c] = np.nanquantile(rng, q)
    return out


# ---------------------------------------------------------------- driver


@lru_cache(maxsize=1)
def cached():
    _, _, M = load_eval("R1")
    perm = np.random.default_rng(SEED).permutation(M.shape[0])
    half = M.shape[0] // 2
    return load_features(), M, np.sort(perm[:half]), np.sort(perm[half:])


def one_instance(args):
    u_idx, rep, K, T, k = args[:5]
    user_cal_only = len(args) > 5 and args[5]
    t0 = time.time()
    feats, M, tune_users, _ = cached()
    rng = np.random.default_rng(SEED + 1000 * rep + u_idx)
    avail = np.flatnonzero(~np.isnan(M[u_idx]))
    nodes = np.sort(rng.choice(avail, size=K, replace=False))
    mu = M[u_idx, nodes].astype(np.float64)
    M_tune = M[np.ix_(tune_users, nodes)].astype(np.float64)
    U = rng.random((K, T))
    level = np.log(2 * (K + COMPONENTS) * T * T)  # delta = 1/T
    runs, insts = [], []

    def record(policy, graph, param, regret):
        cum = np.cumsum(regret)
        row = {"user": u_idx, "rep": rep, "policy": policy, "graph": graph, "param": str(param)}
        for c in CHECKPOINTS:
            if c <= T:
                row[f"regret@{c}"] = float(cum[c - 1])
        runs.append(row)

    if not user_cal_only:
        record("ts", "-", "-", run_ts(mu, U, T, np.random.default_rng(SEED + 7 * u_idx + rep)))
        record("klucb", "-", "logt", run_klucb(mu, U, T))
        record("klucb", "-", "ell", run_klucb(mu, U, T, fixed_level=level))
        Lc = complete_laplacian(K)
        for lam in (1.0, 10.0):
            record("shrink_ts", "complete", lam, run_spectral(mu, U, T, Lc, lam, level, "ts",
                                                              np.random.default_rng(SEED + 11 * u_idx + rep)))

    for g in (("I-mf", "I-coeng") if user_cal_only else GRAPH_NAMES):
        grng = np.random.default_rng(SEED + 31 * u_idx + 97 * rep + zlib.crc32(g.encode()) % 1000)
        base = g.split("~")[0]
        W = build(feats, base, k, grng, nodes)
        if g.endswith("~rewired"):
            W = rewire(W, grng)
        L = scaled_laplacian(W)
        labels = partition(W, SEED + u_idx + rep)
        certs = certificates(W, mu, labels)
        for q in QUANTILES:
            certs[f"cal{int(q * 100)}"] = calibrated(M_tune, labels, q)
        inst = {"user": u_idx, "rep": rep, "graph": g}
        C = labels.max() + 1
        comp_gap = np.array([mu.max() - mu[labels == c].max() for c in range(C)])
        sub = np.arange(C) != labels[np.argmax(mu)]
        for name, w in certs.items():
            inst[f"valid_{name}"] = float((w + 1e-12 >= certs["oracle"]).mean())
            inst[f"rejectable_{name}"] = float((w[sub] < comp_gap[sub]).mean())
            inst[f"mean_width_{name}"] = float(w.mean())
        if user_cal_only:
            for q in (0.9, 0.75):
                fn = calibrated_user(M_tune, labels, q)
                record("sp_klucb", g, f"user{int(q * 100)}", run_sp_klucb(mu, U, T, labels, fn, level))
                w_u = fn(float(np.nanmean(mu)))  # widths at the true level, for the validity check
                inst[f"valid_user{int(q * 100)}"] = float((w_u + 1e-12 >= certs["oracle"]).mean())
                inst[f"mean_width_user{int(q * 100)}"] = float(w_u.mean())
            insts.append(inst)
            continue
        insts.append(inst)
        record("spectral_ts", g, 10.0, run_spectral(mu, U, T, L, 10.0, level, "ts",
                                                    np.random.default_rng(SEED + 11 * u_idx + rep)))
        for name, w in certs.items():
            record("sp_klucb", g, name, run_sp_klucb(mu, U, T, labels, w, level))
    print(f"user {u_idx} rep {rep} done in {time.time() - t0:.0f}s", flush=True)
    return runs, insts


def main(n_users: int, subsets: int, K: int, T: int, k: int, jobs: int, tag: str, user_cal: bool = False) -> None:
    _, _, _, test_users = cached()
    tasks = [(int(u), rep, K, T, k, user_cal) for rep in range(subsets) for u in test_users[:n_users]]
    with ProcessPoolExecutor(jobs) as ex:
        results = list(ex.map(one_instance, tasks, chunksize=1))
    pd.DataFrame([r for rs, _ in results for r in rs]).to_csv(RESULTS / f"setting_a2_runs{tag}.csv", index=False)
    pd.DataFrame([r for _, ins in results for r in ins]).to_csv(RESULTS / f"setting_a2_instances{tag}.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=120)
    ap.add_argument("--subsets", type=int, default=3)
    ap.add_argument("--arms", type=int, default=300)
    ap.add_argument("--horizon", type=int, default=20000)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=7)
    ap.add_argument("--tag", default="")
    ap.add_argument("--user-cal", action="store_true", help="only the per-user calibrated certificates")
    a = ap.parse_args()
    main(a.users, a.subsets, a.arms, a.horizon, a.k, a.jobs, a.tag, a.user_cal)
