# Multiple arms with heterogeneous AR orders

Working derivations, 9 October 2026. This extends the [two-arm AR(1) note](../two_arm_ar1/README.md). To avoid its overloaded `K`, use **L arms** and **T total observations**: `i=1,...,L`, with arm i following AR(`p_i`). Thus L is the number of arms in the current request. Unless stated otherwise, all arms evolve every calendar round and one exact current reward is observed per round.

Full statements and proofs: [manuscript.tex](manuscript.tex), [PDF](manuscript.pdf). Reproducible calculations: [script](../../experiments/ar_p_extension.py), [findings](results/findings.md), [saved checks](results/checks.json).

## What extends, and what changes

| Result | Extension | Scope |
|---|---|---|
| Gaussian beliefs and likelihood information | Exact matrix formulas for arbitrary stable AR orders and sampling schedules | Known AR coefficients and innovation variances; stationary initialization |
| Two-period reward policy | Explicit action score for any number of independent Gaussian arms | Exact with two rounds remaining; repeated use is a rolling approximation |
| Predictive Sampling | A finite future-vector Gaussian score | Known means and dynamics; future length p_i rather than one |
| Full-state oracle regret bounds | Explicit innovation lower bound and constructive refresh upper bound for heterogeneous AR arms | Upper bound uses complete lag-state probes; does not establish a sharp optimal coefficient |
| Multi-arm PCS | Exact one-dimensional integral for a fixed schedule, and for posterior best probabilities | The PCS-maximizing Bayesian recommendation can differ from the largest posterior mean |
| Homogeneous AR(1) round-robin | Optimal total information and posterior mean-square estimation error | T divisible by L; not generally PCS optimal when L>=3 |
| Consecutive local AR(p_i) streams | Exact affine mean information after p_i observations | Rested clock; supports exact finite-budget variance allocation |
| Multi-arm mean identification allocation | Optimal fixed-proportion error exponent, with a one-dimensional root | Rested streams; true means/gaps supplied for this allocation benchmark; not a general finite-T adaptive theorem |

Two important obstructions are proved below: balanced sampling ceases to be generally Bayes-PCS optimal with three arms, even for iid rewards; and the latest observation alone ceases to summarize prediction for AR orders above one.

## Model and Gaussian state

Assume independent Gaussian innovations and stable known dynamics:

```math
X_{i,t}-\mu_i=\sum_{r=1}^{p_i}a_{i,r}(X_{i,t-r}-\mu_i)+\eta_{i,t},
\qquad \eta_{i,t}\sim N(0,q_i),\quad q_i>0.
```

Stability means the companion matrix F_i has spectral radius below one. For
`Z_i,t=(X_i,t-mu_i,...,X_i,t-p_i+1-mu_i)` and first coordinate vector e_i,

```math
Z_{i,t+1}=F_iZ_{i,t}+e_i\eta_{i,t+1},\qquad
\Gamma_i=F_i\Gamma_iF_i^\top+q_ie_ie_i^\top.
```

Initialization is stationary conditional on the means. Define marginal variance `V_i=e_i^T Gamma_i e_i` and autocovariance `gamma_i(h)=e_i^T F_i^|h| Gamma_i e_i`.

For known means, maintain `Z_i,t | H_t ~ N(z_i,P_i)` before the decision. A scalar observation x gives

```math
k_i=\frac{P_ie_i}{e_i^\top P_ie_i},\qquad
z_i^+=z_i+k_i(x-\mu_i-e_i^\top z_i),\qquad
P_i^+=P_i-\frac{P_ie_ie_i^\top P_i}{e_i^\top P_ie_i}.
```

Propagate every arm using `z_i <- F_i z_i`, `P_i <- F_i P_i F_i^T + q_i e_i e_i^T`, after using the selected arm's posterior. An observation updates the whole latent lag vector. Older observations can still inform unobserved lags after the latest scalar state has been observed.

For an unknown Gaussian mean, append mu_i as a static state. In raw lag coordinates the augmented transition is

```math
A_i=\begin{pmatrix}1&0\\c_ie_i&F_i\end{pmatrix},\qquad
c_i=1-\sum_ra_{i,r}.
```

The observation reads the current reward coordinate, and standard Gaussian conditioning remains exact. This separates mean uncertainty from state uncertainty without discarding either.

## Prediction value and an exact two-period reward rule

At a belief, let current mean `m_i=mu_i+e_i^T z_i`, current variance `v_i=e_i^T P_i e_i`, next-round mean `ell_i=mu_i+e_i^T F_i z_i`, and

```math
c_{i,s}=e_i^\top F_i^sP_ie_i.
```

Observing this arm now reduces its future state variance at horizon s by exactly `c_i,s^2/v_i`. The full covariance sequence, not a single persistence coefficient, determines predictive value.

Let `w_i=|c_i,1|/sqrt(v_i)`, `C_i=max_{j!=i} ell_j`, and `g(d,s)=s varphi(d/s)-d Phi(-d/s)`. The exact two-period reward score is

```math
\boxed{Q_i=m_i+\max(\ell_i,C_i)+g(|\ell_i-C_i|,w_i).}
```

Choose the largest score. It reduces to the earlier AR(1) result. The same Gaussian-regression form applies to augmented unknown-mean states using the current/next reward projections. General finite-horizon reward optimization retains a Bellman recursion, rather than this two-period score at every horizon.

For L homogeneous zero-mean arms, the initial two-pull regret also has a closed form:

```math
R_2^*=2\sqrt V\,M_L-\frac{|\gamma(1)|}{\sqrt{2\pi V}},\qquad
M_L=\mathbb E\max_{i\le L}Z_i,\quad Z_i\stackrel{\mathrm{iid}}\sim N(0,1).
```

After observing x on the first arm, repeat it when `gamma(1) x >= 0`; otherwise choose an unobserved arm. Negative lag-one correlation reverses the sign rule.

## Predictive Sampling for AR(p_i)

For known means and dynamics, the first p_i future states
`Y_i=(X_i,t+1,...,X_i,t+p_i)` screen the current state from the rest of that arm's future. Let `c_i=Cov(Y_i,X_i,t | H_t)` and `Omega_i=Var(Y_i | H_t)`. Then the exact predictive score is

```math
\boxed{\widetilde X_i\sim N(m_i,c_i^\top\Omega_i^{-1}c_i).}
```

Draw independently across arms and select the largest score. At p_i=1 this becomes the earlier `phi_i^2 v_i^2/(phi_i^2 v_i+q_i)` formula. The result specializes published Predictive Sampling; it is not an optimal-policy theorem. With unknown means, the finite future vector alone does not screen information about the mean in the remaining infinite future, so the stated formula requires known means.

For `X_t=.8 X_t-2+eta_t`, the current observation tells us nothing about the next reward, but does predict the reward two rounds later. One future state would incorrectly assign zero predictive information; the two-state score retains it.

## Regret against the full-current-state oracle

Let independent Z_i be standard normal and define

```math
G=\mathbb E\max_i(\mu_i+\sqrt{V_i}Z_i),\qquad
G_{\mathrm{past}}=\mathbb E\max_i(\mu_i+\sqrt{V_i-q_i}Z_i).
```

An observer seeing the complete past lag vectors knows the current reward up to its fresh innovation. It is stronger than the actual learner, so every causal policy satisfies

```math
\boxed{R_T^\pi\ge T(G-G_{\mathrm{past}}).}
```

For L>=2 and positive independent q_i, the gap is strictly positive. With common zero mean, V, and q, the coefficient lower bound becomes `M_L [sqrt(V)-sqrt(V-q)]`. Dependence enters through the dynamics' stationary variance and innovation variance; this bound does not resolve the extra monitoring cost or prove a sharp coefficient.

For a constructive upper bound with known common mean zero, let `B=sum_i p_i`. In each period of H>=B rounds, observe each arm for p_i consecutive rounds to reconstruct its complete lag state, then exploit the largest predictive mean. Its coefficient satisfies

```math
\boxed{c_{\mathrm{refresh}}\le\frac BH G+
\left(1-\frac BH\right)\sqrt{2u_H\log L},\qquad
u_H=\max_iq_i\sum_{r=0}^{H-1}(e_i^\top F_i^re_i)^2.}
```

The cost of a sweep depends on the sum of the AR orders; subsequent uncertainty growth depends on the impulse responses. Combining this family with a fixed-arm policy gives `G-G_past <= c* <= min(G, inf_H refresh_bound(H))`. These are explicit bounds, with no matching or optimal-policy claim.

## Exact likelihood information and PCS

If arm i is observed at fixed times `t_i,1,...,t_i,n`, form

```math
\Sigma_i[r,s]=\gamma_i(t_{i,r}-t_{i,s}).
```

The exact mean information and estimator are

```math
\boxed{I_i=\mathbf1^\top\Sigma_i^{-1}\mathbf1,\qquad
\widehat\mu_i=I_i^{-1}\mathbf1^\top\Sigma_i^{-1}Y_i.}
```

Fixed schedules give independent `mu_hat_i ~ N(mu_i,sigma_i^2)` with `sigma_i^2=1/I_i`. If b is the unique true best mean and `Delta_i=mu_b-mu_i`, selecting the largest estimate yields

```math
\boxed{\mathrm{PCS}
=\int_{-\infty}^{\infty}\varphi(z)
\prod_{i\ne b}\Phi\left(\frac{\Delta_i+\sigma_bz}{\sigma_i}\right)\,dz.}
```

This is one-dimensional even with many arms. It reduces to the two-arm Gaussian CDF. It does not say that an arbitrary adaptive estimate has the fixed-schedule Gaussian distribution.

Under independent Gaussian priors with means `m_i0` and variances `tau_i^2`, conditioning on a complete adaptive history gives independent Gaussian mean posteriors with variance `(tau_i^-2+I_i(H))^-1`. Selection probabilities add no mean-dependent likelihood term. In the script, a Kalman innovation calculation independently verifies the dense covariance information formula.

For posterior means M_i and variances s_i^2, the probability that arm i is best is

```math
p_i(H)=\int\varphi(z)\prod_{j\ne i}
\Phi\left(\frac{M_i-M_j+s_iz}{s_j}\right)\,dz.
```

The PCS-optimal terminal decision maximizes p_i, which need not maximize M_i. For means `(.1,0,-.2)` and variances `(.04,.04,4)`, the best probabilities are approximately `(.36737,.20572,.42691)`: the third arm has the highest best probability despite its smaller mean.

## A many-arm theorem that survives for homogeneous AR(1)

For common positive persistence and variance, and T divisible by L, strict round-robin achieves per-arm information

```math
I_*^{(L)}=\frac{1+(T/L-1)(1-\phi^L)/(1+\phi^L)}V.
```

There are T-L within-arm gaps when all arms are observed. Their total length is at most L(T-L), giving the pathwise bound

```math
\sum_iI_i\le L I_*^{(L)}.
```

It also holds if fewer arms are observed, by applying the same bound to the observed arm count. Round-robin attains it with equal information. Hence it minimizes total GLS estimation variance, maximum estimation variance, and covariance determinant over fixed schedules observing all arms.

With independent equal Gaussian priors, it also minimizes prior-averaged total squared mean-estimation error among adaptive policies: the conditional Bayes risk is the sum of posterior variances, which is bounded below pathwise by `L/(tau^-2+I_*^(L))`. **These estimation criteria are not PCS.**

## Why balanced Bayes-PCS optimality fails with three arms

Take three iid Gaussian arms with independent N(0,1) mean priors, observation variance one, and total budget three. Observe arms 1 and 2 first. Consider a history with posterior means `(a,a,0)` and variances `(1/2,1/2,1)`.

As a becomes large, arm 3 is almost certainly not best. Spending the last sample on arm 3 leaves the close contest between arms 1 and 2 unresolved, and optimal conditional PCS tends to 1/2. Resampling arm 1 reduces the posterior difference variance from 1 to 5/6, giving the limiting PCS

```math
\frac12+\frac1\pi\arcsin\sqrt{1/6}\approx0.633860.
```

Continuity gives a positive-probability region of strict improvement. A policy that resamples only when this improves conditional PCS, and otherwise observes arm 3, strictly beats balanced one-observation-per-arm sampling in prior-averaged PCS. This is a proof of failure of a universal balanced-policy extension, rather than an optimality claim for a particular heuristic. The [numerical table](results/findings.md) illustrates the limiting argument.

## Why AR(1) schedule and freshness results fail for AR(2)

Consider `X_t-mu = a (X_t-2-mu)+eta_t`, 0<a<1, with stationary variance V. Its odd-lag autocovariances are zero; `gamma(2r)=a^r V`.

Two consecutive observations provide information `2/V`, while a gap of two gives `2/[V(1+a)]`. Information per observation gap is therefore neither monotonically increasing nor the AR(1) concave gap function. At budget four, `AABB` provides more mean information than `ABAB` on both arms.

For next-state selection at round five, even-time observations are independent of the odd-time target, conditional on the known means. `AABB` observes the two different arms at the useful times one and three and has posterior difference variance `V(2-a^2-a^4)`. `BABA` observes the same arm at both useful times and has variance `V(2-a^2)`, although its last two actual observations are on different arms. Thus an older informative observation can dominate a fresher one; the last-two-different-arms rule does not extend.

## Exact information in separate simulation streams

For consecutive local observations of an AR(p_i) arm, define

```math
c_i=1-\sum_ra_{i,r},\qquad
\kappa_i=\frac{q_i}{c_i^2},\qquad
A_i=\mathbf1^\top\Sigma_{i,p_i}^{-1}\mathbf1,
\qquad \beta_i=\kappa_i A_i-p_i.
```

Here kappa_i is the long-run variance and Sigma_i,p_i is the stationary covariance of the first p_i observations. Initial observations supply A_i; every subsequent AR innovation supplies `c_i^2/q_i`. Thus, exactly for n_i>=p_i,

```math
\boxed{I_i(n_i)=A_i+(n_i-p_i)\frac{c_i^2}{q_i}
=\frac{n_i+\beta_i}{\kappa_i}.}
```

For two arms, minimizing comparison variance `kappa_1/(n_1+beta_1)+kappa_2/(n_2+beta_2)` yields the continuous solution

```math
n_i^*=\frac{\sqrt{\kappa_i}}{\sqrt{\kappa_1}+\sqrt{\kappa_2}}
(T+\beta_1+\beta_2)-\beta_i.
```

Respect the lower bounds n_i>=p_i and compare neighboring feasible integers. This gives exact fixed-count PCS allocation in that regime. With more arms, the analogous formula minimizes **total estimation variance**, with active lower bounds if necessary. The script implements the exact integer variance allocation by successive largest marginal reductions; this is not a multi-arm PCS rule.

## Optimal multi-arm error exponent and allocation

For fixed proportions `n_i/T -> w_i>0` in the rested model, the exact Gaussian error exponent is

```math
\boxed{E(w)=\min_{i\ne b}\frac{\Delta_i^2}
{2(\kappa_b/w_b+\kappa_i/w_i)}.}
```

This follows from pairwise Gaussian tails and a finite union bound, whose lower and upper exponential rates agree. To maximize it, let r be the unique solution in `(0,min_i Delta_i^2)` of

```math
\boxed{\frac{\kappa_b}{r^2}
=\sum_{i\ne b}\frac{\kappa_i}{(\Delta_i^2-r)^2}.}
```

Then

```math
w_b^*=\frac{\kappa_b/r}{D(r)},\qquad
w_i^*=\frac{\kappa_i/(\Delta_i^2-r)}{D(r)},\qquad
D(r)=\frac{\kappa_b}{r}+\sum_{i\ne b}\frac{\kappa_i}{\Delta_i^2-r},
```

and `E*=1/[2D(r)]`. The denominator is strictly convex with divergent endpoint limits, so a scalar bisection solves the allocation. Temporal dependence enters through the exact long-run variances kappa_i. Finite budgets also retain the boundary corrections beta_i.

For equal competitor gaps Delta, there is an elementary closed form:

```math
w_b^*=\frac{\sqrt{\kappa_b}}{\sqrt{\kappa_b}+\sqrt{\sum_{i\ne b}\kappa_i}},\qquad
w_i^*=\frac{\kappa_i}{\sqrt{\sum_{j\ne b}\kappa_j}
(\sqrt{\kappa_b}+\sqrt{\sum_{j\ne b}\kappa_j})}.
```

With common kappa, this becomes `w_b=1/(1+sqrt(L-1))` and `w_i=1/[sqrt(L-1)(1+sqrt(L-1))]`. For three arms, the proportions are approximately `(.414214,.292893,.292893)`, not uniform thirds.

These are optimal **fixed-proportion Gaussian-likelihood error exponents**, using the true best arm and gaps as an allocation benchmark. They are not exact finite-T PCS optima or a proved adaptive tracking algorithm. Restless schedules require their actual covariance information; these rested proportions cannot simply be transplanted into calendar time.

## Reproduction and literature

```sh
python3 experiments/ar_p_extension.py --verify
python3 experiments/ar_p_extension.py --runs 40000
python3 experiments/ar_p_extension.py --render-only
cd research/ar_p_bandits
/Users/guoweisun/.local/bin/tectonic --only-cached --keep-logs manuscript.tex
```

The script checks dense covariance information against innovation filtering, exact affine information, finite-future predictive sufficiency, variance reduction, AR(1) reductions, exhaustive multi-arm schedule bounds, integer variance allocation, and the AR(2) counterexamples. It evaluates PCS integrals and simulates heterogeneous AR(1), AR(2), and AR(3) mean selection. Numerical integration is a consistency check, not a certified quadrature bound or an optimality proof.

The Gaussian filtering architecture, information-value policies, and large-deviation allocation principles are established. The extension applies them to the specified model and states exactly which previous conclusions survive. No publication novelty is asserted.

- [Kalman (1960), original filtering paper](https://skoge.folk.ntnu.no/puublications_others/1960_Kalman%20-%20A%20new%20approach%20to%20linear%20filtering%20and%20prediction%20problems%20-%20Orinal%20version%20with%20comments.pdf).
- [Liu, Van Roy, and Xu (AISTATS 2023), Predictive Sampling](https://proceedings.mlr.press/v206/liu23e.html).
- [Frazier, Powell, and Dayanik (2008), knowledge gradient](https://doi.org/10.1137/070693424).
- [Glynn and Juneja (WSC 2004), allocation through error exponents](https://web.stanford.edu/~glynn/papers/2004/GJuneja04.pdf).
- [Garivier and Kaufmann (COLT 2016), iid fixed-confidence optimal allocation](https://proceedings.mlr.press/v49/garivier16a.html). This supplies related allocation context, not an AR fixed-budget theorem.
