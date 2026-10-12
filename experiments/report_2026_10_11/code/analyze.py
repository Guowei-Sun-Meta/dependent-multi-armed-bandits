"""Inventory existing evidence, recompute comparisons and draw report figures."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import importlib.util

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
OUT, FIG = HERE / "results", HERE / "figures"
SOURCES = {}
SEED = 20261011
COLORS = ["#247ba0", "#ed8b34", "#549f65", "#b24c63", "#7865ad", "#6e747c"]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "savefig.facecolor": "white"})


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read(path):
    p = ROOT / path
    SOURCES[path] = sha(p)
    return pd.read_csv(p)


def output(name, frame):
    frame.to_csv(OUT / (name + ".csv"), index=False)
    (OUT / (name + ".md")).write_text(frame.round(5).to_markdown(index=False) + "\n")


def figure(fig, name):
    fig.savefig(FIG / (name + ".png"), dpi=180, bbox_inches="tight")
    fig.savefig(FIG / (name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def inventory():
    rows, first = [], {}
    for folder in [ROOT / "experiments", ROOT / "research"]:
        for p in sorted(folder.rglob("*")):
            if not p.is_file() or HERE in p.parents:
                continue
            if p.suffix not in [".csv", ".json", ".jsonl", ".npz", ".md"]:
                continue
            rel = str(p.relative_to(ROOT))
            if "/results/" not in rel and p.name not in ["README.md", "findings.md"] and p.name != "temporal_information.csv":
                continue
            fingerprint = sha(p)
            schema, count = [], None
            if p.suffix == ".csv":
                with p.open(newline="") as f:
                    reader = csv.reader(f)
                    schema = next(reader, [])
                    count = sum(1 for _ in reader)
            elif p.suffix == ".jsonl":
                with p.open() as f:
                    count = sum(1 for line in f if line.strip())
            rows.append({"path": rel, "bytes": p.stat().st_size, "sha256": fingerprint,
                         "rows": count, "columns": json.dumps(schema),
                         "frozen_copy": "/gpt_sol_10_09/evidence/" in rel,
                         "exact_duplicate_of": first.get(fingerprint, "")})
            first.setdefault(fingerprint, rel)
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "artifact_inventory.csv", index=False)
    return d


def overnight():
    base = "experiments/oct10_evening/results/setting_a2/"
    main = read(base + "setting_a2_runs_120x3.csv")
    user = read(base + "setting_a2_runs_120x3_usercal.csv")
    assert len(main) == 10440 and len(user) == 1440
    for d in [main, user]:
        assert not d.duplicated(["user", "rep", "policy", "graph", "param"]).any()
        assert d.user.nunique() == 120
        assert d.groupby(["user", "policy", "graph", "param"]).rep.nunique().eq(3).all()
    d = pd.concat([main, user], ignore_index=True)
    U = d.groupby(["user", "policy", "graph", "param"])["regret@20000"].mean().unstack(["policy", "graph", "param"])
    I = d.pivot(index=["user", "rep"], columns=["policy", "graph", "param"], values="regret@20000")
    rng = np.random.default_rng(SEED)
    ix = rng.integers(len(U), size=(2000, len(U)))
    rows = []
    for ref in [("ts", "-", "-"), ("klucb", "-", "ell"), ("klucb", "-", "logt")]:
        b = U[ref].to_numpy()
        assert (b > 0).all()
        for key in U:
            a = U[key].to_numpy()
            low, high = np.quantile(a[ix].mean(1) / b[ix].mean(1), [.025, .975])
            ratio = a / b
            rows.append({"policy": key[0], "graph": key[1], "param": key[2], "reference": "/".join(ref),
                         "users": len(U), "mean_regret": float(a.mean()), "ratio_of_means": float(a.mean() / b.mean()),
                         "ci_low": low, "ci_high": high, "mean_instance_ratio": float((I[key] / I[ref]).mean()),
                         "median_user_ratio": float(np.median(ratio)), "p90_user_ratio": float(np.quantile(ratio, .9)),
                         "share_users_above_2x": float((ratio > 2).mean())})
    comp = pd.DataFrame(rows)
    output("overnight_comparisons", comp)
    graph_contrasts = []
    pairs = [(("spectral_ts", "I-mf", "10.0"), ("spectral_ts", "I-mf~rewired", "10.0")),
             (("sp_klucb", "I-mf", "oracle"), ("sp_klucb", "I-mf~rewired", "oracle")),
             (("sp_klucb", "I-mf", "none"), ("sp_klucb", "I-mf~rewired", "none")),
             (("shrink_ts", "complete", "10.0"), ("spectral_ts", "I-mf", "10.0"))]
    for candidate, baseline in pairs:
        a, b = U[candidate].to_numpy(), U[baseline].to_numpy()
        low, high = np.quantile(a[ix].mean(1) / b[ix].mean(1) - 1, [.025, .975])
        graph_contrasts.append({"candidate": "/".join(candidate), "baseline": "/".join(baseline),
                               "relative_difference": float(a.mean()/b.mean()-1), "ci_low": low, "ci_high": high,
                               "users":120, "scope":"user-cluster bootstrap, conditional on common tuning data"})
    output("overnight_graph_contrasts", pd.DataFrame(graph_contrasts))
    diag = read(base + "setting_a2_instances_120x3.csv")
    diaguser = read(base + "setting_a2_instances_120x3_usercal.csv")
    crows = []
    for graph, g in diag.groupby("graph"):
        for cert in ["oracle", "energy", "cal90", "cal50", "none"]:
            crows.append({"graph": graph, "certificate": cert, "valid_component_fraction": g[f"valid_{cert}"].mean(),
                          "rejectable_component_fraction": g[f"rejectable_{cert}"].mean(), "mean_width": g[f"mean_width_{cert}"].mean(),
                          "diagnostic_basis": "true component ranges"})
    for graph, g in diaguser.groupby("graph"):
        for cert in ["user90", "user75"]:
            crows.append({"graph": graph, "certificate": cert, "valid_component_fraction": g[f"valid_{cert}"].mean(),
                          "rejectable_component_fraction": np.nan, "mean_width": g[f"mean_width_{cert}"].mean(),
                          "diagnostic_basis": "true user level, not realized noisy warm-up"})
    cert = pd.DataFrame(crows)
    output("overnight_certificates", cert)
    selection = [("shrink_ts", "complete", "10.0", "Graph-free shrinkage TS"),
                 ("spectral_ts", "I-mf", "10.0", "Spectral TS, I-mf"),
                 ("spectral_ts", "I-mf~rewired", "10.0", "Spectral TS, rewired"),
                 ("spectral_ts", "I-coeng", "10.0", "Spectral TS, I-coeng"),
                 ("sp_klucb", "I-mf", "none", "Pooling, no certificate"),
                 ("sp_klucb", "I-mf", "oracle", "Pooling, oracle width"),
                 ("sp_klucb", "I-mf", "user75", "Pooling, user 75%"),
                 ("sp_klucb", "I-mf", "cal90", "Pooling, global 90%")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), gridspec_kw={"width_ratios": [1.4, 1]})
    sub = comp[comp.reference == "ts/-/-"].set_index(["policy", "graph", "param"])
    for i, (p, g, v, label) in enumerate(selection):
        r = sub.loc[(p, g, v)]
        axes[0].errorbar(r.ratio_of_means, i, xerr=[[r.ratio_of_means-r.ci_low], [r.ci_high-r.ratio_of_means]],
                         fmt="o", color=COLORS[0] if p != "sp_klucb" else COLORS[1], capsize=3)
    axes[0].set_yticks(range(len(selection)), [x[3] for x in selection])
    axes[0].invert_yaxis(); axes[0].axvline(1, color="gray", ls="--")
    axes[0].set_xlabel("Ratio of mean regret to Bernoulli TS\n120 user clusters; 95% paired bootstrap")
    axes[0].set_title("A. Baseline choice changes the conclusion")
    sub = comp[(comp.reference == "klucb/-/ell") & (comp.graph == "I-mf") & (comp.policy == "sp_klucb")].set_index("param")
    c = cert[cert.graph == "I-mf"].set_index("certificate")
    for i, name in enumerate(["none", "cal50", "user75", "user90", "cal90", "energy", "oracle"]):
        x, y = c.loc[name, "valid_component_fraction"], sub.loc[name, "ratio_of_means"]
        axes[1].scatter(x, y, color=COLORS[i % len(COLORS)], s=50)
        offset = (-48, 8) if name == "energy" else (5, -14) if name == "cal90" else (5, 5)
        axes[1].annotate(name, (x, y), xytext=offset, textcoords="offset points", fontsize=9)
    axes[1].axhline(1, color="gray", ls="--"); axes[1].set_xlim(-.06, 1.15)
    axes[1].set_ylim(.3, 1.1); axes[1].set_xlabel("Fraction of components with valid widths\nuser75/user90 evaluated at true user level")
    axes[1].set_ylabel("Ratio of mean regret to matched KL-UCB")
    axes[1].set_title("B. Practical widths lose the oracle gain")
    fig.tight_layout(); figure(fig, "01_overnight_pooling")
    return comp


def real_panels():
    d = read("experiments/oct10_evening/results/daily_chrono/test_runs.csv")
    U = d.groupby(["unit", "k", "policy"]).regret_per_slot_day.mean().unstack("policy")
    rows = []
    for k, g in U.groupby(level="k"):
        for p in g:
            rows.append({"panel": "KuaiRec chronological", "budget": k, "policy": p,
                         "loss": g[p].mean(), "ratio_to_iid_ts": g[p].mean()/g.ts_iid.mean()})
    w = read("experiments/today_2026_10_10/results/wikipedia/summary.csv")
    for (panel, b), g in w.groupby(["panel", "batch"]):
        ref = g.set_index("policy").loc["iid_ts", "loss_per_slot"]
        for _, r in g.iterrows():
            rows.append({"panel": "Wikipedia " + panel, "budget": b, "policy": r.policy,
                         "loss": r.loss_per_slot, "ratio_to_iid_ts": r.loss_per_slot/ref})
    table = pd.DataFrame(rows); output("real_panel_baselines", table)
    contrasts = []
    rng = np.random.default_rng(SEED)
    for k, g in U.groupby(level="k"):
        g = g.droplevel("k").copy(); g["window"] = g.index.str.extract(r"_F(\d+)_", expand=False).astype(int)
        groups = {v: h for v, h in g.groupby("window")}
        windows = list(groups)
        for a, b in [("st_ucb", "ts_iid"), ("st_ucb", "ar_ucb"), ("st_ucb", "st_ucb_rewired"),
                     ("st_ucb", "st_ucb_nograph"), ("st_ucb", "last_value"), ("st_greedy", "last_value"), ("st_ucb", "ewma")]:
            stats = []
            for _ in range(4000):
                num = den = 0.
                for v in rng.choice(windows, len(windows)):
                    h = groups[v]; ix = rng.integers(len(h), size=len(h))
                    num += h[a].to_numpy()[ix].sum(); den += h[b].to_numpy()[ix].sum()
                stats.append(num / den - 1)
            lo, hi = np.quantile(stats, [.025, .975])
            contrasts.append({"budget": k, "policy": a, "reference": b,
                              "relative_difference": g[a].mean()/g[b].mean()-1,
                              "ci_low": lo, "ci_high": hi, "windows": 3, "panel_windows": 15})
    output("kuairec_chronological_contrasts", pd.DataFrame(contrasts))
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
    names = {"static": "Static", "iid_ts": "IID TS", "last": "Last value", "last_value": "Last value",
             "ewma": "EWMA", "ar_greedy": "AR greedy", "st_greedy": "Joint greedy", "st_ucb": "Joint UCB"}
    order = ["Static", "IID TS", "Last value", "EWMA", "AR greedy", "Joint greedy", "Joint UCB"]
    for ax, panel in zip(axes, table.panel.unique()):
        s = table[(table.panel == panel) & (table.budget == 5)].copy()
        s["name"] = s.policy.map(names); s = s.dropna(subset=["name"]).set_index("name").reindex(order)
        ax.barh(np.arange(len(order)), s.ratio_to_iid_ts, color=[COLORS[5],COLORS[5],COLORS[2],COLORS[2],COLORS[0],COLORS[0],COLORS[1]])
        ax.axvline(1, color="gray", ls="--"); ax.set_title(panel.replace(" chronological", ""))
        ax.set_xlabel("Mean loss / IID TS loss")
    axes[0].set_yticks(range(len(order)), order); axes[0].invert_yaxis()
    fig.suptitle("Five selections per day: improvements depend on panel and comparator", y=1.01)
    fig.tight_layout(); figure(fig, "02_real_panel_baselines")


def certificates():
    c = read("experiments/today_2026_10_10/results/certificates_confirmation/summary.csv")
    d = read("experiments/oct10_evening/results/certificates_real/runs.csv")
    assert len(d) == 4800 and d.groupby(["noise", "learner", "policy", "k"]).size().eq(100).all()
    rows = []
    for keys, g in d.groupby(["noise", "learner", "policy", "k"]):
        k, n = int(g.any_violation.sum()), len(g); z = norm.ppf(.975); den=1+z*z/n
        mid=(k/n+z*z/(2*n))/den; half=z*np.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/den
        rows.append(dict(zip(["noise", "learner", "policy", "budget"], keys),
                         worlds=n, violations=k, failure_rate=k/n, ci_low=min(k/n,max(0.,mid-half)), ci_high=max(k/n,min(1.,mid+half)),
                         mean_regret=g["regret@730"].mean(), active_arms=g.active_at_end.mean(),
                         best_eliminated=int(g.best_eliminated.eq(True).sum())))
    s=pd.DataFrame(rows); output("real_dynamics_certificates", s)
    widths=read("experiments/oct10_evening/results/certificates_real/widths.csv")
    fig, axes=plt.subplots(1,3,figsize=(13,4.5))
    order=["known","fitted","fitted_inflated","wrong_order_or_diagonal"]
    g=c.set_index("mode").loc[order]
    axes[0].bar(range(4), g.failure_rate, color=[COLORS[0],COLORS[2],COLORS[5],COLORS[3]])
    axes[0].errorbar(range(4),g.failure_rate,yerr=[g.failure_rate-g.ci_low,g.ci_high-g.failure_rate],fmt="none",color="black",capsize=3)
    axes[0].set_xticks(range(4),["Known","Fitted","Q × 1.5","AR1 +\ndiagonal"],rotation=25)
    axes[0].axhline(.05,ls="--",color="gray");axes[0].set_ylabel("Fraction of worlds with any violation")
    axes[0].set_title("A. AR(20) joint coverage audit")
    g=s[(s.noise=="gauss") & (s.policy=="sp") & (s.budget==5)].set_index("learner").loc[["known","fitted","fitted_ar1","iid"]]
    axes[1].bar(range(4),g.failure_rate,color=[COLORS[0],COLORS[2],COLORS[5],COLORS[3]])
    axes[1].errorbar(range(4),g.failure_rate,yerr=[g.failure_rate-g.ci_low,g.ci_high-g.failure_rate],fmt="none",color="black",capsize=3)
    axes[1].set_xticks(range(4),["Known","Fitted","Fitted AR1","IID"],rotation=25)
    axes[1].axhline(.05,ls="--",color="gray");axes[1].set_title("B. Wikipedia-derived upper bounds")
    for col,label,color in [("plugin_B1pp","B1″ plug-in",COLORS[3]),("ellipsoid","Joint ellipsoid",COLORS[0]),("pointwise_2sd","Pointwise ±2 sd",COLORS[2])]:
        axes[2].plot(widths.day,widths[col],"o-",label=label,color=color)
    axes[2].axhline(widths.gap_best_to_2nd.iloc[0],color="black",ls=":",label="Best–second gap")
    axes[2].set_ylim(0,2);axes[2].set_xlabel("Day");axes[2].set_ylabel("Mean-interval width, rescaled axis")
    axes[2].set_title("C. Coverage can be too costly to decide");axes[2].legend(fontsize=8)
    fig.tight_layout();figure(fig,"03_coverage_and_usefulness")


def geometry_and_b2():
    g=read("research/alignment_paper/results/geometry/summary.csv")
    output("geometry_summary",g)
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,graph in zip(axes,["path","clique"]):
        for i,policy in enumerate(["ucb","width_pool","width_profile","design"]):
            s=g[(g.graph==graph)&(g.policy==policy)].sort_values("m")
            ax.errorbar(s.m,s.mean_regret,yerr=s.ci95_halfwidth,fmt="o-",label=policy,color=COLORS[i],capsize=3)
        ax.set_xscale("log",base=2);ax.set_xticks([16,64,256],["16","64","256"])
        ax.set_title(graph.title()+", identical resistance diameter");ax.set_xlabel("Component size");ax.set_ylabel("Cumulative mean regret at T=20,000")
    axes[1].legend(fontsize=9);fig.tight_layout();figure(fig,"04_resistance_geometry")
    b=read("experiments/oct10_runs/results/theory_instances/b2_runs.csv")
    s=b[b.batch==25].groupby(["phi","policy"]).agg(failure=("best_eliminated","mean"),regret=("regret@20000","mean")).reset_index()
    output("b2_false_elimination",s)
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for policy, h in s.groupby("policy"):
        color=COLORS[3] if "iid" in policy else COLORS[0]
        axes[0].plot(h.phi,h.failure,"o-",label=policy,color=color)
        axes[1].plot(h.phi,h.regret,"o-",label=policy,color=color)
    axes[0].set_ylabel("Best arm eliminated, fraction of worlds");axes[1].set_ylabel("Mean regret at T=20,000")
    for ax in axes:ax.set_xlabel("AR(1) persistence");ax.legend(fontsize=9)
    axes[0].set_title("Irreversible failures under bursty exposure");axes[1].set_title("Validity does not imply lower finite-horizon loss")
    fig.tight_layout();figure(fig,"05_false_elimination_tradeoff")


def slate():
    b=read("experiments/oct10_runs/results/theory_instances/b3_contrast.csv")
    output("slate_contrasts",b)
    mc=read("experiments/today_2026_10_10/results/slate/summary.csv")
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    selected=b[(b.n==365)&(b.design=="simultaneous")]
    for i,(case,g) in enumerate(selected.groupby("case",sort=False)):
        axes[0].plot(g.rho,g.ratio_to_rho0,"o-",label=case.replace("_"," "),color=COLORS[i])
    axes[0].set_xlabel("Innovation correlation ρ");axes[0].set_ylabel("Contrast variance / variance at ρ=0")
    axes[0].set_title("A. The 1−ρ factor requires matched arms");axes[0].legend(fontsize=8)
    for phi,g in mc.groupby("phi"):
        axes[1].scatter(g.exact_finite_variance,g.empirical_contrast_variance,label=f"φ={phi}, 20,000 worlds",s=45)
    lim=max(mc.exact_finite_variance.max(),mc.empirical_contrast_variance.max())*1.05
    axes[1].plot([0,lim],[0,lim],ls="--",color="gray");axes[1].set_xlabel("Exact finite-sample contrast variance")
    axes[1].set_ylabel("Monte Carlo variance");axes[1].set_title("B. Independent numerical check");axes[1].legend(fontsize=8)
    fig.tight_layout();figure(fig,"06_slate_information")


def obd():
    d=read("experiments/oct10_runs/results/obd_pooling/runs.csv")
    s=d.groupby(["campaign","policy","graph","width"]).agg(regret=("regret","mean"),se=("regret","sem"),worlds=("seed","size"),best_share=("best_share_last_10pct","mean")).reset_index()
    for campaign,g in s.groupby("campaign"):
        baseline=g[g.policy=="klucb_ell"].regret.iloc[0]
        s.loc[g.index,"ratio_to_matched_klucb"]=g.regret/baseline
    output("obd_semisynthetic",s)
    cal=read("experiments/overnight_2026_10_10/results/obd_calibration/calibration.csv")
    rank=read("experiments/overnight_2026_10_10/results/obd_calibration/ranking_uncertainty.csv")
    output("obd_calibration",cal);output("obd_ranking_uncertainty",rank)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    policies=[("klucb","-","-","Standard KL-UCB"),("ts","-","-","Beta TS"),("eb_ts","-","-","Graph-free EB TS"),
              ("sp_klucb","attr","oracle","Oracle pooling, attr"),("sp_klucb","audience","prefix","Prefix pooling, audience")]
    for i,campaign in enumerate(["all","women"]):
        g=s[s.campaign==campaign].set_index(["policy","graph","width"])
        vals=[g.loc[(p,gr,w),"ratio_to_matched_klucb"] for p,gr,w,label in policies]
        axes[0].bar(np.arange(len(policies))+(i-.5)*.34,vals,width=.34,color=COLORS[i],label=campaign)
    axes[0].axhline(1,color="gray",ls="--");axes[0].set_xticks(range(len(policies)),[x[3] for x in policies],rotation=30,ha="right")
    axes[0].set_ylabel("Mean click regret / matched fixed-level KL-UCB");axes[0].set_title("A. Simulated feedback on estimated OBD rates");axes[0].legend()
    q=cal[(cal.prefix_days==3)&(cal.position=="pooled")&(cal.graph=="audience")]
    for i,campaign in enumerate(["all","women"]):
        g=q[q.campaign==campaign].set_index("width")
        vals=[g.loc[x,"posterior_all_components_covered_probability"] for x in ["raw_prefix","simultaneous_binomial"]]
        axes[1].bar(np.arange(2)+(i-.5)*.34,vals,width=.34,color=COLORS[i],label=campaign)
    axes[1].set_ylim(0,1.05);axes[1].set_xticks([0,1],["Raw prefix ranges","Exact binomial ranges"])
    axes[1].set_ylabel("Posterior probability all held-out ranges fit")
    axes[1].set_title("B. Prefix calibration misses uncertainty and drift")
    axes[1].text(.02,.97,"Conditional rate-posterior sensitivity;\nno future-drift coverage guarantee",transform=axes[1].transAxes,va="top",fontsize=9)
    fig.tight_layout();figure(fig,"07_obd_pooling_and_calibration")


def objectives_and_control():
    d=read("research/spatiotemporal_bandits/results/policies_ar20/summary.csv")
    t=d[d.horizon==1000].copy()
    excluded={"known_mean_greedy","mean_oracle","past_state_genie","state_oracle"}
    assert len(t.policy.unique()) == 18 and excluded.issubset(set(t.policy))
    learn=t[~t.policy.isin(excluded)]
    winners=[]
    for config,g in learn.groupby("config"):
        for metric,maximize in [("oracle_regret_per_round",False),("mean_pseudo_regret_per_round",False),("correct_selection",True)]:
            row=g.loc[g[metric].idxmax() if maximize else g[metric].idxmin()]
            winners.append({"configuration":config,"objective":metric,"observed_leader":row.policy,"value":row[metric],
                            "ci_low":row[metric+"_ci_low"],"ci_high":row[metric+"_ci_high"],"worlds":32,
                            "scope":"pointwise observed leader, not an optimality or pairwise significance claim"})
    output("ar20_objective_leaders",pd.DataFrame(winners))
    output("ar20_terminal_summary",t)
    preferred=["iid_ucb","ar_state_ucb","joint_mean_ucb","joint_state_ucb","joint_predictive_ucb","joint_lucb"]
    actual=[p for p in preferred if p in t.policy.unique()]
    if len(actual)<4:
        actual=list(learn.policy.unique())[:6]
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    config="persistent"
    h=learn[(learn.config==config)&learn.policy.isin(actual)].set_index("policy").reindex(actual)
    for ax,metric,title in [(axes[0],"oracle_regret_per_round","Current-field oracle regret"),(axes[1],"correct_selection","Correct selection of permanent best")]:
        ax.bar(range(len(h)),h[metric],color=COLORS)
        ax.errorbar(range(len(h)),h[metric],yerr=[h[metric]-h[metric+"_ci_low"],h[metric+"_ci_high"]-h[metric]],fmt="none",capsize=3,color="black")
        ax.set_xticks(range(len(h)),[x.replace("_"," ") for x in h.index],rotation=35,ha="right",fontsize=8)
        ax.set_title(title)
    axes[0].set_ylabel("Loss per decision, lower is better");axes[1].set_ylabel("PCS, higher is better");axes[1].set_ylim(0,1)
    fig.suptitle("Fixed-mean AR(20): objective-specific conclusions ("+config+")",y=1.02)
    fig.tight_layout();figure(fig,"08_objective_tradeoffs")
    a=read("research/predictive_ar1/results/summary.csv")
    output("known_mean_ar1_control",a)
    h=a[a.case.str.startswith("homogeneous_")].copy()
    h["phi"]=h.case.str.removeprefix("homogeneous_").astype(float)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for i,policy in enumerate(["greedy","ts","ps","two_step"]):
        g=h[h.policy==policy].sort_values("phi")
        axes[0].errorbar(g.phi,g.coefficient,yerr=g.ci95_halfwidth,fmt="o-",label=policy,color=COLORS[i],capsize=2)
    floor=h[h.policy=="ps"].sort_values("phi")
    axes[0].plot(floor.phi,floor.full_past_lower_bound,"k--",label="Full-past innovation floor")
    axes[0].set_xlabel("Persistence φ");axes[0].set_ylabel("Current-state oracle regret per round")
    axes[0].set_title("A. Known means: the policy leader changes");axes[0].legend(fontsize=8)
    names=["fixed","greedy","ts","ps","two_step","past_state_genie"]
    q=a[a.case=="fast_noise_decoy"].set_index("policy").reindex(names)
    axes[1].bar(range(len(q)),q.coefficient,color=[COLORS[5],COLORS[0],COLORS[1],COLORS[2],COLORS[3],COLORS[4]])
    axes[1].errorbar(range(len(q)),q.coefficient,yerr=q.ci95_halfwidth,fmt="none",color="black",capsize=3)
    axes[1].set_xticks(range(len(q)),[x.replace("_"," ") for x in names],rotation=30,ha="right",fontsize=9)
    axes[1].set_ylabel("Current-state oracle regret per round");axes[1].set_title("B. High-variance white-noise decoy")
    fig.tight_layout();figure(fig,"09_predictive_control")


def residual_audit():
    path="experiments/oct10_evening/code/certificates_real.py"
    spec=importlib.util.spec_from_file_location("report_certificate_calibration",ROOT/path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    c=mod.calibrate();shift=c["E"].mean(0)/(1-c["coef"].sum());actual=c["mu"]+shift
    audit={"empirical_innovation_mean_max_abs":float(np.max(abs(c["E"].mean(0)))),
           "stationary_level_offset_max_abs":float(np.max(abs(shift))),
           "best_to_second_gap":float(np.diff(np.sort(c["mu"])[-2:])[0]),
           "ar_radius":float(np.max(abs(np.linalg.eigvals(mod.companion(c["coef"],1))))),
           "best_article_unchanged":bool(np.argmax(actual)==np.argmax(c["mu"])),
           "top5_members_changed":int(len(set(np.argsort(actual)[-5:])-set(np.argsort(c["mu"])[-5:]))),
           "top10_members_changed":int(len(set(np.argsort(actual)[-10:])-set(np.argsort(c["mu"])[-10:]))),
           "components":int(c["labels"].max()+1),
           "oracle_widths_invalid_for_shifted_levels":int(sum(np.ptp(actual[c["labels"]==j])>np.ptp(c["mu"][c["labels"]==j])+1e-12 for j in np.unique(c["labels"]))),
           "scope":"Empirical residual resampling is not recentered in source code; Gaussian worlds are centered."}
    (OUT/"residual_centering_audit.json").write_text(json.dumps(audit,indent=2)+"\n")
    SOURCES[path]=sha(ROOT/path)


def main():
    OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    inv=inventory()
    comp=overnight();real_panels();certificates();geometry_and_b2();slate();obd();objectives_and_control();residual_audit()
    for path in ["research/correlated_arms/README.md","research/gpt_sol_10_09/sections/synthesis.tex",
                 "research/alignment_paper/README.md","experiments/oct10_evening/README.md"]:
        SOURCES[path]=sha(ROOT/path)
    (OUT/"source_manifest.json").write_text(json.dumps({"report_date":"2026-10-11","generated_utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":SOURCES,"catalogued_artifacts":len(inv),"frozen_copies":int(inv.frozen_copy.sum()),
        "exact_duplicate_artifacts":int(inv.exact_duplicate_of.ne("").sum()),"analysis":"existing results only; no new simulation runs"},indent=2)+"\n")
    checks={"overnight_users":120,"overnight_subsets_per_policy_user":3,
            "overnight_unique_main_runs":10440,"overnight_unique_usercal_runs":1440,
            "real_dynamics_worlds_per_cell":100,"real_dynamics_runs":4800,
            "ratio_intervals_finite":bool(np.isfinite(comp[["ratio_of_means","ci_low","ci_high"]]).all().all()),
            "figures":len(list(FIG.glob("*.png"))),"inventory_artifacts":len(inv)}
    assert checks["ratio_intervals_finite"]
    (OUT/"validation.json").write_text(json.dumps(checks,indent=2)+"\n")
    print(json.dumps(checks),flush=True)


if __name__=="__main__":main()
