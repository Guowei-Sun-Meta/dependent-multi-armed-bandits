# Experiment 6: theory instances

## B2: false elimination and lasting regret

Certified successive elimination, known dynamics for `se_st2` (B1''). `best out`: share of runs that eliminated the best arm (95% Wilson). `late rate`: mean per-round regret over the last 2,000 of 20,000 rounds; a positive late rate is linear regret.

|    φ |   batch | policy   | best out           | median time out   |   regret@2k |   regret@20k |   late rate (all) | late rate | best out   |
|-----:|--------:|:---------|:-------------------|:------------------|------------:|-------------:|------------------:|:-----------------------|
| 0    |       1 | se_iid   | 0/100 (0–0.04)     |                   |         470 |         4566 |             0.202 |                        |
| 0    |       1 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         3805 |             0.107 |                        |
| 0    |      10 | se_iid   | 0/100 (0–0.04)     |                   |         470 |         4537 |             0.199 |                        |
| 0    |      10 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         3923 |             0.112 |                        |
| 0    |      25 | se_iid   | 0/100 (0–0.04)     |                   |         470 |         4550 |             0.201 |                        |
| 0    |      25 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         3941 |             0.116 |                        |
| 0    |     100 | se_iid   | 0/100 (0–0.04)     |                   |         470 |         4570 |             0.206 |                        |
| 0    |     100 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4023 |             0.123 |                        |
| 0.9  |       1 | se_iid   | 0/100 (0–0.04)     |                   |         470 |         4475 |             0.192 |                        |
| 0.9  |       1 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4323 |             0.173 |                        |
| 0.9  |      10 | se_iid   | 5/100 (0.02–0.11)  | 210               |         437 |         2762 |             0.08  | 0.202                  |
| 0.9  |      10 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4696 |             0.235 |                        |
| 0.9  |      25 | se_iid   | 28/100 (0.20–0.37) | 1150              |         401 |         2115 |             0.064 | 0.138                  |
| 0.9  |      25 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4696 |             0.235 |                        |
| 0.9  |     100 | se_iid   | 39/100 (0.30–0.49) | 2300              |         434 |         2552 |             0.085 | 0.153                  |
| 0.9  |     100 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4696 |             0.235 |                        |
| 0.97 |       1 | se_iid   | 0/100 (0–0.04)     |                   |         469 |         3979 |             0.131 |                        |
| 0.97 |       1 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4678 |             0.231 |                        |
| 0.97 |      10 | se_iid   | 28/100 (0.20–0.37) | 650               |         426 |         2750 |             0.085 | 0.169                  |
| 0.97 |      10 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4696 |             0.235 |                        |
| 0.97 |      25 | se_iid   | 72/100 (0.63–0.80) | 500               |         416 |         3558 |             0.169 | 0.228                  |
| 0.97 |      25 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4696 |             0.235 |                        |
| 0.97 |     100 | se_iid   | 89/100 (0.81–0.94) | 1100              |         437 |         4550 |             0.229 | 0.256                  |
| 0.97 |     100 | se_st2   | 0/100 (0–0.04)     |                   |         470 |         4696 |             0.235 |                        |

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
