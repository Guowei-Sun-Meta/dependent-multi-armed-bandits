"""Experiments 1 and 2 on KuaiRec: the daily trending slot under a chronological protocol,
with standard baselines.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct10_evening/code/daily_chrono.py --jobs 3

What changes from kuairec/code/daily.py (retrospective):
- Graph. I-coeng is rebuilt at every cutoff from big-matrix rows dated before the first test
  day, still from non-evaluation users only (IDF-weighted engagement, cosine, k = 10 kNN on
  the panel's videos). The rewired control rewires that prefix graph.
- Eligibility. Evaluation videos with at least 10 plays on every fit-window day, known at the
  cutoff. No survival over the test window is required.
- Availability is not known in advance. A video chosen on a test day with no plays (or no row)
  that day returns no observation, and its slot earns that day's median reward among available
  videos. The oracle picks the top k among available videos. Counts are reported.
- Windows and panels. Test windows of 11 days after origins F = 30, 41, 52 (days 31-41, 42-52,
  53-63; disjoint), each fitted on days 1..F. At each origin, up to 250 eligible videos are drawn
  (seeded) and dealt into 5 disjoint panels of up to 50, stratified by prefix popularity within
  prefix-graph communities. 15 panel-window units; budgets k = 1 and 5 videos per day.
- Tuning. Every hyperparameter (EWMA half-life, discount, window, UCB multiplier) is chosen on a
  development window, days 20-30 fitted on days 1-19 with the origin-30 panels, then frozen.
- Policies.
  Baselines: static (fit-window mean), last_value, seasonal (most recent observation on the same
  weekday), ewma, ts_iid (Gaussian TS), dts (discounted Gaussian TS), swucb (sliding-window UCB).
  Filters (from daily.py; lags 1, 2, 7; burn-in on the full fit window): ar_greedy and ar_ucb
  (temporal only), st_greedy and st_ucb (prefix I-coeng shrinkage), st_ucb_rewired,
  st_ucb_nograph (common factor only).
Reward: logit of the daily complete-play rate, observation noise sd 0.05 (as in daily.py).
Regret: per day per slot, oracle top-k sum minus the chosen sum.
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
KC = HERE.parents[1] / "kuairec" / "code"
sys.path.insert(0, str(KC))
sys.path.insert(0, str(HERE.parents[1] / "simulations" / "spatiotemporal_benchmark" / "code"))
from data import CACHE, raw_file  # noqa: E402
from graphs import ENGAGED, cosine_sim, idf_weight, knn_from_similarity, rewire, scaled_laplacian, sparse_matrix  # noqa: E402
from daily import fit_model, LAGS, P_LAG, S_OBS  # noqa: E402
from toy import Filter, stationary_lag_cov  # noqa: E402

RESULTS = HERE.parent / "results" / "daily_chrono"
UNITS = RESULTS / "units.npz"
SEED = 20261010
ORIGINS = (30, 41, 52)
DEV = (19, 30)  # fit days 1..19, development test days 20..30
TEST_LEN = 11
N_PANELS, PANEL = 5, 50
BUDGETS = (1, 5)
SEEDS = 5
GRID = {"ewma": (1, 3, 7, 14), "dts": (0.5, 0.7, 0.9, 0.97), "swucb": (3, 7, 14), "ucb": (0.5, 1.0, 2.0)}
FILTER_POLICIES = ("ar_greedy", "ar_ucb", "st_greedy", "st_ucb", "st_ucb_rewired", "st_ucb_nograph")
BASELINES = ("static", "last_value", "seasonal", "ewma", "ts_iid", "dts", "swucb")


# ---------------------------------------------------------------- data and units


def daily_panel():
    d = pd.read_csv(raw_file("item_daily_features.csv"), usecols=["video_id", "date", "play_cnt", "complete_play_cnt"])
    days = np.sort(d.date.unique())
    ev = np.load(CACHE / "eval_matrix.npz")["videos"]
    d = d[d.video_id.isin(ev)]
    plays = d.pivot_table(index="date", columns="video_id", values="play_cnt", aggfunc="sum").reindex(days)
    comp = d.pivot_table(index="date", columns="video_id", values="complete_play_cnt", aggfunc="sum").reindex(days)
    plays, comp = plays.reindex(columns=ev), comp.reindex(columns=ev)
    rate = (comp + 0.5) / (plays + 1)
    Y = np.log(rate / (1 - rate)).to_numpy()
    P = plays.to_numpy()
    Y[~(P > 0)] = np.nan  # zero plays or no row: unavailable that day
    return days, ev, Y, P


def prefix_graph(big, ev_users, videos, cutoff_date, rng):
    vb = big[(~np.isin(big.user_id, ev_users)) & (big.date < cutoff_date)]
    Ev = sparse_matrix(vb, "video_id", np.sort(videos), "user_id", (vb.watch_ratio.to_numpy() >= ENGAGED).astype(float))
    order = np.searchsorted(np.sort(videos), videos)
    S = cosine_sim(idf_weight(Ev)[order])
    W = knn_from_similarity(S, 10, rng)
    return W, int(len(vb))


def build_units():
    """Panels, prefix graphs and reward matrices for the development and test windows."""
    days, ev, Y, P = daily_panel()
    z = np.load(CACHE / "eval_matrix.npz")
    ev_users = z["users"]
    big = pd.read_csv(raw_file("big_matrix.csv"), usecols=["user_id", "video_id", "watch_ratio", "date"],
                      dtype={"user_id": np.int32, "video_id": np.int32, "watch_ratio": np.float32, "date": np.int64})
    big = big[np.isin(big.video_id, ev)]
    out, meta = {}, []
    from sklearn.cluster import KMeans
    for origin in ORIGINS:
        rng = np.random.default_rng(SEED + origin)
        elig = np.flatnonzero((P[:origin] >= 10).all(0))
        n_pick = min(N_PANELS * PANEL, len(elig) // N_PANELS * N_PANELS)
        pick = np.sort(rng.choice(elig, size=n_pick, replace=False))
        vids = ev[pick]
        W_all, n_rows = prefix_graph(big, ev_users, vids, days[origin], rng)
        # Communities of the prefix graph: k-means on the bottom eigenvectors of its Laplacian.
        L = scaled_laplacian(W_all).toarray()
        w, V = np.linalg.eigh(L)
        comm = KMeans(5, n_init=10, random_state=SEED).fit_predict(V[:, 1:6])
        pop = P[:origin, pick].mean(0)
        order = np.lexsort((-pop, comm))
        panels = [np.sort(pick[order[j::N_PANELS]]) for j in range(N_PANELS)]
        windows = [("test", origin, origin, origin + TEST_LEN)]
        if origin == ORIGINS[0]:
            windows.insert(0, ("dev", origin, DEV[0], DEV[1]))
        for kind, o, F, end in windows:
            for j, cols in enumerate(panels):
                vids_p = ev[cols]
                grng = np.random.default_rng(SEED + 7 * F + j)
                W, n_rows = prefix_graph(big, ev_users, vids_p, days[F], grng)
                Wr = rewire(W, grng)
                key = f"{kind}_F{F}_p{j}"
                out[f"{key}_Y"] = Y[:end, cols]
                out[f"{key}_W"] = W.toarray()
                out[f"{key}_Wr"] = Wr.toarray()
                miss = int(np.isnan(Y[F:end, cols]).sum())
                meta.append({"unit": key, "kind": kind, "origin": o, "fit_days": F, "test_days": f"{F + 1}-{end}",
                             "cutoff_date": int(days[F]), "videos": len(cols), "eligible_at_origin": int(len(elig)),
                             "graph_rows_before_cutoff": n_rows, "unavailable_test_cells": miss,
                             "graph_edges": int((W.toarray() > 0).sum() // 2)})
    RESULTS.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(UNITS, **out)
    pd.DataFrame(meta).to_csv(RESULTS / "units.csv", index=False)
    return pd.DataFrame(meta)


# ---------------------------------------------------------------- policies


def graph_corr(W, gamma=5.0):
    import scipy.sparse as sp
    L = scaled_laplacian(sp.csr_matrix(W)).toarray()
    K = np.linalg.inv(np.eye(len(W)) + gamma * L)
    d = np.sqrt(np.diag(K))
    return K / d[:, None] / d[None, :]


def make_filter(Yfit, C_G, diag=False):
    N = Yfit.shape[1]
    m, a, Q, info = fit_model(Yfit, C_G)
    if diag:
        Q = np.diag(np.diag(Q))
    flt = Filter(a, N, np.eye(N) * Yfit.mean(0).var(), np.kron(stationary_lag_cov(a), Q), Q, S_OBS)
    flt.b[:N] = Yfit.mean()
    return flt


def run_unit(task):
    key, policy, param, k, seed = task
    z = np.load(UNITS)
    Y, W, Wr = z[f"{key}_Y"], z[f"{key}_W"], z[f"{key}_Wr"]
    F = int(key.split("_F")[1].split("_")[0])
    T, N = Y.shape
    rng = np.random.default_rng([SEED, seed, F, k, hash(policy) % 997])
    noise = S_OBS * np.random.default_rng([SEED, seed, F]).standard_normal(Y.shape)
    Yfit = Y[:F]
    obs_hist = [list(Yfit[:, i] + noise[:F, i]) for i in range(N)]  # full fit-window history
    obs_day = [list(range(F)) for _ in range(N)]
    reg, unavailable_picks = [], 0
    flt = None
    if policy.startswith(("ar_", "st_")):
        C_G = np.eye(N) if policy.startswith("ar_") or policy.endswith("nograph") else graph_corr(Wr if policy.endswith("rewired") else W)
        flt = make_filter(Yfit, C_G, diag=policy.startswith("ar_"))
        for t in range(F):
            for i in range(N):
                flt.update(i, Yfit[t, i] + noise[t, i])
            flt.propagate()
    var_y = np.nanvar(Yfit - Yfit.mean(0))
    for t in range(F, T):
        if flt is not None:
            mean, S, _ = flt.reward_mean_cov()
            score = mean + (param * np.sqrt(np.maximum(np.diag(S), 0)) if "ucb" in policy else 0.0)
        elif policy == "static":
            score = Yfit.mean(0)
        elif policy == "last_value":
            score = np.array([h[-1] for h in obs_hist])
        elif policy == "seasonal":
            score = np.array([next((obs_hist[i][j] for j in range(len(obs_day[i]) - 1, -1, -1)
                                    if (t - obs_day[i][j]) % 7 == 0), obs_hist[i][-1]) for i in range(N)])
        elif policy == "ewma":
            lam = 0.5 ** (1 / param)
            score = np.empty(N)
            for i in range(N):
                wts = lam ** (t - np.array(obs_day[i]))
                score[i] = wts @ np.array(obs_hist[i]) / wts.sum()
        elif policy in ("ts_iid", "dts", "swucb"):
            mu_hat, n_eff = np.empty(N), np.empty(N)
            for i in range(N):
                age = t - np.array(obs_day[i])
                if policy == "ts_iid":
                    wts = np.ones_like(age, dtype=float)
                elif policy == "dts":
                    wts = param ** age
                else:
                    wts = (age <= param).astype(float)
                n_eff[i] = wts.sum()
                mu_hat[i] = wts @ np.array(obs_hist[i]) / max(n_eff[i], 1e-9) if n_eff[i] > 0 else np.inf
            sd = np.sqrt(var_y / np.maximum(n_eff, 1e-9))
            if policy == "swucb":
                score = np.where(n_eff > 0, mu_hat + GRID_UCB_SW * sd, np.inf)
            else:
                score = mu_hat + sd * rng.standard_normal(N)
        else:
            raise ValueError(policy)
        chosen = np.argsort(-score)[:k]
        avail = ~np.isnan(Y[t])
        yt = np.where(avail, Y[t], np.nan)
        fill = np.nanmedian(yt)
        got = np.where(avail[chosen], yt[chosen], fill)
        unavailable_picks += int((~avail[chosen]).sum())
        reg.append((np.sort(yt[avail])[-k:].sum() - got.sum()) / k)
        for i in chosen:
            if avail[i]:
                y = Y[t, i] + noise[t, i]
                obs_hist[i].append(y)
                obs_day[i].append(t)
                if flt is not None:
                    flt.update(int(i), y)
        if flt is not None:
            flt.propagate()
    return {"unit": key, "policy": policy, "param": param, "k": k, "seed": seed,
            "regret_per_slot_day": float(np.mean(reg)), "unavailable_picks": unavailable_picks}


GRID_UCB_SW = 1.0  # exploration multiplier for sliding-window UCB (its window is the tuned parameter)


def tasks_for(keys, policies_params, seeds=SEEDS):
    out = []
    for key in keys:
        for k in BUDGETS:
            for pol, params in policies_params.items():
                for prm in params:
                    for s in range(seeds):
                        out.append((key, pol, prm, k, s))
    return out


def pool(tasks, jobs):
    with ProcessPoolExecutor(jobs) as ex:
        return pd.DataFrame(list(ex.map(run_unit, tasks, chunksize=2)))


def main(jobs):
    meta = build_units() if not UNITS.exists() else pd.read_csv(RESULTS / "units.csv")
    print(meta.to_string(), flush=True)
    dev_keys = meta[meta.kind == "dev"].unit.tolist()
    test_keys = meta[meta.kind == "test"].unit.tolist()
    # Development: tune every hyperparameter per budget, freeze.
    t0 = time.time()
    dev_pp = {"ewma": GRID["ewma"], "dts": GRID["dts"], "swucb": GRID["swucb"],
              "ar_ucb": GRID["ucb"], "st_ucb": GRID["ucb"]}
    dev = pool(tasks_for(dev_keys, dev_pp), jobs)
    dev.to_csv(RESULTS / "dev_runs.csv", index=False)
    tuned = {}
    for k in BUDGETS:
        g = dev[dev.k == k].groupby(["policy", "param"]).regret_per_slot_day.mean().reset_index()
        for pol in dev_pp:
            row = g[g.policy == pol].sort_values("regret_per_slot_day").iloc[0]
            tuned[f"{pol}|{k}"] = float(row.param)
    (RESULTS / "tuned.json").write_text(json.dumps(tuned, indent=1))
    print("tuned:", tuned, f"({time.time() - t0:.0f}s)", flush=True)
    # Test: frozen parameters.
    tasks = []
    for key in test_keys:
        for k in BUDGETS:
            for pol in BASELINES + FILTER_POLICIES:
                tp = "st_ucb" if pol.startswith("st_ucb") else pol
                prm = tuned.get(f"{tp}|{k}", 0.0)
                for s in range(SEEDS):
                    tasks.append((key, pol, prm, k, s))
    test = pool(tasks, jobs)
    test.to_csv(RESULTS / "test_runs.csv", index=False)
    print(f"test done ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--units-only", action="store_true")
    a = ap.parse_args()
    if a.units_only:
        print(build_units().to_string())
    else:
        main(a.jobs)
