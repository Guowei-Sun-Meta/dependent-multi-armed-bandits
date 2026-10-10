# Recommended spatiotemporal bandit experiments

Date: 10 October 2026. Status: researched designs and access checks, not five newly executed benchmarks. This plan consolidates the five recommended application studies and their shared validation protocol. It is adapted from the [dated research note](../research/gpt_sol_10_09/application_options_10_10.md).

## Recommendation and the three gaps

Use Wikipedia and KuaiRec as strengthened existing studies, and add Retailrocket catalogue demand, RIPE Atlas DNS monitoring, and Open Bandit Dataset fashion recommendation. Retailrocket is the first new experiment to implement; RIPE supplies the clearest genuine measurement-budget motivation. Open Bandit Dataset adds actual partial click feedback but requires the most care in evaluation and observation modelling.

The three gaps addressed here are:

1. **Separate spatial and temporal effects.** Vary persistence and innovation dependence independently, hold the reward-generating process fixed while corrupting the learner's graph, and compare matched temporal-only and common-factor controls.
2. **Broaden the evidence.** Use multiple mean configurations, panels, time windows, budgets, graph qualities, and model specifications. Increase independent simulation worlds for primary PCS comparisons.
3. **Make application evaluation chronological and defensible.** Construct graphs and eligibility rules from a training prefix; freeze tuning before test; account for initialization observations; distinguish observed-field benchmarks from logged-feedback evaluation.

The [WWW 2027 research call](https://www2027.thewebconf.org/research-track-papers/) explicitly includes recommendation, graph modelling, Web mining, and Web infrastructure. It also requires a scientific challenge specific to the Web: downloading Web data alone does not establish relevance. The applications below fit those research areas, but no dataset or application guarantees acceptance.

## 1. Wikipedia: budgeted article refresh and attention monitoring

**Decision.** Select one or five articles per day for inspection or refresh, using attention as a proxy for the value of allocating a limited monitoring budget. Arms are articles; the recorded reward is `log1p(human page views)`. This is an exogenous attention opportunity benchmark, not a measured causal effect of refreshing or promoting an article.

**Graph and dynamics.** Use direct hyperlinks reconstructed from revisions before evaluation, optionally compared with an available pre-period clickstream graph. Fit stable AR models with weekly lags, and distinguish a global shock from community-specific innovations. Any extra physical smoothness restriction on fixed means needs separate justification.

**Concrete scope.** Predefine 8–12 panels of 32–64 articles from several topical communities; retain the existing panels and their null graph findings. Fit and tune on 2024, then use disjoint 90-day windows in 2025. Primary orders are 7 with selected lags; AR(20) is a sensitivity on a subset. Count all initial full-history readings separately. A rolling restart with additional full-field history and a continuously masked year are different protocols and must be reported separately.

**What this adds.** Test whether graphs help specifically when innovations have community structure and leading articles are close in value, instead of simply when a common factor is present. Include limited-history initialization and seasonal/last-value baselines. Evaluate graph quality on held-out innovations after removing common shocks. Do not retain only communities where a graph wins.

**Targets.** Observed daily-field oracle loss and its average coefficient, attention captured, and terminal finite-window ranking accuracy. True permanent-mean PCS belongs to the calibrated simulations.

**Readiness.** Existing experiments and caches are available: the dated compilation contains two 24-article panels, and the live [Wikipedia report](wikipedia/README.md) contains separate one-domain and six-community studies. These are distinct protocols and should not be pooled as interchangeable replications. Sources: [Wikimedia page-view API](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html), [historical revision API](https://www.mediawiki.org/wiki/API:Revisions).

## 2. KuaiRec: monitoring short-video engagement under a daily budget

**Decision.** Select videos to inspect or shortlist using their evolving aggregate engagement. Use a documented daily aggregate with positive play counts, such as completion rate; distinguish a monitoring objective from personalized recommendation lift. Arms are videos, with noisy daily estimates whose precision depends on exposure count.

**Graph and dynamics.** Rebuild co-engagement, factor, and IDF similarities using only interactions timestamped before the training cutoff. Pair-disjoint graph construction alone does not make a graph chronologically valid. Treat the covariance of engagement innovations and mean pooling as separate ablations.

**Concrete scope.** Use several predefined, disjoint 32–64-video panels, stratified by prefix popularity and graph community, with one or five inspections/day. Freeze eligibility using prefix information and keep future availability explicit. Use two or three rolling origins as descriptive cases; overlapping windows are not independent replications. The available daily span is only 63 days, so use pooled AR(2) or weekly AR(7) as the main fit. AR(20) is a designed simulation/sensitivity, not a well-estimated separate model for every video.

**What this adds.** Correct the future-information issue identified in the archived audit; compare temporal-only, real-graph, rewired-graph, global-factor, and graph-free shrinkage versions with the same initialization and UCB/TS settings. Model zero-play days as unavailable measurements, not zero completion rates. A retrospectively complete cohort can supply an observed oracle diagnostic, but its future-survivor conditioning must be disclosed.

**Targets.** Observed aggregate-engagement opportunity loss where eligibility and rewards are observed; top-video discovery against a prespecified future-window reference. Known fixed-mean PCS and pseudo-regret are simulation targets. The nearly complete user–item matrix is not a complete daily temporal reward panel.

**Readiness.** Raw data and code are already local; no new large acquisition is needed. Start from the live [KuaiRec report](kuairec/README.md) and the dated [feasibility audit](../research/gpt_sol_10_09/evidence/st_applications/results/feasibility/findings.md). The [official KuaiRec site](https://kuairec.com/) documents the CIKM 2022 dataset and its daily-feature files.

## 3. Retailrocket: budgeted e-commerce catalogue demand monitoring

**Decision.** Choose product groups to inspect or shortlist as demand changes. Arms are 32–64 product groups formed before testing, or a stable prefix-selected item catalogue if item coverage supports it. Main rewards are hourly `log1p(view counts)`; cart and purchase counts provide alternative utility definitions. This models allocating a telemetry/analysis budget, not the causal effect of a recommendation or promotion.

**Graph and dynamics.** Construct weighted co-view/co-cart graphs from training sessions. Use only item-property records available as of the cutoff; an undated category hierarchy is a retrospective metadata sensitivity unless its availability is established. Fit general AR models for short-term persistence and include hour-of-day/day-of-week forecasting baselines; group demand innovations can propagate across related products.

**Concrete scope.** The dataset covers approximately 4.5 months. Start with four weeks of training, two weeks of development, then several disjoint two-week test windows. Sessionize using a prespecified inactivity threshold. Freeze group assignments and demand transforms before testing. Primary AR orders are 7 and 20, with shared/shrunk parameters where individual series are sparse. Use one or five group observations per hour, four to eight predefined panels, and ten stochastic-policy seeds for the initial real-data comparison.

**What this adds.** A longer, high-frequency commerce panel with different top-item gaps and seasonality from the existing studies. Run prefix-only co-session, degree-preserving rewiring, and common-factor comparisons. Treat a bin with no recorded events as zero logged count, not proof of zero intrinsic demand or product availability. Inventory changes need explicit masking rather than future-based catalogue selection.

**Targets.** Observed count-panel oracle loss, demand captured, and finite-window group ranking. Purchases are sparse, so views are the main endpoint and purchases a robustness endpoint. The complete log supports an oracle over recorded demand, not latent causal purchase probabilities.

**Readiness.** The creator's [Retailrocket dataset page](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) supplies events, timestamped item properties, and a category tree. The Kaggle metadata API reports about 305 MB and CC BY-NC-SA 4.0. A small ranged GET to the public download endpoint returned HTTP 206 and a ZIP signature on 10 October 2026; no full archive was downloaded for this note. Exact coverage and archive contents still need an ingestion audit.

## 4. RIPE Atlas: DNS-root monitoring and endpoint selection

**Decision.** With a limited active-measurement budget, choose which DNS endpoints to probe and which endpoint appears fastest for a client location. Each experiment fixes one RIPE probe as the client; the 13 root-server identities are its arms. Different client probes form separate cases, not interchangeable endpoints for one client. The utility is negative capped DNS response time, with a declared timeout penalty.

**Graph and dynamics.** Build endpoint similarities from shared route segments or AS paths in training-prefix traceroutes. Avoid letting the common client-side path make every pair identical; compare a client-wide factor explicitly. Root identities are fixed arms, while anycast routing and backend changes contribute to their restless dynamics.

**Concrete scope.** First audit historical coverage for 10–20 client probes. Fetch 28–42 days of built-in DNS measurements for all 13 roots, aggregate into 10- or 15-minute bins, and reserve chronological training, development, and test blocks. Start with AR(7), then AR(20) or pooled longer-memory sensitivity. Test budgets of one and three endpoints/bin. Request only selected probes, measurements, and time ranges; cache responses rather than downloading global Atlas data.

**What this adds.** A native Web-infrastructure problem with a real cost for active observations. Ask whether observing one route predicts related endpoints and future performance sufficiently to reduce loss or probing volume. Calendar evolution continues for unmeasured endpoints. DNS timeout, missing probe record, and missing API record are different events. Built-in observations are not perfectly simultaneous, so the binned oracle is an aggregate observed-field benchmark rather than an omniscient instantaneous network oracle.

**Targets.** Observed latency-oracle loss per bin, accumulated latency cost, measurement count, and finite-window fastest-endpoint identification. This does not measure total Web page-load improvement or all costs of recursive DNS resolution.

**Readiness.** [Official built-in measurement documentation](https://atlas.ripe.net/docs/getting-started/built-in-measurements) lists DNS and traceroute measurements for the roots. Measurement 10301 was verified public and ongoing via the API; a historical result exposed the DNS `rt` field. This verifies access/schema, not coverage of the proposed dates: the queried probe's last result was old, illustrating why a historical-coverage pilot is required. Historical graph acquisition and initialization measurements must be accounted for.

## 5. Open Bandit Dataset: fashion recommendation with partial click feedback

**Decision.** Recommend a fashion item in one fixed display position to a specified visitor cohort. Arms are supported campaign items; clicks are observed only for displayed items. This is the closest direct recommendation application among the three new studies.

**Graph and dynamics.** Construct similarities from training-only audience-response profiles. Released item metadata without timestamp provenance is a retrospective control, not automatically historical input. A stable AR process can model latent click propensity or a transformed aggregate rate, but Bernoulli observations require a new likelihood/approximate filter. The Gaussian observation theorems do not transfer unchanged.

**Concrete scope.** Start with the uniform-random logging policy and one campaign/position, retaining roughly 30–50 supported items after an actual ID/support audit. Fit on days 1–3, tune on day 4, and test on days 5–7. Use calendar time throughout. For the first real-data result, evaluate policies whose rules are fixed before test, including prespecified calendar/context-dependent rules, by propensity-weighted or doubly robust value estimates. Report support/effective sample size and time-block uncertainty, and compare static, contextual, temporal, and graph-temporal rules. Separately benchmark adaptive learners in a model-calibrated simulation with known counterfactuals.

**What this adds.** Actual logged-feedback evidence, true propensities, and position/context controls. It also exposes the observation-model gap hidden by Gaussian fully recorded panels. The release covers only seven days; campaigns share a platform and time period, so they do not supply independent long histories.

**Evaluation constraint.** Ordinary replay changes calendar time, and ordinary one-step IPS does not automatically evaluate the value of a fully adaptive, calendar-restless learner with deployment feedback. A possible additional target is an explicitly randomly censored learner: choose before seeing the current log, update only on matching randomized actions, advance every calendar step, and propensity-weight matches. Its estimand is that censored-feedback policy, not a deployed policy receiving every selected item's reward. A sequential-OPE extension is separate work.

**Targets.** Logged-policy value/CTR with an appropriate identifiable estimand; simulation pseudo-regret and PCS. No unobserved-click full-state oracle or true real-data PCS is claimed.

**Readiness.** The [publisher's data release](https://research.zozo.com/data.html) documents 26 million impressions, timestamps, item IDs, position, clicks, and propensities. The public archive HEAD returned HTTP 200 and 412,931,917 bytes (about 413 MB); no full download was performed. The [official dataset README](https://github.com/st-tech/zr-obp/blob/master/obd/README.md) and [NeurIPS 2021 dataset paper](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/33e75ff09dd601bbe69f351039152189-Abstract-round2.html) describe the benchmark. Stream one campaign into the required aggregate/context representation rather than loading 26 million Python records into memory.

## Common experiments that make the applications address the three gaps

### Controlled simulation layer

For each application's prefix-built graph, construct calibrated Gaussian environments with **fixed** means, stable heterogeneous AR processes, and known truth. Keep this layer labelled as simulation rather than real-data inference.

- Spatial innovation strength: rho in {0, 0.4, 0.8}; temporal profiles: iid, persistent general AR(20), and a seasonal lag-20 process. Add heterogeneous/oscillatory profiles as a secondary sensitivity.
- Use a graph covariance C with unit diagonal and innovations Q = D[(1-rho)I + rho C]D. If arm i has impulse coefficients psi_i and target stationary variance s_i^2, set D_ii = s_i / sqrt(sum_h psi_i(h)^2). This holds marginal stationary variances fixed when persistence changes, instead of confounding predictability with reward scale. Check convergence/stability and the resulting covariance numerically. Rho controls innovation dependence; stationary cross-correlation can also depend on the temporal filters.
- Corrupt 0%, 25%, 50%, or 100% of learner graph edges, preserving degree where feasible, **without changing the true environment**. Report achieved structural and covariance changes rather than assuming rewiring percentage is an alignment metric.
- Use several deterministic mean profiles with controlled gaps: graph-smooth levels, local peaks, and rough permutations. Primary innovation experiments turn mean regularization off; separate experiments study a supplied valid mean certificate and its misspecification.
- Stage N in {32, 64, 100}, T in {250, 1000, 4000}, and budgets rather than running their full Cartesian product. Begin with 20 independent paired worlds to screen; use about 100 for primary regret contrasts and 200 for selected near-tie PCS contrasts. These are starting replication counts, not power guarantees: 200 binary outcomes can still have a roughly seven-percentage-point 95% half-width near PCS = 0.5.
- Separate known-parameter controls, independently prefix-fitted parameters, wrong AR order, wrong covariance, and heavy-tailed/changed-dynamics robustness. Supplied-parameter theory and fitted-model empirical performance are different claims.

### Chronological real-data layer

Use static ranking, last-value/seasonal rules, iid UCB/TS, discounted or sliding-window policies, temporal-only filters, matched spatiotemporal UCB/TS, real versus rewired graphs, and global/low-rank-factor and shrinkage-covariance alternatives. Tune exploration on development data, including a greedy limit. Fresh innovation uncertainty and uncertainty in predictable state should be handled consistently when comparing Thompson variants.

Freeze panels, graphs, transforms, and hyperparameters before test. Use matched observation budgets and initialization information. Maintain missingness/availability masks, advance time for every arm, and keep test observations hidden except when the policy acquires them. Distinguish continuous hidden evolution from protocols that refresh the full field between windows.

Report paired differences within each field, variability across predefined panels/time windows, and policy-randomization uncertainty separately. Resampling policy seeds on one recorded field does not create independent Web histories. A held-out top-item label is a finite-window empirical target, not known permanent-mean PCS.

### Laptop plan and order of execution

1. Correct KuaiRec chronology and expand predefined Wikipedia cases while retaining current negative graph results.
2. Implement Retailrocket: the first additional demand-panel experiment.
3. Run a small RIPE historical-coverage pilot, then the DNS study if coverage and route data are adequate.
4. Add Open Bandit Dataset when partial-feedback evidence is worth its additional modelling/evaluation work.

Primary exact-filter panels stay at 32–64 arms with AR(7); AR(20) is used selectively. One covariance for 64 arms with 20 lags plus a mean coordinate occupies about 14.5 MB in float64, but working matrices and policy copies increase actual memory. Use one process, one BLAS thread, a 2 GB process-memory target, and a measured timing pilot before expanding replications. Neither download size nor covariance size establishes total runtime or memory cost. Save raw-run tables, chronology checks, model fits, graph diagnostics, decision traces, and measured runtime/RSS.

For the final submission, a focused core of strengthened existing studies plus Retailrocket and/or DNS is more compelling than five thin demonstrations. Five designs provide options; acceptance still depends on the contribution, valid evaluation, competitive baselines, and results.
