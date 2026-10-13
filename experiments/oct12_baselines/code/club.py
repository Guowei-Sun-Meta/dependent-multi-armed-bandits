"""CLUB baseline for KuaiRec Setting B (online clustering of users).

Usage (from the repo root; needs data/kuairec_cache from kuairec/code/data.py and graphs.py --k 10):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct12_baselines/code/club.py --jobs 6

CLUB (Gentile, Li and Zappella, ICML 2014) keeps a graph over users, deletes an edge when the
two users' estimates are confidently different, and serves each user from the pooled estimate
of its current connected component. Setting B has no contexts, so we use the multi-armed
version: each user has a Beta-Bernoulli estimate per video; when user u is updated on video i,
the edge (u, v) is deleted if |p_u,i - p_v,i| > gamma (cb(n_u,i) + cb(n_v,i)), with
cb(n) = sqrt((1 + log(1 + n)) / (2 (1 + n))) (Hoeffding scale). Users are served by Thompson
sampling from their component's pooled Beta posterior, so the comparison with ts_ind and
ts_one in setting_b.py is like for like.

Initial graphs: complete (plain CLUB), U-coeng (graph-initialized CLUB) and its rewiring.
Instances, arrivals and the common random numbers are those of kuairec/code/setting_b.py, so
regret is paired with its runs (8 instances, 300 users, 100 videos, T = 100,000).
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "kuairec" / "code"))
import setting_b as sb  # noqa: E402

RESULTS = HERE.parent / "results"
GRAPHS = ("complete", "U-coeng", "U-coeng~rewired")
GAMMAS = (0.25, 0.5, 1.0)


def cb(n):
    return np.sqrt((1 + np.log1p(n)) / (2 * (1 + n)))


def run(args):
    inst, n, K, T, graph, gamma = args
    t0 = time.time()
    feats, users, mu, M_hold, arrivals, U = sb.instance(inst, n, K, T)
    blocked = np.isnan(mu)
    best = np.where(blocked, -1.0, mu).max(axis=1)
    W = sb.user_graph(feats, graph, users, inst)
    A = (W > 0).astype(bool).tolil()
    rng = np.random.default_rng(sb.SEED + 7 * inst + len(graph))
    wins, cnt = np.zeros((n, K)), np.zeros((n, K))
    ncomp, comp = connected_components(A.tocsr(), directed=False)
    Wc = np.zeros((ncomp, K))
    Nc = np.zeros((ncomp, K))
    regret = np.zeros(T)
    deletions, dirty = 0, False
    for t in range(T):
        if dirty:
            ncomp, comp = connected_components(A.tocsr(), directed=False)
            Wc = np.zeros((ncomp, K))
            Nc = np.zeros((ncomp, K))
            np.add.at(Wc, comp, wins)
            np.add.at(Nc, comp, cnt)
            dirty = False
        u = arrivals[t]
        c = comp[u]
        score = rng.beta(1 + Wc[c], 1 + Nc[c] - Wc[c])
        score = np.where(blocked[u], -np.inf, score)
        i = int(np.argmax(score))
        r = sb.reward(U, mu, u, i, cnt[u, i])
        wins[u, i] += r
        cnt[u, i] += 1
        Wc[c, i] += r
        Nc[c, i] += 1
        nbrs = np.array(A.rows[u], dtype=int)
        if len(nbrs):
            pu = (wins[u, i] + 1) / (cnt[u, i] + 2)
            pv = (wins[nbrs, i] + 1) / (cnt[nbrs, i] + 2)
            cut = nbrs[np.abs(pu - pv) > gamma * (cb(cnt[u, i]) + cb(cnt[nbrs, i]))]
            for v in cut:
                A[u, v] = False
                A[v, u] = False
                deletions += 1
            if len(cut):
                dirty = True
        regret[t] = best[u] - mu[u, i]
    cum = np.cumsum(regret)
    row = {"instance": inst, "users": n, "arms": K, "policy": "club_ts", "graph": graph, "param": str(gamma),
           "edges_deleted": deletions, "components_end": int(ncomp), "seconds": round(time.time() - t0, 1)}
    for ck in sb.CHECKPOINTS:
        if ck <= T:
            row[f"regret@{ck}"] = float(cum[ck - 1])
    print(f"inst {inst} club {graph}: {row['seconds']}s, {ncomp} components", flush=True)
    return row


def main(instances, n, K, T, jobs):
    RESULTS.mkdir(parents=True, exist_ok=True)
    tasks = [(i, n, K, T, g, gm) for i in range(instances) for g in GRAPHS for gm in GAMMAS]
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(run, tasks, chunksize=1))
    pd.DataFrame(rows).to_csv(RESULTS / "club_runs.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", type=int, default=8)
    ap.add_argument("--users", type=int, default=300)
    ap.add_argument("--arms", type=int, default=100)
    ap.add_argument("--horizon", type=int, default=100000)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    if a.pilot:
        print(run((0, a.users, a.arms, 20000, "complete", 1.0)))
    else:
        main(a.instances, a.users, a.arms, a.horizon, a.jobs)
