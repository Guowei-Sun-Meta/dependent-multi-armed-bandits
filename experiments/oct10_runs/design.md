# 10 October runs: design

These are the experiments from [experiment_plan.md](../experiment_plan.md) that could produce results on 10 October without the KuaiRec raw data. That data is missing from this checkout. Each script's docstring holds the full specification.

| Plan # | Question | Script | Output |
| --- | --- | --- | --- |
| 3a | On real attention data, how much less does a block of consecutive days tell us about a level than iid days would, and does a prefix fit predict it? | `code/inflation.py` | `results/inflation/` |
| 4 | Do innovation certificates stay valid when the dynamics are estimated from a prefix or misspecified? | `code/robustness.py` | `results/robustness/` |
| 6 (B2) | Does the iid certificate's false elimination under bursty persistence cause lasting (linear) regret? | `code/theory_instances.py b2` | `results/theory_instances/b2_runs.csv` |
| 6 (B3) | When does a slate cut contrast variance by (1 − ρ)? | `code/theory_instances.py b3` | `results/theory_instances/b3_*.csv` |
| 8a | Can the Open Bandit Dataset support a mean-channel instance, a fluctuation channel, or both? | `code/obd_feasibility.py` | `results/obd_feasibility/` |
| 8b | Certified pooling on real e-commerce click rates | `code/obd_pooling.py` | `results/obd_pooling/` |

`code/analyze.py` writes `tables.md` in each results folder.

## Choices and deviations from the plan

**3a**
- Wikipedia only. The KuaiRec daily panel needs the raw data, which is not in this checkout.
- The fit uses 2022–2023 and the observation window is 2024–2025.
- The panels are still the retrospectively selected ones, so this is a diagnostic of the dynamics, not policy evidence.

**4**
- **Shared setup.** The world and the B1″ plug-in bound come from `simulations/certificates_under_persistence/code/coverage.py`, unchanged. The observation noise is known to the learner. Before the online phase there is a fully observed prefix of up to 365 rounds, used only by the fitted conditions.
- **Fitting.** A pooled moment fit of AR(1) plus noise, with innovation correlation shrunk 20% toward I.
- **Conservative remedy.** The fitted φ plus 2 jackknife standard errors, computed over arms.
- **Wrong-order truth.** AR(7) with a weekly lag, in place of the plan's AR(20), so the run stays cheap. It has the same role: the learner fits AR(1).
- **Level shift.** Left out. A shifting mean changes the target, so it belongs in a separate non-stationarity test.
- **Sample size.** 30 seeds per cell, T = 5,000, exposure batches 1 and 25.

**6**
- **B2** reuses the coverage world (shuffled arm order, independent shocks), with 100 seeds, T = 20,000, φ ∈ {0, 0.9, 0.97} and batches {1, 10, 25, 100}.
- **B3** is exact: it computes the full covariance of the observed coordinates and checks it by Monte Carlo.

**8b**
- **Truth and components.**
  - True means are the day 4–7 click rates from the uniform-random logs, pooled over positions.
  - Components are built from days 1–3: groups of `item_feature_1` (a retrospective metadata grouping), and audience-profile k-means over `user_feature_0`.
  - The null control permutes the labels.
- **Block form.** Each decision serves 100 impressions. At a click rate of about 0.4%, per-impression decisions would need horizons of millions of rounds in Python.
- **Prefix certificate.** It uses the raw within-component range of the day 1–3 estimates. It is real-data calibrated, and it can under-cover when click rates drift between the two halves.
