# Consolidated experiment analysis, 11 October 2026

This is an analysis of existing results, not a new experiment. It covers the
experiment folders and numerical theory studies whose results remain under
`research/`. Frozen evidence copies and derived paper analyses are catalogued
but are not counted as independent replications. The overnight expansion is
complete, including the per-user calibration phase.

Primary summary convention: ratios of mean losses, with uncertainty at the
appropriate replication level. Setting A v2 averages three subsets within each
held-out user, then bootstraps 120 users (2,000 draws). We also preserve the mean
of paired instance ratios, because the original tables use that different
estimand. The report explains why they disagree. Real KuaiRec intervals resample
three windows and then panels, and remain descriptive with so few windows.
Wikipedia date-block sensitivities condition on the same two historical panels.
Controlled simulations use independent paired worlds and pointwise intervals.
All reported comparisons are exploratory unless they were predefined in the
source experiment; there is no simultaneous multiplicity correction.

Mean pseudo-regret, current-field oracle loss, PCS, opportunity loss, coverage,
and graph smoothness are treated as distinct objectives. No population-wide
average is formed across their units. Known-model, oracle-width, estimated-model,
real-panel, semi-synthetic and actual logged-feedback studies are kept distinct.

`code/analyze.py` writes a source inventory, checks table integrity, recomputes
selected user-level and panel-level comparisons, and generates standalone PNG
and PDF figures. `report.md` gives the scientific interpretation and claim map;
`results/` contains the quantitative appendices and fingerprints.

Run from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=experiments/report_2026_10_11/.mplconfig .venv/bin/python -I experiments/report_2026_10_11/code/analyze.py
```
