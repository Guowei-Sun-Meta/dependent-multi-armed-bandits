# Spatial and temporal reward experiment

Known zero means and known Gaussian AR(1) dynamics; six path locations, one noisy measurement per round.
24 paired independent runs per configuration, horizon 1200; measurement variance 0.04.
All policies see the same underlying trajectory and potential measurement noises within each run.
Numbers below are cumulative regret divided by the finite horizon, not a proved limiting coefficient.

| Graph strength | Persistence | Policy | Regret/round | SE |
|---|---|---|---|---|
| 0 | 0 | joint_greedy | 1.2543 | 0.0068 |
| 0 | 0 | joint_two_step | 1.2601 | 0.0067 |
| 0 | 0 | independent_two_step | 1.2601 | 0.0067 |
| 0 | 0 | wrong_graph_two_step | 1.2601 | 0.0067 |
| 0 | 0 | joint_predictive | 1.2617 | 0.0065 |
| 0 | 0 | tv_gp_ucb | 1.2630 | 0.0056 |
| 0 | 0.9 | joint_greedy | 0.5381 | 0.0083 |
| 0 | 0.9 | joint_two_step | 0.5196 | 0.0063 |
| 0 | 0.9 | independent_two_step | 0.5196 | 0.0063 |
| 0 | 0.9 | wrong_graph_two_step | 0.5196 | 0.0063 |
| 0 | 0.9 | joint_predictive | 0.6822 | 0.0065 |
| 0 | 0.9 | tv_gp_ucb | 1.0037 | 0.0038 |
| 0 | 0.99 | joint_greedy | 0.3257 | 0.0207 |
| 0 | 0.99 | joint_two_step | 0.2466 | 0.0133 |
| 0 | 0.99 | independent_two_step | 0.2466 | 0.0133 |
| 0 | 0.99 | wrong_graph_two_step | 0.2466 | 0.0133 |
| 0 | 0.99 | joint_predictive | 0.2112 | 0.0045 |
| 0 | 0.99 | tv_gp_ucb | 0.5523 | 0.0032 |
| 2 | 0 | joint_greedy | 1.0335 | 0.0037 |
| 2 | 0 | joint_two_step | 1.0324 | 0.0047 |
| 2 | 0 | independent_two_step | 1.0324 | 0.0047 |
| 2 | 0 | wrong_graph_two_step | 1.0324 | 0.0047 |
| 2 | 0 | joint_predictive | 1.0296 | 0.0038 |
| 2 | 0 | tv_gp_ucb | 1.0241 | 0.0051 |
| 2 | 0.9 | joint_greedy | 0.5206 | 0.0079 |
| 2 | 0.9 | joint_two_step | 0.4690 | 0.0074 |
| 2 | 0.9 | independent_two_step | 0.4822 | 0.0054 |
| 2 | 0.9 | wrong_graph_two_step | 0.4963 | 0.0088 |
| 2 | 0.9 | joint_predictive | 0.6027 | 0.0053 |
| 2 | 0.9 | tv_gp_ucb | 0.8183 | 0.0047 |
| 2 | 0.99 | joint_greedy | 0.3865 | 0.0267 |
| 2 | 0.99 | joint_two_step | 0.2647 | 0.0180 |
| 2 | 0.99 | independent_two_step | 0.2499 | 0.0170 |
| 2 | 0.99 | wrong_graph_two_step | 0.3225 | 0.0256 |
| 2 | 0.99 | joint_predictive | 0.1862 | 0.0036 |
| 2 | 0.99 | tv_gp_ucb | 0.4612 | 0.0029 |

## Paired comparisons

Positive differences favor joint two-step.

| Graph strength | Persistence | Comparator | Difference | Approx. 95% half-width |
|---|---|---|---|---|
| 0 | 0 | joint_greedy | -0.0058 | 0.0137 |
| 0 | 0 | independent_two_step | 0.0000 | 0.0000 |
| 0 | 0 | wrong_graph_two_step | 0.0000 | 0.0000 |
| 0 | 0 | joint_predictive | 0.0017 | 0.0159 |
| 0 | 0 | tv_gp_ucb | 0.0029 | 0.0137 |
| 0 | 0.9 | joint_greedy | 0.0185 | 0.0182 |
| 0 | 0.9 | independent_two_step | 0.0000 | 0.0000 |
| 0 | 0.9 | wrong_graph_two_step | 0.0000 | 0.0000 |
| 0 | 0.9 | joint_predictive | 0.1626 | 0.0152 |
| 0 | 0.9 | tv_gp_ucb | 0.4840 | 0.0155 |
| 0 | 0.99 | joint_greedy | 0.0790 | 0.0388 |
| 0 | 0.99 | independent_two_step | 0.0000 | 0.0000 |
| 0 | 0.99 | wrong_graph_two_step | 0.0000 | 0.0000 |
| 0 | 0.99 | joint_predictive | -0.0354 | 0.0271 |
| 0 | 0.99 | tv_gp_ucb | 0.3057 | 0.0264 |
| 2 | 0 | joint_greedy | 0.0011 | 0.0105 |
| 2 | 0 | independent_two_step | 0.0000 | 0.0000 |
| 2 | 0 | wrong_graph_two_step | 0.0000 | 0.0000 |
| 2 | 0 | joint_predictive | -0.0027 | 0.0121 |
| 2 | 0 | tv_gp_ucb | -0.0083 | 0.0118 |
| 2 | 0.9 | joint_greedy | 0.0516 | 0.0134 |
| 2 | 0.9 | independent_two_step | 0.0132 | 0.0115 |
| 2 | 0.9 | wrong_graph_two_step | 0.0273 | 0.0165 |
| 2 | 0.9 | joint_predictive | 0.1337 | 0.0166 |
| 2 | 0.9 | tv_gp_ucb | 0.3493 | 0.0174 |
| 2 | 0.99 | joint_greedy | 0.1218 | 0.0508 |
| 2 | 0.99 | independent_two_step | -0.0148 | 0.0257 |
| 2 | 0.99 | wrong_graph_two_step | 0.0578 | 0.0511 |
| 2 | 0.99 | joint_predictive | -0.0784 | 0.0339 |
| 2 | 0.99 | tv_gp_ucb | 0.1966 | 0.0360 |

## Limits

The rolling two-step rule is exact only with two reward periods remaining; its last-round action maximizes the current predictive mean. Joint predictive sampling uses the latent next field; no performance theorem is transferred automatically from published Predictive Sampling.
TV-GP-UCB uses the correct finite-domain Gaussian posterior and a specified confidence parameter delta=0.05; the bonus is not tuned. It is a baseline, not a claim to reproduce every convention in the original experiments.
The independent and wrong-graph rules use misspecified covariance models. At graph strength zero their two-step predictions coincide exactly with the correct model.
There is no mean learning, PCS experiment, AR(p) experiment, real traffic data, graph validation, hyperparameter learning, or general optimality benchmark in this experiment.
Sampling reduces variance at every location but can mostly reveal a shared fluctuation rather than a ranking-relevant contrast.

The separate exact-calculation checks passed 1636 assertions; see checks.json and the derivations in ../README.md.
