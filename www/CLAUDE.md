# Graph-Based Bandits on the Web: Research Proposal

As of 9 October 2026. Working title: *Which Graph Can a Bandit Trust? Certified User and Item Graphs for Online Recommendation*.

Target: The ACM Web Conference 2027 (Dublin, 10–14 May 2027). **Abstract due 18 October 2026, full paper due 25 October 2026**, both end of day Anywhere on Earth ([call for papers](https://www2027.thewebconf.org/?p=296)).

## Summary

Web recommenders already produce the graphs that graph-based bandits need: social networks give user–user (U2U) edges, and every embedding model gives U2U and item–item (I2I) kNN graphs. Graph bandits assume rewards are smooth on the supplied graph. Nobody checks that before deployment, and a misaligned graph can cause linear regret.

We propose a WWW paper with two parts:

1. **Theory.** Extend this repo's graph-alignment results (certified energy bounds, resistance geometry, graph-error inflation) from graphs over arms to graphs over users. Then cover both together on the product of the two graphs.
2. **Measurement and experiments.** On KuaiRec, which has a nearly fully observed user × video matrix plus a social network, we can measure exactly how well social, embedding and content graphs align with true rewards. We then test whether alignment predicts which graph bandit wins, and whether certified policies avoid the failures of uncertified ones.

Temporal dependence and non-graph structured bandits (linear, unimodal, Lipschitz) are out of scope for this paper.

## Motivation and gap

Graph bandits in recommendation come in two lines, and both take the graph as given:

- **Graph over arms (items):** SpectralUCB and SpectralTS ([Valko et al. 2014](https://proceedings.mlr.press/v32/valko14.html); [Kocák et al. 2020](https://www.jmlr.org/papers/v21/16-529.html)); GRUB for best-arm identification ([Thaker et al. 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html)).
- **Graph over users:** GOB.Lin on a social graph ([Cesa-Bianchi et al. 2013](https://arxiv.org/abs/1306.0811)); clustering of bandits, which learns a user graph online, such as CLUB ([Gentile et al. 2014](https://proceedings.mlr.press/v32/gentile14.html)) and LOCB ([Ban and He, WWW 2021](https://arxiv.org/abs/2103.00063)); Graph Neural Bandits ([Qi et al., KDD 2023](https://arxiv.org/abs/2308.10808)); the Laplacian Kernelized Bandit ([Wu and Amini, ICLR 2026](https://arxiv.org/abs/2601.00461)).

What the web adds is a choice of graphs, none of them validated:

- **Social graphs measure friendship, not taste.** Homophily on platforms such as Kuaishou or Last.fm may be weak for a given reward.
- **Embedding graphs are trained on past rewards.** They may align well, but they inherit the recommender's exposure bias, and they leak information if trained on the evaluation data.
- **Wrong graphs cause linear regret.** The repo's counterexample ([graph_spectral_bandits.md](../research/graph_spectral_bandits.md), Section 4) makes a smoothed index pick a suboptimal arm forever. The [alignment manuscript](../research/alignment_paper/manuscript.pdf) prices this with a certified energy bound, but only for graphs over arms and only on synthetic graphs.

Recent work adds noisy-graph penalties for spectral projection ([Mondal et al. 2026](https://arxiv.org/abs/2606.27917)) and robust clustering under misspecified user models ([Wang et al., NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/0bcd8d153b8c548629eca53f4ebdeb42-Paper-Conference.pdf)). Neither measures the alignment of real web graphs, or certifies a graph a recommender produced.

**Web relevance, for page 1.** The 2027 call desk-rejects papers that "merely use a Web artifact". Our problem is Web-specific: social and embedding graphs are by-products of web platforms, and the question is whether online learners on those platforms can trust them.

## Model

There are n users and K items. Each user u has a mean reward μ_{u,i} for item i; collect these in an n × K matrix M. In round t a user u_t arrives, the learner picks an item, and observes a noisy reward. Regret is summed over rounds against each arriving user's best item.

Two graphs constrain M:

| Graph | Laplacian | Smoothness assumption | Source on the web |
| --- | --- | --- | --- |
| Item–item (I2I) | L_I (K × K) | Each user's row is smooth over items: Σ_u M_u L_I M_uᵀ ≤ S_I² | Tags, categories, item embeddings, co-consumption |
| User–user (U2U) | L_U (n × n) | Each item's column is smooth over users: Σ_i M_iᵀ L_U M_i ≤ S_U² | Social network; kNN on user embeddings; user features |

The two energies add up to the energy of vec(M) on the **Cartesian product graph**, whose Laplacian is L_U ⊗ I_K + I_n ⊗ L_I:

$$
\operatorname{tr}(M^\top L_U M) + \operatorname{tr}(M L_I M^\top) = \operatorname{vec}(M)^\top \left(L_U \oplus L_I\right) \operatorname{vec}(M)
$$

So a user-graph bandit, an item-graph bandit and a combined one are all graph-over-arms problems on a single graph. The arms are (user, item) pairs, and only the arriving user's row can be played. This is how the repo's theory carries over.

## Theoretical component

Recent WWW bandit papers in research tracks state a regret or correctness guarantee (see the section on WWW precedent). Reviewers need not read past page 8, so theorem statements go in the main text and proofs in the appendix.

| # | Statement | Status | Source |
| --- | --- | --- | --- |
| T1 | A finite-time regret bound for certified graph pooling (SP-UCB / GDE-UCB) under a valid energy bound, never worse than per-arm UCB up to constants | Proved for graphs over arms | [Alignment manuscript](../research/alignment_paper/manuscript.pdf) |
| T2 | If an estimated graph satisfies (1 − η)L ≼ L̂ ≼ (1 + η)L, inflating the energy radius by √(1 + η) keeps the certificate valid | Proved | Alignment manuscript |
| T3 | Uncertified smoothing on a misaligned graph incurs linear regret | Counterexample exists; needs a general statement | [graph_spectral_bandits.md](../research/graph_spectral_bandits.md) |
| T4 | T1 on the product graph, with the restriction that only the arriving user's row can be played. Regret should scale with the product graph's effective dimension and resistance radius | **New; to prove** | This paper |
| T5 | A certificate for embedding-built U2U graphs: an η-comparison between the embedding graph and a held-out reference graph, estimated from data | **New; to prove, or state as a proposition with an empirical check** | This paper |

T4 is the main theoretical risk. The fallback is to prove T4 only for a uniform arrival of users and present the general case as a conjecture with numerical evidence.

## Graphs to build

| Side | Graph | Built from | Leakage control |
| --- | --- | --- | --- |
| U2U | Social | KuaiRec friend list (`social_network.csv`); Last.fm friend relations | None needed |
| U2U | Embedding kNN | User vectors from matrix factorization and LightGCN, trained on KuaiRec's large sparse matrix | Train only on interactions outside the evaluation matrix |
| U2U | Feature kNN | KuaiRec's user feature fields | None needed |
| I2I | Content kNN | Video tags and captions | None needed |
| I2I | Embedding kNN | Item vectors from the same factorization models | As for U2U embeddings |
| Both | Product | Best U2U graph ⊕ best I2I graph | As above |

kNN graphs use k in {5, 10, 20} with cosine weights. For each graph we also build a degree-preserving random rewiring as a null graph.

## Datasets

| Dataset | Role | Users × items | U2U graph | I2I graph | Ground truth |
| --- | --- | --- | --- | --- | --- |
| [KuaiRec](https://github.com/chongminggao/KuaiRec) | Primary | 1,411 × 3,327, nearly fully observed | Social; embeddings; features | Tags; embeddings | Exact |
| Last.fm (HetRec 2011) | Comparison with GOB.Lin and CLUB, which used it | About 1,900 users with a friend graph | Social; embeddings | Artist tags | Semi-synthetic from listening counts |
| [Open Bandit Dataset](https://arxiv.org/abs/2008.07146) | eCommerce item-graph check | Item graph only | None (no user graph) | Item features and categories | Unbiased replay |

KuaiRec's social graph is sparse: `social_network.csv` lists only 472 users, with 1 to 5 friends each (mean 1.42). Embedding, feature and location graphs therefore carry the U2U results on KuaiRec. The social graph remains one condition there, and Last.fm carries the main social-graph result. The full KuaiRec design is in [kuairec_experiment_plan.md](kuairec_experiment_plan.md).

## Algorithms

| Graph used | Algorithms | Certified? |
| --- | --- | --- |
| None | Per-user UCB and Thompson sampling; LinUCB per user (IND) and shared across users (ONE) | Not needed |
| I2I only | SpectralUCB, SpectralTS; GP-UCB with kernel (L_I + εI)⁻¹ | No |
| I2I only | SP-UCB, GDE-UCB (this repo) | Yes |
| U2U, fixed | GOB.Lin; GP-UCB with kernel (L_U + εI)⁻¹ | No |
| U2U, learned online | CLUB, LOCB | Partly: clusters are tested online |
| Both | Laplacian Kernelized Bandit (LK-GP-UCB / TS); certified pooling on the product graph (T4) | The new policy is certified; LK-GP is not |

Graph Neural Bandits is cited but not run, since it needs significant engineering for a two-week schedule.

## Research questions and hypotheses

1. **Which real graphs are aligned?** Measure the energy ratio √(energy)/Γ, the resistance radius and the rank flips after smoothing, for every graph above.
    - H1: embedding U2U graphs are better aligned than the social graph.
    - H2: random rewirings score clearly worse than the real graphs, confirming the measures carry signal.
2. **Does alignment predict regret gain?** Across users, graphs and algorithms, regress the regret gain over per-user UCB on the measured alignment.
    - H3: gains are positive only below an energy-to-gap ratio of about one, as T1 suggests.
3. **Is certification worth it?** Compare certified pooling with SpectralUCB, GOB.Lin and LK-GP on aligned, misaligned and rewired graphs.
    - H4: certified policies lose little on aligned graphs and avoid linear regret on misaligned ones.
4. **Do U2U and I2I graphs combine?** Compare product-graph policies with each graph alone.
    - H5: the product graph beats each single graph when both are aligned, and the certificate falls back when one is not.

## Experimental protocol

- **Instances.** On KuaiRec, users arrive uniformly at random from the 1,411; the arms are 200 to 500 sampled videos. Rewards are Bernoulli with a watch ratio above 2 as a positive. The threshold is varied as a sensitivity check.
- **Horizon and repetition.** 50,000 to 200,000 rounds, so each user is seen 35 to 140 times; 20 seeds per configuration.
- **Tuning.** Every graph-aware method uses the same λ grid, chosen on a held-out user split.
- **Metrics.** Cumulative regret and its ratio to per-user UCB; alignment measures per graph; correlation between alignment and gain; and the share of runs where a certified policy beats both baselines and uncertified graph policies.
- **Reproducibility.** Code and graph-building scripts are released. The call "strongly encourages" this.

## WWW precedent: do application papers include theory?

For bandit papers in WWW research tracks, the answer is usually yes. The calls themselves require no theory: the 2027 criteria are "originality, technical merit, potential impact, quality of execution, quality of presentation, related work, reproducibility of results, and ethics". But recent accepted bandit papers almost all state a regret bound alongside real-data experiments.

| Paper | Venue | Theory | Experiments |
| --- | --- | --- | --- |
| [LinUCB](https://arxiv.org/abs/1003.0146) (Li et al.) | WWW 2010 | None new; the algorithm is motivated by confidence bounds | Yahoo! front-page logs, offline replay evaluation |
| [Conversational Contextual Bandit](https://arxiv.org/abs/1906.01219) (Zhang et al.) | WWW 2020 | Regret bound smaller than LinUCB's | Synthetic data, Yelp and Toutiao |
| [Local Clustering in Contextual Bandits](https://arxiv.org/abs/2103.00063) (Ban and He) | WWW 2021 | Clustering correctness and a regret bound | Synthetic data and MovieLens |
| [Expected Value of Information Meets Bandit Learning](https://dl.acm.org/doi/10.1145/3696410.3714773) | WWW 2025 | Tighter regret bounds for conversational TS and UCB | Not checked |
| [Batch Bayesian Sampling for Adaptive Traffic Experimentation](https://arxiv.org/abs/2305.14704) (eBay) | WWW 2024, Industry | Practical; not centred on new regret theory | eBay experimentation platform |

What this means for us:

- **Research track:** state T1 to T5 as theorems or propositions in the first 8 pages. Experiments alone, without guarantees, would be unusual for a bandit paper there.
- **Industry track:** it reviews "with a focus on real-world applicability over theoretical novelty", but requires that submissions "clearly describe how their work has been deployed". We have no deployment, so this track does not fit.
- **Track choice:** "Search, Recommendation, and Retrieval-Augmented AI" explicitly lists "online learning ... for ranking and recommendation" and is the recommended track. "Graph Algorithms and Modeling for the Web" is the alternative, since it covers user–item graphs. "Evaluation, Human Computation, and Resources" would fit only a benchmark-only framing.

## Expected contributions

1. Regret guarantees for certified graph pooling on user graphs and on the product of user and item graphs (T4), with a certificate for embedding-built graphs (T5).
2. The first measured alignment, to our knowledge, of social, embedding and content graphs against exact rewards, on KuaiRec.
3. Evidence on whether measured alignment predicts which graph bandit wins, and on what certification costs and saves.

## Risks

| Risk | Effect | Mitigation |
| --- | --- | --- |
| 16 days to the full paper | Scope cannot all fit | Cut in this order: Open Bandit Dataset, Last.fm, LOCB, product-graph experiments |
| T4 proof does not close in time | Weaker theory section | Prove the uniform-arrival case; state the general case as a conjecture with evidence |
| KuaiRec social graph is sparse among evaluation users | No social-graph result on exact data | Report its coverage; use Last.fm for the social result |
| Embedding graphs leak evaluation data | Inflated alignment | Train on the large matrix only, excluding evaluation interactions; report a time-split check |
| Real graphs are weakly aligned everywhere | No regret gain to report | Lead with the measurement and with certification avoiding loss |

## Sprint plan to 25 October

1. **9–12 Oct:** KuaiRec loader; build all graphs; check social coverage; alignment diagnostics.
2. **12–16 Oct:** regret runs for the algorithms table on KuaiRec; work on the T4 proof in parallel.
3. **16–18 Oct:** write and submit the title and abstract (deadline 18 Oct; placeholder abstracts are forbidden, and authors are frozen after this date).
4. **18–22 Oct:** product-graph experiments; Last.fm if time allows; figures; theory write-up.
5. **22–25 Oct:** full draft, appendix with proofs and reproducibility details, submission.

If 25 October proves infeasible, the same plan with Last.fm, Open Bandit Dataset and Graph Neural Bandits restored fits a later venue.

## Sources

- The Web Conference 2027. [Call for Research Track Papers](https://www2027.thewebconf.org/?p=296).
- The Web Conference 2026. [Call for Research Tracks](https://www2026.thewebconf.org/calls/research-tracks.html); [Call for Industry Tracks](https://www2026.thewebconf.org/calls/industry.html).
- Valko, Munos, Kveton, Kocák. [Spectral Bandits for Smooth Graph Functions](https://proceedings.mlr.press/v32/valko14.html). ICML 2014.
- Kocák, Munos, Kveton, Agrawal, Valko. [Spectral Bandits](https://www.jmlr.org/papers/v21/16-529.html). JMLR 21, 2020.
- Thaker et al. [Maximizing and Satisficing in Multi-armed Bandits with Graph Information](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html). NeurIPS 2022.
- Cesa-Bianchi, Gentile, Zappella. [A Gang of Bandits](https://arxiv.org/abs/1306.0811). NeurIPS 2013 (GOB.Lin).
- Gentile, Li, Zappella. [Online Clustering of Bandits](https://proceedings.mlr.press/v32/gentile14.html). ICML 2014 (CLUB).
- Ban, He. [Local Clustering in Contextual Multi-Armed Bandits](https://arxiv.org/abs/2103.00063). WWW 2021 (LOCB).
- Qi, Ban, He. [Graph Neural Bandits](https://arxiv.org/abs/2308.10808). KDD 2023.
- Wu, Amini. [Laplacian Kernelized Bandit](https://arxiv.org/abs/2601.00461). ICLR 2026.
- Mondal et al. [Graph Dimensionality Reduction for Contextual Bandits](https://arxiv.org/abs/2606.27917). Preprint, June 2026.
- Wang et al. [Online Clustering of Bandits with Misspecified User Models](https://proceedings.neurips.cc/paper_files/paper/2023/file/0bcd8d153b8c548629eca53f4ebdeb42-Paper-Conference.pdf). NeurIPS 2023.
- Zhou, Fu, Ryzhov. [Sequential Learning with a Similarity Selection Index](https://pubsonline.informs.org/doi/abs/10.1287/opre.2023.2478). Operations Research 72(6), 2024.
- Li, Chu, Langford, Schapire. [A Contextual-Bandit Approach to Personalized News Article Recommendation](https://arxiv.org/abs/1003.0146). WWW 2010.
- Zhang, Xie, Li, Lui. [Conversational Contextual Bandit: Algorithm and Application](https://arxiv.org/abs/1906.01219). WWW 2020.
- [Towards Efficient Conversational Recommendations: Expected Value of Information Meets Bandit Learning](https://dl.acm.org/doi/10.1145/3696410.3714773). WWW 2025.
- [Practical Batch Bayesian Sampling Algorithms for Online Adaptive Traffic Experimentation](https://arxiv.org/abs/2305.14704). WWW 2024 Industry track.
- Gao et al. [KuaiRec: A Fully-observed Dataset and Insights for Evaluating Recommender Systems](https://arxiv.org/abs/2202.10842). CIKM 2022; [data and files](https://github.com/chongminggao/KuaiRec).
- Saito et al. [Open Bandit Dataset and Pipeline](https://arxiv.org/abs/2008.07146). NeurIPS Datasets and Benchmarks 2021.
- Internal: [graph alignment manuscript](../research/alignment_paper/manuscript.pdf) and [graph spectral note](../research/graph_spectral_bandits.md).
