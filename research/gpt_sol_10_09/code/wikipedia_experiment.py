"""Laptop-sized selective-feedback experiment on observed Wikipedia attention.

General AR(7), historical hyperlink graphs, two frozen 24-arm panels. Mean
parameters are fixed unknown quantities; Gaussian draws are working algorithmic
uncertainty. Real-data oracle regret uses observed log views, not latent means.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

import numpy as np
import pandas as pd
from scipy.linalg import solve_discrete_lyapunov

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/wikipedia"
OUT = ROOT / "results/wikipedia"
SEED = 20261009
R = 1e-8
POLICIES = ("fit_mean", "last_value", "round_robin", "iid_ucb", "iid_ts", "sw_ucb",
            "ar_greedy", "ar_predictive_ucb", "ar_predictive_ts", "st_greedy",
            "st_state_ucb", "st_state_ts", "st_predictive_ucb", "st_predictive_ts",
            "rewired_predictive_ts", "factor_predictive_ts", "empirical_predictive_ts")


def load_panel(name):
    manifest = json.loads((DATA / "manifest.json").read_text())
    entries = [x for x in manifest["articles"] if x["panel"] == name]
    arrays, date_lists = [], []
    for e in entries:
        p = ROOT / e["view_file"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == e["views_sha256"]
        values = json.loads(p.read_text())["items"]
        date_lists.append([v["timestamp"][:8] for v in values])
        arrays.append([v["views"] for v in values])
        assert e["revision_timestamp"] < "2024-01-01"
    assert all(d == date_lists[0] for d in date_lists), "Missingness cannot be filled with zero"
    dates = pd.to_datetime(date_lists[0], format="%Y%m%d")
    assert len(dates) == 547 and dates.equals(pd.date_range("2024-01-01", "2025-06-30"))
    titles = [e["title"] for e in entries]
    raw = np.asarray(arrays, dtype=float).T
    assert np.isfinite(raw).all() and (raw >= 0).all()
    w = np.zeros((len(titles), len(titles)))
    index = {x: i for i, x in enumerate(titles)}
    for source, target in json.loads((DATA / (name+"_historical_links.json")).read_text()):
        w[index[source], index[target]] = 1
    w = np.maximum(w, w.T)
    assert not np.diag(w).any()
    return dates, raw, w, titles


def rewire(w):
    rng = np.random.default_rng(SEED)
    edges = set(map(tuple, np.argwhere(np.triu(w, 1) > 0)))
    done = 0
    for _ in range(max(100, len(edges)*100)):
        es = sorted(edges)
        a, b = es[rng.integers(len(es))]
        c, d = es[rng.integers(len(es))]
        if rng.integers(2):
            c, d = d, c
        if len({a, b, c, d}) < 4:
            continue
        new = {tuple(sorted((a, c))), tuple(sorted((b, d)))}
        if new & edges:
            continue
        edges.remove(tuple(sorted((a, b)))); edges.remove(tuple(sorted((c, d))))
        edges |= new
        done += 1
        if done >= 10*len(edges):
            break
    out = np.zeros_like(w)
    for a, b in edges:
        out[a, b] = out[b, a] = 1
    assert np.array_equal(out.sum(0), w.sum(0))
    return out, done


def seasonal(y, weekdays):
    m = y.mean(0)
    return np.stack([y[weekdays == d].mean(0)-m for d in range(7)])


def fit_ar(y, weekdays, order):
    season = seasonal(y, weekdays)
    x = y-season[weekdays]
    mu = x.mean(0)
    z = x-mu
    lags = (1, 2, 7) if order == 7 else tuple(range(1, order+1))
    design = np.stack([z[order-l:len(z)-l] for l in lags], axis=-1)
    target = z[order:]
    flat = design.reshape(-1, len(lags))
    coef = np.linalg.solve(flat.T@flat+10*np.eye(len(lags)), flat.T@target.ravel())
    a = np.zeros(order); a[np.asarray(lags)-1] = coef
    f = np.zeros((order, order)); f[0] = a; f[1:, :-1] = np.eye(order-1)
    original_radius = float(max(abs(np.linalg.eigvals(f))))
    scale = 1.
    if original_radius >= .99:
        scale = .98/max(np.sum(abs(a)), .98)
        a *= scale; f[0] = a
    radius = float(max(abs(np.linalg.eigvals(f))))
    assert radius < 1
    residuals = z[order:]-np.einsum("tnl,l->tn", design, a[np.asarray(lags)-1])
    s = np.cov(residuals, rowvar=False)
    d = np.sqrt(np.maximum(np.diag(s), 1e-6))
    corr = s/d[:, None]/d[None, :]
    common = float(np.clip(corr[np.triu_indices(len(mu), 1)].mean(), 0, .9))
    return {"a": a, "season": season, "mu": mu, "sample_cov": s, "scales": d,
            "common": common, "radius": radius, "original_radius": original_radius,
            "stability_scale": scale, "lags": lags}


def covariance(fit, w, kind, gamma, mix):
    n = len(w); d = fit["scales"]
    if kind == "ar":
        return np.diag(d*d)+R*np.eye(n)
    if kind == "empirical":
        rho = fit["common"]*gamma
        target = (1-rho)*np.eye(n)+rho*np.ones((n, n))
    elif kind == "factor":
        rho = fit["common"]*gamma
        target = (1-rho)*np.eye(n)+rho*np.ones((n, n))
    else:
        l = np.diag(w.sum(0))-w
        l /= max(np.mean(w.sum(0)), 1)
        k = np.linalg.inv(np.eye(n)+gamma*l)
        k /= np.sqrt(np.diag(k))[:, None]*np.sqrt(np.diag(k))[None, :]
        rho = fit["common"]
        target = (1-rho)*k+rho*np.ones((n, n))
    q = (1-mix)*target*d[:, None]*d[None, :]+mix*fit["sample_cov"]
    q = (q+q.T)/2+R*np.eye(n)
    np.linalg.cholesky(q)
    return q


def validation_residuals(y, weekdays, fit, start):
    a = fit["a"]; p = len(a)
    z = y-fit["season"][weekdays]-fit["mu"]
    return np.stack([z[t]-a@z[t-p:t][::-1] for t in range(start, len(y))])


def select_covariances(y, weekdays, w, wr, order):
    # All parameters/preprocessing are fitted on Jan-Sep, then scored on Oct-Dec.
    cut = 274
    fit = fit_ar(y[:cut], weekdays[:cut], order)
    e = validation_residuals(y, weekdays, fit, cut)
    specs, scores = {}, {}
    for kind, graph in [("ar", w), ("st", w), ("rewired", wr), ("factor", w), ("empirical", w)]:
        grid = [(0., 0.)] if kind == "ar" else [(g, m) for g in ((0., .5, 1.) if kind in ("factor", "empirical") else (.5, 2., 8.)) for m in (0., .5, .9)]
        best = None
        for gamma, mix in grid:
            q = covariance(fit, graph, kind, gamma, mix)
            _, logdet = np.linalg.slogdet(q)
            ll = -.5*(logdet+np.einsum("ti,ij,tj->", e, np.linalg.inv(q), e)/len(e))
            if best is None or ll > best[0]:
                best = (float(ll), gamma, mix)
        scores[kind] = best[0]
        specs[kind] = {"gamma": best[1], "mix": best[2]}
    return specs, scores


class Filter:
    """Joint augmented-mean Gaussian working filter, adapted from st_toy/toy.py."""
    def __init__(self, a, q):
        self.a, self.q = a, q
        self.n, self.p = len(q), len(a)
        n, p = self.n, self.p
        f = np.zeros((p, p)); f[0] = a; f[1:, :-1] = np.eye(p-1)
        unit = np.zeros((p, p)); unit[0, 0] = 1
        g = solve_discrete_lyapunov(f, unit)
        self.m = np.zeros(n*(p+1)); self.v = np.zeros((len(self.m), len(self.m)))
        self.v[:n, :n] = 100*np.eye(n)
        self.v[n:, n:] = np.kron(g, q)

    def forecast(self):
        n = self.n
        f = self.m[:n]+self.m[n:2*n]
        rows = self.v[:n]+self.v[n:2*n]
        cov = rows[:, :n]+rows[:, n:2*n]
        return f, (cov+cov.T)/2

    def update(self, arm, y):
        n = self.n
        col = self.v[:, arm]+self.v[:, n+arm]
        den = col[arm]+col[n+arm]+R
        assert den > 0
        self.m += col*(y-self.m[arm]-self.m[n+arm])/den
        self.v -= np.outer(col, col)/den

    def propagate(self):
        n, p, a = self.n, self.p, self.a
        b = self.m.reshape(p+1, n)
        first = a@b[1:]; b[2:] = b[1:-1].copy(); b[1] = first
        rows = self.v.reshape(p+1, n, -1)
        first = np.tensordot(a, rows[1:], axes=1)
        rows[2:] = rows[1:-1].copy(); rows[1] = first
        cols = self.v.reshape(-1, p+1, n)
        first = np.tensordot(cols[:, 1:], a, axes=([1], [0]))
        cols[:, 2:] = cols[:, 1:-1].copy(); cols[:, 1] = first
        self.v[n:2*n, n:2*n] += self.q


def burnin(y, weekdays, fit, q):
    engine = Filter(fit["a"], q)
    for t in range(len(y)):
        x = y[t]-fit["season"][weekdays[t]]
        for i in range(len(q)):
            engine.update(i, x[i])
        engine.propagate()
    return engine


def kind_of(policy):
    return policy.split("_")[0] if policy.startswith(("ar_", "rewired_", "factor_", "empirical_")) else "st"


def policy_scores(policy, engine, history, season_now, rng, bonus, prefix):
    # This interface receives no current or future reward vector.
    n = history.shape[1]
    if policy == "fit_mean":
        return np.nanmean(history[:prefix], axis=0)+season_now
    if policy == "last_value":
        return np.array([history[np.flatnonzero(np.isfinite(history[:, i]))[-1], i] for i in range(n)])+season_now
    if policy == "round_robin":
        scores = np.zeros(n); scores[(len(history)-prefix)%n] = 1
        return scores
    if policy in ("iid_ucb", "iid_ts", "sw_ucb"):
        hist = history[-30:] if policy == "sw_ucb" else history
        count = np.sum(np.isfinite(hist), axis=0)
        means = np.divide(np.nansum(hist, axis=0), count, out=np.full(n, np.nan), where=count > 0)
        var = np.nanvar(history[:prefix], axis=0)
        sd = np.sqrt(var/np.maximum(count, 1))
        means = np.nan_to_num(means, nan=float(np.nanmean(history[:prefix])))
        if policy == "iid_ts":
            return means+sd*rng.standard_normal(n)+season_now
        return means+bonus*np.sqrt(2*np.log(len(history)+2))*sd+season_now
    f, cov = engine.forecast()
    if policy.endswith("greedy"):
        return f+season_now
    if "predictive" in policy:
        cov -= engine.q
    eig = np.linalg.eigvalsh(cov)
    assert eig.min() > -1e-6, (policy, eig.min())
    cov += np.eye(n)*max(1e-10, -eig.min()+1e-10)
    if policy.endswith("ucb"):
        return f+bonus*np.sqrt(np.maximum(np.diag(cov), 0))+season_now
    return f+np.linalg.cholesky(cov)@rng.standard_normal(n)+season_now


def run_policy(y, raw, weekdays, fit, engine, policy, seed, batch, bonus=1., prefix=366, traces=False):
    rng = np.random.default_rng(SEED+seed)
    engine = copy.deepcopy(engine)
    de = y-fit["season"][weekdays]
    history = de[:prefix].copy()
    rows = []; cum = 0.; start = time.perf_counter()
    for t in range(prefix, len(y)):
        score = policy_scores(policy, engine, history, fit["season"][weekdays[t]], rng, bonus, prefix)
        if policy == "round_robin":
            chosen = ((t-prefix)*batch+np.arange(batch))%y.shape[1]
        else:
            chosen = np.argsort(-score, kind="stable")[:batch]
        # All current values are read only after the batch has been chosen.
        oracle = np.argsort(-y[t])[:batch]
        regret = float(y[t, oracle].sum()-y[t, chosen].sum())
        assert regret >= -1e-10
        raw_loss = float(raw[t, oracle].sum()-raw[t, chosen].sum())
        cum += regret
        recorded = np.full(y.shape[1], np.nan)
        filtered = policy.startswith(("ar_", "st_", "rewired_", "factor_", "empirical_"))
        for i in chosen:
            if filtered:
                engine.update(int(i), de[t, i])
            recorded[i] = de[t, i]
        if filtered:
            engine.propagate()
        history = np.vstack((history, recorded))
        rows.append({"day": t-prefix, "chosen": ",".join(map(str, chosen)), "regret": regret,
                     "raw_view_loss": raw_loss, "raw_views": float(raw[t, chosen].sum()),
                     "oracle_views": float(raw[t, oracle].sum()), "overlap": len(set(chosen)&set(oracle))/batch,
                     "cumulative_regret": cum})
    seconds = time.perf_counter()-start
    summary = {"policy": policy, "seed": seed, "batch": batch, "days": len(rows), "paid_test_observations": batch*len(rows),
               "regret_per_slot": cum/(batch*len(rows)), "raw_view_loss_per_slot": sum(x["raw_view_loss"] for x in rows)/(batch*len(rows)),
               "captured_views_fraction": sum(x["raw_views"] for x in rows)/sum(x["oracle_views"] for x in rows),
               "top_batch_overlap": float(np.mean([x["overlap"] for x in rows])), "seconds": seconds,
               "milliseconds_per_decision": 1000*seconds/len(rows), "ucb_bonus": bonus}
    return summary, rows if traces else []


def verify():
    rng = np.random.default_rng(1)
    a = np.array([.4, -.1, .2]); q = np.array([[.4, .1], [.1, .3]])
    engine = Filter(a, q); n, p = engine.n, engine.p
    d = n*(p+1)
    b = rng.normal(size=d); x = rng.normal(size=(d, d)); v = x@x.T+np.eye(d)
    engine.m, engine.v = b.copy(), v.copy()
    f = np.zeros((d, d)); f[:n, :n] = np.eye(n)
    f[n:2*n, n:] = np.kron(a.reshape(1, -1), np.eye(n))
    f[2*n:, n:-n] = np.eye((p-1)*n)
    noise = np.zeros((d, d)); noise[n:2*n, n:2*n] = q
    engine.propagate()
    assert np.allclose(engine.m, f@b)
    assert np.allclose(engine.v, f@v@f.T+noise)
    h = np.zeros(d); h[0] = h[n] = 1
    b, v = engine.m.copy(), engine.v.copy(); y = 2.
    column = v@h; den = h@column+R
    engine.update(0, y)
    assert np.allclose(engine.m, b+column*(y-h@b)/den)
    assert np.allclose(engine.v, v-np.outer(column, column)/den)
    return {"dense_transition_and_update": "pass", "state_dimension": d}


def main(seeds, orders, output):
    t0 = time.perf_counter(); output.mkdir(parents=True, exist_ok=True)
    checks = verify(); summaries, all_traces = [], []
    metadata = {"seed": SEED, "seeds_per_stochastic_policy": seeds, "orders": orders,
                "panels": {}, "feedback": "selected exact observed log1p views", "sensor_regularization": R,
                "theoretical_mean_pcs_and_floor": "not_identifiable_from_real_panel",
                "full_history_fit_exposure_per_panel": 366*24,
                "graph_type": "binary undirected within-panel pre-2024 hyperlinks",
                "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for name in ("astronomy", "football"):
        dates, raw, w, titles = load_panel(name)
        y = np.log1p(raw); weekdays = dates.dayofweek.to_numpy()
        wr, swaps = rewire(w)
        info = {"titles": titles, "edges": int(w.sum()/2), "isolated_nodes": int((w.sum(0) == 0).sum()),
                "rewiring_swaps": swaps, "models": {}}
        for order in orders:
            specs, ll = select_covariances(y[:366], weekdays[:366], w, wr, order)
            fit = fit_ar(y[:366], weekdays[:366], order)
            engines = {}
            for kind, graph in [("ar", w), ("st", w), ("rewired", wr), ("factor", w), ("empirical", w)]:
                q = covariance(fit, graph, kind, **specs[kind])
                engines[kind] = burnin(y[:366], weekdays[:366], fit, q)
            bonuses = {}
            policies = POLICIES if order == 7 else ("ar_predictive_ucb", "ar_predictive_ts", "st_predictive_ucb", "st_predictive_ts")
            # Bonus selection uses only the 2024 development field with a separate prefix.
            dev_fit = fit_ar(y[:274], weekdays[:274], order)
            dev_engines = {k: burnin(y[:274], weekdays[:274], dev_fit,
                                     covariance(dev_fit, wr if k == "rewired" else w, k, **specs[k])) for k in ("ar", "st")}
            for policy in policies:
                if policy.endswith("ucb"):
                    losses = []
                    for bonus in (.5, 1., 2.):
                        row, _ = run_policy(y[:366], raw[:366], weekdays[:366], dev_fit,
                                            dev_engines[kind_of(policy)], policy, 999, 1, bonus, prefix=274)
                        losses.append((row["regret_per_slot"], bonus))
                    bonuses[policy] = min(losses)[1]
            # Complete covariance/AR metadata allows audit and exact reproduction.
            info["models"][str(order)] = {"lags": list(fit["lags"]), "ar_coefficients": fit["a"].tolist(),
                "spectral_radius": fit["radius"], "original_spectral_radius": fit["original_radius"],
                "stability_scale": fit["stability_scale"], "common_residual_correlation": fit["common"],
                "validation_log_scores": ll, "covariance_specs": specs, "ucb_bonuses": bonuses,
                "state_dimension": 24*(order+1), "single_covariance_mb": (24*(order+1))**2*8/1e6}
            np.savez_compressed(output / f"{name}_ar{order}_model.npz", coefficients=fit["a"], season=fit["season"],
                                graph=w, rewired_graph=wr, **{f"Q_{k}": v.q for k, v in engines.items()})
            for batch in (1, 5):
                for policy in policies:
                    reps = range(seeds if order == 7 else min(seeds, 3)) if policy.endswith("ts") else (0,)
                    for seed in reps:
                        row, trace = run_policy(y, raw, weekdays, fit, engines[kind_of(policy)], policy, seed,
                                                batch, bonuses.get(policy, 1.), traces=True)
                        row.update(panel=name, order=order); summaries.append(row)
                        for daily in trace:
                            daily.update(panel=name, order=order, batch=batch, policy=policy, seed=seed)
                        all_traces.extend(trace)
                    print(f"{name} AR({order}) batch={batch} {policy}: {np.mean([r['regret_per_slot'] for r in summaries if r['panel']==name and r['order']==order and r['batch']==batch and r['policy']==policy]):.4f}", flush=True)
        metadata["panels"][name] = info
    pd.DataFrame(summaries).to_csv(output / "runs.csv", index=False)
    pd.DataFrame(all_traces).to_csv(output / "daily.csv", index=False)
    metadata["wall_seconds"] = time.perf_counter()-t0
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    metadata["peak_rss_mb"] = rss/(1e6 if sys.platform == "darwin" else 1024)
    metadata["record_count"] = len(summaries)
    checks.update({"real_panel_complete": "pass", "graph_cutoffs": "pass", "rewiring_degrees": "pass",
                   "predictable_covariance_psd_every_policy_decision": "pass", "nonnegative_oracle_regret": "pass",
                   "batch_selected_before_feedback": "pass_by_observed_only_score_interface"})
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    (output / "checks.json").write_text(json.dumps(checks, indent=2)+"\n")
    print(f"Finished {len(summaries)} runs in {metadata['wall_seconds']:.1f}s; peak RSS {metadata['peak_rss_mb']:.1f} MB", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--orders", type=int, nargs="+", default=[7, 20])
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args(); main(args.seeds, args.orders, args.output)
