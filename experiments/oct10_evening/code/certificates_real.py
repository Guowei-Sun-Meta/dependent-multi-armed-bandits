"""Experiment 3b: certified pooling in worlds calibrated to real Wikipedia attention dynamics.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct10_evening/code/certificates_real.py --verify
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct10_evening/code/certificates_real.py --seeds 50 --jobs 3

World (fitted on the 2022-2023 prefix of the six-community panel, experiments/wikipedia/data):
- Arms: 30 articles, 5 per community (prefix-mean ranks 0, 5, 10, 15, 20 within each); the
  community is the pooling component. Reward x = log(1 + views), rescaled affinely so every
  long-run mean lies in [0, 1] (the bounded-mean setting of the certificates).
- True means: prefix means. Fluctuation: pooled AR(7) on prefix deviations; innovations are
    resample   real prefix residual vectors drawn independently over time (cross-sectional
               dependence and non-Gaussian marginals kept; temporal independence, as B1 assumes);
    gauss      Gaussian with the residual covariance;
    block      7-day blocks of consecutive real residual vectors (a stress test: breaks
               temporal independence of innovations).
  Observation noise sd 0.005 on the rescaled axis, known to the learner.
- Each day the learner observes a slate of k in {5, 10} articles. Horizon 730 days.
Learners (certificate):
    iid        sample means, iid radius with the prefix variance of x (sigma^2 known);
    known      innovation certificate (B1'') with the true AR(7) and covariance;
    fitted     AR(7) and covariance re-estimated from an independent simulated 365-day prefix;
    fitted_ar1 AR(1) fitted on that prefix (wrong order).
Policies: slate SP-UCB (top k of min(arm upper bound, component bound)) and slate successive
elimination (k least-sampled active arms). Component widths: oracle (true within-community
range of means). Measures: any certificate violation, best arm eliminated, mean regret.
The general-AR innovation regression extends coverage.InnovationRegression to AR(p) by an
augmented Kalman filter on the stacked lags; --verify checks it against the AR(1) class.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.linalg import solve_discrete_lyapunov

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "simulations" / "certificates_under_persistence" / "code"))

DATA = HERE.parents[1] / "wikipedia" / "data" / "six_domains"
RESULTS = HERE.parent / "results" / "certificates_real"
SEED = 20261011
P_AR = 7
R_OBS = 0.005
HORIZON = 730
PREFIX = 365
PER_COMM = 5


# ---------------------------------------------------------------- calibration


def fit_ar(X, p):
    """Pooled AR(p) on per-arm demeaned X (T x N); residuals and their covariance."""
    D = X - X.mean(0)
    T, N = D.shape
    A = np.stack([D[p - l - 1:T - l - 1] for l in range(p)], axis=2)  # (T-p, N, p)
    y = D[p:]
    coef = np.linalg.lstsq(A.reshape(-1, p), y.reshape(-1), rcond=None)[0]
    E = y - A @ coef
    return coef, E, np.cov(E.T)


def calibrate():
    v = pd.read_csv(DATA / "views.csv", index_col=0)
    v.index = pd.to_datetime(v.index.astype(str), format="%Y%m%d")
    dom = pd.read_csv(DATA / "domains.csv").set_index("title")["domain"]
    X = np.log1p(v[v.index.year <= 2023])
    m = X.mean()
    arts, labels = [], []
    for c, d in enumerate(sorted(dom.unique())):
        a = m[dom[dom == d].index.intersection(X.columns)].sort_values(ascending=False)
        pick = a.index[[0, 5, 10, 15, 20]][:PER_COMM]
        arts += list(pick)
        labels += [c] * len(pick)
    X = X[arts].to_numpy()
    mu_x = X.mean(0)
    L, U = mu_x.min() - 1.0, mu_x.max() + 1.0
    Xs = (X - L) / (U - L)
    coef, E, Q = fit_ar(Xs, P_AR)
    return {"articles": arts, "labels": np.array(labels), "mu": Xs.mean(0), "coef": coef, "E": E, "Q": Q,
            "var_x": float(Xs.var(0).mean()), "scale": (float(L), float(U))}


CAL = None


def cal():
    global CAL
    if CAL is None:
        CAL = calibrate()
    return CAL


def companion(coef, N):
    p = len(coef)
    A = np.zeros((N * p, N * p))
    for l, c in enumerate(coef):
        A[:N, l * N:(l + 1) * N] = c * np.eye(N)
    if p > 1:
        A[N:, :-N] = np.eye(N * (p - 1))
    return A


def simulate(seed, T, noise, coef, E, Q, burn=400):
    rng = np.random.default_rng(seed)
    N = Q.shape[0]
    p = len(coef)
    tot = burn + T
    if noise == "gauss":
        eps = rng.standard_normal((tot, N)) @ np.linalg.cholesky(Q + 1e-12 * np.eye(N)).T
    elif noise == "resample":
        eps = E[rng.integers(len(E), size=tot)]
    else:  # block: 7-day blocks of consecutive residual vectors
        starts = rng.integers(len(E) - 7, size=tot // 7 + 1)
        eps = np.concatenate([E[s:s + 7] for s in starts])[:tot]
    Z = np.zeros((tot, N))
    for t in range(tot):
        acc = eps[t].copy()
        for l in range(p):
            if t - l - 1 >= 0:
                acc += coef[l] * Z[t - l - 1]
        Z[t] = acc
    return Z[burn:]


# ---------------------------------------------------------------- general-AR innovation regression


class InnovationAR:
    """Augmented Kalman filter for y_{t,a} = mu_a + z_{t,a} + e, z a VAR(p) with diagonal pooled
    coefficients and innovation covariance Q. The stacked lag state s_t has predictive mean
    g + D mu and covariance P; each observation adds u u' to J and u R to q (B1 / [S])."""

    def __init__(self, coef, Q, alpha):
        N = Q.shape[0]
        p = len(coef)
        self.N, self.p = N, p
        self.A = companion(coef, N)
        Qb = np.zeros((N * p, N * p))
        Qb[:N, :N] = Q
        self.Qb = Qb
        self.P = solve_discrete_lyapunov(self.A, Qb)
        self.g = np.zeros(N * p)
        self.D = np.zeros((N * p, N))
        self.H = alpha * np.eye(N)
        self.J = self.H.copy()
        self.q = np.zeros(N)

    def observe(self, a, y):
        N = self.N
        u = np.eye(N)[a] + self.D[a]
        d = self.P[a, a] + R_OBS ** 2
        R = y - self.g[a]
        self.J += np.outer(u, u) / d
        self.q += u * R / d
        k = self.P[:, a] / d
        self.g = self.g + k * R
        self.D = self.D - np.outer(k, u)
        self.P = self.P - np.outer(self.P[:, a], self.P[a]) / d

    def propagate(self):
        self.g = self.A @ self.g
        self.D = self.A @ self.D
        self.P = self.A @ self.P @ self.A.T + self.Qb


def plugin_bounds(st, members, eps, delta, iters=5):
    """coverage.plugin_bounds (B1'') with N, components and widths passed in."""
    N, C = st.J.shape[0], len(members)
    alpha = st.H[0, 0]
    J = st.J
    G = J - alpha * np.eye(N)
    dlt = delta / (N + C)
    stat = lambda x: np.sqrt(2 * x * np.log(np.sqrt(x / alpha) / dlt))  # noqa: E731
    lo, hi = np.zeros(N), np.ones(N)
    Jd = np.diag(J)
    Goff = G - np.diag(np.diag(G))
    off = np.abs(Goff)
    for _ in range(iters):
        m, h = (lo + hi) / 2, (hi - lo) / 2
        mu_hat = (st.q - Goff @ m) / Jd
        rad = (stat(Jd) + alpha + off @ h) / Jd
        lo, hi = np.maximum(lo, mu_hat - rad), np.minimum(hi, mu_hat + rad)
    arm_lo, arm_hi = mu_hat - rad, mu_hat + rad
    Pm = np.zeros((N, C))
    for c, mem in enumerate(members):
        Pm[mem, c] = 1.0
    Gx = Pm.T @ G @ Pm
    Jx = np.diag(Gx) + alpha
    qx = Pm.T @ st.q
    Gxo = Gx - np.diag(np.diag(Gx))
    half = np.zeros(N)
    for c, mem in enumerate(members):
        half[mem] = eps[c] / 2
    dev = np.abs(Pm.T @ G) @ half  # sum_i |(P'G)_ci| eps_c(i) / 2
    tlo, thi = np.zeros(C), np.ones(C)
    for _ in range(iters):
        m, h = (tlo + thi) / 2, (thi - tlo) / 2
        th_hat = (qx - Gxo @ m) / Jx
        rad = (stat(Jx) + alpha + np.abs(Gxo) @ h + dev) / Jx
        tlo, thi = np.maximum(tlo, th_hat - rad), np.minimum(thi, th_hat + rad)
    return arm_lo, arm_hi, th_hat + rad + eps / 2


# ---------------------------------------------------------------- runs


def run(task):
    noise, learner, policy, k, seed = task
    t0 = time.time()
    c = cal()
    mu, labels, coef, E, Q = c["mu"], c["labels"], c["coef"], c["E"], c["Q"]
    N = len(mu)
    C = labels.max() + 1
    members = [np.flatnonzero(labels == j) for j in range(C)]
    eps = np.array([np.ptp(mu[m]) for m in members])
    v_c = np.array([mu[m].max() for m in members])
    rng = np.random.default_rng([SEED, seed])
    Z = simulate(SEED + 1000 * seed, HORIZON, noise, coef, E, Q)
    Y = mu + Z + R_OBS * rng.standard_normal(Z.shape)
    delta = 0.05
    st = None
    if learner == "known":
        st = InnovationAR(coef, Q, 1.0 / N)
    elif learner.startswith("fitted"):
        Zp = simulate(SEED + 1000 * seed + 7, PREFIX, noise, coef, E, Q)
        Xp = mu + Zp + R_OBS * rng.standard_normal(Zp.shape)
        cf, _, Qf = fit_ar(Xp, 1 if learner.endswith("ar1") else P_AR)
        st = InnovationAR(cf, Qf, 1.0 / N)
    sigma2 = c["var_x"] + R_OBS ** 2
    ell = np.log(2 * (N + C) * HORIZON * k / delta)
    n, s = np.zeros(N), np.zeros(N)
    Nc, Sc = np.zeros(C), np.zeros(C)
    best_k = np.sort(mu)[-k:].sum()
    best = int(np.argmax(mu))
    active = np.ones(N, bool)
    reg = np.zeros(HORIZON)
    viol_days, first_viol, best_out = 0, -1, -1
    for t in range(HORIZON):
        if st is None:
            rad = np.sqrt(2 * sigma2 * ell / np.maximum(n, 1))
            lo = np.where(n > 0, s / np.maximum(n, 1) - rad, -np.inf)
            hi = np.where(n > 0, s / np.maximum(n, 1) + rad, np.inf)
            pool = np.where(Nc > 0, Sc / np.maximum(Nc, 1) + np.sqrt(2 * sigma2 * ell / np.maximum(Nc, 1)) + eps, np.inf)
        else:
            lo, hi, pool = plugin_bounds(st, members, eps, delta)
        comp_up = np.array([min(hi[m].max(), pool[j]) for j, m in enumerate(members)])
        viol = (hi < mu - 1e-12).any() or (comp_up < v_c - 1e-12).any()
        viol_days += int(viol)
        if viol and first_viol < 0:
            first_viol = t
        if policy == "sp":
            score = np.minimum(hi, comp_up[labels])
            chosen = np.argsort(-score + 1e-12 * rng.random(N))[:k]
        else:
            best_lo = np.sort(lo[active])[-min(k, active.sum())]  # k-th best lower bound among active
            for j, m in enumerate(members):
                if comp_up[j] < best_lo:
                    active[m] = False
            active &= ~(hi < best_lo)
            if active.sum() < k:
                active[np.argsort(-hi)[:k]] = True
            if not active[best] and best_out < 0:
                best_out = t
            cand = np.flatnonzero(active)
            chosen = cand[np.argsort(n[cand] + 1e-9 * rng.random(len(cand)))[:k]]
        for a in chosen:
            y = Y[t, a]
            n[a] += 1
            s[a] += y
            Nc[labels[a]] += 1
            Sc[labels[a]] += y
            if st is not None:
                st.observe(int(a), y)
        if st is not None:
            st.propagate()
        reg[t] = best_k - mu[chosen].sum()
    cum = np.cumsum(reg)
    return {"noise": noise, "learner": learner, "policy": policy, "k": k, "seed": seed,
            "any_violation": viol_days > 0, "violation_share": viol_days / HORIZON, "first_violation": first_viol,
            "best_eliminated": (best_out >= 0) if policy == "se" else np.nan, "best_eliminated_at": best_out,
            "regret@365": float(cum[364]), "regret@730": float(cum[-1]), "active_at_end": int(active.sum()),
            "seconds": round(time.time() - t0, 1)}


def verify():
    """InnovationAR with p = 1 against coverage.InnovationRegression on the same observations."""
    import coverage as cv
    rng = np.random.default_rng(3)
    N, phi = 6, 0.8
    C = np.eye(N) * 0.7 + 0.3
    q = 1 - phi ** 2
    cv_N = cv.N
    global R_OBS
    r_save = R_OBS
    a = InnovationAR(np.array([phi]), q * C, alpha=1e-6)
    cv.N = N
    b = cv.InnovationRegression(phi, q * C, C, alpha=1e-6)
    R_OBS = cv.R_OBS
    for t in range(60):
        arm, y = int(rng.integers(N)), rng.standard_normal()
        a.observe(arm, y)
        a.propagate()
        b.observe(arm, y)
    cv.N = cv_N
    R_OBS = r_save
    assert np.allclose(a.J, b.J, atol=1e-8) and np.allclose(a.q, b.q, atol=1e-8), (np.abs(a.J - b.J).max())
    print("verify: InnovationAR(p=1) matches coverage.InnovationRegression (J and q) on 60 rounds")
    c = cal()
    rad = np.max(np.abs(np.linalg.eigvals(companion(c["coef"], 1))))
    print(f"calibration: {len(c['mu'])} arms, AR(7) coef {np.round(c['coef'], 3)}, radius {rad:.3f}, "
          f"lag-1 resid corr mean {np.corrcoef(c['E'].T)[np.triu_indices(len(c['mu']), 1)].mean():.3f}")


def main(seeds, jobs):
    RESULTS.mkdir(parents=True, exist_ok=True)
    c = cal()
    pd.DataFrame({"article": c["articles"], "community": c["labels"], "mu_rescaled": c["mu"]}).to_csv(
        RESULTS / "arms.csv", index=False)
    tasks = []
    for noise in ("resample", "gauss", "block"):
        for learner in ("iid", "known", "fitted", "fitted_ar1"):
            for policy in ("sp", "se"):
                for k in (5, 10):
                    for s in range(seeds):
                        tasks.append((noise, learner, policy, k, s))
    tasks.sort(key=lambda x: x[1] == "iid")
    print(f"{len(tasks)} runs", flush=True)
    rows, t0 = [], time.time()
    with ProcessPoolExecutor(jobs) as ex:
        for i, r in enumerate(ex.map(run, tasks, chunksize=2)):
            rows.append(r)
            if (i + 1) % 100 == 0:
                print(f"{i + 1}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
                pd.DataFrame(rows).to_csv(RESULTS / "runs.partial.csv", index=False)
    pd.DataFrame(rows).to_csv(RESULTS / "runs.csv", index=False)
    (RESULTS / "runs.partial.csv").unlink(missing_ok=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    if a.verify:
        verify()
    else:
        main(a.seeds, a.jobs)
