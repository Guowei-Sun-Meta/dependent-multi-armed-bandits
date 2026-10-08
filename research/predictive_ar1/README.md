# Predictive sampling for restless AR(1) rewards

Working development, 8 October 2026. The objective is to reduce the coefficient of expected regret against an oracle observing every arm's current state. The policy below specializes published Predictive Sampling; the elementary bounds and experiments here do not establish a new optimal-regret algorithm or publication novelty.

## Model and observation timing

Independent arms evolve every calendar round:

\[
X_{i,t}=\mu_i+\phi_i(X_{i,t-1}-\mu_i)+\eta_{i,t},
\quad \eta_{i,t}\sim N(0,q_i),\quad q_i>0,\quad |\phi_i|<1.
\]

Parameters are known in this initial study. Initial states have independent stationary laws \(N(\mu_i,V_i)\), with \(V_i=q_i/(1-\phi_i^2)\). The learner chooses before seeing any current state, receives \(X_{A_t,t}\), and observes that state exactly. The oracle observes all current states before choosing. Actions do not change the state dynamics. This is within-arm dependence; an observation does not reveal another arm's state.

Define

\[
R_T^\pi=\mathbb E\sum_{t=1}^T\left[\max_iX_{i,t}-X_{A_t,t}\right],
\qquad c_\pi=\limsup_{T\to\infty}R_T^\pi/T.
\]

The target is \(\inf_\pi c_\pi\). A limit need not exist for every arbitrary time-varying policy, so the limsup is intentional. Finite-horizon simulations estimate \(R_T/T\), rather than proving a limiting coefficient.

## An illustrative comparison

After an exact observation \(x\) with age \(h\), the current predictive belief is Gaussian with

\[
m_i=\mu_i+\phi_i^h(x-\mu_i),\qquad
v_i=V_i(1-\phi_i^{2h}).
\]

For \(\phi=0.99\) and innovation standard deviation \(0.01\), \(q=10^{-4}\) and \(V\approx0.005025\). A one-round-old observation leaves variance \(10^{-4}\), only 1.99% of stationary variance. For \(\phi=0.1\) with the same innovation variance, that fraction is 99%. The one-step conditional variance is \(q\) in both cases, but the amount of the stationary state variation that remains predictable differs greatly.

Observing the current state reduces the conditional variance of the state \(s\) rounds later by exactly

\[
\Delta_i(s)=\phi_i^{2s}v_i.
\]

Its cumulative reduction over \(H\) future rounds is \(v_i\sum_{s=1}^H\phi_i^{2s}\). This is a prediction-error reduction, not a reward-value formula: information is valuable for allocation only when it can change which arm should be selected.

## Exact Gaussian Predictive Sampling

Let \(H_t\) contain the selected-arm observations before decision \(t\). Predictive Sampling samples the random quantity \(\mathbb E[X_{i,t}\mid H_t,X_{i,t+1:\infty}]\). In this exact-observation Markov model, the first future state \(X_{i,t+1}\) is sufficient; later states add no information about \(X_{i,t}\) conditional on it. Gaussian conditioning gives

\[
\widetilde X_{i,t}\sim N(m_i,s_i^2),\qquad
s_i^2=\frac{\phi_i^2v_i^2}{\phi_i^2v_i+q_i},
\qquad A_t\in\arg\max_i\widetilde X_{i,t}.
\]

The draws are independent across arms and independent of actual current states conditional on history. This specializes Liu, Van Roy, and Xu's Predictive Sampling and Proposition 3 to zero measurement noise. We evaluate it against the requested full-current-state oracle, which differs from their future-information regret comparator. [AISTATS 2023 paper](https://proceedings.mlr.press/v206/liu23e/liu23e.pdf).

Implementation at each round:

1. Maintain each arm's exact Gaussian predictive mean and variance.
2. Sample the scores above and pull the largest.
3. Set the selected arm's current posterior mean to its observed state and variance to zero.
4. Propagate every arm: \(m_i\leftarrow\mu_i+\phi_i(m_i-\mu_i)\), \(v_i\leftarrow\phi_i^2v_i+q_i\).

Ordinary state-posterior Thompson Sampling uses sampling variance \(v_i\). Predictive Sampling uses only

\[
s_i^2/v_i=\frac{\phi_i^2v_i}{\phi_i^2v_i+q_i},
\]

the fraction associated with information retained in the next state. When \(\phi_i=0\), its score is the known mean: fresh white noise is not mistaken for information worth acquiring.

This policy is not claimed to minimize \(c_\pi\). It uses the future as a sampling target, rather than actually observing future states or solving the optimal belief-state control problem.

## A universal positive linear lower bound

Write

\[
G=\mathbb E\max_i(\mu_i+\sqrt{V_i}Z_i),\qquad
G_{\mathrm{past}}=\mathbb E\max_i(\mu_i+\phi_i\sqrt{V_i}Z_i),
\]

for independent standard normal \(Z_i\). An observer seeing all arms one round late predicts the current means \(\mu_i+\phi_i(X_{i,t-1}-\mu_i)\). Giving the learner this information can only improve expected reward, so

\[
R_T^\pi\geq T\,L,\qquad L=G-G_{\mathrm{past}}.
\]

For \(K\geq2\) and positive independent innovation variances, \(L>0\). Conditional on any past state vector, Gaussian innovations give positive probability that an arm other than the predicted best is actually best, making \(\mathbb E[\max_iX_{i,t}\mid X_{t-1}]\) strictly greater than the best conditional mean. Stationarity makes the averaged gap identical each round. Also \(R_T^\pi\leq T\mathbb E[\max_iX_i-\min_iX_i]<\infty\). Thus expected regret is \(\Theta(T)\) for fixed nondegenerate parameters under this model.

More precisely,

\[
R_T^\pi=T(G-G_{\mathrm{past}})
+\sum_{t=1}^T\left[G_{\mathrm{past}}-\mathbb E X_{A_t,t}\right].
\]

The first term is the cost of fresh innovations even with complete past observations; the second is the additional loss from incomplete monitoring and policy decisions. The lower-bound observer is stronger than the feasible learner and is not an attainable performance guarantee.

### Homogeneous arms

For common \(\mu=0,V,\phi\in[0,1)\), let \(M_K=\mathbb E\max_{i\leq K}Z_i\). Then

\[
L=(1-\phi)\sqrt V M_K,\qquad c_{\mathrm{fixed}}=\sqrt V M_K.
\]

For two arms, \(M_2=1/\sqrt\pi\), so

\[
R_T^\pi\geq \frac{(1-\phi)\sqrt V}{\sqrt\pi}T.
\]

At \(\phi=0\), all current states are independent of past information and every causal policy has expected reward zero. The lower bound is attained by every policy, including Predictive Sampling. No temporal policy can improve its coefficient in that case.

Degenerate cases fall outside the positive lower bound: one arm, zero innovation noise, or parameters changing with the horizon. Exact \(\phi=1,q>0\) is a random walk and has no stationary variance; it is not covered by this analysis.

## A constructive upper bound and the persistence limit

A simple feasible policy divides time into blocks of length \(H\geq K\), probes each arm once in the first \(K\) rounds, and then chooses the largest predictive mean. Every exploitation round has observation ages at most \(H\). With homogeneous arms its coefficient satisfies

\[
c_{\mathrm{refresh}}\leq
\frac K H\sqrt V M_K
+\left(1-\frac K H\right)
\sqrt{2V(1-\phi^{2H})\log K}.
\]

Proof: predetermined probe rounds have expected reward zero and hence expected regret \(\sqrt V M_K\). At an exploitation round, write \(X_i=m_i+e_i\). Conditional residuals are independent centered Gaussians with variances at most \(V(1-\phi^{2H})\). Since \(\max_i(m_i+e_i)\leq\max_i m_i+\max_i e_i\), the expected regret of choosing the largest \(m_i\) is at most the Gaussian maximum bound \(\sqrt{2v_{\max}\log K}\). Averaging the two types of rounds proves the claim; an incomplete final block contributes only a bounded remainder for fixed \(H\).

Combining this with the fixed-arm policy yields

\[
(1-\phi)\sqrt V M_K\ \leq c^*\ \leq
\min\left\{\sqrt V M_K,\inf_{H\geq K}c_{\mathrm{refresh}}^{\mathrm{bound}}(H)\right\}.
\]

For fixed \(K,V\) and \(\delta=1-\phi\downarrow0\), choosing \(H\) of order \(\delta^{-1/3}\) gives an upper bound of order \(\sqrt V\delta^{1/3}\), with constants depending on \(K\). Thus the optimal coefficient goes to zero in this fixed-stationary-variance limit, although each fixed \(\phi<1\) has linear regret. The lower bound is of order \(\delta\), leaving a substantial gap; this upper bound is for the probing policy, not for Predictive Sampling.

## A two-step control comparator

To distinguish predictive randomization from explicit information value, also evaluate a rolling two-period policy. Put

\[
\ell_i=\mu_i+\phi_i(m_i-\mu_i),\quad
b_i=|\phi_i|\sqrt{v_i},\quad C_i=\max_{j\ne i}\ell_j.
\]

If arm \(i\) is observed now, its next predictive mean has conditional distribution \(N(\ell_i,b_i^2)\). The other next predictive means are unchanged by this observation. Its exact two-period score is

\[
Q_i=m_i+C_i+\mathbb E[(N(\ell_i-C_i,b_i^2))_+].
\]

For \(z=(\ell_i-C_i)/b_i\), the positive-part expectation is \((\ell_i-C_i)\Phi(z)+b_i\varphi(z)\), with the deterministic limit when \(b_i=0\). Select the largest \(Q_i\) and repeat next round. This is optimal for a two-period terminal problem, not a proof of optimal long-run control. No discount or exploration multiplier is tuned in these experiments.

For two arms, the immediate conditional oracle gap of PS also has a closed form. With \(d=m_1-m_2\), \(u=\sqrt{v_1+v_2}\), and \(w=\sqrt{s_1^2+s_2^2}\),

\[
r_{\mathrm{PS}}(b)=
u\varphi(|d|/u)-|d|\Phi(-|d|/u)
+|d|\Phi(-|d|/w).
\]

The first two terms are the greedy immediate gap; the last is the immediate cost of predictive exploration. Long-run improvement must come from changing future beliefs, rather than improving the immediate reward at the same belief. Use limiting values when \(w=0\).

## Reproducible comparisons

The [experiment script](../../experiments/predictive_ar1.py) uses shared exogenous state trajectories across policies and independent replications. Non-oracle decisions are made before current innovations are generated; only the selected state enters their belief updates. All parameters are supplied, so these experiments isolate state tracking rather than parameter learning.

The primary sweep has five homogeneous zero-mean arms, stationary variance one, and persistence \(0,0.1,0.5,0.9,0.99,0.995\). Therefore innovation variance changes as \(q=1-\phi^2\). A separate case has four persistent arms and a high-variance white-noise arm, exposing information that cannot be retained. Comparators are fixed arm, greedy predictions, state-posterior Thompson Sampling, Predictive Sampling, rolling two-step control, deterministic refresh, and the stronger all-past-state observer.

Results are generated in [results/findings.md](results/findings.md), with raw replications, paired differences, cumulative curves, and metadata alongside it. Intervals are approximate 95% intervals over independent replications. They do not certify asymptotic optimality. The [working paper](manuscript.pdf) contains the model, derivations, bounds, and generated comparisons.

```sh
python3 experiments/predictive_ar1.py --verify
python3 experiments/predictive_ar1.py --runs 40 --horizon 30000 --burn 5000 --workers 4
python3 experiments/render_predictive_ar1.py
cd research/predictive_ar1
/Users/guoweisun/.local/bin/tectonic --only-cached --keep-logs manuscript.tex
```

For homogeneous zero-mean arms, multiplying all stationary and innovation variances by \(a^2\) multiplies the coefficients of these scale-equivariant policies by \(a\), without changing their decisions on correspondingly scaled trajectories. The strong-persistence, innovation-standard-deviation-0.01 example can therefore be obtained from the unit-stationary-variance case by multiplying its coefficients by \(\sqrt{10^{-4}/(1-0.99^2)}\). This is an exact scaling calculation, not an additional independent experiment.
