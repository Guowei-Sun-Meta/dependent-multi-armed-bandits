# Overnight experiment follow-through

Status: **complete**. Updated 2026-10-11T07:04:01.036270+00:00.

Priority overnight experiment: **Setting A v2, 120 users × 3 subsets**,
300 videos and 20,000 pulls, followed by per-user calibrated certificates.

Logged completed instances: 720 / 720 across both phases.
Completed CSV phases: main, usercal.

The existing five-worker run writes to `../oct10_evening/results/setting_a2/`.
This monitor copies completed raw CSVs to `results/setting_a2/` and produces
user-level paired intervals and tail tables automatically. Progress log:
`results/active_run.log`; machine-readable status: `results/status.json`.

Completed required batch: [real-dynamics certificates](results/batch_review/certificates.md)
and [chronological KuaiRec comparison](../oct10_evening/results/daily_chrono/tables.md).

OBD calibration sensitivity: `results/obd_calibration/tables.md`.

When a phase finishes, its report appears at `results/setting_a2/tables.md`.
See [design.md](design.md) for replication, scope and reproduction.
