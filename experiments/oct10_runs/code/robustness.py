"""Experiment 4: certificates with estimated and misspecified dynamics.

Usage (from the repo root):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct10_runs/code/robustness.py --seeds 30 --jobs 6
    # elimination at a longer horizon, so the innovation certificate has to decide:
    ... robustness.py --policies se_st2 se_iid --horizon 20000 --phis 0.9 0.97 --batches 25 --tag _elim20k

Reuses the world and the B1'' plug-in bound of
experiments/simulations/certificates_under_persistence/code/coverage.py: N = 20 arms in 4
components, oracle component width EPS = 0.1, observation noise sd 0.1 (known to the learner).

The online horizon T is preceded by a fully observed prefix of up to 365 rounds (a monitoring
panel: every arm observed every round). Fitted conditions estimate the dynamics from that
prefix only; the online path is the same across conditions for a given seed.

Learner conditions for the innovation certificate (policies sp_ucb_st2, se_st2):
- known:        true phi, Var(z) = 1 and C.
- fit100/365:   pooled AR(1)+noise moment fit on a 100- or 365-round prefix: phi = g2 / g1,
                Var(z) = g1 / phi, C = residual correlation shrunk 20% to I.
- fit100_cons:  fit100 with phi raised by 2 jackknife (over arms) standard errors.
- phi_bias:     true parameters with phi - 0.05.
- ignore_corr:  true phi, C = I (correlated truth fitted as independent).
- t3:           truth with variance-normalised Student-t(3) shocks, learner known Gaussian params.
- ar7_as_ar1:   truth AR(7) with weekly lag (z_t = 0.55 z_{t-1} + 0.40 z_{t-7} + e), Var = 1;
                learner fits AR(1) on the 365-round prefix.
The iid certificates (sp_ucb_iid, se_iid) are run once per truth (gauss, t3, ar7).
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "simulations" / "certificates_under_persistence" / "code"))
import coverage as cv  # noqa: E402

RESULTS = HERE.parent / "results" / "robustness"
N, COMP, R_OBS, EPS = cv.N, cv.COMP, cv.R_OBS, cv.EPS
LMAX = 365
AR7 = {1: 0.55, 7: 0.40}
ST_CONDS = ("known", "fit100", "fit365", "fit100_cons", "phi_bias", "ignore_corr", "t3")
IID_TRUTHS = ("gauss", "t3")


def correlation(config):
    if config == "independent":
        return np.eye(N)
    W = np.diag(np.ones(N - 1), 1)
    L = np.diag((W + W.T).sum(1)) - (W + W.T)
    K = np.linalg.inv(np.eye(N) + 3.0 * L)
    d = np.sqrt(np.diag(K))
    return K / d[:, None] / d[None, :]


def ar_coefs(truth, phi):
    if truth == "ar7":
        a = np.zeros(7)
        for k, v in AR7.items():
            a[k - 1] = v
        return a
    return np.array([phi])


def stationary_var(a, H=2000):
    """Var of an AR(p) with unit innovation variance, from the impulse response."""
    p = len(a)
    psi = np.zeros(H)
    psi[0] = 1.0
    for h in range(1, H):
        psi[h] = sum(a[k] * psi[h - 1 - k] for k in range(min(p, h)))
    return float((psi ** 2).sum())


def world(seed, phi, config, T, truth="gauss"):
    """Same means and labels as coverage.world; dynamics per `truth`; Var(z_i) = 1."""
    rng = np.random.default_rng(cv.SEED + seed)
    labels = np.repeat(np.arange(COMP), N // COMP)
    base = np.array([0.45, 0.25, 0.2, 0.15])
    mu = base[labels] + EPS * rng.random(N)
    mu[0] = 0.55
    C = correlation(config)
    a = ar_coefs(truth, phi)
    q = 1.0 / stationary_var(a)
    Lq = np.linalg.cholesky(q * C)
    burn = 500
    total = burn + LMAX + T
    if truth == "t3":
        nu = 3.0
        E = rng.standard_t(nu, size=(total, N)) * np.sqrt((nu - 2) / nu)
    else:
        E = rng.standard_normal((total, N))
    E = E @ Lq.T
    Z = np.zeros((total, N))
    p = len(a)
    for t in range(total):
        acc = E[t].copy()
        for k in range(p):
            if t - 1 - k >= 0:
                acc += a[k] * Z[t - 1 - k]
        Z[t] = acc
    Z = Z[burn:]
    Y = mu + Z + R_OBS * rng.standard_normal(Z.shape)
    perm = rng.permutation(N)  # random arm order, as in the B1'' runs
    mu, labels, Y = mu[perm], labels[perm], Y[:, perm]
    C = C[np.ix_(perm, perm)]
    return mu, labels, C, Y[:LMAX], Y[LMAX:]


def fit_prefix(P):
    """Pooled AR(1)+noise moment fit; jackknife SE of phi over arms."""
    d = P - P.mean(0)

    def acov(x, h):
        return (x[h:] * x[:-h]).mean(0)

    g1, g2 = acov(d, 1), acov(d, 2)
    phi = float(np.clip(g2.mean() / max(g1.mean(), 1e-9), 0.0, 0.995))
    jk = []
    for i in range(N):
        m = np.ones(N, bool)
        m[i] = False
        jk.append(np.clip(g2[m].mean() / max(g1[m].mean(), 1e-9), 0, 0.995))
    jk = np.array(jk)
    se = float(np.sqrt((N - 1) / N * ((jk - jk.mean()) ** 2).sum()))
    vz = float(max(g1.mean() / max(phi, 1e-3), 1e-3))
    e = d[1:] - phi * d[:-1]
    Ch = np.corrcoef(e.T)
    Ch = 0.8 * Ch + 0.2 * np.eye(N)
    return phi, se, vz, Ch


def learner(cond, phi, C, P):
    """Return (phi_l, vz_l, C_l) the learner plugs into the innovation regression."""
    if cond in ("known", "t3"):
        return phi, 1.0, C
    if cond == "phi_bias":
        return max(phi - 0.05, 0.0), 1.0, C
    if cond == "ignore_corr":
        return phi, 1.0, np.eye(N)
    L = 100 if cond.startswith("fit100") else LMAX
    ph, se, vz, Ch = fit_prefix(P[-L:])
    if cond.endswith("_cons"):
        ph = min(ph + 2 * se, 0.995)
    return ph, vz, Ch


def make_st(phi_l, vz_l, C_l):
    q = vz_l * (1 - phi_l ** 2)
    st = cv.InnovationRegression(phi_l, q * C_l, C_l, alpha=1.0 / N)
    st.P = vz_l * C_l.copy()
    return st


def run(task):
    config, phi, seed, policy, cond, T, batch = task
    t0 = time.time()
    truth = {"t3": "t3", "ar7_as_ar1": "ar7"}.get(cond, "gauss")
    mu, labels, C, P, Y = world(seed, phi, config, T, truth)
    members = [np.flatnonzero(labels == c) for c in range(COMP)]
    v_c = np.array([mu[m].max() for m in members])
    delta = 0.05
    sigma2 = 1.0 + R_OBS ** 2
    ell = np.log(2 * (N + COMP) * T / delta)
    st, phi_l = None, np.nan
    if policy.endswith("_st2"):
        lcond = "fit365" if cond == "ar7_as_ar1" else cond
        phi_l, vz_l, C_l = learner(lcond, phi, C, P)
        st = make_st(phi_l, vz_l, C_l)
    n, s = np.zeros(N), np.zeros(N)
    Nc, Sc = np.zeros(COMP), np.zeros(COMP)
    best = int(np.argmax(mu))
    active = np.ones(N, bool)
    reg = np.zeros(T)
    viol_rounds, first_viol, best_out_at = 0, -1, -1
    a = 0
    for t in range(T):
        if t % batch == 0 or policy.startswith("sp_"):
            if policy.endswith("_iid"):
                rad = np.sqrt(2 * sigma2 * ell / np.maximum(n, 1))
                lo = np.where(n > 0, s / np.maximum(n, 1) - rad, -np.inf)
                hi = np.where(n > 0, s / np.maximum(n, 1) + rad, np.inf)
                pool = np.where(Nc > 0, Sc / np.maximum(Nc, 1) + np.sqrt(2 * sigma2 * ell / np.maximum(Nc, 1)) + EPS, np.inf)
            else:
                lo, hi, pool = cv.plugin_bounds(st, members, delta)
            comp_up = np.array([min(hi[m].max(), pool[c]) for c, m in enumerate(members)])
            viol = (hi < mu - 1e-12).any() or (comp_up < v_c - 1e-12).any()
            viol_rounds += int(viol)
            if viol and first_viol < 0:
                first_viol = t
        if t % batch == 0:
            if policy.startswith("sp_"):
                if policy.endswith("_iid") and t < COMP * batch:
                    a = int(members[t // batch][0])
                else:
                    c = int(np.argmax(comp_up))
                    a = int(members[c][np.argmax(hi[members[c]])])
            else:
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
    row = {"config": config, "phi": phi if cond != "ar7_as_ar1" else np.nan, "seed": seed, "policy": policy,
           "condition": cond, "batch": batch, "phi_learner": phi_l, "regret": float(reg.sum()),
           "regret_last_1000": float(reg[-1000:].sum()),
           "sp_violation_share" if policy.startswith("sp_") else "check_violation_share": viol_rounds / T,
           "any_violation": viol_rounds > 0, "first_violation": first_viol,
           "best_eliminated": best_out_at >= 0 if policy.startswith("se_") else np.nan,
           "seconds": round(time.time() - t0, 2)}
    return row


def tasks(seeds, T, phis, batches):
    out = []
    for config in ("independent", "correlated"):
        for b in batches:
            for s in range(seeds):
                for phi in phis:
                    for cond in ST_CONDS:
                        if cond == "ignore_corr" and config == "independent":
                            continue
                        for p in ("sp_ucb_st2", "se_st2"):
                            out.append((config, phi, s, p, cond, T, b))
                    for truth in IID_TRUTHS:
                        for p in ("sp_ucb_iid", "se_iid"):
                            out.append((config, phi, s, p, "t3" if truth == "t3" else "known", T, b))
                for p in ("sp_ucb_st2", "se_st2", "sp_ucb_iid", "se_iid"):
                    out.append((config, 0.0, s, p, "ar7_as_ar1", T, b))
    return out


def main(seeds, T, jobs, phis, batches, tag, policies=None):
    RESULTS.mkdir(parents=True, exist_ok=True)
    ts = tasks(seeds, T, phis, batches)
    if policies:
        ts = [x for x in ts if x[3] in policies and (x[1] in phis or x[4] == "ar7_as_ar1")]
    ts.sort(key=lambda x: (x[6], not x[3].endswith("st2")))
    print(f"{len(ts)} runs", flush=True)
    rows = []
    t0 = time.time()
    with ProcessPoolExecutor(jobs) as ex:
        for i, r in enumerate(ex.map(run, ts, chunksize=4)):
            rows.append(r)
            if (i + 1) % 200 == 0:
                print(f"{i + 1}/{len(ts)} done, {time.time() - t0:.0f}s", flush=True)
                pd.DataFrame(rows).to_csv(RESULTS / f"runs{tag}.partial.csv", index=False)
    pd.DataFrame(rows).to_csv(RESULTS / f"runs{tag}.csv", index=False)
    (RESULTS / f"runs{tag}.partial.csv").unlink(missing_ok=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--horizon", type=int, default=5000)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--phis", type=float, nargs="+", default=[0.5, 0.9, 0.97])
    ap.add_argument("--batches", type=int, nargs="+", default=[1, 25])
    ap.add_argument("--tag", default="")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--policies", nargs="+", default=None, help="restrict to these policies")
    a = ap.parse_args()
    if a.pilot:
        for task in [("correlated", 0.97, 0, "sp_ucb_st2", "fit100", 2000, 25),
                     ("correlated", 0.97, 0, "se_st2", "known", 2000, 25),
                     ("independent", 0.0, 0, "se_iid", "ar7_as_ar1", 2000, 25)]:
            print(run(task))
    else:
        main(a.seeds, a.horizon, a.jobs, a.phis, a.batches, a.tag, a.policies)
