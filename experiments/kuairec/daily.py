"""KuaiRec daily trending slot: correlated arms with persistent daily engagement.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/kuairec/daily.py --seeds 10 --jobs 3

Panel: the 253 evaluation videos observed on all 63 days (5 July to 5 September 2020).
Reward of showing video i on day t: logit of its daily complete-play rate,
(complete_play_cnt + 0.5) / (play_cnt + 1). Assumption: showing a video does not change
its organic engagement (exogenous, restless arms).

Each test day the platform fills k = 10 slots and observes those videos' rewards
(measurement noise sd 0.05 on the logit scale). Fit window: days 1..F, where the learner
has full historical logs. Test window: days F+1..63. Origins F in {28, 35, 42}.

Fitted on the fit window only:
- pooled AR coefficients on deviations from each video's fit-window mean, lags {1, 2, 7};
- innovation covariance: sample covariance shrunk toward s * ((1 - c) C_G + c 11'), where
  C_G is a unit-diagonal graph resolvent and c the common-shock correlation; the shrinkage
  weight is chosen by held-out likelihood on the last 5 fit-window days.

Policies (each picks the top k of a score):
- fit_mean: fit-window means, never updated (static ranking).
- last_value: the most recent observation of each video (naive persistence).
- ts_iid: Gaussian TS per video, iid noise, prior from the fit window.
- ar_greedy / ar_ps: joint filter with diagonal innovation covariance (temporal only).
- st_greedy / st_ps / st_ts / st_ucb: joint filter with the graph-shrunk covariance (I-coeng).
  st_ts samples the whole current-reward posterior, including the fresh daily shock.
  st_ps ("persistent sampling") samples only the long-run means and sets the fluctuation to
  its conditional mean given them: the Predictive Sampling principle [P] of not exploring
  information that will not persist.
- st_ps_rewired, st_ps_nograph: st_ps with a rewired graph, or the common factor only.
The burn-in over the fit window (every video observed every day) is identical across seeds
and policies sharing a covariance variant, so it is cached per (origin, variant).
Regret: the oracle's top-k sum of true rewards minus the chosen sum, per day.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "st_toy"))
from data import CACHE, RESULTS, raw_file  # noqa: E402
from graphs import build, load_features, rewire, scaled_laplacian  # noqa: E402
from toy import Filter, stationary_lag_cov  # noqa: E402

SEED = 20261009
LAGS = (1, 2, 7)
P_LAG = max(LAGS)
K_SLOTS = 10
S_OBS = 0.05
ORIGINS = (28, 35, 42)
POLICIES = ("fit_mean", "last_value", "ts_iid", "ar_greedy", "ar_ps", "st_greedy", "st_ps", "st_ts", "st_ucb",
            "st_ps_rewired", "st_ps_nograph")
DETERMINISTIC = ("fit_mean", "last_value", "ar_greedy", "st_greedy", "st_ucb", "st_ucbm1", "st_ucbm2",
                 "dr1_greedy", "dr2_greedy", "dr3_greedy", "dr1_ucbm1", "dr2_ucbm1", "dr3_ucbm1")
# Follow-up (9 October evening): joint predictive sampling and tuned UCB, as in the toy, and a
# drifting long-run level (random walk with per-day variance DRIFTS[k]) for lifecycle drift.
DRIFTS = {1: 0.0005, 2: 0.002, 3: 0.008}
EXTRA = ("st_jps", "st_ucbm1", "st_ucbm2") + tuple(f"dr{k}_{kind}" for k in DRIFTS for kind in ("greedy", "jps", "ucbm1"))
FILTER_CACHE = CACHE / "daily_filters"


class DriftFilter(Filter):
    """Joint filter whose long-run levels follow a random walk: mu_t = mu_{t-1} + omega_t."""

    def __init__(self, *args, drift: float = 0.0, **kw):
        super().__init__(*args, **kw)
        self.drift = drift

    def propagate(self):
        super().propagate()
        if self.drift:
            self.P[np.diag_indices(self.N)] += self.drift


def variant_of(policy: str) -> str:
    if policy.startswith("dr"):
        return f"st_d{policy[2]}"
    if policy.startswith("ar_"):
        return "ar"
    if policy.endswith("_rewired"):
        return "rewired"
    if policy.endswith("_nograph"):
        return "nograph"
    return "st"


def burnin(origin: int, variant: str):
    """Filter after observing every video on every fit-window day (cached)."""
    Y, keep, nodes = panel()
    N = Y.shape[1]
    path = FILTER_CACHE / f"F{origin}_{variant}.npz"
    grng = np.random.default_rng(SEED + origin)
    C_G = np.eye(N) if variant in ("ar", "nograph") else graph_corr("I-coeng", nodes, grng, 5.0,
                                                                         rewired=variant == "rewired")
    m, a, Q, info = fit_model(Y[:origin], C_G)
    if variant == "ar":
        Q = np.diag(np.diag(Q))
    drift = DRIFTS[int(variant[-1])] if variant.startswith("st_d") else 0.0
    K_mu = np.eye(N) * Y[:origin].mean(0).var()  # prior spread of long-run means across videos
    # Stationary lag covariance: scalar AR(p) lag covariance (unit innovations) kron Q.
    flt = DriftFilter(a, N, K_mu, np.kron(stationary_lag_cov(a), Q), Q, S_OBS, drift=drift)
    if path.exists():
        z = np.load(path)
        flt.b, flt.P = z["b"], z["P"]
        info["fit_loglik_last7"] = float(z["loglik"]) if "loglik" in z else np.nan
        return flt, info
    flt.b[:N] = Y[:origin].mean(0).mean()  # prior mean: platform average
    noise = S_OBS * np.random.default_rng(SEED + 7 * origin).standard_normal((origin, N))
    loglik = 0.0
    for t in range(origin):
        for i in range(N):
            if t >= origin - 7:  # one-step predictive log-likelihood on the last 7 fit days
                m_i = flt.b[i] + flt.b[N + i]
                v_i = flt.P[i, i] + 2 * flt.P[i, N + i] + flt.P[N + i, N + i] + flt.r
                loglik += -0.5 * (np.log(2 * np.pi * v_i) + (Y[t, i] + noise[t, i] - m_i) ** 2 / v_i)
            flt.update(i, Y[t, i] + noise[t, i])
        flt.propagate()
    FILTER_CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(path, b=flt.b, P=flt.P, loglik=loglik)
    info["fit_loglik_last7"] = loglik
    return flt, info


@lru_cache(maxsize=1)
def panel():
    d = pd.read_csv(raw_file("item_daily_features.csv"), usecols=["video_id", "date", "play_cnt", "complete_play_cnt"])
    ev = np.load(CACHE / "eval_matrix.npz")["videos"]
    days = np.sort(d.date.unique())
    full = d.groupby("video_id").date.nunique()
    keep = np.intersect1d(ev, full[full == len(days)].index)
    d = d[d.video_id.isin(keep)]
    rate = (d.complete_play_cnt + 0.5) / (d.play_cnt + 1)
    Y = (pd.DataFrame({"v": d.video_id, "t": d.date, "y": np.log(rate / (1 - rate))})
         .pivot(index="t", columns="v", values="y").loc[days, keep].to_numpy())
    return Y, keep, np.searchsorted(ev, keep)


def graph_corr(name: str, nodes, rng, gamma: float, rewired: bool = False) -> np.ndarray:
    W = build(load_features(), name, 10, rng, nodes)
    if rewired:
        W = rewire(W, rng)
    L = scaled_laplacian(W).toarray()
    K = np.linalg.inv(np.eye(len(nodes)) + gamma * L)
    d = np.sqrt(np.diag(K))
    return K / d[:, None] / d[None, :]


def fit_model(Y_fit: np.ndarray, C_G: np.ndarray):
    """AR coefficients on lags LAGS, innovation covariance shrunk toward a graph target."""
    m = Y_fit.mean(axis=0)
    X = Y_fit - m
    rows = range(P_LAG, len(X))
    A = np.stack([np.stack([X[t - l] for l in LAGS], axis=1) for t in rows])  # (T', N, |LAGS|)
    y = np.stack([X[t] for t in rows])
    coef = np.linalg.lstsq(A.reshape(-1, len(LAGS)), y.reshape(-1), rcond=None)[0]
    a = np.zeros(P_LAG)
    for l, c in zip(LAGS, coef):
        a[l - 1] = c
    E = y - np.einsum("tnl,l->tn", A, coef)
    s = E.var()
    R = np.corrcoef(E.T)
    c_common = float(np.clip(R[np.triu_indices_from(R, 1)].mean(), 0, 0.9))
    target = s * ((1 - c_common) * C_G + c_common)
    np.fill_diagonal(target, s)
    tr, te = E[:-5], E[-5:]
    S_tr = tr.T @ tr / len(tr)
    best, best_ll = None, -np.inf
    for w in (0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99):
        Q = (1 - w) * S_tr + w * target
        sign, logdet = np.linalg.slogdet(Q)
        ll = -0.5 * (len(te) * logdet + np.einsum("ti,ij,tj->", te, np.linalg.inv(Q), te))
        if sign > 0 and ll > best_ll:
            best, best_ll = w, ll
    S = E.T @ E / len(E)
    Q = (1 - best) * S + best * target
    radius = np.max(np.abs(np.linalg.eigvals(np.vstack([a, np.eye(P_LAG)[:-1]]))))
    return m, a, Q, {"shrink_weight": best, "common_corr": c_common, "innov_var": s, "ar_radius": radius,
                     "coef": dict(zip(LAGS, np.round(coef, 3)))}


def run(args):
    origin, seed, policy = args
    t0 = time.time()
    Y, keep, nodes = panel()
    T_all, N = Y.shape
    rng = np.random.default_rng(SEED + 100 * origin + seed)
    noise = S_OBS * rng.standard_normal(Y.shape)
    test = range(origin, T_all)
    regret = []
    info = {}

    if policy.startswith(("st_", "ar_", "dr")):
        flt, info = burnin(origin, variant_of(policy))
        kind = policy.split("_", 1)[1]
        for t in test:
            mean, S, _ = flt.reward_mean_cov()
            if kind == "greedy":
                score = mean
            elif kind == "ucb":
                score = mean + 2.0 * np.sqrt(np.maximum(np.diag(S), 0))
            elif kind.startswith("ucbm"):
                score = mean + float(kind[4:]) * np.sqrt(np.maximum(np.diag(S), 0))
            elif kind == "jps":
                # Joint predictive sampling (as in experiments/st_toy): sample only the part of the
                # current-reward uncertainty that next round's rewards would reveal.
                _, HAP = flt.next_projection()
                Cn = (HAP[:, :N] + HAP[:, N:2 * N]).T
                Hb = HAP.reshape(N, flt.p + 1, N)
                V = Hb[:, 0, :] + np.tensordot(Hb[:, 1:, :], flt.a, axes=([1], [0])) + flt.Q
                if getattr(flt, "drift", 0.0):
                    V = V + flt.drift * np.eye(N)
                B = Cn @ np.linalg.solve(V + 1e-9 * np.eye(N), Cn.T)
                w, U = np.linalg.eigh((B + B.T) / 2)
                score = mean + U @ (np.sqrt(np.maximum(w, 0)) * rng.standard_normal(N))
            elif kind == "ts":
                score = mean + np.linalg.cholesky(S + 1e-9 * np.eye(N)) @ rng.standard_normal(N)
            else:  # ps: sample the long-run means, condition the current fluctuation on them
                Pmm = flt.P[:N, :N]
                Pzm = flt.P[N:2 * N, :N]
                draw = flt.b[:N] + np.linalg.cholesky(Pmm + 1e-10 * np.eye(N)) @ rng.standard_normal(N)
                z_cond = flt.b[N:2 * N] + Pzm @ np.linalg.solve(Pmm + 1e-10 * np.eye(N), draw - flt.b[:N])
                score = draw + z_cond
            chosen = np.argsort(-score)[:K_SLOTS]
            for i in chosen:
                flt.update(int(i), Y[t, i] + noise[t, i])
            flt.propagate()
            regret.append(np.sort(Y[t])[-K_SLOTS:].sum() - Y[t, chosen].sum())
    else:
        m = Y[:origin].mean(0)
        last = Y[origin - 1].copy()
        n = np.full(N, float(origin))
        s = Y[:origin].sum(0)
        var_y = Y[:origin].var(0).mean()
        for t in test:
            if policy == "fit_mean":
                score = m
            elif policy == "last_value":
                score = last
            else:  # ts_iid
                prec = n / var_y
                score = s / n + rng.standard_normal(N) / np.sqrt(prec)
            chosen = np.argsort(-score)[:K_SLOTS]
            obs = Y[t, chosen] + noise[t, chosen]
            last[chosen] = obs
            n[chosen] += 1
            s[chosen] += obs
            regret.append(np.sort(Y[t])[-K_SLOTS:].sum() - Y[t, chosen].sum())

    row = {"origin": origin, "seed": seed, "policy": policy, "test_days": len(regret),
           "regret_per_day": float(np.mean(regret)), "seconds": round(time.time() - t0, 1), **info}
    print(f"F={origin} seed={seed} {policy}: {row['regret_per_day']:.3f}/day", flush=True)
    return row


def burnin_task(args):
    origin, variant = args
    t0 = time.time()
    burnin(origin, variant)
    print(f"burn-in F={origin} {variant}: {time.time() - t0:.0f}s", flush=True)


def main(seeds: int, jobs: int, extra: bool = False) -> None:
    panel()
    load_features()
    variants = ("st", "st_d1", "st_d2", "st_d3") if extra else ("st", "ar", "rewired", "nograph")
    with ProcessPoolExecutor(jobs) as ex:
        list(ex.map(burnin_task, [(o, v) for o in ORIGINS for v in variants]))
    tasks = [(o, s, p) for o in ORIGINS for s in range(seeds) for p in (EXTRA if extra else POLICIES)
             if not (p in DETERMINISTIC and s > 0)]
    tasks.sort(key=lambda x: not (x[2].startswith("st_") or x[2].startswith("ar_")))
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(run, tasks, chunksize=1))
    pd.DataFrame(rows).to_csv(RESULTS / ("daily_runs_extra.csv" if extra else "daily_runs.csv"), index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--extra", action="store_true", help="joint predictive sampling, tuned UCB, drifting level")
    a = ap.parse_args()
    main(a.seeds, a.jobs, a.extra)
