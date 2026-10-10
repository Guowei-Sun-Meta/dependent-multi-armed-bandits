# Experiment design: learning from persistent, correlated Web rewards

9 October 2026. Target: The Web Conference 2027 research track. This is an executable study specification, not a report of completed application experiments. The only new results accompanying it are the [local data audit](../research/st_applications/results/feasibility/findings.md).

**Recommendation.** Use budgeted Web-attention monitoring as the main application, Wikipedia page views and a historical clickstream graph as the main new dataset, and KuaiRec daily engagement as a smaller exploratory replication. Keep the existing graph-alignment results as evidence about when pooling fails. Use simulations on the same Web graphs to measure genuine stationary mean regret and probability of correct selection (PCS). Separate evidence about temporal prediction from evidence about the graph's incremental value.

The scientific question is: **when does a Web graph make a costly observation useful beyond its own item and beyond the current day, and how should an online learner act on that information?** This is more precise than claiming a new general combination of spatial and temporal bandits.

The [official call](https://www2027.thewebconf.org/research-track-papers/) requires explicit Web relevance on page 1. Long papers have eight main-text pages and at most twelve pages including references and appendix. Abstract and paper deadlines are 18 and 25 October 2026, AoE; [official dates](https://www2027.thewebconf.org/important-dates/). The existing merged-paper proposal remains in [CLAUDE.md](CLAUDE.md). This document supplies its empirical protocol; it does not certify the unfinished bridging theorems.

## 1. What the repository actually contains

The scan covered the repository's research notes, manuscript sources, application plans, experiment implementations, result summaries, and local data inventory. Generated PDFs and raw tables were inspected through their sources or metadata rather than rereading every generated artifact.

| Stream | Available evidence | Role in this study |
| --- | --- | --- |
| [Graph alignment](../research/alignment_paper/README.md), [novelty audit](../research/alignment_paper/novelty_audit.md) | Fixed-mean theory, resistance geometry, certificate and corruption simulations | Explain why a graph must be tested for the particular decision target |
| [KuaiRec graphs](../research/kuairec_graphs/README.md); `experiments/kuairec/` | Static item/user experiments, graph diagnostics, a daily policy pilot; raw data are local | Immediate application replication and useful negative evidence about graph benefit |
| [Correlated-arms theory map](../research/correlated_arms/README.md) | Proposed bridge between pooling and innovation regression | Candidate unified-paper theory; requires independent proof review |
| [Predictive AR(1)](../research/predictive_ar1/README.md), [two-arm](../research/two_arm_ar1/README.md), [general AR](../research/ar_p_bandits/README.md) | Timing, contrasts, information lifetime, short-horizon control | Interpret decisions; general AR remains the main model |
| [Fixed-mean spatial/general-AR paper](../research/spatiotemporal_bandits/README.md), [policies](../research/spatiotemporal_bandits/policies.md) | Joint likelihood, mean UCB/TS, predictable-state UCB/TS, contrast allocation, fixed-truth AR(20) results | Primary algorithm and simulation implementation |
| [Other toy benchmark](../research/st_toy/README.md), `experiments/st_toy/` | Alternative filters and two-period policies | Secondary implementation check. Its random-mean population is a different experiment and must be labelled separately |
| [Earlier application sketches](st_applications.md), [static KuaiRec plan](kuairec_experiment_plan.md), [short-paper fallback](st_short_paper.md) | Application candidates and venue positioning | Navigation and historical context, superseded by this protocol for temporal evaluation |

No Wikipedia, Yahoo!, taxi, Spotify, M5 or RIPE Atlas reward panel was found locally. Feasibility of those scenarios is based on documented public sources, not completed downloads or policy results.

### Problems the scan uncovered

1. **The existing daily pilot has weak incremental graph evidence.** Averaging the three origins, ST greedy has oracle regret 2.411/day versus 2.436 for AR-only greedy, a 1.01% difference. Graph, rewired and common-factor sampling are also close. These are descriptive pilot results, not independent confirmation of a graph advantage.
2. **Pair-disjoint is insufficient for temporal evaluation.** The static graph cache correctly excludes evaluation user–video pairs, but `graphs.py` uses interactions from the entire time range. For the first daily cutoff, 1 August 2020, 8,127,889 of its 10,272,525 item-side input rows are later than the cutoff: **79.1%**. The other cutoffs still include 34.9% and 24.9% later rows. Rebuild graphs chronologically.
3. **A recorded row does not always mean observed quality.** KuaiRec has 343,341 video-days, 10,728 videos and 63 days. The 253-video complete-by-presence evaluation cohort contains six zero-play cells on two videos. Pseudocounts produce a finite logit at zero plays but supply no information about completion probability.
4. **The existing origins overlap.** Prefix lengths 28, 35 and 42 reuse test days and the same videos. Random seeds repeat algorithmic randomness on one observed field; they do not create new independent Web worlds.
5. **A short aggregate panel does not reveal permanent means.** A test-window average is not the fixed latent mean, and a covariance fitted from it does not establish a theoretical regret floor. At a 28-day prefix, a dense AR(20) leaves only eight innovation dates. Even the existing sparse lag-7 fit has at most twenty centered covariance directions for 253 arms.
6. **The two implementations use different sampling rules.** KuaiRec `st_ps` samples uncertainty in permanent means and conditions deviations on it. The fixed-mean AR(20) `joint_predictive_ts` samples all predictable reward uncertainty after removing fresh innovations. Past-state uncertainty remains in the latter. They must have different labels in a comparison.

The reproducible [audit JSON](../research/st_applications/results/feasibility/kuairec_audit.json) records input hashes, counts and training-only AR diagnostics. No old result files or cached graphs were changed.

## 2. Application and objective

### Main use case: budgeted attention monitoring and opportunity selection

A publisher, search analyst or content service can inspect a limited number of topics or items each day. Inspection reveals the current demand or engagement statistic and produces an attention-weighted opportunity: an analysis report, content review or follow-up opportunity. Neighbouring topics may share a news shock; the shock can persist into future days. A useful policy should exploit high predicted demand while choosing observations that improve later decisions.

This is a **selective-observation emulation**. Public page views are inexpensive to obtain, so the experiment does not demonstrate a production cost saving. The budget represents a proposed expensive downstream inspection or fine-grained metric unavailable for all candidates. Report this distinction explicitly. An eventual deployment must measure that cost and validate the utility proxy.

We evaluate the exogenous recorded demand of selected arms. We do not interpret page views as incremental clicks caused by promotion, completion rates as causal video quality, or taxi pickups as realized driver earnings. Those effects require a different causal or controlled system model.

Two tasks share the same inference engine but use different policies:

| Task | Decision | Main endpoint | Ground truth |
| --- | --- | --- | --- |
| Repeated opportunity selection | Select one arm, or a simultaneous batch of b distinct arms, before today's field is revealed | Current-field oracle regret per slot | Fully observed evaluation panel; learner receives only selected coordinates |
| Permanent opportunity identification | Spend a fixed observation budget, then recommend the best permanent mean | PCS and simple regret | Controlled fixed-mean simulation only |

Real data can additionally support **future-window selection**: recommend the item with highest average demand over a reserved future interval. Call its success a future-window hit rate, not PCS for a stationary mean. It is a different target, with a finite future window and genuine drift.

## 3. Model and algorithms carried over from the theory

For N arms, use the user's fixed-mean model:

```math
X_{i,t}=s_i(t)+\mu_i+z_{i,t},\qquad
z_{i,t}=\sum_{r=1}^{p_i}a_{i,r}z_{i,t-r}+\eta_{i,t},\qquad
\eta_t\sim N(0,Q_\eta),\qquad Y_{i,t}=X_{i,t}+\xi_{i,t}.
```

Here μ is fixed, not drawn afresh between noise replicates. Each arm evolves on calendar time. The deterministic seasonal term s_i(t), if used, is fitted on historical data and is known at decision time. Use general AR(p_i); AR(1) is just an ablation. State exactly whether X means the observed aggregate signal or a latent expectation: the real-panel primary endpoint uses the **observed aggregate signal**, whose latent noise components cannot be separated from that panel alone.

Keep two graph roles separate:

- **L_μ:** optional deterministic regularization of fixed means, H = αI + λ_μL_μ. A valid supplied energy radius is an additional assumption in certified theory. An observed estimate of smoothness is not a certificate of the unknown truth.
- **L_η:** covariance structure for shared shocks. Spatially correlated innovations do not imply that μ is smooth. Start the main temporal comparison with λ_μ = 0, then test mean regularization separately.

For fitted real-data covariance, one candidate family is

```math
Q_\eta=D\left[(1-w)\{(1-\rho)K_{G,\gamma}+\rho\mathbf1\mathbf1^\top\}
             +w\widehat C_{\rm residual}+\epsilon I\right]D,
\qquad K_{G,\gamma}=\operatorname{corr}\{(I+\gamma L_\eta)^{-1}\}.
```

D supplies arm-specific innovation scales; renormalize the correlation diagonal before applying D. ε > 0 ensures positive definiteness. Estimate every term on the training prefix. Compare with diagonal, common-factor, and graph-free shrinkage covariance at matched tuning effort. A graph kernel assumes positive local association; signed or strongly delayed cross-arm dependence is a model limitation to diagnose, not silently discard.

The joint filter yields mean estimate m_t, mean uncertainty V_t, current forecast f_t and predictive covariance Σ_t. The following rules use the same history and fit:

```math
\begin{array}{ll}
\text{Mean UCB:}&\arg\max_i\{m_{i,t}+c_t\sqrt{V_{ii,t}}\};\\
\text{Mean TS:}&\widetilde\mu\sim N(m_t,V_t),\quad\arg\max_i\widetilde\mu_i;\\
\text{Predictable-state UCB:}&\arg\max_i\{f_{i,t}+c_t\sqrt{(\Sigma_t-Q_\eta)_{ii}}\};\\
\text{Predictable-state TS:}&\widetilde f\sim N(f_t,\Sigma_t-Q_\eta),\quad\arg\max_i\widetilde f_i.
\end{array}
```

Subtract fresh innovation covariance, not sensor noise or all state uncertainty. Under the correct Gaussian model Σ_t − Q_η is positive semidefinite; symmetrize and tolerate roundoff only. A material negative eigenvalue is a failed implementation/model check. Practical UCB bonuses are selected on development data; the certified mean-UCB bonus is reported separately because it assumes correct known parameters and valid bounds. No new learned-parameter confidence theorem is implied.

For mean identification, reuse contrast LUCB and top-two Thompson contrast sampling. With a current estimated winner b and plausible challenger j, choose the observation maximizing the reduction in variance of μ_b − μ_j, which may be a third arm. Recommend argmax m_T, not the largest last reward. See [policy definitions](../research/spatiotemporal_bandits/policies.md).

For b > 1, select the entire batch before any same-time observation. UCB/TS takes the top b scores without replacement; contrast allocation updates its *anticipated covariance* after each batch inclusion but receives no intermediate outcomes. Assimilating simultaneous readings one at a time is mathematically fine after selection. A cascade click model is a different problem and is excluded.

## 4. Datasets and chronological protocol

### A. Wikipedia: main new real-data study

Use the [Wikimedia per-article page-view service](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html), English Wikipedia, all access methods, human `user` traffic, daily resolution. Retain raw JSON responses, request specifications and hashes. Graph source: [Wikipedia clickstream](https://meta.wikimedia.org/wiki/Research:Wikipedia_clickstream), specifically the archived [September 2023 English dump](https://dumps.wikimedia.org/other/clickstream/2023-09/). Clickstream is a weighted navigation graph with low-count transitions removed; missing edges do not establish independence.

**Fixed dates and population.** Use 2024 for fitting/development and 2025 for untouched evaluation. Select twelve disjoint 100-article topical panels using the September 2023 graph and 2024 training coverage, with a fixed seed and a released title manifest. Pick a diverse seed-topic list before retrieving 2025 values; choose communities by graph connectivity and minimum 2024 coverage, not by measured test-time benefit. Do not select only trending pages, only high test volatility, or only graphs that beat a rewiring. Also release a popularity-stratified mixed panel as a stress test.

**Dates.** Test origins are 1 January, 1 April, 1 July and 1 October 2025; use 90 days from each, without overlapping test dates. Fit each episode on its preceding 180-day full-history window, after hyperparameters have been frozen on 2024 development episodes. Hyperparameters never use 2025 results. Episode-specific parameter fits may use history before their origin, including earlier quarters, as an explicitly disclosed full-history initialization privilege. These episodes are not a single continuously hidden online deployment. Report full-history fitting costs and compare with a second protocol fitted only on 2024, with no full-panel refresh during 2025.

**Two initialization conditions.** The main mature-catalog condition lets all methods see the same prefix. A secondary cold-monitoring condition transfers dynamics from development panels but reveals only a paid initial probe sweep on the new panel. Do not compare a fully initialized ST learner with an uninitialized iid baseline. Include fit-window exposure in total-cost reporting; online regret begins after the disclosed fit window.

**Graph chronology.** Freeze the September 2023 navigation graph for the primary study. Symmetrize article-to-article transition counts, use log(1 + count) weights, and build the union kNN graph using k ∈ {5, 10, 20} selected on development data. Preserve isolated nodes. Exclude external and aggregate referrer nodes. A graph-update sensitivity may use only releases demonstrably available before the episode; clickstream release delays make “previous month” insufficient. Record publication/availability evidence. Do not join through current redirects or current categories without documenting their historical status; keep original titles and audit renames, ambiguous joins and non-article pages.

**Signals.** Main utility is log(1 + daily views), using a common training-derived affine scale across arms if numerical scaling is needed. Per-arm reward standardization changes the ranking task and is excluded. Fit weekday effects on training data; add them back for current-demand decisions and original-scale reporting. Report raw-view opportunity regret as a secondary scale, not as a causal promotion gain. The best transformed long-run mean can differ from the best raw-count mean.

**Missingness.** Distinguish an API failure or absent record from a documented zero. Retry transient failures under the API policy. Never replace arbitrary missing observations with zero. Publish coverage and all excluded instances under a predefined data-validity rule; report sensitivity to those exclusions. If counterfactual test rewards cannot be recovered, that episode cannot supply an exact full-field oracle endpoint. Neither the learner nor its graph builder can read future availability when deciding.

**Budgets.** N = 100; b ∈ {1, 5, 10} simultaneous observations per day; T = 90 days. Repeat stochastic policies with twenty fixed seeds per episode. These seeds estimate Monte Carlo uncertainty on a fixed observed field, not twenty independent datasets. The one-arm case is the primary theoretical match. Include b/N and training exposure in every table.

### B. KuaiRec: immediate exploratory replication

Use the local [KuaiRec daily table](https://github.com/chongminggao/KuaiRec), not the nearly complete static user–video matrix as a time-series panel. The raw daily range is 5 July–5 September 2020. The existing daily pilot has already been inspected; the full dataset therefore remains exploratory rather than a new confirmatory holdout.

For an **exact retrospective panel diagnostic**, use the 251 evaluation videos with a row and positive plays on every date, explicitly conditioning on their future survival. Freeze three seeded 100-video subsets from that declared population before new policy comparisons. This conditions the target catalog on hindsight and cannot establish effectiveness for a live catalog with item deaths. Report that selection next to the results.

Use days 1–21 for fitting, 22–35 for development, and 36–63 for the comparison. Refit parameters on days 1–35 after tuning, with no later outcomes. Rebuild I-coeng from non-evaluation-user interactions **dated on or before the relevant fit cutoff**; re-estimate IDF and any embeddings on that same prefix. Rebuild the development graph at day 21 and the final pilot graph at day 35. Creator identity can be taken from prefix daily records; undated side-information remains a separately labelled retrospective sensitivity. Existing `node_features.pkl` and `daily_filters/` caches must not be reused without cutoff-aware fingerprints.

The prefix-realistic cohort is a separate **availability audit**, not an exact oracle comparison on invented missing rates: the ≥10 plays/day rule on the first 28 days yields 255 eligible videos, then thirteen missing and seven zero-play test cells. Do not turn these unknown completion rates into 0.5 through smoothing and call them ground truth.

Reward: complete_play_cnt / play_cnt; logit((complete_play_cnt + 0.5)/(play_cnt + 1)) for Gaussian fitting. The rate is conditional on the logged audience/exposure policy. Start with exact observed aggregates as feedback, without added sensor noise. If testing sampling noise, independently subsample plays under a labelled binomial approximation and vary observation budget. A count-derived variance such as 1/(complete + 0.5) + 1/(play − complete + 0.5) is only known after inspecting that arm; do not leak all current play counts into decisions. Repeated plays can violate the binomial model, so keep it a sensitivity.

Use b ∈ {1, 5, 10}; T = 28 days, no forced 100-round warm-up that consumes the whole test. Historical initialization supplies coverage; cold-start variants use a paid sweep spread across days and charge its regret. Fit pooled sparse AR lags {1, 2, 7}, with order selection on development data. General AR is supported, but dense per-arm AR(20) is not a credible fitted primary model on 63 dates. Keep it in the controlled study.

### C. Web-graph simulations: exact means, PCS and regret floor

Retain the [existing fixed-truth 100-arm AR(20) benchmark](../research/spatiotemporal_bandits/results/policies_ar20/findings.md) as a reference, but it uses a grid. Add simulations on the frozen Wikipedia and chronological KuaiRec graphs, with parameters calibrated only on their development prefixes.

Hold each mean vector fixed across independent innovation and sensor-noise draws. Include three predefined gap profiles: the unmodified training-derived means, a small-gap variant and a heterogeneous-mean variant. Report each; do not retain only favorable graph-smooth cases. Perturb gaps deterministically once, before noise replication, and publish the vectors. Use mean graphs and innovation graphs independently.

| Factor | Values / purpose |
| --- | --- |
| Arms | 100 primary; 50, 300 scaling sensitivity |
| AR order | 20 primary; 1, 2, 7 comparisons; heterogeneous p_i ∈ {2, 7, 20} |
| Temporal profile | iid; weak dense; persistent dense; lag-20 seasonal; heterogeneous/oscillatory |
| Spatial innovation strength | diagonal; medium; strong, with covariance matrices recorded |
| Graph mismatch | fixed truth, learner graph with 0%, 25%, 50%, 100% degree-preserving rewiring; no oracle repair |
| Mean regularization | λ_μ = 0 primary temporal comparison; trained graph penalty; oracle-valid certified bound separately labelled |
| Horizons / batches | T ∈ {250, 1000, 4000}; b = 1 primary, b = 5 sensitivity |
| Noise worlds | 100 paired worlds for primary cells; twenty for exploratory sweeps |
| Parameters | known-correct; learned from independent prefix; underfit order/covariance |

Use a staged factor design rather than the full Cartesian product. Primary cells cross three temporal profiles with three spatial strengths, N = 100, p = 20, T = 1000, b = 1. Heterogeneous orders, mismatch, scaling and horizon sweeps are separate one-factor studies. Normalize stationary marginal variance in the main persistence sweep, and separately hold innovation variance fixed: these answer different questions.

PCS is evaluated at budgets T ∈ {250, 1000, 4000}, with exactly bT paid observations and the same positive-gap fixed truth. Report simple regret as well; near ties can make PCS look poor despite small opportunity loss. Learning μ from a simulation calibration prefix is allowed only under the disclosed mature-catalog condition. Include a cold condition with no direct prior measurements of the test μ.

## 5. Baselines and ablations

### Mandatory comparison families

| Family | Methods | Why needed |
| --- | --- | --- |
| Static / simple | Fit-window ranking, last-observed value, round robin | Strong sanity checks; greedy already wins the short KuaiRec pilot |
| iid | Variance-matched Gaussian UCB and TS | Avoid the old UCB σ = 0.5 handicap; KL-UCB only on actual bounded/Bernoulli tasks |
| Adaptive nonstationary | Sliding-window UCB, discounted TS, EXP3.S or another documented switching comparator | Test whether exploiting AR structure beats generic forgetting |
| Temporal only | Independent AR greedy, state UCB/TS, predictable-state UCB/TS | Hold mean estimator, priors, fit and decision rule fixed while removing off-diagonal Q |
| Spatial only | Graph-regularized mean UCB/TS, with joint covariance draws | Test if static pooling accounts for the gain |
| Spatiotemporal | Joint greedy; full-state UCB/TS; predictable-state UCB/TS | Main proposed policies; isolate exploration of fresh shocks |
| Graph-free correlated | Common-factor + diagonal filter; shrinkage/factor covariance fitted without graph | A real graph must add value beyond ordinary shrinkage and global attention shocks |
| Closest published | TV-GP-UCB; Chen et al. AR2-p; LARL for the latent-factor setting | Address overlap with established space-time and AR bandits |
| Pure exploration | Equal allocation, independent-AR LUCB/top-two, joint contrast LUCB/top-two, static graph elimination | PCS comparisons are separate from online opportunity regret |

Credit [time-varying GP bandits](https://proceedings.mlr.press/v51/bogunovic16.html), [predictive sampling](https://proceedings.mlr.press/v206/liu23e.html), [linear-Gaussian restless bandits](https://proceedings.mlr.press/v242/gornet24a.html), [AR2 and its AR-p extension](https://proceedings.neurips.cc/paper_files/paper/2023/hash/186a213d720568b31f9b59c085a23e5a-Abstract.html), and [LARL](https://rlj.cs.umass.edu/2025/papers/RLJ_RLC_2025_70.pdf). An unknown-prior GP comparator is [PE-GP-UCB](https://proceedings.mlr.press/v258/ziomek25a.html). Do not claim first use of joint spatial/temporal filtering. Graphs here describe statistical dependence, not free observation of all neighbours as in [feedback-graph bandits](https://proceedings.mlr.press/v40/Alon15.html).

Implement published methods from authors' code or pseudocode, record versions, and document adaptations. AR2-p is the appropriate general-AR comparison; its published theorem does not automatically cover our correlated innovations. LARL assumes a shared latent factor, so use a matched factor experiment or disclose the representation approximation. Missing mandatory implementations are a submission gap, not evidence that the simpler baselines are sufficient.

### Tuning and attribution

Freeze hyperparameters before evaluation. Give each family at most twelve development configurations and the same development observation budget; publish grids, compute and the selected configuration. Practical UCB multipliers can range over {0.5, 1, 2, 4}; TS perturbation scales over {0.5, 1, 2}. Fit-window data and initialization are shared. Use separate development objectives for regret and identification.

For covariance/order fitting, use blocked forward validation within each prefix. Recompute centering, weekday effects, AR coefficients and graph features inside each inner training fold. The current `daily.py` first fits AR on the entire prefix then validates residual covariance on its final days; that is not a clean end-to-end validation fold. Check companion spectral radius and reject or explicitly constrain unstable fits before using stationary initialization. Do not silently halve coefficients until the model appears stable.

Run the following attribution tests, using paired fields and the same exploration rule:

1. **Spatial × temporal 2 × 2:** both off, mean graph only, AR only, AR + innovation graph. Additionally compare λ_μ = 0 against positive λ_μ with the innovation graph fixed.
2. **Graph nulls:** the real graph, ten degree-preserving rewirings, diagonal Q, common factor, graph-free covariance shrinkage. Re-estimate nuisance scales on the same prefix; use the same tuning budget and disclose any retuning. Real-versus-rewired differences test information in topology, not merely regularization.
3. **Predictable versus fresh uncertainty:** Σ versus Σ − Q, plus the old mean-only `st_ps` rule, using distinct names.
4. **Observation age and lag:** forecast/contrast errors by time since the last observation, AR(1) versus seasonal/general/heterogeneous AR, and a lag-20 case where next-day prediction misses delayed value.
5. **Known versus fitted parameters:** independent-prefix estimates, reduced prefix lengths, wrong order, covariance perturbation, and heavy-tailed/count innovations. Test-time full-field fits appear only as explicitly privileged diagnostic comparators, never as a deployable variant.
6. **Nonstationary permanent quality:** inject mean drift and compare a local-level/change-aware baseline. This is outside the fixed-μ theorem; do not quietly modify μ and reuse the stationary guarantee.

## 6. Benchmarks and metrics with valid meanings

For a simultaneous b-arm batch, let S_t be its chosen set and Top_b(X_t) the b highest current latent rewards in a simulation or observed signals in a real panel.

```math
R_{\rm current}(T)=\sum_t\left[\sum_{i\in\mathrm{Top}_b(X_t)}X_{i,t}
                                           -\sum_{i\in S_t}X_{i,t}\right],
\qquad
R_\mu(T)=\sum_t\left[\sum_{i\in\mathrm{Top}_b(\mu)}\mu_i
                                           -\sum_{i\in S_t}\mu_i\right].
```

Report both divided by bT. R_current and R_μ are nonnegative. Also report actual reward relative to always choosing the best-mean batch on the same realized path; it can be negative when tracking useful fluctuations. On real data, only the first comparator is exact. A fixed hindsight best batch is a separate descriptive comparator, not a stationary mean oracle.

In a stationary, known Gaussian simulation with s_i(t) = 0, define

```math
\mathcal G_b(\mu,K)=\mathbb E\sum_{i\in\mathrm{Top}_b(\mu+Z)}(\mu_i+Z_i),\qquad Z\sim N(0,K),
\qquad c_{\rm innov}=\mathcal G_b(\mu,G_0)-\mathcal G_b(\mu,G_0-Q_\eta).
```

This is the expected per-day regret of the genie knowing μ and the full past lag state. It lower-bounds causal regret against the current-state oracle under the stated model. It is not a pathwise floor and is generally unattainable under restricted readings. Divide by b for the per-slot coefficient. Estimate it with independent paired Gaussian Monte Carlo and report its numerical uncertainty. For nonzero known seasonality, compute the corresponding time-specific expression or keep floor experiments deseasonalized.

Report learner excess above this floor and, optionally, (R_baseline − R_policy)/(R_baseline − Tc_innov) on matched stationary simulations with a positive denominator. Do not fit a floor to drifting real data and advertise a fraction of an achievable optimum. A known-mean greedy filter is a useful benchmark but not the optimal causal policy. State-oracle reward is zero regret by construction and is never available to the learner.

For identification, PCS = Pr(recommended arm = argmax μ) over independent noise worlds with the same fixed truth. Report Wilson intervals, expected simple regret and pairwise contrast errors. Optional fixed-confidence stopping requires correct known dynamics and supplied valid bounds; learned-model stopping reports empirical coverage rather than a guaranteed δ.

Operational reporting: captured observed demand/rate, per-slot current regret, top-b overlap, raw-scale opportunity loss, number and age of observations, and computation/memory. Prediction reporting: held-out predictive log score, error, interval coverage and graph-neighbour versus non-neighbour residual dependence. A policy that improves a forecast but not decisions has not answered the online-learning question.

## 7. Statistical design and feasibility gates

**Synthetic uncertainty:** paired independent worlds, shared fixed μ, innovation paths and potential measurement noises; policy RNG is separate. One world is the unit for paired regret differences. Use 100 primary worlds: at PCS = 0.8 this still gives roughly ±0.08 uncertainty, so avoid fine-grained optimality claims. Use Wilson intervals for PCS; paired differences for policy comparisons.

**Real-data uncertainty:** first average stochastic repeats within each topic-panel/origin. Release these per-instance values. Resample topic panels and global calendar blocks jointly as a sensitivity to cross-panel and temporal dependence; use block length selected from development autocorrelation, and preserve paired policy comparisons. These intervals are approximate because topics can share global shocks. Report distributions and origin-level differences alongside them; do not multiply the sample size by seeds, overlap, arms or days. KuaiRec's three subsets share one short field and primarily supply descriptive evidence.

Predeclare two primary superiority comparisons: joint predictable-state TS versus temporal-only predictable-state TS, and joint predictable-state UCB versus its temporal-only match, on the b = 1 Wikipedia aggregate endpoint. Use Holm correction across these two comparisons. Against graph-free covariance and rewirings, report paired effect sizes and intervals; additional panels/budgets are secondary. Rank or percentage summaries alone are insufficient. A useful effect threshold is a preregistered 5% relative regret improvement; report intervals and null/negative results whether or not it is reached.

**Development gates, decided before untouched evaluation:**

| Gate | Check | Consequence |
| --- | --- | --- |
| Usable panel | At least eight of twelve planned Wikipedia panels have recoverable test fields and valid historical joins | Otherwise narrow scope, report exclusions and do not present large-scale generality |
| Predictability | AR improves forward-validation score over seasonal/static and simple forgetting models | If not, report the weak-persistence regime; do not force an AR story |
| Incremental graph information | Real graph improves validation score/contrast prediction beyond common-factor and graph-free shrinkage | If absent, keep it as a negative case; any spatial-benefit headline needs another predefined dataset or must be narrowed |
| Stable inference | Positive definite Q, stable transition, likelihood conditioning checks, calibrated prediction diagnostics | Failure blocks that model configuration, not publication of the failure |
| Cost feasibility | Prototype N = 100 within 1 GB and median decision latency under 1 s on the available laptop | Measure before expanding; document approximation when required |
| Claim consistency | Real-data means/floors not called true; known-parameter and fitted results distinguished | Mandatory before writing abstract claims |

Failure does not authorize searching test data for a more flattering graph or window. Freeze amendments, state why they were made, and distinguish exploratory from confirmatory results.

## 8. Implementation and resource plan

Use `experiments/st_apps/` for a new shared harness; preserve the existing research scripts and results. Planned result roots are `research/st_applications/results/{feasibility,wikipedia,kuairec_corrected,webgraph_simulation}/`. A smaller Wikipedia experiment has now been executed under [research/gpt_sol_10_09](../research/gpt_sol_10_09/README.md), using two 24-article panels and pre-2024 hyperlink graphs. Its [protocol](../research/gpt_sol_10_09/experiment_design.md) and [completed findings](../research/gpt_sol_10_09/results/wikipedia/findings.md) describe the actual run; the twelve-panel clickstream study above remains a proposal.

| Module | Required behavior | Status |
| --- | --- | --- |
| `audit_kuairec.py` | Count validation, prefix eligibility, streamed chronology audit, source hashes | Implemented and run with this design |
| Dataset loaders / manifests | Frozen IDs, explicit missing masks, date and graph provenance; Wikimedia acquisition/cache | Planned |
| Fitting | Forward blocked validation, stable AR, graph/factor covariance, training-only preprocessing | Planned |
| Policy adapters | Reuse fixed-mean likelihood/filter semantics; observed-only API; simultaneous batches | Planned |
| Runner | Separate hidden evaluation panel from learner observations; paired seeds; append-only run records | Planned |
| Analysis | Objectives separated, cluster-aware summaries, raw-scale metrics, figures | Planned |

Do not launch the full matrix before measuring a one-panel timing pilot. The exact selected-history implementation stores O(B² + N²) covariance information for B recorded observations and has growing per-decision work. The augmented lag-state implementation stores O([N(p+1)]²): at N = 100, p = 20, one double covariance alone is about 35 MB, before work arrays; at N = 1000 it is about 3.5 GB. Sparse lag sets do **not** reduce the largest retained lag to the number of nonzero coefficients. Low-rank/factor approximations need their own dense-reference accuracy check.

Cache fits and deterministic policy runs by input hash, exact date cutoff, selected IDs, lag configuration, preprocessing and covariance settings. Only stochastic policies need repeated RNG seeds; count-derived feedback simulations introduce separately recorded measurement seeds. Start with one BLAS thread and two workers on the 8 GB machine. Record actual runtime and memory; no unsupported “two-hour full study” estimate.

Minimum scientific checks before policy experiments: filter versus dense Gaussian conditioning on a small heterogeneous-AR model; mean and forecast covariance orientation; Σ − Q positivity; batch selection before observations; no reads of future fields or availability in learner code; exact observation counts; graph cutoff assertions; correct raw/transformed endpoints; reproduce one run from its manifest. These validate scientific assumptions rather than mirroring implementation details.

## 9. What belongs in the WWW paper

The contribution should connect **a specific Web decision** with information that persists across its navigation/co-engagement graph. Established filters and graph kernels are tools. The candidate incremental contribution is objective-specific sampling with separately tested mean and shock graphs, plus a reproducible account of when real Web topology improves or fails to improve decisions. Any new certified-pooling bridge is an additional theorem only after its conditions and proof are checked.

Suggested first-page framing: “Web attention shifts across related content while measurements are selectively available. An inspection can reveal a local attention shock and improve later choices, but a graph that groups long-run preferences need not predict those shocks. We study when navigation and co-engagement graphs improve budgeted opportunity selection and permanent-quality identification.”

Recommended track for the monitoring study: **Web Mining, Multimedia and Multilingual Content Analysis**, whose scope includes Web traffic and log analysis. If the merged paper retains a genuinely recommendation-specific task and theory, the existing Search, Recommendation, and Retrieval-Augmented AI positioning remains reasonable; explicitly explain the exogenous-demand limitation. Dataset use alone is insufficient Web relevance.

For the eight-page main text, reserve approximately 0.75 page for motivation/Web relevance, 0.75 for model/objectives, 1.5 for policies/theory, 0.75 for related work, 1 for design, 2.5 for results, and 0.75 for limitations/conclusion. Allocate the four remaining total pages between references, essential proofs and reproducibility; lengthy existing proofs cannot all fit in a twelve-page submission.

Five main exhibits:

1. Data/topology diagnostics: temporal predictability and real-graph information beyond common factors.
2. Matched policy results: ST versus temporal-only, spatial-only and graph-free shrinkage.
3. Spatial-strength × temporal-profile controlled simulation, with the theoretical floor.
4. Graph mismatch and fresh-versus-predictable exploration ablations.
5. PCS/simple-regret curves with fixed truth and observation cost; raw-scale and runtime detail in the appendix.

For the current merged long paper, prioritize the corrected KuaiRec pilot, existing static alignment/certificate evidence, and one complete Web-graph simulation. Wikipedia can support a stronger application-centered version if its acquisition and diagnostics are ready. It is not mandatory to squeeze both real panels and every theorem into eight pages. If Wikipedia is deferred, narrow the submission's empirical graph-benefit claims to what the other data actually supports.

## 10. Work before the deadlines

| Date | Concrete deliverable | Decision |
| --- | --- | --- |
| 9–11 October | Freeze design; chronological KuaiRec graphs; small adapter timing/conditioning checks; acquire Wikipedia development data | Establish costs and data availability |
| 12–14 October | Development diagnostics, mandatory baseline adapters, stable fits and registered parameter choices | Fix main scope; graph benefit remains a hypothesis |
| 15–17 October | Corrected pilot and controlled primary runs; untouched Wikipedia runs if ready; analysis artifacts | Abstract uses only supported statements |
| 18 October | Reviewable abstract and final author list | User handles submission; no publication action is implied by this task |
| 19–20 October | Proof review of the bridge; empirical results and uncertainty; narrow claims where needed | Retain the repo's merged-paper go/no-go |
| 21–25 October | Eight-page self-contained paper, at most twelve total pages, anonymous reproducibility package | Submit only after human review |

This plan cannot guarantee acceptance or empirical superiority. It makes the question, comparator information, missingness, chronology, algorithm provenance and achievable deliverables reviewable. The honest present conclusion is that persistence is promising, while the added value of Web topology remains a measurable research question.
