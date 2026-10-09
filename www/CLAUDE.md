# Cross-Arm Dependent Bandits for Web Recommendation: Research Proposal

As of 9 October 2026. Working title: *Which Graph Should a Bandit Trust? Measuring and Certifying Cross-Arm Dependence on the Web*.

## Summary

We propose a WWW paper asking **which cross-arm graph a bandit should trust** in web recommendation, and how much regret a valid or invalid graph buys.

Web platforms expose many candidate arm graphs at once: content similarity, category trees, co-purchase links, price ladders, geography and learned embeddings. Spectral bandits take one graph as given and assume rewards are smooth on it. We will build a benchmark of seven dependency types on public datasets where every arm's mean reward is known. On it we measure how well each real graph aligns with the true rewards, and test whether the alignment theory in this repo predicts which algorithm wins.

Temporal (within-arm) dependence is deliberately out of scope until the general model replaces AR(1).

## Motivation and gap

The gap is empirical: no one has measured whether real web graphs satisfy the smoothness assumptions that spectral-bandit guarantees need. Prior spectral-bandit experiments use one graph per dataset and report regret, not graph validity ([Valko et al., ICML 2014](https://proceedings.mlr.press/v32/valko14.html); [Kocák et al., JMLR 2020](https://www.jmlr.org/papers/v21/16-529.html)).

Three problems make this matter on the web:

- **Many graphs compete.** One catalogue yields a category tree, an also-bought graph and an embedding kNN graph. These can disagree about which items are close.
- **Some edges mean the opposite of similarity.** Bought-together links usually join complements, such as a phone and its case. Complements can have very different click or purchase rates, so smoothing over them biases the estimates.
- **Wrong graphs cause linear regret.** The repo's counterexample ([graph_spectral_bandits.md](../research/graph_spectral_bandits.md), Section 4) shows a misaligned graph can make a smoothed index pick a suboptimal arm forever. The [manuscript](../research/alignment_paper/manuscript.pdf) prices this with a certified energy bound, but only on synthetic graphs.

Recent work adds noisy-graph penalties ([Mondal et al., 2026](https://arxiv.org/abs/2606.27917)) and multi-user graph kernels ([Wu and Amini, ICLR 2026](https://arxiv.org/abs/2601.00461)). Neither reports how aligned real graphs are with the rewards. A measured benchmark of graph alignment is the contribution WWW reviewers can use.

## Cross-arm dependency types and applications

Seven dependency types map onto public web datasets; three have exact or unbiased per-arm means, which is what a regret study needs. Rows are sorted by how cleanly they can be evaluated.

| # | Dependency type (graph shape) | Web application | Arms | Public dataset | Graph source, built without rewards | Per-arm ground truth | Expected alignment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Content similarity (kNN graph) | Short-video feed slot | Videos, or tag clusters | [KuaiRec](https://arxiv.org/abs/2202.10842): 1,411 users × 3,327 videos, nearly fully observed | Video tags; caption embeddings | Exact | Moderate; varies by user segment |
| 2 | Variant similarity (small dense graph) | Headline and thumbnail A/B tests | Packages within one test | [Upworthy Research Archive](https://upworthy.natematias.com/about-the-archive): 32,487 tests, 150,817 arms | Text embeddings of headlines; shared image | Exact (randomized aggregate clicks per arm) | Unknown; measured across thousands of instances |
| 3 | Category hierarchy (tree) | Fashion eCommerce carousel | Items (80 / 34 / 46 by campaign) | [Open Bandit Dataset](https://arxiv.org/abs/2008.07146) (ZOZOTOWN) | Item category and attribute features | Unbiased (uniform-random logging policy) | High within a leaf category, low across |
| 4 | Ordinal ladder (path) | Dynamic pricing; bid and reserve levels | Price points or bid levels | [iPinYou RTB logs](https://arxiv.org/abs/1407.7073); M5 / Dominick's sales | Adjacency of price or bid values | Semi-synthetic (fitted win-rate or demand curve) | High: demand and win rate vary smoothly with price |
| 5 | Knowledge-graph entities (embedding kNN) | News recommendation | Articles, or topic subcategories | [MIND](https://learn.microsoft.com/en-us/azure/open-datasets/dataset-microsoft-news): 65,238 articles, WikiData entity embeddings | TransE entity embeddings; categories | Biased logs; Yahoo! R6 gives a uniform-random alternative | Moderate; topic drives click rate |
| 6 | Geographic proximity (spatial kNN) | Local services and point-of-interest suggestions | Venues, or map cells | Yelp Open Dataset; Foursquare check-ins | Distance between venues | Semi-synthetic from ratings and check-ins | High for some categories, such as restaurants in one area |
| 7 | Complement and substitute links (signed graph) | Bundle and cross-sell widgets | Products | [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/), bought-together field | Bought-together and also-viewed links | Semi-synthetic from ratings (self-selected) | Low: complements violate smoothness, a natural stress test |

A related setting uses a graph over users, not arms (Last.fm and Delicious social graphs, as in multi-user graph bandits). It is cited for contrast, not benchmarked. Upworthy tests from 25 June 2013 to 10 January 2014 are excluded because the archive authors found randomization problems in that window.

## Algorithm families and where they apply

Every structured bandit shrinks the search space by restricting the vector of arm means μ. They differ in what the restriction is, and so in how it fails when it is wrong. The graph energy bound in this repo is one case: it is a kernel-norm ball with kernel (L + εI)⁻¹. SpectralUCB is a linear bandit in the Laplacian eigenbasis.

| Family | Restriction on μ | Representative algorithms | Input needed | Search space shrinks from K arms to | Failure when misspecified | Application rows |
| --- | --- | --- | --- | --- | --- | --- |
| Unstructured baselines | None | UCB1, KL-UCB, Thompson sampling | Nothing | K (no reduction) | None | All (reference) |
| Linear in arm features | μ = Xθ, θ ∈ ℝᵈ | [LinUCB](https://arxiv.org/abs/1003.0146), OFUL, [LinTS](https://arxiv.org/abs/1209.3352) | Feature vector per arm | d dimensions | Bias equal to the best linear fit's error; linear regret if the argmax changes | 1, 2, 3, 5 |
| Generalized linear | μ = g(Xθ), e.g. logistic | GLM-UCB (Filippi et al. 2010), [UCB-GLM](https://arxiv.org/abs/1703.00048), logistic TS | Features; binary rewards | d dimensions | As linear; better calibrated for low click rates | 1, 2, 3, 5 |
| Low-rank or bilinear | μ(u, i) = x_uᵀΘ z_i, Θ low rank | [ESTR / LowOFUL](https://arxiv.org/abs/1901.02470), matrix-completion bandits | User and item features | about (d₁ + d₂)·r | Rank too small merges distinct tastes | 1 (user × video) |
| Kernel or Gaussian process | μ in an RKHS ball of norm B | [GP-UCB](https://arxiv.org/abs/0912.3995), [KernelUCB](https://arxiv.org/abs/1309.6869), IGP-UCB, GP-TS | Kernel on arm features | Effective dimension of the kernel | Norm B underestimated gives overconfidence | 1, 2, 4, 5, 6 |
| Neural | μ = f_w(x), f a network | [NeuralUCB](https://arxiv.org/abs/1911.04462), [NeuralTS](https://arxiv.org/abs/2010.00827), NeuraLinear | Raw features, e.g. text or LLM embeddings | Effective dimension of the network's tangent kernel | Poor uncertainty estimates early | 2, 5, 7 |
| Graph over arms | μᵀLμ ≤ S² | [SpectralUCB / TS / Eliminator](https://www.jmlr.org/papers/v21/16-529.html), [GRUB](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html) (best-arm identification); this repo's SP-UCB, GDE-UCB | A weighted graph | Effective dimension of the graph | Linear regret on misaligned graphs (repo counterexample) | 1, 3, 5, 6, 7 |
| Lipschitz or metric | \|μ_i − μ_j\| ≤ d(i, j) | [Zooming](https://arxiv.org/abs/1312.1277), HOO | A distance between arms | Zooming dimension near the optimum | Lipschitz constant too small | 4, 6 |
| Unimodal on a graph | One peak along the graph | [OSUB](https://proceedings.mlr.press/v32/combes14.html), unimodal TS | Graph (often a path or grid) | Neighbours of the best arm only; regret independent of K | Several peaks trap the policy at a local maximum | 4 |
| Clusters or hierarchy | Arms share a cluster or category mean, plus noise | [Two-level policies](https://icml.cc/imls/conferences/2007/proceedings/abstracts/388.htm) (Pandey et al.), [HierTS](https://proceedings.mlr.press/v162/hong22a.html), Clus-UCB, latent bandits | Cluster labels or a category tree | Number of clusters, then arms within the best ones | Heterogeneous clusters hide good arms | 3, 5, 7 |
| Explicit correlation | Pseudo-reward bounds, or a correlated Gaussian prior | [C-UCB, C-TS](https://arxiv.org/abs/1911.03959), correlated-prior TS | Pseudo-reward table or prior covariance | Competitive arms only; others pulled O(1) times | Wrong bounds can rule out the best arm | 2, 4, 7 |
| General structure | Any known set of feasible μ | [OSSB](https://proceedings.neurips.cc/paper/2017/hash/e19347e1c3ca0c0b97de5fb3b690855a-Abstract.html) | The set itself | Matches the instance lower bound | As the stated structure | Reference for lower bounds |
| Ranked slates | Click model over positions plus any family above | [CascadeLinTS / CascadeLinUCB](https://arxiv.org/abs/1603.05359) | Position model | As the inner family | Click-model bias | 1, 3 (Open Bandit Dataset shows 3 positions) |

Graphs over users, not arms, form a separate family: [GOB.Lin](https://arxiv.org/abs/1306.0811), [CLUB](https://proceedings.mlr.press/v32/gentile14.html), [Graph Neural Bandits](https://arxiv.org/abs/2308.10808) and [Laplacian Kernelized Bandit](https://arxiv.org/abs/2601.00461). They need per-user rewards and a social or similarity graph. KuaiRec, which has per-user rewards and a social network file, is the only listed dataset that supports them.

### Which algorithms to run on each application

| # | Application | Main families to compare | Why these | Inputs to build |
| --- | --- | --- | --- | --- |
| 1 | Short-video feed (KuaiRec) | Linear or GLM on tags; GP on caption embeddings; graph on tag kNN; low-rank user × video; graph over users | The fully observed matrix lets every family be scored exactly, including misspecification error | Tag one-hot vectors, caption embeddings, kNN graph, user social graph |
| 2 | Headline A/B tests (Upworthy) | LinTS or GP on LLM headline embeddings; neural TS; correlated-prior TS; graph on embedding kNN | Few arms per test, so per-test structure must come from a model trained on other tests | Embeddings of headline text; a prior fitted on held-out tests |
| 3 | Fashion carousel (Open Bandit Dataset) | HierTS or two-level policies on the category tree; LinUCB on item features; CascadeLinTS for 3 positions | The catalogue already supplies a tree and features; the production system used Bernoulli TS | Category tree, item feature vectors, position index |
| 4 | Pricing and bid levels (iPinYou, M5) | OSUB and unimodal TS; Zooming; GP-UCB on a 1-D price kernel; GDE-UCB on the path | Revenue is usually single-peaked in price, a stronger shape than smoothness | Price or bid ladder, fitted win-rate or demand curve |
| 5 | News (MIND, Yahoo! R6) | LinUCB (the original WWW 2010 setting); GP on entity embeddings; HierTS on subcategories | Direct comparison with LinUCB on its home dataset | Article features, entity embeddings, category tree |
| 6 | Local services (Yelp) | GP with a spatial kernel; Zooming on geographic distance; graph on venue kNN | Spatial correlation in the literal sense; kernels on coordinates are standard | Venue coordinates, attributes |
| 7 | Bundles and cross-sell (Amazon) | C-UCB with pseudo-rewards; neural TS on text; graph on co-purchase as a stress test | Complement links break smoothness; correlation bounds or learned models may survive where graphs fail | Bought-together graph, product text embeddings |

**A unifying measurement.** For each family we can measure misspecification on the true μ, as the graph energy ratio does for graphs:

- Linear and GLM: the largest error of the best fit, relative to the gap Γ
- Kernel: the RKHS norm of μ relative to Γ
- Lipschitz: the smallest valid Lipschitz constant relative to Γ divided by the diameter
- Unimodal: the number of local maxima
- Clusters: the spread within clusters relative to Γ

Where the true μ is known (KuaiRec, Upworthy), this gives one table: rows are families, columns are datasets, cells are misspecification. The repo's alignment theory then predicts regret gain across all families, not only graphs.

## Research questions and hypotheses

1. **How aligned are real web graphs?** For each dataset and candidate graph, compute the graph energy of the true means, scaled by the gap to the best arm, and the resistance radius.
    - H1: alignment differs more across graph types on one dataset than across datasets for one graph type.
    - H2: complement graphs (row 7) score worst; ordinal ladders (row 4) score best.
2. **Do the alignment numbers predict which algorithm wins?** Regress each graph-aware algorithm's regret gain over UCB on the measured alignment.
    - H3: the gain is positive only below an energy-to-gap threshold of about one, as the manuscript's bound suggests.
3. **Is certification worth its cost?** Compare SpectralUCB, which trusts the graph fully, with GDE-UCB and the S-index pooling policy, which fall back to per-arm UCB.
    - H4: certified policies lose little on aligned graphs and avoid linear regret on misaligned ones.
4. **Which graph should a practitioner pick?** Test whether a short uniform warm-up can estimate alignment well enough to choose among candidate graphs.
    - H5: the selected graph's regret is within 10% of the best graph chosen in hindsight.
5. **Does misspecification predict regret across model families, not just graphs?** Use the unifying measurement to compare linear, kernel, graph, unimodal and cluster models on the same instances.
    - H6: on each instance the family with the smallest misspecification relative to Γ has the lowest regret more often than the family with the smallest nominal dimension.

## Methods

Every algorithm sees the same arms and noise. They differ only in the restriction they place on μ (see the algorithm families table). The core set, run on every dataset, is:

- Baselines: UCB1, KL-UCB, Bernoulli Thompson sampling
- Feature models: LinUCB, LinTS, logistic TS
- Kernel: GP-UCB with a feature kernel, and with the graph kernel (L + εI)⁻¹
- Graph: SpectralUCB, SpectralTS
- Certified graph policies from this repo: S-index pooling (SP-UCB) and GDE-UCB, which fall back to per-arm UCB
- Clusters: HierTS on the category tree, or on graph communities where no tree exists

Shape-specific families (OSUB, Zooming, C-UCB, CascadeLinTS, NeuralTS) run only on the applications they fit, per the table above.

**Graph construction.** Each graph is built from metadata only: tags, categories, text or entity embeddings, coordinates, prices or co-purchase links. kNN graphs use k in {5, 10, 20} with Gaussian edge weights. No reward data enters the graph, so alignment is a property we measure, not one we tune.

**Alignment diagnostics.** For true means μ, best-arm gap Γ and Laplacian L, we report the energy ratio and the resistance radius from the manuscript:

$$
\text{energy ratio} = \frac{\sqrt{\mu^\top L \mu}}{\Gamma}, \qquad
\rho_L = \min_{p \in \Delta_K} \max_i \sqrt{(e_i - p)^\top L^\dagger (e_i - p)}
$$

We also report the fraction of arms whose ranking flips after smoothing with (I + λL)⁻¹. That count is the empirical version of the repo's misalignment counterexample.

**Certified graph error.** For candidate graphs we estimate a spectral comparison factor η against a reference graph. The manuscript's result then gives the inflated energy radius. We report how often that radius is still small enough to help.

## Experimental protocol

The study uses three tiers of evaluation fidelity, and every result is labelled with its tier.

| Tier | Datasets | How an instance is built | What is exact |
| --- | --- | --- | --- |
| Exact simulation | KuaiRec, Upworthy | KuaiRec: one user cluster, 100 to 500 sampled videos as arms. Upworthy: one A/B test, its packages as arms. | True means, so regret and alignment are exact |
| Unbiased replay | Open Bandit Dataset, Yahoo! R6 | Replay of uniform-random logs | Average reward; regret only against the best fixed arm |
| Semi-synthetic | iPinYou, M5, MIND, Yelp, Amazon | Fitted reward model per arm, then simulated Bernoulli or Gaussian rewards | Only relative to the fitted model |

**Rewards.** Clicks are Bernoulli. KuaiRec uses a watch ratio above 2 as a positive, following common practice for that dataset. iPinYou rewards are click value minus the price paid, from logged market prices.

**Settings.** Horizons from 10,000 to 100,000 rounds and 50 seeds per instance. Graph-aware methods get the same λ grid, chosen on held-out instances.

**Metrics.**

- Cumulative regret at the horizon, and its ratio to UCB1
- Energy ratio, resistance radius and smoothing rank flips for each graph
- Correlation between alignment and regret gain across all instances (RQ2)
- Share of instances where a certified policy beats both UCB1 and SpectralUCB (RQ3)

Upworthy contributes tens of thousands of small real instances, so RQ2 can be answered with a scatter plot over real tests, not a handful of datasets.

## Expected contributions and novelty boundary

The paper's claim is a measurement and benchmark contribution backed by the repo's theory, not a new regret bound.

1. **A cross-arm dependency benchmark** of seven graph types on public web data, with labelled evaluation tiers and released code.
2. **Measured alignment statistics, which we have not found in prior work,** for real recommendation graphs: energy ratio, resistance radius and smoothing rank flips.
3. **Evidence on whether alignment predicts regret gain**, using thousands of real Upworthy tests as instances.
4. **A practical graph-selection rule** for choosing among candidate graphs after a short warm-up.

| Closest work | What it covers | What this paper adds |
| --- | --- | --- |
| [Valko et al. 2014](https://proceedings.mlr.press/v32/valko14.html); [Kocák et al. 2020](https://www.jmlr.org/papers/v21/16-529.html) | Spectral bandits, effective dimension, one graph per dataset | Many graphs per dataset; alignment measured, not assumed |
| [Mondal et al. 2026](https://arxiv.org/abs/2606.27917) | Noisy-graph penalty for contextual spectral projection | Real graph errors measured; certified fallback compared |
| [Wu and Amini, ICLR 2026](https://arxiv.org/abs/2601.00461) | Graphs over users fused with arm kernels | Graphs over arms, the case web catalogues expose |
| [Saito et al. 2021](https://arxiv.org/abs/2008.07146) | Off-policy evaluation benchmark | Graph structure across arms as the object of study |

## Risks and plan

The largest risk is a null result: real graphs may be too weakly aligned for any graph-aware method to help. That outcome is still publishable as a benchmark finding, provided certified methods are shown not to lose.

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Real graphs are weakly aligned everywhere | No regret gain to report | Frame as a measurement result; certified methods' small loss becomes the headline |
| Upworthy tests have few arms (about 4.6 on average) | Little room for graph pooling | Use it for RQ2 only; KuaiRec carries the many-arm results |
| Semi-synthetic tiers depend on fitted models | Reviewers discount those results | Keep them as secondary; report fit diagnostics |
| Replay discards most logged rounds | Short effective horizons on Open Bandit Dataset and Yahoo! R6 | Use the full random-policy logs; report effective sample sizes |
| Reward thresholds such as KuaiRec's watch ratio are arbitrary | Alignment depends on the reward definition | Report two thresholds as a sensitivity check |

**Eight-week plan.** The target deadline is still open.

1. Weeks 1 to 2: loaders for KuaiRec, Upworthy and Open Bandit Dataset; graph builders; alignment diagnostics.
2. Weeks 3 to 4: alignment measurements across all graphs (RQ1).
3. Weeks 5 to 6: regret runs for all algorithms; alignment-versus-gain analysis (RQ2, RQ3).
4. Week 7: semi-synthetic tiers (iPinYou, M5, MIND); graph-selection rule (RQ4).
5. Week 8: writing and the reproducibility package.

Open question: should KuaiRec and Upworthy lead, or the Open Bandit Dataset first for a stronger eCommerce story?

## Sources

- Valko, Munos, Kveton, Kocák. [Spectral Bandits for Smooth Graph Functions](https://proceedings.mlr.press/v32/valko14.html). ICML 2014.
- Kocák, Munos, Kveton, Agrawal, Valko. [Spectral Bandits](https://www.jmlr.org/papers/v21/16-529.html). JMLR 21, 2020.
- Mondal et al. [Graph Dimensionality Reduction for Contextual Bandits](https://arxiv.org/abs/2606.27917). Preprint, June 2026.
- Wu, Amini. [Laplacian Kernelized Bandit](https://arxiv.org/abs/2601.00461). ICLR 2026.
- Thaker et al. [Maximizing and Satisficing in Multi-armed Bandits with Graph Information](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html). NeurIPS 2022.
- Zhou, Fu, Ryzhov. [Sequential Learning with a Similarity Selection Index](https://pubsonline.informs.org/doi/abs/10.1287/opre.2023.2478). Operations Research 72(6), 2024.
- Gao et al. [KuaiRec: A Fully-observed Dataset and Insights for Evaluating Recommender Systems](https://arxiv.org/abs/2202.10842). CIKM 2022.
- Matias et al. [The Upworthy Research Archive](https://upworthy.natematias.com/about-the-archive). Scientific Data, 2021; data on [OSF](https://osf.io/jd64p/).
- Saito et al. [Open Bandit Dataset and Pipeline](https://arxiv.org/abs/2008.07146). NeurIPS Datasets and Benchmarks 2021.
- Li, Chu, Langford, Wang. [Unbiased Offline Evaluation of Contextual-bandit-based News Article Recommendation Algorithms](https://arxiv.org/abs/1003.5956). WSDM 2011 (Yahoo! R6).
- Zhang et al. [Real-Time Bidding Benchmarking with iPinYou Dataset](https://arxiv.org/abs/1407.7073). 2014.
- Wu et al. [MIND: Microsoft News Dataset](https://learn.microsoft.com/en-us/azure/open-datasets/dataset-microsoft-news). ACL 2020.
- Hou et al. [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/). McAuley Lab, 2023.
- Li, Chu, Langford, Schapire. [A Contextual-Bandit Approach to Personalized News Article Recommendation](https://arxiv.org/abs/1003.0146). WWW 2010 (LinUCB).
- Agrawal, Goyal. [Thompson Sampling for Contextual Bandits with Linear Payoffs](https://arxiv.org/abs/1209.3352). ICML 2013.
- Filippi, Cappé, Garivier, Szepesvári. Parametric Bandits: The Generalized Linear Case. NeurIPS 2010.
- Li, Lu, Zhou. [Provably Optimal Algorithms for Generalized Linear Contextual Bandits](https://arxiv.org/abs/1703.00048). ICML 2017.
- Jun, Willett, Wright, Nowak. [Bilinear Bandits with Low-rank Structure](https://arxiv.org/abs/1901.02470). ICML 2019.
- Srinivas, Krause, Kakade, Seeger. [Gaussian Process Optimization in the Bandit Setting](https://arxiv.org/abs/0912.3995). ICML 2010.
- Valko, Korda, Munos, Flaounas, Cristianini. [Finite-Time Analysis of Kernelised Contextual Bandits](https://arxiv.org/abs/1309.6869). UAI 2013.
- Zhou, Li, Gu. [Neural Contextual Bandits with UCB-based Exploration](https://arxiv.org/abs/1911.04462). ICML 2020.
- Zhang, Zhou, Li, Gu. [Neural Thompson Sampling](https://arxiv.org/abs/2010.00827). ICLR 2021.
- Kleinberg, Slivkins, Upfal. [Bandits and Experts in Metric Spaces](https://arxiv.org/abs/1312.1277). JACM 2019 (Zooming).
- Combes, Proutiere. [Unimodal Bandits: Regret Lower Bounds and Optimal Algorithms](https://proceedings.mlr.press/v32/combes14.html). ICML 2014.
- Pandey, Chakrabarti, Agarwal. [Multi-armed Bandit Problems with Dependent Arms](https://icml.cc/imls/conferences/2007/proceedings/abstracts/388.htm). ICML 2007.
- Hong, Kveton, Zaheer, Ghavamzadeh et al. [Deep Hierarchy in Bandits](https://proceedings.mlr.press/v162/hong22a.html). ICML 2022 (HierTS).
- Gupta, Chaudhari, Joshi, Yağan. [Multi-Armed Bandits with Correlated Arms](https://arxiv.org/abs/1911.03959). IEEE Trans. Inf. Theory 2021 (C-UCB, C-TS).
- Combes, Magureanu, Proutiere. [Minimal Exploration in Structured Stochastic Bandits](https://proceedings.neurips.cc/paper/2017/hash/e19347e1c3ca0c0b97de5fb3b690855a-Abstract.html). NeurIPS 2017 (OSSB).
- Zong et al. [Cascading Bandits for Large-Scale Recommendation Problems](https://arxiv.org/abs/1603.05359). UAI 2016.
- Cesa-Bianchi, Gentile, Zappella. [A Gang of Bandits](https://arxiv.org/abs/1306.0811). NeurIPS 2013 (GOB.Lin).
- Gentile, Li, Zappella. [Online Clustering of Bandits](https://proceedings.mlr.press/v32/gentile14.html). ICML 2014 (CLUB).
- Qi, Ban, He. [Graph Neural Bandits](https://arxiv.org/abs/2308.10808). KDD 2023.
- Internal: [graph alignment manuscript](../research/alignment_paper/manuscript.pdf) and [graph spectral note](../research/graph_spectral_bandits.md).
