# Experiment 3b: certified pooling in worlds calibrated to Wikipedia attention

30 articles (5 per community), AR(7) fitted on 2022–2023, horizon 730 days, 100 worlds per cell. `violation`: any arm or component upper bound below its target on some day (95% Wilson). `best out`: successive elimination dropped the best article. Regret is mean regret over 730 days (rescaled log-views, slate of k).

| innovations   | policy      |   k | learner    | violation          | best out          |   regret@730 |   active at end |
|:--------------|:------------|----:|:-----------|:-------------------|:------------------|-------------:|----------------:|
| block         | elimination |   5 | fitted     | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| block         | elimination |   5 | fitted_ar1 | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| block         | elimination |   5 | iid        | 86/100 (0.78–0.91) | 0/100 (0.00–0.04) |          168 |             6.1 |
| block         | elimination |   5 | known      | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| block         | elimination |  10 | fitted     | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| block         | elimination |  10 | fitted_ar1 | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| block         | elimination |  10 | iid        | 98/100 (0.93–0.99) | 0/100 (0.00–0.04) |          303 |            10.4 |
| block         | elimination |  10 | known      | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| block         | SP-UCB      |   5 | fitted     | 0/100 (0.00–0.04)  |                   |          473 |            30   |
| block         | SP-UCB      |   5 | fitted_ar1 | 1/100 (0.00–0.05)  |                   |          248 |            30   |
| block         | SP-UCB      |   5 | iid        | 47/100 (0.38–0.57) |                   |           36 |            30   |
| block         | SP-UCB      |   5 | known      | 1/100 (0.00–0.05)  |                   |          459 |            30   |
| block         | SP-UCB      |  10 | fitted     | 0/100 (0.00–0.04)  |                   |          578 |            30   |
| block         | SP-UCB      |  10 | fitted_ar1 | 0/100 (0.00–0.04)  |                   |          585 |            30   |
| block         | SP-UCB      |  10 | iid        | 98/100 (0.93–0.99) |                   |           48 |            30   |
| block         | SP-UCB      |  10 | known      | 0/100 (0.00–0.04)  |                   |          460 |            30   |
| gauss         | elimination |   5 | fitted     | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| gauss         | elimination |   5 | fitted_ar1 | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| gauss         | elimination |   5 | iid        | 78/100 (0.69–0.85) | 0/100 (0.00–0.04) |          179 |             6.5 |
| gauss         | elimination |   5 | known      | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| gauss         | elimination |  10 | fitted     | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| gauss         | elimination |  10 | fitted_ar1 | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| gauss         | elimination |  10 | iid        | 99/100 (0.95–1.00) | 0/100 (0.00–0.04) |          289 |            10.4 |
| gauss         | elimination |  10 | known      | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| gauss         | SP-UCB      |   5 | fitted     | 0/100 (0.00–0.04)  |                   |          459 |            30   |
| gauss         | SP-UCB      |   5 | fitted_ar1 | 0/100 (0.00–0.04)  |                   |          211 |            30   |
| gauss         | SP-UCB      |   5 | iid        | 56/100 (0.46–0.65) |                   |           38 |            30   |
| gauss         | SP-UCB      |   5 | known      | 0/100 (0.00–0.04)  |                   |          441 |            30   |
| gauss         | SP-UCB      |  10 | fitted     | 0/100 (0.00–0.04)  |                   |          506 |            30   |
| gauss         | SP-UCB      |  10 | fitted_ar1 | 0/100 (0.00–0.04)  |                   |          511 |            30   |
| gauss         | SP-UCB      |  10 | iid        | 94/100 (0.88–0.97) |                   |           45 |            30   |
| gauss         | SP-UCB      |  10 | known      | 0/100 (0.00–0.04)  |                   |          467 |            30   |
| resample      | elimination |   5 | fitted     | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| resample      | elimination |   5 | fitted_ar1 | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| resample      | elimination |   5 | iid        | 80/100 (0.71–0.87) | 0/100 (0.00–0.04) |          177 |             6.4 |
| resample      | elimination |   5 | known      | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1079 |            30   |
| resample      | elimination |  10 | fitted     | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| resample      | elimination |  10 | fitted_ar1 | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| resample      | elimination |  10 | iid        | 98/100 (0.93–0.99) | 0/100 (0.00–0.04) |          289 |            10.3 |
| resample      | elimination |  10 | known      | 0/100 (0.00–0.04)  | 0/100 (0.00–0.04) |         1600 |            30   |
| resample      | SP-UCB      |   5 | fitted     | 0/100 (0.00–0.04)  |                   |          481 |            30   |
| resample      | SP-UCB      |   5 | fitted_ar1 | 0/100 (0.00–0.04)  |                   |          245 |            30   |
| resample      | SP-UCB      |   5 | iid        | 56/100 (0.46–0.65) |                   |           37 |            30   |
| resample      | SP-UCB      |   5 | known      | 0/100 (0.00–0.04)  |                   |          466 |            30   |
| resample      | SP-UCB      |  10 | fitted     | 0/100 (0.00–0.04)  |                   |          565 |            30   |
| resample      | SP-UCB      |  10 | fitted_ar1 | 0/100 (0.00–0.04)  |                   |          514 |            30   |
| resample      | SP-UCB      |  10 | iid        | 95/100 (0.89–0.98) |                   |           47 |            30   |
| resample      | SP-UCB      |  10 | known      | 0/100 (0.00–0.04)  |                   |          455 |            30   |

## Why the valid certificates never decide: interval widths

Median arm interval width with the true model, random 5-article slates, 5 worlds. Means lie in [0, 1]. `pointwise_2sd` is ±2 posterior sd with no anytime or simultaneity correction.

|   day |   plugin_B1pp |   ellipsoid |   pointwise_2sd |    beta |   spread_of_means_sd |   gap_best_to_2nd |
|------:|--------------:|------------:|----------------:|--------:|---------------------:|------------------:|
|   365 |        1.7925 |      0.9308 |          0.0957 | 19.4492 |               0.1737 |            0.1351 |
|   730 |        1.7394 |      0.7025 |          0.0704 | 19.9513 |               0.1737 |            0.1351 |
