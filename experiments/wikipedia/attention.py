"""Wikipedia attention slot: correlated arms over the hyperlink graph, persistent daily attention.

Usage (from the repo root, after collect.py or collect_multi.py):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/wikipedia/attention.py [--dataset multi] --diagnose
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/wikipedia/attention.py [--dataset multi] --seeds 5 --jobs 5

Datasets: "single" (150 programming-language articles; research/claude_opus_10_09/wikipedia) and
"multi" (6 communities x 25 articles; research/claude_opus_10_09_v2/wikipedia_multi), which adds
a domain-block graph (articles connected within their community) as a reference condition.

Arms: 150 programming-language articles. Reward of featuring article i on day t: log(1 + daily
user views). Assumption: featuring does not change organic attention (exogenous, restless).
Each day 10 slots are featured and their rewards observed (noise sd 0.05). For each origin F
in {365, 730, 1095} the model is fitted on days F-365..F-1 (AR lags {1, 2, 7}; innovation
covariance shrunk toward a hyperlink-graph resolvent plus a common shock) and run on the next
120 days. Graph conditions: real hyperlinks, a degree-preserving rewiring, no graph.
Policies mirror experiments/kuairec/daily.py, including drift and sparse-history variants.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "kuairec"))
sys.path.insert(0, str(ROOT / "experiments" / "st_toy"))
from daily import DriftFilter, fit_model  # noqa: E402
from graphs import rewire, scaled_laplacian  # noqa: E402
from toy import stationary_lag_cov  # noqa: E402

DATASETS = {
    "single": (ROOT / "research" / "claude_opus_10_09" / "wikipedia", ROOT / "data" / "wikipedia" / "filters"),
    "multi": (ROOT / "research" / "claude_opus_10_09_v2" / "wikipedia_multi", ROOT / "data" / "wikipedia" / "filters_multi"),
}
DATASET = "single"
DATA = DATASETS[DATASET][0] / "data"
RESULTS = DATASETS[DATASET][0] / "results"
CACHE = DATASETS[DATASET][1]


def configure(name: str) -> None:
    """Point paths at a dataset (called in every worker, since workers re-import this module)."""
    global DATASET, DATA, RESULTS, CACHE
    if name != DATASET:
        DATASET = name
        DATA, RESULTS, CACHE = DATASETS[name][0] / "data", DATASETS[name][0] / "results", DATASETS[name][1]
        panel.cache_clear()
SEED = 20261009
WINDOW, TEST, K_SLOTS, S_OBS = 365, 120, 10, 0.05
ORIGINS = (365, 730, 1095)
DRIFT = 0.0005
POLICIES = ("fit_mean", "last_value", "ts_iid", "ar_greedy", "st_greedy", "st_greedy_rewired",
            "st_greedy_nograph", "st_ucbm1", "st_jps", "dr_greedy",
            "sh_greedy", "sh_ucbm1", "sh_jps", "sh_tsiid")
MULTI_POLICIES = ("fit_mean", "last_value", "ts_iid", "ar_greedy", "st_greedy", "st_greedy_rewired",
                  "st_greedy_block", "st_greedy_nograph", "st_jps", "st_jps_block", "st_jps_nograph",
                  "st_ucbm1", "dr_greedy")
DETERMINISTIC = ("fit_mean", "last_value", "ar_greedy", "st_greedy", "st_greedy_rewired", "st_greedy_nograph",
                 "st_greedy_block", "st_ucbm1", "dr_greedy", "sh_greedy", "sh_ucbm1")


@lru_cache(maxsize=1)
def panel():
    v = pd.read_csv(DATA / "views.csv", index_col="date")
    Y = np.log1p(v.to_numpy(float))
    titles = list(v.columns)
    links = pd.read_csv(DATA / "links.csv")
    pos = {t: i for i, t in enumerate(titles)}
    r = [pos[a] for a, b in zip(links.source, links.target) if a in pos and b in pos]
    c = [pos[b] for a, b in zip(links.source, links.target) if a in pos and b in pos]
    A = sp.csr_matrix((np.ones(len(r)), (r, c)), shape=(len(titles), len(titles)))
    W = ((A + A.T) > 0).astype(float).tocsr()
    return Y, titles, W


@lru_cache(maxsize=1)
def domains():
    """Domain label per article, and the domain-block graph (multi dataset only)."""
    path = DATA / "domains.csv"
    if not path.exists():
        return None, None
    _, titles, _ = panel()
    dom = pd.read_csv(path).set_index("title")["domain"].reindex(titles).to_numpy()
    B = sp.csr_matrix((dom[:, None] == dom[None, :]).astype(float) - np.eye(len(titles)))
    return dom, B


def graph_corr(W: sp.csr_matrix, gamma: float = 5.0) -> np.ndarray:
    L = scaled_laplacian(W).toarray()
    K = np.linalg.inv(np.eye(W.shape[0]) + gamma * L)
    d = np.sqrt(np.diag(K))
    return K / d[:, None] / d[None, :]


def variant_of(policy: str) -> str:
    if policy.startswith("sh_"):
        return "sparse"
    if policy.startswith("ar_"):
        return "ar"
    if policy.startswith("dr_"):
        return "drift"
    for v in ("rewired", "nograph", "block"):
        if policy.endswith(v):
            return v
    return "st"


def sparse_seen(origin: int, N: int) -> np.ndarray:
    rng = np.random.default_rng(SEED + 13 * origin)
    return np.stack([rng.choice(N, size=K_SLOTS, replace=False) for _ in range(WINDOW)])


def burnin(origin: int, variant: str):
    Y, _, W = panel()
    N = Y.shape[1]
    Yf = Y[origin - WINDOW:origin]
    if variant == "rewired":
        C_G = graph_corr(rewire(W, np.random.default_rng(SEED + origin)))
    elif variant == "block":
        C_G = graph_corr(domains()[1])
    elif variant in ("nograph", "ar"):
        C_G = np.eye(N)
    else:
        C_G = graph_corr(W)
    m, a, Q, info = fit_model(Yf, C_G)
    if variant == "ar":
        Q = np.diag(np.diag(Q))
    K_mu = np.eye(N) * Yf.mean(0).var()
    flt = DriftFilter(a, N, K_mu, np.kron(stationary_lag_cov(a), Q), Q, S_OBS,
                      drift=DRIFT if variant == "drift" else 0.0)
    path = CACHE / f"F{origin}_{variant}.npz"
    if path.exists():
        z = np.load(path)
        flt.b, flt.P = z["b"], z["P"]
        return flt, info
    flt.b[:N] = Yf.mean()
    noise = S_OBS * np.random.default_rng(SEED + 7 * origin).standard_normal(Yf.shape)
    seen = sparse_seen(origin, N) if variant == "sparse" else None
    for t in range(WINDOW):
        for i in (range(N) if seen is None else seen[t]):
            flt.update(int(i), Yf[t, i] + noise[t, i])
        flt.propagate()
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(path, b=flt.b, P=flt.P)
    return flt, info


def run(args):
    origin, seed, policy = args[:3]
    configure(args[3] if len(args) > 3 else "single")
    t0 = time.time()
    Y, _, _ = panel()
    N = Y.shape[1]
    rng = np.random.default_rng(SEED + 100 * origin + seed)
    noise = S_OBS * rng.standard_normal(Y.shape)
    test = range(origin, min(origin + TEST, len(Y)))
    regret, info = [], {}
    Yf = Y[origin - WINDOW:origin]

    def pick(score):
        return np.argsort(-score)[:K_SLOTS]

    if policy in ("fit_mean", "last_value", "ts_iid", "sh_tsiid"):
        if policy == "sh_tsiid":
            seen = sparse_seen(origin, N)
            n, s = np.zeros(N), np.zeros(N)
            for t in range(WINDOW):
                n[seen[t]] += 1
                s[seen[t]] += Yf[t, seen[t]]
        else:
            n, s = np.full(N, float(WINDOW)), Yf.sum(0)
        last = Yf[-1].copy()
        var_y, prior_m, prior_v = Yf.var(0).mean(), Yf.mean(), Yf.mean(0).var()
        for t in test:
            if policy == "fit_mean":
                score = Yf.mean(0)
            elif policy == "last_value":
                score = last
            else:
                prec = 1 / prior_v + n / var_y
                score = (prior_m / prior_v + s / var_y) / prec + rng.standard_normal(N) / np.sqrt(prec)
            ch = pick(score)
            obs = Y[t, ch] + noise[t, ch]
            last[ch], n[ch], s[ch] = obs, n[ch] + 1, s[ch] + obs
            regret.append(np.sort(Y[t])[-K_SLOTS:].sum() - Y[t, ch].sum())
    else:
        flt, info = burnin(origin, variant_of(policy))
        kind = policy.split("_")[1]
        for t in test:
            mean, S, _ = flt.reward_mean_cov()
            if kind == "greedy":
                score = mean
            elif kind == "ucbm1":
                score = mean + np.sqrt(np.maximum(np.diag(S), 0))
            else:  # jps: joint predictive sampling
                _, HAP = flt.next_projection()
                Cn = (HAP[:, :N] + HAP[:, N:2 * N]).T
                Hb = HAP.reshape(N, flt.p + 1, N)
                V = Hb[:, 0, :] + np.tensordot(Hb[:, 1:, :], flt.a, axes=([1], [0])) + flt.Q
                B = Cn @ np.linalg.solve(V + 1e-9 * np.eye(N), Cn.T)
                w, U = np.linalg.eigh((B + B.T) / 2)
                score = mean + U @ (np.sqrt(np.maximum(w, 0)) * rng.standard_normal(N))
            ch = pick(score)
            for i in ch:
                flt.update(int(i), Y[t, i] + noise[t, i])
            flt.propagate()
            regret.append(np.sort(Y[t])[-K_SLOTS:].sum() - Y[t, ch].sum())
    row = {"origin": origin, "seed": seed, "policy": policy, "test_days": len(regret),
           "regret_per_day": float(np.mean(regret)), "seconds": round(time.time() - t0, 1),
           **{k: v for k, v in info.items() if k != "coef"}}
    print(f"F={origin} seed={seed} {policy}: {row['regret_per_day']:.3f}/day", flush=True)
    return row


def burnin_task(args):
    configure(args[2] if len(args) > 2 else "single")
    burnin(args[0], args[1])
    print(f"burn-in F={args[0]} {args[1]} done", flush=True)


def heldout_loglik(Y, W, B) -> dict:
    """Policy-free test of the fluctuation channel: fit AR + shrunk innovation covariance on each
    365-day window, then score the next 120 days' AR residuals under each covariance target
    (Gaussian log-likelihood per day). A graph that carries shock correlation scores higher."""
    N = Y.shape[1]
    targets = {"no graph (common shock)": np.eye(N), "hyperlinks": graph_corr(W),
               "rewired hyperlinks": graph_corr(rewire(W, np.random.default_rng(SEED)))}
    if B is not None:
        targets["domain blocks"] = graph_corr(B)
    out = {}
    for name, C_G in targets.items():
        tot = []
        for F in ORIGINS:
            Yf = Y[F - WINDOW:F]
            m, a, Q, _ = fit_model(Yf, C_G)
            Xt = Y[F - 7:F + TEST] - m
            E = np.stack([Xt[t] - a[0] * Xt[t - 1] - a[1] * Xt[t - 2] - a[6] * Xt[t - 7] for t in range(7, len(Xt))])
            sign, logdet = np.linalg.slogdet(Q)
            Qi = np.linalg.inv(Q)
            ll = -0.5 * (N * np.log(2 * np.pi) + logdet + np.einsum("ti,ij,tj->t", E, Qi, E))
            tot.append(float(ll.mean()))
        out[name] = {"by_origin": tot, "mean": float(np.mean(tot))}
    return out


def diagnose() -> dict:
    """Persistence, weekly structure, and whether shocks travel along hyperlinks."""
    Y, titles, W = panel()
    X = Y - Y.mean(0)
    rng = np.random.default_rng(SEED)
    ac = {h: float(np.mean([np.corrcoef(X[:-h, i], X[h:, i])[0, 1] for i in range(X.shape[1])]))
          for h in (1, 2, 7, 30)}
    _, a, _, info = fit_model(Y[:WINDOW], np.eye(Y.shape[1]))
    lags = [1, 2, 7]
    rows = range(7, len(X))
    E = np.stack([X[t] - sum(c * X[t - l] for l, c in zip(lags, [a[0], a[1], a[6]])) for t in rows])
    R = np.corrcoef(E.T)
    T_ = sp.triu(W, 1).tocoo()
    Wr = rewire(W, rng)
    Tr = sp.triu(Wr, 1).tocoo()
    iu = np.triu_indices_from(R, 1)
    out = {
        "articles": len(titles), "days": int(Y.shape[0]), "hyperlink_edges": int(T_.nnz),
        "mean_degree": float(2 * T_.nnz / len(titles)), "isolated": int((np.asarray(W.sum(1)).ravel() == 0).sum()),
        "autocorrelation": ac, "ar_coefficients_lags_1_2_7": [float(a[0]), float(a[1]), float(a[6])],
        "ar_radius": float(info["ar_radius"]),
        "innovation_corr_hyperlink_edges": float(R[T_.row, T_.col].mean()),
        "innovation_corr_rewired_edges": float(R[Tr.row, Tr.col].mean()),
        "innovation_corr_all_pairs": float(R[iu].mean()),
        "level_sd_across_articles": float(Y.mean(0).std()), "deviation_sd": float(X.std()),
    }
    dom, B = domains()
    if dom is not None:
        same = dom[:, None] == dom[None, :]
        out["innovation_corr_within_domain"] = float(R[iu][same[iu]].mean())
        out["innovation_corr_across_domain"] = float(R[iu][~same[iu]].mean())
        out["hyperlink_edges_within_domain"] = float(same[T_.row, T_.col].mean())
        out["per_domain"] = {d: {"articles": int((dom == d).sum()),
                                 "lag1_autocorr": float(np.mean([np.corrcoef(X[:-1, i], X[1:, i])[0, 1]
                                                                  for i in np.flatnonzero(dom == d)])),
                                 "lag7_autocorr": float(np.mean([np.corrcoef(X[:-7, i], X[7:, i])[0, 1]
                                                                  for i in np.flatnonzero(dom == d)]))}
                             for d in pd.unique(dom)}
    out["heldout_loglik_per_day"] = heldout_loglik(Y, W, B)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "diagnostics.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return out


def main(seeds: int, jobs: int, dataset: str = "single") -> None:
    configure(dataset)
    panel()
    RESULTS.mkdir(parents=True, exist_ok=True)
    multi = dataset == "multi"
    variants = ("st", "ar", "rewired", "nograph", "drift", "block") if multi else \
        ("st", "ar", "rewired", "nograph", "drift", "sparse")
    with ProcessPoolExecutor(jobs) as ex:
        list(ex.map(burnin_task, [(o, v, dataset) for o in ORIGINS for v in variants]))
    tasks = [(o, s, p, dataset) for o in ORIGINS for s in range(seeds) for p in (MULTI_POLICIES if multi else POLICIES)
             if not (p in DETERMINISTIC and s > 0)]
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(run, tasks, chunksize=1))
    pd.DataFrame(rows).to_csv(RESULTS / "runs.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("--dataset", default="single", choices=list(DATASETS))
    a = ap.parse_args()
    configure(a.dataset)
    if a.diagnose:
        diagnose()
    else:
        main(a.seeds, a.jobs, a.dataset)
