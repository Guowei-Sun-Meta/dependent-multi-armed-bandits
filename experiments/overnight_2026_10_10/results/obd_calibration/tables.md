# OBD calibration and truth uncertainty sensitivity

All/Women campaigns; pooled positions and position 1; first 2, 3 or 4 days as prefix.
Graphs and widths use only the prefix. Held-out rates use the remaining days.

Raw prefix ranges ignore sampling uncertainty. The alternative uses simultaneous exact
binomial item intervals, then max upper minus min lower in each component. Those bounds
cover stationary prefix rates under the binomial model; future drift is outside that guarantee.

Posterior coverage integrates 5,000 independent Jeffreys posterior draws of held-out rates.
This is a sensitivity measure conditional on a stationary pooled-rate model, not frequentist
coverage under temporal dependence. Attribute groups use released retrospective metadata.

This audit adds no new bandit-policy results. Existing policy comparisons remain in
`../../oct10_runs/results/obd_pooling/tables.md` and use fixed held-out point estimates as truth.

## Uncertainty about the empirically best item

| campaign   | position   |   prefix_days |   items |   empirical_best_item |   empirical_best_ctr |   posterior_prob_empirical_best_is_best |   items_with_p_best_above_1pct |
|:-----------|:-----------|--------------:|--------:|----------------------:|---------------------:|----------------------------------------:|-------------------------------:|
| all        | pooled     |             2 |      80 |                    60 |              0.00834 |                                  0.533  |                              5 |
| all        | pooled     |             3 |      80 |                    60 |              0.00918 |                                  0.6268 |                              4 |
| all        | pooled     |             4 |      80 |                    60 |              0.01047 |                                  0.7346 |                              4 |
| all        | position1  |             2 |      80 |                    39 |              0.00987 |                                  0.3794 |                              7 |
| all        | position1  |             3 |      80 |                    39 |              0.00984 |                                  0.3644 |                             10 |
| all        | position1  |             4 |      80 |                    39 |              0.01235 |                                  0.513  |                              6 |
| women      | pooled     |             2 |      46 |                    26 |              0.00813 |                                  0.3586 |                              9 |
| women      | pooled     |             3 |      46 |                    26 |              0.00864 |                                  0.5534 |                             10 |
| women      | pooled     |             4 |      46 |                    26 |              0.00881 |                                  0.317  |                             10 |
| women      | position1  |             2 |      46 |                    26 |              0.0107  |                                  0.6412 |                              6 |
| women      | position1  |             3 |      46 |                    26 |              0.01129 |                                  0.5754 |                              5 |
| women      | position1  |             4 |      46 |                    10 |              0.01178 |                                  0.4472 |                              5 |

## Component range calibration

| campaign   | position   |   prefix_days | graph         | width                 |   components |   median_width |   covers_heldout_point_range_share |   posterior_component_coverage_mean |   posterior_all_components_covered_probability |
|:-----------|:-----------|--------------:|:--------------|:----------------------|-------------:|---------------:|-----------------------------------:|------------------------------------:|-----------------------------------------------:|
| all        | pooled     |             2 | attr          | raw_prefix            |           12 |        0.00417 |                            0.5     |                             0.48812 |                                         0      |
| all        | pooled     |             2 | attr          | simultaneous_binomial |           12 |        0.0098  |                            1       |                             1       |                                         1      |
| all        | pooled     |             2 | audience      | raw_prefix            |           12 |        0.00168 |                            0.25    |                             0.22998 |                                         0      |
| all        | pooled     |             2 | audience      | simultaneous_binomial |           12 |        0.00737 |                            1       |                             0.98957 |                                         0.878  |
| all        | pooled     |             2 | attr_shuffled | raw_prefix            |           12 |        0.00451 |                            0.58333 |                             0.55522 |                                         0      |
| all        | pooled     |             2 | attr_shuffled | simultaneous_binomial |           12 |        0.0105  |                            1       |                             0.99993 |                                         0.9992 |
| all        | pooled     |             3 | attr          | raw_prefix            |           12 |        0.00356 |                            0.66667 |                             0.53322 |                                         0      |
| all        | pooled     |             3 | attr          | simultaneous_binomial |           12 |        0.00823 |                            1       |                             0.99582 |                                         0.9498 |
| all        | pooled     |             3 | audience      | raw_prefix            |           12 |        0.00118 |                            0.25    |                             0.28348 |                                         0      |
| all        | pooled     |             3 | audience      | simultaneous_binomial |           12 |        0.00588 |                            1       |                             0.99278 |                                         0.9152 |
| all        | pooled     |             3 | attr_shuffled | raw_prefix            |           12 |        0.00388 |                            0.41667 |                             0.41245 |                                         0      |
| all        | pooled     |             3 | attr_shuffled | simultaneous_binomial |           12 |        0.00848 |                            1       |                             0.98253 |                                         0.798  |
| all        | pooled     |             4 | attr          | raw_prefix            |           12 |        0.00347 |                            0.33333 |                             0.29848 |                                         0      |
| all        | pooled     |             4 | attr          | simultaneous_binomial |           12 |        0.00739 |                            0.91667 |                             0.94092 |                                         0.3482 |
| all        | pooled     |             4 | audience      | raw_prefix            |           12 |        0.00166 |                            0.16667 |                             0.08545 |                                         0      |
| all        | pooled     |             4 | audience      | simultaneous_binomial |           12 |        0.00578 |                            0.91667 |                             0.86343 |                                         0.0224 |
| all        | pooled     |             4 | attr_shuffled | raw_prefix            |           12 |        0.00369 |                            0.33333 |                             0.30283 |                                         0      |
| all        | pooled     |             4 | attr_shuffled | simultaneous_binomial |           12 |        0.00779 |                            0.91667 |                             0.89877 |                                         0.157  |
| all        | position1  |             2 | attr          | raw_prefix            |           12 |        0.00628 |                            0.83333 |                             0.7075  |                                         0.0028 |
| all        | position1  |             2 | attr          | simultaneous_binomial |           12 |        0.01791 |                            1       |                             1       |                                         1      |
| all        | position1  |             2 | audience      | raw_prefix            |           12 |        0.00273 |                            0.25    |                             0.25243 |                                         0      |
| all        | position1  |             2 | audience      | simultaneous_binomial |           12 |        0.01487 |                            1       |                             0.9995  |                                         0.994  |
| all        | position1  |             2 | attr_shuffled | raw_prefix            |           12 |        0.00615 |                            0.83333 |                             0.67218 |                                         0      |
| all        | position1  |             2 | attr_shuffled | simultaneous_binomial |           12 |        0.01768 |                            1       |                             0.99995 |                                         0.9994 |
| all        | position1  |             3 | attr          | raw_prefix            |           12 |        0.00478 |                            0.58333 |                             0.50052 |                                         0      |
| all        | position1  |             3 | attr          | simultaneous_binomial |           12 |        0.01327 |                            1       |                             0.99973 |                                         0.9968 |
| all        | position1  |             3 | audience      | raw_prefix            |           12 |        0.00295 |                            0.41667 |                             0.24992 |                                         0      |
| all        | position1  |             3 | audience      | simultaneous_binomial |           12 |        0.01193 |                            1       |                             0.99825 |                                         0.979  |
| all        | position1  |             3 | attr_shuffled | raw_prefix            |           12 |        0.00505 |                            0.5     |                             0.40765 |                                         0      |
| all        | position1  |             3 | attr_shuffled | simultaneous_binomial |           12 |        0.01417 |                            1       |                             0.99893 |                                         0.9872 |
| all        | position1  |             4 | attr          | raw_prefix            |           12 |        0.00517 |                            0.33333 |                             0.30558 |                                         0      |
| all        | position1  |             4 | attr          | simultaneous_binomial |           12 |        0.01324 |                            1       |                             0.99608 |                                         0.954  |
| all        | position1  |             4 | audience      | raw_prefix            |           12 |        0.00256 |                            0.16667 |                             0.13717 |                                         0      |
| all        | position1  |             4 | audience      | simultaneous_binomial |           12 |        0.00965 |                            1       |                             0.93042 |                                         0.3668 |
| all        | position1  |             4 | attr_shuffled | raw_prefix            |           12 |        0.0042  |                            0.33333 |                             0.2873  |                                         0      |
| all        | position1  |             4 | attr_shuffled | simultaneous_binomial |           12 |        0.01151 |                            1       |                             0.95637 |                                         0.5712 |
| women      | pooled     |             2 | attr          | raw_prefix            |           10 |        0.00339 |                            0.6     |                             0.49484 |                                         0      |
| women      | pooled     |             2 | attr          | simultaneous_binomial |           10 |        0.00945 |                            1       |                             1       |                                         1      |
| women      | pooled     |             2 | audience      | raw_prefix            |           10 |        0.0014  |                            0.4     |                             0.3276  |                                         0      |
| women      | pooled     |             2 | audience      | simultaneous_binomial |           10 |        0.00824 |                            1       |                             1       |                                         1      |
| women      | pooled     |             2 | attr_shuffled | raw_prefix            |           10 |        0.00405 |                            0.5     |                             0.52038 |                                         0      |
| women      | pooled     |             2 | attr_shuffled | simultaneous_binomial |           10 |        0.01025 |                            1       |                             1       |                                         1      |
| women      | pooled     |             3 | attr          | raw_prefix            |           10 |        0.00328 |                            0.5     |                             0.50282 |                                         0      |
| women      | pooled     |             3 | attr          | simultaneous_binomial |           10 |        0.00847 |                            1       |                             0.99992 |                                         0.9992 |
| women      | pooled     |             3 | audience      | raw_prefix            |           10 |        0.00117 |                            0.4     |                             0.32218 |                                         0      |
| women      | pooled     |             3 | audience      | simultaneous_binomial |           10 |        0.00628 |                            1       |                             0.96574 |                                         0.6864 |
| women      | pooled     |             3 | attr_shuffled | raw_prefix            |           10 |        0.00412 |                            0.7     |                             0.61506 |                                         0      |
| women      | pooled     |             3 | attr_shuffled | simultaneous_binomial |           10 |        0.00936 |                            1       |                             1       |                                         1      |
| women      | pooled     |             4 | attr          | raw_prefix            |           10 |        0.00298 |                            0.5     |                             0.36352 |                                         0      |
| women      | pooled     |             4 | attr          | simultaneous_binomial |           10 |        0.00715 |                            1       |                             0.96216 |                                         0.6596 |
| women      | pooled     |             4 | audience      | raw_prefix            |           10 |        0.00137 |                            0.5     |                             0.44474 |                                         0      |
| women      | pooled     |             4 | audience      | simultaneous_binomial |           10 |        0.00596 |                            1       |                             0.94624 |                                         0.5438 |
| women      | pooled     |             4 | attr_shuffled | raw_prefix            |           10 |        0.00362 |                            0.4     |                             0.41026 |                                         0      |
| women      | pooled     |             4 | attr_shuffled | simultaneous_binomial |           10 |        0.00761 |                            1       |                             0.9705  |                                         0.7238 |
| women      | position1  |             2 | attr          | raw_prefix            |           10 |        0.00459 |                            0.6     |                             0.60778 |                                         0      |
| women      | position1  |             2 | attr          | simultaneous_binomial |           10 |        0.01526 |                            1       |                             1       |                                         1      |
| women      | position1  |             2 | audience      | raw_prefix            |           10 |        0.00269 |                            0.2     |                             0.23652 |                                         0      |
| women      | position1  |             2 | audience      | simultaneous_binomial |           10 |        0.01379 |                            1       |                             1       |                                         1      |
| women      | position1  |             2 | attr_shuffled | raw_prefix            |           10 |        0.00317 |                            0.6     |                             0.51012 |                                         0      |
| women      | position1  |             2 | attr_shuffled | simultaneous_binomial |           10 |        0.01547 |                            1       |                             1       |                                         1      |
| women      | position1  |             3 | attr          | raw_prefix            |           10 |        0.00539 |                            0.6     |                             0.55322 |                                         0      |
| women      | position1  |             3 | attr          | simultaneous_binomial |           10 |        0.01534 |                            1       |                             0.99996 |                                         0.9996 |
| women      | position1  |             3 | audience      | raw_prefix            |           10 |        0.00245 |                            0.3     |                             0.2116  |                                         0      |
| women      | position1  |             3 | audience      | simultaneous_binomial |           10 |        0.01161 |                            1       |                             0.9998  |                                         0.998  |
| women      | position1  |             3 | attr_shuffled | raw_prefix            |           10 |        0.00415 |                            0.5     |                             0.46522 |                                         0      |
| women      | position1  |             3 | attr_shuffled | simultaneous_binomial |           10 |        0.01413 |                            1       |                             0.99998 |                                         0.9998 |
| women      | position1  |             4 | attr          | raw_prefix            |           10 |        0.00376 |                            0.4     |                             0.33676 |                                         0      |
| women      | position1  |             4 | attr          | simultaneous_binomial |           10 |        0.01191 |                            1       |                             0.99252 |                                         0.9274 |
| women      | position1  |             4 | audience      | raw_prefix            |           10 |        0.00294 |                            0.3     |                             0.25672 |                                         0      |
| women      | position1  |             4 | audience      | simultaneous_binomial |           10 |        0.01144 |                            1       |                             0.99384 |                                         0.9396 |
| women      | position1  |             4 | attr_shuffled | raw_prefix            |           10 |        0.00475 |                            0.4     |                             0.42682 |                                         0      |
| women      | position1  |             4 | attr_shuffled | simultaneous_binomial |           10 |        0.01259 |                            1       |                             0.98906 |                                         0.8924 |
