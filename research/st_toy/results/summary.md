Regret per round at T = 2,000 (mean over seeds; standard error in brackets). Dynamic regret is against the full-current-state oracle; mean regret against the best long-run mean.

**main** (innovation lower bound: 0.298 per round)

| Policy | Uses | Dynamic regret / round | Ratio to TS | Gap to the bound closed | Mean regret / round |
| --- | --- | ---: | ---: | ---: | ---: |
| st_ucbm2 | spatiotemporal | 0.850 [0.043] | 0.651 | +46% | 0.565 |
| st_ucbm4 | spatiotemporal | 0.863 [0.040] | 0.666 | +45% | 0.655 |
| st_ps | spatiotemporal | 0.950 [0.031] | 0.733 | +37% | 0.686 |
| spectral_ucb | spatial only | 1.026 [0.045] | 0.794 | +29% | 0.712 |
| ucb | iid | 1.095 [0.061] | 0.847 | +23% | 0.682 |
| st_ucbm1 | spatiotemporal | 1.098 [0.045] | 0.845 | +22% | 0.600 |
| ar_ps | temporal only | 1.121 [0.047] | 0.864 | +20% | 0.752 |
| st_ts | spatiotemporal | 1.258 [0.027] | 0.969 | +7% | 0.784 |
| spectral_ts | spatial only | 1.314 [0.083] | 1.004 | +1% | 0.530 |
| ar_twostep | temporal only | 1.323 [0.078] | 1.022 | +1% | 0.780 |
| ts | iid | 1.329 [0.070] | 1.000 | +0% | 0.523 |
| st_twostep | spatiotemporal | 1.402 [0.084] | 1.086 | -7% | 0.681 |
| ar_ts | temporal only | 1.433 [0.036] | 1.103 | -10% | 0.821 |
| st_ucb | spatiotemporal | 1.489 [0.016] | 1.145 | -16% | 0.876 |
| st_greedy | spatiotemporal | 1.509 [0.099] | 1.166 | -17% | 0.774 |
| swucb | iid | 1.540 [0.043] | 1.191 | -20% | 0.916 |

**no_spatial** (innovation lower bound: 0.323 per round)

| Policy | Uses | Dynamic regret / round | Ratio to TS | Gap to the bound closed | Mean regret / round |
| --- | --- | ---: | ---: | ---: | ---: |
| st_ucbm2 | spatiotemporal | 0.890 [0.048] | 0.599 | +53% | 0.512 |
| st_ucbm4 | spatiotemporal | 0.953 [0.040] | 0.648 | +48% | 0.680 |
| spectral_ucb | spatial only | 1.014 [0.049] | 0.685 | +42% | 0.592 |
| st_ps | spatiotemporal | 1.057 [0.039] | 0.717 | +39% | 0.721 |
| ar_ps | temporal only | 1.094 [0.054] | 0.744 | +36% | 0.743 |
| ucb | iid | 1.157 [0.032] | 0.775 | +30% | 0.661 |
| st_ucbm1 | spatiotemporal | 1.252 [0.078] | 0.849 | +23% | 0.736 |
| spectral_ts | spatial only | 1.416 [0.087] | 0.933 | +9% | 0.554 |
| st_twostep | spatiotemporal | 1.429 [0.066] | 0.973 | +8% | 0.717 |
| st_ts | spatiotemporal | 1.452 [0.039] | 0.980 | +6% | 0.806 |
| ar_ts | temporal only | 1.452 [0.050] | 0.982 | +6% | 0.826 |
| ts | iid | 1.523 [0.090] | 1.000 | +0% | 0.584 |
| ar_twostep | temporal only | 1.586 [0.069] | 1.083 | -5% | 0.883 |
| swucb | iid | 1.586 [0.023] | 1.076 | -5% | 0.909 |
| st_greedy | spatiotemporal | 1.678 [0.061] | 1.138 | -13% | 0.782 |
| st_ucb | spatiotemporal | 1.838 [0.033] | 1.242 | -26% | 0.929 |

**weak_persistence** (innovation lower bound: 1.276 per round)

| Policy | Uses | Dynamic regret / round | Ratio to TS | Gap to the bound closed | Mean regret / round |
| --- | --- | ---: | ---: | ---: | ---: |
| st_ucb | spatiotemporal | 1.499 [0.061] | 0.896 | +44% | 0.192 |
| ar_ps | temporal only | 1.525 [0.053] | 0.911 | +38% | 0.198 |
| st_ps | spatiotemporal | 1.568 [0.063] | 0.937 | +27% | 0.257 |
| st_ucbm4 | spatiotemporal | 1.596 [0.065] | 0.956 | +20% | 0.297 |
| spectral_ts | spatial only | 1.617 [0.035] | 0.967 | +15% | 0.242 |
| ts | iid | 1.675 [0.049] | 1.000 | +0% | 0.293 |
| st_ucbm1 | spatiotemporal | 1.705 [0.094] | 1.026 | -7% | 0.345 |
| st_twostep | spatiotemporal | 1.848 [0.068] | 1.113 | -43% | 0.459 |
| ar_twostep | temporal only | 1.850 [0.077] | 1.108 | -44% | 0.502 |
| st_ucbm2 | spatiotemporal | 1.856 [0.041] | 1.114 | -45% | 0.522 |
| ucb | iid | 1.867 [0.048] | 1.117 | -48% | 0.557 |
| st_greedy | spatiotemporal | 1.932 [0.075] | 1.161 | -64% | 0.545 |
| spectral_ucb | spatial only | 1.953 [0.034] | 1.170 | -70% | 0.697 |
| st_ts | spatiotemporal | 2.246 [0.016] | 1.348 | -143% | 0.862 |
| ar_ts | temporal only | 2.270 [0.019] | 1.362 | -149% | 0.879 |
| swucb | iid | 2.282 [0.012] | 1.370 | -152% | 0.963 |
