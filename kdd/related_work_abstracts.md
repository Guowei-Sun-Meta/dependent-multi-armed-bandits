# Related Work: Indexed Abstracts from ICLR, ICML, NeurIPS, COLT, AISTATS and KDD, 2024–2026

18 October 2026. Compiled for the KDD 2027 paper on correlated arms ([kdd/README.md](README.md)). The scan covers the six venues over the last three years (NeurIPS 2023 to the NeurIPS 2026 accepted list) and keeps the papers that bear on the paper's three questions: structure between arms, dependence over time, and confidence under adaptive sampling.

## How the scan was done

- **Harvest.** Every accepted paper of NeurIPS 2023–2025, ICLR 2024–2026, ICML 2024–2026 and AISTATS 2025–2026 matching 13 search terms (bandit, confidence sequence, anytime-valid, restless, autoregressive, non-stationary, correlated arms, graph-structured, spectral bandit, time-uniform, sequential testing, Markov reward) was pulled from the OpenReview API; AISTATS 2024, COLT 2024–2026 and ICML 2024–2026 from the PMLR proceedings pages (titles matched against a broader keyword list, abstracts fetched); KDD 2024–2026 from OpenAlex, with arXiv comment fields as a cross-check; NeurIPS 2026 accepted papers from arXiv. 13,039 records, 11,597 unique titles.
- **Screening.** Titles and abstracts were scored by topic buckets (structure, temporal, inference, exposure, spatiotemporal) and screened by hand to 99 candidates.
- **Reading.** For each candidate the PDF was downloaded (arXiv or PMLR; OpenReview and the ACM Digital Library block automated downloads) and the abstract and introduction were read. 77 papers were kept. For 4 of them the PDF was not reachable from this machine, so only the abstract was read; they are marked.
- **Abstracts are verbatim** from OpenReview, PMLR, arXiv or OpenAlex. **Relevance notes are ours**, keyed to the theory labels in [research/correlated_arms](../research/correlated_arms/README.md) (A1–A4, N1, B1–B3, S5, S6) and the verdicts in [experiments/report](../experiments/report/README.md). Papers marked **core** should be cited in the KDD draft; the others are adjacent.
- Scripts to repeat the scan are in [related_work_scan/](related_work_scan/README.md).

## What the scan shows

1. **Nobody certifies pooling under temporal dependence.** The structured-arm papers (theme A) pool along graphs, clusters or hierarchies and either assume the structure is exact (P15, P14, P05) or tolerate a deviation that enters regret linearly (P17); none checks validity from data, and none combines pooling with autocorrelated rewards. The closest theory, P01 (COLT 2026), uses known within-group ranges, which are our ε_c without the certificate; P02 (ICLR 2026) is the kernelized Gang-of-Bandits and the natural uncertified baseline to add to Setting B.
2. **Temporal dependence is modelled as drift, change points or action-induced memory, not as exogenous persistence with a confidence guarantee for fixed means.** The AR papers (Autoregressive Bandits, AR temporal dependency) and the latent-dynamics papers (explore-then-commit, block optimism, latent-state bandits at KDD 2026) bound regret against dynamic benchmarks; the only confidence sequences for fixed means under dependence are the state-space A/B paper (AISTATS 2026, one two-arm test, known AR(1)) and the Markovian sequential test (ICML 2026, finite-state chains).
3. **The anytime-valid literature has moved to tighter multivariate and likelihood-ratio sequences.** Martingale-mixture, dual-program, likelihood-ratio and condition-number bounds (NeurIPS 2023 oral, AISTATS 2025, NeurIPS 2024, COLT 2025) are the tools for shrinking B1's √(N log T) width, which is the paper's top open problem.
4. **The A/B-testing papers assume independent daily data.** YEAST, counting-process e-processes, horizon-aware betting and design-based delayed-outcome sequences all take iid or exchangeable increments; the carryover and non-stationarity papers (robust sequential design, state-space A/B, Experimenting Fast and Slow, False Positives at KDD 2024) establish that the assumption fails in practice without measuring the inflation. That is the opening for experiment proposal 1 and for B2.
5. **Network interference is the other 'spatial' dependence.** Five papers in 2024–2026 put a graph between units whose treatments interfere; one (NeurIPS 2025) adds an anytime-valid sequence. They are a distinct channel from ours (dependence through treatments, not through reward shocks) and should be cited to delimit the claim.

## Index

| ID | Year | Venue | Title | Theme | Core |
| --- | ---: | --- | --- | --- | :---: |
| [P01](#p01) | 2026 | COLT 2026 | Leveraging Similarities in Multi-Armed Bandits | A | yes |
| [P02](#p02) | 2026 | ICLR 2026 | Laplacian Kernelized Bandit | A | yes |
| [P03](#p03) | 2026 | KDD 2026 | Hierarchical Adversarial Bandits for Online Configuration Optimization | A |  |
| [P04](#p04) | 2025 | ICLR 2025 | Demystifying Online Clustering of Bandits: Enhanced Exploration Under Stochastic and Smoothed Adversarial Contexts | A | yes |
| [P05](#p05) | 2025 | ICML 2025 | Near Optimal Best Arm Identification for Clustered Bandits | A |  |
| [P06](#p06) | 2025 | KDD 2025 | Multi-Task Combinatorial Bandits for Budget Allocation | A |  |
| [P07](#p07) | 2025 | KDD 2025 | Revisiting Clustering of Neural Bandits: Selective Reinitialization for Mitigating Loss of Plasticity | A | yes |
| [P08](#p08) | 2024 | ICML 2024 | Graph-Triggered Rising Bandits | A | yes |
| [P09](#p09) | 2024 | KDD 2024 | Meta Clustering of Neural Bandits | A | yes |
| [P10](#p10) | 2024 | KDD 2024 | Multi-Task Neural Linear Bandit for Exploration in Recommender Systems | A |  |
| [P11](#p11) | 2024 | NeurIPS 2024 | Improved Bayes Regret Bounds for Multi-Task Hierarchical Bayesian Bandit Algorithms | A |  |
| [P12](#p12) | 2024 | NeurIPS 2024 | PageRank Bandits for Link Prediction | A |  |
| [P13](#p13) | 2024 | NeurIPS 2024 | RoME: A Robust Mixed-Effects Bandit Algorithm for Optimizing Mobile Health Interventions | A | yes |
| [P14](#p14) | 2023 | NeurIPS 2023 | Blocked Collaborative Bandits: Online Collaborative Filtering with Per-Item Budget Constraints | A |  |
| [P15](#p15) | 2023 | NeurIPS 2023 | Context-lumpable stochastic bandits | A |  |
| [P16](#p16) | 2023 | NeurIPS 2023 | Exploiting Correlated Auxiliary Feedback in Parameterized Bandits | A |  |
| [P17](#p17) | 2023 | NeurIPS 2023 | Online Clustering of Bandits with Misspecified User Models | A | yes |
| [P18](#p18) | 2026 | AISTATS 2026 | A Modularized Framework for Piecewise-Stationary Restless Bandits | B |  |
| [P19](#p19) | 2026 | AISTATS 2026 | Explore-then-Commit for Nonstationary Linear Bandits with Latent Dynamics | B | yes |
| [P20](#p20) | 2026 | COLT 2026 | On the Complexity of Best-Arm Identification in Non-Stationary Linear Bandits | B |  |
| [P21](#p21) | 2026 | ICML 2026 | A Direct Approach for Handling Contextual Bandits with Latent State Dynamics | B |  |
| [P22](#p22) | 2026 | ICML 2026 | DAL: A Practical Prior-Free Black-Box Framework for Piecewise Stationary Bandits | B |  |
| [P23](#p23) | 2026 | ICML 2026 | Generalized Linear Bandits with Memory | B |  |
| [P24](#p24) | 2026 | KDD 2026 | Adaptive Exploration for Latent-State Bandits | B | yes |
| [P25](#p25) | 2026 | NeurIPS 2026 (accepted; arXiv version) | Best Arm Identification for Bandits with Shifting Means | B | yes |
| [P26](#p26) | 2026 | NeurIPS 2026 (accepted; arXiv version) | Block Optimism for Nonstationary Bandits with Latent Linear Dynamics | B | yes |
| [P27](#p27) | 2025 | AISTATS 2025 | Lower Bounds for Time-Varying Kernelized Bandits | B |  |
| [P28](#p28) | 2025 | AISTATS 2025 | Near-Optimal Algorithm for Non-Stationary Kernelized Bandits | B |  |
| [P29](#p29) | 2025 | AISTATS 2025 | Time-varying Gaussian Process Bandits with Unknown Prior | B |  |
| [P30](#p30) | 2025 | AISTATS 2025 | Variance-Dependent Regret Bounds for Nonstationary Linear Bandits | B |  |
| [P31](#p31) | 2025 | KDD 2025 | Experimenting, Fast and Slow: Bayesian Optimization of Long-term Outcomes with Online Experiments | B |  |
| [P32](#p32) | 2025 | KDD 2025 | Off-Policy Evaluation and Learning for the Future under Non-Stationarity | B | yes |
| [P33](#p33) | 2025 | KDD 2025 | Quick Draw Bandits: Quickly Optimizing in Nonstationary Environments with Extremely Many Arms | B | yes |
| [P34](#p34) | 2024 | AISTATS 2024 | A/B Testing and Best-arm Identification for Linear Bandits with Robustness to Non-stationarity | B | yes |
| [P35](#p35) | 2024 | AISTATS 2024 | Autoregressive Bandits | B | yes |
| [P36](#p36) | 2024 | NeurIPS 2024 | Almost Minimax Optimal Best Arm Identification in Piecewise Stationary Linear Bandits | B |  |
| [P37](#p37) | 2023 | NeurIPS 2023 | Non-Stationary Bandits with Auto-Regressive Temporal Dependency | B | yes |
| [P38](#p38) | 2023 | NeurIPS 2023 | Tracking Most Significant Shifts in Nonparametric Contextual Bandits | B |  |
| [P39](#p39) | 2026 | AISTATS 2026 | Kernel Treatment Effects with Adaptively Collected Data | C |  |
| [P40](#p40) | 2026 | COLT 2026 | Self-Normalized Martingales and Uniform Regret Bounds for Linear Regression | C |  |
| [P41](#p41) | 2026 | ICML 2026 | Asymptotically Optimal Sequential Testing with Markovian Data | C | yes |
| [P42](#p42) | 2026 | ICML 2026 | Beyond First-order Asymptotics in Sequential Mean Testing | C |  |
| [P43](#p43) | 2026 | ICML 2026 | Learning to Bet for Horizon-Aware Anytime-Valid Testing | C |  |
| [P44](#p44) | 2026 | ICML 2026 | Prediction-Powered Adaptive Inference with Pretrained AI Models for Contextual Bandits | C |  |
| [P45](#p45) | 2026 | NeurIPS 2026 (accepted; arXiv version) | On the Tightness and Computational Tractability of Higher-Dimensional Confidence Sequences | C | yes |
| [P46](#p46) | 2025 | AISTATS 2025 | Tighter Confidence Bounds for Sequential Kernel Regression | C | yes |
| [P47](#p47) | 2025 | COLT 2025 | Time-Uniform Self-Normalized Concentration for Vector-Valued Processes (Extended Abstract) | C | yes |
| [P48](#p48) | 2025 | ICML 2025 | Optimistic Algorithms for Adaptive Estimation of the Average Treatment Effect | C |  |
| [P49](#p49) | 2025 | NeurIPS 2025 | Bernstein–von Mises for Adaptively Collected Data | C | yes |
| [P50](#p50) | 2025 | NeurIPS 2025 | STAR-Bets: Sequential TArget-Recalculating Bets for Tighter Confidence Intervals | C |  |
| [P51](#p51) | 2025 | NeurIPS 2025 | Simulation-Based Inference for Adaptive Experiments | C |  |
| [P52](#p52) | 2024 | COLT 2024 | An information-theoretic lower bound in time-uniform estimation | C |  |
| [P53](#p53) | 2024 | ICML 2024 | Gambling-Based Confidence Sequences for Bounded Random Vectors | C |  |
| [P54](#p54) | 2024 | ICML 2024 | Peeking with PEAK: Sequential, Nonparametric Composite Hypothesis Tests for Means of Multiple Data Streams | C | yes |
| [P55](#p55) | 2024 | NeurIPS 2024 | A Unified Confidence Sequence for Generalized Linear Models, with Applications to Bandits | C | yes |
| [P56](#p56) | 2024 | NeurIPS 2024 | Off-policy estimation with adaptively collected data: the power of online learning | C |  |
| [P57](#p57) | 2023 | NeurIPS 2023 | Improved Algorithms for Stochastic Linear Bandits Using Tail Bounds for Martingale Mixtures | C | yes |
| [P58](#p58) | 2023 | NeurIPS 2023 | Likelihood Ratio Confidence Sets for Sequential Decision Making | C | yes |
| [P59](#p59) | 2023 | NeurIPS 2023 | Time-uniform confidence bands for the CDF under nonstationarity | C |  |
| [P60](#p60) | 2026 | AISTATS 2026 | Adaptive A/B Testing under Nonstationary Dynamics using State-Space Models | D | yes |
| [P61](#p61) | 2026 | AISTATS 2026 | Adaptive Combinatorial Experimental Design: Pareto Optimality for Decision-Making and Inference | D |  |
| [P62](#p62) | 2026 | ICML 2026 | Contextual Slate GLM Bandits with Limited Adaptivity | D |  |
| [P63](#p63) | 2026 | ICML 2026 | Design-Based Anytime-Valid Inference for Randomized Experiments with Delayed Outcomes and Staggered Entry | D | yes |
| [P64](#p64) | 2026 | ICML 2026 | Robust Sequential Experimental Design for A/B Testing | D | yes |
| [P65](#p65) | 2025 | AISTATS 2025 | Anytime-Valid A/B Testing of Counting Processes | D |  |
| [P66](#p66) | 2025 | ICLR 2025 | Almost Optimal Batch-Regret Tradeoff for Batch Linear Contextual Bandits | D |  |
| [P67](#p67) | 2025 | ICLR 2025 | Breaking the $\log(1/\Delta_2)$ Barrier: Better Batched Best Arm Identification with Adaptive Grids | D |  |
| [P68](#p68) | 2025 | KDD 2025 | A/B Test and Online Experiment Under Diminishing Marginal Effects: Regret Minimization and Statistical Inference | D |  |
| [P69](#p69) | 2025 | NeurIPS 2025 | YEAST: Yet Another Sequential Test | D | yes |
| [P70](#p70) | 2024 | ICML 2024 | On Universally Optimal Algorithms for A/B Testing | D |  |
| [P71](#p71) | 2024 | KDD 2024 | False Positives in A/B Tests | D | yes |
| [P72](#p72) | 2026 | AISTATS 2026 | Scalable Policy Maximization Under Network Interference | E |  |
| [P73](#p73) | 2026 | KDD 2026 | Learning Peer Influence Probabilities with Linear Contextual Bandits | E |  |
| [P74](#p74) | 2025 | ICML 2025 | Linear Contextual Bandits With Interference | E |  |
| [P75](#p75) | 2025 | ICML 2025 | Multi-Armed Bandits with Interference: Bridging Causal Inference and Adversarial Bandits | E | yes |
| [P76](#p76) | 2025 | NeurIPS 2025 | Design-Based Bandits Under Network Interference: Trade-Off Between Regret and Statistical Inference | E | yes |
| [P77](#p77) | 2024 | NeurIPS 2024 | Mutli-Armed Bandits with Network Interference | E | yes |

**Themes.**

- **A.** Structured and correlated arms: graphs, clusters, similarity (mean channel; A1, A4, N1)
- **B.** Temporally dependent and non-stationary rewards (fluctuation channel; S5, P1, B3)
- **C.** Confidence sequences, anytime-valid inference, and inference after adaptive sampling (bridge; B1, B2)
- **D.** Online experiments, A/B testing, and limited adaptivity (bursty exposure; B2, B3)
- **E.** Dependence across units: network interference (spatial correlation of rewards)

**By venue.** AISTATS: 14, COLT: 5, ICLR: 4, ICML: 18, KDD: 12, NeurIPS: 24.

**Where each theme enters the draft.**

| Draft section | Themes | Core papers |
| --- | --- | --- |
| Spatial dependence (related work) | A, E | P01, P02, P04, P07, P08, P09, P13, P17, P75, P76, P77 |
| Temporal dependence (related work) | B | P19, P24, P25, P26, P32, P33, P34, P35, P37 |
| Confidence and evaluation on logged data (related work) | C, D | P41, P45, P46, P47, P49, P54, P55, P57, P58, P60, P63, P64, P69, P71 |
| Experiment proposal 1: sequential stopping in online experiments | C, D | P41, P45, P46, P47, P49, P54, P55, P57, P58, P60, P63, P64, P69, P71 |
| Open problem: tighter certificate | C | P41, P45, P46, P47, P49, P54, P55, P57, P58 |


## Theme A. Structured and correlated arms: graphs, clusters, similarity (mean channel; A1, A4, N1)

### P01

**Leveraging Similarities in Multi-Armed Bandits**  
Khaled Eldowa, Thibaud Rahier, Augustin Cablant, Panayotis Mertikopoulos, Pierre Gaillard. *COLT 2026.* [Page](https://proceedings.mlr.press/v336/eldowa26a.html) · [PDF](http://arxiv.org/pdf/2606.23414v1)

> In many online learning and bandit problems, the actions we consider possess inherent similarities–for instance because they share latent traits, tags, or hierarchical structure. We study online learning with a similarity-structured action set, encoded by a rooted tree whose leaves are the actions and whose levels quantify how closely two actions are related. The loss sequence is assumed tree-compatible: losses of similar actions are constrained to be close. We establish an impossibility result showing that usual one-point bandit feedback cannot, in general, leverage range or tree-induced similarity, even under very strong similarity constraints. We then provide a unified set of algorithms which adapt to a wide range of richer feedback models, from semi-bandit feedback down to multi-point bandit protocols, including the minimal two-point feedback setting. We show these algorithms exhibit best-of-both-worlds guarantees and provably exploit action similarities by replacing the number of actions $K$ by a similarity-aware effective number of actions $K_{\mathrm{eff}}$ in the regret bounds. As an application, we show that under two-point feedback, it is possible to achieve $\sqrt{T}$ regret in Lipschitz bandits when $d \leq 2$.

**Relevance (core).** Hierarchical similarity over arms (nested partitions by traits) constrains within-group reward ranges and yields regret that improves with the hierarchy. The closest recent theory to our certified diameters: their partition-level range bounds are our ε_c, but assumed known and valid rather than certified from data.

### P02

**Laplacian Kernelized Bandit**  
Shuang Wu, Arash A. Amini. *ICLR 2026.* [Page](https://openreview.net/forum?id=5majEbTAZa) · [PDF](http://arxiv.org/pdf/2601.00461v1)

> We study multi-user contextual bandits where users are related by a graph and their reward functions exhibit both non-linear behavior and graph homophily. We introduce a principled joint penalty for the collection of user reward functions $\\{f_u\\}$, combining a graph smoothness term based on RKHS distances with an individual roughness penalty. Our central contribution is proving that this penalty is equivalent to the squared norm within a single, unified _multi-user RKHS_. We explicitly derive its reproducing kernel, which elegantly fuses the graph Laplacian with the base arm kernel. This unification allows us to reframe the problem as learning a single "lifted" function, enabling the design of principled algorithms, LK-GP-UCB and LK-GP-TS, that leverage Gaussian Process posteriors over this new kernel for exploration. We provide high-probability regret bounds that scale with an _effective dimension_ of the multi-user kernel, replacing dependencies on user count or ambient dimension. Empirically, our methods outperform strong linear and non-graph-aware baselines in non-linear settings and remain competitive even when the true rewards are linear. Our work delivers a unified, theoretically grounded, and practical framework that bridges Laplacian regularization with kernelized bandits for structured exploration.

**Relevance (core).** Multi-user contextual bandits with a user graph: a joint penalty (graph smoothness in RKHS distance plus ridge) is shown to be a single multi-user RKHS whose kernel fuses the Laplacian with the arm kernel; regret scales with an effective dimension. The kernelized form of Gang-of-Bandits/spectral smoothing, with no validity check of the graph; our rewired-null and certificate tests apply directly.

### P03

**Hierarchical Adversarial Bandits for Online Configuration Optimization**  
Gil Shabat, Chen Avin, Shie Mannor, Hanan Shteingart, Zvi Lotker, Roey Yadgar. *KDD 2026.* [Page](https://doi.org/10.1145/3770855.3818431) · [PDF](http://arxiv.org/pdf/2505.19061v2)

> Motivated by Online Configuration Optimization in large, dynamic parameter spaces, this work studies the nonstochastic multi-armed bandit (MAB) problem in metric action spaces with oblivious Lipschitz adversaries. We propose ABoB (Adversarial Bandit over Bandits), a hierarchical framework that decomposes the configuration space into clusters to accelerate learning and adapt to changing environments. We evaluate ABoB using standard algorithms such as EXP3 and Tsallis-INF on a real-world production storage system, demonstrating significant performance gains of up to $50\%$ compared to state-of-the-art "flat" bandit algorithms. Extensive simulations further confirm that ABoB effectively exploits metric structures, achieving up to $91\%$ improvement in adversarial metric scenarios while significantly reducing computational running time. Theoretical analysis grounds this empirical success: we prove that ABoB maintains a worst-case "safety net" bound of $O(\sqrt{kT})$, matching traditional methods, where $T$ is the number of rounds and $k$ is the number of arms, while capable of accelerating learning to $O(k^{1/4}\sqrt{T})$ under favorable Lipschitz conditions. This combination of operational efficiency and theoretical soundness makes ABoB a practical solution for automated system tuning.

**Relevance.** KDD 2026: adversarial bandits over a metric configuration space partitioned into clusters with Lipschitz rewards within clusters; a bandit over bandits with an O(√(kT)) safety net and faster learning under Lipschitz structure. Cluster-level pooling with a worst-case fallback, the adversarial counterpart of certified pooling's 'never worse than per-arm' structure.

### P04

**Demystifying Online Clustering of Bandits: Enhanced Exploration Under Stochastic and Smoothed Adversarial Contexts**  
Zhuohua Li, Maoli Liu, Xiangxiang Dai, John C.S. Lui. *ICLR 2025.* [Page](https://openreview.net/forum?id=421D67DY3i) · [PDF](http://arxiv.org/pdf/2501.00891v1)

> The contextual multi-armed bandit (MAB) problem is crucial in sequential decision-making. A line of research, known as online clustering of bandits, extends contextual MAB by grouping similar users into clusters, utilizing shared features to improve learning efficiency. However, existing algorithms, which rely on the upper confidence bound (UCB) strategy, struggle to gather adequate statistical information to accurately identify unknown user clusters. As a result, their theoretical analyses require several strong assumptions about the "diversity" of contexts generated by the environment, leading to impractical settings, complicated analyses, and poor practical performance. Removing these assumptions has been a long-standing open problem in the clustering of bandits literature. In this work, we provide two partial solutions. First, we introduce an additional exploration phase to accelerate the identification of clusters. We integrate this general strategy into both graph-based and set-based algorithms and propose two new algorithms, UniCLUB and UniSCLUB. Remarkably, our algorithms require substantially weaker assumptions and simpler theoretical analyses while achieving superior cumulative regret compared to previous studies. Second, inspired by the smoothed analysis framework, we propose a more practical setting that eliminates the requirement for i.i.d. context generation used in previous studies, thus enhancing the performance of existing algorithms for online clustering of bandits. Extensive evaluations on both synthetic and real-world datasets demonstrate that our proposed algorithms outperform existing approaches.

**Relevance (core).** Shows that UCB-based online clustering of bandits lacks the exploration needed to identify clusters and needs strong context-diversity assumptions; adds an exploration phase (UniCLUB, UniSCLUB). Relevant to our CLUB-style control: the clustering baseline's weakness is in cluster identification, which certified pooling sidesteps by taking the partition from a mined graph and certifying it.

### P05

**Near Optimal Best Arm Identification for Clustered Bandits**  
Yash, Avishek Ghosh, Nikhil Karamchandani. *ICML 2025.* [Page](https://openreview.net/forum?id=3Jr5Al16MS) · [PDF](http://arxiv.org/pdf/2505.10147v1)

> This work investigates the problem of best arm identification for multi-agent multi-armed bandits. We consider $N$ agents grouped into $M$ clusters, where each cluster solves a stochastic bandit problem. The mapping between agents and bandits is \textit{a priori} unknown. Each bandit is associated with $K$ arms, and the goal is to identify the best arm for each agent under a $\delta$-probably correct ($\delta$-PC) framework, while minimizing sample complexity and communication overhead. We propose two novel algorithms: \emph{Clustering then Best Arm Identification} (\texttt{Cl-BAI}) and \emph{Best Arm Identification then Clustering} (\texttt{BAI-Cl}). \texttt{Cl-BAI} employs a two-phase approach that first clusters agents based on the bandit problems they are learning, followed by identifying the best arm for each cluster. \texttt{BAI-Cl} reverses the sequence by identifying the best arms first and then clustering agents accordingly. Both algorithms exploit the successive elimination framework to ensure computational efficiency and high accuracy. Theoretical analysis establishes $\delta$-PC guarantees for both methods, derives bounds on their sample complexity, and provides a lower bound for the problem class. Moreover, when $M$ is small (a constant), we show that the sample complexity of (a variant of) \texttt{BAI-Cl} is (order-wise) minimax optimal. Experiments on synthetic and real-world (Movie Lens, Yelp) data demonstrates the superior performance of the proposed algorithms in terms of sample and communication efficiency, particularly in settings where $M \ll N$.

**Relevance.** Best-arm identification for N agents in M unknown clusters sharing bandit instances; cluster-then-identify and identify-then-cluster with minimax sample complexity for constant M. Pure-exploration analogue of Setting B's user-side pooling, without a diameter slack.

### P06

**Multi-Task Combinatorial Bandits for Budget Allocation**  
Lin Ge, Yang Xu, Jianing Chu, David Cramer, Fuhong Li, Kelly Paulson, Rui Song. *KDD 2025.* [Page](https://doi.org/10.1145/3690624.3709434) · [PDF](http://arxiv.org/pdf/2409.00561v1)

> Today's top advertisers typically manage hundreds of campaigns simultaneously and consistently launch new ones throughout the year. A crucial challenge for marketing managers is determining the optimal allocation of limited budgets across various ad lines in each campaign to maximize cumulative returns, especially given the huge uncertainty in return outcomes. In this paper, we propose to formulate budget allocation as a multi-task combinatorial bandit problem and introduce a novel online budget allocation system. The proposed system: i) integrates a Bayesian hierarchical model to intelligently utilize the metadata of campaigns and ad lines and budget size, ensuring efficient information sharing; ii) provides the flexibility to incorporate diverse modeling techniques such as Linear Regression, Gaussian Processes, and Neural Networks, catering to diverse environmental complexities; and iii) employs the Thompson sampling technique to strike a balance between exploration and exploitation. Through extensive empirical evaluations with both synthetic data and real-world data from Amazon campaigns, our system demonstrates robustness and adaptability, effectively maximizing the overall cumulative returns. A Python implementation of the proposed procedure is available at https://anonymous.4open.science/r/MCMAB.

**Relevance.** KDD 2025: budget allocation across ad lines as a multi-task combinatorial bandit with a Bayesian hierarchical model that shares information through campaign metadata; Thompson sampling; Amazon campaign data. Hierarchical shrinkage is the graph-free pooling that our experiments found to carry most of the gain.

### P07

**Revisiting Clustering of Neural Bandits: Selective Reinitialization for Mitigating Loss of Plasticity**  
Zhiyuan Su, Sunhao Dai, Xiao Zhang. *KDD 2025.* [Page](https://doi.org/10.1145/3711896.3737105) · [PDF](http://arxiv.org/pdf/2506.12389v3)

> Clustering of Bandits (CB) methods enhance sequential decision-making by grouping bandits into clusters based on similarity and incorporating cluster-level contextual information, demonstrating effectiveness and adaptability in applications like personalized streaming recommendations. However, when extending CB algorithms to their neural version (commonly referred to as Clustering of Neural Bandits, or CNB), they suffer from loss of plasticity, where neural network parameters become rigid and less adaptable over time, limiting their ability to adapt to non-stationary environments (e.g., dynamic user preferences in recommendation). To address this challenge, we propose Selective Reinitialization (SeRe), a novel bandit learning framework that dynamically preserves the adaptability of CNB algorithms in evolving environments. SeRe leverages a contribution utility metric to identify and selectively reset underutilized units, mitigating loss of plasticity while maintaining stable knowledge retention. Furthermore, when combining SeRe with CNB algorithms, the adaptive change detection mechanism adjusts the reinitialization frequency according to the degree of non-stationarity, ensuring effective adaptation without unnecessary resets. Theoretically, we prove that SeRe enables sublinear cumulative regret in piecewise-stationary environments, outperforming traditional CNB approaches in long-term performances. Extensive experiments on six real-world recommendation datasets demonstrate that SeRe-enhanced CNB algorithms can effectively mitigate the loss of plasticity with lower regrets, improving adaptability and robustness in dynamic settings.

**Relevance (core).** KDD 2025 follow-up: clustering of neural bandits loses plasticity in non-stationary environments; selective reinitialization with change detection restores sublinear regret in piecewise-stationary settings, tested on six recommendation datasets. The KDD precedent that combines pooling across users with non-stationarity, treated as abrupt change rather than persistence.

### P08

**Graph-Triggered Rising Bandits**  
Gianmarco Genalti, Marco Mussi, Nicola Gatti, Marcello Restelli, Matteo Castiglioni, Alberto Maria Metelli. *ICML 2024.* [Page](https://openreview.net/forum?id=bPsohGR6gD) · [PDF](https://raw.githubusercontent.com/mlresearch/v235/main/assets/genalti24a/genalti24a.pdf)

> In this paper, we propose a novel generalization of rested and restless bandits where the evolution of the arms' expected rewards is governed by a graph defined over the arms. An edge connecting a pair of arms $(i,j)$ represents the fact that a pull of arm $i$ *triggers* the evolution of arm $j$, and vice versa. Interestingly, rested and restless bandits are both special cases of our model for some suitable (degenerate) graphs. Still, the model can represent way more general and interesting scenarios. We first tackle the problem of computing the optimal policy when no specific structure is assumed on the graph, showing that it is NP-hard. Then, we focus on a specific structure forcing the graph to be composed of a set of fully connected subgraphs (i.e., cliques), and we prove that the optimal policy can be easily computed in closed form. Then, we move to the learning problem presenting regret minimization algorithms for deterministic and stochastic cases. Our regret bounds highlight the complexity of the learning problem by incorporating instance-dependent terms that encode specific properties of the underlying graph structure. Moreover, we illustrate how the knowledge of the underlying graph is not necessary for achieving the no-regret property.

**Relevance (core).** Graph-triggered rising bandits: a graph over arms says which arms' reward evolution a pull triggers; restless and rested are the two extreme graphs; optimal policy NP-hard in general, closed form for cliques. A graph that shapes dynamics rather than means, which is our second graph role, under rested (action-driven) rather than exogenous evolution.

### P09

**Meta Clustering of Neural Bandits**  
Yikun Ban, Yunzhe Qi, Tianxin Wei, Lihui Liu, Jingrui He. *KDD 2024.* [Page](https://doi.org/10.1145/3637528.3671691) · [PDF](http://arxiv.org/pdf/2408.05586v2)

> The contextual bandit has been identified as a powerful framework to formulate the recommendation process as a sequential decision-making process, where each item is regarded as an arm and the objective is to minimize the regret of T rounds. In this paper, we study a new problem, Clustering of Neural Bandits, by extending previous work to the arbitrary reward function, to strike a balance between user heterogeneity and user correlations in the recommender system. To solve this problem, we propose a novel algorithm called M-CNB, which utilizes a meta-learner to represent and rapidly adapt to dynamic clusters, along with an informative Upper Confidence Bound (UCB)-based exploration strategy. We provide an instance-dependent performance guarantee for the proposed algorithm that withstands the adversarial context, and we further prove the guarantee is at least as good as state-of-the-art (SOTA) approaches under the same assumptions. In extensive experiments conducted in both recommendation and online classification scenarios, M-CNB outperforms SOTA baselines. This shows the effectiveness of the proposed approach in improving online recommendation and online classification performance.

**Relevance (core).** Clustering of neural bandits (M-CNB): a meta-learner represents dynamic user clusters with arbitrary reward functions, UCB exploration, instance-dependent guarantee. KDD 2024; the KDD-side state of the art for pooling across users. It pools whatever the clustering finds and has no validity guarantee for the pooled estimate.

### P10

**Multi-Task Neural Linear Bandit for Exploration in Recommender Systems**  
(authors on the linked page). *KDD 2024.* [Page](https://doi.org/10.1145/3637528.3671649) · [PDF](https://doi.org/10.1145/3637528.3671649)  
*Abstract only: the PDF was not reachable from this machine, so the introduction was not read.*

> Exposure bias and its induced feedback loop effect are well-known problems in recommender systems. Exploration is believed to be the key to break such feedback loops. While classical contextual bandit algorithms such as Upper-Confidence-Bound and Thompson Sampling have been successful in addressing the exploration-exploitation trade-off in the single-task settings with one clear reward signal, modern recommender systems often leverage multiple rich sources of feedback such as clicks, likes, dislikes, shares, satisfaction survey responses, and employ multi-task learning in practice. It is unclear how one can incorporate exploration in the multi-task setup with different objectives. In this paper, we study an efficient bandit algorithm tailored to multi-task recommender systems, named Multi-task Neural Linear Bandit (mtNLB). In particular, we investigate efficient feature embeddings in the multi-task setups that could be used as contextual features in the Neural Linear Bandit, a contextual bandit algorithm that nicely combines the representation power from DNN and simplicity in uncertainty calculation from linear models. We further study cost-effective approximations of the uncertainty estimate and principled ways to incorporate uncertainty into the multi-task scoring of items. To showcase the efficacy of our proposed method, we conduct live experiments on a large-scale commercial recommendation platform that serves billions of users. We evaluate the quality of the uncertainty estimate and demonstrate its ability to improve exploration across the different dimensions of the reward signals in comparison to baseline approaches.

**Relevance.** KDD 2024, deployed at scale: Neural Linear Bandit with multi-task embeddings and approximate uncertainty, live experiments on a commercial recommender. Evidence that KDD values uncertainty-driven exploration in production recommenders; no structure between arms beyond shared embeddings. (Abstract only.)

### P11

**Improved Bayes Regret Bounds for Multi-Task Hierarchical Bayesian Bandit Algorithms**  
Jiechao Guan, Hui Xiong. *NeurIPS 2024.* [Page](https://openreview.net/forum?id=joNPMCzVIi) · [PDF](https://openreview.net/pdf/35c624f4c1c81fe9bad7cac2cf5867fdf06ae4ad.pdf)  
*Abstract only: the PDF was not reachable from this machine, so the introduction was not read.*

> Hierarchical Bayesian bandit refers to the multi-task bandit problem in which bandit tasks are assumed to be drawn from the same distribution. In this work, we provide improved Bayes regret bounds for hierarchical Bayesian bandit algorithms in the multi-task linear bandit and semi-bandit settings. For the multi-task linear bandit, we first analyze the preexisting hierarchical Thompson sampling (HierTS) algorithm, and improve its gap-independent Bayes regret bound from $O(m\sqrt{n\log{n}\log{(mn)}})$ to $O(m\sqrt{n\log{n}})$ in the case of infinite action set, with $m$ being the number of tasks and $n$ the number of iterations per task. In the case of finite action set, we propose a novel hierarchical Bayesian bandit algorithm, named hierarchical BayesUCB (HierBayesUCB), that achieves the logarithmic but gap-dependent regret bound $O(m\log{(mn)}\log{n})$ under mild assumptions. All of the above regret bounds hold in many variants of hierarchical Bayesian linear bandit problem, including when the tasks are solved sequentially or concurrently. Furthermore, we extend the aforementioned HierTS and HierBayesUCB algorithms to the multi-task combinatorial semi-bandit setting. Concretely, our combinatorial HierTS algorithm attains comparable Bayes regret bound $O(m\sqrt{n}\log{n})$ with respect to the latest one. Moreover, our combinatorial HierBayesUCB yields a sharper Bayes regret bound $O(m\log{(mn)}\log{n})$. Experiments are conducted to validate the soundness of our theoretical results for multi-task bandit algorithms.

**Relevance.** Improved Bayes regret for hierarchical Thompson sampling and a hierarchical BayesUCB in multi-task linear and semi-bandits. Theory for the shrinkage baseline (tasks drawn from a shared prior). (Abstract only.)

### P12

**PageRank Bandits for Link Prediction**  
Yikun Ban, Jiaru Zou, Zihao Li, Yunzhe Qi, Dongqi Fu, Jian Kang, Hanghang Tong, Jingrui He. *NeurIPS 2024.* [Page](https://openreview.net/forum?id=VSz9na5Jtl) · [PDF](http://arxiv.org/pdf/2411.01410v1)

> Link prediction is a critical problem in graph learning with broad applications such as recommender systems and knowledge graph completion. Numerous research efforts have been directed at solving this problem, including approaches based on similarity metrics and Graph Neural Networks (GNN). However, most existing solutions are still rooted in conventional supervised learning, which makes it challenging to adapt over time to changing customer interests and to address the inherent dilemma of exploitation versus exploration in link prediction. To tackle these challenges, this paper reformulates link prediction as a sequential decision-making process, where each link prediction interaction occurs sequentially. We propose a novel fusion algorithm, PRB (PageRank Bandits), which is the first to combine contextual bandits with PageRank for collaborative exploitation and exploration. We also introduce a new reward formulation and provide a theoretical performance guarantee for PRB. Finally, we extensively evaluate PRB in both online and offline settings, comparing it with bandit-based and graph-based methods. The empirical success of PRB demonstrates the value of the proposed fusion approach. Our code is released at https://github.com/jiaruzouu/PRB.

**Relevance.** Link prediction as a contextual bandit fused with PageRank over the graph for exploitation and exploration. Uses graph connectivity as a prior for reward aggregation, uncertified; relevant as a KDD-audience precedent for graphs in bandits.

### P13

**RoME: A Robust Mixed-Effects Bandit Algorithm for Optimizing Mobile Health Interventions**  
Easton Knight Huch, Jieru Shi, Madeline R Abbott, Jessica R Golbus, Alexander Moreno, Walter H. Dempsey. *NeurIPS 2024.* [Page](https://openreview.net/forum?id=eKVugi5zr0) · [PDF](http://arxiv.org/pdf/2312.06403v4)

> Mobile health leverages personalized and contextually tailored interventions optimized through bandit and reinforcement learning algorithms. In practice, however, challenges such as participant heterogeneity, nonstationarity, and nonlinear relationships hinder algorithm performance. We propose RoME, a **Ro**bust **M**ixed-**E**ffects contextual bandit algorithm that simultaneously addresses these challenges via (1) modeling the differential reward with user- and time-specific random effects, (2) network cohesion penalties, and (3) debiased machine learning for flexible estimation of baseline rewards. We establish a high-probability regret bound that depends solely on the dimension of the differential-reward model, enabling us to achieve robust regret bounds even when the baseline reward is highly complex. We demonstrate the superior performance of the RoME algorithm in a simulation and two off-policy evaluation studies.

**Relevance (core).** Mobile-health contextual bandit with user- and time-specific random effects, network-cohesion penalties across users, and debiased baseline estimation; regret depends only on the differential-reward dimension. Combines a user graph penalty with time effects, which is the closest applied analogue of our two-channel model; the graph is used as a prior, not certified.

### P14

**Blocked Collaborative Bandits: Online Collaborative Filtering with Per-Item Budget Constraints**  
Soumyabrata Pal, Arun Suggala, Karthikeyan Shanmugam, Prateek Jain. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=Ntd6X7uWYF) · [PDF](http://arxiv.org/pdf/2311.03376v1)

> We consider the problem of \emph{blocked} collaborative bandits where there are multiple users, each with an associated multi-armed bandit problem. These users are grouped into \emph{latent} clusters such that the mean reward vectors of users within the same cluster are identical. Our goal is to design algorithms that maximize the cumulative reward accrued by all the users over time, under the \emph{constraint} that no arm of a user is pulled more than $\mathsf{B}$ times. This problem has been originally considered by \cite{Bresler:2014}, and designing regret-optimal algorithms for it has since remained an open problem. In this work, we propose an algorithm called B-LATTICE (Blocked Latent bAndiTs via maTrIx ComplEtion) that collaborates across users, while simultaneously satisfying the budget constraints, to maximize their cumulative rewards. Theoretically, under certain reasonable assumptions on the latent structure, with $\mathsf{M}$ users, $\mathsf{N}$ arms, $\mathsf{T}$ rounds per user, and $\mathsf{C}=O(1)$ latent clusters, B-LATTICE achieves a per-user regret of  $\widetilde{O}(\sqrt{\mathsf{T}(1 + \mathsf{N}\mathsf{M}^{-1})})$ under a budget constraint of $\mathsf{B}=\Theta(\log \mathsf{T})$. These are the first sub-linear regret bounds for this problem, and match the minimax regret bounds when $\mathsf{B}=\mathsf{T}$. Empirically, we demonstrate that our algorithm has superior performance over baselines even when $\mathsf{B}=1$. B-LATTICE is a phased algorithm where in each phase it clusters users into groups and collaborates across users within a group to quickly learn their reward models.

**Relevance.** Users in latent clusters with identical reward vectors, each item recommendable at most B times per user; matrix-completion-based collaboration. Latent-cluster pooling with equal means, no diameter slack and no validity certificate.

### P15

**Context-lumpable stochastic bandits**  
Chung-Wei Lee, Qinghua Liu, Yasin Abbasi-Yadkori, Chi Jin, Tor Lattimore, Csaba Szepesvari. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=EY7Hpj8Ok6) · [PDF](http://arxiv.org/pdf/2306.13053v2)

> We consider a contextual bandit problem with $S $ contexts and $K $ actions. In each round $t=1,2,\dots$ the learner observes a random context and chooses an action based on its past experience. The learner then observes a random reward whose mean is a function of the context and the action for the round. Under the assumption that the contexts can be lumped into $r\le \min(S ,K)$ groups such that the mean reward for the various actions is the same for any two contexts that are in the same group, we give an algorithm that outputs an $\epsilon$-optimal policy after using at most $\widetilde O(r (S +K )/\epsilon^2)$ samples with high probability and provide a matching $\widetilde\Omega(r (S +K )/\epsilon^2)$ lower bound. In the regret minimization setting, we give an algorithm whose cumulative regret up to time $T$ is bounded by $\widetilde O(\sqrt{r ^3(S +K )T})$. To the best of our knowledge, we are the first to show the near-optimal sample complexity in the PAC setting and $\widetilde O{\sqrt{\text{poly}(r)(S+K)T}}$ minimax regret in the online setting for this problem.  We also show our algorithms can be applied to more general low-rank bandits and get improved regret bounds in some scenarios.

**Relevance.** Contexts (users) lumpable into r groups with identical mean rewards; near-optimal sample complexity and regret in r(S+K). The exact-equality version of our component model (ε_c = 0) with unknown groups.

### P16

**Exploiting Correlated Auxiliary Feedback in Parameterized Bandits**  
Arun Verma, Zhongxiang Dai, Yao Shu, Bryan Kian Hsiang Low. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=vM5VnNQ4n7) · [PDF](http://arxiv.org/pdf/2311.02715v1)

> We study a novel variant of the parameterized bandits problem in which the learner can observe additional auxiliary feedback that is correlated with the observed reward. The auxiliary feedback is readily available in many real-life applications, e.g., an online platform that wants to recommend the best-rated services to its users can observe the user's rating of service (rewards) and collect additional information like service delivery time (auxiliary feedback). In this paper, we first develop a method that exploits auxiliary feedback to build a reward estimator with tight confidence bounds, leading to a smaller regret. We then characterize the regret reduction in terms of the correlation coefficient between reward and its auxiliary feedback. Experimental results in different settings also verify the performance gain achieved by our proposed method.

**Relevance.** Auxiliary feedback correlated with the reward (a control variate with known mean) tightens confidence bounds and reduces regret by a factor depending on the correlation coefficient. Correlation across observations of the same arm, not across arms; the mechanism (known correlation reduces variance) parallels B3.2's contrast gain.

### P17

**Online Clustering of Bandits with Misspecified User Models**  
Zhiyong Wang, Jize Xie, Xutong Liu, Shuai Li, John C.S. Lui. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=CQuRzAgjg9) · [PDF](http://arxiv.org/pdf/2310.02717v2)

> The contextual linear bandit is an important online learning problem where given arm features, a learning agent selects an arm at each round to maximize the cumulative rewards in the long run. A line of works, called the clustering of bandits (CB), utilize the collaborative effect over user preferences and have shown significant improvements over classic linear bandit algorithms. However, existing CB algorithms require well-specified linear user models and can fail when this critical assumption does not hold. Whether robust CB algorithms can be designed for more practical scenarios with misspecified user models remains an open problem. In this paper, we are the first to present the important problem of clustering of bandits with misspecified user models (CBMUM), where the expected rewards in user models can be perturbed away from perfect linear models. We devise two robust CB algorithms, RCLUMB and RSCLUMB (representing the learned clustering structure with dynamic graph and sets, respectively), that can accommodate the inaccurate user preference estimations and erroneous clustering caused by model misspecifications. We prove regret upper bounds of $O(\epsilon_*T\sqrt{md\log T}  + d\sqrt{mT}\log T)$ for our algorithms under milder assumptions than previous CB works, which match the lower bound asymptotically in $T$ up to logarithmic factors, and also match the state-of-the-art results in several degenerate cases. Our regret analysis is novel and different from the typical proof flow of previous CB works. The techniques in proving the regret caused by misclustering users are quite general and may be of independent interest. Experiments on both synthetic and real-world data show our outperformance over previous algorithms.

**Relevance (core).** Clustering of bandits where users in a cluster share the linear part of the reward but deviate by up to ε_*; robust graph- and set-based clustering with regret O(ε_* T √(md log T) + d√(mT) log T). Their per-user deviation is a within-cluster diameter that enters regret linearly, which is the misalignment cost N1 and A1 describe; they tolerate it rather than reject components.


## Theme B. Temporally dependent and non-stationary rewards (fluctuation channel; S5, P1, B3)

### P18

**A Modularized Framework for Piecewise-Stationary Restless Bandits**  
Kuan-Ta Li, Chia-Chun Lin, Ping-Chun Hsieh, Yu-Chih Huang. *AISTATS 2026.* [Page](https://openreview.net/forum?id=Bsj4O76Box) · [PDF](http://arxiv.org/pdf/2604.10177v1)

> We study the piecewise-stationary restless multi-armed bandit (PS-RMAB) problem, where each arm evolves as a Markov chain but \emph{mean rewards may change across unknown segments}. To address the resulting exploration--detection delay trade-off, we propose a modular framework that integrates arbitrary RMAB base algorithms with change detection and a novel diminishing exploration mechanism. This design enables flexible plug-and-play use of existing solvers and detectors, while efficiently adapting to mean changes without prior knowledge of their number. To evaluate performance, we introduce a refined regret notion that measures the \emph{excess regret due to exploration and detection}, benchmarked against an oracle that restarts the base algorithm at the true change points. Under this metric, we prove a regret bound of $\tilde{O}(\sqrt{LMKT})$, where $L$ denotes the maximum mixing time of the Markov chains across all arms and segments, $M$ the number of segments, $K$ the number of arms, and $T$ the horizon. Simulations confirm that our framework achieves regret close to that of the segment oracle and consistently outperforms base solvers that do not incorporate any mechanism to handle environmental hanges.

**Relevance.** Piecewise-stationary restless bandits: arms are Markov chains whose mean rewards change across unknown segments; modular change detection with diminishing exploration; regret Õ(√(LMKT)) with mixing time L. Restless Markov arms with regime changes; the mixing time plays the role our long-run variance plays.

### P19

**Explore-then-Commit for Nonstationary Linear Bandits with Latent Dynamics**  
Sunmook Choi, Yahya Sattar, Yassir Jedra, Maryam Fazel, Sarah Dean. *AISTATS 2026.* [Page](https://openreview.net/forum?id=2gbhbWlmQq) · [PDF](http://arxiv.org/pdf/2510.16208v1)

> We study a nonstationary bandit problem where rewards depend on both actions and latent states, the latter governed by unknown linear dynamics. Crucially, the state dynamics also depend on the actions, resulting in tension between short-term and long-term rewards. We propose an explore-then-commit algorithm for a finite horizon $T$. During the exploration phase, random Rademacher actions enable estimation of the Markov parameters of the linear dynamics, which characterize the action-reward relationship. In the commit phase, the algorithm uses the estimated parameters to design an optimized action sequence for long-term reward. Our proposed algorithm achieves $\tilde{\mathcal{O}}(pT^{2/3})$ regret where $p$ is the action dimension. Our analysis handles two key challenges: learning from temporally correlated rewards, and designing action sequences with optimal long-term reward. We address the first challenge by providing near-optimal sample complexity and error bounds for system identification using bilinear rewards. We address the second challenge by proving an equivalence with indefinite quadratic optimization over a hypercube, a known NP-hard problem. We provide a sub-optimality guarantee for this problem, enabling our regret upper bound. Lastly, we propose a semidefinite relaxation with Goemans-Williamson rounding as a practical approach.

**Relevance (core).** Rewards bilinear in the action and a latent state with unknown stable linear dynamics driven by the actions; explore-then-commit with Õ(pT^{2/3}) regret; the exploration phase must learn from temporally correlated rewards. Endogenous latent dynamics; our dynamics are exogenous, but their system-identification error bounds under correlated rewards are the kind of estimated-dynamics result our certificate needs.

### P20

**On the Complexity of Best-Arm Identification in Non-Stationary Linear Bandits**  
Leo Maynard-Zhang, Zhihan Xiong, Kevin Jamieson, Maryam Fazel. *COLT 2026.* [Page](https://proceedings.mlr.press/v336/maynard-zhang26a.html) · [PDF](http://arxiv.org/pdf/2603.10346v1)

> We study the fixed-budget best-arm identification (BAI) problem in non-stationary linear bandits. Concretely, given a fixed time budget $T\in \mathbb{N}$, finite arm set $\mathcal{X} \subset \mathbb{R}^d$, and a potentially adversarial sequence of unknown parameters $\lbrace \theta_t\rbrace_{t=1}^{T}$ (hence non-stationary), a learner aims to identify the arm with the largest cumulative reward $x_* = \arg\max_{x \in \mathcal{X}} x^\top\sum_{t=1}^T \theta_t$ with high probability. In this setting, it is well-known that i.i.d. sampling arms from the G-optimal design yields a minimax-optimal error probability of $\exp\left(-\Theta\left(T / H_{G}\right)\right)$, where $H_{G}$ scales proportionally with the dimension $d$. However, this notion of complexity is overly pessimistic, as it is derived from a lower bound in which the arm set consists only of the standard basis vectors, thus masking any potential advantages arising from arm sets with richer geometric structure. To address this, we establish an \textit{arm-set-dependent} lower bound that, in contrast, holds for any arm set. Motivated by the ideas underlying our lower bound, we propose the \textit{Adjacent-optimal design}, a specialization of the well-known $\mathcal{XY}$-optimal design, and develop the \textsf{Adjacent-BAI} algorithm. We prove that the error probability of \textsf{Adjacent-BAI} matches our lower bound up to constants, verifying the tightness of our lower bound, and establishing the arm-set-dependent complexity of this setting.

**Relevance.** Complexity of fixed-budget BAI in non-stationary linear bandits is governed by adjacent arm pairs, an arm-set-dependent geometry. Geometry beyond pairwise gaps determines difficulty, in the spirit of our path-versus-clique separation (A2), here for non-stationary identification.

### P21

**A Direct Approach for Handling Contextual Bandits with Latent State Dynamics**  
Zhen LI, Gilles Stoltz. *ICML 2026.* [Page](https://openreview.net/forum?id=7NA81PFi77) · [PDF](http://arxiv.org/pdf/2604.08149v2)

> We consider a linear contextual bandit model where contexts and rewards are governed by a finite hidden Markov chain. We first revisit the simplified model by Nelson et al. (2022), in which rewards are linear functions of the posterior probabilities over the hidden states given the observed contexts (called beliefs), rather than functions of the hidden states themselves. This simplified model may be handled through a direct reduction to standard linear contextual bandits. We extend the theoretical analysis of this reduction to take into account the estimation of the parameters of the hidden Markov model [HMM] in the regret bound and to provide high-probability bounds not depending anymore on the reward functions and only depending on the model through the estimation of the HMM parameters. Second, and most importantly, we instead study the more natural and more complex model incorporating direct dependencies in the hidden states (on top of dependencies on the observed contexts, as is natural for contextual bandits). Under a classic HMM forgetting condition, the main algorithmic tool introduced to cope with the various statistical dependencies that the reward structure introduces is to only periodically update reward-model parameters.

**Relevance.** Linear contextual bandits whose contexts and rewards are governed by a finite hidden Markov chain; reduction to linear bandits via beliefs, with the HMM estimation error entering the regret; periodic parameter updates handle the dependence. A Markov-state version of persistence with forgetting conditions; relevant to how estimated dynamics enter guarantees.

### P22

**DAL: A Practical Prior-Free Black-Box Framework for Piecewise Stationary Bandits**  
Argyrios Gerogiannis, Yu-Han Huang, Subhonmesh Bose, Venugopal Veeravalli. *ICML 2026.* [Page](https://openreview.net/forum?id=eNvxTIZugB) · [PDF](http://arxiv.org/pdf/2501.19401v5)

> We introduce a practical, black-box framework termed Detection Augmented Learning (DAL) for the problem of piecewise stationary bandits without knowledge of the underlying non-stationarity. DAL accepts any stationary bandit algorithm with order-optimal regret as input and augments it with a change detector, enabling applicability to all common bandit variants. Extensive experimentation demonstrates that DAL consistently surpasses all state-of-the-art methods across diverse non-stationary scenarios, including synthetic benchmarks and real-world datasets, underscoring its versatility and scalability. We provide theoretical insights into DAL's strong empirical performance, complemented by thorough empirical validation.

**Relevance.** Detection Augmented Learning: any order-optimal stationary bandit algorithm plus a change detector, prior-free, for piecewise-stationary bandits of all kinds; extensive experiments including real data. Representative of the change-detection family we compare against (abrupt change rather than persistence).

### P23

**Generalized Linear Bandits with Memory**  
Heesang Ann, Hyunjun Choi, Taehyun Hwang, Younghoon Shin, Haeju Cheong, Min-hwan Oh. *ICML 2026.* [Page](https://openreview.net/forum?id=DfZS0M8leJ) · [PDF](http://arxiv.org/pdf/2608.15848v1)

> We study generalized linear bandits with memory, an endogenous non-stationary setting in which rewards depend on past actions through a finite memory matrix. Building on prior work for linear models Clerici et al.,(2024), we show that the previously known $\tilde{\mathcal{O}}(T^{3/4})$ regret bound stems from a loose analysis, and we provide a sharpened analysis that recovers a $\tilde{\mathcal{O}}(\sqrt{T})$ regret rate in the linear case. We then extend this improvement to generalized linear models and propose a block-wise algorithm based on shrunken confidence bounds. Our algorithm achieves a regret bound of $\tilde{\mathcal{O}}\left(\sqrt{mT} + d\sqrt{T} + \sqrt{\kappa}d^{2} m^{1/4} T^{1/4} + \kappa d^{2} \right)$, where $d$ denotes the feature dimension, $m$ the memory length, and $\kappa$ a curvature parameter of the link function. This attains a $\sqrt{T}$-type rate despite nonlinear rewards and memory effects. To the best of our knowledge, this analysis provides a unified treatment of memory-induced non-stationarity and nonlinear link functions, while ensuring that the leading regret term is independent of the curvature of the link function. We conduct numerical experiments that are consistent with our theoretical findings.

**Relevance.** Generalized linear bandits with memory: rewards depend on past actions through a finite memory matrix; block-wise algorithm with shrunken confidence bounds reaches √T rates. Endogenous memory over structured action spaces; the block-wise confidence construction (commit to a block, update after) is a bursty-exposure design.

### P24

**Adaptive Exploration for Latent-State Bandits**  
Jikai Jin, Kenneth Hung, Sanath Kumar Krishnamurthy, Baoyi Shi, Congshan Zhang. *KDD 2026.* [Page](https://doi.org/10.1145/3770855.3817882) · [PDF](http://arxiv.org/pdf/2602.05139v3)

> We study bandits whose rewards depend on an unobserved Markov state that evolves independently of the learner's actions. The optimal arm can change even though the learner observes only past actions and rewards. We propose algorithms that feed LinUCB with two summaries of the hidden state: a lagged action-reward pair and, when available, a probe fingerprint formed from rewards of multiple arms. The adaptive variants refresh the fingerprint using residual, margin, and staleness tests. In synthetic stress tests over state count, transition rate, noise, and horizon, these methods reduce dynamic regret relative to standard, adversarial, and non-stationary bandit baselines when the summaries distinguish states and are updated often enough. Ablations and misspecification tests identify the main failure modes: weak fingerprint separation, high noise, and state changes during sequential probes.

**Relevance (core).** KDD 2026: rewards depend on an unobserved Markov state evolving independently of actions; LinUCB fed with lagged action-reward pairs and probe fingerprints from several arms; synthetic stress tests. The KDD-side version of exogenous latent dynamics; the probe fingerprint is a slate-style joint observation, as in our B3.2.

### P25

**Best Arm Identification for Bandits with Shifting Means**  
Lukas Zierahn, Wouter M. Koolen, Shubhada Agrawal, Christina Katsimerou, Dirk van der Hoeven. *NeurIPS 2026 (accepted; arXiv version).* [Page](http://arxiv.org/abs/2610.10488v1) · [PDF](http://arxiv.org/pdf/2610.10488v1)

> We study the best arm identification problem in a stochastic environment with a novel form of adversarial perturbations, which we coin Shifting Means. While classically the mean rewards of the $K$ arms are stable in time, in Shifting Means only the gaps $\boldsymbolΔ$ between mean rewards are stable, while their common shift may be determined adversarially in each round. The objective of the learner is to identify the best arm with high probability while minimizing sample complexity (the fixed confidence setting). Handling shifts requires new tools: we show that algorithms employing a Generalized Likelihood Ratio Test (GLRT) stopping rule, including the popular Track-and-Stop, fail under time-varying shifts. Instead, we propose Importance Weights for Shifting Means ($\mathsf{ISM}$). Assuming means bounded by $U$ and $σ^2$-sub-Gaussian rewards, we show $\mathsf{ISM}$ to be $δ$-correct and to enjoy a sample complexity bound of order $K (σ^2 + U^2) Δ_{\min}^{-2} \ln \frac{1}δ$. We also present a matching (up to constant factors) worst-case lower bound and evaluate our results empirically.

**Relevance (core).** Best-arm identification when all arms' means share an arbitrary, possibly adversarial common shift each round while gaps are stable; GLRT stopping rules such as Track-and-Stop fail; importance weights restore δ-correctness. The common shift is exactly the common factor our Wikipedia and KuaiRec panels show carries most of the graph-covariance gain (S6); their failure of GLRT stopping under shifts is a decision-level analogue of B2.

### P26

**Block Optimism for Nonstationary Bandits with Latent Linear Dynamics**  
Taehyun Hwang, Hyunjun Choi, Heesang Ann, Min-hwan Oh. *NeurIPS 2026 (accepted; arXiv version).* [Page](http://arxiv.org/abs/2610.00911v1) · [PDF](http://arxiv.org/pdf/2610.00911v1)

> We study an endogenous nonstationary stochastic bandit problem with latent linear dynamics, where actions affect both immediate rewards and the future evolution of an unobserved latent state. Rewards are bilinear in the current action and latent state, inducing history-dependent rewards and a nontrivial long-horizon planning problem. The existing explore-then-commit approach achieves $\tilde{O}(T^{2/3})$ regret by uniformly exploring to estimate the latent dynamics and then committing to an optimized open-loop action sequence. We show that this rate can be improved via adaptive block-level optimism. Our key step is a cyclic approximation: under stable dynamics, the infinite-memory reward process can be truncated, and the open-loop benchmark can be approximated by optimizing a finite-memory block-level proxy. Building on this reduction, we propose a UCB-based block algorithm that maintains confidence sets for the truncated dynamics parameters and selects blocks optimistically. We prove a regret bound of order $\tilde{O}(\sqrt T)$, significantly improving over the previous $\tilde{O}(T^{2/3})$ guarantee for the same model. To the best of our knowledge, this is the first $\tilde{O}(\sqrt T)$ regret guarantee for latent linear-dynamics bandits with bilinear reward observations and an open-loop action-sequence benchmark.

**Relevance (core).** Same latent-linear-dynamics model; block-level optimism with a finite-memory cyclic approximation gives Õ(√T). Shows that under stable dynamics the infinite-memory reward process can be truncated, which is the same geometric-decay argument behind our long-run substitution (B3.1).

### P27

**Lower Bounds for Time-Varying Kernelized Bandits**  
Xu Cai, Jonathan Scarlett. *AISTATS 2025.* [Page](https://openreview.net/forum?id=hAQnKnkCT4) · [PDF](http://arxiv.org/pdf/2410.16692v2)

> The optimization of black-box functions with noisy observations is a fundamental problem with widespread applications, and has been widely studied under the assumption that the function lies in a reproducing kernel Hilbert space (RKHS).  This problem has been studied extensively in the stationary setting, and near-optimal regret bounds are known via developments in both upper and lower bounds.  In this paper, we consider non-stationary scenarios, which are crucial for certain applications but are currently less well-understood.  Specifically, we provide the first algorithm-independent lower bounds, where the time variations are subject satisfying a total variation budget according to some function norm.  Under $\ell_{\infty}$-norm variations, our bounds are found to be close to an existing upper bound (Hong et al., 2023).  Under RKHS norm variations, the upper and lower bounds are still reasonably close but with more of a gap, raising the interesting open question of whether non-minor improvements in the upper bound are possible.

**Relevance.** First algorithm-independent lower bounds for time-varying kernelized bandits under total-variation budgets in sup and RKHS norms. See [4].

### P28

**Near-Optimal Algorithm for Non-Stationary Kernelized Bandits**  
Shogo Iwazaki, Shion Takeno. *AISTATS 2025.* [Page](https://openreview.net/forum?id=1y9UG4YOnm) · [PDF](http://arxiv.org/pdf/2410.16052v1)

> This paper studies a non-stationary kernelized bandit (KB) problem, also called time-varying Bayesian optimization, where one seeks to minimize the regret under an unknown reward function that varies over time. In particular, we focus on a near-optimal algorithm whose regret upper bound matches the regret lower bound. For this goal, we show the first algorithm-independent regret lower bound for non-stationary KB with squared exponential and Mat\'ern kernels, which reveals that an existing optimization-based KB algorithm with slight modification is near-optimal. However, this existing algorithm suffers from feasibility issues due to its huge computational cost. Therefore, we propose a novel near-optimal algorithm called restarting phased elimination with random permutation (R-PERP), which bypasses the huge computational cost. A technical key point is the simple permutation procedures of query candidates, which enable us to derive a novel tighter confidence bound tailored to the non-stationary problems.

**Relevance.** Near-optimal non-stationary kernelized bandits (time-varying Bayesian optimization): first lower bounds for SE and Matérn kernels; restarting phased elimination with random permutation. With [7] and [9], the current theory of time-varying GP bandits, all under variation budgets rather than autocorrelated dynamics.

### P29

**Time-varying Gaussian Process Bandits with Unknown Prior**  
Juliusz Ziomek, Masaki Adachi, Michael A Osborne. *AISTATS 2025.* [Page](https://openreview.net/forum?id=IG44SrW8l9) · [PDF](http://arxiv.org/pdf/2402.01632v4)

> Bayesian optimisation requires fitting a Gaussian process model, which in turn requires specifying prior on the unknown black-box function---most of the theoretical literature assumes this prior is known. However, it is common to have more than one possible prior for a given black-box function, for example suggested by domain experts with differing opinions. In some cases, the type-II maximum likelihood estimator for selecting prior enjoys the consistency guarantee, but it does not universally apply to all types of priors. If the problem is stationary, one could rely on the Regret Balancing scheme to conduct the optimisation, but in the case of time-varying problems, such a scheme cannot be used.  To address this gap in existing research, we propose a novel algorithm, PE-GP-UCB, which is capable of solving time-varying Bayesian optimisation problems even without the exact knowledge of the function's prior.  The algorithm relies on the fact that either the observed function values are consistent with some of the priors, in which case it is easy to reject the wrong priors, or the observations are consistent with all candidate priors, in which case it does not matter which prior our model relies on. We provide a regret bound on the proposed algorithm. Finally, we empirically evaluate our algorithm on toy and real-world time-varying problems and show that it outperforms the maximum likelihood estimator, fully Bayesian treatment of unknown prior and Regret Balancing.

**Relevance.** Time-varying GP bandits when the prior (kernel) is unknown: reject priors inconsistent with the data, with a regret bound; real-world time-varying problems. Model selection among candidate dynamics models, which our estimated-dynamics certificates also need (lag-order selection is our open item 4).

### P30

**Variance-Dependent Regret Bounds for Nonstationary Linear Bandits**  
Zhiyong Wang, Jize Xie, Yi Chen, John C.S. Lui, Dongruo Zhou. *AISTATS 2025.* [Page](https://openreview.net/forum?id=H6Co3RbkGB) · [PDF](https://raw.githubusercontent.com/mlresearch/v258/main/assets/wang25g/wang25g.pdf)

> We investigate the non-stationary stochastic linear bandit problem where the reward distribution evolves each round. Existing algorithms characterize the non-stationarity by the total variation budget $B_K$, which is the summation of the change of the consecutive feature vectors of the linear bandits over $K$ rounds. However, such a quantity only measures the non-stationarity with respect to the expectation of the reward distribution, which makes existing algorithms sub-optimal under the general non-stationary distribution setting. In this work, we propose algorithms that utilize the variance of the reward distribution as well as the $B_K$, and show that they can achieve tighter regret upper bounds. Specifically, we introduce two novel algorithms: Restarted Weighted$\text{OFUL}^+$ and Restarted $\text{SAVE}^+$. These algorithms address cases where the variance information of the rewards is known and unknown, respectively. Notably, when the total variance $V_K$ is much smaller than $K$, our algorithms outperform previous state-of-the-art results on non-stationary stochastic linear bandits under different settings. Experimental evaluations further validate the superior performance of our proposed algorithms over existing works.

**Relevance.** Non-stationary linear bandits with variance-dependent regret: using the reward variance as well as the variation budget B_K tightens dynamic regret. Variation-budget non-stationarity; no temporal correlation structure.

### P31

**Experimenting, Fast and Slow: Bayesian Optimization of Long-term Outcomes with Online Experiments**  
Qing Feng, Samuel Daulton, Benjamin Letham, Maximilian Balandat, Eytan Bakshy. *KDD 2025.* [Page](https://doi.org/10.1145/3690624.3709419) · [PDF](http://arxiv.org/pdf/2506.18744v2)

> Online experiments in internet systems, also known as A/B tests, are used for a wide range of system tuning problems, such as optimizing recommender system ranking policies and learning adaptive streaming controllers. Decision-makers generally wish to optimize for long-term treatment effects of the system changes, which often requires running experiments for a long time as short-term measurements can be misleading due to non-stationarity in treatment effects over time. The sequential experimentation strategies--which typically involve several iterations--can be prohibitively long in such cases. We describe a novel approach that combines fast experiments (e.g., biased experiments run only for a few hours or days) and/or offline proxies (e.g., off-policy evaluation) with long-running, slow experiments to perform sequential, Bayesian optimization over large action spaces in a short amount of time.

**Relevance.** KDD 2025: Bayesian optimization over A/B tests that combines fast biased experiments and offline proxies with slow long-running ones, because short-term measurements mislead under non-stationary treatment effects. Practitioner evidence that treatment effects persist and drift over days, the regime of experiment proposal 1.

### P32

**Off-Policy Evaluation and Learning for the Future under Non-Stationarity**  
Tatsuhiro Shimizu, Kazuki Kawamura, Takanori Muroi, Yusuke Narita, Kei Tateno, Takuma Udagawa, Yuta Saito. *KDD 2025.* [Page](https://doi.org/10.1145/3690624.3709237) · [PDF](https://arxiv.org/pdf/2506.20417)

> We study the novel problem of future off-policy evaluation (F-OPE) and learning (F-OPL) for estimating and optimizing the future value of policies in non-stationary environments, where distributions vary over time. In e-commerce recommendations, for instance, our goal is often to estimate and optimize the policy value for the upcoming month using data collected by an old policy in the previous month. A critical challenge is that data related to the future environment is not observed in the historical data. Existing methods assume stationarity or depend on restrictive reward-modeling assumptions, leading to significant bias. To address these limitations, we propose a novel estimator named Off-Policy Estimator for the Future Value (OPFV), designed for accurately estimating policy values at any future time point. The key feature of OPFV is its ability to leverage the useful structure within time-series data. While future data might not be present in the historical log, we can leverage, for example, seasonal, weekly, or holiday effects that are consistent in both the historical and future data. Our estimator is the first to exploit these time-related structures via a new type of importance weighting, enabling effective F-OPE. Theoretical analysis identifies the conditions under which OPFV becomes low-bias. In addition, we extend our estimator to develop a new policy-gradient method to proactively learn a good future policy using only historical data. Empirical results show that our methods substantially outperform existing methods in estimating and optimizing the future policy value under non-stationarity for various experimental setups.

**Relevance (core).** KDD 2025: future off-policy evaluation and learning under non-stationarity, exploiting seasonal, weekly and holiday structure shared between past and future data through a new importance weighting. The same long-run time structure (weekly lags) that our inflation diagnostic needs, used for offline evaluation rather than online confidence.

### P33

**Quick Draw Bandits: Quickly Optimizing in Nonstationary Environments with Extremely Many Arms**  
Derek Everett, Fred Lu, Edward Raff, Fernando Camacho, James Holt. *KDD 2025.* [Page](https://doi.org/10.1145/3711896.3737097) · [PDF](https://arxiv.org/pdf/2505.24692)

> Canonical algorithms for multi-armed bandits typically assume a stationary reward environment where the size of the action space (number of arms) is small. More recently developed methods typically relax only one of these assumptions: existing non-stationary bandit policies are designed for a small number of arms, while Lipschitz, linear, and Gaussian process bandit policies are designed to handle a large (or infinite) number of arms in stationary reward environments under constraints on the reward function. In this manuscript, we propose a novel policy to learn reward environments over a continuous space using Gaussian interpolation. We show that our method efficiently learns continuous Lipschitz reward functions with $\mathcal{O}^*(\sqrt{T})$ cumulative regret. Furthermore, our method naturally extends to non-stationary problems with a simple modification. We finally demonstrate that our method is computationally favorable (100-10000x faster) and experimentally outperforms sliding Gaussian process policies on datasets with non-stationarity and an extremely large number of arms.

**Relevance (core).** KDD 2025: Gaussian-interpolation bandit over a continuous arm space with a non-stationary extension, 100–10000× faster than sliding GP policies, on datasets with non-stationarity and very many arms. The KDD-side baseline for 'many arms plus drift'; similarity between arms is Lipschitz in a metric, not a mined graph, and time dependence is a window, not a model.

### P34

**A/B Testing and Best-arm Identification for Linear Bandits with Robustness to Non-stationarity**  
Zhihan Xiong, Romain Camilleri, Maryam Fazel, Lalit Jain, Kevin Jamieson. *AISTATS 2024.* [Page](https://proceedings.mlr.press/v238/xiong24a.html) · [PDF](https://proceedings.mlr.press/v238/xiong24a/xiong24a.pdf)

> We investigate the fixed-budget best-arm identification (BAI) problem for linear bandits in a potentially non-stationary environment. Given a finite arm set $\mathcal{X}\subset\mathbb{R}^d$, a fixed budget $T$, and an unpredictable sequence of parameters $\left\lbrace\theta_t\right\rbrace_{t=1}^{T}$, an algorithm will aim to correctly identify the best arm $x^* := \arg\max_{x\in\mathcal{X}}x^\top\sum_{t=1}^{T}\theta_t$ with probability as high as possible. Prior work has addressed the stationary setting where $\theta_t = \theta_1$ for all $t$ and demonstrated that the error probability decreases as $\exp(-T /\rho^*)$ for a problem-dependent constant $\rho^*$. But in many real-world $A/B/n$ multivariate testing scenarios that motivate our work, the environment is non-stationary and an algorithm expecting a stationary setting can easily fail. For robust identification, it is well-known that if arms are chosen randomly and non-adaptively from a G-optimal design over $\mathcal{X}$ at each time then the error probability decreases as $\exp(-T\Delta^2_{(1)}/d)$, where $\Delta_{(1)} = \min_{x \neq x^*} (x^* - x)^\top \frac{1}{T}\sum_{t=1}^T \theta_t$. As there exist environments where $\Delta_{(1)}^2/ d \ll 1/ \rho^*$, we are motivated to propose a novel algorithm P1-RAGE that aims to obtain the best of both worlds: robustness to non-stationarity and fast rates of identification in benign settings. We characterize the error probability of P1-RAGE and demonstrate empirically that the algorithm indeed never performs worse than G-optimal design but compares favorably to the best algorithms in the stationary setting.

**Relevance (core).** A/B testing and best-arm identification in linear bandits when arm values change arbitrarily over time; randomized designs with IPS estimators identify the counterfactual best treatment. Motivation overlaps ours (hour-to-hour non-stationarity in experiments); their fix is randomization against adversarial variation, ours is modelling persistence.

### P35

**Autoregressive Bandits**  
Francesco Bacchiocchi, Gianmarco Genalti, Davide Maran, Marco Mussi, Marcello Restelli, Nicola Gatti, Alberto Maria Metelli. *AISTATS 2024.* [Page](https://proceedings.mlr.press/v238/bacchiocchi24a.html) · [PDF](https://proceedings.mlr.press/v238/bacchiocchi24a/bacchiocchi24a.pdf)

> Autoregressive processes naturally arise in a large variety of real-world scenarios, including stock markets, sales forecasting, weather prediction, advertising, and pricing. When facing a sequential decision-making problem in such a context, the temporal dependence between consecutive observations should be properly accounted for guaranteeing convergence to the optimal policy. In this work, we propose a novel online learning setting, namely, Autoregressive Bandits (ARBs), in which the observed reward is governed by an autoregressive process of order $k$, whose parameters depend on the chosen action. We show that, under mild assumptions on the reward process, the optimal policy can be conveniently computed. Then, we devise a new optimistic regret minimization algorithm, namely, AutoRegressive Upper Confidence Bound (AR-UCB), that suffers sublinear regret of order $\tilde{O} ( \frac{(k+1)^{3/2}\sqrt{nT}}{(1-\Gamma)^2} )$, where $T$ is the optimization horizon, $n$ is the number of actions, and $\Gamma < 1$ is a stability index of the process. Finally, we empirically validate our algorithm, illustrating its advantages w.r.t. bandit baselines and its robustness to misspecification of key parameters.

**Relevance (core).** Rewards follow an AR(k) process whose coefficients depend on the chosen action; the optimal policy is stationary and closed-loop; AR-UCB has regret Õ((k+1)^{3/2}√(nT)/(1−Γ)^2). Action-dependent AR dynamics against our exogenous AR(p) fields; the (1−Γ)^{-2} persistence cost matches the (1−φ)^{-2} factor in B1's corollary.

### P36

**Almost Minimax Optimal Best Arm Identification in Piecewise Stationary Linear Bandits**  
Yunlong Hou, Vincent Y. F. Tan, Zixin Zhong. *NeurIPS 2024.* [Page](https://openreview.net/forum?id=Q5e3ftQ3q3) · [PDF](http://arxiv.org/pdf/2410.07638v1)

> We propose a novel piecewise stationary linear bandit (PSLB) model, where the environment randomly samples a context from an unknown probability distribution at each changepoint, and the quality of an arm is measured by its return averaged over all contexts. The contexts and their distribution, as well as the changepoints are unknown to the agent. We design Piecewise-Stationary $\varepsilon$-Best Arm Identification$^+$ (PS$\varepsilon$BAI$^+$), an algorithm that is guaranteed to identify an $\varepsilon$-optimal arm with probability $\ge 1-\delta$ and with a minimal number of samples. PS$\varepsilon$BAI$^+$ consists of two subroutines, PS$\varepsilon$BAI and Naïve $\varepsilon$-BAI (N$\varepsilon$BAI), which are executed in parallel. PS$\varepsilon$BAI actively detects changepoints and aligns contexts to facilitate the arm identification process. When  PS$\varepsilon$BAI and N$\varepsilon$BAI are utilized judiciously in parallel,  PS$\varepsilon$BAI$^+$ is shown to have a finite expected sample complexity. By proving a  lower bound, we show the expected sample complexity of PS$\varepsilon$BAI$^+$ is optimal up to a logarithmic factor. We compare PS$\varepsilon$BAI$^+$ to baseline algorithms using numerical experiments which demonstrate its   efficiency. Both our analytical and numerical results corroborate that the efficacy   of PS$\varepsilon$BAI$^+$ is due to   the delicate change detection and context alignment procedures embedded in PS$\varepsilon$BAI.

**Relevance.** Fixed-confidence BAI in piecewise-stationary linear bandits where contexts are resampled at change points; change detection and context alignment give near-optimal sample complexity. Irrevocable identification under non-stationarity, the decision type our B2 consequence concerns.

### P37

**Non-Stationary Bandits with Auto-Regressive Temporal Dependency**  
Qinyi Chen, Negin Golrezaei, Djallel Bouneffouf. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=tP50lLiZIo) · [PDF](http://arxiv.org/pdf/2210.16386v3)

> Traditional multi-armed bandit (MAB) frameworks, predominantly examined under stochastic or adversarial settings, often overlook the temporal dynamics inherent in many real-world applications such as recommendation systems and online advertising. This paper introduces a novel non-stationary MAB framework that captures the temporal structure of these real-world dynamics through an auto-regressive (AR) reward structure. We propose an algorithm that integrates two key mechanisms: (i) an alternation mechanism adept at leveraging temporal dependencies to dynamically balance exploration and exploitation, and (ii) a restarting mechanism designed to discard out-of-date information. Our algorithm achieves a regret upper bound that nearly matches the lower bound, with regret measured against a robust dynamic benchmark. Finally, via a real-world case study on tourism demand prediction, we demonstrate both the efficacy of our algorithm and the broader applicability of our techniques to more complex, rapidly evolving time series.

**Relevance (core).** Non-stationary MAB with an AR reward structure; alternation plus restarting; near-matching regret against a dynamic benchmark; tourism demand case study. The paper already cited as O11; it has no mean-channel structure and no confidence guarantee for fixed means.

### P38

**Tracking Most Significant Shifts in Nonparametric Contextual Bandits**  
Joe Suk, Samory Kpotufe. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=SGerL9HMrp) · [PDF](http://arxiv.org/pdf/2307.05341v2)

> We study nonparametric contextual bandits where Lipschitz mean reward functions may change over time. We first establish the minimax dynamic regret rate in this less understood setting in terms of number of changes $L$ and total-variation $V$, both capturing all changes in distribution over context space, and argue that state-of-the-art procedures are suboptimal in this setting. Next, we tend to the question of an _adaptivity_ for this setting, i.e. achieving the minimax rate without knowledge of $L$ or $V$. Quite importantly, we posit that the bandit  problem, viewed locally at a given context $X_t$, should not be affected by reward changes in other parts of context space $\cal X$. We therefore propose a notion of _change_, which we term _experienced significant shifts_, that better accounts for locality, and thus counts considerably less changes than $L$ and $V$. Furthermore, similar to recent work on non-stationary MAB (Suk & Kpotufe, 2022), _experienced significant shifts_ only count the most _significant_ changes in mean rewards, e.g., severe best-arm changes relevant to observed contexts. Our main result is to show that this more tolerant notion of change can in fact be adapted to.

**Relevance.** Nonparametric (Lipschitz) contextual bandits with changing rewards; minimax dynamic regret in L and V, and adaptivity to 'experienced significant shifts' that count only changes relevant to observed contexts. Defines non-stationarity by its effect on decisions, which is how we present B2's consequence (only shifts that cross a gap matter).


## Theme C. Confidence sequences, anytime-valid inference, and inference after adaptive sampling (bridge; B1, B2)

### P39

**Kernel Treatment Effects with Adaptively Collected Data**  
Houssam Zenati, Bariscan Bozkurt, Arthur Gretton. *AISTATS 2026.* [Page](https://proceedings.mlr.press/v300/zenati26a.html) · [PDF](http://arxiv.org/pdf/2510.10245v2)

> Adaptive experiments improve efficiency by adjusting treatment assignments based on past outcomes, but this adaptivity breaks the i.i.d. assumptions that underpin classical asymptotics. At the same time, many questions of interest are distributional, extending beyond average effects. Kernel treatment effects (KTE) provide a flexible framework by representing interventional outcome distributions in an RKHS and comparing them via kernel distances. We present the first kernel-based framework for distributional inference under adaptive data collection. Our method combines doubly robust RKHS scores with a witness function learned on one fold, and performs inference on a second fold using a projected, sequentially normalized scalar statistic with valid type-I error. Experiments show that the resulting procedure is well calibrated and effective for both mean shifts and higher-moment differences, outperforming adaptive baselines limited to scalar effects.

**Relevance.** Kernel treatment effects (distributional) under adaptive data collection, with sample-split sequential normalization. Shows the breakage of iid asymptotics under adaptive logging that motivates all of theme C.

### P40

**Self-Normalized Martingales and Uniform Regret Bounds for Linear Regression**  
Fan Chen, Jian Qian, Alexander Rakhlin, Nikita Zhivotovskiy. *COLT 2026.* [Page](https://proceedings.mlr.press/v336/chen26f.html) · [PDF](http://arxiv.org/pdf/2605.01628v1)

> Self-normalized martingale inequalities lie at the heart of confidence ellipsoids for online least squares and, more broadly, many bandit and reinforcement-learning results. Yet existing vector and scalar results typically rely on bounded covariates and an explicit regularization matrix, producing bounds that are \emph{not scale-invariant}: although the self-normalized quantity is scale-invariant by definition, its standard upper bounds are not. We characterize when scale-invariant upper bounds on self-normalized martingales are possible. Without further assumptions, we prove that nontrivial scale-invariant bounds exist only in dimension $d=1$; moreover, in $d=1$ we obtain $O(\log T)$ scale-invariant self-normalized bounds without any assumptions on the covariates. In contrast, for $d>1$ we show that no nontrivial scale-invariant bound can hold in full generality. We then connect this dichotomy to \emph{doubly-uniform} regret in online linear regression (i.e., regret bounds that are simultaneously independent of the covariate scale and the comparator norm) and use it to resolve the open question of Gaillard, Gerchinovitz, Huard, and Stoltz, \emph{“Uniform regret bounds over $\mathbb{R}^d$ for the sequential linear regression problem with the square loss”} (ALT 2019): in $d=1$ we give an explicit algorithm with $O(\log T)$ doubly-uniform regret, whereas for $d>1$ sublinear doubly-uniform regret is impossible. Finally, under a natural \emph{smoothness} condition (bounded Radon–Nikodym derivatives of the conditional covariate laws with respect to a fixed base measure), we recover sublinear regret for $d>1$ without bounded covariates and derive a self-normalized concentration inequality free of the usual regularization penalties, yielding arguably a first natural scale-invariant bound for adaptive, non-i.i.d. vector martingales.

**Relevance.** COLT 2026: scale-invariant self-normalized martingale inequalities and their equivalence with doubly uniform regret in linear regression. Foundations for S2-type bounds; relevant to removing the regularization term's scale dependence.

### P41

**Asymptotically Optimal Sequential Testing with Markovian Data**  
Alhad Sethi, Kavali Sofia Sagar, Shubhada Agrawal, Debabrota Basu, P. N. Karthik. *ICML 2026.* [Page](https://openreview.net/forum?id=YEckWPoS09) · [PDF](http://arxiv.org/pdf/2602.17587v3)

> We study one-sided and $\alpha$-correct sequential hypothesis testing for data generated by an ergodic, finite-state Markov chain. The *null* hypothesis is that the unknown transition matrix belongs to a prescribed set $\cal P$ of stochastic matrices, and the *alternative* corresponds to a disjoint set $\cal Q$. We establish *a non-asymptotic instance-dependent lower bound* on the expected stopping time of any valid sequential test under the alternative, which is asymptotically tight. Our novel analysis improves the existing lower bounds, which are either asymptotic or provably sub-optimal in this setting. Our lower bound incorporates both the stationary distribution and the transition structure induced by the unknown Markov chain. We further propose an optimal test whose expected stopping time matches this lower bound asymptotically as $\alpha \to 0$. We illustrate the usefulness of our framework through applications to sequential detection of model misspecification in Markov Chain Monte Carlo and to testing structural properties, such as the linearity of transition dynamics, in Markov decision processes. Our findings yield a sharp and general characterization of optimal sequential testing procedures under Markovian dependence.

**Relevance (core).** Asymptotically optimal α-correct power-one sequential tests for data from an ergodic finite-state Markov chain, with instance-dependent lower bounds on stopping time in terms of stationary-weighted KL. Sequential testing under Markovian dependence is the discrete-state counterpart of B1/B2; their stopping-time constants are what B3.1's long-run variance gives for Gaussian AR.

### P42

**Beyond First-order Asymptotics in Sequential Mean Testing**  
VIKAS DEEP, Shubhada Agrawal. *ICML 2026.* [Page](https://openreview.net/forum?id=HMyCBL2yMV) · [PDF](http://arxiv.org/pdf/2606.04520v2)

> We revisit the problem of sequentially testing the mean of bounded distributions in a level-$\alpha$ power-one framework. We study a $\mathrm{KL_{inf}}$-based sequential test that is known to attain the information-theoretic lower bound on the expected stopping time with exact constants as $\alpha \to 0$. Going beyond first-order asymptotics, we establish a central limit theorem (CLT) for the stopping time of this test. Our analysis proceeds in two steps. First, we prove a  novel CLT for the $\mathrm{KL_{inf}}$ statistic itself, characterizing its fluctuations around its deterministic limit. We then leverage this result to show that the stopping time, centered appropriately and scaled by $\sqrt{\log(1/\alpha)}$, converges in distribution to a Gaussian limit with an explicit variance. This yields a second-order characterization of an asymptotically optimal sequential test for bounded distributions. Finally, we present numerical experiments that corroborate our theoretical findings.

**Relevance.** A CLT for the stopping time of the KL_inf-based sequential mean test, giving second-order (variability) guarantees beyond the first-order optimal expected stopping time. For reporting stopping-time distributions of certified elimination, which our report asks for.

### P43

**Learning to Bet for Horizon-Aware Anytime-Valid Testing**  
Ege Onur Taga, Samet Oymak, Shubhanshu Shekhar. *ICML 2026.* [Page](https://openreview.net/forum?id=GiSCgWW0Ze) · [PDF](http://arxiv.org/pdf/2603.19551v2)

> We develop horizon-aware anytime-valid tests and confidence sequences for bounded means under a strict deadline $N$. Using the betting/e-process framework, we cast horizon-aware betting as a finite-horizon optimal control problem with state space $(t, \log W_t)$, where $t$ is the time and $W_t$ is the test martingale value. We first show that in certain interior regions of the state space, policies that deviate significantly from Kelly betting are provably suboptimal, while Kelly betting reaches the threshold with high probability. We then identify sufficient conditions showing that outside this region, more aggressive betting than Kelly can be better if the bettor is behind schedule, and less aggressive can be better if the bettor is ahead. Taken together these results suggest a simple phase diagram in the $(t, \log W_t)$ plane, delineating regions where Kelly, fractional Kelly, and aggressive betting may be preferable.  Guided by this phase diagram, we introduce a Deep Reinforcement Learning approach based on a universal Deep Q-Network (DQN) agent that learns a single policy from synthetic experience and maps simple statistics of past observations to bets across horizons and null values. In limited-horizon experiments, the learned DQN policy yields state-of-the-art results.

**Relevance.** Horizon-aware anytime-valid tests: Kelly betting is optimal in an interior region and more or less aggressive betting elsewhere; a learned DQN betting policy. The practical point that known deadlines allow narrower sequences than fully time-uniform ones applies to our fixed-horizon KuaiRec runs.

### P44

**Prediction-Powered Adaptive Inference with Pretrained AI Models for Contextual Bandits**  
Gabriel Sargent, Will Wei Sun, Zhengwu Zhang, Yufeng Liu. *ICML 2026.* [Page](https://openreview.net/forum?id=epqq9KvxUa) · [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/sargent26a/sargent26a.pdf)

> In adaptive experiments, statistical inference is essential for reliable decision-making and scientific discovery. Often in these settings, collecting labeled data is expensive, but decision-makers have access to large unlabeled datasets and strong pretrained AI models that can generate outcome predictions. Effectively leveraging these predictions in online experiments poses fundamental challenges for statistical inference: AI models may be misspecified, and data collected under adaptive policies are inherently non-i.i.d., invalidating classical inference techniques. To address these challenges, we propose a Prediction-Powered Adaptive Inference (PPAI) estimator that integrates unlabeled data, predicted labels, and adaptively collected labeled data through a single estimating equation. We establish asymptotic normality of the PPAI estimator under mild conditions on the data-collection policy, enabling valid confidence intervals and hypothesis tests for a broad class of Z-functionals. The method incorporates a data-driven tuning mechanism that adaptively weights AI predictions according to their informativeness, guaranteeing that the resulting asymptotic variance is no worse than that of the labeled-only baseline, and is strictly smaller when predictions are informative. Numerical experiments further support the theory, illustrating efficiency gains with informative AI predictions and robust performance when predictions are inaccurate.

**Relevance.** Prediction-powered adaptive inference: combines adaptively collected labels, unlabeled data and pretrained predictions in one estimating equation with asymptotic normality. Auxiliary predictions as extra information under adaptive sampling; adjacent to our use of mined graphs as prior information.

### P45

**On the Tightness and Computational Tractability of Higher-Dimensional Confidence Sequences**  
Fabian Denoodt, Sibylle Hess, Joaquin Vanschoren, Christian A. Naesseth. *NeurIPS 2026 (accepted; arXiv version).* [Page](http://arxiv.org/abs/2610.03727v2) · [PDF](http://arxiv.org/pdf/2610.03727v2)

> Modern sequential monitoring problems often involve multiple metrics, where we monitor several data streams simultaneously and may act once the evidence is strong enough. Confidence sequences (CSs) are a natural tool for such continuous monitoring. However, for bounded vector means, existing multivariate CSs are either tight but computationally intractable, or fast to compute but conservative. To address this, we study three lifts of one-dimensional betting-based CSs to higher dimensions: a weighted Bonferroni region, an equivalent max-wealth form, and a portfolio region. The portfolio is typically much tighter, especially in higher dimensions, but its boundary and properties such as volume are not available in closed form. To make this tighter construction usable, we propose tractable outer approximations of the portfolio region that preserve statistical validity: a bounding box, an $\ell_p$-ellipsoid, and their intersection. We prove set relations among all constructions and show empirically that these approximations (i) achieve regions close to the intractable portfolio, (ii) substantially outperform existing tractable multivariate CSs, and (iii) enable practical use cases such as multi-metric A/B testing and model comparison.

**Relevance (core).** NeurIPS 2026: tractable multivariate confidence sequences for bounded vector means (weighted Bonferroni, max-wealth, portfolio region with outer approximations) for multi-metric A/B testing and model comparison. The tightness/tractability trade-off of multivariate CSs is the same one between B1 (vector, log-det) and B1′ (scalar union).

### P46

**Tighter Confidence Bounds for Sequential Kernel Regression**  
Hamish Flynn, David Reeb. *AISTATS 2025.* [Page](https://openreview.net/forum?id=DDeyFOIG1E) · [PDF](http://arxiv.org/pdf/2403.12732v2)

> Confidence bounds are an essential tool for rigorously quantifying the uncertainty of predictions. They are a core component in many sequential learning and decision-making algorithms, with tighter confidence bounds giving rise to algorithms with better empirical performance and better performance guarantees. In this work, we use martingale tail inequalities to establish new confidence bounds for sequential kernel regression. Our confidence bounds can be computed by solving a conic program, although this bare version quickly becomes impractical, because the number of variables grows with the sample size. However, we show that the dual of this conic program allows us to efficiently compute tight confidence bounds. We prove that our new confidence bounds are always tighter than existing ones in this setting. We apply our confidence bounds to kernel bandit problems, and we find that when our confidence bounds replace existing ones, the KernelUCB (GP-UCB) algorithm has better empirical performance, a matching worst-case performance guarantee and comparable computational cost.

**Relevance (core).** Martingale tail inequalities give confidence bounds for sequential kernel regression, computed through the dual of a conic program; always tighter than existing bounds; better KernelUCB. Companion to [70]; the dual computation is the practical route to per-contrast widths.

### P47

**Time-Uniform Self-Normalized Concentration for Vector-Valued Processes (Extended Abstract)**  
Justin Whitehouse, Zhiwei Steven Wu, Aaditya Ramdas. *COLT 2025.* [Page](https://proceedings.mlr.press/v291/whitehouse25b.html) · [PDF](https://raw.githubusercontent.com/mlresearch/v291/main/assets/whitehouse25b/whitehouse25b.pdf)

> Self-normalized processes arise naturally in many learning-related tasks. While self-normalized concentration has been extensively studied for scalar-valued processes, there are few results for multidimensional processes outside of the sub-Gaussian setting. In this work, we construct a general, self-normalized inequality for multivariate processes that satisfy a simple yet broad “sub-$\psi$” tail condition, which generalizes assumptions based on cumulant generating functions. From this general inequality, we derive an upper law of the iterated logarithm for sub-$\psi$ vector-valued processes, which is tight up to small constants. We show how our inequality can be leveraged to derive a variety of novel, self-normalized concentration inequalities under both light and heavy-tailed observations. Further, we provide applications in prototypical statistical tasks, such as parameter estimation in online linear regression, autoregressive modeling, and bounded mean estimation via a new (multivariate) empirical Bernstein concentration inequality.

**Relevance (core).** Time-uniform self-normalized concentration for vector-valued processes under a sub-ψ condition; rate √(log log γ_max(V_t) + d log κ(V_t)), tighter than the log-det method of mixtures when V_t is well conditioned. Directly addresses why B1's width is √(N log T): a condition-number bound could replace the log-determinant.

### P48

**Optimistic Algorithms for Adaptive Estimation of the Average Treatment Effect**  
Ojash Neopane, Aaditya Ramdas, Aarti Singh. *ICML 2025.* [Page](https://openreview.net/forum?id=1RS4cPFNZ6) · [PDF](http://arxiv.org/pdf/2502.04673v1)

> Estimation and inference for the Average Treatment Effect (ATE) is a cornerstone of causal inference and often serves as the foundation for developing procedures for more complicated settings. Although traditionally analyzed in a batch setting, recent advances in martingale theory have paved the way for adaptive methods that can enhance the power of downstream inference. Despite these advances, progress in understanding and developing adaptive algorithms remains in its early stages. Existing work either focus on asymptotic analyses that overlook exploration-exploitation trade-offs relevant in finite-sample regimes or rely on simpler but suboptimal estimators. In this work, we address these limitations by studying adaptive sampling procedures that take advantage of the asymptotically optimal Augmented Inverse Probability Weighting (AIPW) estimator. Our analysis uncovers challenges obscured by asymptotic approaches and introduces a novel algorithmic design principle reminiscent of optimism in multi-armed bandits. This principled approach enables our algorithm to achieve significant theoretical and empirical gains compared to previous methods. Our findings mark a step forward in the advancement of adaptive causal inference methods in theory and practice.

**Relevance.** Optimistic adaptive sampling (OPTrack) for ATE estimation with the AIPW estimator; finite-sample analysis; oversample arms that will later be under-sampled. Adaptive experimental design for inference rather than regret; the optimism principle transfers to information-directed certification.

### P49

**Bernstein–von Mises for Adaptively Collected Data**  
Kevin Du, Yash Nair, Lucas Janson. *NeurIPS 2025.* [Page](https://openreview.net/forum?id=arw2uk9Ica) · [PDF](http://arxiv.org/pdf/2511.06639v1)

> Uncertainty quantification (UQ) for adaptively collected data, such as that coming from adaptive experiments, bandits, or reinforcement learning, is necessary for critical elements of data collection such as ensuring safety and conducting after-study inference. The data's adaptivity creates significant challenges for frequentist UQ, yet Bayesian UQ remains the same as if the data were independent and identically distributed (i.i.d.), making it an appealing and commonly used approach. Bayesian UQ requires the (correct) specification of a prior distribution while frequentist UQ does not, but for i.i.d. data the celebrated Bernstein–von Mises theorem shows that as the sample size grows, the prior `washes out' and Bayesian UQ becomes frequentist-valid, implying that the choice of prior need not be a major impediment to Bayesian UQ as it makes no difference asymptotically. This paper for the first time extends the Bernstein–von Mises theorem to adaptively collected data, proving asymptotic equivalence between Bayesian UQ and Wald-type frequentist UQ in this challenging setting. Our results do not require the standard stability condition for validity of Wald-type frequentist UQ, and thus provide positive results on frequentist validity of Bayesian UQ under stability. Counterintuitively however, they also provide a negative result that Bayesian UQ is not asymptotically frequentist valid when stability fails, despite the fact that the prior washes out and Bayesian UQ asymptotically matches standard Wald-type frequentist UQ. We empirically validate our theory (positive and negative) via a range of simulations.

**Relevance (core).** Bernstein–von Mises for adaptively collected data: Bayesian uncertainty asymptotically matches Wald-type frequentist UQ under stability, and is not frequentist-valid when stability fails. Explains why the Bayesian (Thompson/Gaussian) baselines in our experiments give calibrated-looking intervals in some regimes and not others.

### P50

**STAR-Bets: Sequential TArget-Recalculating Bets for Tighter Confidence Intervals**  
Vaclav Voracek, Francesco Orabona. *NeurIPS 2025.* [Page](https://openreview.net/forum?id=LHsQSC89Pt) · [PDF](http://arxiv.org/pdf/2505.22422v2)

> The construction of confidence intervals for the mean of a bounded random variable is a classical problem in statistics with numerous applications in machine learning and virtually all scientific fields. In particular, obtaining the tightest possible confidence intervals is vital every time the sampling of the random variables is expensive. The current state-of-the-art method to construct confidence intervals is by using betting algorithms. This is a very successful approach for deriving optimal confidence sequences, even matching the rate of law of iterated logarithms. However, in the fixed horizon setting, these approaches are either sub-optimal or based on heuristic solutions with strong empirical performance but without a finite-time guarantee. Hence, no betting-based algorithm guaranteeing the optimal $\mathcal{O}(\sqrt{\frac{\sigma^2\log\frac1\delta}{n}})$ width of the confidence intervals are known. This work bridges this gap. We propose a betting-based algorithm to compute confidence intervals that empirically outperforms the competitors. Our betting strategy uses the optimal strategy in every step (in a certain sense), whereas the standard betting methods choose a constant strategy in advance. Leveraging this fact results in strict improvements even for classical concentration inequalities, such as the ones of Hoeffding or Bernstein. Moreover, we also prove that the width of our confidence intervals is optimal up to an $1+o(1)$ factor diminishing with $n$.

**Relevance.** Betting-based confidence intervals for bounded means that recalculate the target at each step; optimal width up to 1+o(1) in the fixed-horizon regime. Fixed-n (not time-uniform) betting; relevant to narrowing certificates when a horizon is known.

### P51

**Simulation-Based Inference for Adaptive Experiments**  
Brian M Cho, Aurelien Bibaut, Nathan Kallus. *NeurIPS 2025.* [Page](https://openreview.net/forum?id=lGUzCAdYoq) · [PDF](http://arxiv.org/pdf/2506.02881v1)

> Multi-arm bandit experimental designs are increasingly being adopted over standard randomized trials due to their potential to improve outcomes for study participants, enable faster identification of the best-performing options, and/or enhance the precision of estimating key parameters. Current approaches for inference after adaptive sampling either rely on asymptotic normality under restricted experiment designs or underpowered martingale concentration inequalities that lead to weak power in practice. To bypass these limitations, we propose a simulation-based approach for conducting hypothesis tests and constructing confidence intervals for arm specific means and their differences. Our simulation-based approach uses positively biased nuisances to generate additional trajectories of the experiment, which we call \textit{simulation with optimism}. Using these simulations, we characterize the distribution potentially non-normal sample mean test statistic to conduct inference. We provide guarantees for (i) asymptotic type I error control, (ii) convergence of our confidence intervals, and (iii) asymptotic strong consistency of our estimator over a wide variety of common bandit designs. Our empirical results show that our approach achieves the desired coverage while reducing confidence interval widths by up to 50\%, with drastic improvements for arms not targeted by the design.

**Relevance.** Simulation-based inference for adaptive experiments (simulation with optimism) gives asymptotic type-I control and 50% narrower intervals than martingale concentration. Asymptotic, design-specific inference as the alternative to anytime-valid certificates; the width gap it reports is the gap our report measures (10–25×).

### P52

**An information-theoretic lower bound in time-uniform estimation**  
John Duchi, Saminul Haque. *COLT 2024.* [Page](https://proceedings.mlr.press/v247/duchi24a.html) · [PDF](https://proceedings.mlr.press/v247/duchi24a/duchi24a.pdf)

> We present an information-theoretic lower bound for the problem of parameter estimation with time-uniform coverage guarantees. We use a reduction to sequential testing to obtain stronger lower bounds that capture the hardness of the time-uniform setting. In the case of location model estimation and logistic regression, our lower bound is $\Omega(\sqrt{n^{-1}\log \log n})$, which is tight up to constant factors in typical settings.

**Relevance.** Information-theoretic proof that time-uniform estimation must pay a √(log log n) factor over fixed-n confidence. Sets the floor for any anytime-valid certificate: B1 cannot do better than LIL rates, but is currently far above them.

### P53

**Gambling-Based Confidence Sequences for Bounded Random Vectors**  
Jongha Jon Ryu, Gregory W. Wornell. *ICML 2024.* [Page](https://openreview.net/forum?id=mu7Er7f9NQ) · [PDF](http://arxiv.org/pdf/2402.03683v2)

> A confidence sequence (CS) is a sequence of confidence sets that contains a target parameter of an underlying stochastic process at any time step with high probability. This paper proposes a new approach to constructing CSs for means of bounded multivariate stochastic processes using a general gambling framework, extending the recently established coin toss framework for bounded random processes. The proposed gambling framework provides a general recipe for constructing CSs for categorical and probability-vector-valued observations, as well as for general bounded multidimensional observations through a simple reduction. This paper specifically explores the use of the mixture portfolio, akin to Cover's universal portfolio, in the proposed framework and investigates the properties of the resulting CSs. Simulations demonstrate the tightness of these confidence sequences compared to existing methods. When applied to the sampling without-replacement setting for finite categorical data, it is shown that the resulting CS based on a universal gambling strategy is provably tighter than that of the posterior-prior ratio martingale proposed by Waudby-Smith and Ramdas.

**Relevance.** Gambling-based confidence sequences for bounded random vectors via universal portfolios; tighter than existing vector CSs. Betting CSs for several arms at once, an alternative to our union bound over N+M scalar processes in B1′.

### P54

**Peeking with PEAK: Sequential, Nonparametric Composite Hypothesis Tests for Means of Multiple Data Streams**  
Brian M Cho, Kyra Gan, Nathan Kallus. *ICML 2024.* [Page](https://openreview.net/forum?id=hcASxFvmZ5) · [PDF](http://arxiv.org/pdf/2402.06122v3)

> We propose a novel nonparametric sequential test for composite hypotheses for means of multiple data streams. Our proposed method, peeking with expectation-based averaged capital (PEAK), builds upon the testing-by-betting framework and provides a non-asymptotic $\alpha$-level test across any stopping time. Our contributions are two-fold: (1) we propose a novel betting scheme and provide theoretical guarantees on type-I error control, power, and asymptotic growth rate/$e$-power in the setting of a single data stream; (2) we introduce PEAK, a generalization of this betting scheme to multiple streams, that (i) avoids using wasteful union bounds via averaging, (ii) is a test of power one under mild regularity conditions on the sampling scheme of the streams, and (iii) reduces computational overhead when applying the testing-as-betting approaches for pure-exploration bandit problems. We illustrate the practical benefits of PEAK using both synthetic and real-world HeartSteps datasets. Our experiments show that PEAK provides up to an 85% reduction in the number of samples before stopping compared to existing stopping rules for pure-exploration bandit problems, and matches the performance of state-of-the-art sequential tests while improving upon computational complexity.

**Relevance (core).** PEAK: non-asymptotic sequential tests for composite hypotheses on means of multiple adaptively sampled streams by betting, avoiding union bounds through averaged capital; up to 85% fewer samples before stopping in pure-exploration bandits; HeartSteps data. A direct alternative to our union-bounded B1′ for component rejection, under iid streams.

### P55

**A Unified Confidence Sequence for Generalized Linear Models, with Applications to Bandits**  
Junghyun Lee, Se-Young Yun, Kwang-Sung Jun. *NeurIPS 2024.* [Page](https://openreview.net/forum?id=MDdOQayWTA) · [PDF](http://arxiv.org/pdf/2407.13977v3)

> We present a unified likelihood ratio-based confidence sequence (CS) for *any* (self-concordant) generalized linear model (GLM) that is guaranteed to be convex and numerically tight. We show that this is on par or improves upon known CSs for various GLMs, including Gaussian, Bernoulli, and Poisson. In particular, for the first time, our CS for Bernoulli has a $\mathrm{poly}(S)$-free radius where $S$ is the norm of the unknown parameter. Our first technical novelty is its derivation, which utilizes a time-uniform PAC-Bayesian bound with a uniform prior/posterior, despite the latter being a rather unpopular choice for deriving CSs. As a direct application of our new CS, we propose a simple and natural optimistic algorithm called **OFUGLB**, applicable to *any* generalized linear bandits (**GLB**; Filippi et al. (2010)). Our analysis shows that the celebrated optimistic approach simultaneously attains state-of-the-art regrets for various self-concordant (not necessarily bounded) **GLB**s, and even $\mathrm{poly}(S)$-free for bounded **GLB**s, including logistic bandits. The regret analysis, our second technical novelty, follows from combining our new CS with a new proof technique that completely avoids the previously widely used self-concordant control lemma (Faury et al., 2020, Lemma 9). Numerically, **OFUGLB** outperforms or is at par with prior algorithms for logistic bandits.

**Relevance (core).** A unified likelihood-ratio confidence sequence for self-concordant GLMs, convex and numerically tight, with poly(S)-free radius for Bernoulli; OFUGLB. Relevant to the KL-UCB-style certificates in Setting A v2 and to a Bernoulli version of B1.

### P56

**Off-policy estimation with adaptively collected data: the power of online learning**  
Jeonghwan Lee, Cong Ma. *NeurIPS 2024.* [Page](https://openreview.net/forum?id=8qEkjSEdls) · [PDF](http://arxiv.org/pdf/2411.12786v1)

> We consider estimation of a linear functional of the treatment effect from adaptively collected data. This problem finds a variety of applications including off-policy evaluation in contextual bandits, and estimation of the average treatment effect in causal inference. While a certain class of augmented inverse propensity weighting (AIPW) estimators enjoys desirable asymptotic properties including the semi-parametric efficiency, much less is known about their non-asymptotic theory with adaptively collected data. To fill in the gap, we first present generic upper bounds on the mean-squared error of the class of AIPW estimators that crucially depends on a sequentially weighted error between the treatment effect and its estimates. Motivated by this, we propose a general reduction scheme that allows one to produce a sequence of estimates for the treatment effect via online learning to minimize the sequentially weighted estimation error. To illustrate this, we provide three concrete instantiations in (1) the tabular case; (2) the case of linear function approximation; and (3) the case of general function approximation for the outcome model. We then provide a local minimax lower bound to show the instance-dependent optimality of the AIPW estimator using no-regret online learning algorithms.

**Relevance.** Non-asymptotic MSE bounds for AIPW estimators from adaptively collected data, with the sequentially weighted estimation error minimized by online learning. Inference from adaptively collected data for off-policy value; complements our confidence-for-fixed-means question.

### P57

**Improved Algorithms for Stochastic Linear Bandits Using Tail Bounds for Martingale Mixtures**  
Hamish Flynn, David Reeb, Melih Kandemir, Jan Peters. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=TXoZiUZywf) · [PDF](http://arxiv.org/pdf/2309.14298v2)

> We present improved algorithms with worst-case regret guarantees for the stochastic linear bandit problem. The widely used "optimism in the face of uncertainty" principle reduces a stochastic bandit problem to the construction of a confidence sequence for the unknown reward function. The performance of the resulting bandit algorithm depends on the size of the confidence sequence, with smaller confidence sets yielding better empirical performance and stronger regret guarantees. In this work, we use a novel tail bound for adaptive martingale mixtures to construct confidence sequences which are suitable for stochastic bandits. These confidence sequences allow for efficient action selection via convex programming. We prove that a linear bandit algorithm based on our confidence sequences is guaranteed to achieve competitive worst-case regret. We show that our confidence sequences are tighter than competitors, both empirically and theoretically. Finally, we demonstrate that our tighter confidence sequences give improved performance in several hyperparameter tuning tasks.

**Relevance (core).** Tail bounds for adaptive martingale mixtures give confidence sequences for linear bandits that are tighter than OFUL's, computable by convex programming, with competitive worst-case regret. Tighter mixtures over the same self-normalized martingale we use in S2; a candidate for shrinking B1's log-determinant width (our top open problem).

### P58

**Likelihood Ratio Confidence Sets for Sequential Decision Making**  
Nicolas Emmenegger, Mojmir Mutny, Andreas Krause. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=4anryczeED) · [PDF](http://arxiv.org/pdf/2311.04402v1)

> Certifiable, adaptive uncertainty estimates for unknown quantities are an essential ingredient of sequential decision-making algorithms. Standard approaches rely on problem-dependent concentration results and are limited to a specific combination of parameterization, noise family, and estimator. In this paper, we revisit the likelihood-based inference principle and propose to use \emph{likelihood ratios} to construct \emph{any-time valid} confidence sequences without requiring specialized treatment in each application scenario. Our method is especially suitable for problems with well-specified likelihoods, and the resulting sets always maintain the prescribed coverage in a model-agnostic manner. The size of the sets depends on a choice of estimator sequence in the likelihood ratio. We discuss how to provably choose the best sequence of estimators and shed light on connections to online convex optimization with algorithms such as Follow-the-Regularized-Leader. To counteract the initially large bias of the estimators, we propose a reweighting scheme that also opens up deployment in non-parametric settings such as RKHS function classes. We provide a \emph{non-asymptotic} analysis of the likelihood ratio confidence sets size for generalized linear models, using insights from convex duality and online learning. We showcase the practical strength of our method on generalized linear bandit problems, survival analysis, and bandits with various additive noise distributions.

**Relevance (core).** Likelihood-ratio confidence sequences, any-time valid for well-specified likelihoods, with estimator sequences chosen by online learning and reweighting; non-asymptotic size for GLMs. Our innovation regression has an exact Gaussian likelihood, so these sets apply directly and may be narrower than the mixture bound.

### P59

**Time-uniform confidence bands for the CDF under nonstationarity**  
Paul Mineiro, Steven R Howard. *NeurIPS 2023.* [Page](https://openreview.net/forum?id=39cFjnRpYm) · [PDF](http://arxiv.org/pdf/2302.14248v1)

> Estimation of a complete univariate distribution from a sequence of observations is a useful primitive for both manual and automated decision making. This problem has received extensive attention in the i.i.d. setting, but the arbitrary data dependent setting remains largely unaddressed. We present computationally felicitous time-uniform and value-uniform bounds on the CDF of the running averaged conditional distribution of a sequence of real-valued random variables. Consistent with known impossibility results, our CDF bounds are always valid but sometimes trivial when the instance is too hard, and we give an instance-dependent convergence guarantee.  The importance-weighted extension is appropriate for estimating complete counterfactual distributions of rewards given data from a randomized experiment, e.g., from an A/B test or a contextual bandit.

**Relevance.** Time-uniform, value-uniform CDF bounds for the running averaged conditional distribution of a dependent sequence; always valid, sometimes trivial; counterfactual version for A/B tests and bandits. Anytime-valid inference under arbitrary dependence at the cost of width, the same 'valid but vacuous' trade-off our report names.


## Theme D. Online experiments, A/B testing, and limited adaptivity (bursty exposure; B2, B3)

### P60

**Adaptive A/B Testing under Nonstationary Dynamics using State-Space Models**  
Junzhe Shao, Waverly Wei, Jingshen Wang. *AISTATS 2026.* [Page](https://openreview.net/forum?id=gjIn18VuA7) · [PDF](https://raw.githubusercontent.com/mlresearch/v300/main/assets/shao26a/shao26a.pdf)

> A/B testing is central to evaluating how modifications to products, services, and user experiences impact user outcomes. Yet in practice, experiments rarely occur in stationary environments: seasonality, feature launches, and dynamically evolved user demographics make the underlying treatment effects shift over time. Conventional fixed-allocation designs fail to adapt to this nonstationarity, relying on static treatment allocations that potentially compromise estimation efficiency and lead to inefficient use of experimental resources. Response-adaptive randomization (RAR) design provides a natural alternative, adaptively allocating participants over time based on accrued information. In this work, we propose a methodology framework that addresses these challenges. On the one hand, we model period-level treatment arm means as autoregressive state-space processes and develop a Kalman smoother estimator for the time-averaged treatment effect that exploits temporal dependence. On the other hand, we propose an RAR design that accommodates nonstationarity by incorporating state uncertainty via predicted Kalman variances. Our theoretical analysis establishes asymptotic normality of both a naive and a smoother-based estimator, proves that the smoother strictly dominates the naive estimator in asymptotic variance under correct specification, compares relative efficiency, and enables the construction of anytime-valid confidence sequences for continuous monitoring. Simulation studies demonstrate that our method is significantly more efficient than a benchmark time-averaging estimator and fixed allocation strategy, particularly under treatment effect drift and variance imbalance.

**Relevance (core).** Period-level treatment-arm means modelled as autoregressive state-space processes; a Kalman-smoother estimator of the time-averaged effect, response-adaptive allocation using predicted Kalman variances, asymptotic normality, dominance over the naive estimator, and anytime-valid confidence sequences. The nearest neighbour to our experiment proposal 1 and to B1 on daily aggregates; it treats one two-arm test with a known AR(1) and does not study the failure of iid sequences (B2) or pooling across tests.

### P61

**Adaptive Combinatorial Experimental Design: Pareto Optimality for Decision-Making and Inference**  
Xie Hongrui, Junyu Cao, Kan Xu. *AISTATS 2026.* [Page](https://openreview.net/forum?id=FLiPfTIzuD) · [PDF](http://arxiv.org/pdf/2602.24231v1)

> In this paper, we provide the first investigation into adaptive combinatorial experimental design, focusing on the trade-off between regret minimization and statistical power in combinatorial multi-armed bandits (CMAB). While minimizing regret requires repeated exploitation of high-reward arms, accurate inference on reward gaps requires sufficient exploration of suboptimal actions. We formalize this trade-off through the concept of Pareto optimality and establish equivalent conditions for Pareto-efficient learning in CMAB. We consider two relevant cases under different information structures, i.e., full-bandit feedback and semi-bandit feedback, and propose two algorithms MixCombKL and MixCombUCB respectively for these two cases. We provide theoretical guarantees showing that both algorithms are Pareto optimal, achieving finite-time guarantees on both regret and estimation error of arm gaps. Our results further reveal that richer feedback significantly tightens the attainable Pareto frontier, with the primary gains arising from improved estimation accuracy under our proposed methods. Taken together, these findings establish a principled framework for adaptive combinatorial experimentation in multi-objective decision-making.

**Relevance.** Pareto-optimal trade-off between regret and estimation error of reward gaps in combinatorial bandits under full-bandit and semi-bandit feedback. The regret-versus-inference frontier that certified pooling sits on (correct decisions at a regret cost).

### P62

**Contextual Slate GLM Bandits with Limited Adaptivity**  
Tanmay Goyal, Sukruta Prakash Midigeshi, Gaurav Sinha. *ICML 2026.* [Page](https://openreview.net/forum?id=4yLiQ3vcC9) · [PDF](http://arxiv.org/pdf/2606.31449v2)

> We investigate the contextual slate bandit problem with generalized linear rewards under limited adaptivity. At each round, the learner is presented with $N$ sets of items, where each item is represented by a $d$-dimensional feature vector. The learner then constructs a slate by selecting one item per set; the resulting slate yields a scalar reward sampled from a Generalized Linear Model (GLM). We propose algorithms under two limited-adaptivity settings: (a) Batched and (b) Rarely-Switching. For the batched setting, we introduce B-SlateGLinCB, which partitions the time horizon into $\mathcal{O}(\log\log T)$ batches such that each batch's policy relies only on data from previous batches. For the rarely-switching setting, we propose RS-SlateGLinCB, which adaptively performs only $\mathcal{O}(Nd\log T)$ parameter updates. Under a diversity assumption on the item sequences, we prove that B-SlateGLinCB and RS-SlateGLinCB achieve regret bounds of $\mathcal{O}(Nd^{3/2}\sqrt{T})$ and $\mathcal{O}(Nd\sqrt{T})$, respectively. Notably, both bounds are independent of the non-linearity parameter $\kappa$ that is typically found to scale the regret of GLM bandit algorithms. Our algorithms are computationally efficient, requiring only $\text{poly}(N)$ time per round despite $2^{\Omega(N)}$ possible slates. Simulations show our algorithms outperform existing baselines with limited adaptivity and remain competitive with Slate-GLM-OFU, a fully adaptive state-of-the-art algorithm. Notably, a slightly modified B-SlateGLinCB empirically matches this baseline. Finally, we demonstrate strong performance in a practical in-context example selection task for language models.

**Relevance.** Contextual slate bandits with GLM rewards under batched and rarely-switching limited adaptivity; O(log log T) batches; κ-free regret. Slates with limited adaptivity, our bursty-exposure regime, again with independent rewards.

### P63

**Design-Based Anytime-Valid Inference for Randomized Experiments with Delayed Outcomes and Staggered Entry**  
Michael Lindon, Nathan Kallus. *ICML 2026.* [Page](https://openreview.net/forum?id=FXWnvznHMW) · [PDF](http://arxiv.org/pdf/2603.25971v2)

> Delayed outcomes are ubiquitous in online experimentation: treatment can affect whether an outcome occurs, when it occurs, and its realized value. To accommodate staggered entry while remaining robust to environmental nonstationarity and unit-level heterogeneity, we adopt a design-based perspective and target the sample cumulative reward in each arm as a function of calendar time. Our confidence sequences allow practitioners to continuously monitor the counterfactual incremental reward, such as revenue, that would have been realized by calendar time $t$ had all entered units been assigned to treatment rather than control. The main technical challenge is the choice of design-based filtration, complicated by the presence of asynchronous potential outcome times. We show that the IPW treatment-effect estimation error is not a martingale with respect to any filtration, while each arm-specific IPW estimation error is a martingale with respect to a carefully chosen arm-specific event-time filtration. We therefore construct a confidence sequence for the treatment effect by combining two arm-level confidence sequences with a union bound, and further demonstrate that this can outperform the traditional design-based variance upper bound. Finally, we characterize the class of augmentations for which the per-arm AIPW estimation error remains a martingale.

**Relevance (core).** Design-based anytime-valid inference with delayed outcomes and staggered entry: the IPW treatment-effect error is not a martingale under any filtration, but per-arm errors are, so a union of per-arm confidence sequences is used. The same per-arm-then-union construction as our B1′, arrived at for a different reason; their estimand is design-based and robust to nonstationarity.

### P64

**Robust Sequential Experimental Design for A/B Testing**  
Qianglin Wen, Xiangkun Wu, Chengchun Shi, Ting Li, Niansheng Tang, Yingying Zhang, Hongtu Zhu. *ICML 2026.* [Page](https://openreview.net/forum?id=Q7lEZjtDKO) · [PDF](http://arxiv.org/pdf/2605.12899v1)

> Experimental design has emerged as a powerful approach for improving the sample efficiency of A/B testing, yet existing designs rely critically on correctly specified models. We study robust sequential experimental design under model misspecification and develop a unified framework that covers both contextual bandit and dynamic settings. Theoretically, we prove that our design bounds the worst-case mean squared error of the estimated treatment effect. Empirically, we demonstrate the effectiveness of the proposed approach using synthetic and real-world datasets from a leading technology company.

**Relevance (core).** Robust sequential experimental design for A/B tests under model misspecification, covering contextual-bandit and dynamic settings with carryover effects; bounds worst-case MSE; real data from a technology company. Carryover between periods is the mechanism behind our bursty-exposure inflation; they design allocations, we certify confidence.

### P65

**Anytime-Valid A/B Testing of Counting Processes**  
Michael Lindon, Nathan Kallus. *AISTATS 2025.* [Page](https://openreview.net/forum?id=56aJtyPC4X) · [PDF](https://raw.githubusercontent.com/mlresearch/v258/main/assets/lindon25a/lindon25a.pdf)

> Motivated by monitoring the arrival of incoming adverse events such as customer support calls or crash events from users exposed to an experimental product change, we consider sequential hypothesis testing of continuous-time counting processes. Specifically, we provide a multivariate confidence process on the cumulative rates $(\Lambda^A_t, \Lambda^B_t)$ giving an anytime-valid coverage guarantee $\mathbb{P}[(\Lambda^A_t, \Lambda^B_t) \in C^\alpha_t \, \forall t >0] \geq 1-\alpha$. This provides simultaneous confidence process on $\Lambda^A_t$, $\Lambda^B_t$ and their difference $\Lambda^B_t-\Lambda^A_t$, allowing each arm of the experiment and the difference between them to be safely monitored throughout the experiment. We extend our results by constructing a closed-form $e$-process for testing the equality of rates with a time-uniform Type-I error guarantee at a nominal $\alpha$. We characterize the asymptotic growth rate of the proposed $e$-process under the alternative and show that it has power 1 when the average rates of the two process differ in the limit.

**Relevance.** Anytime-valid confidence processes for cumulative rates of two counting processes and an e-process for equality of rates, for monitoring adverse events in experiments. Continuous-time sequential monitoring in A/B tests; iid increments.

### P66

**Almost Optimal Batch-Regret Tradeoff for Batch Linear Contextual Bandits**  
Zihan Zhang, Xiangyang Ji, Yuan Zhou. *ICLR 2025.* [Page](https://openreview.net/forum?id=rakhNY32vw) · [PDF](http://arxiv.org/pdf/2110.08057v3)

> We study the optimal batch-regret tradeoff for batch linear contextual bandits. For this problem, we design batch learning algorithms and prove that they achieve the optimal regret bounds (up to logarithmic factors) for any batch number $M$, number of actions $K$, time horizon $T$, and dimension $d$. Therefore, we establish the \emph{full-parameter-range} (almost) optimal batch-regret tradeoff for the batch linear contextual bandit problem. Along our analysis, we also prove a new matrix concentration inequality with dependence on their dynamic upper bounds, which, to the best of our knowledge, is the first of its kind in literature and maybe of independent interest.

**Relevance.** Optimal batch-regret trade-off for batch linear contextual bandits for all parameter ranges, with a new matrix concentration inequality under dynamic upper bounds. Batched (bursty) exposure as a constraint; iid noise within batches.

### P67

**Breaking the $\log(1/\Delta_2)$ Barrier: Better Batched Best Arm Identification with Adaptive Grids**  
Tianyuan Jin, Qin Zhang, Dongruo Zhou. *ICLR 2025.* [Page](https://openreview.net/forum?id=buxFBI6GG4) · [PDF](https://openreview.net/pdf/e35c89789cbaf91ae27c67f7fc8e8587eece6875.pdf)

> We investigate the problem of batched best arm identification in multi-armed bandits, where we want to find the best arm from a set of $n$ arms while minimizing both the number of samples and batches. We introduce an algorithm that achieves near-optimal sample complexity and features an instance-sensitive batch complexity, which breaks the $\log(1/\Delta_2)$ barrier. The main contribution of our algorithm is a novel sample allocation scheme that effectively balances exploration and exploitation for batch sizes. Experimental results indicate that our approach is more batch-efficient across various setups. We also extend this framework to the problem of batched best arm identification in linear bandits and achieve similar improvements.

**Relevance.** Batched best-arm identification with instance-sensitive batch complexity below log(1/Δ_2), on synthetic and MovieLens data. Batched identification under iid rewards; B2 says consecutive batches of persistent rewards break the iid confidence these methods use.

### P68

**A/B Test and Online Experiment Under Diminishing Marginal Effects: Regret Minimization and Statistical Inference**  
(authors on the linked page). *KDD 2025.* [Page](https://doi.org/10.1145/3711896.3736826) · [PDF](https://dl.acm.org/doi/pdf/10.1145/3711896.3736826)  
*Abstract only: the PDF was not reachable from this machine, so the introduction was not read.*

> When large online platforms test new strategies with their user traffic, the phenomenon of diminishing marginal effects often arise. For example, when a strategy is implemented on 60% of the user traffic, the expected per user effect can be lower compared to that when a strategy is implemented on 30% of the user traffic, potentially due to limits of overall budget, resource, attention or content involved with a strategy. In presence of this phenomenon, we aim to deliver two critical tasks for online sequential experiments: (1) Adaptively identify the optimal traffic allocation to maximize the expected cumulative reward and (2) Construct valid central limit theorem to perform valid statistical inference for the expected reward under the optimal traffic allocation that is a priori unknown. We show that standard algorithms that achieve near-optimal performance can fail to deliver the second task, as the statistical inference task presents its own difficulty. We develop a novel online algorithm that leverages an additional smoothness condition on how the marginal effects change. We prove that the algorithm obtains the best achievable expected cumulative reward. Further, crucially for online platforms' need to do trustworthy statistical inference, the algorithm is proved to enjoy a valid central limit theorem. The theoretical findings are illustrated through numerical experiments.

**Relevance.** KDD 2025: online experiments with diminishing marginal effects of traffic allocation; an algorithm that attains optimal cumulative reward and a valid CLT for inference at the unknown optimal allocation. Regret-and-inference trade-off in platform experiments; iid across users. (Abstract only.)

### P69

**YEAST: Yet Another Sequential Test**  
Alexey Kurennoy, Majed Dodin, Tural Gurbanov, Ana Peleteiro Ramallo. *NeurIPS 2025.* [Page](https://openreview.net/forum?id=aq3tgx5wcu) · [PDF](http://arxiv.org/pdf/2406.16523v5)

> The online evaluation of machine learning models is typically conducted through A/B experiments. Sequential statistical tests are valuable tools for analysing these experiments, as they enable researchers to stop data collection early without increasing the risk of false discoveries. However, existing sequential tests either limit the number of interim analyses or suffer from low statistical power. In this paper, we introduce a novel sequential test designed for the continuous monitoring of A/B experiments. We validate our method using semi-synthetic simulations and demonstrate that it outperforms current state-of-the-art sequential testing approaches. Our method is derived using a new technique that inverts a bound on the probability of threshold crossing, based on a classical maximal inequality.

**Relevance (core).** YEAST: a continuous sequential test for A/B experiments derived by inverting a maximal-inequality bound; better type-I control and power than existing continuous monitoring methods; semi-synthetic validation on a public dataset. A representative iid sequential test that experiment proposal 1 would run on autocorrelated daily metrics.

### P70

**On Universally Optimal Algorithms for A/B Testing**  
Po-An Wang, Kaito Ariu, Alexandre Proutiere. *ICML 2024.* [Page](https://openreview.net/forum?id=ft5jK9uPgC) · [PDF](http://arxiv.org/pdf/2308.12000v4)

> We study the problem of best-arm identification with fixed budget in stochastic multi-armed bandits with Bernoulli rewards. For the problem with two arms, also known as the A/B testing problem, we prove that there is no algorithm that (i) performs as well as the algorithm sampling each arm equally (referred to as the *uniform sampling* algorithm) in all instances, and that (ii) strictly outperforms uniform sampling on at least one instance. In short, there is no algorithm better than the uniform sampling algorithm. To establish this result, we first introduce the natural class of *consistent* and *stable* algorithms, and show that any algorithm that performs as well as the uniform sampling algorithm in all instances belongs to this class. The proof then proceeds by deriving a lower bound on the error rate satisfied by any consistent and stable algorithm, and by showing that the uniform sampling algorithm matches this lower bound. Our results provide a solution to the two open problems presented in (Qin, 2022). For the general problem with more than two arms, we provide a first set of results. We characterize the asymptotic error rate of the celebrated Successive Rejects (SR) algorithm (Audibert et al., 2010) and show that, surprisingly, the uniform sampling algorithm outperforms the SR algorithm in some instances.

**Relevance.** For fixed-budget A/B testing (two Bernoulli arms) no algorithm beats uniform sampling on all instances; for more arms, uniform sampling sometimes beats Successive Rejects. A caution for adaptive allocation in two-arm tests; our proposal 1 uses fixed allocation with sequential stopping.

### P71

**False Positives in A/B Tests**  
(authors on the linked page). *KDD 2024.* [Page](https://doi.org/10.1145/3637528.3671631) · [PDF](https://dl.acm.org/doi/pdf/10.1145/3637528.3671631)  
*Abstract only: the PDF was not reachable from this machine, so the introduction was not read.*

> A/B tests, or online controlled experiments, are used heavily in the software industry to evaluate implementations of ideas, as the paradigm is the gold standard in science for establishing causality: the changes introduced in the treatment caused the changes to the metrics of interest with high probability.What distinguishes software experiments, or A/B tests, from experiments in many other domains is the scale (e.g., over 100 experiment treatments may launch on a given workday in large companies) and the effect sizes that matter to the business are small (e.g., a 3% improvement to conversion rate from a single experiment is a cause for celebration).The humbling reality is that most experiments fail to improve key metrics, and success rates of only about 10-20% are most common.With low success rates, the industry standard alpha threshold of 0.05 implies a high probability of false positives.We begin with motivation about why false positives are expensive in many software domains.We then offer several approaches to estimate the true success rate of experiments, given the observed "win" rate (statistically significant positive improvements), and show examples from Expedia and Optimizely.We offer a modified procedure for experimentation, based in sequential group testing, that selectively extends experiments to reduce false positives, increase power, at a small increase to runtime.We conclude with a discussion of the difference between ideas and experiments in practice, terms that are often incorrectly used interchangeably. CCS CONCEPTS General and Reference →

**Relevance (core).** KDD 2024: with 10–20% true success rates, α = 0.05 implies many false positive A/B wins; estimates true success rates from observed win rates at Expedia and Optimizely; proposes sequential group testing that extends experiments selectively. KDD's own evidence that false positives in experimentation matter, which B2 adds a mechanism to. (Abstract only.)


## Theme E. Dependence across units: network interference (spatial correlation of rewards)

### P72

**Scalable Policy Maximization Under Network Interference**  
Aidan Gleich, Eric Laber, Alexander Volfovsky. *AISTATS 2026.* [Page](https://openreview.net/forum?id=x6pYSOVcNC) · [PDF](http://arxiv.org/pdf/2505.18118v2)

> Many interventions, such as vaccines in clinical trials or coupons in online marketplaces, must be assigned sequentially without full knowledge of their effects. Multi-armed bandit algorithms have proven successful in such settings. However, standard independence assumptions fail when the treatment status of one individual impacts the outcomes of others, a phenomenon known as interference. We study optimal-policy learning under interference on large networks. Existing approaches to this problem require repeated observations of the same fixed network and struggle to scale in sample size beyond as few as fifteen connected units --- both limit applications. We show that common assumptions on the structure of interference enable a parsimonious linear parameterization of the reward function. We develop a scalable Thompson sampling algorithm that maximizes cumulative rewards on a $n$-node network while allowing for both nodes and edges to be sampled at each time period. We prove upper and lower bounds on Bayesian regret that imply near-optimality.  Simulation experiments show that our algorithm learns quickly and outperforms existing methods. The results close a key scalability gap between causal inference methods for interference and practical bandit algorithms, enabling policy optimization in large-scale networked systems.

**Relevance.** Scalable Thompson sampling for policy learning on large networks with interference, with nodes and edges sampled each period and Bayesian regret bounds. Addresses the fixed-network, temporally independent assumptions of earlier interference bandits, the same two assumptions our model relaxes.

### P73

**Learning Peer Influence Probabilities with Linear Contextual Bandits**  
Ahmed Sayeed Faruk, Mohammad Shahverdikondori, Elena Zheleva. *KDD 2026.* [Page](https://doi.org/10.1145/3770855.3817733) · [PDF](http://arxiv.org/pdf/2510.19119v2)

> In networked environments, it is common for users to share recommendations about content, products, services, and possible courses of action. Whether these recommendations are accepted and acted upon is highly context-dependent, influenced by the characteristics of the sender and recipient, the nature of their relationship, the attributes of the recommended item, and the communication context. Consequently, probabilities of peer influence exhibit substantial heterogeneity across individuals and settings. Accurate estimation of these probabilities is key to understanding information diffusion processes and to improving the effectiveness of viral marketing strategies. However, learning these probabilities from data is challenging; static data may capture correlations between peer recommendations and peer actions but fails to reveal influence relationships. Online learning algorithms can learn these probabilities from interventions but either waste resources by learning from random exploration or optimize for rewards, thus favoring exploration of the space with higher influence probabilities. In this work, we study learning peer influence probabilities under a contextual linear bandit framework. We show that a fundamental trade-off can arise between regret minimization and estimation error, characterize all achievable rate pairs, and propose an uncertainty-guided exploration algorithm that, by tuning a parameter, attains any pair within this trade-off. Our experiments on semi-synthetic network datasets show the advantages of our method over static methods and contextual bandits that ignore this trade-off.

**Relevance.** KDD 2026: learning peer-influence probabilities with linear contextual bandits; a regret–estimation-error trade-off with all achievable rate pairs; uncertainty-guided exploration. KDD-side evidence that estimation under network dependence is a recognized problem.

### P74

**Linear Contextual Bandits With Interference**  
Yang Xu, Wenbin Lu, Rui Song. *ICML 2025.* [Page](https://openreview.net/forum?id=fbRbrtSvKm) · [PDF](http://arxiv.org/pdf/2409.15682v1)

> Interference, a key concept in causal inference, extends the reward modeling process by accounting for the impact of one unit's actions on the rewards of others. In contextual bandit (CB) settings where multiple units are present in the same round, interference can significantly affect the estimation of expected rewards for different arms, thereby influencing the decision-making process. Although some prior work has explored multi-agent and adversarial bandits in interference-aware settings, how to model interference in CB remains significantly underexplored. In this paper, we introduce a systematic framework to address interference in Linear CB (LinCB), bridging the gap between causal inference and online decision-making. We propose a series of algorithms that explicitly quantify the interference effect in the reward modeling process and provide comprehensive theoretical guarantees, including sublinear regret bounds, finite sample upper bounds, and asymptotic properties. The effectiveness of our approach is demonstrated through simulations and a synthetic data generated based on MovieLens data.

**Relevance.** Linear contextual bandits with interference across units in the same round; algorithms that quantify the interference effect with regret, finite-sample and asymptotic guarantees; MovieLens-based synthetic data. See [82].

### P75

**Multi-Armed Bandits with Interference: Bridging Causal Inference and Adversarial Bandits**  
Su Jia, Peter I. Frazier, Nathan Kallus. *ICML 2025.* [Page](https://openreview.net/forum?id=3YTjTQhX8B) · [PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/jia25b/jia25b.pdf)

> Experimentation with interference poses a significant challenge in contemporary online platforms. Prior research on experimentation with interference has concentrated on the final output of a policy. Cumulative performance, while equally important, is less well understood. To address this gap, we introduce the problem of Multi-armed Bandits with Interference (MABI), where the learner assigns an arm to each of $N$ experimental units over $T$ rounds. The reward of each unit in each round depends on the treatments of all units, where the interference between two units decays in their distance. The reward functions are chosen by an adversary and may vary arbitrarily over time and across different units. We first show that the optimal expected regret (against the best fixed-arm policy) is $\tilde O(\sqrt T)$, and can be achieved by a switchback policy. However, the regret (as a random variable) for any switchback policy suffers a high variance, since it does not account for $N$. We propose a policy based on a novel clustered randomization scheme, whose regret (i) is optimal in  expectation and (ii) admits a high probability bound that vanishes in $N$.

**Relevance (core).** Multi-armed bandits with interference where interference decays with distance and rewards are adversarial; switchback policies are optimal in expectation but high-variance in N; clustered randomization fixes it. Spatially decaying interference and clustered designs mirror our graph-correlated shocks and component structure; their switchbacks are bursty exposure by design.

### P76

**Design-Based Bandits Under Network Interference: Trade-Off Between Regret and Statistical Inference**  
Zichen Wang, Haoyang Hong, Chuanhao Li, Haoxuan Li, Zhiheng Zhang, Huazheng Wang. *NeurIPS 2025.* [Page](https://openreview.net/forum?id=TLxJAqucpL) · [PDF](http://arxiv.org/pdf/2510.07646v2)

> In multi-armed bandits with network interference (MABNI), the action taken by one node can influence the rewards of others, creating complex interdependence. While existing research on MABNI largely concentrates on minimizing regret, it often overlooks the crucial concern that an excessive emphasis on the optimal arm can undermine the inference accuracy for sub-optimal arms. Although initial efforts have been made to address this trade-off in single-unit scenarios, these challenges have become more pronounced in the context of MABNI. In this paper, we establish, for the first time, a theoretical Pareto frontier characterizing the trade-off between regret minimization and inference accuracy in adversarial (design-based) MABNI. We further introduce an anytime-valid asymptotic confidence sequence along with a corresponding algorithm, $\texttt{EXP3-N-CS}$, specifically designed to balance the trade-off between regret minimization and inference accuracy in this setting.

**Relevance (core).** Design-based (adversarial) bandits under network interference with a Pareto frontier between regret and inference accuracy and an anytime-valid asymptotic confidence sequence (EXP3-N-CS). Anytime-valid inference plus network dependence in one paper; their confidence sequence is asymptotic, ours exact under Gaussian dynamics.

### P77

**Mutli-Armed Bandits with Network Interference**  
Abhineet Agarwal, Anish Agarwal, Lorenzo Masoero, Justin Whitehouse. *NeurIPS 2024.* [Page](https://openreview.net/forum?id=ZxZOvVOiiL) · [PDF](https://openreview.net/pdf/7a7932fd0368f67a09848e14871c164691067a1e.pdf)

> Online experimentation with interference is a common challenge in modern applications such as e-commerce and adaptive clinical trials in medicine. For example, in online marketplaces, the revenue of a good depends on discounts applied to competing goods. Statistical inference with interference is widely studied in the offline setting, but far less is known about how to adaptively assign treatments to minimize regret. We address this gap by studying a multi-armed bandit (MAB) problem where a learner (e-commerce platform) sequentially assigns one of possible $\mathcal{A}$ actions (discounts) to $N$ units (goods) over $T$ rounds to minimize regret (maximize revenue). Unlike traditional MAB problems, the reward of each unit depends on the treatments assigned to other units, i.e., there is *interference* across the underlying network of units. With $\mathcal{A}$ actions and $N$ units, minimizing regret is combinatorially difficult since the action space grows as $\mathcal{A}^N$. To overcome this issue, we study a *sparse network interference* model, where the reward of a unit is only affected by the treatments assigned to $s$ neighboring units. We use tools from discrete Fourier analysis to develop a sparse linear representation of the unit-specific reward $r_n: [\mathcal{A}]^N \rightarrow \mathbb{R} $, and propose simple, linear regression-based algorithms to minimize regret. Importantly, our algorithms achieve provably low regret both when the learner observes the interference neighborhood for all units and when it is unknown. This significantly generalizes other works on this topic which impose strict conditions on the strength of interference on a *known* network, and also compare regret to a markedly weaker optimal action. Empirically, we corroborate our theoretical findings via numerical simulations.

**Relevance (core).** MAB where each unit's reward depends on the treatments of s neighbours in a network (sparse interference); a Fourier sparse-linear representation gives regret Õ((A^s T)^{2/3}) with unknown neighbourhoods. Dependence across units through treatments; our dependence is in the rewards' shocks. Both are 'spatial' correlation a graph encodes, in different channels.
