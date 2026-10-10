# Novelty audit: graph alignment and cumulative regret

Assessment date: 8 October 2026. This assesses the current working manuscript, not an independently reviewed publication. The search establishes substantial prior overlap; it does not establish priority for every specialized result.

**Revision update.** The assessment below originally concerned the diameter-based pooling draft. The revised manuscript now makes a narrower, stronger case: an exact information design for homogeneous graph-energy components, a first-order sensitivity governed by resistance radius, a path--clique separation invisible to component diameters, and a policy that achieves the improved arm-count dependence on paths. It also quantifies certified Laplacian perturbations. These are candidate graph-specific contributions; their priority has not been established.

The minimum enclosing resistance radius is equivalent to the established maximum graph variance problem of [Devriendt, Martin-Gutierrez, and Lambiotte, SIAM Review 2022](https://doi.org/10.1137/20M1361328). The revised paper credits that geometry. Resistance-based sampling and elimination of unsampled arms also appear in [Thaker et al.'s GRUB, NeurIPS 2022](https://papers.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html), with a pure-exploration objective. Neither construction should be claimed as a new general principle.

The original limitations concerning untrusted certificates and unmatched positive-uncertainty leading constants remain. The new experiments expose design overhead on small graphs and cliques. Their Gaussian width-profile comparator is an analogue, not the Bernoulli Clus-UCB implementation, and they do not establish superiority over tuned spectral policies. The earlier audit is retained below to make the motivation and limits of the revision reviewable.

**Assessment.** A claim to be the first study of graph correctness, similarity quality, or structural misspecification in regret minimization is unsupported. The current manuscript is a useful technical starting point with incremental contributions. A stronger publication contribution would need to explain what its graph geometry or learning guarantees add beyond existing spectral, clustered, and misspecified bandits.

**What “correctness” means.** Three questions should be separated:

1. Does smoothing preserve the ordering of true rewards? This is ordinal alignment.
2. How informative is a valid quantitative restriction on reward differences? This is the question answered by the current energy certificates and regret bounds.
3. What if the asserted restriction is false or unknown, and how much does learning its validity cost? The present algorithm has no general guarantee for this setting.

The manuscript assumes supplied bounds $`\mu_c^\top L_c\mu_c\le S_c^2`$. Its clique calculation varies the allowed budget $`S_c`$ while the actual true means remain homogeneous and their energy remains zero. Consequently, that curve describes uncertainty allowed by prior information, not a directly observed measure of how wrong the graph is. The corrupted-graph experiment also supplies an oracle certificate. It does not demonstrate inexpensive validation from selected-arm feedback.

**Closest primary research.**

| Prior work | Established overlap | Consequence for this manuscript |
| --- | --- | --- |
| [Valko et al., ICML 2014](https://proceedings.mlr.press/v32/valko14.html); [Kocák et al., JMLR 2020](https://www.jmlr.org/papers/v21/16-529.html) | Graph-smooth arm rewards, spectral estimation, and cumulative-regret bounds using effective dimension and a smoothness norm. JMLR Theorem 8 and Remark 9 discuss the necessary norm bound and choosing it too small. | Graph arms, Laplacian regularization, and quantitative dependence on smoothness are established. |
| [Carlsson, Dubhashi, and Johansson, IJCAI 2021](https://www.ijcai.org/proceedings/2021/0305.pdf) | Theorem 4 explicitly connects clustering quality to regret through cluster widths and separation, under strong dominance. | A regret bound that improves with similarity quality is not a new general principle. Our assumptions differ, which must be made explicit. |
| [Gore and Chaporkar, Clus-UCB, 2025 preprint, v2](https://arxiv.org/html/2508.02909v2) | Known cluster-width constraints, regret lower bounds, information sharing, and discussion of incorrect widths. | The closest comparator for the policy and interpolation calculation. It also raises the difficulty of learning widths. |
| [Bogunovic and Krause, NeurIPS 2021](https://papers.neurips.cc/paper_files/paper/2021/hash/177db6acfe388526a4c7bff88e1feb15-Abstract.html) | Kernelized bandit regret depends on approximation error; algorithms address known and unknown misspecification. | Robustness to an imperfect similarity model and unknown error are already studied more broadly. |
| [Combes, Magureanu, and Proutiere, NIPS 2017](https://papers.nips.cc/paper_files/paper/2017/hash/e19347e1c3ca0c0b97de5fb3b690855a-Abstract.html) | Instance-specific information lower bounds and optimal exploration for structured bandits. | The information optimization and its monotonicity under nested model classes are inherited principles. |
| [Mondal, Shihab, and Sharma, June 2026 preprint](https://arxiv.org/html/2606.27917v1) | Regret analysis for approximate graph smoothness and noisy eigenspaces, including a residual-sensitive oracle bound. | Even explicitly graph-dependent mismatch penalties have a close recent predecessor. Its contextual setting and oracle requirements differ from ours. This is a preprint, not a peer-reviewed result. |

Related ideas also constrain possible extensions. [Liu, Yin, and Wang, UAI 2023](https://proceedings.mlr.press/v216/liu23c.html) study approximation error relative to suboptimality gaps. [Wang et al., 2023 preprint](https://arxiv.org/abs/2310.02717) study robust online clustering of contextual user models. These are different models, but a proposal for “errors near the optimum matter more” or “learn a robust similarity graph” must explain its distinction from them.

**Assessment of individual contributions.**

| Element of the draft | Incremental value | Present novelty assessment |
| --- | --- | --- |
| Distinguishing ranking preservation from useful quantitative information | Clarifies the transition from final selection to cumulative regret. | Useful conceptual explanation and counterexample; insufficient as the main research contribution. |
| Energy-to-diameter conversion using effective resistance | Translates graph smoothness into a usable pooling certificate. | Standard quadratic-form geometry applied to this bandit construction. |
| SP-UCB and its finite-time component bound | Simple policy and transparent dependence on certified width relative to the component gap; does not need one initial pull per arm. | A candidate algorithmic variation. The proof is elementary and its analysis ultimately uses cluster widths rather than the full graph spectrum. |
| Homogeneous-clique information constant | Explicitly solves the optimization for this Gaussian energy class. | A candidate specialized result, with strong mathematical overlap described below. Priority is not established. |
| Synthetic experiments | Reproducible illustration of the theorem's intended regime. | No empirical superiority established: favorable homogeneous groups, isolated best arm, supplied certificates, and no Clus-UCB or clustered Thompson sampling comparisons. |
| Validation of an untrusted graph | Potentially consequential practical question. | Not solved in this manuscript. It cannot be included among completed contributions. |

**The clique interpolation needs particularly careful positioning.** Our constant is

```math
C_c=\frac{2\sigma^2m\Gamma}
{\Gamma^2+(m-1)(\Gamma-S/\sqrt{w(m-1)})_+^2}.
```

For a homogeneous cluster, Clus-UCB's lower-bound expression reduces to $`m\Gamma/[d+(m-1)b]`$, where $`d`$ and $`b`$ are its one-sided divergences at the optimum and at the optimum minus the width. Replacing these by Gaussian divergences gives the same algebraic expression with width $`\beta=S/\sqrt{w(m-1)}`$. This is our mathematical comparison, not a Gaussian theorem proved in that Bernoulli paper. The energy and width classes are different; the shared extremal shape limits the case for a fundamentally new interpolation law.

**A useful limitation on any validation proposal.** Consider Gaussian rewards with known variance $`\sigma^2`$, a unique best arm with mean below one, and an arbitrary candidate graph carrying no trusted restrictions. If a policy is uniformly efficient over every mean vector in $`[0,1]^K`$, then even at an instance perfectly matching the candidate graph,

```math
\liminf_{T\to\infty}\frac{\mathbb E R_T}{\log T}
\ge \sum_{i:\Delta_i>0}\frac{2\sigma^2}{\Delta_i}.
```

This is a direct specialization of the standard change-of-measure lower bound, not a new theorem. To see why, an alternative environment can change only arm $`i`$ to mean $`\mu^*+\eta`$. Other arms provide no evidence against this alternative. The necessary information gives $`\liminf \mathbb E N_i(T)/\log T\ge 2\sigma^2/(\Delta_i+\eta)^2`$; let $`\eta\downarrow0`$ and sum regret contributions. The structured information framework above formalizes the same argument.

Thus a policy cannot retain the reduced component-wise logarithmic constant while also promising logarithmic regret on every arbitrary graph violation using only ordinary bandit observations. This does not rule out finite-horizon benefits, weaker robustness requirements, restricted violations, or additional informative data. Clus-UCB v2 also discusses the corresponding obstacle for learning unrestricted cluster widths.

**Where a stronger contribution could lie.** These are research targets, not verified gaps or completed results:

- Retain geometry of general weighted graphs in both upper and lower bounds. Show a separation from methods that compress each component to one diameter, and obtain a computable allocation that attains the new bound. Applying an existing structured-bandit framework alone is unlikely to be enough.
- Analyze the original finite-strength spectral index, including its bias under unequal adaptive sampling. A regret theorem for a meaningful class of ordinally aligned graphs would connect more directly to the original selection papers than the infinite-smoothing limit does.
- Specify a restricted model of uncertain or incorrect graph information and quantify the cost of validating, rejecting, or repairing it. Prove both an achievable regret guarantee and a matching obstruction. Compare against misspecified GP bandits, gap-adjusted linear bandits, Clus-UCB's width discussion, and graph-residual bounds before claiming novelty.

A defensible description of the current draft is: **“A certificate-based spectral pooling analysis that translates graph energy into finite-time regret bounds and evaluates a structured information lower bound for homogeneous Gaussian cliques.”** A stronger paper would establish a graph-dependent result that existing width-based or spectral analyses do not already imply.
