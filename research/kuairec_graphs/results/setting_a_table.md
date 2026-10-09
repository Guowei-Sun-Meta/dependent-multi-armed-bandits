Regret at T = 20,000 relative to Bernoulli Thompson sampling (mean over users; 95% bootstrap CI).

Family ratio: UCB-style policies against UCB1; spectral TS against itself at lambda = 0.1 (nearly graph-free).

| Policy | Graph | Parameter | Ratio to TS (mean) | 95% CI | Median | 90th pct. | Share beating TS | Ratio to family (mean / median) |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| ucb | - | - | 7.780 | 6.477 to 9.076 | 4.286 | 14.02 | 0.00 | 1.000 / 1.000 |
| ts | - | - | 1.000 | 1.000 to 1.000 | 1.000 | 1.00 | 0.00 | nan / nan |
| spectral_ucb | I-mf | 0.1 | 7.726 | 6.415 to 9.101 | 4.279 | 13.99 | 0.00 | 0.995 / 0.998 |
| spectral_ts | I-mf | 0.1 | 2.637 | 2.209 to 3.073 | 1.335 | 4.73 | 0.03 | 1.000 / 1.000 |
| spectral_ucb | I-mf | 1.0 | 7.414 | 6.201 to 8.643 | 4.125 | 13.26 | 0.00 | 0.966 / 0.964 |
| spectral_ts | I-mf | 1.0 | 2.292 | 1.929 to 2.643 | 1.180 | 3.97 | 0.30 | 0.899 / 0.888 |
| spectral_ucb | I-mf | 10.0 | 4.558 | 3.973 to 5.141 | 2.728 | 7.54 | 0.00 | 0.697 / 0.654 |
| spectral_ts | I-mf | 10.0 | 1.645 | 0.833 to 2.671 | 0.680 | 1.71 | 0.75 | 0.611 / 0.399 |
| sp_ucb | I-mf | oracle | 3.683 | 2.995 to 4.435 | 2.228 | 8.06 | 0.00 | 0.529 / 0.507 |
| sp_ucb | I-mf | energy | 6.978 | 5.842 to 8.196 | 3.842 | 12.87 | 0.00 | 0.922 / 0.938 |
| sp_ucb | I-mf | none | 1.945 | 1.638 to 2.260 | 1.293 | 3.61 | 0.35 | 0.303 / 0.255 |
| spectral_ucb | I-coeng | 0.1 | 7.733 | 6.427 to 9.131 | 4.279 | 13.98 | 0.00 | 0.996 / 0.998 |
| spectral_ts | I-coeng | 0.1 | 2.638 | 2.213 to 3.068 | 1.337 | 4.73 | 0.03 | 1.000 / 1.000 |
| spectral_ucb | I-coeng | 1.0 | 7.449 | 6.189 to 8.739 | 4.148 | 13.38 | 0.00 | 0.970 / 0.968 |
| spectral_ts | I-coeng | 1.0 | 2.388 | 2.006 to 2.797 | 1.187 | 4.12 | 0.30 | 0.922 / 0.908 |
| spectral_ucb | I-coeng | 10.0 | 7.347 | 5.424 to 9.578 | 3.048 | 14.69 | 0.00 | 0.920 / 0.814 |
| spectral_ts | I-coeng | 10.0 | 4.189 | 2.258 to 6.378 | 1.112 | 18.78 | 0.45 | 1.339 / 0.661 |
| sp_ucb | I-coeng | oracle | 3.495 | 2.847 to 4.255 | 1.956 | 7.90 | 0.03 | 0.495 / 0.476 |
| sp_ucb | I-coeng | energy | 7.305 | 6.066 to 8.572 | 3.811 | 13.53 | 0.00 | 0.950 / 0.977 |
| sp_ucb | I-coeng | none | 2.602 | 1.892 to 3.421 | 1.490 | 5.02 | 0.28 | 0.370 / 0.291 |
| spectral_ucb | I-coauthor | 0.1 | 7.744 | 6.416 to 9.033 | 4.268 | 13.97 | 0.00 | 0.997 / 0.997 |
| spectral_ts | I-coauthor | 0.1 | 2.639 | 2.245 to 3.052 | 1.335 | 4.72 | 0.03 | 1.000 / 1.000 |
| spectral_ucb | I-coauthor | 1.0 | 7.521 | 6.319 to 8.855 | 4.159 | 13.53 | 0.00 | 0.975 / 0.974 |
| spectral_ts | I-coauthor | 1.0 | 2.522 | 2.104 to 2.926 | 1.273 | 4.48 | 0.22 | 0.962 / 0.958 |
| spectral_ucb | I-coauthor | 10.0 | 7.194 | 5.988 to 8.388 | 3.933 | 12.90 | 0.00 | 0.938 / 0.931 |
| spectral_ts | I-coauthor | 10.0 | 2.474 | 2.093 to 2.875 | 1.363 | 4.40 | 0.32 | 0.944 / 0.933 |
| sp_ucb | I-coauthor | oracle | 6.264 | 5.078 to 7.454 | 3.398 | 13.00 | 0.05 | 0.808 / 0.921 |
| sp_ucb | I-coauthor | energy | 7.485 | 6.169 to 8.838 | 4.087 | 13.58 | 0.00 | 0.968 / 0.968 |
| sp_ucb | I-coauthor | none | 8.804 | 5.556 to 12.096 | 2.064 | 29.61 | 0.27 | 0.952 / 0.733 |
| spectral_ucb | I-tag | 0.1 | 7.727 | 6.412 to 9.045 | 4.277 | 13.99 | 0.00 | 0.995 / 0.998 |
| spectral_ts | I-tag | 0.1 | 2.638 | 2.218 to 3.075 | 1.336 | 4.73 | 0.03 | 1.000 / 1.000 |
| spectral_ucb | I-tag | 1.0 | 7.421 | 6.179 to 8.670 | 4.139 | 13.30 | 0.00 | 0.967 / 0.967 |
| spectral_ts | I-tag | 1.0 | 2.305 | 1.956 to 2.660 | 1.179 | 4.05 | 0.28 | 0.902 / 0.898 |
| spectral_ucb | I-tag | 10.0 | 4.665 | 4.026 to 5.290 | 2.806 | 7.94 | 0.00 | 0.707 / 0.664 |
| spectral_ts | I-tag | 10.0 | 1.389 | 0.922 to 1.988 | 0.764 | 2.16 | 0.67 | 0.575 / 0.453 |
| sp_ucb | I-tag | oracle | 4.147 | 3.408 to 4.964 | 2.482 | 10.01 | 0.00 | 0.594 / 0.577 |
| sp_ucb | I-tag | energy | 7.117 | 5.946 to 8.294 | 3.797 | 13.07 | 0.00 | 0.934 / 0.952 |
| sp_ucb | I-tag | none | 3.246 | 2.234 to 4.613 | 1.762 | 4.75 | 0.27 | 0.451 / 0.321 |
| spectral_ucb | I-cat | 0.1 | 7.735 | 6.460 to 9.105 | 4.276 | 13.99 | 0.00 | 0.996 / 0.998 |
| spectral_ts | I-cat | 0.1 | 2.636 | 2.186 to 3.076 | 1.334 | 4.70 | 0.03 | 1.000 / 1.000 |
| spectral_ucb | I-cat | 1.0 | 7.428 | 6.080 to 8.700 | 4.147 | 13.32 | 0.00 | 0.967 / 0.967 |
| spectral_ts | I-cat | 1.0 | 2.329 | 1.964 to 2.690 | 1.205 | 4.06 | 0.27 | 0.909 / 0.903 |
| spectral_ucb | I-cat | 10.0 | 5.398 | 4.532 to 6.338 | 3.039 | 8.86 | 0.00 | 0.771 / 0.730 |
| spectral_ts | I-cat | 10.0 | 2.827 | 1.755 to 4.214 | 1.106 | 6.30 | 0.47 | 1.012 / 0.620 |
| sp_ucb | I-cat | oracle | 4.284 | 3.476 to 5.076 | 2.538 | 10.20 | 0.00 | 0.608 / 0.608 |
| sp_ucb | I-cat | energy | 7.135 | 5.901 to 8.311 | 3.821 | 13.08 | 0.00 | 0.937 / 0.956 |
| sp_ucb | I-cat | none | 4.540 | 2.837 to 6.738 | 1.721 | 11.37 | 0.32 | 0.542 / 0.361 |
| spectral_ucb | I-mf~rewired | 0.1 | 7.726 | 6.464 to 9.082 | 4.278 | 13.99 | 0.00 | 0.995 / 0.998 |
| spectral_ts | I-mf~rewired | 0.1 | 2.636 | 2.192 to 3.068 | 1.337 | 4.72 | 0.03 | 1.000 / 1.000 |
| spectral_ucb | I-mf~rewired | 1.0 | 7.413 | 6.131 to 8.760 | 4.128 | 13.30 | 0.00 | 0.966 / 0.965 |
| spectral_ts | I-mf~rewired | 1.0 | 2.293 | 1.944 to 2.668 | 1.182 | 3.98 | 0.30 | 0.900 / 0.890 |
| spectral_ucb | I-mf~rewired | 10.0 | 4.524 | 3.873 to 5.157 | 2.761 | 7.46 | 0.00 | 0.695 / 0.650 |
| spectral_ts | I-mf~rewired | 10.0 | 1.673 | 0.813 to 2.801 | 0.676 | 1.79 | 0.80 | 0.610 / 0.375 |
| sp_ucb | I-mf~rewired | oracle | 3.991 | 3.227 to 4.852 | 2.408 | 9.24 | 0.02 | 0.580 / 0.572 |
| sp_ucb | I-mf~rewired | energy | 7.700 | 6.339 to 9.072 | 4.165 | 14.01 | 0.00 | 0.993 / 1.000 |
| sp_ucb | I-mf~rewired | none | 1.972 | 1.672 to 2.298 | 1.442 | 3.68 | 0.30 | 0.317 / 0.257 |

Per-instance graph diagnostics (300-video graphs; medians or means over users):

| Graph | Quotient | Energy-to-gap (10th) | Share of components rejectable, oracle cert. | Share rejectable, energy cert. |
| --- | ---: | ---: | ---: | ---: |
| I-coauthor | 0.709 | 5.0 | 0.83 | 0.68 |
| I-mf | 0.846 | 4.9 | 0.61 | 0.21 |
| I-cat | 0.950 | 5.0 | 0.66 | 0.33 |
| I-mf~rewired | 0.964 | 5.3 | 0.55 | 0.03 |
| I-tag | 0.974 | 5.4 | 0.65 | 0.29 |
| I-coeng | 1.038 | 5.7 | 0.71 | 0.18 |
