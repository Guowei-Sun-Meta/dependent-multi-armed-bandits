"""Tables for experiment 7 (Setting A v2 at 120 users x 3 subsets).

Usage (from the repo root):
    .venv/bin/python -I experiments/oct10_evening/code/analyze_a2.py

Runs kuairec/code/analyze_b.summarize_a2 unchanged on this folder's runs (main and per-user
calibration), on the full 360 instances and on the first 30 users x 2 subsets (the committed v2
size), so the effect of the larger sample on tails can be read directly.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "kuairec" / "code"))
import analyze_b  # noqa: E402

OUT = HERE.parent / "results" / "setting_a2"


def table(runs, insts):
    with tempfile.TemporaryDirectory() as tmp:
        runs.to_csv(Path(tmp) / "setting_a2_runs.csv", index=False)
        insts.to_csv(Path(tmp) / "setting_a2_instances.csv", index=False)
        analyze_b.RESULTS = Path(tmp)
        text = analyze_b.summarize_a2()
        summary = pd.read_csv(Path(tmp) / "setting_a2_summary.csv")
    return text, summary


def main():
    parts = ["# Setting A v2 at 120 users x 3 subsets", ""]
    for tag, label in (("_120x3", "All policies"), ("_120x3_usercal", "Per-user calibrated certificates")):
        r = OUT / f"setting_a2_runs{tag}.csv"
        if not r.exists():
            continue
        runs, insts = pd.read_csv(r), pd.read_csv(OUT / f"setting_a2_instances{tag}.csv")
        text, summary = table(runs, insts)
        summary.to_csv(OUT / f"setting_a2_summary{tag}.csv", index=False)
        users = sorted(runs.user.unique())[:30]
        small = (runs.user.isin(users)) & (runs.rep < 2)
        small_i = (insts.user.isin(users)) & (insts.rep < 2)
        text30, _ = table(runs[small].copy(), insts[small_i].copy())
        parts += [f"## {label}: 360 instances", "", text, "", f"## {label}: first 30 users x 2 subsets (committed v2 size)",
                  "", text30, ""]
    (OUT / "tables.md").write_text("\n".join(parts))
    print("\n".join(parts))


if __name__ == "__main__":
    main()
