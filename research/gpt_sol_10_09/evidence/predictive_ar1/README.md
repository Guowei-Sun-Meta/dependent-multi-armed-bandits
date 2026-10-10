# Predictive control for restless AR(1) rewards

Working development, 8 October 2026. The objective is to reduce the coefficient of expected regret against an oracle observing every arm's current state. We specialize published Predictive Sampling, derive exact finite-horizon belief control, and give a conditional average-reward certificate. The experiments do not establish an optimal policy or publication novelty.

The [two-arm allocation development](../two_arm_ar1/README.md) and its [proofs in PDF](../two_arm_ar1/manuscript.pdf) now give exact even-budget allocation for identifying unknown long-run means, an adaptive Bayesian optimality theorem, and an exact terminal-state identification policy. They also derive the two-pull reward optimum and a stronger two-arm sparse-monitoring regret lower bound. In that note `K` denotes the total sample budget; this draft uses `K` for the number of arms.

The [multiple-arm AR(p) development](../ar_p_bandits/README.md) extends the Gaussian belief calculations and Predictive Sampling to heterogeneous orders, gives an exact general two-period reward score, and derives allocation benchmarks for separate simulation streams. Its counterexamples distinguish those results from a general optimal PCS or reward policy.

## Model and observation timing

Independent arms evolve every calendar round:

```math
X_{i,t}=\mu_i+\phi_i(X_{i,t-1}-\mu_i)+\eta_{i,t},
\quad \eta_{i,t}\sim N(0,q_i),\quad q_i>0,\quad |\phi_i|<1.
```

Parameters are known in this initial study. Initial states have independent stationary laws $`N(\mu_i,V_i)`$, with $`V_i=q_i/(1-\phi_i^2)`$. The learner chooses before seeing any current state, receives $`X_{A_t,t}`$, and observes that state exactly. The oracle observes all current states before choosing. Actions do not change the state dynamics. This is within-arm dependence; an observation does not reveal another arm's state.

Define

```math
R_T^\pi=\mathbb E\sum_{t=1}^T\left[\max_iX_{i,t}-X_{A_t,t}\right],
\qquad c_\pi=\limsup_{T\to\infty}R_T^\pi/T.
```

The target is $`\inf_\pi c_\pi`$. A limit need not exist for every arbitrary time-varying policy, so the limsup is intentional. Finite-horizon simulations estimate $`R_T/T`$, rather than proving a limiting coefficient.

## An illustrative comparison

After an exact observation $`x`$ with age $`h`$, the current predictive belief is Gaussian with

```math
m_i=\mu_i+\phi_i^h(x-\mu_i),\qquad
v_i=V_i(1-\phi_i^{2h}).
```

For $`\phi=0.99`$ and innovation standard deviation $`0.01`$, $`q=10^{-4}`$ and $`V\approx0.005025`$. A one-round-old observation leaves variance $`10^{-4}`$, only 1.99% of stationary variance. For $`\phi=0.1`$ with the same innovation variance, that fraction is 99%. The one-step conditional variance is $`q`$ in both cases, but the amount of the stationary state variation that remains predictable differs greatly.

Observing the current state reduces the conditional variance of the state $`s`$ rounds later by exactly

```math
\Delta_i(s)=\phi_i^{2s}v_i.
```

Its cumulative reduction over $`H`$ future rounds is $`v_i\sum_{s=1}^H\phi_i^{2s}`$. This is a prediction-error reduction, not a reward-value formula: information is valuable for allocation only when it can change which arm should be selected.

## Exact Gaussian Predictive Sampling

Let $`H_t`$ contain the selected-arm observations before decision $`t`$. Predictive Sampling samples the random quantity $`\mathbb E[X_{i,t}\mid H_t,X_{i,t+1:\infty}]`$. In this exact-observation Markov model, the first future state $`X_{i,t+1}`$ is sufficient; later states add no information about $`X_{i,t}`$ conditional on it. Gaussian conditioning gives

```math
\widetilde X_{i,t}\sim N(m_i,s_i^2),\qquad
s_i^2=\frac{\phi_i^2v_i^2}{\phi_i^2v_i+q_i},
\qquad A_t\in\arg\max_i\widetilde X_{i,t}.
```

The draws are independent across arms and independent of actual current states conditional on history. This specializes Liu, Van Roy, and Xu's Predictive Sampling and Proposition 3 to zero measurement noise. We evaluate it against the requested full-current-state oracle, which differs from their future-information regret comparator. [AISTATS 2023 paper](https://proceedings.mlr.press/v206/liu23e/liu23e.pdf).

Implementation at each round:

1. Maintain each arm's exact Gaussian predictive mean and variance.
2. Sample the scores above and pull the largest.
3. Set the selected arm's current posterior mean to its observed state and variance to zero.
4. Propagate every arm: $`m_i\leftarrow\mu_i+\phi_i(m_i-\mu_i)`$, $`v_i\leftarrow\phi_i^2v_i+q_i`$.

Ordinary state-posterior Thompson Sampling uses sampling variance $`v_i`$. Predictive Sampling uses only

```math
s_i^2/v_i=\frac{\phi_i^2v_i}{\phi_i^2v_i+q_i},
```

the fraction associated with information retained in the next state. When $`\phi_i=0`$, its score is the known mean: fresh white noise is not mistaken for information worth acquiring.

This policy is not claimed to minimize $`c_\pi`$. It uses the future as a sampling target, rather than actually observing future states or solving the optimal belief-state control problem.

## A universal positive linear lower bound

Write

```math
G=\mathbb E\max_i(\mu_i+\sqrt{V_i}Z_i),\qquad
G_{\mathrm{past}}=\mathbb E\max_i(\mu_i+\phi_i\sqrt{V_i}Z_i),
```

for independent standard normal $`Z_i`$. An observer seeing all arms one round late predicts the current means $`\mu_i+\phi_i(X_{i,t-1}-\mu_i)`$. Giving the learner this information can only improve expected reward, so

```math
R_T^\pi\geq T\,L,\qquad L=G-G_{\mathrm{past}}.
```

For $`K\geq2`$ and positive independent innovation variances, $`L>0`$. Conditional on any past state vector, Gaussian innovations give positive probability that an arm other than the predicted best is actually best, making $`\mathbb E[\max_iX_{i,t}\mid X_{t-1}]`$ strictly greater than the best conditional mean. Stationarity makes the averaged gap identical each round. Also $`R_T^\pi\leq T\mathbb E[\max_iX_i-\min_iX_i]<\infty`$. Thus expected regret is $`\Theta(T)`$ for fixed nondegenerate parameters under this model.

More precisely,

```math
R_T^\pi=T(G-G_{\mathrm{past}})
+\sum_{t=1}^T\left[G_{\mathrm{past}}-\mathbb E X_{A_t,t}\right].
```

The first term is the cost of fresh innovations even with complete past observations; the second is the additional loss from incomplete monitoring and policy decisions. The lower-bound observer is stronger than the feasible learner and is not an attainable performance guarantee.

### Homogeneous arms

For common $`\mu=0,V,\phi\in[0,1)`$, let $`M_K=\mathbb E\max_{i\leq K}Z_i`$. Then

```math
L=(1-\phi)\sqrt V M_K,\qquad c_{\mathrm{fixed}}=\sqrt V M_K.
```

For two arms, $`M_2=1/\sqrt\pi`$, so

```math
R_T^\pi\geq \frac{(1-\phi)\sqrt V}{\sqrt\pi}T.
```

At $`\phi=0`$, all current states are independent of past information and every causal policy has expected reward zero. The lower bound is attained by every policy, including Predictive Sampling. No temporal policy can improve its coefficient in that case.

For two homogeneous arms, the [new sparse-monitoring proof](../two_arm_ar1/README.md#a-stronger-sparse-monitoring-regret-lower-bound) improves the coefficient lower bound to `sqrt(V/pi) [1-phi sqrt((1+phi^2)/2)]`. It uses the fact that a learner observing one arm per round cannot have refreshed both arms in the immediately previous round. This is a lower bound, with no general attainability claim.

Degenerate cases fall outside the positive lower bound: one arm, zero innovation noise, or parameters changing with the horizon. Exact $`\phi=1,q>0`$ is a random walk and has no stationary variance; it is not covered by this analysis.

## A constructive upper bound and the persistence limit

A simple feasible policy divides time into blocks of length $`H\geq K`$, probes each arm once in the first $`K`$ rounds, and then chooses the largest predictive mean. Every exploitation round has observation ages at most $`H`$. With homogeneous arms its coefficient satisfies

```math
c_{\mathrm{refresh}}\leq
\frac K H\sqrt V M_K
+\left(1-\frac K H\right)
\sqrt{2V(1-\phi^{2H})\log K}.
```

Proof: predetermined probe rounds have expected reward zero and hence expected regret $`\sqrt V M_K`$. At an exploitation round, write $`X_i=m_i+e_i`$. Conditional residuals are independent centered Gaussians with variances at most $`V(1-\phi^{2H})`$. Since $`\max_i(m_i+e_i)\leq\max_i m_i+\max_i e_i`$, the expected regret of choosing the largest $`m_i`$ is at most the Gaussian maximum bound $`\sqrt{2v_{\max}\log K}`$. Averaging the two types of rounds proves the claim; an incomplete final block contributes only a bounded remainder for fixed $`H`$.

Combining this with the fixed-arm policy yields

```math
(1-\phi)\sqrt V M_K\ \leq c^*\ \leq
\min\left\{\sqrt V M_K,\inf_{H\geq K}c_{\mathrm{refresh}}^{\mathrm{bound}}(H)\right\}.
```

For fixed $`K,V`$ and $`\delta=1-\phi\downarrow0`$, choosing $`H`$ of order $`\delta^{-1/3}`$ gives an upper bound of order $`\sqrt V\delta^{1/3}`$, with constants depending on $`K`$. Thus the optimal coefficient goes to zero in this fixed-stationary-variance limit, although each fixed $`\phi<1`$ has linear regret. The lower bound is of order $`\delta`$, leaving a substantial gap; this upper bound is for the probing policy, not for Predictive Sampling.

## A two-step control comparator

To distinguish predictive randomization from explicit information value, also evaluate a rolling two-period policy. Put

```math
\ell_i=\mu_i+\phi_i(m_i-\mu_i),\quad
b_i=|\phi_i|\sqrt{v_i},\quad C_i=\max_{j\ne i}\ell_j.
```

If arm $`i`$ is observed now, its next predictive mean has conditional distribution $`N(\ell_i,b_i^2)`$. The other next predictive means are unchanged by this observation. Its exact two-period score is

```math
Q_i=m_i+C_i+\mathbb E[(N(\ell_i-C_i,b_i^2))_+].
```

For $`z=(\ell_i-C_i)/b_i`$, the positive-part expectation is $`(\ell_i-C_i)\Phi(z)+b_i\varphi(z)`$, with the deterministic limit when $`b_i=0`$. Select the largest $`Q_i`$ and repeat next round. This is optimal for a two-period terminal problem, not a proof of optimal long-run control. No discount or exploration multiplier is tuned in these experiments.

For two arms, the immediate conditional oracle gap of PS also has a closed form. With $`d=m_1-m_2`$, $`u=\sqrt{v_1+v_2}`$, and $`w=\sqrt{s_1^2+s_2^2}`$,

```math
r_{\mathrm{PS}}(b)=
u\varphi(|d|/u)-|d|\Phi(-|d|/u)
+|d|\Phi(-|d|/w).
```

The first two terms are the greedy immediate gap; the last is the immediate cost of predictive exploration. Long-run improvement must come from changing future beliefs, rather than improving the immediate reward at the same belief. Use limiting values when $`w=0`$.

## Reproducible comparisons

The [experiment script](../../experiments/predictive_ar1.py) uses shared exogenous state trajectories across policies and independent replications. Non-oracle decisions are made before current innovations are generated; only the selected state enters their belief updates. All parameters are supplied, so these experiments isolate state tracking rather than parameter learning.

The primary sweep has five homogeneous zero-mean arms, stationary variance one, and persistence $`0,0.1,0.5,0.9,0.99,0.995`$. Therefore innovation variance changes as $`q=1-\phi^2`$. A separate case has four persistent arms and a high-variance white-noise arm, exposing information that cannot be retained. Comparators are fixed arm, greedy predictions, state-posterior Thompson Sampling, Predictive Sampling, rolling two-step control, deterministic refresh, and the stronger all-past-state observer.

Results are generated in [results/findings.md](results/findings.md), with raw replications, paired differences, cumulative curves, and metadata alongside it. Intervals are approximate 95% intervals over independent replications. They do not certify asymptotic optimality. The [working paper](manuscript.pdf) contains the model, derivations, bounds, and generated comparisons.

```sh
python3 experiments/predictive_ar1.py --verify
python3 experiments/predictive_ar1.py --runs 40 --horizon 30000 --burn 5000 --workers 4
python3 experiments/render_predictive_ar1.py
python3 experiments/ar1_policy_improvement.py --verify
python3 experiments/ar1_policy_improvement.py --workers 4
# Regenerate the additional comparison without rerunning simulation:
python3 experiments/ar1_policy_improvement.py --render-only
cd research/predictive_ar1
/Users/guoweisun/.local/bin/tectonic --only-cached --keep-logs manuscript.tex
```

For homogeneous zero-mean arms, multiplying all stationary and innovation variances by $`a^2`$ multiplies the coefficients of these scale-equivariant policies by $`a`$, without changing their decisions on correspondingly scaled trajectories. The strong-persistence, innovation-standard-deviation-0.01 example can therefore be obtained from the unit-stationary-variance case by multiplying its coefficients by $`\sqrt{10^{-4}/(1-0.99^2)}`$. This is an exact scaling calculation, not an additional independent experiment.

## The best policy: exact control and what remains unresolved

For known parameters, the sufficient control state is the complete vector of predictive means and variances $`b=((m_i,v_i))_{i=1}^K`$. Pulling arm $`i`$ and observing $`x\sim N(m_i,v_i)`$ produces the next belief $`\mathcal T_i(b,x)`$:

```math
(m_i',v_i')=(\mu_i+\phi_i(x-\mu_i),q_i),\qquad
(m_j',v_j')=(\mu_j+\phi_j(m_j-\mu_j),\phi_j^2v_j+q_j),\ j\ne i.
```

Thus the exact finite-horizon optimal policy comes from

```math
J_0(b)=0,\qquad
J_n(b)=\max_i\{m_i+\mathbb E J_{n-1}(\mathcal T_i(b,X_i))\}.
```

Choose a maximizing action at every remaining horizon. The formula is an exact optimality characterization, rather than a numerical solution for the five-arm cases. Each action requires a one-dimensional Gaussian integral, but the continuation value depends on every arm's joint belief.

For a direct information-value interpretation, let $`b^-`$ be the hypothetical next belief with no current observation, obtained by applying the unselected-arm update to all arms. The exact finite-horizon information bonus is $`I_{i,n}=\mathbb E J_{n-1}(\mathcal T_i(b,X_i))-J_{n-1}(b^-)`$, and the optimal score is $`m_i+I_{i,n}`$. This bonus is nonnegative because a continuation policy can ignore the observation. It depends on decision gaps and subsequent refreshes; it is zero with one round remaining and gives the exact two-period information value with two rounds remaining.

The linear coefficient instead requires average-reward control. Because the oracle's rate $`G`$ is independent of our actions,

```math
c_\pi=G-\liminf_{T\to\infty}\frac1T\mathbb E_\pi\sum_{t=1}^T X_{A_t,t}.
```

The corresponding Bellman equation is

```math
g+h(b)=\max_i\{m_i+\mathbb E h(\mathcal T_i(b,X_i))\}.
```

If a solution satisfies $`\mathbb E_\pi|h(B_{T+1})|/T\to0`$ for all admissible policies from our initial belief, choosing a maximizing action is average optimal and $`c^*=G-g`$. The continuation term accounts for information that changes future allocation, including later refreshes. We have not proved existence or computed such a solution for the unbounded Gaussian belief space. Predictive Sampling, two-step control, and the new lifetime rule are approximations with different empirical strengths.

General restless Markov examples show that independent-arm indices need not be optimal. This does not prove an impossibility theorem for our restricted Gaussian family, but it prevents invoking a universal index theorem here. [Ortner et al., Theorem 4](https://daniil.ryabko.net/mabajr.pdf). A Whittle approximation would require its own indexability and performance analysis.

## A certificate for how close a candidate is to optimal

For any trial continuation function $`h`$, define

```math
D_h(b,i)=m_i+\mathbb E h(\mathcal T_i(b,X_i))-h(b),\qquad
r_h(b)=\max_iD_h(b,i),\quad \pi_h(b)\in\arg\max_iD_h(b,i).
```

If $`\ell\le r_h(b)\le u`$ on all reachable beliefs, expectations are finite, and the transversality condition above holds, then

```math
G-u\le c^*\le c_{\pi_h}\le G-\ell,\qquad
c_{\pi_h}-c^*\le u-\ell.
```

Proof: under any policy, conditional expected reward plus the expected change in $`h`$ is at most $`u`$. Under $`\pi_h`$, it is at least $`\ell`$. Sum over rounds, telescope the changes in $`h`$, and divide by the horizon. Transversality removes the terminal contribution. A constant residual certifies optimality.

Unbounded Gaussian means admit a weighted version. Conditional Jensen's inequality and stationary states give a policy-independent moment bound

```math
\mathbb E_\pi\sum_i|m_i-\mu_i|\le C_V:=\sqrt{2/\pi}\sum_i\sqrt{V_i}.
```

Linear growth $`|h(b)|\le C_0+C_1\sum_i|m_i-\mu_i|`$ therefore suffices for transversality. If a globally verified bound is

```math
|r_h(b)-g|\le\epsilon_0+\epsilon_1\sum_i|m_i-\mu_i|,
```

put $`\epsilon=\epsilon_0+\epsilon_1C_V`$. Then $`G-g-\epsilon\le c^*\le c_{\pi_h}\le G-g+\epsilon`$, and the candidate's coefficient is within $`2\epsilon`$ of optimal. We have not computed such a global residual bound. A sampled grid alone cannot certify it; numerical integration, interpolation, and Gaussian tails must also be controlled.

This also supplies a conditional route to improving PS. If its constant gain $`g_0`$ and bias $`h_0`$ satisfy the policy evaluation equation $`g_0=\sum_i\pi_0(i\mid b)D_{h_0}(b,i)`$, then maximization gives $`r_{h_0}(b)\ge g_0`$. Under transversality, greedifying with respect to this bias cannot increase the average regret coefficient. Estimated biases and truncated rollouts need separate error bounds; discounted improvement alone does not certify an average-reward improvement.

## Does a long information lifetime alone give a better policy?

For common means and common nonnegative persistence $`\phi`$, let $`C_i=\max_{j\ne i}m_j`$, $`d_i=|m_i-C_i|`$, and define

```math
\mathrm{KG}_i(b)=\mathbb E\max(C_i,X_i)-\max_jm_j
=\sqrt{v_i}\varphi(d_i/\sqrt{v_i})-d_i\Phi(-d_i/\sqrt{v_i}).
```

This values uncertainty according to whether resolving it can change the selected arm. Knowledge-gradient policies are established in Bayesian information collection; their ranking-and-selection optimality results do not establish optimality for restless reward allocation. [Frazier, Powell, and Dayanik, 2008](https://doi.org/10.1137/070693424).

If we retain one new observation and ignore all subsequent observations in the continuation calculation, the improvement in the best predictive mean $`s`$ rounds later is exactly $`\phi^s\mathrm{KG}_i`$. Summing its future benefits gives the candidate

```math
A_t\in\arg\max_i\left\{m_i+\frac\phi{1-\phi}\mathrm{KG}_i(b)\right\}.
```

The multiplier is derived before simulation, with no fitted parameter. At $`\phi=0`$ it becomes greedy; at $`\phi=0.99`$ the multiplier is 99. Two-period control uses only $`\phi\mathrm{KG}_i`$. This information value is in reward units and decays as $`\phi^s`$, whereas the earlier prediction-error reduction decays as $`\phi^{2s}`$.

Replanning this rule uses future feedback that its continuation calculation ignored. Its accumulated bonus can therefore count benefits that later observations replace. The geometric formula is exact for that one-observation calculation, but the resulting repeated policy is an approximation. Heterogeneous means or persistence require another calculation.

The [additional experiment](../../experiments/ar1_policy_improvement.py) reuses the original 40 trajectories per homogeneous case, with 5,000 burn-in and 30,000 measured rounds. It verifies an exact replay of a saved PS replication before comparing against the baseline files. [Complete results and paired intervals](results/policy_improvement/findings.md).

| Persistence | Greedy | Two-step | Predictive Sampling | Lifetime KG |
|---|---:|---:|---:|---:|
| 0.5 | 0.8926 | 0.8927 | 1.0203 | 0.8932 |
| 0.9 | 0.4613 | 0.4334 | 0.5669 | 0.4574 |
| 0.99 | 0.2687 | 0.1997 | 0.1495 | 0.1659 |
| 0.995 | 0.2566 | 0.1795 | 0.0951 | 0.1171 |

These are finite-horizon regret-per-round estimates at stationary variance one. Lifetime KG beats PS at moderate persistence, but PS remains strongest among the tested policies at high persistence. Two-step control is strongest at 0.9; at 0.5 greedy and two-step are essentially tied. No candidate is uniformly best or certified optimal. The next computational target is the actual average-reward bias and its residual, rather than another lifetime multiplier.
