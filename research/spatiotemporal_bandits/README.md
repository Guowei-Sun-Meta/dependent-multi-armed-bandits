# Fixed graph-smooth means with correlated AR(p_i) innovations

The [standalone paper](manuscript.pdf) and [LaTeX source](manuscript.tex) extend the [general autoregressive development](../ar_p_bandits/README.md) to spatially correlated innovations. **Each mu_i is a fixed unknown constant.** No Gaussian distribution for the means is assumed.

## Physical model and two graph roles

For arm i:

```math
X_{i,t}-\mu_i
=\sum_{k=1}^{p_i}a_{i,k}(X_{i,t-k}-\mu_i)+\eta_{i,t},
\qquad \eta_t\stackrel{\mathrm{iid}}{\sim}N(0,Q_G).
```

AR orders and coefficients may differ across arms. Their polynomials are stable and known. All arms evolve every calendar round; one selected coordinate is measured. Innovation vectors are independent across time but their coordinates are spatially correlated through Q_G. Independent sensor noise can be added.

There are two separate assumptions:

- **Spatially correlated shocks:** Q_G describes shared random deviations. It may be a graph covariance such as a rescaled inverse of alpha_eta I + lambda_eta L.
- **Graph-smooth fixed means:** mu^T L mu <= S^2 restricts permanent differences. This is a deterministic assumption, not a covariance or probability distribution for mu.

Correlated shocks alone do not imply similar means. If only innovation correlation is justified, set the mean Laplacian penalty to zero while retaining the joint likelihood.

The raw AR intercept is (1 - sum_k a_i,k) mu_i; it is not generally mu_i.

## Covariance and mean estimation

Stack each arm's current deviation and lags into a joint state. With companion transition F, innovation insertion E, and current selector C:

```math
s_{t+1}=Fs_t+E\eta_{t+1},\qquad
\Gamma=F\Gamma F^\top+EQ_GE^\top,\qquad
G_h=CF^h\Gamma C^\top.
```

The lag covariance matrices combine spatial innovations with all AR coefficients. Heterogeneous dynamics generally give nonseparable node-time covariance; one temporal persistence factor is insufficient.

For a recorded schedule, let M select observed arms and Xi be its trajectory covariance:

```math
\widehat\mu=(M^\top\Xi^{-1}M+H)^{-1}M^\top\Xi^{-1}Y.
```

H is a deterministic penalty. Lambda L leaves the common offset unpenalized; alpha I + lambda L is proper and used in adaptive confidence. Inverse regularized information is not the frequentist sampling covariance. The paper derives smoothing bias and sampling variance separately.

A hard constraint on the estimate's energy literally enforces a supplied radius, with an active multiplier found by scalar search. Neither a penalty nor a constrained estimate verifies the radius at the truth.

## Results in the revised paper

- Exact joint lag-state covariance and an impulse-response expression for cross-location, cross-time dependence.
- Fixed-design graph GLS bias and variance, plus energy-constrained mean estimation.
- A conditional lag-state filter converting adaptive readings into predictable Gaussian experiments about fixed mu.
- All-time confidence and correct stopping under supplied mean-norm and energy bounds, known dynamics, and correct innovation covariance. Forced probes ensure eventual termination.
- A contrast-information heuristic and exact future-state variance reductions using F^h, without general finite-budget policy optimality.
- Fixed-truth PCS formulas for fixed Gaussian designs and an exact correlated AR(2) schedule comparison.
- General full-field information I_n = I_p + (n-p) D_c Q_G^-1 D_c, and long-run covariance D_c^-1 Q_G D_c^-1, with c_i = 1 - sum_k a_i,k.
- An adaptive KL identity and an innovation-based linear regret floor against an oracle seeing all current states.
- Objective-specific mean and state UCB/Thompson-style rules, with spatially correlated uncertainty draws and two PCS-oriented contrast designs.
- A conservative sublinear stationary mean-regret theorem for certified mean UCB, distinct from the unavoidable linear current-state-oracle regret.

## UCB, Thompson sampling, and 100-arm AR(20) experiments

The [policy derivations](policies.md) distinguish permanent means, predictable current states, and fresh innovations. All arms evolve every calendar round. The exact joint likelihood retains heterogeneous AR filters and spatial innovation covariance. Thompson-style Gaussian draws represent algorithmic uncertainty about a fixed truth, not a randomly generated mean population.

The [new executable study](../../experiments/simulations/theory/spatiotemporal/spatiotemporal_policies.py) compares 14 learning policies and four information benchmarks on 100 arms, AR(20), five dependence configurations, and 32 paired independent noise worlds per configuration. Each world has 1,000 decisions, including initial coverage. The configurations include persistent, weak, lag-20, heterogeneous, and independent-innovation processes. Practical policy scales are fixed across configurations.

The [findings](results/policies_ar20/findings.md), [summary](results/policies_ar20/summary.csv), [paired comparisons](results/policies_ar20/paired.csv), and [figures](results/policies_ar20/oracle_regret.pdf) report:

- Current-state-oracle regret and its estimated irreducible innovation coefficient.
- Stationary mean pseudo-regret and actual reward regret against T times the best permanent mean.
- Actual reward regret against always operating the best permanent arm, which can be negative.
- Fixed-truth PCS, simple regret, and mean estimation MSE.

Continuous-metric intervals use independent noise worlds; PCS uses Wilson intervals. The theory covers the certified mean-UCB policy under supplied bounds and known correct dynamics. The tuned state and selection rules remain heuristics; no general optimality or fixed-budget PCS target is claimed. The [analysis code](../../experiments/simulations/theory/spatiotemporal/spatiotemporal_policies_analysis.py) checks paired-result completeness and counterfactual regret bookkeeping. The separate [numerical checks](results/policies_ar20/checks.json) contain 642 assertions against dense Gaussian likelihood and independent state calculations.

Use the workspace scientific environment or the [recorded dependencies](../../experiments/simulations/theory/spatiotemporal/requirements.txt):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  .venv/bin/python -I experiments/simulations/theory/spatiotemporal/spatiotemporal_policies.py --verify
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  .venv/bin/python -I experiments/simulations/theory/spatiotemporal/spatiotemporal_policies.py --runs 32 --horizon 1000 --jobs 4
MPLCONFIGDIR=/private/tmp/dependent-mab-mpl OPENBLAS_NUM_THREADS=1 \
  .venv/bin/python -I experiments/simulations/theory/spatiotemporal/spatiotemporal_policies_analysis.py
```

## Illustrative AR(2) result

Take z_i,t = a z_i,t-2 + eta_i,t, with marginal stationary variance V and innovation correlation rho. Odd-lag correlations vanish; even-lag correlations persist.

For four calendar samples:

| Schedule | GLS variance of the estimated mean difference |
|---|---|
| AABB | V + r - a rho V |
| ABAB | V + r + a V |

For a positive fixed gap Delta, PCS is Phi(Delta / sqrt(variance)). At V=1, r=0.1, a=0.8, rho=0.6, and Delta=0.4, AABB gives PCS **0.6943**, versus **0.6142** for ABAB.

Block sampling avoids redundant same-arm readings at lag two and accesses shared shocks that cancel in the comparison. This strictly compares two designs; it does not prove a universally optimal adaptive policy.

## Position relative to existing research

| Literature | Distinction developed here |
|---|---|
| [Spectral bandits](https://proceedings.mlr.press/v32/valko14.html) and [graph pure exploration](https://papers.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html) | Fixed graph-smooth means, with correlated general-AR observation likelihoods replacing independent samples. |
| [Time-varying GP bandits](https://proceedings.mlr.press/v51/bogunovic16.html) | Separate fixed permanent means from the evolving field and retain heterogeneous lag structure. |
| [Shared linear Gaussian bandits](https://proceedings.mlr.press/v242/gornet24a.html) | Specialize this established state-space family to graph-constrained fixed means and comparison confidence. |
| [Graph ARMA reconstruction](https://doi.org/10.1109/TSP.2023.3329948) | Put spatial correlation in innovations, allow heterogeneous node filters, and target adaptive selection. |
| [Correlated-normal knowledge gradient](https://doi.org/10.1287/ijoc.1080.0314) | Use a deterministic mean class and frequentist contrast information instead of a mean-prior selection objective. |

Publication priority for the specialized results is not established. General optimal allocation, matching bounds, graph validation, and unknown dynamics remain open.

## Evidence and reproduction

Use the [executable study](../../experiments/simulations/theory/spatiotemporal/graph_ar_mean.py), [findings](results/general_ar/findings.md), [summary](results/general_ar/summary.csv), [paired comparisons](results/general_ar/paired.csv), [metadata](results/general_ar/metadata.json), and [checks](results/general_ar/checks.json).

The experiment uses six arms, 60 samples, seven policies, and 200 paired independent noise trajectories per configuration. Means are fixed across runs. Dynamics include lag-two AR(2), oscillatory AR(2), and heterogeneous AR(2)/AR(3). The iid model is a misspecification baseline.

The revised script passes **1,525 assertions**, including independent dense likelihood, impulse-response covariance, full-field information, and AR(2) design checks. A separate 30,000-trajectory fixed-mean simulation checks the PCS formulas.

All audited graph-policy trajectories satisfy the conservative confidence bound; no terminal certificate passes at budget 60. Reported fixed-budget decisions are uncertified. A contrast rule can improve selection loss while a fixed schedule gives smaller overall estimation MSE; performance depends on the objective and configuration.

```sh
python3 experiments/simulations/theory/spatiotemporal/graph_ar_mean.py --verify
python3 experiments/simulations/theory/spatiotemporal/graph_ar_mean.py --runs 200 --budget 60
python3 experiments/simulations/theory/spatiotemporal/graph_ar_mean.py --render-only
cd research/spatiotemporal_bandits
tectonic --only-cached --keep-logs manuscript.tex
```

The [superseded manuscript](archive/common_ar1/manuscript.pdf), [historical overview](archive/common_ar1/overview.md), and [earlier experiment](results/mean_selection/findings.md) remain for provenance. Their common-order-one Bayesian results are not claims of this paper.
