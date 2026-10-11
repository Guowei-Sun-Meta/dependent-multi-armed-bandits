"""Report the completed batch and monitor the already-running overnight expansion."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import shutil
import time

import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
OUT = HERE / "results"
EVENING = ROOT / "experiments/oct10_evening/results"
LOG = ROOT / "data/logs/setting_a2_120x3.log"
SOURCE = EVENING / "setting_a2"
PHASES = {
    "main": ("setting_a2_runs_120x3.csv", "setting_a2_instances_120x3.csv"),
    "usercal": ("setting_a2_runs_120x3_usercal.csv", "setting_a2_instances_120x3_usercal.csv"),
}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def wilson(k, n):
    z = norm.ppf(.975)
    mid = (k / n + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(k / n * (1 - k / n) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return float(mid - half), float(mid + half)


def review_batch():
    dest = OUT / "batch_review"
    dest.mkdir(parents=True, exist_ok=True)
    path = EVENING / "certificates_real/runs.csv"
    d = pd.read_csv(path)
    keys = ["noise", "learner", "policy", "k"]
    assert not d.duplicated(keys + ["seed"]).any()
    assert len(d) == 4800 and d.groupby(keys).size().eq(100).all()
    assert np.isfinite(d[["regret@365", "regret@730", "active_at_end"]]).all().all()
    rows = []
    for key, g in d.groupby(keys):
        fails = int(g.any_violation.sum())
        lo, hi = wilson(fails, len(g))
        rows.append(dict(zip(keys, key), worlds=len(g), failures=fails,
                         failure_rate=fails / len(g), ci_low=lo, ci_high=hi,
                         best_eliminated=int(g.best_eliminated.eq(True).sum()),
                         regret=float(g["regret@730"].mean()),
                         active_at_end=float(g.active_at_end.mean())))
    s = pd.DataFrame(rows)
    s.to_csv(dest / "certificate_summary.csv", index=False)
    text = ["# Completed real-dynamics certificate batch", "",
            "4,800 runs; 100 worlds per cell; 30 Wikipedia-derived arms; AR(7); 730 days.", "",
            "Known and fitted innovation bounds have zero recorded violations on Gaussian and",
            "independently resampled main worlds. Zero of 100 gives a 95% Wilson upper bound",
            "of 3.7%, not zero population risk. Independent empirical residual draws need not",
            "satisfy the Gaussian proxy used by the bound; their coverage is empirical evidence.", "",
            "The innovation elimination rule retains all 30 arms. Iid rules have many certificate",
            "violations but lower mean regret here. Report coverage and decision usefulness together.", "",
            "The source violation flag checks upper arm/component bounds only, not lower-bound",
            "coverage or preservation of every top-k arm. Wrong-order AR(1) has few violations in",
            "these conservative worlds; do not generalize the earlier wrong-order failure rate.", "",
            "Pooling widths are oracle widths. The cohort is selected from an existing retrospective",
            "Wikipedia panel. This is a dynamics-calibrated simulation, not new real-data policy evidence.", "",
            s.round(5).to_markdown(index=False), ""]
    (dest / "certificates.md").write_text("\n".join(text))
    save(dest / "sources.json", {"certificate_runs": str(path.relative_to(ROOT)),
                                 "sha256": sha(path), "checked_utc": stamp()})


def analyze_overnight():
    dest = OUT / "setting_a2"
    dest.mkdir(parents=True, exist_ok=True)
    manifest, frames, diagnostics = {}, [], []
    done = []
    for phase, filenames in PHASES.items():
        if not all((SOURCE / f).exists() for f in filenames):
            continue
        run = pd.read_csv(SOURCE / filenames[0])
        inst = pd.read_csv(SOURCE / filenames[1])
        if run.user.nunique() != 120 or run.groupby("user").rep.nunique().ne(3).any():
            raise ValueError(f"{phase}: incomplete users/subsets")
        key = ["user", "rep", "policy", "graph", "param"]
        if run.duplicated(key).any() or not np.isfinite(run["regret@20000"]).all():
            raise ValueError(f"{phase}: duplicate or nonfinite runs")
        if run.groupby(["user", "policy", "graph", "param"]).rep.nunique().ne(3).any():
            raise ValueError(f"{phase}: a policy is missing subsets")
        if inst.user.nunique() != 120 or inst.groupby(["user", "graph"]).rep.nunique().ne(3).any():
            raise ValueError(f"{phase}: incomplete certificate diagnostics")
        for f in filenames:
            shutil.copy2(SOURCE / f, dest / f)
            manifest[f] = {"source": str((SOURCE / f).relative_to(ROOT)), "sha256": sha(dest / f)}
        frames.append(run)
        inst["phase"] = phase
        diagnostics.append(inst)
        done.append(phase)
    if not frames:
        return done
    allruns = pd.concat(frames, ignore_index=True)
    if "main" not in done:
        return done
    allruns["param"] = allruns.param.astype(str)
    U = allruns.groupby(["user", "policy", "graph", "param"])["regret@20000"].mean().unstack(["policy", "graph", "param"])
    rng = np.random.default_rng(20261011)
    ix = rng.integers(len(U), size=(2000, len(U)))
    comparisons = []
    for ref in [("ts", "-", "-"), ("klucb", "-", "logt"), ("klucb", "-", "ell")]:
        b = U[ref].to_numpy()
        assert (b > 0).all()
        for key in U:
            a = U[key].to_numpy()
            assert np.isfinite(a).all()
            samples = a[ix].mean(1) / b[ix].mean(1)
            low, high = np.quantile(samples, [.025, .975])
            ratios = a / b
            comparisons.append(dict(policy=key[0], graph=key[1], param=key[2],
                                    reference="/".join(ref), users=len(U),
                                    mean_regret=float(a.mean()), ratio_of_means=float(a.mean() / b.mean()),
                                    ci_low=float(low), ci_high=float(high),
                                    p90_user_ratio=float(np.quantile(ratios, .9)),
                                    share_users_above_2x=float((ratios > 2).mean())))
    table = pd.DataFrame(comparisons)
    table.to_csv(dest / "comparisons.csv", index=False)
    diag = pd.concat(diagnostics, ignore_index=True)
    drows = []
    for col in diag:
        if col.startswith(("valid_", "rejectable_", "mean_width_")):
            for (phase, graph), g in diag.groupby(["phase", "graph"]):
                if g[col].notna().any():
                    user = g.groupby("user")[col].mean().dropna()
                    drows.append({"phase": phase, "graph": graph, "metric": col,
                                  "mean_over_users": float(user.mean()), "users": len(user)})
    pd.DataFrame(drows).to_csv(dest / "certificates.csv", index=False)
    report = ["# Overnight Setting A v2 expansion", "",
              f"Completed phases: {', '.join(done)}. 120 held-out users × 3 subsets; 300 videos; T=20,000.", "",
              "Subsets are averaged within users. Intervals resample users and are conditional on",
              "the released mean matrix and the shared tuning population; they do not address",
              "uncertainty in the estimated reward means. User-calibration validity diagnostics",
              "evaluate widths at the true user level, while policies use a paid noisy warm-up.", ""]
    for ref, g in table.groupby("reference", sort=False):
        report += [f"## Reference: {ref}", "", g.drop(columns=["reference", "users"]).round(4).to_markdown(index=False), ""]
    (dest / "tables.md").write_text("\n".join(report))
    save(dest / "manifest.json", manifest)
    return done


def write_status(status):
    save(OUT / "status.json", status)
    lines = ["# Overnight experiment follow-through", "",
             f"Status: **{status['status']}**. Updated {status['updated_utc']}.", "",
             "Priority overnight experiment: **Setting A v2, 120 users × 3 subsets**,",
             "300 videos and 20,000 pulls, followed by per-user calibrated certificates.", "",
             f"Logged completed instances: {status['logged_instances_completed']} / 720 across both phases.",
             f"Completed CSV phases: {', '.join(status['completed_phases']) or 'none yet'}.", "",
             "The existing five-worker run writes to `../oct10_evening/results/setting_a2/`.",
             "This monitor copies completed raw CSVs to `results/setting_a2/` and produces",
             "user-level paired intervals and tail tables automatically. Progress log:",
             "`results/active_run.log`; machine-readable status: `results/status.json`.", "",
             "Completed evening studies: [real-dynamics certificates](results/batch_review/certificates.md)",
             "and [chronological KuaiRec comparison](../oct10_evening/results/daily_chrono/tables.md).", "",
             "OBD calibration sensitivity: `results/obd_calibration/tables.md`.", "",
             "When a phase finishes, its report appears at `results/setting_a2/tables.md`.",
             "See [design.md](design.md) for replication, scope and reproduction.", ""]
    if status.get("error"):
        lines += [f"Failure: {status['error']}", ""]
    temp = HERE / "README.md.tmp"
    temp.write_text("\n".join(lines))
    temp.replace(HERE / "README.md")


def monitor(hours):
    review_batch()
    start = time.monotonic()
    analyzed = set()
    while True:
        log = LOG.read_text() if LOG.exists() else ""
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "active_run.log").write_text(log)
        complete = [phase for phase, fs in PHASES.items()
                    if all((SOURCE / f).exists() and time.time() - (SOURCE / f).stat().st_mtime > 2 for f in fs)]
        status = {"updated_utc": stamp(), "status": "running", "completed_phases": complete,
                  "logged_instances_completed": len(re.findall(r"user \d+ rep \d+ done in", log)),
                  "workers": 5, "target_instances_per_phase": 360,
                  "source_log": str(LOG.relative_to(ROOT)), "source_results": str(SOURCE.relative_to(ROOT))}
        try:
            if set(complete) != analyzed:
                analyze_overnight()
                analyzed = set(complete)
        except Exception as e:
            status.update(status="analysis_failed", error=str(e))
        if len(complete) == 2 and status["status"] == "running":
            status["status"] = "complete"
        elif "Traceback (most recent call last)" in log:
            status.update(status="run_failed", error="The source experiment log contains a traceback.")
        elif time.monotonic() - start > hours * 3600:
            status.update(status="monitor_timeout", error="Monitor time limit reached; source job is not stopped.")
        write_status(status)
        print(json.dumps(status), flush=True)
        if status["status"] != "running":
            return
        time.sleep(30)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--monitor", action="store_true")
    ap.add_argument("--hours", type=float, default=12)
    args = ap.parse_args()
    if args.monitor:
        monitor(args.hours)
    else:
        review_batch()
        print("Completed batch report written; available overnight phases:", analyze_overnight())
