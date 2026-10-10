# Executed experiment: selective monitoring of Wikipedia attention

This protocol describes the experiment actually run on 9 October 2026. The earlier twelve-panel clickstream proposal under `www/` remains a larger future study. This execution uses historical hyperlinks and two small fixed panels.

## Decision problem and data

A monitor selects an attention opportunity before seeing that day's statistics. Selecting article i yields utility `log(1 + human page views_i,t)` and reveals that article's statistic for updating future predictions. Unselected articles remain hidden from the learner. Public page-view queries are inexpensive: selective masking emulates a budget for a more costly downstream inspection. The study does not demonstrate production cost savings or the effect of promoting articles.

Two 24-article panels, astronomy and football, are fixed in [frozen_panels.json](data/wikipedia/frozen_panels.json) before downloading test values. All 48 series contain every day from 1 January 2024 to 30 June 2025. No missing value is replaced with zero. Data come from the Wikimedia per-article API, English Wikipedia, all access modes, human `user` traffic.

For each article, fetch the final revision on or before 31 December 2023. Extract direct links to other panel articles and symmetrize binary adjacency. Current redirects and links are not used. The original graphs contain 134 astronomy edges and 189 football edges, with no isolates. A degree-preserving null completes 1,340 swaps in astronomy and 474 in football; the constrained dense football graph does not reach its target swap count. These nulls are controls, not uniformly sampled independent graph draws.

## Model and development

Physical means are fixed unknown quantities. Arm deviations use a common fitted AR coefficient vector with arm-specific innovation scales and correlated innovations. The common vector is a computational simplification; the theoretical model in the paper permits heterogeneous coefficients and orders.

1. Fit on the first 274 days of 2024; use the remaining 92 for development.
2. Apply the common log1p transform, with no per-arm standardization. Fit arm-specific weekday effects using training observations.
3. Fit pooled ridge AR(7), retaining lags 1, 2, and 7, with ridge coefficient 10. Dense AR(20) is secondary.
4. Select covariance shrinkage by Gaussian residual score on development data. Select practical UCB scales from 0.5, 1, and 2 using selectively observed development regret. Thompson scale is fixed at one.
5. Refit on all 366 days of 2024 after settings are selected. Test values never choose parameters.

Covariance families include diagonal innovations, a historical graph resolvent plus common factor, the rewired counterpart, and graph-free common-factor/empirical shrinkage. Full grids and selected values are in [metadata.json](results/wikipedia/metadata.json). Two graph-free variants share an overlapping target family and select identical final fits; they are not independent corroborating controls. Mean graph regularization is omitted to isolate innovation dependence.

All final AR fits are stable without coefficient rescaling. The diffuse static-mean belief uses covariance 100I and mean zero; it is a working inference device, rather than a random physical mean population. Observation variance 1e-8 provides numerical regularization; no sensor noise is added to the recorded field.

## Observation budget and policies

Every method receives the full 2024 history, costing 8,784 historical observations per panel. The 181-day 2025 test proceeds continuously. Daily batch sizes are one and five, giving 181 and 905 test readings. Each distinct batch is chosen before any current feedback and is followed by a joint observation update. There is no full-panel test refresh.

The main policies are static fit-history ranking, stale last value, round robin, iid UCB/TS, 30-calendar-day sliding-window UCB, temporal-only greedy/predictive UCB/predictive TS, joint greedy, joint full-state UCB/TS, joint predictive UCB/TS, and predictive TS under rewired and graph-free covariance models. The window baseline uses only selectively observed values in the last 30 calendar rows; arms without observations receive the documented historical fallback and high uncertainty. All UCB choices use training-only scales. Random seeds are shared across matched policies, retaining joint cross-arm Gaussian draws.

Predictive policies use `Sigma_current - Q_innovation`, retaining uncertainty in permanent means and past states while removing fresh unpredictable innovations. They are one-step policies, rather than optimal Bellman control or the full future-information Predictive Sampling algorithm.

AR(7) stochastic policies use ten seeds; deterministic policies run once. AR(20) uses matched temporal-only/joint predictive UCB and TS, with three TS seeds. There are 352 completed runs and 63,712 daily action records.

## Endpoints and uncertainty

The observed full-field oracle selects the best b articles each day. Primary reported loss is its summed log-view utility minus selected utility, divided by bT. All arm values are potential utilities unaffected by the monitor, so selective masking supplies counterfactual evaluation for this exogenous field. Raw views captured, oracle raw-view loss, selected-batch overlap, runtime, and peak memory are secondary endpoints.

Stochastic-seed Student-t intervals and paired intervals measure Monte Carlo uncertainty conditional on one realized panel. Thirty-day blocks describe temporal variation without treating them as independent trajectories. There is no population significance claim. Permanent-mean PCS and the theoretical innovation floor are unidentifiable from these real data; the controlled simulation studies retain those endpoints.

## Compute and results

Use one BLAS thread and exact Gaussian covariance filtering. AR(7) has 192 augmented coordinates and AR(20) has 504. The full experiment, including fitting, development, historical initialization, both budgets and sensitivities, took 197.9 seconds and 166.8 MB peak RSS on the laptop. Acquisition, analysis plotting and paper compilation are separate costs.

The [findings](results/wikipedia/findings.md) report all main policy rows and limitations. Five-reading joint predictive UCB improves on its temporal-only match, while static ranking is strong for one-reading decisions. Temporal-only greedy wins the football five-reading comparison. Real and rewired graphs perform almost identically. These outcomes support further covariance and temporal research, while supplying no established topology advantage on these panels.
