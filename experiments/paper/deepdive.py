"""Deep-dive analyses that connect each theoretical prediction to the saved experiment results.

Usage (from the repo root; KuaiRec data and all result files must exist):
    OPENBLAS_NUM_THREADS=2 .venv/bin/python -I experiments/paper/deepdive.py

Writes research/claude_opus_10_09_v2/analysis/<name>.{csv,md}:
  P2a  certified_gain_vs_rejectable  SP-UCB theorem: gain only from components with eps_c < Gamma_c
  P2b  uncertified_failure_mechanism  zero-width pooling fails when the optimal component is not
                                      the top component by average (dilution)
  P3a  b2_prediction_vs_observed      B2 variance inflation predicts iid-certificate violations
  P4a  exploration_vs_horizon         exploration pays only with enough future observations per arm
  P4b  toy_learning_curves            regret per round over time, benchmark
  D1   wikipedia_turnover             where the Wikipedia regret comes from (rank turnover)
  D2   kuairec_cohort_drift           level shifts behind the stationary-mean misfit on KuaiRec daily
"""

from __future__ import annotations

import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments"
sys.path.insert(0, str(EXP / "kuairec" / "code"))
KR = EXP / "kuairec" / "results"
ST = EXP / "simulations" / "spatiotemporal_benchmark" / "results"
CP = EXP / "simulations" / "certificates_under_persistence" / "results"
WS = {d: EXP / "wikipedia" / d / "one_domain" for d in ("data", "results")}
WM = {d: EXP / "wikipedia" / d / "six_domains" for d in ("data", "results")}
OUT = ROOT / "research" / "claude_opus_10_09_v2" / "analysis"


def save(df: pd.DataFrame, name: str, note: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / f"{name}.csv", index=False)
    (OUT / f"{name}.md").write_text(f"{note}\n\n" + df.to_markdown(index=False, floatfmt=".3f") + "\n")
    print(f"\n## {name}\n{note}\n{df.to_string(index=False)}")


def p2a_certified_gain() -> None:
    r = pd.read_csv(KR / "setting_a_runs.csv")
    ins = pd.read_csv(KR / "setting_a_instances.csv")
    col = "regret@20000"
    ucb = r[r.policy == "ucb"].set_index("user")[col]
    rows = []
    for cert, share in (("oracle", "rejectable_oracle"), ("energy", "rejectable_energy")):
        s = r[(r.policy == "sp_ucb") & (r.param == cert)][["user", "graph", col]].copy()
        s["ratio"] = s[col].to_numpy() / ucb.reindex(s.user).to_numpy()
        m = s.merge(ins, on=["user", "graph"])
        OUT.mkdir(parents=True, exist_ok=True)
        m[["user", "graph", "ratio", share]].to_csv(OUT / f"certified_instances_{cert}.csv", index=False)
        rho, p = stats.spearmanr(m[share], np.log(m.ratio))
        m["bin"] = pd.cut(m[share], [-0.01, 0.4, 0.6, 0.8, 1.0], labels=["<=40%", "40-60%", "60-80%", ">80%"])
        for b, g in m.groupby("bin", observed=True):
            rows.append({"certificate": cert, "rejectable share": str(b), "instances": len(g),
                         "median ratio to UCB1": g.ratio.median(), "q25": g.ratio.quantile(0.25),
                         "q75": g.ratio.quantile(0.75), "spearman (all)": rho, "p": p})
    save(pd.DataFrame(rows), "certified_gain_vs_rejectable",
         "Setting A, 60 users x 6 graphs: SP-UCB regret / UCB1 regret against the share of suboptimal "
         "components whose certified width is below their gap (the condition for H_c < infinity).")


def p2b_uncertified_failure() -> None:
    import setting_a as A
    from data import load_eval
    from graphs import build, rewire
    feats = A.load_features()
    _, _, M = load_eval("R1")
    perm = np.random.default_rng(A.SEED).permutation(M.shape[0])
    test = np.sort(perm[M.shape[0] // 2:])[:60]
    rows = []
    for u in test:
        rng = np.random.default_rng(A.SEED + int(u))
        nodes = np.sort(rng.choice(np.flatnonzero(~np.isnan(M[u])), size=300, replace=False))
        mu = M[u, nodes].astype(float)
        for g in A.GRAPH_NAMES:
            grng = np.random.default_rng(A.SEED + 31 * int(u) + zlib.crc32(g.encode()) % 1000)
            W = build(feats, g.split("~")[0], 10, grng, nodes)
            if g.endswith("~rewired"):
                W = rewire(W, grng)
            lab = A.partition(W, A.SEED + int(u))
            means = np.array([mu[lab == c].mean() for c in range(lab.max() + 1)])
            cb = lab[np.argmax(mu)]
            rows.append({"user": int(u), "graph": g, "optimal_component_top": bool(means[cb] >= means.max()),
                         "optimal_component_size": int((lab == cb).sum()), "pooled_shortfall": means.max() - means[cb]})
    D = pd.DataFrame(rows)
    r = pd.read_csv(KR / "setting_a_runs.csv")
    col = "regret@20000"
    ucb = r[r.policy == "ucb"].set_index("user")[col]
    s = r[(r.policy == "sp_ucb") & (r.param == "none")][["user", "graph", col]].copy()
    s["ratio"] = s[col].to_numpy() / ucb.reindex(s.user).to_numpy()
    m = s.merge(D, on=["user", "graph"])
    OUT.mkdir(parents=True, exist_ok=True)
    m.to_csv(OUT / "uncertified_instances.csv", index=False)
    out = []
    for key, g in m.groupby("optimal_component_top"):
        out.append({"optimal component is top by average": key, "instances": len(g), "median ratio to UCB1": g.ratio.median(),
                    "90th pct": g.ratio.quantile(0.9), "share worse than UCB1": (g.ratio > 1).mean()})
    rho_size, p_size = stats.spearmanr(m.optimal_component_size, np.log(m.ratio))
    rho_short, p_short = stats.spearmanr(m.pooled_shortfall, np.log(m.ratio))
    per_graph = m.groupby("graph").agg(share_worse=("ratio", lambda x: (x > 1).mean()),
                                       optimal_top=("optimal_component_top", "mean")).reset_index()
    save(pd.DataFrame(out), "uncertified_failure_mechanism",
         f"Setting A, SP-UCB with zero width (no certificate) / UCB1. Spearman with the optimal component's size: "
         f"{rho_size:.3f} (p={p_size:.1e}); with the pooled shortfall (top component average minus the optimal "
         f"component's average): {rho_short:.3f} (p={p_short:.1e}).")
    save(per_graph, "uncertified_failure_by_graph", "Share of users for whom uncertified pooling is worse than UCB1, "
         "and share of instances where the optimal component is the top component by average.")


def p3a_b2() -> None:
    def inflation(phi: float, b: int, V: float = 1.0, r: float = 0.01) -> float:
        if phi == 0:
            return 1.0
        f = (1 + phi) / (1 - phi) - 2 * phi * (1 - phi ** b) / (b * (1 - phi) ** 2)
        return float(np.sqrt((V * f + r) / (V + r)))
    ell = np.log(2 * 24 * 5000 / 0.05)
    d = pd.read_csv(CP / "coverage_runs_plugin.csv")
    rows = []
    for phi in (0.0, 0.5, 0.9, 0.97):
        k = inflation(phi, 25)
        for cfg in ("independent", "correlated"):
            s = d[(d.policy == "sp_ucb_iid") & (d.phi == phi) & (d.batch == 25) & (d.config == cfg)]
            s1 = d[(d.policy == "sp_ucb_iid") & (d.phi == phi) & (d.batch == 1) & (d.config == cfg)]
            st2 = d[(d.policy == "sp_ucb_st2") & (d.phi == phi) & (d.batch == 25) & (d.config == cfg)]
            rows.append({"phi": phi, "shocks": cfg, "B2 sd inflation (blocks of 25)": k,
                         "B2 per-check miscoverage": 2 * norm.cdf(-np.sqrt(2 * ell) / k),
                         "iid runs violated (blocks)": s.any_violation.mean(),
                         "iid rounds violated (blocks)": s.violation_share.mean(),
                         "iid runs violated (one at a time)": s1.any_violation.mean(),
                         "B1'' runs violated (blocks)": st2.any_violation.mean()})
    save(pd.DataFrame(rows), "b2_prediction_vs_observed",
         "B2: sampling an AR(1) arm in blocks of b consecutive pulls inflates the sample-mean standard deviation by "
         "sqrt(f(b, phi)); per-check miscoverage of the iid radius is 2 Phi(-sqrt(2 ell) / inflation). Observed "
         "violation rates are for SP-UCB with iid certificates (24 statistics checked every round).")


def panel_stats(Y: np.ndarray, starts, length: int | None, k: int = 10) -> dict:
    """Near-tie gap and turnover of the oracle top k, and fluctuation-to-level ratio of a daily panel."""
    gaps, turns = [], []
    for F in starts:
        T = Y[F:F + length] if length else Y[F:]
        gaps += [np.sort(T[t])[-k] - np.sort(T[t])[-k - 1] for t in range(len(T))]
        turns += [1 - len(set(np.argsort(-T[t])[:k]) & set(np.argsort(-T[t - 1])[:k])) / k for t in range(1, len(T))]
    X = Y - Y.mean(0)
    return {"10th-11th gap": float(np.mean(gaps)), "daily top-10 turnover": float(np.mean(turns)),
            "fluctuation sd / level sd": float(X.std() / Y.mean(0).std())}


def p4a_exploration() -> None:
    import daily as d
    toy = pd.concat([pd.read_csv(ST / "runs.csv"), pd.read_csv(ST / "runs_extra.csv")])
    toy = toy[toy.config == "main"].groupby("policy")["dyn@2000"].mean() / 2000
    kd = pd.concat([pd.read_csv(KR / "daily_runs.csv"), pd.read_csv(KR / "daily_runs_extra.csv")]).groupby("policy").regret_per_day.mean()
    ks = pd.read_csv(KR / "daily_runs_sparse.csv").groupby("policy").regret_per_day.mean()
    ws = pd.read_csv(WS["results"] / "runs.csv").groupby("policy").regret_per_day.mean()
    Yk, _, _ = d.panel()
    kstats = panel_stats(Yk, (28, 35, 42), None)
    wsY = np.log1p(pd.read_csv(WS["data"] / "views.csv", index_col="date").to_numpy(float))
    rows = [
        {"environment": "Benchmark (100 arms, AR(20))", "observations per arm in horizon": 20.0, "prior history": "none",
         "greedy": toy["st_greedy"], "UCB 1 sd": toy["st_ucbm1"], "predictive sampling": toy["st_ps"], "iid TS": toy["ts"],
         "10th-11th gap": np.nan, "daily top-10 turnover": np.nan, "fluctuation sd / level sd": 1.0 / 0.5},
        {"environment": "Wikipedia, one domain", "observations per arm in horizon": 120 * 10 / 150, "prior history": "365 days, full",
         "greedy": ws["st_greedy"], "UCB 1 sd": ws["st_ucbm1"], "predictive sampling": ws["st_jps"], "iid TS": ws["ts_iid"],
         **panel_stats(wsY, (365, 730, 1095), 120)},
        {"environment": "KuaiRec daily, full history", "observations per arm in horizon": 28 * 10 / 253, "prior history": "28-42 days, full",
         "greedy": kd["st_greedy"], "UCB 1 sd": kd["st_ucbm1"], "predictive sampling": kd["st_jps"], "iid TS": kd["ts_iid"], **kstats},
        {"environment": "KuaiRec daily, sparse history", "observations per arm in horizon": 28 * 10 / 253, "prior history": "10 videos per day",
         "greedy": ks["sh_greedy"], "UCB 1 sd": ks["sh_ucbm1"], "predictive sampling": ks["sh_jps"], "iid TS": ks["sh_tsiid"], **kstats},
    ]
    if (WM["results"] / "runs.csv").exists():
        wm = pd.read_csv(WM["results"] / "runs.csv").groupby("policy").regret_per_day.mean()
        wmY = np.log1p(pd.read_csv(WM["data"] / "views.csv", index_col="date").to_numpy(float))
        rows.insert(2, {"environment": "Wikipedia, six domains", "observations per arm in horizon": 120 * 10 / 150,
                        "prior history": "365 days, full", "greedy": wm["st_greedy"], "UCB 1 sd": wm["st_ucbm1"],
                        "predictive sampling": wm["st_jps"], "iid TS": wm["ts_iid"], **panel_stats(wmY, (365, 730, 1095), 120)})
    df = pd.DataFrame(rows)
    df["PS / greedy"] = df["predictive sampling"] / df["greedy"]
    df["UCB 1 sd / greedy"] = df["UCB 1 sd"] / df["greedy"]
    df["best model / iid TS"] = df[["greedy", "UCB 1 sd", "predictive sampling"]].min(axis=1) / df["iid TS"]
    save(df, "exploration_vs_horizon", "Regret per round (benchmark) or per day (panels). Predictive sampling explores "
         "all uncertainty that persists; UCB with a 1-sd bonus adds mild optimism. Panel statistics describe the test windows.")


def d4_graph_decisions() -> None:
    """Six-domain Wikipedia: paired effect of the graph in the shock covariance on decisions."""
    path = WM["results"] / "runs.csv"
    if not path.exists():
        return
    d = pd.read_csv(path)
    rows = []
    for base, others in (("st_greedy_nograph", ("st_greedy", "st_greedy_block", "st_greedy_rewired")),
                         ("st_jps_nograph", ("st_jps", "st_jps_block"))):
        b = d[d.policy == base].set_index(["origin", "seed"]).regret_per_day
        for p in others:
            x = d[d.policy == p].set_index(["origin", "seed"]).regret_per_day
            diff = (x - b).dropna()
            rows.append({"policy": p, "baseline": base, "runs": len(diff), "mean difference": diff.mean(),
                         "standard error": diff.std() / np.sqrt(len(diff)), "relative": diff.mean() / b.mean()})
    save(pd.DataFrame(rows), "wikipedia_multi_graph_effect", "Six-domain Wikipedia: regret per day with a graph-shrunk "
         "shock covariance minus regret with the common-factor covariance, paired by origin and noise seed.")


def p4b_toy_curves() -> None:
    t = pd.concat([pd.read_csv(ST / "runs.csv"), pd.read_csv(ST / "runs_extra.csv")])
    rows = []
    for cfg in ("main", "no_spatial", "weak_persistence"):
        x = t[t.config == cfg]
        for c in (100, 250, 500, 1000, 2000):
            row = {"configuration": cfg, "t": c, "t / N": c / 100}
            for p in ("st_ps", "st_ucbm2", "st_greedy", "ar_ps", "spectral_ucb", "ucb", "ts"):
                row[p] = x[x.policy == p][f"dyn@{c}"].mean() / c
            rows.append(row)
    save(pd.DataFrame(rows), "toy_learning_curves", "Benchmark: average dynamic regret per round over the first t rounds.")


def d1_wikipedia_turnover() -> None:
    rows = []
    for name, base in (("one domain", WS), ("six domains", WM)):
        path = base["data"] / "views.csv"
        if not path.exists():
            continue
        v = pd.read_csv(path, index_col="date")
        Y = np.log1p(v.to_numpy(float))
        runs = pd.read_csv(base["results"] / "runs.csv") if (base["results"] / "runs.csv").exists() else None
        for F in (365, 730, 1095):
            T = Y[F:F + 120]
            top = [set(np.argsort(-T[t])[:10]) for t in range(len(T))]
            fit_top = set(np.argsort(-Y[F - 365:F].mean(0))[:10])
            row = {"panel": name, "origin": F, "test starts": str(v.index[F]),
                   "daily top-10 turnover": np.mean([1 - len(top[t] & top[t - 1]) / 10 for t in range(1, len(top))]),
                   "top-10 outside fit-window top-10": np.mean([1 - len(s & fit_top) / 10 for s in top]),
                   "10th-11th gap": np.mean([np.sort(T[t])[-10] - np.sort(T[t])[-11] for t in range(len(T))])}
            if runs is not None:
                g = runs[runs.origin == F].groupby("policy").regret_per_day.mean()
                row.update({"regret: best model": g.drop(["fit_mean", "last_value", "ts_iid"], errors="ignore").min(),
                            "regret: iid TS": g.get("ts_iid", np.nan)})
            rows.append(row)
    save(pd.DataFrame(rows), "wikipedia_turnover", "Where Wikipedia regret comes from: turnover of the oracle's top 10.")


def d2_kuairec_drift() -> None:
    import daily as d
    Y, keep, _ = d.panel()
    f = pd.read_csv(ROOT / "data" / "kuairec_raw" / "KuaiRec 2.0" / "data" / "item_daily_features.csv",
                    usecols=["video_id", "upload_dt"])
    up = f.drop_duplicates("video_id").set_index("video_id").upload_dt.reindex(keep)
    age0 = (pd.Timestamp("2020-07-05") - pd.to_datetime(up)).dt.days.to_numpy()
    rows = []
    for a, b in ((0, 21), (21, 42), (42, 63)):
        sl = np.array([np.polyfit(np.arange(b - a), Y[a:b, i], 1)[0] for i in range(Y.shape[1])])
        rows.append({"days": f"{a + 1}-{b}", "mean slope per day": sl.mean(), "mean |slope|": np.abs(sl).mean(),
                     "spearman(|slope|, age at start)": stats.spearmanr(np.abs(sl), age0)[0]})
    save(pd.DataFrame(rows), "kuairec_cohort_drift",
         f"KuaiRec daily (253 videos): logit complete-play rate. Median video age at the start of the panel: "
         f"{np.nanmedian(age0):.0f} days, so the panel is one upload cohort; mean level change from days 1-21 to 43-63: "
         f"{(Y[42:63].mean(0) - Y[:21].mean(0)).mean():+.3f} (mean absolute {np.abs(Y[42:63].mean(0) - Y[:21].mean(0)).mean():.3f}).")


def d3_kuairec_heldout() -> None:
    """Policy-free fluctuation-channel test on KuaiRec daily, matching the Wikipedia diagnostics."""
    import daily as d
    from graphs import rewire
    Y, keep, nodes = d.panel()
    N = Y.shape[1]
    grng = np.random.default_rng(20261009)
    targets = {"no graph (common shock)": np.eye(N), "I-coeng": d.graph_corr("I-coeng", nodes, grng, 5.0),
               "I-coeng rewired": d.graph_corr("I-coeng", nodes, grng, 5.0, rewired=True),
               "I-mf": d.graph_corr("I-mf", nodes, grng, 5.0)}
    rows = []
    for name, C_G in targets.items():
        lls = []
        for F in (28, 35, 42):
            m, a, Q, _ = d.fit_model(Y[:F], C_G)
            Xt = Y[F - 7:] - m
            E = np.stack([Xt[t] - a[0] * Xt[t - 1] - a[1] * Xt[t - 2] - a[6] * Xt[t - 7] for t in range(7, len(Xt))])
            _, logdet = np.linalg.slogdet(Q)
            lls.append(float((-0.5 * (N * np.log(2 * np.pi) + logdet + np.einsum("ti,ij,tj->t", E, np.linalg.inv(Q), E))).mean()))
        rows.append({"covariance target": name, "F=28": lls[0], "F=35": lls[1], "F=42": lls[2], "mean": np.mean(lls)})
    save(pd.DataFrame(rows), "kuairec_heldout_loglik", "KuaiRec daily: held-out Gaussian log-likelihood per day of AR "
         "residuals under each innovation-covariance target (fit on days 1..F, scored on the rest).")


if __name__ == "__main__":
    p2a_certified_gain()
    p2b_uncertified_failure()
    p3a_b2()
    p4b_toy_curves()
    d2_kuairec_drift()
    d3_kuairec_heldout()
    p4a_exploration()
    d1_wikipedia_turnover()
    d4_graph_decisions()
