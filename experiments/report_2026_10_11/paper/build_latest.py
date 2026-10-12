"""Generate manuscript tables from the completed October 10--11 result snapshots."""
from pathlib import Path
import hashlib
import json
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/report_2026_10_11/results"
MANIFEST = {}


def read(relative):
    path = ROOT / relative
    MANIFEST[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return pd.read_csv(path)


def esc(text):
    return str(text).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


def table(name, headers, rows, caption):
    lines = [r"\begin{table}[htbp]\centering\small", r"\resizebox{\linewidth}{!}{%",
             r"\begin{tabular}{l" + "r" * (len(headers)-1) + "}", r"\toprule",
             " & ".join(esc(x) for x in headers) + r" \\", r"\midrule"]
    lines += [" & ".join(esc(x) for x in row) + r" \\" for row in rows]
    lines += [r"\bottomrule", r"\end{tabular}}", r"\caption{" + caption + "}",
              r"\label{tab:latest-" + name + "}", r"\end{table}", ""]
    (HERE / (name + ".tex")).write_text("\n".join(lines))


def main():
    d = read("experiments/report_2026_10_11/results/overnight_comparisons.csv")
    c = read("experiments/report_2026_10_11/results/overnight_certificates.csv")
    rows = []
    policies = [("shrink_ts", "complete", "10.0", "Graph-free shrinkage TS"),
                ("spectral_ts", "I-mf", "10.0", "Spectral TS, real I-mf"),
                ("spectral_ts", "I-mf~rewired", "10.0", "Spectral TS, rewired I-mf"),
                ("sp_klucb", "I-mf", "oracle", "SP-KLUCB, oracle"),
                ("sp_klucb", "I-mf", "energy", "SP-KLUCB, energy"),
                ("sp_klucb", "I-mf", "cal90", "SP-KLUCB, global 90%"),
                ("sp_klucb", "I-mf", "cal50", "SP-KLUCB, global 50%"),
                ("sp_klucb", "I-mf", "user90", "SP-KLUCB, user 90%"),
                ("sp_klucb", "I-mf", "user75", "SP-KLUCB, user 75%"),
                ("sp_klucb", "I-mf", "none", "SP-KLUCB, zero width")]
    for policy, graph, param, label in policies:
        sub = d[(d.policy == policy) & (d.graph == graph) & (d.param == param)].set_index("reference")
        ts, kl = sub.loc["ts/-/-"], sub.loc["klucb/-/ell"]
        cv = c[(c.graph == graph) & (c.certificate == param)]
        valid = f"{100*cv.valid_component_fraction.iloc[0]:.1f}%" if len(cv) else "--"
        rows.append([label, f"{ts.ratio_of_means:.3f}", f"[{ts.ci_low:.3f}, {ts.ci_high:.3f}]",
                     f"{kl.ratio_of_means:.3f}", f"{kl.mean_instance_ratio:.3f}", valid])
    table("pooling", ["Policy", "Mean loss / TS", "95% user interval", "Mean loss / fixed KL", "Mean paired ratio / fixed KL", "Valid components"], rows,
          "Completed Setting A v2: 120 held-out users, three subsets each, 300 videos, $T=20{,}000$. "
          "Ratios of mean losses differ from means of instance ratios. Intervals bootstrap users after averaging subsets. "
          "User-calibration validity is evaluated at the true user level, not the realized noisy warm-up; it is diagnostic, not a simultaneous certificate guarantee.")
    d = read("experiments/report_2026_10_11/results/real_panel_baselines.csv")
    rows = []
    for p, label in [("ts_iid", "IID TS"), ("static", "Static"), ("last_value", "Last value"),
                     ("ewma", "EWMA"), ("ar_greedy", "Temporal greedy"), ("st_greedy", "Joint greedy"),
                     ("ar_ucb", "Temporal UCB"), ("st_ucb", "Joint UCB"),
                     ("st_ucb_rewired", "Joint UCB, rewired"), ("st_ucb_nograph", "Joint UCB, common factor")]:
        q=d[(d.panel=="KuaiRec chronological") & (d.policy==p)].set_index("budget")
        rows.append([label, f"{q.loc[1,'loss']:.4f}", f"{q.loc[1,'ratio_to_iid_ts']:.3f}",
                     f"{q.loc[5,'loss']:.4f}", f"{q.loc[5,'ratio_to_iid_ts']:.3f}"])
    table("daily", ["Policy", "Loss, k=1", "/ IID TS", "Loss, k=5", "/ IID TS"], rows,
          "Chronological KuaiRec: observed-oracle logit completion-rate loss per day per selected slot. "
          "Five panels in each of three disjoint 11-day windows; policy seeds are averaged within each panel-window. "
          "Unavailable selections receive the specified retrospective median fallback for scoring and no feedback.")
    rows=[]
    for p,label in [("iid_ts","IID TS"),("static","Static"),("ewma","EWMA"),("ar_greedy","Temporal greedy"),("st_ucb","Joint UCB")]:
        q=d[(d.budget==5)&(d.policy==p)].set_index("panel")
        rows.append([label,f"{q.loc['Wikipedia astronomy','loss']:.4f}",f"{q.loc['Wikipedia football','loss']:.4f}"])
    table("wikipedia", ["Policy", "Astronomy", "Football"], rows,
          "Full-year Wikipedia extension: mean observed-oracle $\log(1+\mathrm{views})$ loss per selected slot, "
          "$k=5$, 365 test days in 2025. Each 24-article panel receives the same 8,784 historical readings in 2024. "
          "These are the same historical panels as the earlier half-year study, not independent platform replications.")
    d=read("experiments/today_2026_10_10/results/certificates_confirmation/summary.csv")
    rows=[]
    for p,label in [("known","Known model"),("fitted","Fitted AR(20)"),("fitted_inflated","Fitted, Q times 1.5"),("wrong_order_or_diagonal","AR(1), diagonal shocks")]:
        r=d[d['mode']==p].iloc[0]
        rows.append([label,f"{int(r.failures)}/100",f"[{r.ci_low:.3f}, {r.ci_high:.3f}]",f"{r.mean_final_max_width:.2f}"])
    table("coverage", ["Learner", "Anytime failures", "95% Wilson interval", "Final maximum width"], rows,
          "Fresh AR(20) confirmation after screening: six arms, 800 rounds, burst length 25, an independent 365-round fitting prefix, "
          "100 paired worlds. The last row bundles wrong lag order and diagonalized innovations. Covariance inflation is an empirical heuristic.")
    d=read("experiments/report_2026_10_11/results/real_dynamics_certificates.csv")
    rows=[]
    for p,label in [("known","Known AR(7)"),("fitted","Fitted AR(7)"),("fitted_ar1","Fitted AR(1)"),("iid","IID confidence")]:
        q=d[(d.noise=="gauss")&(d.policy=="sp")&(d.learner==p)].set_index("budget")
        rows.append([label,f"{int(q.loc[5,'violations'])}/100",f"{q.loc[5,'mean_regret']:.1f}",
                     f"{int(q.loc[10,'violations'])}/100",f"{q.loc[10,'mean_regret']:.1f}"])
    table("realcert", ["SP-UCB confidence", "Violations, k=5", "Mean regret, k=5", "Violations, k=10", "Mean regret, k=10"], rows,
          "Centered Gaussian worlds calibrated to 30 Wikipedia articles: 730 days, 100 worlds per cell, oracle community widths. "
          "Violations check arm/component upper bounds; mean regret sums slate gaps over the horizon. "
          "Low empirical violation rates do not establish a fitted-model theorem.")
    d=read("experiments/report_2026_10_11/results/obd_semisynthetic.csv")
    rows=[]
    policies=[("klucb","-","-","Standard log-t KL-UCB"),("ts","-","-","Beta TS"),("eb_ts","-","-","Graph-free empirical-Bayes TS"),
              ("sp_klucb","attr","oracle","Oracle pooling, attributes"),("sp_klucb","audience","oracle","Oracle pooling, audience"),
              ("sp_klucb","attr","prefix","Prefix pooling, attributes"),("sp_klucb","audience","prefix","Prefix pooling, audience")]
    for p,g,w,label in policies:
        q=d[(d.policy==p)&(d.graph==g)&(d.width==w)].set_index("campaign")
        rows.append([label,f"{q.loc['all','ratio_to_matched_klucb']:.3f}",f"{q.loc['women','ratio_to_matched_klucb']:.3f}"])
    table("obd", ["Policy", "All: ratio to fixed KL-UCB", "Women: ratio to fixed KL-UCB"], rows,
          "OBD semi-synthetic study: day 4--7 estimated click rates treated as fixed means; components and priors from days 1--3; "
          "two million simulated impressions in batches of 100, 20 seeds. Attribute metadata have retrospective provenance. "
          "The conservative fixed-confidence KL-UCB comparator is distinct from standard log-t KL-UCB.")
    d=read("experiments/report_2026_10_11/results/slate_contrasts.csv")
    rows=[]
    for p,label in [("equal","Equal variances, phi=0.9"),("unequal_sd","Unequal standard deviations 1, 2"),
                     ("hetero_phi","Persistence 0.9 and 0.5"),("equal_iid","Equal, iid")]:
        q=d[(d['case']==p)&(d.n==365)&(d.rho==.9)].set_index("design")
        rows.append([label,f"{q.loc['simultaneous','ratio_to_rho0']:.3f}",f"{q.loc['staggered','ratio_to_rho0']:.3f}"])
    table("slates", ["Pair", "Simultaneous variance ratio", "Staggered variance ratio"], rows,
          "Contrast variance relative to zero innovation correlation, 365 observations per arm, innovation correlation 0.9. "
          "The ideal equal-pair factor is 0.1; heterogeneous pairs and staggered schedules require their own conditional covariance. "
          "The staggered design uses a different calendar length; its ratios do not establish equal-budget policy dominance.")
    (HERE/"source_manifest.json").write_text(json.dumps({"manuscript_update_date":"2026-10-12","experiment_snapshot":"2026-10-10 through 2026-10-11", "sources_sha256":MANIFEST},indent=2)+"\n")
    print(f"Generated 7 tables from {len(MANIFEST)} source tables.")


if __name__=="__main__":main()
