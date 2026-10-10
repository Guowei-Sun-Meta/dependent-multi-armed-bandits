"""Certified pooling under persistent rewards: tests of B1 and B2 (research/correlated_arms).

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/st_toy/coverage.py --verify
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/st_toy/coverage.py --seeds 30 --horizon 5000 --jobs 2

World: N = 20 arms in 4 components of 5; component c has means in a band of width 0.1
(the oracle diameter certificate eps_c = 0.1); the best component's top arm has mean 0.5,
the others are 0.2-0.3 below. z is AR(1) with persistence phi, Var(z) = V = 1, and innovation
covariance Q = q C (C = I for "independent", a unit-diagonal path-graph resolvent across
arms for "correlated"). Observation noise sd 0.1. The learner pulls one arm per round.

Policies (all target the long-run means; regret is mean regret):
- ucb_iid / sp_ucb_iid: arm UCB and SP-UCB from [A] with sample means and the iid radius
  sigma sqrt(2 ell / n), sigma^2 = V + r.
- ucb_st / sp_ucb_st: the same indices built on the innovation regression [S] (S1) and its
  all-time confidence set (S2): B1's policy.
At every round we record whether any arm or component upper bound lies below its target
(mu_i or v_c): a certificate violation.
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "research" / "st_toy" / "results"
SEED = 20261009
N, COMP, R_OBS, EPS = 20, 4, 0.1, 0.1
POLICIES = ("ucb_iid", "sp_ucb_iid", "sp_ucb_emp", "ucb_st", "sp_ucb_st")
ELIM_POLICIES = ("se_iid", "se_st")
# B1' (independent shocks only): the innovation information is diagonal, so each arm and each
# component is a scalar martingale; use the one-dimensional mixture bound with a union over the
# N + M arms and components instead of the N-dimensional log-determinant ellipsoid.
SCALAR_POLICIES = ("sp_ucb_iid", "sp_ucb_st", "sp_ucb_st1", "se_iid", "se_st", "se_st1")
# B1'' (correlated shocks): scalar martingale bounds with other arms' means treated as bounded
# nuisances, plugged in from their current intervals and iterated from [0, 1].
PLUGIN_POLICIES = ("sp_ucb_iid", "sp_ucb_st", "sp_ucb_st2", "se_iid", "se_st2")
BATCHES = (1, 25)
PHIS = (0.0, 0.5, 0.9, 0.97)
CONFIGS = ("independent", "correlated")


def world(seed: int, phi: float, config: str, T: int):
    rng = np.random.default_rng(seed)
    labels = np.repeat(np.arange(COMP), N // COMP)
    base = np.array([0.45, 0.25, 0.2, 0.15])
    mu = base[labels] + EPS * rng.random(N)
    mu[0] = 0.55  # unique best arm, in component 0
    if config == "independent":
        C = np.eye(N)
    else:
        W = np.diag(np.ones(N - 1), 1)
        L = np.diag((W + W.T).sum(1)) - (W + W.T)
        K = np.linalg.inv(np.eye(N) + 3.0 * L)
        d = np.sqrt(np.diag(K))
        C = K / d[:, None] / d[None, :]
    q = 1 - phi ** 2  # Var(z) = 1
    Lq = np.linalg.cholesky(q * C)
    z = np.linalg.cholesky(C) @ rng.standard_normal(N)
    Z = np.zeros((T, N))
    for t in range(T):
        Z[t] = z
        z = phi * z + Lq @ rng.standard_normal(N)
    Y = mu + Z + R_OBS * rng.standard_normal((T, N))
    return mu, labels, C, q, Y


def scalar_bounds(st, members, delta):
    """B1' bounds from the diagonal innovation information (valid when Q is diagonal)."""
    alpha = st.H[0, 0]
    Jd = np.diag(st.J)
    dlt = delta / (N + COMP)
    mu_i = st.q / Jd
    rad_i = (np.sqrt(2 * np.log(np.sqrt(Jd / alpha) / dlt)) + np.sqrt(alpha)) / np.sqrt(Jd)
    pool = np.empty(COMP)
    for c, m in enumerate(members):
        Jc = alpha + (Jd[m] - alpha).sum()
        pool[c] = st.q[m].sum() / Jc + (np.sqrt(2 * np.log(np.sqrt(Jc / alpha) / dlt)) + np.sqrt(alpha)) / np.sqrt(Jc)
    return mu_i - rad_i, mu_i + rad_i, pool + EPS


def plugin_bounds(st, members, delta, iters: int = 5):
    """B1'': valid with correlated shocks.

    Arms: q_i - sum_{j!=i} G_ij m_j = G_ii mu_i + sum_{j!=i} G_ij (mu_j - m_j) + W_i, with
    G = J - alpha I, W_i a scalar martingale (quadratic variation G_ii). On the event that every
    scalar mixture bound holds, intervals containing the truth map to intervals containing it,
    so iterating from [0, 1] stays valid. Components: write mu_i = theta_c + d_i with theta_c the
    component midrange and |d_i| <= eps_c / 2; the same argument on theta with design P'u gives
    a pooled bound theta_hat_c + rad_c + eps_c / 2 >= v_c. With independent shocks this reduces
    to SP-UCB's pooled index."""
    alpha = st.H[0, 0]
    J = st.J
    G = J - alpha * np.eye(N)
    dlt = delta / (N + COMP)
    stat = lambda x: np.sqrt(2 * x * np.log(np.sqrt(x / alpha) / dlt))  # noqa: E731
    lo, hi = np.zeros(N), np.ones(N)
    Jd = np.diag(J)
    off = np.abs(G - np.diag(np.diag(G)))
    for _ in range(iters):
        m, h = (lo + hi) / 2, (hi - lo) / 2
        cross = (G - np.diag(np.diag(G))) @ m
        mu_hat = (st.q - cross) / Jd
        rad = (stat(Jd) + alpha + off @ h) / Jd
        lo, hi = np.maximum(lo, mu_hat - rad), np.minimum(hi, mu_hat + rad)
    P = np.zeros((N, COMP))
    for c, mem in enumerate(members):
        P[mem, c] = 1.0
    Gx = P.T @ G @ P
    Jx = np.diag(Gx) + alpha
    qx = P.T @ st.q
    offx = np.abs(Gx - np.diag(np.diag(Gx)))
    dev = np.abs(P.T @ G) @ np.full(N, EPS / 2)  # sum_i |(P'G)_ci| eps / 2
    tlo, thi = np.zeros(COMP), np.ones(COMP)
    for _ in range(iters):
        m, h = (tlo + thi) / 2, (thi - tlo) / 2
        th_hat = (qx - (Gx - np.diag(np.diag(Gx))) @ m) / Jx
        rad = (stat(Jx) + alpha + offx @ h + dev) / Jx
        tlo, thi = np.maximum(tlo, th_hat - rad), np.minimum(thi, th_hat + rad)
    return lo, hi, thi + EPS / 2


class InnovationRegression:
    """[S] Theorem 'Predictable innovation experiments' for AR(1): s_t | mu ~ N(g + D mu, P)."""

    def __init__(self, phi, Q, C, alpha):
        self.phi, self.Q = phi, Q
        self.g = np.zeros(N)
        self.D = np.zeros((N, N))
        self.P = C.copy()  # stationary covariance, Var(z) = 1
        self.H = alpha * np.eye(N)
        self.J = self.H.copy()
        self.q = np.zeros(N)
        self.logdet_H = N * np.log(alpha)

    def observe(self, a, y):
        v = np.eye(N)[a] + self.D[a]
        d = self.P[a, a] + R_OBS ** 2
        u = v / np.sqrt(d)
        Rt = (y - self.g[a]) / np.sqrt(d)
        self.J += np.outer(u, u)
        self.q += u * Rt
        k = self.P[:, a] / d
        self.g = self.g + k * (y - self.g[a])
        self.D = self.D - np.outer(k, v)
        self.P = self.P - np.outer(self.P[:, a], self.P[a]) / d
        self.g *= self.phi
        self.D *= self.phi
        self.P = self.phi ** 2 * self.P + self.Q

    def estimate(self, delta, B):
        Jinv = np.linalg.inv(self.J)
        mu_hat = Jinv @ self.q
        logdet = np.linalg.slogdet(self.J)[1]
        beta = np.sqrt(max(logdet - self.logdet_H, 0) + 2 * np.log(1 / delta)) + np.sqrt(self.H[0, 0]) * B
        return mu_hat, Jinv, beta


def run(args):
    config, phi, seed, policy, T = args[:5]
    batch = args[5] if len(args) > 5 else 1
    t0 = time.time()
    mu, labels, C, q, Y = world(SEED + seed, phi, config, T)
    delta = 0.05
    vstar = mu.max()
    v_c = np.array([mu[labels == c].max() for c in range(COMP)])
    members = [np.flatnonzero(labels == c) for c in range(COMP)]
    n, s, ss = np.zeros(N), np.zeros(N), np.zeros(N)
    Nc, Sc, SSc = np.zeros(COMP), np.zeros(COMP), np.zeros(COMP)
    a = 0
    sigma2 = 1.0 + R_OBS ** 2
    ell = np.log(2 * (N + COMP) * T / delta)
    reg = np.zeros(T)
    viol_rounds = 0
    st = InnovationRegression(phi, q * C, C, alpha=1.0 / N) if policy.endswith(("_st", "_st1", "_st2")) else None
    if policy.startswith("se_"):
        return run_elimination(policy, config, phi, seed, T, batch, mu, labels, members, Y, st, sigma2, ell, delta, t0)
    for t in range(T):
        if policy.endswith("_iid"):
            b = lambda x: np.sqrt(2 * sigma2 * ell / np.maximum(x, 1))  # noqa: E731
            U_i = np.where(n > 0, s / np.maximum(n, 1) + b(n), np.inf)
            pool = np.where(Nc > 0, Sc / np.maximum(Nc, 1) + b(Nc) + EPS, np.inf)
        elif policy.endswith("_emp"):
            # Practical iid certificate: variance estimated from the arm's own samples, level log t.
            lvl = 2 * np.log(max(t, 2))
            var_i = np.where(n > 1, ss / np.maximum(n, 1) - (s / np.maximum(n, 1)) ** 2, sigma2)
            var_c = np.where(Nc > 1, SSc / np.maximum(Nc, 1) - (Sc / np.maximum(Nc, 1)) ** 2, sigma2)
            U_i = np.where(n > 1, s / np.maximum(n, 1) + np.sqrt(np.maximum(var_i, 1e-6) * lvl / np.maximum(n, 1)), np.inf)
            pool = np.where(Nc > 1, Sc / np.maximum(Nc, 1) + np.sqrt(np.maximum(var_c, 1e-6) * lvl / np.maximum(Nc, 1)) + EPS, np.inf)
        elif policy.endswith("_st1"):
            _, U_i, pool = scalar_bounds(st, members, delta)
        elif policy.endswith("_st2"):
            _, U_i, pool = plugin_bounds(st, members, delta)
        else:
            mu_hat, Jinv, beta = st.estimate(delta, np.sqrt(N))
            sd = np.sqrt(np.maximum(np.diag(Jinv), 0))
            U_i = mu_hat + beta * sd
            pool = np.empty(COMP)
            for c, m in enumerate(members):
                cands = [np.full(len(m), 1 / len(m))]
                w_info = 1 / np.maximum(sd[m] ** 2, 1e-12)
                cands.append(w_info / w_info.sum())
                vals = [w @ mu_hat[m] + beta * np.sqrt(w @ Jinv[np.ix_(m, m)] @ w) for w in cands]
                pool[c] = min(vals) + EPS
        decide = t % batch == 0
        if policy.startswith("sp_"):
            comp_up = np.array([min(U_i[m].max(), pool[c]) for c, m in enumerate(members)])
            viol = (U_i < mu - 1e-12).any() or (comp_up < v_c - 1e-12).any()
            if decide:
                if not policy.endswith(("_st", "_st1", "_st2")) and t < COMP * batch:
                    a = int(members[t // batch][0])
                else:
                    c = int(np.argmax(comp_up))
                    a = int(members[c][np.argmax(U_i[members[c]])])
        else:
            viol = (U_i < mu - 1e-12).any()
            if decide:
                a = int(np.argmax(U_i))
        viol_rounds += int(viol)
        y = Y[t, a]
        n[a] += 1
        s[a] += y
        ss[a] += y * y
        Nc[labels[a]] += 1
        Sc[labels[a]] += y
        SSc[labels[a]] += y * y
        if st is not None:
            st.observe(a, y)
        reg[t] = vstar - mu[a]
    cum = np.cumsum(reg)
    row = {"config": config, "phi": phi, "seed": seed, "policy": policy, "batch": batch, "regret": float(cum[-1]),
           "regret@1000": float(cum[min(999, T - 1)]), "violation_share": viol_rounds / T,
           "any_violation": viol_rounds > 0, "best_arm_share_last_1000": float((reg[-1000:] == 0).mean()),
           "seconds": round(time.time() - t0, 1)}
    print(f"{config} phi={phi} b={batch} seed={seed} {policy}: regret={row['regret']:.1f} viol={row['violation_share']:.3f}",
          flush=True)
    return row


def run_elimination(policy, config, phi, seed, T, batch, mu, labels, members, Y, st, sigma2, ell, delta, t0):
    """Certified successive elimination with component pooling: an irrevocable decision.
    Arms and whole components are eliminated when their upper bound falls below the best
    lower bound. Eliminating the best arm makes mean regret grow linearly."""
    active = np.ones(N, bool)
    n, s = np.zeros(N), np.zeros(N)
    Nc, Sc = np.zeros(COMP), np.zeros(COMP)
    reg = np.zeros(T)
    best = int(np.argmax(mu))
    best_out_at = -1
    a = 0
    for t in range(T):
        if t % batch == 0:
            if policy == "se_iid":
                rad = np.sqrt(2 * sigma2 * ell / np.maximum(n, 1))
                lo = np.where(n > 0, s / np.maximum(n, 1) - rad, -np.inf)
                hi = np.where(n > 0, s / np.maximum(n, 1) + rad, np.inf)
                pool = np.where(Nc > 0, Sc / np.maximum(Nc, 1) + np.sqrt(2 * sigma2 * ell / np.maximum(Nc, 1)) + EPS, np.inf)
            elif policy == "se_st1":
                lo, hi, pool = scalar_bounds(st, members, delta)
            elif policy == "se_st2":
                lo, hi, pool = plugin_bounds(st, members, delta)
            else:
                mu_hat, Jinv, beta = st.estimate(delta, np.sqrt(N))
                sd = np.sqrt(np.maximum(np.diag(Jinv), 0))
                lo, hi = mu_hat - beta * sd, mu_hat + beta * sd
                pool = np.empty(COMP)
                for c, m in enumerate(members):
                    w = np.full(len(m), 1 / len(m))
                    pool[c] = w @ mu_hat[m] + beta * np.sqrt(w @ Jinv[np.ix_(m, m)] @ w) + EPS
            best_lo = lo[active].max()
            for c, m in enumerate(members):
                if min(hi[m].max(), pool[c]) < best_lo:
                    active[m] = False
            active &= ~(hi < best_lo)
            if not active.any():
                active[int(np.argmax(hi))] = True
            if not active[best] and best_out_at < 0:
                best_out_at = t
            cand = np.flatnonzero(active)
            a = int(cand[np.argmin(n[cand])])
        y = Y[t, a]
        n[a] += 1
        s[a] += y
        Nc[labels[a]] += 1
        Sc[labels[a]] += y
        if st is not None:
            st.observe(a, y)
        reg[t] = mu[best] - mu[a]
    row = {"config": config, "phi": phi, "seed": seed, "policy": policy, "batch": batch, "regret": float(reg.sum()),
           "best_eliminated": best_out_at >= 0, "best_eliminated_at": best_out_at,
           "regret_last_1000": float(reg[-1000:].sum()), "active_at_end": int(active.sum()),
           "seconds": round(time.time() - t0, 1)}
    print(f"{config} phi={phi} b={batch} seed={seed} {policy}: regret={row['regret']:.1f} "
          f"best_out={row['best_eliminated']}", flush=True)
    return row


def verify():
    """B2 formula and the innovation regression against dense GLS on a tiny case."""
    phi, V, n = 0.9, 1.0, 400
    var = V / n * ((1 + phi) / (1 - phi) - 2 * phi * (1 - phi ** n) / (n * (1 - phi) ** 2))
    rng = np.random.default_rng(1)
    sims = []
    for _ in range(4000):
        z = rng.standard_normal()
        xs = []
        for _ in range(n):
            xs.append(z)
            z = phi * z + np.sqrt(1 - phi ** 2) * rng.standard_normal()
        sims.append(np.mean(xs))
    assert abs(np.var(sims) / var - 1) < 0.08, np.var(sims) / var
    # Innovation regression information equals dense GLS information for a fixed design.
    mu, labels, C, q, Y = world(3, 0.8, "correlated", 30)
    st = InnovationRegression(0.8, q * C, C, alpha=1e-9)
    acts = np.random.default_rng(2).integers(N, size=30)
    for t, a in enumerate(acts):
        st.observe(a, Y[t, a])
    M = np.eye(N)[acts]
    Xi = np.array([[C[a, b] * 0.8 ** abs(t - s) for s, b in enumerate(acts)] for t, a in enumerate(acts)])
    Xi += R_OBS ** 2 * np.eye(len(acts))
    info = M.T @ np.linalg.solve(Xi, M)
    assert np.allclose(st.J - st.H, info, atol=1e-6), np.abs(st.J - st.H - info).max()
    print("verify: B2 variance formula matches simulation; innovation information matches dense GLS")


def main(seeds, T, jobs, tag=""):
    RESULTS.mkdir(parents=True, exist_ok=True)
    pols = (PLUGIN_POLICIES if tag.startswith("_plugin") else SCALAR_POLICIES if tag.startswith("_scalar")
            else ELIM_POLICIES if tag.startswith("_elim") else POLICIES)
    configs = ("independent",) if tag.startswith("_scalar") else CONFIGS
    tasks = [(c, phi, s, p, T, b) for c in configs for phi in PHIS for s in range(seeds) for p in pols
             for b in BATCHES]
    tasks.sort(key=lambda x: not x[3].endswith("_st"))
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(run, tasks, chunksize=4))
    pd.DataFrame(rows).to_csv(RESULTS / f"coverage_runs{tag}.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--horizon", type=int, default=5000)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.verify:
        verify()
    else:
        main(a.seeds, a.horizon, a.jobs, a.tag)
