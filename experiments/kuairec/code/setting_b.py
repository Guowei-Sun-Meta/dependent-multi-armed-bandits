"""Setting B: many users, a user-user graph pools information across users.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/kuairec/code/setting_b.py \
        --instances 6 --users 300 --arms 100 --horizon 100000 --jobs 7

An instance samples n test users and K videos. Each round a user arrives uniformly at
random and the learner shows one video; reward is Bernoulli with that user's R1 mean.
Blocked (user, video) pairs are never shown. Each (instance, policy, graph, parameter)
is one job, so all cores stay busy.

Policies
- ts_ind: Beta-Bernoulli TS per (user, video); no pooling.
- ts_one: Beta-Bernoulli TS per video shared by all users (complete pooling).
- klucb_ind: KL-UCB per (user, video) at the fixed level used by the certified policy.
- graph_ts (lambda): for each video, Gaussian posterior over users with precision
  lambda * L_U + eps * I + diag(counts), centred at M0. The complete graph gives
  graph-free shrinkage toward each video's population mean.
- sp_klucb_user (certificate): users are partitioned into 20 clusters of the U2U graph.
  For user u in cluster c and video i the index is
  min(KL-UCB of (u, i), KL-UCB of the pooled cluster mean of i + width(c, i)).
  Widths: oracle (true range of i's means inside c), cal90 / cal50 (quantile over
  held-out videos of within-cluster ranges), none (zero: trusts the clusters).
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
from setting_a import partition  # noqa: E402
from setting_a2 import kl_upper  # noqa: E402

SEED = 20261009
M0, EPS, SIGMA = 0.18, 1e-3, 0.5
COMPONENTS = 20
GRAPH_NAMES = ("U-coeng", "U-mf", "U-coauthor", "U-geo", "U-coeng~rewired")
CHECKPOINTS = (1000, 5000, 10000, 20000, 50000, 100000, 200000, 300000)


@lru_cache(maxsize=1)
def base_data():
    _, _, M = load_eval("R1")
    perm = np.random.default_rng(SEED).permutation(M.shape[0])
    return load_features(), M, np.sort(perm[M.shape[0] // 2:])


@lru_cache(maxsize=2)
def instance(inst: int, n: int, K: int, T: int):
    feats, M, test_users = base_data()
    rng = np.random.default_rng(SEED + 100 * inst)
    users = np.sort(rng.choice(test_users, size=n, replace=False))
    videos = np.sort(rng.choice(M.shape[1], size=K, replace=False))
    mu = M[np.ix_(users, videos)].astype(np.float64)  # NaN = blocked
    held_out = np.setdiff1d(np.arange(M.shape[1]), videos)
    M_hold = M[np.ix_(users, held_out)].astype(np.float64)
    arrivals = rng.integers(n, size=T)
    U = rng.random((n, K, max(8, 4 * T // (n * K) + 64)))  # CRN by (user, video, pull count)
    return feats, users, mu, M_hold, arrivals, U


def reward(U, mu, u, i, cnt):
    c = int(cnt)
    draw = U[u, i, c] if c < U.shape[2] else np.random.default_rng(hash((u, i, c)) % 2**32).random()
    return float(draw < mu[u, i])


def user_graph(feats, name, users_idx, inst):
    rng = np.random.default_rng(SEED + inst + zlib.crc32(name.encode()) % 1000)
    if name == "complete":
        n = len(users_idx)
        return sp.csr_matrix(np.ones((n, n)) - np.eye(n))
    W = build(feats, name.split("~")[0], 10, rng, users_idx)
    return rewire(W, rng) if name.endswith("~rewired") else W


def run(args):
    inst, n, K, T, policy, graph, param = args
    t0 = time.time()
    feats, users, mu, M_hold, arrivals, U = instance(inst, n, K, T)
    blocked = np.isnan(mu)
    mu_f = np.where(blocked, -1.0, mu)
    best = mu_f.max(axis=1)
    level = np.log(2 * (n * K + COMPONENTS * K) * T * T)
    cnt = np.zeros((n, K))
    regret = np.zeros(T)
    rng = np.random.default_rng(SEED + inst + zlib.crc32(f"{policy}{graph}{param}".encode()) % 10_000)

    if policy in ("ts_ind", "ts_one", "klucb_ind"):
        wins = np.zeros((n, K))
        up = np.full((n, K), np.inf)
        for t in range(T):
            u = arrivals[t]
            if policy == "ts_ind":
                score = rng.beta(1 + wins[u], 1 + cnt[u] - wins[u])
            elif policy == "ts_one":
                w, c = wins.sum(0), cnt.sum(0)
                score = rng.beta(1 + w, 1 + c - w)
            else:
                score = up[u]
            score = np.where(blocked[u], -np.inf, score)
            i = int(np.argmax(score))
            r = reward(U, mu, u, i, cnt[u, i])
            wins[u, i] += r
            cnt[u, i] += 1
            if policy == "klucb_ind":
                up[u, i] = kl_upper(np.array([wins[u, i] / cnt[u, i]]), np.array([cnt[u, i]]), level)[0]
            regret[t] = best[u] - mu[u, i]

    elif policy == "graph_ts":
        L = scaled_laplacian(user_graph(feats, graph, users, inst)).toarray()
        P0 = np.linalg.inv(float(param) * L + EPS * np.eye(n))
        P = np.repeat(P0[None], K, axis=0)  # per-video covariance over users (/ sigma^2)
        resid = np.zeros((K, n))
        for t in range(T):
            u = arrivals[t]
            Pu = P[:, u, :]  # K x n
            mean = M0 + np.einsum("kn,kn->k", Pu, resid)
            sd = SIGMA * np.sqrt(np.maximum(Pu[:, u], 0))
            score = np.where(blocked[u], -np.inf, mean + sd * rng.standard_normal(K))
            i = int(np.argmax(score))
            r = reward(U, mu, u, i, cnt[u, i])
            cnt[u, i] += 1
            resid[i, u] += r - M0
            col = P[i, :, u].copy()
            P[i] -= np.outer(col, col) / (1.0 + col[u])
            regret[t] = best[u] - mu[u, i]

    elif policy == "sp_klucb_user":
        W = user_graph(feats, graph, users, inst)
        labels = partition(W, SEED + inst)
        C = labels.max() + 1
        if param == "oracle":
            width = np.stack([np.nanmax(mu[labels == c], 0) - np.nanmin(mu[labels == c], 0) for c in range(C)])
        elif param.startswith("cal"):
            q = int(param[3:]) / 100
            width = np.stack([np.repeat(np.nanquantile(
                np.nanmax(M_hold[labels == c], 0) - np.nanmin(M_hold[labels == c], 0), q), K) for c in range(C)])
        else:
            width = np.zeros((C, K))
        width = np.nan_to_num(width, nan=1.0)
        wins = np.zeros((n, K))
        Nc, Sc = np.zeros((C, K)), np.zeros((C, K))
        arm_up = np.full((n, K), np.inf)
        pool_up = np.full((C, K), np.inf)
        for t in range(T):
            u = arrivals[t]
            c = labels[u]
            score = np.minimum(arm_up[u], pool_up[c] + width[c])
            score = np.where(blocked[u], -np.inf, score)
            i = int(np.argmax(score))
            r = reward(U, mu, u, i, cnt[u, i])
            wins[u, i] += r
            cnt[u, i] += 1
            Nc[c, i] += 1
            Sc[c, i] += r
            arm_up[u, i] = kl_upper(np.array([wins[u, i] / cnt[u, i]]), np.array([cnt[u, i]]), level)[0]
            pool_up[c, i] = kl_upper(np.array([Sc[c, i] / Nc[c, i]]), np.array([Nc[c, i]]), level)[0]
            regret[t] = best[u] - mu[u, i]
    else:
        raise ValueError(policy)

    cum = np.cumsum(regret)
    row = {"instance": inst, "users": n, "arms": K, "policy": policy, "graph": graph, "param": str(param),
           "seconds": round(time.time() - t0, 1)}
    for c in CHECKPOINTS:
        if c <= T:
            row[f"regret@{c}"] = float(cum[c - 1])
    print(f"inst {inst} {policy} {graph} {param}: {row['seconds']}s", flush=True)
    return row


def jobs_for(instances, n, K, T):
    out = []
    for inst in instances:
        out += [(inst, n, K, T, p, "-", "-") for p in ("ts_ind", "ts_one", "klucb_ind")]
        out += [(inst, n, K, T, "graph_ts", "complete", lam) for lam in (1.0, 10.0)]
        for g in GRAPH_NAMES:
            out += [(inst, n, K, T, "graph_ts", g, lam) for lam in (1.0, 10.0)]
            out += [(inst, n, K, T, "sp_klucb_user", g, c) for c in ("oracle", "cal90", "cal50", "none")]
    # Longest jobs first keeps the pool busy until the end.
    return sorted(out, key=lambda j: j[4] != "graph_ts")


def main(instances: int, n: int, K: int, T: int, jobs: int, tag: str) -> None:
    base_data()
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(run, jobs_for(range(instances), n, K, T), chunksize=1))
    pd.DataFrame(rows).to_csv(RESULTS / f"setting_b_runs{tag}.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", type=int, default=6)
    ap.add_argument("--users", type=int, default=300)
    ap.add_argument("--arms", type=int, default=100)
    ap.add_argument("--horizon", type=int, default=100000)
    ap.add_argument("--jobs", type=int, default=7)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    main(a.instances, a.users, a.arms, a.horizon, a.jobs, a.tag)
