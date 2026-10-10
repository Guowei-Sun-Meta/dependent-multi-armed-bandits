# Experiment 6: theory instances

## B3: slate contrast information

Variance of the contrast of two arms' sample means at shock correlation ρ, relative to ρ = 0 (smaller is better), n = 365 observations of each arm. `1−ρ` is the shortcut; `long-run` uses (Ω_ii + Ω_jj − 2Ω_ij) / (Ω_ii + Ω_jj).

| case       |   rho |   simultaneous |   staggered |   1−ρ |   long-run |
|:-----------|------:|---------------:|------------:|------:|-----------:|
| equal      |   0   |          1     |       1     |   1   |      1     |
| equal      |   0.3 |          0.7   |       0.702 |   0.7 |      0.7   |
| equal      |   0.6 |          0.4   |       0.404 |   0.4 |      0.4   |
| equal      |   0.9 |          0.1   |       0.106 |   0.1 |      0.1   |
| equal_iid  |   0   |          1     |       1     |   1   |      1     |
| equal_iid  |   0.3 |          0.703 |       1     |   0.7 |      0.703 |
| equal_iid  |   0.6 |          0.406 |       1     |   0.4 |      0.406 |
| equal_iid  |   0.9 |          0.109 |       1     |   0.1 |      0.109 |
| hetero_phi |   0   |          1     |       1     |   1   |      1     |
| hetero_phi |   0.3 |          0.794 |       0.802 |   0.7 |      0.794 |
| hetero_phi |   0.6 |          0.589 |       0.604 |   0.4 |      0.589 |
| hetero_phi |   0.9 |          0.383 |       0.406 |   0.1 |      0.383 |
| unequal_sd |   0   |          1     |       1     |   1   |      1     |
| unequal_sd |   0.3 |          0.76  |       0.761 |   0.7 |      0.76  |
| unequal_sd |   0.6 |          0.52  |       0.523 |   0.4 |      0.52  |
| unequal_sd |   0.9 |          0.28  |       0.284 |   0.1 |      0.28  |

Finite-n exact variance over the long-run prediction (simultaneous, ρ = 0.6). Below 1: the long-run formula overstates the variance of short persistent runs.

| case       |     7 |    30 |   365 |
|:-----------|------:|------:|------:|
| equal      | 0.295 | 0.698 | 0.974 |
| equal_iid  | 1     | 1     | 1     |
| hetero_phi | 0.365 | 0.733 | 0.977 |
| unequal_sd | 0.294 | 0.698 | 0.974 |

Monte Carlo check (equal pair, φ = 0.9, ρ = 0.6, n = 30, 20,000 draws):

| design       |   mc_var |   exact_var |
|:-------------|---------:|------------:|
| simultaneous |   0.3532 |      0.3541 |
| staggered    |   0.2173 |      0.2173 |
