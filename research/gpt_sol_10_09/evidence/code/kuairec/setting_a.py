"""Setting A: one user, K sampled videos, an item-item graph built on those videos.

Usage (from the repo root, after graphs.py has cached node features):
    .venv/bin/python -I experiments/kuairec/setting_a.py --users 100 --horizon 5000 --jobs 6

Each instance is (user, video subset, graph). Rewards are Bernoulli with the user's
R1 means. Arms share common random numbers across policies (the n-th pull of an arm
gives the same reward under every policy). Outputs go to
research/kuairec_graphs/results/setting_a_{runs,instances}.csv.

Policies
- ucb: arm UCB with radius sigma*sqrt(2*ell/n), ell = log(2(K+M)T/delta), delta = 1/T.
- ts: Beta(1, 1)-Bernoulli Thompson sampling.
- spectral_ucb / spectral_ts (lambda): Gaussian posterior with precision lambda*L + eps*I
  + diag(n), centred at the prior mean M0; UCB uses the same sqrt(2*ell) multiplier as
  ucb, so lambda -> 0 recovers it. TS samples each arm's marginal posterior.
- sp_ucb (certificate): SP-UCB from the alignment manuscript on a 20-component spectral
  partition of the graph. Certificates: oracle (true within-component range, the tightest
  valid one), energy (sqrt(component energy x resistance diameter), valid but looser),
  none (zero width: trusts the partition, invalid).
"""

from __future__ import annotations

import argparse
import sys
import time
import zlib
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from sklearn.cluster import SpectralClustering

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data import RESULTS, load_eval  # noqa: E402
from graphs import build, load_features, rewire, scaled_laplacian  # noqa: E402

SIGMA = 0.5  # sub-Gaussian proxy valid for any Bernoulli reward
M0 = 0.18  # prior mean: average R1 mean over the platform
EPS = 1e-3
LAMBDAS = (0.1, 1.0, 10.0)
COMPONENTS = 20
GRAPH_NAMES = ("I-mf", "I-coeng", "I-coauthor", "I-tag", "I-cat", "I-mf~rewired")
CHECKPOINTS = (100, 500, 1000, 2000, 5000, 10000, 20000)
SEED = 20261009


# ---------------------------------------------------------------- policies


def run_ucb(mu, U, T, ell):
    K = len(mu)
    n, s = np.zeros(K), np.zeros(K)
    regret, best = np.zeros(T), mu.max()
    for t in range(T):
        idx = np.where(n > 0, s / np.maximum(n, 1) + SIGMA * np.sqrt(2 * ell / np.maximum(n, 1)), np.inf)
        a = int(np.argmax(idx))
        s[a] += U[a, int(n[a])] < mu[a]
        n[a] += 1
        regret[t] = best - mu[a]
    return regret


def run_ts(mu, U, T, rng):
    K = len(mu)
    wins, n = np.zeros(K), np.zeros(K)
    regret, best = np.zeros(T), mu.max()
    for t in range(T):
        a = int(np.argmax(rng.beta(1 + wins, 1 + n - wins)))
        wins[a] += U[a, int(n[a])] < mu[a]
        n[a] += 1
        regret[t] = best - mu[a]
    return regret


def run_spectral(mu, U, T, L, lam, ell, mode, rng):
    K = len(mu)
    P = np.linalg.inv(lam * L.toarray() + EPS * np.eye(K))  # posterior covariance / sigma^2
    resid = np.zeros(K)  # sum of (reward - M0) per arm
    n = np.zeros(K)
    regret, best, alpha = np.zeros(T), mu.max(), np.sqrt(2 * ell)
    for t in range(T):
        mean = M0 + P @ resid
        sd = SIGMA * np.sqrt(np.maximum(np.diag(P), 0))
        score = mean + alpha * sd if mode == "ucb" else mean + sd * rng.standard_normal(K)
        a = int(np.argmax(score))
        r = float(U[a, int(n[a])] < mu[a])
        n[a] += 1
        resid[a] += r - M0
        Pa = P[:, a].copy()
        P -= np.outer(Pa, Pa) / (1.0 + Pa[a])
        regret[t] = best - mu[a]
    return regret


def run_sp_ucb(mu, U, T, labels, widths, ell):
    K, C = len(mu), labels.max() + 1
    members = [np.flatnonzero(labels == c) for c in range(C)]
    n, s = np.zeros(K), np.zeros(K)
    Nc, Sc = np.zeros(C), np.zeros(C)
    regret, best = np.zeros(T), mu.max()

    def b(x):
        return SIGMA * np.sqrt(2 * ell / x)

    for t in range(T):
        if t < C:
            a = int(members[t][0])
        else:
            u = np.where(n > 0, s / np.maximum(n, 1) + b(np.maximum(n, 1)), np.inf)
            best_c, best_val, best_arm = -1, -np.inf, -1
            for c in range(C):
                m = members[c]
                i = m[np.argmax(u[m])]
                val = min(u[i], Sc[c] / Nc[c] + b(Nc[c]) + widths[c])
                if val > best_val:
                    best_c, best_val, best_arm = c, val, i
            a = int(best_arm)
        r = float(U[a, int(n[a])] < mu[a])
        n[a] += 1
        s[a] += r
        Nc[labels[a]] += 1
        Sc[labels[a]] += r
        regret[t] = best - mu[a]
    return regret


# ---------------------------------------------------------------- instance diagnostics


def partition(W: sp.csr_matrix, seed: int) -> np.ndarray:
    A = W.toarray()
    A = A + 1e-6 * (A.sum() / A.size)  # keeps spectral clustering defined on disconnected graphs
    sc = SpectralClustering(COMPONENTS, affinity="precomputed", assign_labels="cluster_qr", random_state=seed)
    return sc.fit_predict(A)


def certificates(W: sp.csr_matrix, mu: np.ndarray, labels: np.ndarray) -> dict[str, np.ndarray]:
    C = labels.max() + 1
    oracle, energy = np.zeros(C), np.ones(C)
    for c in range(C):
        m = np.flatnonzero(labels == c)
        oracle[c] = mu[m].max() - mu[m].min()
        if len(m) == 1:
            energy[c] = 0.0
            continue
        Wc = W[m][:, m]
        if connected_components(Wc, directed=False)[0] > 1:
            continue  # no graph bound across disconnected pieces; trivial width 1
        Lc = (sp.diags(np.asarray(Wc.sum(axis=1)).ravel()) - Wc).toarray()
        Pinv = np.linalg.pinv(Lc)
        d = np.diag(Pinv)
        diameter = float((d[:, None] + d[None, :] - 2 * Pinv).max())
        energy[c] = min(1.0, np.sqrt(max(mu[m] @ Lc @ mu[m], 0.0) * diameter))
    return {"oracle": oracle, "energy": energy, "none": np.zeros(C)}


def instance_stats(mu, L, labels, certs) -> dict:
    srt = np.sort(mu)[::-1]
    gap1, gap10 = srt[0] - srt[1], srt[0] - srt[9]
    energy = float(mu @ (L @ mu))
    quotient = energy / float(((mu - mu.mean()) ** 2).sum())
    C = labels.max() + 1
    best_c = labels[np.argmax(mu)]
    comp_gap = np.array([mu.max() - mu[labels == c].max() for c in range(C)])
    sub = np.arange(C) != best_c
    out = {
        "gap1": gap1,
        "gap10": gap10,
        "energy": energy,
        "energy_to_gap10": np.sqrt(energy) / gap10 if gap10 > 0 else np.inf,
        "quotient": quotient,
    }
    for name, w in certs.items():
        out[f"rejectable_{name}"] = float((w[sub] < comp_gap[sub]).mean())
        out[f"valid_{name}"] = bool(np.all(w + 1e-12 >= certs["oracle"]))
    return out


# ---------------------------------------------------------------- driver


@lru_cache(maxsize=1)
def cached_features():
    return load_features()


def one_user(args):
    u_idx, K, T, k = args
    t0 = time.time()
    feats = cached_features()
    _, videos, M = load_eval("R1")
    rng = np.random.default_rng(SEED + u_idx)
    avail = np.flatnonzero(~np.isnan(M[u_idx]))
    nodes = np.sort(rng.choice(avail, size=K, replace=False))
    mu = M[u_idx, nodes].astype(np.float64)
    U = rng.random((K, T))  # common random numbers, indexed by (arm, pull count)
    M_arms = COMPONENTS
    ell = np.log(2 * (K + M_arms) * T * T)  # delta = 1/T
    runs, insts = [], []

    def record(policy, graph, param, regret):
        cum = np.cumsum(regret)
        row = {"user": u_idx, "policy": policy, "graph": graph, "param": param}
        for c in CHECKPOINTS:
            if c <= T:
                row[f"regret@{c}"] = float(cum[c - 1])
        runs.append(row)

    record("ucb", "-", "-", run_ucb(mu, U, T, ell))
    record("ts", "-", "-", run_ts(mu, U, T, np.random.default_rng(SEED + 7 * u_idx)))

    for g in GRAPH_NAMES:
        grng = np.random.default_rng(SEED + 31 * u_idx + zlib.crc32(g.encode()) % 1000)
        base = g.split("~")[0]
        W = build(feats, base, k, grng, nodes)
        if g.endswith("~rewired"):
            W = rewire(W, grng)
        L = scaled_laplacian(W)
        labels = partition(W, SEED + u_idx)
        certs = certificates(W, mu, labels)
        insts.append({"user": u_idx, "graph": g, **instance_stats(mu, L, labels, certs)})
        for lam in LAMBDAS:
            record("spectral_ucb", g, lam, run_spectral(mu, U, T, L, lam, ell, "ucb", None))
            record("spectral_ts", g, lam, run_spectral(mu, U, T, L, lam, ell, "ts",
                                                       np.random.default_rng(SEED + 11 * u_idx)))
        for name, w in certs.items():
            record("sp_ucb", g, name, run_sp_ucb(mu, U, T, labels, w, ell))
    print(f"user {u_idx} done in {time.time() - t0:.0f}s", flush=True)
    return runs, insts


def main(n_users: int, K: int, T: int, k: int, jobs: int) -> None:
    _, _, M = load_eval("R1")
    perm = np.random.default_rng(SEED).permutation(M.shape[0])
    test_users = np.sort(perm[M.shape[0] // 2:])[:n_users]  # first half is reserved for tuning
    load_features()  # build the cache once before forking
    with ProcessPoolExecutor(jobs) as ex:
        results = list(ex.map(one_user, [(int(u), K, T, k) for u in test_users]))
    runs = pd.DataFrame([r for rs, _ in results for r in rs])
    insts = pd.DataFrame([r for _, ins in results for r in ins])
    runs.to_csv(RESULTS / "setting_a_runs.csv", index=False)
    insts.to_csv(RESULTS / "setting_a_instances.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=100)
    ap.add_argument("--arms", type=int, default=300)
    ap.add_argument("--horizon", type=int, default=5000)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    main(a.users, a.arms, a.horizon, a.k, a.jobs)
