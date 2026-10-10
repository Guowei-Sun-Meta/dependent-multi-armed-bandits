"""Read-only feasibility audit for the WWW spatiotemporal experiment design.

Writes new reports under research/st_applications/results/feasibility/; never
changes KuaiRec data, graph caches, or existing experimental results. This is
an exploratory data audit, not a policy comparison or a latent-mean estimate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "research/st_applications/results/feasibility"


def locate(name):
    hits = sorted((ROOT / "data/kuairec_raw").rglob(name))
    if len(hits) != 1:
        raise ValueError(f"Expected one {name}, found {len(hits)}")
    return hits[0]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pooled_ar_diagnostic(values, lags=(1, 2, 7)):
    """Training-only descriptive fit; intentionally not a model selection step."""
    x = values - values.mean(axis=0)
    p = max(lags)
    design = np.stack([x[p-l:len(x)-l] for l in lags], axis=-1)
    target = x[p:]
    a = np.linalg.lstsq(design.reshape(-1, len(lags)), target.ravel(), rcond=None)[0]
    residuals = target - np.einsum("tnl,l->tn", design, a)
    companion = np.zeros((p, p))
    companion[0, np.array(lags)-1] = a
    companion[1:, :-1] = np.eye(p-1)
    rho = np.corrcoef(x[:-1].ravel(), x[1:].ravel())[0, 1]
    return {
        "lags": list(lags), "coefficients": a.tolist(),
        "spectral_radius": float(np.max(np.abs(np.linalg.eigvals(companion)))),
        "pooled_lag1_correlation": float(rho),
        "innovation_time_rows": len(residuals),
        "centered_covariance_rank_upper_bound": min(len(residuals)-1, values.shape[1]),
    }


def audit(output, scan_interactions=True):
    daily_path = locate("item_daily_features.csv")
    cache_path = ROOT / "data/kuairec_cache/eval_matrix.npz"
    d = pd.read_csv(daily_path, usecols=["video_id", "date", "play_cnt", "complete_play_cnt"])
    with np.load(cache_path) as cache:
        videos, users = cache["videos"], cache["users"]
    days = np.sort(d.date.unique())
    duplicates = int(d.duplicated(["video_id", "date"]).sum())
    if duplicates:
        raise ValueError("Duplicate video-day rows require a documented aggregation rule")
    if (d.complete_play_cnt > d.play_cnt).any() or (d.complete_play_cnt < 0).any():
        raise ValueError("Invalid count pairs")
    counts = d.groupby("video_id").date.nunique()
    complete = np.intersect1d(videos, counts[counts == len(days)].index)
    retrospective = d[d.video_id.isin(complete)]
    table = retrospective.pivot(index="date", columns="video_id", values="play_cnt")
    # Count-based smoothing makes zero-play cells finite, but does not make
    # them observed information about completion quality.
    rate = (retrospective.complete_play_cnt + .5) / (retrospective.play_cnt + 1)
    logits = pd.DataFrame({"date": retrospective.date, "video_id": retrospective.video_id,
                           "y": np.log(rate/(1-rate))}).pivot(index="date", columns="video_id", values="y")
    report = {
        "status": "exploratory_feasibility_audit_not_policy_evidence",
        "sources": {"daily": str(daily_path.relative_to(ROOT)),
                    "daily_sha256": sha256(daily_path),
                    "evaluation_ids": str(cache_path.relative_to(ROOT)),
                    "evaluation_ids_sha256": sha256(cache_path)},
        "daily": {"rows": len(d), "videos": int(d.video_id.nunique()), "days": len(days),
                  "first_date": int(days[0]), "last_date": int(days[-1]),
                  "duplicate_video_days": duplicates,
                  "zero_play_video_days": int((d.play_cnt == 0).sum()),
                  "all_videos_complete_by_presence": int((counts == len(days)).sum()),
                  "evaluation_videos_complete_by_presence": len(complete),
                  "retrospective_cohort_zero_play_cells": int((table == 0).sum().sum()),
                  "retrospective_cohort_videos_with_any_zero_play": int((table == 0).any().sum()),
                  "warning": "Complete-by-presence uses future survival; zero plays are unobserved quality."},
        "origins": [],
    }
    for f in (28, 35, 42):
        cutoff = int(days[f-1])
        train = d[(d.date <= cutoff) & d.video_id.isin(videos)]
        grouped = train.groupby("video_id")
        prefix_complete = grouped.date.nunique()
        prefix_min = grouped.play_cnt.min()
        eligible = np.intersect1d(prefix_complete[prefix_complete == f].index,
                                 prefix_min[prefix_min >= 10].index)
        test = d[(d.date > cutoff) & d.video_id.isin(eligible)]
        missing = len(eligible)*(len(days)-f)-len(test)
        report["origins"].append({
            "fit_days": f, "cutoff_date": cutoff, "test_days": len(days)-f,
            "prefix_eligible_eval_videos_min_play_10": len(eligible),
            "eligible_missing_test_video_days": missing,
            "eligible_zero_play_test_video_days": int((test.play_cnt == 0).sum()),
            "retrospective_cohort_training_ar": pooled_ar_diagnostic(logits.iloc[:f].to_numpy()),
            "ar20_innovation_time_rows": f-20,
        })
    if scan_interactions:
        path = locate("big_matrix.csv")
        totals = {str(o["cutoff_date"]): {"rows": 0, "post_cutoff_rows": 0} for o in report["origins"]}
        all_rows, date_min, date_max, bad_dates = 0, np.inf, -np.inf, 0
        for chunk in pd.read_csv(path, usecols=["user_id", "video_id", "date"], chunksize=250000):
            all_rows += len(chunk)
            date_min = min(date_min, chunk.date.min())
            date_max = max(date_max, chunk.date.max())
            bad_dates += int(chunk.date.isna().sum())
            side = chunk[np.isin(chunk.video_id, videos) & ~np.isin(chunk.user_id, users)]
            for cutoff, entry in totals.items():
                entry["rows"] += len(side)
                entry["post_cutoff_rows"] += int((side.date > int(cutoff)).sum())
        for entry in totals.values():
            entry["post_cutoff_fraction"] = entry["post_cutoff_rows"]/max(entry["rows"], 1)
        report["interaction_graph_audit"] = {
            "file": str(path.relative_to(ROOT)), "rows_scanned": all_rows,
            "first_date": int(date_min), "last_date": int(date_max), "missing_dates": bad_dates,
            "cached_item_graph_input_rows_by_cutoff": totals,
            "interpretation": "graphs.py excludes evaluation pairs, but has no time cutoff; rebuild for temporal tests.",
        }
    existing = ROOT / "research/kuairec_graphs/results/daily_runs.csv"
    if existing.exists():
        runs = pd.read_csv(existing)
        means = runs.groupby("policy").regret_per_day.mean()
        report["existing_daily_results"] = {
            "file": str(existing.relative_to(ROOT)), "sha256": sha256(existing),
            "rows": len(runs), "origins": sorted(int(v) for v in runs.origin.unique()),
            "seed_count": int(runs.seed.nunique()),
            "mean_regret_per_day": {k: float(v) for k, v in means.items()},
            "st_greedy_relative_gain_over_ar_greedy": float(1-means.st_greedy/means.ar_greedy),
            "warning": "Overlapping test windows, synthetic noise, and full-period graph; descriptive pilot only.",
        }
    output.mkdir(parents=True, exist_ok=True)
    (output / "kuairec_audit.json").write_text(json.dumps(report, indent=2)+"\n")
    lines = ["# KuaiRec feasibility audit", "", "Exploratory audit; no new policy experiment was run.", "",
             f"The raw table has {len(d):,} video-days, {d.video_id.nunique():,} videos and {len(days)} days.",
             f"The retrospective 253-video cohort has {report['daily']['retrospective_cohort_zero_play_cells']} zero-play cells.",
             "", "| Prefix days | Eligible videos (prefix only, ≥10 plays/day) | Missing test cells | Zero-play test cells | AR(20) innovation days |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for o in report["origins"]:
        lines.append(f"| {o['fit_days']} | {o['prefix_eligible_eval_videos_min_play_10']} | {o['eligible_missing_test_video_days']} | {o['eligible_zero_play_test_video_days']} | {o['ar20_innovation_time_rows']} |")
    if scan_interactions:
        lines += ["", "| Origin cutoff | Item-graph side-input rows after cutoff | Fraction |", "| --- | ---: | ---: |"]
        for cutoff, entry in totals.items():
            lines.append(f"| {cutoff} | {entry['post_cutoff_rows']:,} / {entry['rows']:,} | {entry['post_cutoff_fraction']:.1%} |")
    lines += ["", "Full-period graph caches are unsuitable for chronological policy evidence. The short",
              "panel also cannot establish fixed latent means, PCS, or a fitted theoretical innovation floor.",
              "The JSON records source fingerprints, training-only AR diagnostics and the existing pilot summary.", ""]
    (output / "findings.md").write_text("\n".join(lines))
    print(json.dumps({"report": str(output), "daily": report["daily"], "origins": report["origins"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-interactions", action="store_true", help="Skip streamed timestamp leakage audit")
    args = parser.parse_args()
    audit(args.output, not args.skip_interactions)
