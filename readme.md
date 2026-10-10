# Dependent Bandits

this is to pick up the research idea we had during graduate school: a traditional multi-armed bandits problem deals with independet rewards. What if we can introduce dependency?

There are two types of dependencies:
1. Within-arm dependency. What if each sample is not drawn from an iid distribution, what if it is drawn from a time series process such as an ARIMA process where the reward distribution at time t, is dependent on previous rewards at times t-1, .., 0. In the case of rewards being Markovian, then reward at time t is only dependent on rewards realized at time t-1
2. Cross-arm dependnecy. What if arms {a1,...ak} are not independent, what if say a1 and a2 are "closer" than a1 and ak, and the correlation can be modeled via a Gaussian process, where the mean values of rewards for ai,aj can be modeled with correlation determined by a distance function dij?

Under the two types of dependency, how would the optimal policy of reducing regret change? Do some research and evaluate the value of the idea.

## Extended research collection, 9 October 2026

The [long manuscript](research/gpt_sol_10_09/manuscript.pdf) integrates the graph and temporal theory, UCB and Thompson-style policies, selection formulas, controlled experiments, and KuaiRec findings, with five full technical appendices. The [package overview](research/gpt_sol_10_09/README.md) links source evidence and reproduction commands. A [completed Wikipedia experiment](research/gpt_sol_10_09/results/wikipedia/findings.md) adds two historical-graph attention panels with general AR(7)/AR(20) models, one- and five-reading budgets, and topology controls, using about three minutes and 167 MB of laptop compute.

## Temporal dependence and predictive rewards

The [temporal-bandit research map](research/temporal_bandits.md) reviews autoregressive and Markovian bandits, distinguishes rested and restless evolution, and compares regret against fixed arms, causal policies, and full-state oracles. It develops an AR(1) starting model with separate parameter and prediction uncertainty, including the effects of observation age and sampling gaps. A [formula illustration](research/temporal_information.svg) shows how persistence preserves forecasts while reducing the information in consecutive samples about the mean.

The [predictive AR(1) study](research/predictive_ar1/README.md) develops an exact Gaussian Predictive Sampling policy and targets the coefficient of linear regret against an oracle seeing all current states. It includes proved lower and constructive upper bounds, a two-step control comparator, and reproducible simulations.

## Graph alignment and cumulative regret

The revised [working research manuscript](research/alignment_paper/manuscript.pdf) develops graph-specific information complexity, resistance-based observation designs, a policy with finite-time regret bounds, and an explicit price for certified graph errors. Its central result compares paths and cliques with identical reward means, energy budgets, and resistance diameters: endpoint observations can reject a path component, while the clique class requires arm-wise exploration. Its [overview](research/alignment_paper/README.md) explains the results and limitations; the [LaTeX source](research/alignment_paper/manuscript.tex) includes the proofs and references.

The central question is how accurately the graph restricts competing reward vectors, relative to gaps from the best arm. Ranking preservation alone does not guarantee lower regret, and component widths can lose useful graph geometry. The manuscript includes reproducible comparisons and an invalid-certificate stress test. It distinguishes its proved statements from unresolved questions about publication novelty, optimal leading constants, and online graph validation; the [novelty audit](research/alignment_paper/novelty_audit.md) records that boundary.

## Spatial and temporal dependence in permanent-mean selection

The [standalone spatial/general-AR paper](research/spatiotemporal_bandits/manuscript.pdf) uses fixed unknown graph-smooth means and heterogeneous AR(p_i) deviations with spatially correlated innovations. It develops joint lag-state likelihoods, graph estimation, adaptive confidence and stopping, comparison and prediction information, and an exact AR(2) schedule comparison. The [overview](research/spatiotemporal_bandits/README.md) separates the deterministic mean restriction from innovation covariance; [the experiments](research/spatiotemporal_bandits/results/general_ar/findings.md) hold means fixed across repeated-noise runs under AR(2) and mixed AR(2)/AR(3) dynamics.

The [UCB and Thompson-style policies](research/spatiotemporal_bandits/policies.md) target permanent mean regret, predictable current reward, or terminal PCS. The [100-arm AR(20) study](research/spatiotemporal_bandits/results/policies_ar20/findings.md) compares five dependence configurations with paired uncertainty, current-state-oracle regret, stationary mean pseudo-regret, and actual reward relative to the best permanent arm. The paper proves a conservative sublinear mean-regret bound for certified UCB; current-state-oracle regret retains an irreducible linear innovation term.
