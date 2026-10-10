# UCB, Thompson-style sampling, and selection under spatial AR rewards

The [paper](manuscript.pdf) and [simulation code](../../experiments/spatiotemporal_policies.py) use fixed unknown means and known, stable AR filters. Gaussian parameter draws below are a randomized decision mechanism. They do not make the environment's means random, and their covariance is inverse penalized information rather than the repeated-noise sampling covariance of the estimator.

For each arm,

```math
X_{i,t}=\mu_i+z_{i,t},\qquad
z_{i,t}=\sum_{k=1}^{p_i}a_{i,k}z_{i,t-k}+\eta_{i,t},\qquad
\eta_t\overset{\mathrm{iid}}\sim N(0,Q_G).
```

Every arm advances each calendar round. The action is chosen before the current innovation or reading is seen. Only `Y_t = X_{a_t,t} + sensor_noise` is revealed. The supplied mean class is `||mu|| <= B` and `mu' L mu <= S^2`. Correlated innovations and graph-smooth means are separate assumptions.

## Objectives that need different policies

| Objective | Quantity | Interpretation |
|---|---|---|
| Current-state oracle regret | `sum_t [max_i X_i,t - X_a_t,t]` | Missed actual reward relative to seeing the entire current field. |
| Stationary mean pseudo-regret | `sum_t [max_i mu_i - mu_a_t]` | Cost of choosing inferior permanent locations. |
| Stationary mean reward regret | `T mu* - sum_t X_a_t,t` | Actual reward relative to the best permanent mean; can be negative. |
| Fixed best-mean-arm reward regret | `sum_t [X_b*,t - X_a_t,t]`, `b*=argmax mu` | Actual reward relative to operating the best permanent location on the same path. Can be negative. |
| PCS | `Pr(argmax_i muhat_i,T = b*)` | Repeated-noise terminal selection accuracy at the same fixed truth. |

The instantaneous oracle may select low-mean arms during positive shocks. Consequently even that oracle has positive *mean pseudo-regret*. A mean-regret policy and a current-reward policy optimize different quantities. We report both instead of treating them as interchangeable.

Writing `z_i,t = X_i,t - mu_i`, the expected actual fixed-arm regret satisfies

```math
\mathbb E R_{\mathrm{stationary}}(T)=\mathbb E R_{\mathrm{fixed}}(T)
=\mathbb E R_\mu(T)-\sum_t\mathbb E z_{a_t,t}.
```

The adaptive selected deviation need not average to zero; exploiting predictable positive shocks can give negative fixed-arm reward regret while mean pseudo-regret stays positive.

## A common likelihood engine

Stack the lag states into `s_t`, with `s_{t+1}=F s_t+E eta_{t+1}` and current selector `C`. Solve the stationary Lyapunov equation for `Gamma` and use `G_h=C F^h Gamma C'`. This retains all lags, including delayed and oscillatory correlations. Heterogeneous filters generally give asymmetric cross-covariance matrices at positive lags.

For observations before decision `t`, let `M` be the arm-selection matrix, `Xi` their noise covariance including sensor noise, and `Y` the readings. Put

```math
H=\alpha I+\lambda L,\quad
V=(H+M^\top\Xi^{-1}M)^{-1},\quad
m=VM^\top\Xi^{-1}Y.
```

For the whole current field, let `K=Cov(z_t, selected past deviations)`. Then

```math
A=K\Xi^{-1},\quad W=I-AM,\quad f=AY+Wm,
\quad P=G_0-K\Xi^{-1}K^\top.
```

`f` is the plug-in forecast. At the true fixed mean, the conditional expected field is `AY+W mu` and the conditional noise covariance is `P`. Define the *working* Gaussian uncertainty

```math
\Sigma=P+WVW^\top,\qquad B_\mathrm{cross}=VW^\top.
```

This is also the covariance from a Gaussian penalized-likelihood integration, but it is not a calibrated frequentist prediction interval by itself. Its useful role here is to define randomized policies and one-step information gains. The all-time confidence theorem in the paper handles mean estimation error, including smoothing bias, separately.

Adding a reading at arm `a` reduces `V` by

```math
V^+=V-\frac{(VW_a^\top)(W_aV)}{P_{aa}+r+W_aVW_a^\top}.
```

For a permanent comparison `c=e_b-e_j`, its inverse-information reduction is

```math
g_t(c,a)=\frac{(c^\top B_{\mathrm{cross},:,a})^2}{\Sigma_{aa}+r}.
```

A measurement of a third arm can maximize this score. Its covariance can help remove a shared shock while the graph couples the permanent mean estimates. The reduction is exact for inverse regularized information; it is not an exact reduction in frequentist PCS.

The implementation uses the selected-history Schur inverse to compute these expressions exactly. It does not truncate AR memory or discard spatial cross-covariances. History storage costs `O(T^2)`, all-arm forecasts cost `O(N t^2)` per decision, and a selected update costs `O(t^2+N^2)`. A joint state filter is an alternative with state size `sum_i p_i`; neither representation is a constant-cost solution for arbitrarily large problems.

## UCB policies

For permanent means, choose

```math
a_t=\arg\max_i\{m_i+c_t\sqrt{V_{ii}}\}.
```

The practical experiment uses `c_t=0.7 sqrt(2 log(t+2))`. A separate certified version replaces `c_t` by

```math
\beta_t(\delta)
=\sqrt{\log\frac{\det(H+\mathcal I_{t-1})}{\det H}+2\log(1/\delta)}
+\sqrt{\alpha B^2+\lambda S^2}.
```

Only the latter inherits the paper's fixed-mean confidence theorem. Graph regularization enters its estimate, its coordinate width, and its bias allowance.

For current rewards, the full-variance version chooses `argmax_i {f_i+c_t sqrt(Sigma_ii)}`. A more targeted version uses

```math
a_t=\arg\max_i\{f_i+c_t\sqrt{(\Sigma-Q_G)_{ii}}\}.
```

The subtraction has a precise meaning: `z_t=CF s_{t-1}+eta_t`, and current `eta_t` is independent of the entire past. Therefore `P-Q_G` is the conditional covariance of the predictable state contribution and is positive semidefinite. Exploration can learn means and past state, but cannot reveal the current innovation before choosing an arm. With zero temporal dependence this predictive score reduces to a mean score, as it should.

Both practical state versions are tuned heuristics. A conservative certified current-field upper bound instead uses

```math
f_i+\beta_t\sqrt{W_iVW_i^\top}+\kappa_t\sqrt{P_{ii}},
\qquad \kappa_t=\sqrt{2\log(2\pi^2Nt^2/(3\delta))}.
```

Use the mean confidence event with failure probability `delta/2`. A two-sided Gaussian tail union bound over arms and times spends the remaining `delta/2`. Selecting the largest certified upper bound gives a pathwise oracle-regret bound by twice the sum of the selected widths. That bound is generally linear or looser, because `P >= Q_G`. It does not identify the optimal linear coefficient, and this conservative state rule is not one of the tuned experiment policies.

### A proved mean-regret bound

Let `v_-` and `v_+` be the uniform lower and upper eigenvalue bounds for every selected observation covariance from the paper's AR spectral argument. After an initial sample of each arm,

```math
V_{ii}\le v_+/N_i(t-1).
```

On the all-time confidence event, a non-forced certified mean-UCB action satisfies `mu* - mu_a <= 2 beta_t sqrt(V_aa)`. Summing reciprocal square-root counts gives

```math
R_\mu(T)\le 2B F_T+4\beta_T\sqrt{v_+NT},
```

where `F_T` counts forced observations and

```math
\beta_T\le\sqrt{N\log(1+T/(\alpha v_-))+2\log(1/\delta)}
+\sqrt{\alpha B^2+\lambda S^2}.
```

This is sublinear for fixed stable dynamics and fixed `N`. It is a conservative bound, not a sharp dependence on graph geometry or AR coefficients. The square-root probe schedule below gives `F_T <= N+sqrt(T)`; the additive forced cost is also sublinear. For an expectation bound add `2BT delta`, or choose a horizon-dependent `delta=1/T`.

The argument does **not** automatically give a Thompson regret theorem: the whitened information vector `W_a/sqrt(P_aa+r)` differs from the physical reward coordinate `e_a`. Standard linear Thompson results require their own conditions and proof. [Abeille and Lazaric (2017)](https://proceedings.mlr.press/v54/abeille17a.html) motivates randomized optimistic decisions, rather than certifying the new dynamic policy.

## Thompson-style policies

Mean Thompson-style sampling draws

```math
\widetilde\mu=m+\tau V^{1/2}\xi,\quad\xi\sim N(0,I),\qquad
a_t=\arg\max_i\widetilde\mu_i.
```

The current-state version draws `f+tau Sigma^(1/2) xi`. The predictive-state version draws `f+tau (Sigma-Q_G)^(1/2) xi`. All joint draws preserve cross-arm covariance. The experiment fixes `tau=1` for all configurations.

The predictive version samples uncertainty in the current conditional reward given complete past states, integrating the uncertainty about those states and the unknown means. It omits a fresh innovation that is irrelevant to a pre-observation choice. It is a one-step heuristic, not the full future-information algorithm of [Liu, Van Roy, and Xu (2023)](https://proceedings.mlr.press/v206/liu23e.html), and not a solved restless-bandit control problem. A decision can still have value at later lags that a one-step rule undervalues.

## PCS-oriented policies

Both rules below recommend the largest estimated **permanent mean**, not the largest last reward or forecast.

1. **Contrast LUCB:** use the estimated best mean `b`; choose the challenger maximizing `m_j-m_b+c_t sqrt((e_b-e_j)'V(e_b-e_j))`; then measure the arm maximizing `g_t(e_b-e_j,a)`.
2. **Top-two Thompson contrast design:** draw a plausible best mean `b` from the correlated Gaussian perturbation; redraw until another winner `j` appears, with a cap of 64 draws and the LUCB challenger as fallback; then maximize the same contrast gain.

The second adapts the idea of sampling plausible competing winners from [Russo (2016)](https://proceedings.mlr.press/v49/russo16.html). It can observe a third arm, has correlated uncertainty and evolving experiments, and is not the standard top-two Thompson algorithm. Published asymptotic optimality results do not transfer automatically.

The allocation depends on the state and all observations. No finite-budget PCS optimum is claimed. The fixed-confidence stopping certificate from the paper remains available when supplied assumptions hold. The simulations make forced terminal decisions and report empirical PCS, not a guaranteed target PCS.

## Coverage, comparisons, and reproducibility

All learning rules first observe every arm. Thereafter, at square ages `t-N+1=k^2`, they observe arm `(k-1) mod N`. These `O(sqrt(T))` probes eventually give every arm `Omega(sqrt(T)/N)` readings while their fraction vanishes. Combined with correct likelihood and fixed bounds, this makes mean confidence widths shrink and gives consistent selection at a positive gap. Round robin retains its strict cyclic schedule. The iid and independent-temporal baselines do not inherit the joint-model theorem under correlated innovations.

The 100-arm experiments use a 10-by-10 grid, a fixed two-peak mean surface with gap 0.20, and stationary marginal deviation variance one. Every arm has an AR(20) process. Five configurations isolate dense persistent filters, weak filters, lag-20 dependence, three heterogeneous filters, and independent spatial innovations. Sensor variance is 0.09; `H=0.1 I+0.5 L`; the supplied bounds `B=6` and `S=3` contain the same fixed truth in every configuration. Full parameter matrices and coefficient vectors are recorded in metadata.

Learning comparisons include naive iid UCB/TS, independent per-arm AR state UCB/TS, joint mean UCB/TS, certified mean UCB, full-variance and predictive-variance joint state UCB/TS, the two selection designs, and round robin. All see only the selected reading. Each replicate shares latent paths and potential sensor noises across policies; policy randomization has a reproducible separate seed.

Four benchmarks expose different information limits:

- Best-mean arm: knows `mu`, always observes its best coordinate.
- Known-mean greedy filter: knows `mu`, gets only selected readings, maximizes the filtered current forecast. It is a benchmark, not an optimal causal policy or a lower bound on all learners.
- Full-past-state genie: knows `mu` and every arm's complete past lag state, chooses the largest current conditional mean. It still lacks the current innovation.
- Full-current-state oracle: knows every current latent reward and earns their maximum.

For stationary initialization, the full-past genie attains the expected coefficient

```math
\mathcal G(\mu,G_0)-\mathcal G(\mu,G_0-Q_G),\qquad
\mathcal G(\mu,K)=\mathbb E\max_i(\mu_i+Z_i),\quad Z\sim N(0,K).
```

This is a lower bound for causal regret against the current-state oracle. We estimate the expectation separately by paired Gaussian Monte Carlo, and show the sampled genie as a check. Learner excess above the floor reflects missing past states and unknown means as well as imperfect control. A declining finite-horizon ratio is not proof of an asymptotic optimal coefficient.

See the [results](results/policies_ar20/findings.md), raw [paired runs](results/policies_ar20/runs.jsonl), [metadata](results/policies_ar20/metadata.json), and [checks](results/policies_ar20/checks.json).

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  .venv/bin/python -I experiments/spatiotemporal_policies.py --verify
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  .venv/bin/python -I experiments/spatiotemporal_policies.py --runs 32 --horizon 1000 --jobs 4
MPLCONFIGDIR=/private/tmp/dependent-mab-mpl OPENBLAS_NUM_THREADS=1 \
  .venv/bin/python -I experiments/spatiotemporal_policies_analysis.py
```
