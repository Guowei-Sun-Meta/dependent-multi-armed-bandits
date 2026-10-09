# Historical overview of the superseded formulation

The current manuscript uses fixed means and heterogeneous AR orders. This document preserves the previous development.

# Persistent graph means under spatial AR(1) fluctuations

The standalone [paper](manuscript.pdf) and [LaTeX source](manuscript.tex) develop the tractable common-AR(1) model for selecting the best long-run location. The paper includes proofs, an analytic PCS figure, a literature comparison, and a permanent-mean experiment. The earlier exploratory formulation and reward experiment remain below.

## Standalone paper: model, estimator, and contribution

At each calendar time, observe one location:

```math
Y_t=\mu_{a_t}+z_{a_t,t}+\xi_t,\qquad
z_{t+1}=\phi z_t+\varepsilon_{t+1},\qquad
\varepsilon_t\sim N(0,(1-\phi^2)K_z).
```

Here the unknown permanent mean `mu` is graph-smooth, while the stationary residual covariance `K_z` describes spatially shared fluctuations. All locations evolve every round; dynamics and residual covariance are known. Permanent-mean selection targets the largest `mu_i`, measured by PCS or expected opportunity loss. Tracking the largest current `mu_i + z_i,t` is a separate objective.

For a recorded design matrix `M` and trajectory covariance `Xi`, use

```math
\widehat\mu=
\left(M^\top\Xi^{-1}M+\alpha I+\lambda L\right)^{-1}
M^\top\Xi^{-1}Y.
```

The covariance-weighted fit accounts for AR dependence; the Laplacian discourages neighboring permanent means from disagreeing. A **hard constraint** `mu^T L mu <= S^2` literally enforces a supplied smoothness radius, with an active multiplier found by scalar search. A **Gaussian graph prior** with precision `alpha I + lambda L` encourages smoothness and gives exact conjugate updates, but does not enforce a deterministic radius. Frequentist intervals include smoothing bias rather than treating reduced posterior variance as verified accuracy.

The paper establishes:

- Fixed-design contrast bias and variance, including an explicit energy-based bias bound and a constrained estimator.
- An affine Kalman innovation regression for adaptive measurements, exact Bayesian mean updates, and an all-time confidence bound using established self-normalized concentration. A supplied mean-norm bound and energy radius yield a correct stopping certificate; forced cyclic probes ensure eventual termination.
- Permanent-contrast information sampling and correlated-normal knowledge gradient with history-dependent measurement vectors. The rules are exact for their respective two-candidate PCS or general opportunity-loss objective when one measurement remains; multi-step use is an approximation.
- An exact two-location, two-observation Bayes-PCS optimum: for nonnegative temporal persistence and equal marginal residual variances, sample each location once. With prior difference precision `h_minus = alpha + 2 lambda w` and `v_minus = V(1-rho phi)+r`, optimal PCS is `1/2 + atan(1/sqrt(h_minus v_minus))/pi`.
- Minimax shrinkage within a specified linear two-location contrast family. It reduces worst-case MSE while preserving the observed difference's sign, so it leaves fixed-mean PCS unchanged.
- A full-field information benchmark showing temporal effective sample size `a_n = [n(1-phi)+2phi]/(1+phi)`. Strong persistence can preserve short-term forecasts while slowing estimation of a permanent mean.

### Difference from existing research

This model belongs to established Gaussian-process and linear Gaussian families. Its additive covariance `K_mu + phi^|t-s| K_z` is not a new kernel construction.

| Closest literature | Distinction developed here |
|---|---|
| [Spectral bandits, ICML 2014](https://proceedings.mlr.press/v32/valko14.html), and [GRUB, NeurIPS 2022](https://papers.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html) | The graph constrains permanent means, but measurement errors are spatially and temporally correlated. The likelihood information is generally a matrix rather than per-arm iid sample counts. |
| [Time-varying GP bandits, AISTATS 2016](https://proceedings.mlr.press/v51/bogunovic16.html) | Separate an unknown static component from the evolving field and optimize its final selection. Instantaneous reward tracking uses a different comparator. |
| [Correlated-normal knowledge gradient, INFORMS Journal on Computing 2009](https://doi.org/10.1287/ijoc.1080.0314) | Retain its established terminal-value objective and envelope calculation, while replacing independent measurement errors with AR innovation regression and history-dependent measurement vectors. |
| [Shared linear Gaussian bandits, L4DC 2024](https://proceedings.mlr.press/v242/gornet24a.html) | Specialize exact filtering to graph-constrained permanent-mean estimation, contrast confidence, and short-budget selection designs. |

The present contribution is the integration, explicit estimation and confidence formulas, and specialized exact designs. Publication priority for those specializations is not established. General optimal allocation, matching bounds, learning graph validity, and unknown temporal dynamics remain open.

### Reproducible evidence

Use [the executable mean-selection study](../../../../experiments/graph_ar1_mean.py), [findings](../../results/mean_selection/findings.md), [summary](../../results/mean_selection/summary.csv), [paired comparisons](../../results/mean_selection/paired.csv), [metadata](../../results/mean_selection/metadata.json), and [checks](../../results/mean_selection/checks.json).

The permanent-mean experiment uses six locations, 48 measurements, seven policies, and **200 independent paired runs per configuration** across six configurations. It reports opportunity loss, recommendation PCS, MSE, and interval coverage. Correct AR modeling improves estimation under strong persistence; rolling KG does not consistently beat round robin or the other priors. The diagonal-mean baseline preserves graph-prior marginal variances while removing mean correlations. A permuted mean graph and an iid-noise model separately stress spatial and temporal assumptions.

The script passes **8,888 counted assertions**, including independent dense-likelihood comparisons and three 50,000-draw checks of the exact two-location PCS. The all-time frequentist confidence audit uses each truth's actual norm and energy solely as supplied certificates for graph--AR KG; it does not demonstrate learning these bounds.

```sh
python3 experiments/graph_ar1_mean.py --verify
python3 experiments/graph_ar1_mean.py --runs 200 --budget 48
python3 experiments/graph_ar1_mean.py --render-only
cd research/spatiotemporal_bandits
tectonic --only-cached --keep-logs manuscript.tex
```

## Earlier exploratory development

Working research development, 9 October 2026. This connects the [graph alignment paper](../../../alignment_paper/README.md) with the [heterogeneous AR bandit development](../../../ar_p_bandits/README.md). The combination is well grounded in existing research; priority for the specialized results below has not been established.

**Main conclusion.** Spatial and temporal bandit dependence have already been combined, including an almost exact common-AR(1) predecessor. We can nevertheless develop a coherent extension focused on graph validity, information about reward differences, and the distinction between ongoing reward and final selection. This note supplies exact Gaussian formulas, an implementable reward policy, a selection policy, explicit comparator bounds, and a small reproducible reward experiment. It does not establish a generally optimal policy or a new matching regret theorem.

- [Executable policies and checks](../../../../experiments/spatiotemporal_bandits.py).
- [Experiment findings](../../results/findings.md), [paired comparisons](../../results/paired.csv), [metadata](../../results/metadata.json), and [exact checks](../../results/checks.json).
- [Illustration of spatial reach, predictive lifetime, and ranking information](../../information.svg).

## 1. Existing research: the overlap is substantial

The literature was checked on 9 October 2026. These are primary sources; a preprint date and a publication date are distinguished where relevant.

| Work and venue | What it already combines | Implication for this project |
|---|---|---|
| [Krause and Ong, Contextual Gaussian Process Bandit Optimization, NIPS 2011](https://papers.nips.cc/paper/2011/hash/f3f1b7fc5a8779a9e618e1f23a7b7860-Abstract.html) | GP kernels over joint action and context spaces, composite kernels, and regret analysis. Time can enter the context. | A kernel over location and time is an established bandit construction. |
| [Bogunovic, Scarlett, and Cevher, Time-Varying Gaussian Process Bandit Optimization, AISTATS 2016](https://proceedings.mlr.press/v51/bogunovic16.html), [paper](https://proceedings.mlr.press/v51/bogunovic16.pdf) | A spatial GP evolving through a Markov recurrence; resetting and time-varying GP-UCB; upper bounds depending on variation and a linear-regret obstruction at fixed nondegenerate variation. | The closest predecessor to common-AR(1) graph-correlated fluctuations. Its temporal factor is explicitly separable from its spatial kernel. |
| [Imamura et al., Time-varying Gaussian Process Bandit Optimization with Non-constant Evaluation Time, 2020 preprint](https://arxiv.org/abs/2003.04691) | Temporal GP optimization when evaluations take different amounts of time, with regret analysis. | Expensive traffic measurement requires calendar time and measurement duration as well as a sample budget. |
| [Liu, Van Roy, and Xu, Nonstationary Bandit Learning via Predictive Sampling, AISTATS 2023](https://proceedings.mlr.press/v206/liu23e.html) | Exploration directed toward information that remains useful for future decisions. | The predictive-information principle is established. Applying it to a graph Gaussian state is a specialization. |
| [Gornet and Sinopoli, Restless bandits with rewards generated by a linear Gaussian dynamical system, L4DC 2024](https://proceedings.mlr.press/v242/gornet24a.html) | Shared Gaussian latent dynamics and reward prediction across actions using past observations from other actions. | Cross-arm and cross-time inference through a joint Kalman state is already a bandit research direction. |
| [Trella et al., Non-Stationary Latent Auto-Regressive Bandits, Reinforcement Learning Journal / RLC 2025](https://rlj.cs.umass.edu/2025/papers/Paper70.html) | Arms share a latent AR process; LARL learns prediction parameters online. The published account qualifies sublinear regret by requiring sufficiently small latent process noise relative to the horizon. | Shared AR drivers, parameter learning, and temporal prediction are established. Do not import the older preprint's simplified rate into our fixed-innovation oracle comparison. |
| [Ziomek, Adachi, and Osborne, Time-varying Gaussian Process Bandits with Unknown Prior, AISTATS 2025](https://proceedings.mlr.press/v258/ziomek25a.html) | PE-GP-UCB eliminates inconsistent candidate priors and provides regret guarantees. | Selecting or rejecting a wrong spatiotemporal prior is already studied. A graph-error contribution must go beyond a generic candidate-prior construction. |
| [Gornet, Mo, and Sinopoli, A Control Theory inspired Exploration Method for a Linear Bandit driven by a Linear Gaussian Dynamical System, 2025 preprint](https://arxiv.org/abs/2510.01364) | Kalman-UCB and an information-filter exploration rule depending on dynamical observability. | A predicted-reward score plus a state-information term has a close predecessor. Its published status is not established here. |
| [Güneyi et al., Learning Graph ARMA Processes From Time-Vertex Spectra, IEEE Transactions on Signal Processing, vol. 72, 2024](https://ieeexplore.ieee.org/document/10311074/), [author preprint](https://arxiv.org/abs/2302.06887) | Graph ARMA modeling and reconstruction of missing node-time values from learned joint spectra. The online publication date is November 2023. | Graph spectral temporal models and interpolation are established signal-processing tools; adaptive regret and PCS are different objectives. |
| [Zhang and Yao, Geometry-aware Active Learning of Spatiotemporal Dynamic Systems, IISE Transactions, 2026](https://www.tandfonline.com/doi/full/10.1080/24725854.2026.2655757), [2025 preprint](https://arxiv.org/abs/2504.19012) | Geometry-aware spatiotemporal GP inference and adaptive spatial measurement for reconstruction. | Expensive spatiotemporal sensing has an active-learning literature. Reconstruction accuracy differs from identifying the best location. |

For the closest comparison, the 2016 process can be written

```math
f_{t+1}=\phi f_t+\sqrt{1-\phi^2}\,g_{t+1},
\qquad g_t\stackrel{\mathrm{iid}}\sim\operatorname{GP}(0,k),
\qquad \phi=\sqrt{1-\epsilon}.
```

Restrict locations to graph nodes and choose a valid graph kernel for k. This yields our simplest zero-mean model below. A change from a Euclidean kernel to a graph kernel alone is therefore insufficient as a novelty claim. Graph-feedback bandits and communication-graph bandits should also be distinguished: an edge in those models can reveal an actual extra observation or permit communication, whereas our edge supplies a statistical relationship.

## 2. Which business decision are we optimizing?

Suppose each node is a prospective business location. Let latent traffic be f_i,t, and let a measurement be Y_t=f_a,t+xi_t. One measurement is obtained per round; all locations evolve each calendar round. Measurement variance r may be zero for exact observations.

Three objectives have different optimal sampling behavior:

1. **Permanent location selection:** choose the largest long-run mean mu_i after T measurements. Optimize PCS or expected opportunity loss `E[max_i mu_i - mu_recommendation]`. This is the natural first objective for opening a business.
2. **A future operating window:** choose the largest conditional expected integrated traffic over a specified future interval. Its target is a linear projection of the Gaussian trajectory, so the calculations below still apply.
3. **Ongoing operation:** earn f_a,t each round while learning. Optimize cumulative reward, or regret against a full-current-state oracle. Forecasting and refreshing beliefs now have immediate economic value.

A location can have a high reading because of a temporary event rather than a high long-run mean. Sampling to predict that event and sampling to determine permanent location quality are related but different. Mean pseudo-regret `sum_t(max_i mu_i-mu_a,t)` also differs from actual reward regret: an adaptive action can deliberately exploit fluctuations around its mean.

For traffic, seasonality, time of day, weather, direction of travel, rent, and measurement duration should be incorporated in the eventual model. The theory here uses Gaussian deviations around a baseline; it does not treat negative Gaussian values as literal vehicle counts. A permanent location target should ultimately be expected business profit or an explicitly weighted traffic measure.

## 3. A model that preserves the per-arm AR interpretation

Let L_G be the Laplacian of a supplied undirected similarity graph. Use N arms to keep the Laplacian and arm count distinct. Set

```math
f_t=\mu+z_t,\qquad
z_{i,t}=\sum_{r=1}^{p_i}a_{i,r}z_{i,t-r}+\varepsilon_{i,t},
\qquad \varepsilon_t\stackrel{\mathrm{iid}}\sim N(0,Q_G).
```

Every scalar AR polynomial is stable. The innovation vector is independent over time and independent of the initial stationary state and of mu, but its coordinates are correlated through Q_G. This retains heterogeneous per-arm AR(p_i) dynamics. Padded diagonal coefficient matrices give a vector AR representation; stacking lags produces a stable finite-dimensional state.

There are **two separate spatial assumptions**:

- A trusted deterministic mean certificate `mu^T L_G mu <= S_mu^2`, as in the graph alignment track; or a proper Gaussian mean prior `mu ~ N(m_mu,K_mu)` with graph-based covariance.
- Graph-correlated transient fluctuations, through Q_G or their stationary covariance. This is required if observing a location should reveal its neighbors' current deviations even when the long-run means are already known.

Smooth means with independent innovations share information about persistent location quality; they do not by themselves create contemporaneously correlated deviations. Applying a smoother to observations cannot manufacture a valid data-generating relationship.

A convenient proper graph covariance is `K_G=(alpha I+lambda L_G)^-1`, alpha>0, or a heat kernel. A Laplacian pseudoinverse alone omits uncertainty in the constant mode; an improper prior requires additional handling. A Gaussian graph prior satisfies an expected energy relation

```math
\mathbb E[\mu^\top L_G\mu]
=m_\mu^\top L_Gm_\mu+\operatorname{tr}(L_GK_\mu),
```

and is not a deterministic energy certificate. Gaussian fluctuations also need not satisfy a hard graph-energy bound at every time. Deterministic certificates and Bayesian priors must retain their separate interpretations.

Our simplest benchmark takes common persistence and a specified stationary residual covariance:

```math
\boxed{z_{t+1}=\phi z_t+\varepsilon_{t+1},\quad
\varepsilon_t\sim N(0,(1-\phi^2)K_z),\quad |\phi|<1.}
```

With stationary initialization, conditional on mu,

```math
\operatorname{Cov}(f_{i,t},f_{j,t+s}\mid\mu)
=\phi^{|s|}(K_z)_{ij}.
```

Under an independent Gaussian prior for mu,

```math
\boxed{\operatorname{Cov}(f_{i,t},f_{j,u})
=(K_\mu)_{ij}+\phi^{|t-u|}(K_z)_{ij}.}
```

The static term carries information that persists indefinitely; the transient term carries information whose usefulness changes with elapsed time.

## 4. Joint filtering: one observation changes every belief

For common AR(1), append the static mean to the transient state:

```math
x_t=\begin{pmatrix}\mu\\z_t\end{pmatrix},\quad
A=\begin{pmatrix}I&0\\0&\phi I\end{pmatrix},\quad
h_i=\begin{pmatrix}e_i\\e_i\end{pmatrix},\quad
\mathcal Q=\begin{pmatrix}0&0\\0&(1-\phi^2)K_z\end{pmatrix}.
```

Before a measurement, `x_t | H_t ~ N(b_t,P_t)`. For arm a let

```math
m_a=h_a^\top b_t,\quad d_a=h_a^\top P_th_a+r,\quad
k_a=P_th_a/d_a.
```

The exact update and propagation are

```math
b_t^+=b_t+k_a(Y_t-m_a),\qquad
P_t^+=P_t-P_th_ah_a^\top P_t/d_a,
```

```math
b_{t+1}=Ab_t^+,\qquad P_{t+1}=AP_t^+A^\top+\mathcal Q.
```

An observation updates all nodes and all hidden lags through the covariance column. Mean and transient-state errors become dependent after observing their sum; keeping separate independent filters for them is generally wrong. With heterogeneous orders, augment the lag vector instead of the scalar residual. Known coefficients and covariance retain exact Gaussian closure. Learning unknown coefficients usually requires a richer posterior or approximation.

Conditional on the complete history, these updates remain valid under adaptive sampling. The chosen action is known when its observation arrives and contributes no extra parameter-dependent likelihood factor.

## 5. The exact bridge quantity: information that reaches a target

For a future node j at lag s define

```math
C_{j,s;a}=\operatorname{Cov}(f_{j,t+s},Y_t\mid H_t,a_t=a).
```

Then observing a reduces that future reward variance by

```math
\boxed{\Delta V_{j,s;a}=C_{j,s;a}^2/d_a.}
```

In the augmented state, `C_j,s;a = h_j^T A^s P_t h_a`. The fresh measurement noise is independent and contributes only to d_a. More generally, for a vector target U of permanent means, a future traffic window, or future reward differences,

```math
\boxed{\operatorname{Cov}(U\mid H_t)-\operatorname{Cov}(U\mid H_t,Y_t,a)
=\frac{c_ac_a^\top}{d_a},\quad c_a=\operatorname{Cov}(U,Y_t\mid H_t).}
```

For a particular difference D=f_j,t+s-f_k,t+s, the reduction is

```math
\boxed{\Delta V_{D;a}=\frac{(C_{j,s;a}-C_{k,s;a})^2}{d_a}.}
```

This distinguishes reducing prediction error from improving a ranking decision. If a reading moves both candidates' predictions by the same amount, its one-step value for distinguishing them is zero.

At the initial stationary belief, with a Gaussian mean prior,

```math
C_{j,s;a}=(K_\mu)_{ja}+\phi^s(K_z)_{ja}.
```

After adaptive observations, the joint covariance need not retain this simple factorization. The general conditional C is the correct quantity. Shortest-path distance is also only a proxy: the covariance can be nonlocal, and distant nodes can share a useful latent factor.

## 6. A reward algorithm with an exact two-period derivation

Let m_i be current reward means and ell_i next-period reward means before the current observation. For candidate measurement a, put

```math
u_j^{(a)}=\frac{\operatorname{Cov}(f_{j,t+1},Y_t\mid H_t,a)}{\sqrt{d_a}}.
```

The standardized observation innovation Z is N(0,1), and every next-period mean changes to `ell_j+u_j^(a) Z`. Therefore

```math
\boxed{Q_a=m_a+\mathbb E_Z\max_j\{\ell_j+u_j^{(a)}Z\}.}
```

**Proof.** The final reward action has no subsequent information value, so it maximizes the posterior predictive mean. Gaussian regression gives its mean after the current observation. Averaging that maximum and adding the current expected reward gives Q_a. Choose its largest value. This is exact with two reward periods remaining, for any number of correlated Gaussian arms and known linear Gaussian dynamics, including augmented uncertain means.

The remaining expectation has only one scalar integration variable, regardless of arm count. The maximum of affine functions of Z is an upper envelope. If line j is maximal on interval [l_j,r_j], then

```math
\mathbb E_Z\max_j(\ell_j+u_jZ)
=\sum_j\left[\ell_j\{\Phi(r_j)-\Phi(l_j)\}
+u_j\{\varphi(l_j)-\varphi(r_j)\}\right].
```

The script computes this envelope exactly up to floating-point arithmetic. It sorts slopes and discards dominated lines. No Monte Carlo is needed for the two-period action scores.

With two candidate arms, define `g(d,s)=s varphi(d/s)-d Phi(-d/s)` for d>=0, and g(d,0)=0. Then

```math
\boxed{Q_a=m_a+\max(\ell_1,\ell_2)
+g\!\left(|\ell_1-\ell_2|,
\frac{|\operatorname{Cov}(f_{1,t+1}-f_{2,t+1},Y_t\mid H_t)|}{\sqrt{d_a}}\right).}
```

This extends the independent-arm rule: the information bonus depends on the uncertainty reduction of the **future difference**. A large common fluctuation cancels. With more than two arms the full upper envelope replaces this pairwise formula.

A practical reward policy is:

1. Maintain one joint Gaussian belief.
2. Compute current means, next means, and each measurement's covariance with the next reward vector.
3. Evaluate the envelope score Q_a and measure its maximizer.
4. Update every node, propagate the state, and repeat; at the last period maximize the current predictive mean.

Repeated two-period planning is an approximation for a longer horizon. The exact general policy is the Gaussian belief-state Bellman recursion

```math
J_r(b,P)=\max_a\{m_a+\mathbb E[J_{r-1}(\mathcal T(b,P,a,Y))]\},\quad J_0=0.
```

It retains the earlier difficulty: today's observation changes future measurement choices. Spatial coupling also breaks independent-arm index decompositions. An armwise Whittle index is not automatically justified.

**Joint predictive-sampling alternative.** With known means, AR(1) residual covariance P, and process covariance Q, the next latent vector screens the present from the remaining latent future. A predictive score draw has distribution

```math
\widetilde f_t\sim N\left(m_t,
\underbrace{P A^\top(APA^\top+Q)^{-1}AP}_{B_{\rm pred}}\right).
```

Select the largest jointly sampled score. For common AR(1), A=phi I. These draws must retain cross-arm covariance; sampling independent marginal scores changes the policy. The implementation uses this latent-future specialization, and does not automatically inherit every guarantee of published Predictive Sampling. For higher orders, a sufficiently long future lag reconstruction vector supplies the corresponding screening state. Unknown permanent means require an additional persistent target rather than blindly using one next vector.

## 7. A final-selection algorithm for the business example

Let theta be the Gaussian target vector: permanent means mu, or an integrated future traffic window. Its conditional distribution is `N(M,S)`.

The PCS-optimal terminal recommendation is

```math
\widehat b=\arg\max_i p_i,\qquad
p_i=\Pr(\theta_i\ge\theta_j\ \forall j\mid H).
```

For correlated targets, p_i is a Gaussian orthant probability for the difference vector. Its covariance entries are

```math
\operatorname{Cov}(\theta_i-\theta_j,\theta_i-\theta_k)
=S_{ii}-S_{ij}-S_{ik}+S_{jk}.
```

The product of independent-arm Gaussian CDFs from the AR-only paper is generally invalid here. For two candidates,

```math
\mathrm{conditional\ PCS}=\Phi\!\left(
\frac{|M_1-M_2|}{\sqrt{S_{11}+S_{22}-2S_{12}}}\right).
```

With one measurement left, a **PCS knowledge-gradient rule** chooses

```math
\boxed{a^*=\arg\max_a\mathbb E_Y\max_i p_i(H,Y,a).}
```

For two candidates this rule has a simple exact allocation: maximize

```math
\boxed{\frac{\operatorname{Cov}(\theta_1-\theta_2,Y_a\mid H)^2}
{\operatorname{Var}(Y_a\mid H)}.}
```

**Reason.** The target is the scalar Gaussian contrast D. Each possible measurement supplies a Gaussian experiment about D, with deterministic posterior contrast variance. A larger variance reduction is a more informative Gaussian experiment: the smaller-information experiment can be simulated by adding independent noise to the more informative one. Thus its optimal sign-selection success cannot be greater. The rule holds even at a nonzero posterior contrast mean, with a common measurement budget and target. Costs or durations change the allocation problem. For more than two contenders, one contrast variance does not determine PCS; use the expected best-probability objective or a documented approximation.

If expected opportunity loss is the target instead, terminal recommendation is the largest posterior mean and the one-measurement objective is `E[max_i M_i^after]`. This yields the same affine-envelope calculation as Section 6, with permanent target means and no immediate measurement reward. It is not a PCS objective for many candidates.

For a fixed Gaussian measurement design and a centered two-arm prior contrast with variance S_0, let S_D be the deterministic posterior contrast variance. Prior-averaged Bayes PCS is

```math
\boxed{\mathrm{PCS}=\frac12+\frac1\pi\arcsin\sqrt{1-S_D/S_0}.}
```

The posterior contrast mean has variance S_0-S_D and covariance S_0-S_D with the true contrast. Their sign-agreement probability gives the formula. This extends our earlier two-arm calculations to spatially correlated priors and observations. It does not yield the same expression for a nonzero prior contrast mean or an arbitrary adaptive random S_D without further analysis.

## 8. An illustrative closed form: correlation can help prediction but dilute ranking information

Take known equal means zero, stationary variance V, common persistence phi, and instantaneous spatial correlation rho, -1<rho<1:

```math
K_z=V\begin{pmatrix}1&\rho\\\rho&1\end{pmatrix},\qquad r=0.
```

Observing arm 1 at t gives future predictions `phi^s x` and `rho phi^s x` for arms 1 and 2. Their future variance reductions are `V phi^(2s)` and `V rho^2 phi^(2s)`. This directly illustrates both information pathways.

But for the next-period difference D, the variance reduction is

```math
\Delta V_D=\phi^2 V(1-\rho)^2,
\qquad V_D=2V(1-\rho).
```

Hence one-measurement next-state selection has exact prior-averaged PCS

```math
\boxed{\mathrm{PCS}_{1\to t+1}=\frac12+
\frac1\pi\arcsin\!\left(|\phi|\sqrt{\frac{1-\rho}{2}}\right).}
```

The exact optimal expected total reward for two periods is

```math
\boxed{J_2^*=\frac{|\phi|\sqrt V(1-\rho)}{\sqrt{2\pi}},\qquad
R_2^*=2\sqrt{\frac{V(1-\rho)}\pi}-J_2^*.}
```

The first choice is symmetric; after measuring x, repeat when `phi(1-rho)x>=0` and switch otherwise. The second-period maximum forecast integrates to J_2^*. The full-state oracle's per-period expected reward is `sqrt(V(1-rho)/pi)`.

At V=1 and phi=0.9:

| rho | Two-period optimal reward | Two-period regret | One-sample next-state PCS |
|---|---|---|---|
| 0 | 0.359048 | 0.769331 | 0.719576 |
| 0.5 | 0.179524 | 0.618361 | 0.648576 |
| 0.9 | 0.035905 | 0.320920 | 0.564499 |
| 0.99 | 0.003590 | 0.109247 | 0.520271 |

As rho increases, absolute tracking regret falls because the oracle's advantage shrinks; PCS for the next instantaneous winner falls because the observation reveals mostly a common component. This is a fixed-marginal-variance comparison of transient fluctuations, not a theorem that every kind of spatial information harms PCS. Permanent-mean identification can benefit from a valid graph mean restriction. At rho=1 the two states tie exactly, so unique-best PCS is no longer the same problem.

The normalized two-period regret relative to two periods of oracle reward is

```math
\frac{R_2^*}{2\mathbb E\max_i f_i}
=1-\frac{|\phi|\sqrt{1-\rho}}{2\sqrt2}.
```

Thus decreasing absolute regret alone need not establish a better policy's relative tracking quality.

## 9. Bounds and information calculations that combine the tracks

### A. Full-current-state regret has a correlated innovation floor

With known mu and stable vector AR dynamics, let Gamma be the stationary contemporaneous residual covariance and Q the covariance of the fresh innovation. A genie observing all past lag states knows the current predictable component. Its unconditional covariance is Gamma-Q. Define

```math
G(\mu,C)=\mathbb E\max_i\{\mu_i+Z_i\},\qquad Z\sim N(0,C).
```

Then every causal policy satisfies

```math
\boxed{R_T^\pi\ge T\{G(\mu,\Gamma)-G(\mu,\Gamma-Q)\}.}
```

**Proof.** Conditional on complete past lags, the causal action's expected reward is at most their largest current conditional mean. The genie can attain that mean. Independent fresh innovations can increase the full-state oracle's expected maximum, by convexity. Stationarity supplies the same expectation each round.

For two equal-mean common-AR(1) arms this becomes

```math
\boxed{R_T^\pi/T\ge
\sqrt{V(1-\rho)/\pi}\,(1-|\phi|).}
```

This is an explicit joint spatial/temporal lower bound. It does not include the additional cost of sparse observations or match a policy upper bound. If Q is positive definite and there are at least two arms, the gap is strictly positive. If innovations are only a common shift `Q=q 11^T`, they can leave every ordering unchanged, and the gap can be zero. It is therefore incorrect to infer positive linear regret merely from a large total innovation variance.

### B. A generic GP-UCB bound is available, but can be linear

For a correctly specified Gaussian prior over node-time latent rewards, r>0, and marginal prior variances bounded by v_max, use current predictive UCB

```math
a_t=\arg\max_i\{m_{i,t}+\sqrt{\beta_t P_{ii,t}}\},\qquad
\beta_t=2\log\{N\pi^2t^2/(3\delta)\}.
```

A Gaussian tail union bound over arms and times gives simultaneous confidence with probability at least 1-delta. On that event, instantaneous full-state regret is at most `2 sqrt(beta_t P_a,a,t)`.

Let gamma_T be the largest half log determinant `1/2 log det(I+K_design/r)` over fixed designs with exactly one location at each of the T calendar times. The selected covariance is from the complete node-time kernel. The conditional variance/determinant identity, applied to each realized design, and concavity of log yield

```math
\boxed{R_T\le
\sqrt{\frac{8v_{\max}T\beta_T\gamma_T}
{\log(1+v_{\max}/r)}}}
```

with the same high probability under the Bayesian model. This is a standard GP-UCB information argument specialized to the finite node-time domain. It is not a newly established regret rate, an expected-regret theorem without additional handling, or a certificate for a misspecified graph. At fixed nondegenerate temporal innovations, gamma_T can grow linearly, consistent with a linear tracking floor. A graph/temporal model does not guarantee sublinear full-state regret.

### C. Permanent-mean information is a schedule-dependent matrix

For fixed measurements `(a_r,t_r)`, let M have row r equal to `e_a,r^T`. Conditional on a deterministic mu, the observation covariance in the common-AR(1) model is

```math
\Xi_{rs}=(K_z)_{a_r,a_s}\phi^{|t_r-t_s|}+\sigma_{\rm obs}^2\,\mathbf1\{r=s\}.
```

Here sigma_obs^2 is the measurement variance denoted by r elsewhere. The exact information and Gaussian likelihood divergence are

```math
\boxed{\mathcal I=M^\top\Xi^{-1}M,\qquad
\operatorname{KL}(P_\mu,P_\nu)=\tfrac12(\mu-\nu)^\top\mathcal I(\mu-\nu).}
```

With a proper Gaussian mean prior,

```math
\boxed{S_\mu=(K_\mu^{-1}+\mathcal I)^{-1}.}
```

These combine graph restrictions on mean alternatives with AR-dependent observation information. For heterogeneous AR orders, replace the separable covariance by the stationary covariance of the vector companion system. Counts alone generally cannot describe the information matrix: the order, times, and locations matter. A Kronecker kernel does not make this sampling allocation separable, because selected node-time pairs need not form a full grid.

Given a completed adaptive history, the Bayesian likelihood and posterior calculations remain valid for its realized design. A fixed-design frequentist Gaussian estimator law or KL formula for an entire adaptive experiment cannot be imported by conditioning on its random action sequence: policy selection changes that conditional law. Adaptive lower-bound arguments instead use the sequential likelihood innovations or expected conditional divergences.

### D. A limited joint-covariance robustness certificate

Fix a measurement design and a scalar contrast target D. Suppose the centered joint covariance of `(D,Y)` is C under the true Bayesian model and C_hat under the fitted graph/temporal model. Assume a supplied joint spectral certificate

```math
(1-\eta)C\preceq\widehat C\preceq(1+\eta)C,
\qquad 0\le\eta<1.
```

Let S_hat be the fitted posterior contrast variance and `D_hat=w_hat^T Y` its fitted linear predictor, with the correct common prior mean. Then

```math
\boxed{\mathbb E_C(D-\widehat D)^2\le S_{\rm hat}/(1-\eta).}
```

**Proof.** For `a=(1,-w_hat)`, the fitted MSE is `a^T C_hat a=S_hat`. The lower covariance inequality gives `a^T C a<=S_hat/(1-eta)`. The error is Gaussian under the fixed true design, so inflated normal error bars have the corresponding unconditional Bayesian coverage. This is not a history-conditional or arbitrary-adaptive guarantee, nor does it handle an incorrect prior mean.

The same variational characterization of a Schur complement gives `(1-eta) S_true <= S_hat <= (1+eta) S_true`. A Laplacian comparison alone does not provide this full certificate if temporal coefficients or process noise are wrong. Conversely, when only a valid deterministic mean-energy certificate is used, the graph-alignment paper's Laplacian radius inflation still applies to that mean class; it supplies no certificate for transient covariance.

This identifies a concrete theoretical target: valid adaptive confidence and policy guarantees that quantify error in the **decision-relevant joint covariance**, together with the cost of diagnosing restricted graph and temporal violations. The fixed-design calculation above is only a starting result.

## 10. Extension to graph spectral temporal modes

A richer graph VAR model is

```math
z_t=\sum_{r=1}^p b_r(L_G)z_{t-r}+\varepsilon_t.
```

If `L_G=U diag(lambda_k) U^T` and Q shares this eigensystem, then mode k follows

```math
\widehat z_{k,t}=\sum_r b_r(\lambda_k)\widehat z_{k,t-r}+\widehat\varepsilon_{k,t}.
```

Every mode polynomial must be stable. Its variance, impulse response, and measurement loading U_i,k specify the spatial extent and temporal lifetime of information. Modes need not have the same persistence; this produces a generally nonseparable node-time covariance.

This model is motivated by existing graph ARMA/time-vertex work. A node reward is now a mixture of modes and generally is not a scalar AR(p_i) of the originally asserted order. Use the diagonal-coefficient, correlated-innovation model when preserving that assertion matters. Directed traffic propagation can also require nonsymmetric transitions and a stationary covariance obtained from a Lyapunov equation; an undirected similarity graph does not imply physical traffic causality.

For ranking, a mode's loading on a pairwise difference is `U_j,k-U_l,k`. A constant graph mode cancels exactly. A small-amplitude, persistent mode that distinguishes two near-optimal locations can therefore matter more than a large global traffic mode. This is the appropriate connection between spectral alignment and predictive lifetime.

## 11. Prototype and publication direction

The initial implementation compares joint greedy filtering, rolling joint two-step control, independent-arm two-step control, a relabeled-graph two-step rule, joint latent-future predictive sampling, and TV-GP-UCB with a specified untuned confidence parameter. It uses known zero means and dynamics, six path nodes, common stationary marginal variance one, measurement variance 0.04, persistence 0, 0.9, or 0.99, and graph covariance strength 0 or 2. There are 24 paired runs at horizon 1,200 for each configuration. The covariance is a diagonally normalized graph resolvent; its normalization is part of the model specification.

The separate checks compare sequential filtering with dense node-time conditioning, validate augmented unknown-mean filtering, compare exact envelope integration with independent quadrature, and check the two-arm closed forms and common-mode cancellation. Unknown-mean PCS is derived above but has not been evaluated in this reward simulation. Results and uncertainty are saved in [findings](../../results/findings.md); finite-horizon regret per round is not an estimated optimum or a proved limiting coefficient.

At graph strength two and phi=0.9, regret per round is about 0.469 for joint two-step and 0.521 for joint greedy. At phi=0.99, joint predictive sampling gives about 0.186 versus 0.265 for joint two-step. Independent-arm two-step remains competitive, giving about 0.250 in the latter configuration; its paired difference from joint two-step is not resolved by the reported approximate 95% interval. A correct covariance model therefore improves inference without guaranteeing that every approximate decision rule using it beats a simpler rule. The checks pass 1,636 assertions, including PCS quadrature and the fixed-design covariance-error inequality.

The strongest candidate research direction is **graph validity for decision-relevant information that persists through time**. A defensible next paper should:

- Specify whether the target is permanent-mean PCS, future-window opportunity loss, or ongoing reward, and compare to the matching oracle.
- Establish a bound involving graph-mode loadings on relevant contrasts, their temporal impulse responses, and certified model errors. Total state reconstruction variance is insufficient.
- Provide an adaptive policy guarantee and a lower bound in the same model, including costs of sparse measurement and restricted model validation. The current generic UCB bound and innovation floor do not match.
- Compare to TV-GP-UCB, candidate-prior elimination, shared latent-AR methods, observability-based exploration, and graph pure-exploration methods. Joint Kalman filtering, spectral covariances, and short-horizon knowledge gradient should be credited as established tools.
- Sweep mean alignment, fluctuation alignment, temporal mismatch, costs, and sample timing separately; then test traffic data with seasonality and business-relevant targets. An arbitrary shuffled graph is one stress test rather than a general graph-correctness study.

The current evidence supports a combined model and working algorithms. It does not support a claim to introduce spatial/temporal bandits or to have resolved the optimal long-horizon policy.

Reproduce from the repository root:

```sh
python3 experiments/spatiotemporal_bandits.py --verify
python3 experiments/spatiotemporal_bandits.py --runs 24 --horizon 1200
```
