# Temporal dependence, prediction, and bandit regret

Literature checked on 8 October 2026. This is a research map and a proposed starting model, rather than a new regret theorem.

## 1. The effect we want to study

Pulling an arm can serve three purposes: collect its current reward, learn persistent parameters such as its long-run mean, and refresh our knowledge of its changing state. The third purpose remains relevant even when the parameters are known.

The crucial modeling choice is the clock. In a **rested** model, an arm advances only when pulled; its unobserved state freezes. In a **restless** model, every arm advances each calendar round. The proposed loss of predictive information during inactivity belongs most directly to a partially observed restless bandit.

An ergodic AR or Markov process can have a stationary marginal distribution while its conditional reward forecast changes over time. Literature using “nonstationary” latent reward means therefore overlaps with literature using “stationary” temporally dependent processes. Model equations and observation timing are more informative than these labels.

## 2. A transparent AR(1) starting model

Take independent arms evolving in calendar time:

\[
X_{i,t}=\mu_i+\phi_i(X_{i,t-1}-\mu_i)+\eta_{i,t},
\qquad \eta_{i,t}\sim N(0,q_i),\quad q_i>0,\quad |\phi_i|<1.
\]

Innovations are independent across arms and time. Choose an arm before observing its current state, receive reward \(X_{i,t}\), and observe that state exactly. Unplayed arms keep evolving. The formulas below are elementary calculations for this model, not claims from a new bandit theorem.

If the last observation was \(X_{i,\tau}=x\), its age is \(h=t-\tau\geq1\), and parameters are known, then

\[
m_i(h)=\mu_i+\phi_i^h(x-\mu_i),\qquad
v_i(h)=q_i\sum_{j=0}^{h-1}\phi_i^{2j}
=\frac{q_i(1-\phi_i^{2h})}{1-\phi_i^2}.
\]

The forecast mean reverts toward the long-run mean; its variance increases with age and approaches the stationary variance \(V_i=q_i/(1-\phi_i^2)\). For a rested arm, calendar inactivity does not increase this transition count.

With noisy observations \(Y=X+\epsilon\), \(\operatorname{Var}(\epsilon)=r_i\), the state posterior variance after observation is

\[
P^+=\frac{P^-r_i}{P^-+r_i},\qquad
P(h)=\phi_i^{2h}P^++q_i\sum_{j=0}^{h-1}\phi_i^{2j}.
\]

The reward's predictive variance also includes measurement noise if the noisy measurement itself is the payoff. Process noise and measurement noise should be specified separately.

Parameter uncertainty is a different quantity. With known \(\phi_i,q_i\), unknown \(\mu_i\), and an exact last state observation, the law of total variance gives

\[
\operatorname{Var}(X_{i,t}\mid H_t)
=v_i(h)+(1-\phi_i^h)^2\operatorname{Var}(\mu_i\mid H_t).
\]

More generally it gives \(\mathbb E_\theta[v_i(h;\theta)\mid H_t]+\operatorname{Var}_\theta(m_i(h;\theta)\mid H_t)\), with the conditional state uncertainty included in \(v_i\). Parameter learning can reduce the second term; innovations continually replenish the first.

### Correlation has opposing effects

At fixed stationary variance \(V_i\), positive persistence makes a recent observation useful for longer:

\[
v_i(h)/V_i=1-\phi_i^{2h}.
\]

However, for a stationary consecutively observed AR(1) sequence,

\[
n\operatorname{Var}(\bar X_n)\longrightarrow
V_i\frac{1+\phi_i}{1-\phi_i}
=\frac{q_i}{(1-\phi_i)^2}.
\]

Thus the large-sample effective count for estimating the mean is approximately \(n(1-\phi_i)/(1+\phi_i)\). This calculation concerns consecutive stationary observations, not a confidence bound for arbitrary adaptive sampling. At \(\phi=0.95\), that ratio is about 0.026, while a five-round-old exact observation still leaves only \(1-0.95^{10}\approx0.401\) of the stationary state variance unresolved.

The [formula illustration](temporal_information.svg), [plotted values](temporal_information.csv), and [regeneration script](../experiments/temporal_information.py) hold stationary variance fixed. Holding innovation variance fixed instead changes the marginal reward scale as persistence changes. Neither comparison supports a universal claim that more correlation always lowers regret.

### Sampling gaps also change learning information

For two models with the same known \(\phi,q\) and means differing by \(d\), the conditional KL divergence of an exact state observation after gap \(h\) is

\[
I_h(d)=\frac{(1-\phi^h)^2d^2}{2v(h)}
=\frac{d^2}{2V}\frac{1-\phi^h}{1+\phi^h}.
\]

For positive \(\phi\), a longer gap increases mean-identification information **per observation**, while the previous observation becomes less useful for tracking the state. The information per calendar round and the opportunity cost must also be accounted for. This identity supplies an ingredient for a lower-bound argument, not a complete lower bound.

## 3. Choose the regret comparator first

| Comparator | What it measures | Consequence |
|---|---|---|
| Best fixed arm by stationary mean | Learning a persistent arm ranking | Logarithmic weak regret can be possible, even for restless Markov rewards. It can miss the value of state-dependent switching. |
| Optimal causal policy knowing parameters, with the same feedback limits | Learning how to act under partial observation | Sublinear learning regret can be possible. The comparator itself must monitor and revisit arms. |
| Oracle observing all current states | Learning plus the cost of hidden, continually changing states | Fixed innovation noise can create linear regret even with known parameters. |

For our exogenous-state model, define \(V_T^{\mathrm{full}}\) and \(V_T^{\mathrm{causal}}\) as optimal expected cumulative rewards under full current-state observation and under the learner's observation restrictions, respectively, with parameters known. Then

\[
V_T^{\mathrm{full}}-V_T^\pi
=\underbrace{V_T^{\mathrm{full}}-V_T^{\mathrm{causal}}}_{\text{price of partial observation}}
+\underbrace{V_T^{\mathrm{causal}}-V_T^\pi}_{\text{learning and control error}}.
\]

Each policy has its own observation history. This finite-horizon identity does not identify the comparator with a myopic policy on the learner's history. Papers using an optimal long-run average reward use a related comparator with their own transient terms.

For an elementary illustration, let two arms have independent states \(N(0,V)\) each round (\(\phi=0\)). Any causal policy collecting a reward before seeing current states has expected reward zero. A full-state oracle has expected reward \(\sqrt{V/\pi}\) per round. Its regret is exactly \(T\sqrt{V/\pi}\), even with all parameters known; regret relative to the best fixed mean is zero. This is a counterexample to demanding sublinear full-state regret in every such model.

## 4. Closest autoregressive research

**Chen, Golrezaei, and Bouneffouf, “Non-Stationary Bandits with Auto-Regressive Temporal Dependency,” NeurIPS 2023.** AR2 alternates exploitation and triggered exploration of stale arms, with restarts, in a truncated AR(1) mean model. Its full-current-mean comparator gives per-round lower bound \(\Omega(\alpha\sigma g(K,\alpha,\sigma))\), where \(g\) is the stationary probability of a near tie between the best two arms. Its upper bound is \(\widetilde O(K^3\alpha^2\sigma^2)\) when \(\alpha\geq1/2\) and \(K\leq\lfloor(\log(1/8)/\log\alpha+1)/2\rfloor\). Noise timing differs from our model. [Paper, Theorems 3.1 and 5.2](https://proceedings.neurips.cc/paper_files/paper/2023/file/186a213d720568b31f9b59c085a23e5a-Paper-Conference.pdf).

The authors also [report acceptance in Mathematics of Operations Research in 2026](https://qinyic.com/), under “Learning to Adapt in Non-Stationary Bandits with Autoregressive Temporal Structure.” The bounds above are from the verified conference version, rather than an unverified journal revision.

**Liu, Van Roy, and Xu, “Nonstationary Bandit Learning via Predictive Sampling,” AISTATS 2023.** Predictive Sampling explicitly values information by its remaining useful lifetime. It includes independent latent Gaussian AR(1) arms with separate process and observation noise. Its Bayesian bound depends on cumulative predictive information and can be linear with persistent change. Its comparator uses future information, rather than the optimal causal policy above. [Proceedings](https://proceedings.mlr.press/v206/liu23e.html), [model and theorem](https://proceedings.mlr.press/v206/liu23e/liu23e.pdf).

**Bacchiocchi et al., “Autoregressive Bandits,” AISTATS 2024.** AR-UCB has regret \(\widetilde O((p+1)^{3/2}\sqrt{KT}/(1-\Gamma)^2)\), hiding fixed reward/noise scales. Here \(\Gamma<1\) controls stability. The model is one observed AR(\(p\)) reward process with action-dependent coefficients; it is not a collection of independent hidden trajectories. The bound concerns learning an optimal controller under the paper's coefficient assumptions. [Proceedings and paper](https://proceedings.mlr.press/v238/bacchiocchi24a.html).

**Trella et al., “Non-Stationary Latent Auto-Regressive Bandits,” Reinforcement Learning Journal / RLC 2025.** LARL learns reward and AR parameters using a Kalman-filter-inspired reduction to linear contextual bandits. Arms share a latent AR state. Published Theorem 4.2 separates a full-state tracking term, learning, and approximation bias. Fixed process noise leaves a linear term; sublinear full-state regret needs sufficiently shrinking process noise and the remaining conditions. [Published paper](https://rlj.cs.umass.edu/2025/papers/RLJ_RLC_2025_70.pdf). An unconditional square-root claim from an earlier abstract should not replace this theorem.

## 5. Markovian results and temporal dependence in their bounds

**Anantharam, Varaiya, and Walrand, IEEE Transactions on Automatic Control, 1987, Part II: Markovian Rewards; Moulos, NeurIPS 2020.** For suitable rested finite-state Markov families, logarithmic regret against the best stationary mean has matching asymptotic information constants. Moulos supplies a finite-time round-robin KL-UCB analysis, including multiple plays, for a one-parameter exponential family with regularity conditions. [1987 paper](https://people.eecs.berkeley.edu/~ananth/1987-1989/Pravin/MarkovMultiarmedbandit.pdf), [2020 paper](https://proceedings.neurips.cc/paper/2020/file/597c7b407a02cc0a92167e7a371eca25-Paper.pdf).

For fully observed state transitions, the relevant information rate is

\[
D(P\Vert Q)=\sum_{x,y}\pi_P(x)P(x,y)
\log\frac{P(x,y)}{Q(x,y)}.
\]

In regular single-play settings, the lower-bound structure is

\[
R_T\ \gtrsim\ \sum_{i:\Delta_i>0}
\frac{\Delta_i}{\inf_{Q:\mu(Q)>\mu_*}D(P_i\Vert Q)}\log T.
\]

This involves transition information, rather than only KL between marginal rewards. The achievable exact statement is family-dependent. With hidden states or reward emissions that conceal transitions, the observed-data information rate must be used instead.

**Tekin and Liu, “Online Learning of Rested and Restless Bandits,” IEEE Transactions on Information Theory, 2012.** UCB-M and regenerative-cycle methods yield logarithmic weak regret against the best fixed stationary arm. Constants involve chain properties, including spectral gaps and return behavior. These results do not establish logarithmic regret against the optimal policy that exploits changing states. [Author manuscript](https://arxiv.org/abs/1102.3508).

**Ortner, Ryabko, Auer, and Munos, “Regret bounds for restless Markov bandits,” Theoretical Computer Science, 2014 (earlier ALT 2012).** Arms evolve while unplayed; a selected arm reveals its state. The sufficient statistic is the last state and elapsed time, giving a belief through \(P_i^h\). Against a known-transition policy with the same observation limits, the paper gives \(\widetilde O(\sqrt T)\) regret with substantial state-space, mixing, and diameter factors, and an \(\Omega(\sqrt{ST})\) lower bound for total state count \(S\). The temporal factors are not all matched. [Published author copy](https://daniil.ryabko.net/mabajr.pdf).

**Jiang et al., “Online Restless Bandits with Unobserved States,” ICML 2023.** States remain hidden even after a pull; both transitions and reward emissions are unknown. TSEETC achieves \(\widetilde O(\sqrt T)\) Bayesian regret against the known-parameter, partially observed optimal average reward. Assumptions include finite state/reward sets and strictly positive transitions and emissions. Constants depend on positivity and bias-span quantities, and the algorithm requires a planning oracle. [Proceedings](https://proceedings.mlr.press/v202/jiang23d.html), [Theorem 5.1](https://proceedings.mlr.press/v202/jiang23d/jiang23d.pdf).

For our fully observed-at-pull Markov model, a gap-dependent likelihood contribution is \(\mathrm{KL}(P_i^h(x,\cdot)\Vert Q_i^h(x,\cdot))\). Thus sampling schedules themselves affect learning information. A mixing-time multiplier alone need not capture this structure.

## 6. Recent pointers with different guarantees

- Keqin Liu, **“Relaxed Indexability and Index Policy for Partially Observable Restless Bandits,” Management Science 71(12), 2025**: planning and index computation for known models. This should not be cited as an unknown-parameter learning-regret theorem. [Journal page](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.2022.02831).
- Piray, **“Not all uncertainty is alike: volatility, stochasticity, and exploration,” May 2026 preprint**: separates volatility from observation stochasticity and studies information incentives. The preprint does not establish a restless-bandit regret theorem. [Preprint](https://arxiv.org/abs/2605.19215).

## 7. A concrete research direction

The broad claim that stale arm information matters is established, especially by Predictive Sampling and AR2. A useful contribution would need a more specific model, comparator, and improved dependence in a proved bound.

Start with the independent restless AR(1) model in Section 2, initially with known \(\phi_i,q_i\) and unknown bounded means \(\mu_i\). Use a common specified initialization for the learner and comparator, for example independent stationary states conditional on the parameters. Permit heterogeneous persistence and innovation variances. This isolates parameter learning from state tracking. Treat the all-known case as a necessary planning baseline; later add noisy observations and unknown dynamics.

Use the optimal causal known-parameter policy as the main regret comparator and separately quantify its gap to the full-state oracle. The first target is to characterize how persistence, innovation noise, observation age, and decision gaps jointly enter these two quantities. We have not established a new matching upper/lower theorem for that target.

The policy should maintain each arm's predictive mean and variance together with parameter uncertainty. For known parameters, a finite-horizon belief-state recursion is

\[
V_t(b)=\max_i\left\{m_i(b)+
\mathbb E[V_{t+1}(\mathcal T(b,i,Y_i))\mid b]\right\},
\]

where \(\mathcal T\) incorporates observation of the selected arm and temporal propagation of every arm. The continuation term contains the value of refreshing state knowledge. A policy based only on the immediate predictive mean can neglect this value. A bonus growing only with variance can overvalue information that expires before it can improve decisions.

A practical study should compare stationary UCB, greedy Kalman predictions, Thompson Sampling, Predictive Sampling, AR2 where its noise model applies, and a numerical belief-state planning benchmark for a small number of arms. Sweep persistence and process noise separately; perform both fixed-stationary-variance and fixed-innovation-variance comparisons. Report causal learning regret and full-state tracking regret separately, together with observation ages.

For theory, the natural first lower-bound object is the conditional likelihood accumulated across adaptive observation gaps, illustrated by \(I_h\) above. Its information constraints must be coupled to the cost of acting under stale beliefs. Any computational planning approximation should have a separate cumulative error term. Extending to a shared latent state would later connect this direction to cross-arm dependence, but it changes the information structure and requires its own analysis.

Suggested first reading: Predictive Sampling for the value-of-information viewpoint, AR2 for an explicit dependence on persistence and innovation noise, and Ortner et al. for the causal restless comparator and Markov belief representation.

## 8. Follow-up: minimize the full-state linear coefficient

The selected follow-up direction is now the full-current-state comparator: minimize the coefficient of its unavoidable linear regret. The [AR(1) development](predictive_ar1/README.md) specializes Gaussian Predictive Sampling, derives a positive full-past-information lower bound and a constructive refresh-policy upper bound, and compares policies on common simulated trajectories. The causal comparator above remains useful for separating learning from monitoring, while this follow-up deliberately studies the stronger oracle.

The updated development also derives exact finite-horizon belief control and a conditional average-reward Bellman formulation. A residual certificate bounds a candidate's linear coefficient relative to the optimum, provided the residual is controlled globally and a terminal-value condition holds. An additional lifetime-weighted knowledge-gradient comparison improves on PS at moderate persistence but loses at high persistence. The [working paper](predictive_ar1/manuscript.pdf) distinguishes exact characterization, conditional certification, and empirical policy comparisons; no computed average-optimal policy is claimed.
