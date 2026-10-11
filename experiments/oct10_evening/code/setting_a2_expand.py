"""Experiment 7: Setting A v2 at 120 test users x 3 video subsets, written to this folder.

Usage (from the repo root; needs data/kuairec_cache from kuairec/code/data.py and graphs.py --k 10):
    OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/oct10_evening/code/setting_a2_expand.py --jobs 5

Runs kuairec/code/setting_a2.py unchanged (all policies, then the per-user calibrated
certificates) with its RESULTS redirected to results/setting_a2/. Instances are seeded by
(user, subset), so the first 30 users x 2 subsets reproduce the committed v2 runs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "kuairec" / "code"))
import setting_a2  # noqa: E402

OUT = HERE.parent / "results" / "setting_a2"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=120)
    ap.add_argument("--subsets", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=5)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    setting_a2.RESULTS = OUT
    setting_a2.main(a.users, a.subsets, 300, 20000, 10, a.jobs, "_120x3")
    setting_a2.main(a.users, a.subsets, 300, 20000, 10, a.jobs, "_120x3_usercal", user_cal=True)
