# Overnight follow-through, 10 October 2026

The required evening batch already produced 4,800 real-dynamics certificate runs and
the chronological KuaiRec daily comparison in `../oct10_evening/results/`.
The active overnight experiment is experiment 7 of `../experiment_plan.md`:
Setting A v2, 120 held-out users × 3 subsets, 300 videos and 20,000 pulls per instance.
Its existing launcher runs five workers, first all policies, then the per-user
calibrated certificates. Do not start a duplicate copy.

This folder adds automatic progress tracking and analysis to that existing run.
The monitor reads the log and completed CSVs, copies the completed raw outputs
here with SHA-256 hashes, and produces comparison and certificate tables.
It never modifies the active experiment's code or results.

Replication is by held-out user. The three video subsets are averaged within each
user before uncertainty intervals and tail summaries are computed. Each policy is
compared separately with Bernoulli TS, standard log-t KL-UCB and fixed-confidence
KL-UCB. Paired bootstrap intervals resample users (2,000 draws). Tail summaries
report the 90th percentile of the per-user regret ratio and the share above 2×.
The quantile certificates are empirical calibration rules, not proven per-user
confidence guarantees. The user-calibration instance diagnostics use the true
user level and must be labelled as diagnostic; the policy uses a paid warm-up.

The monitor snapshots the latest log every 30 seconds and analyzes each phase
after its output CSVs are complete. It waits at most 12 hours. A failure or timeout
is recorded explicitly. The original launcher writes results at phase completion;
the progress count refers to logged completed instances, not saved per-instance
CSV checkpoints. Status is in `results/status.json`, current report in `README.md`.

The OBD calibration audit in this folder is a lightweight follow-up, not a new
bandit benchmark. It compares prefix component ranges with simultaneous exact
binomial intervals and with held-out rate posterior draws across chronological
splits. Prefix binomial coverage concerns stationary prefix rates; it provides no
guarantee under subsequent drift. Attribute metadata have retrospective provenance.

Reproduce the lightweight analyses from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -I experiments/overnight_2026_10_10/code/obd_calibration.py
.venv/bin/python -I experiments/overnight_2026_10_10/code/follow_through.py
```

The active monitor is the same script with `--monitor --hours 12`. Its PID is in
`results/monitor.pid`. The overnight experiment's existing launcher is
`../oct10_evening/code/setting_a2_expand.py`; do not launch another copy while it
is active. An idle-sleep assertion is attached to its existing PID and ends when
that experiment exits. This does not override lid closure or manual sleep.
