| configuration   | objective                    | observed_leader      |   value |   ci_low |   ci_high |   worlds | scope                                                                       |
|:----------------|:-----------------------------|:---------------------|--------:|---------:|----------:|---------:|:----------------------------------------------------------------------------|
| heterogeneous   | oracle_regret_per_round      | joint_predictive_ucb | 1.61684 |  1.56753 |   1.66615 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| heterogeneous   | mean_pseudo_regret_per_round | joint_state_ucb      | 0.39716 |  0.36845 |   0.42587 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| heterogeneous   | correct_selection            | joint_tt_ts          | 0.5625  |  0.39326 |   0.71835 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| no_spatial      | oracle_regret_per_round      | joint_state_ucb      | 1.27017 |  1.21576 |   1.32458 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| no_spatial      | mean_pseudo_regret_per_round | joint_mean_ucb       | 0.4982  |  0.43148 |   0.56493 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| no_spatial      | correct_selection            | joint_predictive_ucb | 0.375   |  0.22934 |   0.54746 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| persistent      | oracle_regret_per_round      | joint_state_ucb      | 1.24772 |  1.20689 |   1.28855 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| persistent      | mean_pseudo_regret_per_round | iid_ucb              | 0.66751 |  0.61418 |   0.72084 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| persistent      | correct_selection            | ar_state_ucb         | 0.25    |  0.13252 |   0.42107 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| seasonal        | oracle_regret_per_round      | joint_state_ucb      | 1.76043 |  1.73468 |   1.78619 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| seasonal        | mean_pseudo_regret_per_round | joint_mean_ucb       | 0.42695 |  0.38876 |   0.46513 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| seasonal        | correct_selection            | joint_lucb           | 0.84375 |  0.68246 |   0.93136 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| weak            | oracle_regret_per_round      | joint_state_ucb      | 1.83752 |  1.78114 |   1.89391 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| weak            | mean_pseudo_regret_per_round | joint_state_ucb      | 0.3211  |  0.2674  |   0.37481 |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
| weak            | correct_selection            | joint_predictive_ucb | 0.90625 |  0.75782 |   0.9676  |       32 | pointwise observed leader, not an optimality or pairwise significance claim |
