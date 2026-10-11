# 10 October evening runs: experiments 1, 2, 3b and 7

These follow [oct10_runs](../oct10_runs/README.md), from [experiment_plan.md](../experiment_plan.md). The KuaiRec raw data was downloaded from Zenodo record 18164998 and the caches were rebuilt. The rebuilt graph metadata matches the committed `graphs_meta_k10.json` exactly.

| Plan # | What | Script | Results | Status |
| --- | --- | --- | --- | --- |
| 1 + 2 | KuaiRec daily slot, chronological protocol, with standard baselines | `code/daily_chrono.py`, `code/analyze_daily.py` | `results/daily_chrono/` | Done |
| 3b | Certified pooling in worlds calibrated to Wikipedia attention | `code/certificates_real.py`, `code/analyze_certs.py` | `results/certificates_real/` | Done |
| 7 | Setting A v2 at 120 users × 3 subsets | `code/setting_a2_expand.py`, `code/analyze_a2.py` | `results/setting_a2/` | **Running overnight** (about 6 h, then the per-user calibration pass) |

Experiment 1 covers KuaiRec only. The Wikipedia half needs the article lists re-selected chronologically and links taken from dated revisions; the parallel run in [today_2026_10_10](../today_2026_10_10/README.md) did part of that.

## Headlines

1. **The look-ahead fix does not remove the dynamics gain on KuaiRec; it grows.**
   - Under the chronological protocol (prefix-only graph, prefix eligibility, availability not known in advance), the joint filter cuts regret relative to iid Thompson sampling (TS) by 49% at 1 video/day and 54% at 5/day. Both intervals exclude zero.
   - The retrospective run reported 24–44%.
2. **"Modelling or forgetting?" Mostly forgetting.**
   - The joint filter does **not** beat the simplest persistence rule, each video's last observed value: +3% at k = 1 (interval −13% to +43%) and +7% at k = 5 (−10% to +61%), both inconclusive.
   - At k = 1, EWMA ties the filter.
   - Discounted TS and sliding-window UCB are worse than the filter.
   - On this panel, the paper should say "persistence pays, and the simplest persistence rule captures it", not "modelling the dynamics pays".
3. **The graph helps through correlated shocks, not through the specific topology.**
   - At k = 5, adding the graph to the temporal filter cuts regret by 11% (interval −20% to −5%).
   - The prefix graph is indistinguishable from its rewiring (−1.4%, −6.6% to +3.5%) and from a common factor alone (−3.5%, −6.8% to +1.0%).
   - At k = 1 nothing graph-related is distinguishable.
4. **On real-calibrated dynamics, iid certificates fail and valid ones never decide (3b).**
   - With Wikipedia-fitted AR(7) dynamics and real resampled shocks, the iid certificate is violated in 47–56% of runs at k = 5 and 94–99% at k = 10.
   - The innovation certificates (known, re-fitted, even AR(1)-fitted) violate in 0–1%. But in 730 days they eliminate nothing, and SP-UCB's regret is about 10 times the iid rule's.
   - The cause is not missing information. After 2 years the posterior sd of each mean is 0.018 (pointwise ±2 sd width 0.07, against a best-to-second gap of 0.135).
   - The anytime-valid constructions inflate it: the log-determinant ellipsoid by β ≈ 20 (width 0.70), and B1″ more (1.74).
   - **A tighter anytime-valid certificate is the binding problem for the paper's bridge, not more data.**

## 1 + 2. KuaiRec daily slot, chronological protocol (`results/daily_chrono/`)

**Protocol** (details in the script docstring):
- **Graph and eligibility.** I-coeng is rebuilt at each cutoff from big-matrix rows dated before the first test day. Eligible videos had at least 10 plays on every fit day.
- **Units.** Test windows are days 31–41, 42–52 and 53–63. There are 5 predefined panels of 49–50 videos per window, giving 15 units, with 5 seeds averaged within each unit.
- **Tuning.** Done on days 20–30 (fit on 1–19), then frozen.
- **Availability.** It is not known in advance. 17 test cells are unavailable. Policies chose an unavailable video 201 times, in 71 of 1,950 runs.
- **Intervals.** A two-level bootstrap: resample windows, then panels within each window.

Regret per slot per day (logit complete-play rate), relative to iid TS:

| Policy | k = 1 | k = 5 |
| --- | --- | --- |
| Joint filter, greedy (st_greedy) | 0.47 | 0.44 |
| EWMA (tuned half-life 1 / 7 days) | 0.49 | 0.73 |
| Last value | 0.49 | **0.43** |
| Temporal-only filter, greedy | 0.50 | 0.46 |
| Joint filter, UCB (st_ucb) | 0.51 | 0.46 |
| Same, rewired prefix graph | 0.50 | 0.47 |
| Same, common factor only | 0.50 | 0.48 |
| Temporal-only filter, UCB | 0.51 | 0.52 |
| Sliding-window UCB | 0.61 | 0.74 |
| Discounted TS | 0.77 | 0.90 |
| iid TS | 1 | 1 |
| Seasonal naive (same weekday) | 1.00 | 1.01 |
| Static (fit-window mean) | 1.01 | 1.06 |

Paired contrasts, with 95% intervals:

| Contrast | k = 1 | k = 5 |
| --- | --- | --- |
| Joint filter vs iid TS | −49% (−86% to −14%) | −54% (−67% to −43%) |
| Joint filter vs last value | +3% (−13% to +43%) | +7% (−10% to +61%) |
| Graph vs temporal-only (UCB) | −1% (−6% to +4%) | **−11% (−20% to −5%)** |
| Real vs rewired prefix graph | +1% (−17% to +9%) | −1% (−7% to +4%) |
| Graph vs common factor only | +1% (−5% to +6%) | −3% (−7% to +1%) |
| Joint filter vs EWMA | +4% (−10% to +42%) | −37% (−52% to −17%)* |

\* At k = 5, the development window picked a 7-day EWMA half-life that generalized poorly. Last value, the zero half-life limit, matches the filter. So the "filter beats EWMA" result at k = 5 is a tuning artefact, not evidence for modelling.

**Other observations**
- Regret is much higher in the first test window (days 31–41) for every policy. The interval widths reflect that.
- The big matrix has no rows at all dated 11–26 August 2020 (a gap in the KuaiRec log). So the prefix graphs at origins 41 and 52 are built from the same rows, and origin 41's graph is already 5 days stale.

## 3b. Certified pooling in Wikipedia-calibrated worlds (`results/certificates_real/`)

**Setup**
- **Arms.** 30 articles, 5 per community of the six-community panel, with the community as the component. Oracle component widths.
- **Dynamics.** AR(7) and innovation covariance fitted on 2022–2023 (sum of AR coefficients 0.92, weekly lag 0.18). Rewards rescaled so the means lie in [0, 1].
- **Shocks**, three kinds:
  - resampled real residual vectors, independent over time (the main worlds);
  - Gaussian;
  - weekly blocks of real residuals (stress).
- **Runs.** 730 days, slates of 5 or 10 articles, 100 worlds per cell.
- **New code.** The general-AR innovation regression, `InnovationAR`. It matches `coverage.InnovationRegression` exactly at p = 1, and the generalized B1″ bound matches `coverage.plugin_bounds`.

| Shocks | Policy | k | iid violation | Innovation violation (known / fitted AR(7) / fitted AR(1)) | iid regret | Innovation regret (known) |
| --- | --- | --- | --- | --- | --- | --- |
| Resampled | SP-UCB | 5 | 56% | 0% / 0% / 0% | 37 | 466 |
| Resampled | SP-UCB | 10 | 95% | 0% / 0% / 0% | 47 | 455 |
| Resampled | Elimination | 5 | 80% | 0% / 0% / 0% | 177 | 1,079 (round-robin) |
| Resampled | Elimination | 10 | 98% | 0% / 0% / 0% | 289 | 1,600 (round-robin) |
| Weekly blocks | SP-UCB | 5 | 47% | 1% / 0% / 1% | 36 | 459 |
| Gaussian | SP-UCB | 10 | 94% | 0% / 0% / 0% | 45 | 467 |

- The iid-certified elimination never dropped the best article here (0/100 in every cell), unlike the bursty toy. The best article leads by 0.135, which survives the iid certificate's under-coverage.
- The iid violations mean its intervals are wrong. They did not cost decisions in this world.

**Median arm interval width with the true model** (random 5-article slates):

| Day | B1″ plug-in | Ellipsoid (β ≈ 20) | Pointwise ±2 sd |
| --- | --- | --- | --- |
| 365 | 1.79 | 0.93 | 0.096 |
| 730 | 1.74 | 0.70 | 0.070 |

## 7. Setting A v2 at 120 users × 3 subsets (`results/setting_a2/`)

Running overnight on 5 workers, at about 200–240 s per instance. When it finishes, `code/analyze_a2.py` writes `results/setting_a2/tables.md`, covering the full 360 instances and the committed 30 × 2 subset.

## What this changes

- **Abstract wording, Q4 (dynamics):** on KuaiRec, "persistence-aware policies cut regret by about half against iid bandits, and most of the gain comes from using recent observations". Claim modelling gains only where a filter beats last value or EWMA. Check whether that happens on the chronological Wikipedia panels.
- **Q1/Q4 graph claim:** "shocks are correlated, so joint filtering helps at larger budgets", not "the item graph's topology helps".
- **Q3 (bridge):**
  - iid certificates are invalid on real-calibrated dynamics.
  - Innovation certificates are valid, even with fitted dynamics, but too wide to act on within 2 years.
  - The method gap is the anytime/simultaneous inflation (β ≈ 20 against about 2 pointwise). A tighter certificate, for example per-arm stitched bounds after whitening, is the most valuable method work before the deadline. Without it, the bridge is a negative result plus a safety argument.

## Reproduce

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
# KuaiRec raw data into data/kuairec_raw/ (KuaiRec.zip unzipped, plus the three CSVs of Zenodo 18164998)
.venv/bin/python -I experiments/kuairec/code/data.py && .venv/bin/python -I experiments/kuairec/code/graphs.py --k 10
.venv/bin/python -I experiments/oct10_evening/code/daily_chrono.py --jobs 3        # 2 min
.venv/bin/python -I experiments/oct10_evening/code/analyze_daily.py
.venv/bin/python -I experiments/oct10_evening/code/certificates_real.py --verify
.venv/bin/python -I experiments/oct10_evening/code/certificates_real.py --seeds 100 --jobs 3   # ~15 min
.venv/bin/python -I experiments/oct10_evening/code/analyze_certs.py
.venv/bin/python -I experiments/oct10_evening/code/setting_a2_expand.py --jobs 5   # ~7 h
.venv/bin/python -I experiments/oct10_evening/code/analyze_a2.py
```
