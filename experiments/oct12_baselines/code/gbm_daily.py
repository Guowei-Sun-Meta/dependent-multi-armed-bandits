"""Forecast-then-rank baseline on the chronological KuaiRec daily slot.

Usage (from the repo root; needs experiments/oct10_evening/results/daily_chrono/units.npz):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct12_baselines/code/gbm_daily.py --jobs 4

A practical alternative to bandit filters: a pooled gradient-boosted regressor
(scikit-learn HistGradientBoostingRegressor, default settings, fixed seed) forecasts each
video's reward today from lag features, and the policy shows the top k forecasts (greedy).
Features of video i on day t, computed from the observations available to the learner:
last observed value, its age in days, the value seven days earlier if observed, the mean and
count of observations in the last 7 days, the video's prefix mean, and the weekday.
Training uses fit-window days only. Because the fit window is fully observed while test days
are only observed when chosen, each training row hides the most recent a - 1 days for a random
age a in {1, ..., 10}, so the model learns to forecast from stale observations.
Units, availability rules, observation noise (sd 0.05, same seeds) and regret follow
experiments/oct10_evening/code/daily_chrono.py, so runs pair with its test_runs.csv.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "oct10_evening" / "code"))
sys.path.insert(0, str(HERE.parents[1] / "kuairec" / "code"))
sys.path.insert(0, str(HERE.parents[1] / "simulations" / "spatiotemporal_benchmark" / "code"))
import daily_chrono as dc  # noqa: E402

RESULTS = HERE.parent / "results"
MAX_AGE = 10


def features(hist_v, hist_d, t, prefix_mean, weekday):
    """hist_v/hist_d: observed values and days (< t) for one video."""
    if len(hist_d) == 0:
        return [np.nan, np.nan, np.nan, np.nan, 0, prefix_mean, weekday]
    d = np.asarray(hist_d)
    v = np.asarray(hist_v)
    last = v[-1]
    age = t - d[-1]
    lag7 = v[d == t - 7][0] if (d == t - 7).any() else np.nan
    recent = v[d >= t - 7]
    return [last, age, lag7, recent.mean() if len(recent) else np.nan, len(recent), prefix_mean, weekday]


def train_model(Yfit, noise_fit, rng):
    F, N = Yfit.shape
    prefix_mean = Yfit.mean(0)
    X, y = [], []
    for t in range(8, F):
        for i in range(N):
            a = int(rng.integers(1, MAX_AGE + 1))
            days = np.arange(0, t - a + 1)
            X.append(features(Yfit[days, i] + noise_fit[days, i], days, t, prefix_mean[i], t % 7))
            y.append(Yfit[t, i])
    m = HistGradientBoostingRegressor(random_state=0)
    m.fit(np.array(X, dtype=float), np.array(y))
    return m


def run(task):
    key, k, seed = task
    t0 = time.time()
    z = np.load(dc.UNITS)
    Y = z[f"{key}_Y"]
    F = int(key.split("_F")[1].split("_")[0])
    T, N = Y.shape
    noise = dc.S_OBS * np.random.default_rng([dc.SEED, seed, F]).standard_normal(Y.shape)
    model = train_model(Y[:F], noise[:F], np.random.default_rng([dc.SEED, seed, F, 99]))
    prefix_mean = Y[:F].mean(0)
    hv = [list(Y[:F, i] + noise[:F, i]) for i in range(N)]
    hd = [list(range(F)) for _ in range(N)]
    reg, unavailable = [], 0
    for t in range(F, T):
        Xt = np.array([features(hv[i], hd[i], t, prefix_mean[i], t % 7) for i in range(N)], dtype=float)
        score = model.predict(Xt)
        chosen = np.argsort(-score)[:k]
        avail = ~np.isnan(Y[t])
        yt = np.where(avail, Y[t], np.nan)
        fill = np.nanmedian(yt)
        got = np.where(avail[chosen], yt[chosen], fill)
        unavailable += int((~avail[chosen]).sum())
        reg.append((np.sort(yt[avail])[-k:].sum() - got.sum()) / k)
        for i in chosen:
            if avail[i]:
                hv[i].append(Y[t, i] + noise[t, i])
                hd[i].append(t)
    return {"unit": key, "policy": "gbm_greedy", "param": 0.0, "k": k, "seed": seed,
            "regret_per_slot_day": float(np.mean(reg)), "unavailable_picks": unavailable,
            "seconds": round(time.time() - t0, 1)}


def main(jobs):
    RESULTS.mkdir(parents=True, exist_ok=True)
    meta = pd.read_csv(dc.RESULTS / "units.csv")
    keys = meta[meta.kind == "test"].unit.tolist()
    tasks = [(u, k, s) for u in keys for k in dc.BUDGETS for s in range(dc.SEEDS)]
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(run, tasks, chunksize=2))
    pd.DataFrame(rows).to_csv(RESULTS / "gbm_daily_runs.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    if a.pilot:
        print(run(("test_F30_p0", 5, 0)))
    else:
        main(a.jobs)
