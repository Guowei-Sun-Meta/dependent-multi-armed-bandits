Regret per round at T = 2,000 (mean over seeds; standard error in brackets). Dynamic regret is against the full-current-state oracle; mean regret against the best long-run mean.

**main** (innovation lower bound: 0.298 per round)

| Policy | Uses | Dynamic regret / round | Ratio to TS | Mean regret / round |
| --- | --- | ---: | ---: | ---: |
| spectral_ucb | spatial only | 1.026 [0.045] | 0.794 | 0.712 |
| ucb | iid | 1.095 [0.061] | 0.847 | 0.682 |
| st_ts | spatiotemporal | 1.258 [0.027] | 0.969 | 0.784 |
| spectral_ts | spatial only | 1.314 [0.083] | 1.004 | 0.530 |
| ar_twostep | temporal only | 1.323 [0.078] | 1.022 | 0.780 |
| ts | iid | 1.329 [0.070] | 1.000 | 0.523 |
| st_twostep | spatiotemporal | 1.402 [0.084] | 1.086 | 0.681 |
| ar_ts | temporal only | 1.433 [0.036] | 1.103 | 0.821 |
| st_ucb | spatiotemporal | 1.489 [0.016] | 1.145 | 0.876 |
| st_greedy | spatiotemporal | 1.509 [0.099] | 1.166 | 0.774 |
| swucb | iid | 1.540 [0.043] | 1.191 | 0.916 |

**no_spatial** (innovation lower bound: 0.323 per round)

| Policy | Uses | Dynamic regret / round | Ratio to TS | Mean regret / round |
| --- | --- | ---: | ---: | ---: |
| spectral_ucb | spatial only | 1.014 [0.049] | 0.685 | 0.592 |
| ucb | iid | 1.157 [0.032] | 0.775 | 0.661 |
| spectral_ts | spatial only | 1.416 [0.087] | 0.933 | 0.554 |
| st_twostep | spatiotemporal | 1.429 [0.066] | 0.973 | 0.717 |
| st_ts | spatiotemporal | 1.452 [0.039] | 0.980 | 0.806 |
| ar_ts | temporal only | 1.452 [0.050] | 0.982 | 0.826 |
| ts | iid | 1.523 [0.090] | 1.000 | 0.584 |
| ar_twostep | temporal only | 1.586 [0.069] | 1.083 | 0.883 |
| swucb | iid | 1.586 [0.023] | 1.076 | 0.909 |
| st_greedy | spatiotemporal | 1.678 [0.061] | 1.138 | 0.782 |
| st_ucb | spatiotemporal | 1.838 [0.033] | 1.242 | 0.929 |

**weak_persistence** (innovation lower bound: 1.276 per round)

| Policy | Uses | Dynamic regret / round | Ratio to TS | Mean regret / round |
| --- | --- | ---: | ---: | ---: |
| st_ucb | spatiotemporal | 1.499 [0.061] | 0.896 | 0.192 |
| spectral_ts | spatial only | 1.617 [0.035] | 0.967 | 0.242 |
| ts | iid | 1.675 [0.049] | 1.000 | 0.293 |
| st_twostep | spatiotemporal | 1.848 [0.068] | 1.113 | 0.459 |
| ar_twostep | temporal only | 1.850 [0.077] | 1.108 | 0.502 |
| ucb | iid | 1.867 [0.048] | 1.117 | 0.557 |
| st_greedy | spatiotemporal | 1.932 [0.075] | 1.161 | 0.545 |
| spectral_ucb | spatial only | 1.953 [0.034] | 1.170 | 0.697 |
| st_ts | spatiotemporal | 2.246 [0.016] | 1.348 | 0.862 |
| ar_ts | temporal only | 2.270 [0.019] | 1.362 | 0.879 |
| swucb | iid | 2.282 [0.012] | 1.370 | 0.963 |
