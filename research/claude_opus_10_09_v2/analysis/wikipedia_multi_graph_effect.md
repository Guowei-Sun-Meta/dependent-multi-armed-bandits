Six-domain Wikipedia: regret per day with a graph-shrunk shock covariance minus regret with the common-factor covariance, paired by origin and noise seed.

| policy            | baseline          |   runs |   mean difference |   standard error |   relative |
|:------------------|:------------------|-------:|------------------:|-----------------:|-----------:|
| st_greedy         | st_greedy_nograph |     15 |             0.029 |            0.014 |      0.022 |
| st_greedy_block   | st_greedy_nograph |     15 |            -0.009 |            0.012 |     -0.007 |
| st_greedy_rewired | st_greedy_nograph |     15 |             0.008 |            0.005 |      0.006 |
| st_jps            | st_jps_nograph    |     15 |            -0.030 |            0.019 |     -0.020 |
| st_jps_block      | st_jps_nograph    |     15 |            -0.044 |            0.026 |     -0.029 |
