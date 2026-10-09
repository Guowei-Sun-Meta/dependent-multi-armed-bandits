"""Toy spatiotemporal bandit: 100 arms on a grid, AR(20) fluctuations, correlated innovations.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/st_toy/toy.py --verify
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/st_toy/toy.py --seeds 10 --horizon 2000 --jobs 2

World (restless; every arm evolves every round):
    f_{i,t} = mu_i + z_{i,t},  z_t = sum_{r=1}^{p} a_r z_{t-r} + eps_t,  eps_t ~ N(0, q C),
    Y_t = f_{a_t,t} + xi_t,  xi_t ~ N(0, s_obs^2).
- 100 arms on a 10 x 10 grid; C is the unit-diagonal graph resolvent (I + gamma L)^{-1}.
- a_r proportional to exp(-r / tau), summing to `persistence`; q sets Var(z) = 1.
- mu ~ N(0, s_mu^2 C): long-run means are smooth on the grid.
Dynamics, innovation covariance and noise are known to the model-based policies; means
are unknown (Gaussian prior). Regret is measured against the full-current-state oracle
max_i f_{i,t} ("dynamic regret") and against the best long-run mean ("mean regret").

Policies
- iid baselines: ucb (Gaussian UCB1), ts (Gaussian TS), swucb (sliding-window UCB).
- spatial only (iid noise): spectral_ucb / spectral_ts, a Bayesian graph prior on mu
  with noise variance Var(z) + s_obs^2 (GP-UCB/TS with a graph kernel).
- temporal only: ar_ts / ar_twostep, the exact AR(20) Kalman filter per arm with
  independent innovations and independent mean prior (spatial correlation ignored).
- spatiotemporal (the model): st_greedy, st_ts (joint posterior draw of current
  rewards), st_ucb (TV-GP-UCB-style index on the current state), st_twostep (the exact
  two-period score of research/spatiotemporal_bandits, rolled forward; the expectation
  of the max of lines uses a 256-point normal-quantile grid, checked against the exact
  upper-envelope formula).
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

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "research" / "st_toy" / "results"
SEED = 20261009
from scipy.stats import norm  # noqa: E402

GRID = 256
GH_Z = norm.ppf((np.arange(GRID) + 0.5) / GRID)  # equal-probability normal quantiles
GH_W = np.full(GRID, 1.0 / GRID)

POLICIES = ("ucb", "ts", "swucb", "spectral_ucb", "spectral_ts", "ar_ts", "ar_twostep",
            "st_greedy", "st_ts", "st_ucb", "st_twostep")


# ---------------------------------------------------------------- world


def grid_laplacian(side: int) -> np.ndarray:
    n = side * side
    W = np.zeros((n, n))
    for r in range(side):
        for c in range(side):
            i = r * side + c
            if c + 1 < side:
                W[i, i + 1] = W[i + 1, i] = 1
            if r + 1 < side:
                W[i, i + side] = W[i + side, i] = 1
    return np.diag(W.sum(1)) - W


def unit_diag(K: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.diag(K))
    return K / d[:, None] / d[None, :]


def ar_coefficients(p: int, persistence: float, tau: float) -> np.ndarray:
    w = np.exp(-np.arange(1, p + 1) / tau)
    return persistence * w / w.sum()


def companion(a: np.ndarray) -> np.ndarray:
    p = len(a)
    F = np.zeros((p, p))
    F[0] = a
    F[1:, :-1] = np.eye(p - 1)
    return F


def stationary_lag_cov(a: np.ndarray, iters: int = 60) -> np.ndarray:
    """Stationary covariance of (z_t, ..., z_{t-p+1}) for a scalar AR(p) with unit innovations."""
    F = companion(a)
    E = np.zeros_like(F)
    E[0, 0] = 1.0
    G, Fk = E.copy(), F.copy()
    for _ in range(iters):  # doubling: G = sum_k F^k E F^k'
        G = G + Fk @ G @ Fk.T
        Fk = Fk @ Fk
    return G


class World:
    def __init__(self, side=10, p=20, persistence=0.97, tau=6.0, gamma=5.0, s_mu=0.5, s_obs=0.3,
                 spatial=True, seed=0, T=2000):
        rng = np.random.default_rng(seed)
        self.N, self.p, self.T, self.s_obs = side * side, p, T, s_obs
        self.L = grid_laplacian(side)
        C = unit_diag(np.linalg.inv(np.eye(self.N) + gamma * self.L))
        self.C = C if spatial else np.eye(self.N)
        self.C_mu = unit_diag(np.linalg.inv(np.eye(self.N) + gamma * self.L))
        self.a = ar_coefficients(p, persistence, tau)
        G = stationary_lag_cov(self.a)
        self.q = 1.0 / G[0, 0]  # Var(z) = 1
        self.G = G * self.q
        self.Q = self.q * self.C
        self.s_mu = s_mu
        self.mu = s_mu * np.linalg.cholesky(self.C_mu) @ rng.standard_normal(self.N)
        # Stationary initial lags: Cov = G (lags) kron C (space).
        Lg, Lc = np.linalg.cholesky(self.G + 1e-12 * np.eye(p)), np.linalg.cholesky(self.C)
        lags = Lg @ rng.standard_normal((p, self.N)) @ Lc.T  # p x N, row 0 = z_t
        Lq = np.linalg.cholesky(self.Q)
        Z = np.zeros((T, self.N))
        for t in range(T):
            Z[t] = lags[0]
            new = self.a @ lags + Lq @ rng.standard_normal(self.N)
            lags = np.vstack([new, lags[:-1]])
        self.f = self.mu + Z
        self.noise = s_obs * rng.standard_normal((T, self.N))


# ---------------------------------------------------------------- joint Kalman filter


class Filter:
    """State x = (mu, z_t, z_{t-1}, ..., z_{t-p+1}), dimension N (p + 1)."""

    def __init__(self, a, N, K_mu, lag_cov, Q, s_obs):
        p = len(a)
        self.a, self.N, self.p, self.r = a, N, p, s_obs ** 2
        D = N * (p + 1)
        self.b = np.zeros(D)
        self.P = np.zeros((D, D))
        self.P[:N, :N] = K_mu
        self.P[N:, N:] = lag_cov
        self.Q = Q

    def reward_mean_cov(self):
        N = self.N
        m = self.b[:N] + self.b[N:2 * N]
        R = self.P[:N] + self.P[N:2 * N]  # rows of H P
        S = R[:, :N] + R[:, N:2 * N]  # H P H'
        return m, S, R

    def next_projection(self):
        """Rows of (H A) P and the next-round reward means (H A) b."""
        N, p = self.N, self.p
        Rb = self.P.reshape(p + 1, N, -1)
        HAP = Rb[0] + np.tensordot(self.a, Rb[1:], axes=1)
        bb = self.b.reshape(p + 1, N)
        ell = bb[0] + self.a @ bb[1:]
        return ell, HAP

    def update(self, arm, y):
        N = self.N
        Ph = self.P[:, arm] + self.P[:, N + arm]
        d = Ph[arm] + Ph[N + arm] + self.r
        self.b += Ph * ((y - self.b[arm] - self.b[N + arm]) / d)
        self.P -= np.outer(Ph, Ph / d)

    def propagate(self):
        N, p, a = self.N, self.p, self.a
        bb = self.b.reshape(p + 1, N)
        new0 = a @ bb[1:]
        bb[2:] = bb[1:-1].copy()
        bb[1] = new0
        D = self.P.shape[0]
        R = self.P.reshape(p + 1, N, D)
        row0 = np.tensordot(a, R[1:], axes=1)
        R[2:] = R[1:-1].copy()
        R[1] = row0
        Cv = self.P.reshape(D, p + 1, N)
        col0 = np.tensordot(Cv[:, 1:, :], a, axes=([1], [0]))
        Cv[:, 2:, :] = Cv[:, 1:-1, :].copy()
        Cv[:, 1, :] = col0
        self.P[N:2 * N, N:2 * N] += self.Q


def expected_max_lines(ell, U):
    """E_Z max_j (ell_j + U[j, a] Z) for every column a (normal-quantile grid)."""
    vals = ell[:, None, None] + U[:, :, None] * GH_Z[None, None, :]
    return vals.max(axis=0) @ GH_W


# ---------------------------------------------------------------- policies


def run_policy(world: World, policy: str, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    N, T = world.N, world.T
    var_y = 1.0 + world.s_obs ** 2  # marginal variance of an observation around mu
    regret_dyn, regret_mu = np.zeros(T), np.zeros(T)
    best_mu = world.mu.max()

    if policy.startswith("st_") or policy.startswith("ar_"):
        spatial = policy.startswith("st_")
        K_mu = world.s_mu ** 2 * (world.C_mu if spatial else np.eye(N))
        C = world.C if spatial else np.eye(N)
        flt = Filter(world.a, N, K_mu, np.kron(world.G, C), world.q * C, world.s_obs)
        kind = policy.split("_", 1)[1]
        for t in range(T):
            m, S, _ = flt.reward_mean_cov()
            if kind == "greedy":
                arm = int(np.argmax(m))
            elif kind == "ts":
                Lc = np.linalg.cholesky(S + 1e-9 * np.eye(N)) if spatial else None
                draw = m + (Lc @ rng.standard_normal(N) if spatial else np.sqrt(np.maximum(np.diag(S), 0)) * rng.standard_normal(N))
                arm = int(np.argmax(draw))
            elif kind == "ucb":
                beta = 2 * np.log(N * (t + 1) ** 2 * np.pi ** 2 / (6 * 0.1))
                arm = int(np.argmax(m + np.sqrt(beta * np.maximum(np.diag(S), 0))))
            elif kind == "twostep":
                if t == T - 1:
                    arm = int(np.argmax(m))
                else:
                    ell, HAP = flt.next_projection()
                    cov_next = HAP[:, :N] + HAP[:, N:2 * N]  # Cov(f_{j,t+1}, f_{a,t})
                    d = np.diag(S) + world.s_obs ** 2
                    U = cov_next / np.sqrt(d)[None, :]
                    arm = int(np.argmax(m + expected_max_lines(ell, U)))
            else:
                raise ValueError(policy)
            y = world.f[t, arm] + world.noise[t, arm]
            flt.update(arm, y)
            flt.propagate()
            regret_dyn[t] = world.f[t].max() - world.f[t, arm]
            regret_mu[t] = best_mu - world.mu[arm]

    elif policy.startswith("spectral_"):
        K = world.s_mu ** 2 * world.C_mu
        P = K.copy()
        mean = np.zeros(N)
        for t in range(T):
            sd = np.sqrt(np.maximum(np.diag(P), 0))
            if policy == "spectral_ucb":
                beta = 2 * np.log(N * (t + 1) ** 2 * np.pi ** 2 / (6 * 0.1))
                arm = int(np.argmax(mean + np.sqrt(beta) * sd))
            else:
                arm = int(np.argmax(mean + np.linalg.cholesky(P + 1e-9 * np.eye(N)) @ rng.standard_normal(N)))
            y = world.f[t, arm] + world.noise[t, arm]
            Pa = P[:, arm].copy()
            d = Pa[arm] + var_y
            mean += Pa * (y - mean[arm]) / d
            P -= np.outer(Pa, Pa) / d
            regret_dyn[t] = world.f[t].max() - world.f[t, arm]
            regret_mu[t] = best_mu - world.mu[arm]

    else:
        n, s = np.zeros(N), np.zeros(N)
        hist_arm, hist_y = np.zeros(T, int), np.zeros(T)
        window = 500
        for t in range(T):
            if policy == "ucb":
                idx = np.where(n > 0, s / np.maximum(n, 1) + np.sqrt(var_y * 2 * np.log(t + 1) / np.maximum(n, 1)), np.inf)
            elif policy == "ts":
                prec = 1 / world.s_mu ** 2 + n / var_y
                idx = (s / var_y) / prec + rng.standard_normal(N) / np.sqrt(prec)
            elif policy == "swucb":
                lo = max(0, t - window)
                nw = np.bincount(hist_arm[lo:t], minlength=N).astype(float)
                sw = np.bincount(hist_arm[lo:t], weights=hist_y[lo:t], minlength=N)
                idx = np.where(nw > 0, sw / np.maximum(nw, 1) + np.sqrt(var_y * 2 * np.log(min(t + 1, window)) / np.maximum(nw, 1)), np.inf)
            else:
                raise ValueError(policy)
            arm = int(np.argmax(idx))
            y = world.f[t, arm] + world.noise[t, arm]
            n[arm] += 1
            s[arm] += y
            hist_arm[t], hist_y[t] = arm, y
            regret_dyn[t] = world.f[t].max() - world.f[t, arm]
            regret_mu[t] = best_mu - world.mu[arm]

    return {"dyn": np.cumsum(regret_dyn), "mu": np.cumsum(regret_mu)}


# ---------------------------------------------------------------- checks


def verify() -> None:
    """Filter checks against dense Gaussian conditioning on a small world."""
    w = World(side=3, p=3, persistence=0.9, tau=2.0, T=6, seed=1)
    N, p = w.N, w.p
    flt = Filter(w.a, N, w.s_mu ** 2 * w.C_mu, np.kron(w.G, w.C), w.Q, w.s_obs)
    # Dense prior over (mu, f_0..f_{T-1}): Cov(f_t, f_s) = K_mu + gamma(|t-s|) C.
    gam = np.zeros(w.T)
    F = companion(w.a)
    for h in range(w.T):
        gam[h] = (np.linalg.matrix_power(F, h) @ w.G)[0, 0]
    T = w.T
    big = np.zeros((T * N, T * N))
    for t in range(T):
        for s in range(T):
            big[t * N:(t + 1) * N, s * N:(s + 1) * N] = w.s_mu ** 2 * w.C_mu + gam[abs(t - s)] * w.C
    arms, ys = [], []
    rng = np.random.default_rng(0)
    for t in range(T):
        m, S, _ = flt.reward_mean_cov()
        if arms:
            idx = [s * N + a for s, a in zip(range(t), arms)]
            Koo = big[np.ix_(idx, idx)] + w.s_obs ** 2 * np.eye(len(idx))
            Kco = big[np.ix_(range(t * N, (t + 1) * N), idx)]
            m_d = Kco @ np.linalg.solve(Koo, np.array(ys))
            S_d = big[t * N:(t + 1) * N, t * N:(t + 1) * N] - Kco @ np.linalg.solve(Koo, Kco.T)
        else:
            m_d, S_d = np.zeros(N), big[:N, :N]
        assert np.allclose(m, m_d, atol=1e-8), (t, np.abs(m - m_d).max())
        assert np.allclose(S, S_d, atol=1e-8), (t, np.abs(S - S_d).max())
        a = int(rng.integers(N))
        y = w.f[t, a] + w.noise[t, a]
        arms.append(a)
        ys.append(y)
        flt.update(a, y)
        flt.propagate()
    # Expected max of lines against the exact upper-envelope formula.
    for _ in range(50):
        ell, U = rng.standard_normal(8), rng.standard_normal((8, 4))
        exact = np.array([exact_max_lines(ell, U[:, a]) for a in range(4)])
        assert np.allclose(expected_max_lines(ell, U), exact, atol=5e-3), np.abs(expected_max_lines(ell, U) - exact).max()
    print("verify: filter matches dense conditioning; quantile grid matches the exact envelope")


def exact_max_lines(ell, u):
    """E max_j (ell_j + u_j Z) by the upper envelope (research/spatiotemporal_bandits, Section 6)."""
    zs = np.linspace(-12, 12, 200_001)
    top = np.argmax(ell[:, None] + u[:, None] * zs[None], axis=0)
    change = np.flatnonzero(np.diff(top)) + 1
    starts = np.concatenate([[0], change])
    ends = np.concatenate([change, [len(zs)]])
    total = 0.0
    for s0, e0 in zip(starts, ends):
        j = top[s0]
        lo = -np.inf if s0 == 0 else (ell[top[s0 - 1]] - ell[j]) / (u[j] - u[top[s0 - 1]])
        hi = np.inf if e0 == len(zs) else (ell[top[e0]] - ell[j]) / (u[j] - u[top[e0]])
        total += ell[j] * (norm.cdf(hi) - norm.cdf(lo)) + u[j] * (norm.pdf(lo) - norm.pdf(hi))
    return total


# ---------------------------------------------------------------- driver


CONFIGS = {
    "main": dict(persistence=0.97, spatial=True),
    "weak_persistence": dict(persistence=0.6, spatial=True),
    "no_spatial": dict(persistence=0.97, spatial=False),
}


def job(args):
    config, seed, policy, T = args
    t0 = time.time()
    world = World(seed=SEED + seed, T=T, **CONFIGS[config])
    out = run_policy(world, policy, SEED + 1000 * seed + 7)
    row = {"config": config, "seed": seed, "policy": policy, "seconds": round(time.time() - t0, 1)}
    for c in (100, 250, 500, 1000, 2000, 5000):
        if c <= T:
            row[f"dyn@{c}"] = float(out["dyn"][c - 1])
            row[f"mu@{c}"] = float(out["mu"][c - 1])
    print(f"{config} seed {seed} {policy}: {row['seconds']}s dyn/T={row[f'dyn@{T}'] / T:.3f}", flush=True)
    return row


def main(seeds: int, T: int, jobs: int, configs: list[str]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    tasks = [(c, s, p, T) for c in configs for s in range(seeds) for p in POLICIES]
    tasks.sort(key=lambda x: not (x[2].startswith("st_") or x[2].startswith("ar_")))  # heavy first
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(job, tasks, chunksize=1))
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "runs.csv", index=False)
    (RESULTS / "metadata.json").write_text(json.dumps({"seeds": seeds, "horizon": T, "configs": CONFIGS,
                                                       "policies": POLICIES}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--horizon", type=int, default=2000)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--configs", nargs="+", default=list(CONFIGS))
    a = ap.parse_args()
    if a.verify:
        verify()
    else:
        main(a.seeds, a.horizon, a.jobs, a.configs)
