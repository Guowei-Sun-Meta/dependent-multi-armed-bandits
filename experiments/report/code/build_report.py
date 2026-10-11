"""Cross-experiment analyses and figures for the experiment report (experiments/report/README.md).

Usage (from the repo root):
    .venv/bin/python -I experiments/report/code/build_report.py

Every number the report derives across experiments is computed here from the raw run files:
1. dose_response.csv   - certified pooling: share of rejectable components vs regret ratio
                         (Setting A v2 at 360 instances; OBD semi-synthetic). Tests A1 / A4.
2. real_vs_rewired.csv - paired real-graph vs rewired-graph contrasts on every platform with
                         both (shrinkage vs structure).
3. validity.csv        - certificate violation rates, iid vs innovation (B1/B1''), across the
                         toy, the robustness sweep, the real-calibrated worlds and the parallel
                         AR(20) confirmation. Tests B1 validity and B2.
4. inflation.csv       - Wikipedia block-mean inflation, observed vs predicted (B2, B3 part 1).
5. dynamics.csv        - regret relative to iid TS on the chronological KuaiRec panel (S5, P1).
Ratios of means use a user (or seed) bootstrap; shares use Wilson intervals.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

EXP = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "results"
FIG = Path(__file__).resolve().parents[1] / "figures"
RNG = np.random.default_rng(20261011)
B = 2000

# Reference palette (dataviz skill, light mode): categorical slots 1-3 and text/grid tokens.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def style(ax, xlabel, ylabel, title):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel, color=INK2, fontsize=10)
    ax.set_ylabel(ylabel, color=INK2, fontsize=10)
    ax.figure.suptitle(title, x=0.012, ha="left", color=INK, fontsize=11)


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(c - h, 0.0), min(c + h, 1.0)


def boot_ratio(num, den, groups):
    """Ratio of means sum(num)/sum(den) with a bootstrap over groups (users or seeds)."""
    df = pd.DataFrame({"n": num, "d": den, "g": groups}).groupby("g").sum()
    est = df.n.sum() / df.d.sum()
    idx = RNG.integers(len(df), size=(B, len(df)))
    n, d = df.n.to_numpy()[idx].sum(1), df.d.to_numpy()[idx].sum(1)
    lo, hi = np.quantile(n / d, [0.025, 0.975])
    return est, lo, hi


# ---------------------------------------------------------------- 1. dose response (A1, A4)


def dose_response():
    d = EXP / "oct10_evening" / "results" / "setting_a2"
    runs = pd.read_csv(d / "setting_a2_runs_120x3.csv")
    inst = pd.read_csv(d / "setting_a2_instances_120x3.csv")
    col = "regret@20000"
    base = runs[(runs.policy == "klucb") & (runs.param.astype(str) == "ell")].set_index(["user", "rep"])[col]
    ts = runs[runs.policy == "ts"].set_index(["user", "rep"])[col]
    rows, per_inst = [], []
    for g in ("I-mf", "I-coeng", "I-tag", "I-mf~rewired"):
        for cert in ("oracle", "energy", "cal90", "cal50", "none"):
            r = runs[(runs.policy == "sp_klucb") & (runs.graph == g) & (runs.param.astype(str) == cert)].set_index(["user", "rep"])[col]
            i = inst[inst.graph == g].set_index(["user", "rep"])
            j = pd.DataFrame({"r": r, "b": base.reindex(r.index), "t": ts.reindex(r.index),
                              "rej": i[f"rejectable_{cert}"].reindex(r.index),
                              "valid": i[f"valid_{cert}"].reindex(r.index)}).dropna()
            users = j.index.get_level_values("user")
            est, lo, hi = boot_ratio(j.r.to_numpy(), j.b.to_numpy(), users)
            est_ts, lo_ts, hi_ts = boot_ratio(j.r.to_numpy(), j.t.to_numpy(), users)
            ratio_i = j.r / j.b
            rows.append({"platform": "KuaiRec Setting A v2", "graph": g, "certificate": cert,
                         "instances": len(j), "rejectable_share": j.rej.mean(), "valid_share": j.valid.mean(),
                         "ratio_of_means_vs_klucb_ell": est, "ci_low": lo, "ci_high": hi,
                         "mean_of_ratios_vs_klucb_ell": ratio_i.mean(), "p90_ratio_vs_klucb_ell": ratio_i.quantile(.9),
                         "ratio_of_means_vs_ts": est_ts, "ts_ci_low": lo_ts, "ts_ci_high": hi_ts})
            if cert == "oracle":
                per_inst.append(pd.DataFrame({"graph": g, "rejectable": j.rej, "ratio": ratio_i}))
    # OBD semi-synthetic: rejectable components (oracle) vs oracle ratio to klucb_ell, paired by seed.
    o = EXP / "oct10_runs" / "results" / "obd_pooling"
    orun, oinst = pd.read_csv(o / "runs.csv"), pd.read_csv(o / "instance.csv")
    for (camp, g), h in orun[orun.policy == "sp_klucb"].groupby(["campaign", "graph"]):
        b = orun[(orun.campaign == camp) & (orun.policy == "klucb_ell")].set_index("seed")["regret@2000000"]
        ii = oinst[(oinst.campaign == camp) & (oinst.graph == g)].iloc[0]
        n_sub = ii.components - 1
        for cert in ("oracle", "prefix", "none"):
            r = h[h.width == cert].set_index("seed")["regret@2000000"]
            est, lo, hi = boot_ratio(r.to_numpy(), b.reindex(r.index).to_numpy(), r.index.to_numpy())
            rows.append({"platform": f"OBD ({camp})", "graph": g, "certificate": cert, "instances": len(r),
                         "rejectable_share": (ii.components_rejectable_oracle / n_sub) if cert == "oracle" else np.nan,
                         "valid_share": 1.0 if cert == "oracle" else (ii.prefix_covers_oracle_share if cert == "prefix" else 0.0),
                         "ratio_of_means_vs_klucb_ell": est, "ci_low": lo, "ci_high": hi,
                         "mean_of_ratios_vs_klucb_ell": (r / b.reindex(r.index)).mean(),
                         "p90_ratio_vs_klucb_ell": (r / b.reindex(r.index)).quantile(.9)})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "dose_response.csv", index=False)
    pi = pd.concat(per_inst)
    rho = pi[["rejectable", "ratio"]].rank().corr().iloc[0, 1]
    kk = df[(df.platform == "KuaiRec Setting A v2") & (df.certificate != "none")]
    rho_agg = kk[["rejectable_share", "ratio_of_means_vs_klucb_ell"]].rank().corr().iloc[0, 1]
    oo = df[df.platform.str.startswith("OBD") & (df.certificate == "oracle")]
    rho_obd = oo[["rejectable_share", "ratio_of_means_vs_klucb_ell"]].rank().corr().iloc[0, 1]
    print(f"Spearman across KuaiRec certificate x graph points (excluding none): {rho_agg:.3f}; OBD oracle points: {rho_obd:.3f}")
    # Binned per-instance relation for the oracle certificate.
    pi["bin"] = pd.cut(pi.rejectable, [0, 0.4, 0.55, 0.7, 0.85, 1.0], include_lowest=True)
    binned = pi.groupby("bin", observed=True).ratio.agg(["count", "median", "mean"]).reset_index()
    binned["bin"] = binned["bin"].astype(str)
    binned.to_csv(OUT / "dose_response_oracle_binned.csv", index=False)

    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    k = df[(df.platform == "KuaiRec Setting A v2") & (df.certificate != "none")]
    ob = df[df.platform.str.startswith("OBD") & (df.certificate == "oracle")]
    for sub, colr, lab in ((k, BLUE, "KuaiRec Setting A v2 (certificate × graph)"), (ob, ORANGE, "OBD, oracle certificate (campaign × graph)")):
        valid = sub.valid_share >= 0.85
        ax.errorbar(sub.rejectable_share, sub.ratio_of_means_vs_klucb_ell,
                    yerr=[sub.ratio_of_means_vs_klucb_ell - sub.ci_low, sub.ci_high - sub.ratio_of_means_vs_klucb_ell],
                    fmt="none", ecolor=colr, elinewidth=1, alpha=0.6)
        ax.scatter(sub.rejectable_share[valid], sub.ratio_of_means_vs_klucb_ell[valid], s=46, color=colr,
                   edgecolor=SURFACE, linewidth=2, label=lab, zorder=3)
        ax.scatter(sub.rejectable_share[~valid], sub.ratio_of_means_vs_klucb_ell[~valid], s=46, facecolor=SURFACE,
                   edgecolor=colr, linewidth=2, zorder=3)
    ax.axhline(1, color=INK2, linewidth=1)
    ax.text(0.02, 1.01, "no gain over KL-UCB", color=INK2, fontsize=8, va="bottom")
    ax.annotate("energy, cal90\n(valid, too wide)", xy=(0.21, 0.962), xytext=(0.22, 0.83), fontsize=8, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.annotate("cal50 (hollow: valid\nfor about half of components)", xy=(0.63, 0.75), xytext=(0.66, 0.92), fontsize=8,
                color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    style(ax, "Share of suboptimal components the certificate can reject", "Regret ÷ KL-UCB (same level), ratio of means",
          "Certified pooling gains in proportion to what it can reject (A1)")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIG / "fig1_dose_response.png")
    plt.close(fig)
    return df, rho, binned


# ---------------------------------------------------------------- 2. real vs rewired


def real_vs_rewired():
    rows = []
    d = EXP / "oct10_evening" / "results" / "setting_a2"
    runs = pd.read_csv(d / "setting_a2_runs_120x3.csv")
    col = "regret@20000"
    for pol, prm, lab in (("sp_klucb", "oracle", "SP-KLUCB, oracle certificate"), ("sp_klucb", "none", "SP-KLUCB, no certificate"),
                          ("spectral_ts", "10.0", "Spectral TS, λ = 10")):
        a = runs[(runs.policy == pol) & (runs.graph == "I-mf") & (runs.param.astype(str) == prm)].set_index(["user", "rep"])[col]
        b = runs[(runs.policy == pol) & (runs.graph == "I-mf~rewired") & (runs.param.astype(str) == prm)].set_index(["user", "rep"])[col]
        j = pd.DataFrame({"a": a, "b": b}).dropna()
        est, lo, hi = boot_ratio(j.a.to_numpy(), j.b.to_numpy(), j.index.get_level_values("user"))
        rows.append({"platform": "KuaiRec Setting A v2 (I-mf, 360 instances)", "policy": lab, "real_over_rewired": est,
                     "ci_low": lo, "ci_high": hi, "units": len(j)})
    o = pd.read_csv(EXP / "oct10_runs" / "results" / "obd_pooling" / "runs.csv")
    for camp in ("all", "women"):
        for pol, w, lab in (("sp_klucb", "oracle", "SP-KLUCB, oracle certificate"), ("sp_klucb", "none", "SP-KLUCB, no certificate"),
                            ("comp_ts", "-", "TS pooled to component mean")):
            a = o[(o.campaign == camp) & (o.policy == pol) & (o.graph == "attr") & (o.width == w)].set_index("seed")["regret@2000000"]
            b = o[(o.campaign == camp) & (o.policy == pol) & (o.graph == "attr~rw") & (o.width == w)].set_index("seed")["regret@2000000"]
            est, lo, hi = boot_ratio(a.to_numpy(), b.reindex(a.index).to_numpy(), a.index.to_numpy())
            rows.append({"platform": f"OBD {camp} (attribute groups, 20 seeds)", "policy": lab, "real_over_rewired": est,
                         "ci_low": lo, "ci_high": hi, "units": len(a)})
    dc = pd.read_csv(EXP / "oct10_evening" / "results" / "daily_chrono" / "test_runs.csv")
    dc["window"] = dc.unit.str.extract(r"_F(\d+)_")[0].astype(int)
    for k in (1, 5):
        u = dc[dc.k == k].groupby(["window", "unit", "policy"]).regret_per_slot_day.mean().unstack()
        a, b = u["st_ucb"], u["st_ucb_rewired"]
        est, lo, hi = boot_ratio(a.to_numpy(), b.to_numpy(), u.index.get_level_values("unit"))
        rows.append({"platform": f"KuaiRec daily, chronological (k = {k}, 15 units)", "policy": "Joint filter, UCB",
                     "real_over_rewired": est, "ci_low": lo, "ci_high": hi, "units": len(u)})
    sb = pd.read_csv(EXP / "kuairec" / "results" / "setting_b_summary.csv")
    sb["param"] = sb["param"].astype(str)
    for pol, prm, lab in (("graph_ts", "10.0", "Gaussian TS pooled over users, λ = 10"), ("sp_klucb_user", "oracle", "SP-KLUCB over user clusters, oracle")):
        a = sb[(sb.policy == pol) & (sb.graph == "U-coeng") & (sb.param == prm)].regret.iloc[0]
        b = sb[(sb.policy == pol) & (sb.graph == "U-coeng~rewired") & (sb.param == prm)].regret.iloc[0]
        rows.append({"platform": "KuaiRec Setting B (U-coeng, 8 instances, no interval)", "policy": lab,
                     "real_over_rewired": a / b, "ci_low": np.nan, "ci_high": np.nan, "units": 8})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "real_vs_rewired.csv", index=False)

    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    labels = [f"{r.platform.split(' (')[0]}{' (k = ' + r.platform.split('k = ')[1][0] + ')' if 'k = ' in r.platform else ''} · {r.policy}"
              for r in df.itertuples()]
    y = np.arange(len(df))[::-1]
    has = df.ci_low.notna()
    ax.hlines(y[has], df.ci_low[has], df.ci_high[has], color=BLUE, linewidth=2)
    ax.scatter(df.real_over_rewired, y, s=40, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.axvline(1, color=INK2, linewidth=1)
    ax.set_xscale("log")
    ax.set_xticks([0.5, 0.75, 1, 1.5, 2, 3])
    ax.set_xticklabels(["0.5", "0.75", "1", "1.5", "2", "3"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.5)
    style(ax, "Real ÷ rewired regret (95% interval, log scale)", "",
          "Real graphs rarely beat rewired nulls; uncertified pooling on real groups can be far worse")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIG / "fig2_real_vs_rewired.png")
    plt.close(fig)
    return df


# ---------------------------------------------------------------- 3. validity (B1, B2)


def validity():
    rows = []

    def add(setting, cert, s, note=""):
        k, n = int(s.sum()), int(s.count())
        lo, hi = wilson(k, n)
        rows.append({"setting": setting, "certificate": cert, "violated": k, "runs": n, "rate": k / n if n else np.nan,
                     "ci_low": lo, "ci_high": hi, "note": note})

    p = pd.read_csv(EXP / "simulations" / "certificates_under_persistence" / "results" / "coverage_runs_plugin.csv")
    p = p[p.policy.str.startswith("sp_")]
    for b, lab in ((1, "Toy, one at a time"), (25, "Toy, bursty (blocks of 25)")):
        for phi in (0.9, 0.97):
            s = p[(p.batch == b) & (p.phi == phi)]
            add(f"{lab}, φ = {phi}", "iid", s[s.policy == "sp_ucb_iid"].any_violation)
            add(f"{lab}, φ = {phi}", "innovation (B1′/B1″, known)", s[s.policy.isin(["sp_ucb_st1", "sp_ucb_st2"])].any_violation)
    r = pd.read_csv(EXP / "oct10_runs" / "results" / "robustness" / "runs.csv")
    r = r[(r.batch == 25) & r.policy.str.startswith("sp_")]
    for phi in (0.9, 0.97):
        s = r[r.phi == phi]
        add(f"Robustness sweep, bursty, φ = {phi}", "iid", s[(s.policy == "sp_ucb_iid") & (s.condition == "known")].any_violation)
        for cond, lab in (("known", "innovation, known"), ("fit365", "innovation, fitted (365-round prefix)"),
                          ("fit100", "innovation, fitted (100-round prefix)"), ("fit100_cons", "innovation, fitted 100 + 2 SE")):
            add(f"Robustness sweep, bursty, φ = {phi}", lab, s[(s.policy == "sp_ucb_st2") & (s.condition == cond)].any_violation)
    s = r[r.condition == "ar7_as_ar1"]
    add("Robustness sweep, bursty, AR(7) truth", "iid", s[s.policy == "sp_ucb_iid"].any_violation)
    add("Robustness sweep, bursty, AR(7) truth", "innovation, AR(1) fitted (wrong order)", s[s.policy == "sp_ucb_st2"].any_violation)
    c = pd.read_csv(EXP / "oct10_evening" / "results" / "certificates_real" / "runs.csv")
    c = c[(c.noise == "resample") & (c.policy == "sp")]
    for k in (5, 10):
        s = c[c.k == k]
        add(f"Wikipedia-calibrated AR(7), k = {k}", "iid", s[s.learner == "iid"].any_violation)
        add(f"Wikipedia-calibrated AR(7), k = {k}", "innovation, known", s[s.learner == "known"].any_violation)
        add(f"Wikipedia-calibrated AR(7), k = {k}", "innovation, fitted AR(7)", s[s.learner == "fitted"].any_violation)
        add(f"Wikipedia-calibrated AR(7), k = {k}", "innovation, fitted AR(1)", s[s.learner == "fitted_ar1"].any_violation)
    t = pd.read_csv(EXP / "today_2026_10_10" / "results" / "certificates_confirmation" / "runs.csv")
    for mode, lab in (("known", "innovation, known"), ("fitted", "innovation, fitted"),
                      ("fitted_inflated", "innovation, fitted, Q × 1.5"), ("wrong_order_or_diagonal", "innovation, wrong order")):
        add("Parallel run: dense AR(20), bursty", lab, t[t["mode"] == mode].any_violation.astype(bool), "today_2026_10_10")
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "validity.csv", index=False)

    keep = [("Toy, bursty (blocks of 25), φ = 0.97", "Toy, bursty, φ = 0.97"),
            ("Robustness sweep, bursty, φ = 0.97", "Fitted dynamics sweep, φ = 0.97"),
            ("Robustness sweep, bursty, AR(7) truth", "Weekly-lag truth"),
            ("Wikipedia-calibrated AR(7), k = 5", "Wikipedia-calibrated, k = 5"),
            ("Wikipedia-calibrated AR(7), k = 10", "Wikipedia-calibrated, k = 10")]
    fig, ax = plt.subplots(figsize=(8.2, 4.4), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    y = np.arange(len(keep))[::-1] * 1.0
    for off, cert_pick, colr, lab in ((0.18, lambda d: d[d.certificate == "iid"], ORANGE, "iid certificate"),
                                      (-0.18, lambda d: d[d.certificate.str.startswith("innovation") & ~d.certificate.str.contains("100")
                                                          & ~d.certificate.str.contains("AR\\(1\\)") & ~d.certificate.str.contains("AR\\(7\\)")
                                                          | (d.certificate == "innovation, AR(1) fitted (wrong order)")],
                                       BLUE, "innovation certificate (known or long-prefix fit; wrong order where truth is AR(7))")):
        vals, los, his = [], [], []
        for setting, _ in keep:
            sub = cert_pick(df[df.setting == setting])
            if "AR(7) truth" in setting and lab.startswith("innovation"):
                sub = df[(df.setting == setting) & (df.certificate == "innovation, AR(1) fitted (wrong order)")]
            elif lab.startswith("innovation"):
                sub = sub[sub.certificate.isin(["innovation (B1′/B1″, known)", "innovation, fitted (365-round prefix)", "innovation, known"])].head(1) \
                    if setting != "Robustness sweep, bursty, φ = 0.97" else df[(df.setting == setting) & (df.certificate == "innovation, fitted (365-round prefix)")]
            row = sub.iloc[0]
            vals.append(row.rate)
            los.append(row.rate - row.ci_low)
            his.append(row.ci_high - row.rate)
        ax.barh(y + off, vals, height=0.32, color=colr, label=lab, xerr=[los, his],
                error_kw=dict(ecolor=INK2, elinewidth=1, capsize=0))
        for yi, v in zip(y + off, vals):
            if v == 0:
                ax.text(0.075, yi, "0 violations", va="center", fontsize=7.5, color=INK2)
    ax.axvline(0.05, color=INK2, linewidth=1)
    ax.text(0.055, y[-1] - 0.5, "nominal δ = 0.05", fontsize=8, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([b for _, b in keep], fontsize=8.5)
    ax.set_xlim(0, 1.02)
    style(ax, "Share of runs with any certificate violation (95% Wilson interval)", "",
          "iid certificates fail under persistence; innovation certificates hold (B1, B2)")
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.16), ncol=1)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIG / "fig3_validity.png")
    plt.close(fig)
    return df


# ---------------------------------------------------------------- 4. inflation (B2, B3)


def inflation():
    d = pd.read_csv(EXP / "oct10_runs" / "results" / "inflation" / "per_article.csv")
    s = d[(d.variant == "weekday") & (d.b.isin([7, 28]))]
    summ = s.groupby(["panel", "b"]).agg(
        observed=("observed", "median"), pred_ar1=("pred_ar1", "median"), pred_ar20=("pred_ar20", "median"),
        log_err_ar1=("observed", lambda x: 0), articles=("observed", "size")).reset_index()
    for p in ("ar1", "ar20"):
        s = s.assign(**{f"lr_{p}": np.log(s.observed / s[f"pred_{p}"])})
    cal = s.groupby(["panel", "b"]).agg(median_obs_over_ar1=("lr_ar1", lambda x: float(np.exp(x.median()))),
                                        median_obs_over_ar20=("lr_ar20", lambda x: float(np.exp(x.median()))),
                                        share_under_ar20=("lr_ar20", lambda x: float((x > 0).mean()))).reset_index()
    summ = summ.drop(columns="log_err_ar1").merge(cal, on=["panel", "b"])
    summ.to_csv(OUT / "inflation.csv", index=False)

    s7 = s[s.b == 7]
    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    ax.scatter(s7.pred_ar1, s7.observed, s=14, color=ORANGE, alpha=0.55, edgecolor="none", label="AR(1) shortcut from lag-1 ρ")
    ax.scatter(s7.pred_ar20, s7.observed, s=14, color=BLUE, alpha=0.55, edgecolor="none", label="AR(20) fitted on 2022–2023")
    lim = [1, float(np.ceil(max(s7.observed.max(), s7.pred_ar20.max(), s7.pred_ar1.max())))]
    ax.plot(lim, lim, color=INK2, linewidth=1)
    ax.text(6.3, 6.6, "observed = predicted", fontsize=8, color=INK2, rotation=35)
    ax.axhline(1, color=GRID, linewidth=1)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    style(ax, "Predicted inflation of a 7-day block mean (from the 2022–23 fit)", "Observed inflation, 2024–25",
          "Real attention is in B2's regime; full-ACF fits predict it")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIG / "fig4_inflation.png")
    plt.close(fig)
    return summ


# ---------------------------------------------------------------- 5. certificate widths (B1 power)


def widths():
    w = pd.read_csv(EXP / "oct10_evening" / "results" / "certificates_real" / "widths.csv")
    r = w[w.day == 730].iloc[0]
    fig, ax = plt.subplots(figsize=(7.6, 3.2), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    names = ["Pointwise ±2 posterior sd\n(not anytime-valid)", "Log-det ellipsoid (B1)", "Scalar plug-in (B1″)"]
    vals = [r.pointwise_2sd, r.ellipsoid, r.plugin_B1pp]
    y = np.arange(3)[::-1]
    ax.barh(y, vals, height=0.45, color=BLUE)
    for yi, v in zip(y, vals):
        ax.text(v + 0.02, yi, f"{v:.2f}", va="center", fontsize=9, color=INK)
    ax.axvline(r.gap_best_to_2nd, color=ORANGE, linewidth=2)
    ax.text(r.gap_best_to_2nd + 0.02, y[1] + 0.42, f"best-to-2nd gap {r.gap_best_to_2nd:.3f}", fontsize=8, color=INK2)
    ax.axvline(1.0, color=INK2, linewidth=1)
    ax.text(1.02, y[0] + 0.05, "whole range\nof means", fontsize=8, color=INK2, va="center")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8.5)
    style(ax, "Median arm interval width after 730 days (means lie in [0, 1])", "",
          "Real-calibrated dynamics: the information is there, the valid bounds are not")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIG / "fig5_widths.png")
    plt.close(fig)
    return w


# ---------------------------------------------------------------- 6. dynamics (S5, P1)


def dynamics():
    dc = pd.read_csv(EXP / "oct10_evening" / "results" / "daily_chrono" / "test_runs.csv")
    u = dc.groupby(["k", "unit", "policy"]).regret_per_slot_day.mean().unstack()
    rows = []
    for k, g in u.groupby(level="k"):
        for pol in g.columns:
            est, lo, hi = boot_ratio(g[pol].to_numpy(), g["ts_iid"].to_numpy(), g.index.get_level_values("unit"))
            rows.append({"k": k, "policy": pol, "ratio_to_iid_ts": est, "ci_low": lo, "ci_high": hi})
    df = pd.DataFrame(rows).sort_values(["k", "ratio_to_iid_ts"])
    df.to_csv(OUT / "dynamics_kuairec_chrono.csv", index=False)
    return df


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 220)
    dr, rho, binned = dose_response()
    print("== dose response ==")
    print(dr.round(3).to_string())
    print(f"Spearman(rejectable share, oracle ratio) per instance: {rho:.3f}")
    print(binned.round(3).to_string())
    print("== real vs rewired ==")
    print(real_vs_rewired().round(3).to_string())
    print("== validity ==")
    print(validity().round(3).to_string())
    print("== inflation ==")
    print(inflation().round(3).to_string())
    widths()
    print("== dynamics ==")
    print(dynamics().round(3).to_string())


if __name__ == "__main__":
    main()
