# KuaiRec Experiment Plan: Graph-Based Bandits

As of 9 October 2026. Companion to the [research proposal](../../www/CLAUDE.md). Target: WWW 2027 full paper, 25 October 2026.

> **As built (10 October 2026).** This is the original plan, kept as written. Phase 1, Settings A and B, and a certificate study (Setting A v2) were run; Setting C, the multi-user baselines (GOB.Lin, CLUB, LOCB) and the learned embeddings (ALS, LightGCN, captions) were not. Factorization graphs use PureSVD. The daily trending slot was added later for the fluctuation channel; its protocol is in the [report](README.md#daily-trending-slot-the-fluctuation-channel). The code is in [code/](code), with the layout in the [report's Reproduce section](README.md#reproduce), not the layout of §7.

The plan has three phases:

1. Measure how well each user–user (U2U) and item–item (I2I) graph aligns with KuaiRec's true rewards. This needs no bandit runs.
2. Run graph-based bandits on the same graphs, from instances where every arm's mean is known.
3. Test whether Phase 1's alignment predicts Phase 2's regret gains.

## 1. Data

Source: [KuaiRec 2.0](https://github.com/chongminggao/KuaiRec) ([Zenodo](https://zenodo.org/records/18164998), CC BY-SA 4.0).

| File | Contents | Used for |
| --- | --- | --- |
| `small_matrix.csv` | 1,411 users × 3,327 videos, 4,676,570 rows, 99.6% dense | Ground-truth rewards |
| `big_matrix.csv` | 7,176 users × 10,728 videos, 12,530,806 rows, 16.3% dense | Training embeddings for graphs only |
| `social_network.csv` | 472 users; `friend_list` such as "[4202, 7126]"; 1 to 5 friends, mean 1.42 | Social U2U graph |
| `user_features.csv` | 31 columns: activity level, follow, fan and friend counts, 18 encrypted one-hot features | Feature U2U graph |
| `user_features_raw.csv` | Adds gender, age range, device, and city, province and region | Location and demographic U2U graphs |
| `item_categories.csv` | Tag list per video (1 to 4 tags, mean 1.18) | Tag I2I graph |
| `kuairec_caption_category.csv` | Caption, cover text, topic tag, three-level category | Text and category I2I graphs |
| `item_daily_features.csv` | Daily plays, likes, shares and similar counts per video | Aggregate-statistics I2I graph (leaky; see 3.3) |

Column details used below:

- `watch_ratio` = play_duration / video_duration. The README suggests `like = 1 if watch_ratio > 2.0`.
- About 0.4% of pairs are missing because users blocked those videos' authors.
- Version 2.0 removed video 1225 and re-indexed later IDs.

### 1.1 Step 0 checks (first day)

These facts are not documented, and the leakage rules depend on them:

1. Are the small matrix's users and videos subsets of the big matrix's?
2. Do any (user, video) pairs appear in both matrices?
3. How many of the 1,411 evaluation users appear in `social_network.csv`, and how many of their friends are also evaluation users?
4. Are there duplicate (user, video) rows in the small matrix? If so, average them.
5. What is the distribution of `watch_ratio` (expected mean about 0.85, with a long right tail)?

The result of check 3 decides whether the social graph is a main condition or a minor one. With at most 472 users and 1.42 friends each, expect most evaluation users to be isolated in it.

## 2. Ground-truth rewards

Each (user, video) pair in the small matrix has one observed watch ratio. That observation becomes the arm's true mean, and the simulator draws noisy rewards around it.

| Reward model | True mean μ(u, i) | Simulated reward | Role |
| --- | --- | --- | --- |
| R1 (primary) | min(watch_ratio, 5) / 5 | Bernoulli(μ) | Bounded and continuous, so arm gaps are graded |
| R2 | min(watch_ratio, 5) | μ + Gaussian noise, σ = 0.5 | Matches the Gaussian analysis in the theory |
| R3 (sensitivity) | 1 if watch_ratio > 2, else 0.1 | Bernoulli(μ) | The README's like threshold; large gaps and many ties |

Blocked pairs are removed from that user's arm set. Each user's regret is measured against their best available arm in the sampled set.

A low-rank completion of the small matrix is **not** used as ground truth. It would hand an artificial advantage to embedding graphs.

## 3. Graph construction

### 3.1 Shared conventions

- **Leakage-free embeddings.** Evaluation users are the 1,411 small-matrix users, and evaluation videos are its 3,327 videos.
    - User embeddings are trained on big-matrix interactions with **non-evaluation videos only**.
    - Video embeddings are trained on big-matrix interactions from **non-evaluation users only**.
    - No graph sees any evaluation (user, video) pair. This holds whatever Step 0 finds.
- **Sparsification.** Use mutual kNN with k ∈ {5, 10, 20}, then add each node's single nearest neighbour so no node is isolated. The social graph is the exception and keeps its isolated nodes.
- **Weights.** w = max(cos, 0) for embeddings; Jaccard similarity for sets; 1 for unweighted links.
- **Laplacians.** Combinatorial L = D − W, scaled so the average weighted degree is 1. This keeps energies comparable across graphs. The normalized Laplacian is reported as a check.
- **Null graphs.** For each real graph, build a degree-preserving random rewiring (10 × |E| edge swaps) and an Erdős–Rényi graph with the same number of edges.
- **Extremes.** The empty graph (every user or video alone) and the complete graph (everything pooled) bracket all real graphs.

### 3.2 User–user graphs

| ID | Graph | Construction | Expected alignment |
| --- | --- | --- | --- |
| U-soc | Social | Symmetrize `friend_list`, keep evaluation users; isolated users stay isolated | Weak, mostly from sparsity |
| U-mf | Collaborative MF | Implicit ALS, d = 64, positives = watch_ratio > 2 on non-evaluation videos; cosine mutual kNN | Strongest expected |
| U-gcn | LightGCN | 3 layers, d = 64, BPR loss, same training data as U-mf; cosine mutual kNN | Similar to U-mf |
| U-feat | Profile features | One-hot encode `user_features.csv` (activity, count ranges, 18 encrypted features); Jaccard kNN | Moderate |
| U-geo | Location | Edges between users sharing `fre_city`, weight 1; same `fre_province` only, weight 0.3; sparsified by kNN within groups | Unknown; the literally spatial graph |
| U-demo | Demographic | Gender, age range, device price band from `user_features_raw.csv`; Jaccard kNN | Weak to moderate |
| U-soc+mf | Union | U-soc ∪ U-mf, social edges weighted 1 | Tests whether social edges add anything |

### 3.3 Item–item graphs

| ID | Graph | Construction | Expected alignment |
| --- | --- | --- | --- |
| I-tag | Tags | Jaccard similarity on `feat` tag sets; kNN with random tie-breaking, since many videos share one tag | Moderate |
| I-cat | Category tree | Weight 1 for the same third-level category, 0.3 for the same second level, 0.1 for the same first level; kNN | Moderate; tree-like |
| I-text | Caption text | Chinese sentence encoder (for example bge-small-zh) on caption, cover text and topic tag; cosine kNN | Moderate |
| I-mf | Collaborative MF | Video vectors from ALS on non-evaluation users; cosine kNN | Strongest expected |
| I-gcn | LightGCN | As I-mf with LightGCN | Similar to I-mf |
| I-stat | Aggregate statistics | Standardized per-video means of `item_daily_features` rates (play progress, like, share and complete-play rates); cosine kNN | Probably high, **but leaky**: the counts include evaluation users. Reported separately, never as a main result |

### 3.4 Product graphs

For the joint setting, the arms are (user, video) pairs on L_U ⊕ L_I = L_U ⊗ I + I ⊗ L_I. This graph is never built explicitly. Its eigenpairs are the sums λ_a + λ_b of factor eigenvalues and the outer products u_a ⊗ v_b of factor eigenvectors. Spectral methods therefore need only the two factor eigendecompositions, of at most 1,411 × 1,411 and 3,327 × 3,327.

Candidate pairs: the best U2U graph from Phase 1 with the best I2I graph, plus U-soc ⊕ I-tag as the graphs a platform has without any model.

## 4. Phase 1: alignment diagnostics

These are computed on the full 1,411 × 3,327 matrix, for every graph and every null graph.

| Measure | Definition | Computed for | Link to theory |
| --- | --- | --- | --- |
| Smoothness quotient | μᵀLμ / ‖μ − mean(μ)‖², a scale-free graph frequency | Each user's row on I2I graphs; each video's column on U2U graphs | Low means smooth; compared against the null graphs |
| Energy-to-gap ratio | √(μᵀLμ) / Γ, with Γ = the best arm minus the 10th best | Each user (I2I), each video (U2U) | The certified bound helps when this is below about 1 |
| Resistance radius | ρ_L from the minimum enclosing ball in the L† embedding | Each graph on sampled 300-node subsets | Sets how much loosening the certificate costs |
| Top-1 preservation | Share of users whose best video is unchanged after smoothing with (I + λL)⁻¹, λ ∈ {0.1, 1, 10} | I2I graphs; U2U graphs per video | The empirical form of the repo's counterexample |
| Top-10 overlap | Overlap of the top 10 before and after smoothing | As above | Softer version of the above |
| Edge homophily | Mean correlation of μ_u and μ_v over U2U edges, against non-edges | U2U graphs | Plain-language summary for WWW readers |

Outputs:

- Figure 1: smoothness quotients per graph, real against null.
- Table 1: median energy-to-gap ratio and top-1 preservation per graph.
- A ranked choice of graphs for Phase 2.

## 5. Phase 2: bandit experiments

### 5.1 Settings

| Setting | Graph | Instance | Users and arms | Horizon |
| --- | --- | --- | --- | --- |
| A: item graph, one user | I2I | Each user is an independent bandit; the I2I graph is shared | 100 sampled users; K ∈ {100, 300} videos | 5,000 rounds per user |
| B: user graph, many users | U2U | Users arrive uniformly at random; the learner picks a video for the arriving user | n = 300 users; K = 100 videos | 100,000 rounds, about 333 per user |
| C: both graphs | U2U ⊕ I2I | As B | n = 300, K = 300 | 100,000 rounds |
| B-large | U2U | As B, with scalable methods only | n = 1,411, K = 100 | 300,000 rounds |

In B and C each user is seen fewer times than there are arms. This is the cold-user regime where pooling across users matters most, and it is typical of real feeds.

Videos are sampled stratified by first-level category, with 5 independent video draws per setting. Users are split 50/50 into a tuning half and a test half; all reported numbers come from the test half. A second arrival model weights users by `user_active_degree`.

### 5.2 Algorithms

All methods use the same reward stream per seed (common random numbers), so comparisons are paired.

**Baselines (no graph)**

| Algorithm | Notes | Settings |
| --- | --- | --- |
| UCB1, KL-UCB | Independent per (user, video) | A, B, C |
| Bernoulli Thompson sampling | Beta(1, 1) priors | A, B, C |
| Global Thompson sampling | One posterior per video shared by all users (the complete-graph extreme) | B, C |
| LinUCB-IND, LinUCB-ONE | Video features = tag one-hot (31) concatenated with I-mf vector (64, reduced to 16 by PCA); per-user and shared models | B, C |
| Oracle best-fixed | Each user's best arm; the regret reference | All |

**Item-graph methods**

| Algorithm | Graph use | Settings | Key hyperparameters |
| --- | --- | --- | --- |
| SpectralUCB, SpectralTS ([Kocák et al. 2020](https://www.jmlr.org/papers/v21/16-529.html)) | Regression on the 50 smoothest L_I eigenvectors | A | λ ∈ {0.01, 0.1, 1}; eigenvectors ∈ {20, 50, 100}; confidence scale ∈ {0.1, 0.5, 1} |
| GP-UCB, regularized Laplacian kernel | Kernel (L_I + εI)⁻¹, ε = 0.01 | A | Exploration scale grid as above |
| SP-UCB (this repo) | Count-weighted spectral pooling, intersected with arm UCB | A | λ grid; energy bound S |
| GDE-UCB (this repo) | Resistance design with certified elimination | A | Energy bound S |

**User-graph methods**

| Algorithm | Graph use | Settings | Notes |
| --- | --- | --- | --- |
| GOB.Lin ([Cesa-Bianchi et al. 2013](https://arxiv.org/abs/1306.0811)) | Fixed L_U couples per-user linear models | B (n = 300) | n·d = 4,800 parameters with d = 16 |
| Spectral TS on L_U ⊗ I | Non-contextual: each video's column is smoothed over users | B, B-large | Factor eigendecomposition only |
| Certified user pooling | SP-UCB applied per video column on L_U | B, B-large | The new method; T4 covers it |
| CLUB ([Gentile et al. 2014](https://proceedings.mlr.press/v32/gentile14.html)) | Learns user clusters online from a complete graph | B, B-large | Edge-deletion threshold grid |
| CLUB seeded with a U2U graph | As CLUB, starting from the supplied graph instead of a complete graph | B | Shows whether the graph helps clustering |
| LOCB ([Ban and He, WWW 2021](https://arxiv.org/abs/2103.00063)) | Local clustering around seeds | B | Optional; cut first if time is short |

**Both graphs**

| Algorithm | Graph use | Settings | Notes |
| --- | --- | --- | --- |
| Product Spectral TS / UCB | Eigenbasis of L_U ⊕ L_I, top 200 eigenpairs | C | Implemented through the factor eigenpairs |
| Laplacian Kernelized Bandit, TS variant ([Wu and Amini 2026](https://arxiv.org/abs/2601.00461)) | Multi-user kernel fusing L_U with a video kernel | C | Implemented in a truncated eigenbasis, so T = 100,000 stays tractable |
| Certified product pooling | SP-UCB on L_U ⊕ L_I with fallback to arm UCB | C | The paper's main method |

Graph Neural Bandits ([Qi et al., KDD 2023](https://arxiv.org/abs/2308.10808)) is cited but not run in the sprint.

### 5.3 Graph conditions per run

Each graph-aware method runs on:

- The best real graph and a mid-ranked real graph from Phase 1
- U-soc, wherever coverage permits
- The degree-preserving null graph
- A deliberately misaligned graph: the best graph with edges rewired toward dissimilar nodes, to trigger the counterexample's failure

Certified methods also vary their supplied energy bound:

- S = the true energy × {1, 2, 4} (valid)
- S = the true energy × 0.5 (invalid, as a stress test)
- S estimated from a uniform warm-up of 5% of the horizon (realistic)

### 5.4 Metrics

- Cumulative regret at the horizon and over time; regret ratio against Bernoulli TS
- Regret by user segment: friend count (0 against 1 or more), activity level, embedding-neighbour density
- Rounds until each user's chosen video is within 0.05 of their best
- Wall-clock time per 1,000 rounds

Statistics:

- 10 seeds per configuration in the sprint, 20 for the camera-ready.
- 95% confidence intervals by bootstrap over users.
- Paired differences between methods using the common random numbers.

## 6. Phase 3: does alignment predict regret?

- For each (graph, method, video draw), regress log(regret ratio against TS) on the median energy-to-gap ratio and on top-1 preservation, with graph-family fixed effects.
- Report the threshold ratio where the gain changes sign, and compare it with the value of about 1 predicted by T1.
- **Graph-selection rule.** After the warm-up, estimate each candidate graph's smoothness quotient from warm-up data and pick the smoothest. Report its regret relative to the best graph chosen in hindsight.

Planned figures:

- Figure 2: regret curves for Settings A, B and C.
- Figure 3: alignment against regret gain, one point per (graph, video draw).
- Figure 4: certified against uncertified methods on aligned, null and misaligned graphs.

## 7. Implementation

```
experiments/kuairec/
  data.py          # load, re-index, Step 0 checks, reward models R1 to R3
  embeddings.py    # ALS and LightGCN on leakage-free splits; caption encoder
  graphs.py        # U2U and I2I builders, nulls, Laplacians, factor eigendecompositions
  alignment.py     # Phase 1 measures; writes results/kuairec/alignment.csv
  bandits/
    baselines.py   # UCB1, KL-UCB, TS, global TS, LinUCB
    spectral.py    # SpectralUCB/TS on one graph or a product graph; GP-UCB
    certified.py   # SP-UCB, GDE-UCB, certified user and product pooling
    multiuser.py   # GOB.Lin, CLUB, LOCB, LK-GP (truncated)
  run.py           # one configuration per call; writes runs.csv like the repo's other studies
  analyze.py       # Phase 3 regressions and figures
```

The repo's existing experiments use only the standard library. These need numpy, scipy and pandas, plus `implicit` for ALS, PyTorch for LightGCN and `sentence-transformers` for captions. Pin them in `experiments/requirements.txt`.

Scale check:

- The largest dense eigendecomposition is 3,327 × 3,327 and runs in seconds.
- GOB.Lin's 4,800 × 4,800 matrix is updated by rank-one steps.
- Setting B-large at 300,000 rounds with spectral methods costs one 200-dimensional update per round.
- The whole grid should fit on a laptop over 2 to 3 days, or less if runs are parallel.

## 8. Schedule

| Dates | Work | Output |
| --- | --- | --- |
| 9–10 Oct | Download; Step 0 checks; reward models | Data report, including social coverage |
| 10–12 Oct | Embeddings on leakage-free splits; all graphs and nulls | `graphs/` cache |
| 12–13 Oct | Phase 1 alignment | Figure 1, Table 1, graph ranking |
| 13–17 Oct | Baselines and Setting A; then Settings B and B-large | First regret tables |
| 16–18 Oct | Abstract written from Phase 1 and early Phase 2 results | Abstract submitted by 18 Oct |
| 18–21 Oct | Setting C; energy-bound stress tests; Phase 3 | Figures 2 to 4 |
| 21–25 Oct | Writing; appendix with proofs and reproducibility | Submission by 25 Oct |

If time runs short, cut in this order: LOCB, B-large, U-demo and U-geo, the 20-seed reruns. The minimum paper is Phase 1 for all graphs, plus Settings A and B with baselines, Spectral methods, GOB.Lin, CLUB and the certified methods.
