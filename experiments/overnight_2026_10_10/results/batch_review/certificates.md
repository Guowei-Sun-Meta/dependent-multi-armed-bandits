# Completed real-dynamics certificate batch

4,800 runs; 100 worlds per cell; 30 Wikipedia-derived arms; AR(7); 730 days.

Known and fitted innovation bounds have zero recorded violations on Gaussian and
independently resampled main worlds. Zero of 100 gives a 95% Wilson upper bound
of 3.7%, not zero population risk. Independent empirical residual draws need not
satisfy the Gaussian proxy used by the bound; their coverage is empirical evidence.

The innovation elimination rule retains all 30 arms. Iid rules have many certificate
violations but lower mean regret here. Report coverage and decision usefulness together.

The source violation flag checks upper arm/component bounds only, not lower-bound
coverage or preservation of every top-k arm. Wrong-order AR(1) has few violations in
these conservative worlds; do not generalize the earlier wrong-order failure rate.

Pooling widths are oracle widths. The cohort is selected from an existing retrospective
Wikipedia panel. This is a dynamics-calibrated simulation, not new real-data policy evidence.

| noise    | learner    | policy   |   k |   worlds |   failures |   failure_rate |   ci_low |   ci_high |   best_eliminated |    regret |   active_at_end |
|:---------|:-----------|:---------|----:|---------:|-----------:|---------------:|---------:|----------:|------------------:|----------:|----------------:|
| block    | fitted     | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.32   |           30    |
| block    | fitted     | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.23   |           30    |
| block    | fitted     | sp       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  472.553  |           30    |
| block    | fitted     | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  577.746  |           30    |
| block    | fitted_ar1 | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.32   |           30    |
| block    | fitted_ar1 | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.23   |           30    |
| block    | fitted_ar1 | sp       |   5 |      100 |          1 |           0.01 |  0.00177 |   0.05449 |                 0 |  248.073  |           30    |
| block    | fitted_ar1 | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  584.607  |           30    |
| block    | iid        | se       |   5 |      100 |         86 |           0.86 |  0.77863 |   0.91474 |                 0 |  168.479  |            6.13 |
| block    | iid        | se       |  10 |      100 |         98 |           0.98 |  0.92999 |   0.9945  |                 0 |  303.318  |           10.38 |
| block    | iid        | sp       |   5 |      100 |         47 |           0.47 |  0.37511 |   0.56711 |                 0 |   36.2578 |           30    |
| block    | iid        | sp       |  10 |      100 |         98 |           0.98 |  0.92999 |   0.9945  |                 0 |   47.5815 |           30    |
| block    | known      | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.26   |           30    |
| block    | known      | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.17   |           30    |
| block    | known      | sp       |   5 |      100 |          1 |           0.01 |  0.00177 |   0.05449 |                 0 |  458.523  |           30    |
| block    | known      | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  459.557  |           30    |
| gauss    | fitted     | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.32   |           30    |
| gauss    | fitted     | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.23   |           30    |
| gauss    | fitted     | sp       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  459.422  |           30    |
| gauss    | fitted     | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  506.359  |           30    |
| gauss    | fitted_ar1 | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.32   |           30    |
| gauss    | fitted_ar1 | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.23   |           30    |
| gauss    | fitted_ar1 | sp       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  210.554  |           30    |
| gauss    | fitted_ar1 | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  511.076  |           30    |
| gauss    | iid        | se       |   5 |      100 |         78 |           0.78 |  0.6893  |   0.84999 |                 0 |  179.166  |            6.54 |
| gauss    | iid        | se       |  10 |      100 |         99 |           0.99 |  0.94551 |   0.99823 |                 0 |  289.167  |           10.38 |
| gauss    | iid        | sp       |   5 |      100 |         56 |           0.56 |  0.46228 |   0.65328 |                 0 |   37.7841 |           30    |
| gauss    | iid        | sp       |  10 |      100 |         94 |           0.94 |  0.87523 |   0.97221 |                 0 |   44.5688 |           30    |
| gauss    | known      | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.26   |           30    |
| gauss    | known      | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.17   |           30    |
| gauss    | known      | sp       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  440.971  |           30    |
| gauss    | known      | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  466.562  |           30    |
| resample | fitted     | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.32   |           30    |
| resample | fitted     | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.23   |           30    |
| resample | fitted     | sp       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  480.556  |           30    |
| resample | fitted     | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  564.869  |           30    |
| resample | fitted_ar1 | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.32   |           30    |
| resample | fitted_ar1 | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.23   |           30    |
| resample | fitted_ar1 | sp       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  245.078  |           30    |
| resample | fitted_ar1 | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  513.819  |           30    |
| resample | iid        | se       |   5 |      100 |         80 |           0.8  |  0.71117 |   0.86663 |                 0 |  177.181  |            6.36 |
| resample | iid        | se       |  10 |      100 |         98 |           0.98 |  0.92999 |   0.9945  |                 0 |  289.287  |           10.33 |
| resample | iid        | sp       |   5 |      100 |         56 |           0.56 |  0.46228 |   0.65328 |                 0 |   37.3864 |           30    |
| resample | iid        | sp       |  10 |      100 |         95 |           0.95 |  0.88825 |   0.97846 |                 0 |   47.12   |           30    |
| resample | known      | se       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1079.26   |           30    |
| resample | known      | se       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 | 1600.17   |           30    |
| resample | known      | sp       |   5 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  466.38   |           30    |
| resample | known      | sp       |  10 |      100 |          0 |           0    |  0       |   0.03699 |                 0 |  454.516  |           30    |
