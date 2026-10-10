# From the similarity selection index to cumulative-regret bandits

Research note, 7 October 2026. Literature findings, original derivations, and candidate contributions are distinguished below. Novelty has not been established by an exhaustive search.

## 1. The precise continuation of the earlier work

[Sun, Li, and Fu (WSC 2019)](https://www.informs-sim.org/wsc19papers/422.pdf) represent alternatives as nodes of a similarity graph and define the spectral index by graph regularization:

```math
z_\lambda=\arg\min_z\|z-\bar y\|_2^2+\lambda z^\top Lz
=(I+\lambda L)^{-1}\bar y.
```

Here $`L`$ is the unnormalized Laplacian of an undirected graph with nonnegative weights. Their objective is final selection, evaluated through probability of correct selection (PCS). Order preservation is established under an aligned-graph condition; the general PCS-improvement statements are presented as conjectures, with numerical evidence.

[Sun's 2019 dissertation, *Topics in Stochastic Optimization*](https://drum.lib.umd.edu/bitstreams/ea092ea6-7422-4782-ab97-45b7a94fd90d/download) contains this construction in Chapter 2 and restless temporal bandits in Chapter 4.

[Zhou, Fu, and Ryzhov, *Sequential Learning with a Similarity Selection Index*](https://pubsonline.informs.org/doi/abs/10.1287/opre.2023.2478) develop allocations tailored to this selection score. The article appeared online in 2023 and in *Operations Research* 72(6), 2526–2542, in 2024. Their objective remains best-alternative selection.

[Zhou's 2023 dissertation](https://drum.lib.umd.edu/bitstreams/c2bd14eb-26b2-4a89-b395-a5db155efe7a/download), Section 2.2, calls the construction the S-index, supplies a relaxed alignment definition, and explicitly corrects a technical issue in the earlier order-preservation proof. Its analyzed allocation has positive limiting fractions for every alternative (Theorems 2.5–2.6). Copying such an allocation into a cumulative-reward problem would incur linear regret whenever a suboptimal arm receives a positive fraction of pulls.

Thus the proposed continuation is: use the S-index to make online allocation decisions, with regret charged for every suboptimal pull. Neither the graph representation nor the estimator alone supplies the new contribution.

## 2. Closest competing work

| Work | Relationship to this project |
|---|---|
| [Valko et al., *Spectral Bandits for Smooth Graph Functions*, ICML 2014](https://proceedings.mlr.press/v32/valko14.html) | Already treats arms as graph nodes and minimizes cumulative regret using smooth mean rewards and graph spectral structure. |
| [Kocak et al., *Spectral bandits*, JMLR 2020](https://www.jmlr.org/papers/v21/16-529.html) | Develops SpectralUCB, SpectralTS, and SpectralEliminator. The principal cumulative-regret comparison. |
| [Thaker et al., *Maximizing and Satisficing in Multi-armed Bandits with Graph Information*, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html) | Graph-based best-arm identification; helps locate the boundary between the earlier selection objective and cumulative regret. |
| [Mondal et al., *Graph Dimensionality Reduction for Contextual Bandits*, June 2026 preprint](https://arxiv.org/abs/2606.27917) | Studies spectral projection with approximate smoothness and noisy graphs. Relevant when claiming novelty for graph error or dimension reduction; its setting is contextual. |

Graph-similarity bandits should also be distinguished from feedback-graph bandits: a similarity edge does not mean that playing one arm directly observes its neighbors' rewards.

## 3. A stationary model to start with

There are $`K`$ arms with fixed means $`\mu\in[0,1]^K`$. Pulling arm $`a_t`$ reveals only

```math
Y_t=\mu_{a_t}+\epsilon_t.
```

For the first analysis, assume each arm has an iid reward stream with known sub-Gaussian noise proxy $`\sigma`$. A fixed graph represents similarity between the means, with a supplied valid bound

```math
\mu^\top L\mu\le S^2.
```

The graph structure need not introduce correlated observation noise. Define cumulative pseudo-regret in terms of the original means:

```math
R_T=\sum_{t=1}^T(\mu_* -\mu_{a_t}),\qquad
\Delta_i=\mu_* -\mu_i.
```

The following derivations do not cover temporally dependent observations.

## 4. A failure that the algorithm must address

Write $`Q_\lambda=(I+\lambda L)^{-1}`$. Even if all raw means are estimated perfectly, the fixed S-index converges to $`Q_\lambda\mu`$, which can have a different maximizer on a general graph.

For example, let $`\mu=(1,0.9,0)`$, connect only arms 1 and 3 with weight 1, and set $`\lambda=1`$. Then

```math
Q=\begin{pmatrix}2/3&0&1/3\\0&1&0\\1/3&0&2/3\end{pmatrix},
\qquad Q\mu=(2/3,0.9,1/3).
```

The best raw arm is 1; the best smoothed arm is 2. This deliberately misaligned graph illustrates why arbitrary fixed smoothing needs a bias correction or a justified rank-preservation assumption.

With deterministic rewards, a naive policy that adds the ordinary arm confidence bonus to this fixed S-index behaves like UCB on the wrong means. It pulls arm 2 on $`T-O(\log T)`$ rounds and incurs $`0.1T+O(\log T)`$ true regret.

The accompanying script reproduces the example with a conservative noise proxy $`\sigma=1`$, one initial sample per arm, and horizon-dependent confidence bounds:

```sh
python3 experiments/simulations/theory/graph_alignment/s_index_counterexample.py
```

| Policy | Regret at T=1,000 | T=10,000 | T=100,000 |
|---|---:|---:|---:|
| Ordinary UCB | 53.2 | 177.9 | 377.9 |
| Naive S-index + ordinary bonus | 131.9 | 1,046.5 | 10,053.6 |
| Bias-corrected intersection index below | 53.2 | 177.9 | 377.9 |

These are deterministic failure checks, not evidence of an improvement over UCB on informative graphs.

## 5. A candidate index with an elementary safety argument

After pulling every arm once, let $`n_i(t)`$ be its sample count before the next decision and $`\bar y_i(t)`$ its sample average. For a known horizon $`T`$, set

```math
r_i(t)=\sigma\sqrt{\frac{2\log(2KT/\delta)}{n_i(t)}}.
```

A union bound over arms and sample counts $`1,\ldots,T`$ ensures
$`|\bar y_i(t)-\mu_i|\le r_i(t)`$ simultaneously with probability at least $`1-\delta`$. This event remains valid under adaptive sampling; it does not assume that a stopped sample average is Gaussian.

The S-index error decomposes exactly as

```math
z_\lambda-\mu
=Q_\lambda(\bar y-\mu)-\lambda Q_\lambda L\mu.
```

The first term propagates sampling error; the second is smoothing bias. Since $`Q_\lambda`$ has nonnegative entries, the sampling term is bounded coordinatewise by $`(Q_\lambda r)_i`$. Cauchy–Schwarz and the supplied smoothness bound give

```math
b_i(\lambda)=\lambda S
\sqrt{(Q_\lambda LQ_\lambda)_{ii}},
\qquad
|z_{\lambda,i}-\mu_i|\le(Q_\lambda r)_i+b_i(\lambda).
```

A concrete candidate is

```math
U_i(t)=\min\left\{
\bar y_i(t)+r_i(t),
z_{\lambda,i}(t)+(Q_\lambda r(t))_i+b_i(\lambda)
\right\},\qquad
a_t\in\arg\max_i U_i(t).
```

Both terms inside the minimum are valid upper bounds under the stated assumptions. If a suboptimal arm $`i`$ is selected, then

```math
\mu_*\le U_*(t)\le U_i(t)
\le\bar y_i(t)+r_i(t)\le\mu_i+2r_i(t).
```

Consequently, on the confidence event,

```math
N_i(T)\le1+\frac{8\sigma^2\log(2KT/\delta)}{\Delta_i^2},
\quad
R_T\le\sum_{i:\Delta_i>0}\Delta_i
+8\sigma^2\log(2KT/\delta)
\sum_{i:\Delta_i>0}\frac1{\Delta_i}.
```

This is the standard gap-dependent UCB bound, not a demonstrated graph-dependent improvement or a claim of pathwise domination over ordinary UCB. With bounded means, the expected-regret bound adds at most $`\delta T`$ for the failure event.

The same raw confidence event supports taking the minimum across multiple smoothing strengths, including $`\lambda=0`$. It also permits data-dependent choices of $`\lambda`$ for fixed $`L`$, because the bound is a deterministic consequence of that event for every $`\lambda\ge0`$.

The smoothness bound must be valid. Including ordinary UCB in a minimum does not protect against an invalid graph upper bound. If only bounded means are known, the universal choice $`S^2=\sum_{i<j}w_{ij}`$ is valid, but may yield little information-sharing benefit. A graph estimated from the same observations needs a separately justified smoothness certificate.

## 6. Why sample-count weighting is a baseline

An alternative is to fit all observations directly:

```math
\hat\mu_t=\arg\min_f\sum_i n_i(t)(f_i-\bar y_i(t))^2
+\lambda f^\top Lf+\eta\|f\|_2^2
=(D_t+\lambda L+\eta I)^{-1}D_t\bar y_t,
```

where $`D_t=\mathrm{diag}(n_i(t))`$ and $`\eta>0`$. In the graph eigenbasis, this is regularized linear least squares with graph-frequency penalties. This puts the estimator in the same class as [SpectralUCB's estimator](https://jmlr.org/papers/volume21/16-529/16-529.pdf); adding its standard confidence bonus is an existing baseline.

With equal counts $`n`$ and $`\eta=0`$, the estimate reduces to $`(I+(\lambda/n)L)^{-1}\bar y`$. With unequal counts, it changes the original S-index and needs its own rank-preservation analysis.

## 7. Candidate contributions worth investigating

The most direct continuation is a regret analysis that exploits rank preservation of the original selection index. Suppose $`\theta=Q\mu`$ has the same unique best arm as $`\mu`$, and define

```math
\widetilde\Delta_i=\theta_* -\theta_i>0,
\qquad
\kappa=\max_{i:\Delta_i>0}\frac{\Delta_i}{\widetilde\Delta_i}.
```

For any action sequence, original-mean regret is at most $`\kappa`$ times regret measured with $`\theta`$. However, observations still have means $`\mu_i`$, so the learner cannot treat $`\theta_i`$ as directly observed arm rewards.

For comparing two smoothed scores, the raw confidence event gives the sharper bound

```math
|(z_i-z_j)-(\theta_i-\theta_j)|
\le\sum_k|Q_{ik}-Q_{jk}|r_k.
```

This exposes cancellation of shared estimation error. A potential contribution would couple these pairwise bounds to a sampling rule that accounts for the regret cost of obtaining information. The research question is whether the resulting regret bound can reflect transformed gaps, graph geometry, and alignment errors, and improve on SpectralUCB under a clearly different structural assumption. This is a candidate direction, not a verified open problem.

A second direction is adaptive smoothing with valid confidence bounds: demonstrate graph-dependent gains when similarity is reliable and quantify degradation when it is inaccurate. Unknown-graph or unknown-smoothness claims need careful comparison with existing literature.

## 8. Next experiments and temporal extension

Benchmark ordinary UCB, naive S-index UCB, the certified index, and SpectralUCB on clustered means, graph-smooth means, aligned graphs, and graphs with perturbed or incorrect edges. Generate learned graphs only from available features and selected-arm observations; reserve oracle graphs as explicitly labeled controls. Vary gaps, graph strength, and noise. Measure original cumulative regret, uncertainty coverage, sample allocation, and runtime across repeated noisy trials.

The initial all-arm sampling requirement is a limitation when $`K`$ is large; avoiding it needs stronger structural assumptions or another estimator.

Temporal dependence can subsequently be introduced through a graph-spectral state model, $`f_t=U\alpha_t`$, $`\alpha_{t+1}=A\alpha_t+\xi_t`$, with scalar observations at selected nodes. This requires state prediction, uncertainty from unobserved evolution, and a new regret benchmark. Compare with [time-varying GP bandits](https://proceedings.mlr.press/v51/bogunovic16.html). Regret against a fully observed latent-state oracle may have an irreducible linear component; a known-model policy receiving the same kind of feedback is another possible benchmark.
