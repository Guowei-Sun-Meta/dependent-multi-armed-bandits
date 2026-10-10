# Prioritized experiment plan for the correlated-arms paper

10 October 2026. Status: assessment and proposed execution plan; no new benchmark was run for this document.

Compared documents: [next_experiments.md](next_experiments.md) and [recommended_spatiotemporal_experiments.md](recommended_spatiotemporal_experiments.md). The latter is the repository file corresponding to the requested `recommended_st_experiments.md`.

The [merged experiment plan](experiment_plan.md) reaches similar priorities. This assessment adds model-assumption and evaluation corrections that should be applied when executing that plan; the original proposals and merged plan are preserved.

## Decision

Run four core studies after a chronology audit: **strong real-data baselines with paired evaluation; general-AR certificate robustness; an independently controlled correlation/alignment experiment; and two targeted theory instances**. Include **Open Bandit Dataset as the primary new application**, with a bounded calendar-time censored-feedback study. Keep a small computational-cost profile in the appendix. Retailrocket becomes optional; full DNS and evaluation of an uncensored deployed adaptive learner remain later extensions.

| Work package | Priority |
| --- | --- |
| P0: chronology and feedback audit | Prerequisite |
| P1: real-data baselines and paired evidence | Core |
| P2: general-AR certificate robustness | Core |
| P3: controlled correlation and graph alignment | Core |
| P4: false-elimination and slate-contrast instances | Core |
| P5: Open Bandit Dataset recommendation study | Primary new application |
| Small computational-cost profile | Supplementary |
| Retailrocket | Optional additional application |

The selection criterion is coverage of the paper's central claims per unit of engineering and laptop compute, with evaluation validity as a prerequisite. This is a practical prioritization, not a proven global optimum. The [official WWW 2027 call](https://www2027.thewebconf.org/research-track-papers/) gives 18 October for abstracts and 25 October for full papers; freeze experimental scope by 16 October and final results by 21 October.

`next_experiments.md` supplies the better immediate submission agenda: test the bridge and challenge the current performance claims. The recommendation note supplies controls that agenda needs: chronological graph construction, separate spatial and temporal variation, honest oracle definitions, and data-access checks. Their combination should produce a focused evidence package rather than a five-dataset expansion.

## Comparison and corrections

| Proposal | Assessment | Combined decision |
| --- | --- | --- |
| E1a: block-mean variance inflation | Useful diagnostic, inexpensive, and relevant to general AR models | Keep; use the full fitted autocovariance, with an AR(1) approximation labelled separately |
| E1b: real-calibrated certificate worlds | High value for bridging mean pooling and dynamics | Keep; primary worlds use temporally independent Gaussian innovations; weekly residual blocks become a misspecification stress test |
| E2: fitted/wrong dynamics | Essential practical limitation | Keep; distinguish nuisance-mean refinement from estimated dynamics, and empirical coverage from a proved guarantee |
| E3: standard baselines | Highest-value challenge to the real-data headline | Keep discounted/window methods, seasonal/EWMA, and AR2-p where its protocol fits; defer CLUB/GOB.Lin unless their multi-user claim remains central |
| E4: more origins and replications | Necessary, but the proposed overlapping windows do not create independent trials | Prefer non-overlapping windows; retain dense rolling origins as a sensitivity; pair methods on the same field and account for dependence |
| E5: spatial strength versus level spread | Valuable mechanism test, currently incomplete | Add independent temporal variation, fixed-truth graph corruption, controlled gaps, and known-mean PCS |
| E6: false elimination and slate contrasts | Low-cost tests directly tied to central theory | Promote into the core set; reuse the certificate runner |
| E7: featuring-effect perturbations | Introduces action-dependent transitions and a different oracle problem | Defer; retain the present exogenous-monitoring interpretation |
| E8: large-N filter approximation | Useful engineering work, but the proposed sizes/complexity claims need a pilot | Keep a small measured profile; defer a new low-rank filter and 3,000-arm exact runs |
| E9: Open Bandit Dataset replay | Highest recommendation relevance; partial outcomes require an explicit feedback target | Promote a bounded calendar-time censored-feedback study; ordinary replay does not identify full adaptive deployment value |
| E10: Yahoo! R6 | Access/licensing and temporal replay work add dependencies | Defer |
| E11: practical certificates | Potential method contribution, not a quick experiment | Separate method project; do not infer validity from a successful robustness sweep |
| Expanded Wikipedia/KuaiRec | Existing data make these the fastest real-data improvements | Keep selected, predefined cases; repair chronology before expanding |
| Retailrocket | Useful additional commerce demand panel; archive access checked | Optional after Open Bandit Dataset and the core studies |
| RIPE Atlas DNS | Strongest genuine active-measurement-budget story | Reserve alternative if the paper pivots to infrastructure; avoid a second acquisition pipeline now |
| Fashion recommendation | Genuine randomized clicks and propensities; aggregate observation modelling is feasible | First new application, with explicit censoring and approximation limits |

Several statements in `next_experiments.md` need qualification before execution:

- **Weekly resampling of residual vectors introduces temporal innovation dependence.** Stable AR rewards are already serially correlated; primary theory tests should preserve the specified independence of innovations over time. Independently resampling centered residual vectors preserves empirical cross-sectional dependence but remains a non-Gaussian robustness condition. Weekly residual blocks add another misspecification.
- **A successful plug-in sweep cannot establish a new confidence theorem.** A persistence estimate plus two standard errors and an inflated beta are candidate heuristics, not a simultaneous uncertainty bound for all AR coefficients, innovation covariance, observation noise, and adaptive times. The current `plugin_bounds` refines nuisance means while the simulation supplies dynamics; it does not establish coverage with learned dynamics.
- **Non-significance does not establish a tie.** An interval crossing zero means the comparison is inconclusive. Call two methods practically equivalent only with a prespecified equivalence margin and an interval wholly inside it.
- **Ordinary replay needs an assumption audit.** The [Li et al. replay theorem](https://arxiv.org/pdf/1003.5956) assumes iid logged events. Our inference is that its guarantee does not automatically cover serially correlated rewards with physical time continuing through rejected log events.
- **AR2 has a relevant general-order comparator.** [Chen et al., Appendix B.2](https://arxiv.org/html/2210.16386v3#A2.SS2), explicitly describes AR2-p. Its single-pull protocol, initialization, restart costs, and model assumptions still need matching to our experiments; a top-k adaptation does not inherit its original guarantee.

## P0. Prerequisite: chronology, feedback, and model audit

**Priority:** first, before any expensive rerun. **Outputs:** eligibility/graph manifests, dated provenance, feedback-budget checks, and a table classifying existing results as chronological, retrospective, or simulated.

The code review found two concrete Wikipedia issues:

1. [collect.py](wikipedia/code/collect.py) ranks candidates by median traffic across the complete 2022–2025 panel and requires complete coverage across that period. [collect_multi.py](wikipedia/code/collect_multi.py) does the same within communities. This makes the evaluation catalogue retrospectively selected.
2. Both collectors retrieve current hyperlinks through `prop=links`, with no historical revision cutoff. The resulting graph is not demonstrated to have existed before the backtest.

Rebuild candidates from a historically available list/category snapshot and training-prefix eligibility/popularity. Freeze the article set before test and use historical revisions for the graph. Prefer literal links in the dated revision, or pin transcluded template revisions too: parsing an old article with current templates does not establish a historical graph. Missing observations and article renames need explicit handling. Existing panels can remain retrospective diagnostics. The [dated 24-article Wikipedia study](../research/gpt_sol_10_09/experiment_design.md) provides a separate example of historical graph reconstruction; its panels and initialization differ from the live studies.

For KuaiRec, [daily.py](kuairec/code/daily.py) selects complete rows over the full 63 days and uses cached feature inputs in graph construction. The [archived audit](../research/gpt_sol_10_09/evidence/st_applications/results/feasibility/findings.md) found post-cutoff item-graph inputs and zero-play cells. Rebuild graphs from timestamped training interactions, choose candidates from the prefix, and distinguish zero play count from zero completion probability. Prefix-only eligibility can leave future missing feedback; do not silently impute a completion rate. If a full-field oracle requires a future-complete cohort, report it as a conditional retrospective benchmark. Keep unresolved daily evidence exploratory.

Availability information must itself be available before selection. A mask defined by the total plays accumulated later that day reveals future activity; sharing that mask with the policy is a different retrospective information model. Define and disclose that target rather than presenting it as prospective deployment. Likewise, disjoint panels/windows reduce overlap but can still share global shocks and fitted parameters; they are not automatically independent units. Monitoring framing specifies a utility proxy and budget; it does not establish causal promotion effects or prove production measurement costs.

Every method must receive the same allowed initialization data. Sparse test feedback does not make a study cold-start if model estimation used a full historical field. Record historical and test acquisition counts separately. Select a slate before observing any reward in that slate; keep unobserved arms evolving.

Retain preprocessing, graph, and model-fit hashes in cache keys, including cutoff, panel, dynamics, and covariance variant. Audit stability/positive-definiteness before running; a fitted unstable AR model is not a stationary environment.

## P1. Existing applications: baselines and paired evidence

**Combines:** E3 and E4, plus the chronology and initialization controls from the recommendation note.

**Primary question:** does spatial/temporal modelling add decision value beyond forgetting, seasonality, and generic shrinkage?

**Scope.** Retain clean versions of the Wikipedia single-domain and multi-community cases, and a corrected KuaiRec daily study where feasible. For Wikipedia, prefer approximately 12 non-overlapping 90-day windows after the initial 2022 prefix, subject to coverage. A rolling fit may use earlier logged history, but every full-field refresh must be explicitly counted. The continuously hidden-field protocol is a separate sensitivity. KuaiRec has only 63 days: use a few 14-day cases and predefined video subsets, describe overlap, and avoid treating 15 nearby origins as 15 independent histories. Main models use pooled AR(2) or selected-lag AR(7); dense AR(20) is a selected sensitivity.

**Baselines.** Static prefix ranking; last observation; seasonal naive with forecasted missing lags; EWMA; discounted and sliding-window UCB/TS; temporal-only filter UCB/TS; matched spatiotemporal UCB/TS; common-factor/low-rank and covariance-shrinkage controls; real versus degree-preserving rewired graphs. Reuse existing implementations where possible. Add AR2-p on compatible single-pull conditions, with its initialization/restart samples counted. A warm-start variant should receive the same prefix and be labelled as an adaptation; do not manufacture within-slate sequential feedback. A boosted forecaster is optional once this core comparison is complete.

**Fairness.** Retain the existing 10-slot case as a reference, and add budget-one cases where feasible; use budgets five/ten selectively rather than multiplying the full grid. Freeze exploration constants, windows, discount rates, and covariance tuning using development data. The original toy selected a UCB multiplier on evaluation runs; confirmation uses a separately selected, frozen multiplier. Deterministic policies need replication only when observation noise changes; separate policy randomness from synthetic measurement noise and precompute common noise for paired comparisons.

**Analysis.** Report daily decision traces, observed-field oracle loss, loss per selected item, and paired differences against prespecified temporal-only and forgetting baselines. Use date-aware dependence analysis within each fixed panel, with a moving-block analysis where justified and block-length sensitivity. Overlapping origins reuse dates and initialization data, so merely bootstrapping 15 origin averages is not automatically reliable. Retain panel-level results and describe conditional seed uncertainty separately. Three shared histories cannot establish broad population generalization regardless of the seed count.

If the Q2 mean-channel tail claim remains prominent, add a bounded confirmation of Setting A v2: 60–120 held-out users, two subsets/user, one prespecified graph, and the primary matched KL/certificate controls. Cluster uncertainty by user. Expanding every graph and reward definition is lower priority than estimating the central comparison and its tails.

**Claim rule.** If discounted methods match or beat the filter, report that outcome and narrow the performance claim. If real and rewired graphs match, retain that negative result. Do not interpret a common-factor gain as evidence for the actual graph topology.

## P2. General-AR bridge: known, fitted, and wrong dynamics

**Combines:** E1 and E2. **Primary question:** how do model uncertainty and persistence affect coverage, false decisions, and fixed-mean learning?

Start with a small general-AR environment of 32–64 arms, with at least one AR(20) configuration and one heterogeneous-order configuration. Use Wikipedia/KuaiRec training fits to calibrate selected covariance structures and scales. Oracle component widths are allowed in this controlled experiment and must be labelled oracle; they do not solve practical certificate estimation.

**Diagnostic first.** For block lengths 1, 3, 7, and 14, compare observed block-mean variance with the complete fitted autocovariance prediction:

```math
\operatorname{Var}(\bar X_b)
=\frac{\gamma(0)}{b}
\left[1+2\sum_{h=1}^{b-1}\left(1-\frac{h}{b}\right)\frac{\gamma(h)}{\gamma(0)}\right].
```

Observation noise contributes at lag zero. Use the full AR covariance rather than treating lag-one correlation as an AR(1) parameter. Real-data inflation is a diagnostic; it does not directly measure coverage of a true permanent mean.

**Three evaluation layers.**

1. **Correct specification:** fixed means, stable general AR dynamics, temporally independent Gaussian innovation vectors, known model. Check sequential joint whitening/innovation regression against dense Gaussian conditioning on small cases before extending the existing AR(1) certificate code.
2. **Learned specification:** same true world, with dynamics fitted from independent prefixes of two lengths, for example 100 and 365 complete calendar observations. Add budget-limited burn-in as a separate protocol with per-arm sample counts; 200 total pulls across 64 arms cannot provide 200 observations per arm or ordinary complete AR(20) histories. Budget online refitting separately.
3. **Misspecification:** wrong AR order, ignored spatial covariance, iid variance-normalized Student-t innovations, and temporally blocked residual resampling. A changing physical mean is a separate nonstationary performance stress test, with a different mean target.

Compare iid, known-model innovation, fitted-model innovation, and a prespecified conservative fitted-model heuristic. Known-model uncertainty in nuisance means and uncertainty in fitted dynamics are distinct. A rigorous learned-model coverage claim would need a separate parameter-uncertainty argument; otherwise report observed coverage with binomial intervals and the failure conditions.

**Outputs.** Any-time mean/component coverage, false elimination, stopping/rejection times, stationary mean pseudo-regret, and terminal PCS. Track true-current-state oracle loss as a separate decision objective. Define the fixed-arm realized comparator separately if reported; its sample-path regret can be negative. Use true fixed means for PCS. Zero observed violations is finite-simulation evidence, not a proof.

**Replication.** Screen with 20 independent worlds; confirm the few prespecified primary contrasts with around 100 worlds. Use about 200 worlds for selected near-tie PCS contrasts and report their remaining uncertainty. Heavy-tail/block-resampling results cannot be pooled into the Gaussian-theorem validation table.

## P3. Controlled spatial–temporal interaction and alignment

**Combines:** E5 and the recommendation note's factorial design. **Primary question:** when does spatial information improve future decisions, and how much does an incorrect constructed graph hurt?

Use a stable general AR(20) process as a main environment, alongside iid and seasonal/heterogeneous profiles. Keep fixed deterministic means and independent innovation vectors over calendar time. Introduce spatial strength through a unit-diagonal graph covariance C:

```math
Q_\rho=D[(1-\rho)I+\rho C]D,\qquad
D_{ii}=\frac{s_i}{\sqrt{\sum_{h\ge0}\psi_i(h)^2}}.
```

Here psi_i is the arm's impulse response and s_i its target stationary standard deviation. This normalization keeps marginal reward variance fixed when persistence changes. Spatial innovation strength is not automatically the same as stationary cross-correlation under heterogeneous temporal filters.

**Staged design.**

- Screen the 3-by-3 persistence/innovation-strength grid at 32 arms and T = 1,000, with paired worlds and matched ST/temporal-only UCB and predictive-sampling variants. Freeze tuning outside the evaluation worlds.
- Confirm prespecified correlated and uncorrelated persistent cases with more worlds. Add the existing 100-arm AR(20) setup for selected scale/replication confirmations, rather than repeating every prior policy.
- At fixed true dynamics/covariance, corrupt only the learner graph at achieved edge changes near 0%, 50%, and 100%. Fit the same allowed strength/shrinkage parameters for each graph. A structural rewiring percentage is not itself reward alignment: report held-out edge innovation correlation, covariance discrepancy, and decision-relevant neighbourhood diagnostics.
- Add two prespecified mean-gap/fluctuation regimes and deterministic smooth versus rough/localized mean profiles. Keep all candidate cases, including no spatial benefit. Turn mean regularization off in the primary innovation comparison; study certified mean pooling separately with valid and invalid assumptions.
- Use T = 250, 1,000, and 4,000 only for selected learning-curve contrasts. Avoid a full product of horizons, graphs, profiles, budgets, and model fits.

**Objectives.** Report the average current-state oracle-loss coefficient and stationary mean pseudo-regret separately. For PCS, include mean-targeted UCB/TS and round-robin with an appropriate mean estimator, and recommend using estimated means rather than the last latent state. A dynamic-reward policy need not be optimal for fixed-mean identification. Do not rank every algorithm using one blended objective.

For a real-data check of the proposed level/fluctuation mechanism, choose level-matched article subsets using training means only, freeze them before test, and retain the unmatched original panel. These subsets are a sensitivity, not independent new datasets.

## P4. Two targeted theory tests

**Combines:** E6. Reuse P2's runner, rather than creating another benchmark framework.

**False elimination and lasting regret.** Construct a fixed-mean environment in which the optimal component can be wrongly eliminated under bursty sampling. Prespecify the gaps and exposure pattern, randomize arm order, and compare iid versus correct-model certificates. Show failure probability, conditional regret after failure, and regret curves for several horizons. A simulation illustrates a linear-loss mechanism; it does not prove an asymptotic lower bound. Keep any claimed lower bound tied to its actual proof.

**Slate contrast information.** Compare simultaneously observed equal-variance arm pairs at several spatial correlations. For general AR processes, use the complete long-run covariance Omega: the asymptotic contrast variance is approximately `(Omega_ii + Omega_jj - 2 Omega_ij) / n`. The simplified `(1-rho)` gain requires equal variance, comparable temporal filters, and matched simultaneous sampling. Add unequal/heterogeneous and staggered-exposure controls, where that shortcut need not apply. Use the covariance of observed coordinates and joint whitening; a principal block of full precision is not generally the precision of a marginally observed subset.

Report finite-sample variance, predicted contrast uncertainty, and samples needed for a correct certified decision. Positive spatial correlation can reduce contrast noise without reducing each marginal variance; this is a separate mechanism from transferring an unobserved arm's state.

## P5. First new application: Open Bandit Dataset

**Confirmed priority.** Open Bandit Dataset is included in the main experiment set as the first new application. Recommendation relevance and genuine randomized click feedback motivate its inclusion. The [bounded study design](open_bandit/design.md) defines its evaluation target and implementation scope. Retailrocket remains an optional longer demand-panel complement.

**Pilot cap:** about half a day plus a timing run. Stream one uniform-random campaign and one fixed position, audit actual item support/propensities/timestamps, and form 10–60-minute bins with training-selected resolution. Use days 1–3 for fitting, day 4 for development, and days 5–7 for test where actual coverage permits. Build item similarities from training-only visitor-cohort response profiles; compare common-factor and rewired controls. Report null persistence or graph findings rather than selecting a winning campaign.

**Primary experiment.** At the start of each physical bin, an adaptive UCB/TS policy chooses one item. It updates only from randomized impressions that match its chosen item. Time advances through every bin, including those without matching feedback. Estimate the policy's click value with the matching indicators and recorded propensities. The estimand is a learner receiving randomly censored feedback. It is not the value of a deployed learner that observes every selected impression, and it assumes the target's choices do not change the historical reward-state evolution.

**Observation model.** Aggregate matching successes/impression counts and use an exposure-aware Gaussian approximation for transformed click rates when its diagnostics support it. A new exact Bernoulli filter is therefore not an entry requirement. The exact Gaussian confidence theorem still does not apply unchanged to clicks. Include selected general-AR fits and matched temporal-only, discounted/window, static, real/rewired-graph, and common-factor controls.

**Secondary evidence.** Frozen-policy IPS/DR evaluation and held-out aggregate-rate forecasting are easier identifiable targets. Controlled general-AR simulations calibrated to the prefix compare censored versus full feedback and supply known means/states for oracle regret and PCS. The real logs have no observed full-state click oracle or true permanent-mean PCS.

**Execution checklist.**

- [ ] Audit one random-policy campaign/position and publish its chronological split, item support, and propensities.
- [ ] Build the prefix-only graph and fit the general-AR observation model, with exposure/approximation diagnostics.
- [ ] Run matched UCB/TS, temporal-only, forgetting, static, common-factor, and rewired-graph controls under the same calendar-time censoring.
- [ ] Report propensity-weighted click value, feedback counts, effective sample size, uncertainty, runtime, and memory.
- [ ] Keep controlled-simulation oracle regret/PCS and frozen-policy OPE results separate from the adaptive censored-feedback result.

**Go/no-go.** Proceed when support, time coverage, observation precision, chronology, and measured resources allow the declared experiment. Seven days do not establish long-horizon generalization. If aggregation is inadequate, report the limitation and retain the frozen-policy/diagnostic scope rather than rushing a new likelihood theorem. A null graph gain is a result, not a reason to switch applications.

**Source:** [publisher's Open Bandit Dataset release](https://research.zozo.com/data.html). Complete definitions, checks, and deliverables are in [open_bandit/design.md](open_bandit/design.md). The [recommendation note](recommended_spatiotemporal_experiments.md) preserves the additional Retailrocket and RIPE options.

## Small supplementary cost profile

Profile the current exact implementation at N = 32, 64, 100, and 300 with AR(7), adding AR(20) at selected sizes. Record propagation, selection, update, complete-run time, and peak RSS separately. Stop at a measured resource cap. Covariance storage is quadratic in state dimension, while runtime also depends on transition structure, whitening, slate size, and matrix factorizations; do not assert a single quadratic bound for the whole implementation.

A new low-rank filter is method work: low-rank Q plus a diagonal does not by itself guarantee a small exact filtering state under arbitrary heterogeneous AR dynamics. Defer that implementation and claims of Web scale. Measured laptop feasibility is the appropriate claim for this study.

## Execution order and scope control

| Phase | Work | Completion criterion |
| --- | --- | --- |
| 10–11 October | P0; real-data variance diagnostic; resource pilots; begin P4 | Chronology/feedback audit and fixed evaluation protocol |
| 12–14 October | P1 baseline suite; P2 known/fitted dynamics on small cases | Checked innovations, frozen tuning, first paired tables |
| 14–16 October | P3 screening and prespecified confirmations; P4; Open Bandit pilot | Core claim decisions available before the abstract |
| 17–20 October | Confirm key coverage/PCS and real-panel contrasts; bounded Open Bandit run; small cost profile | Complete primary raw-run records and uncertainty analysis |
| 21 October | Freeze results and record unresolved limits | Reproducible figures, manifests, and claims supported by the outcomes |
| 22–25 October | Paper reduction, figures, and final verification | Submission-ready evidence package |

These dates are sequencing targets, not measured runtime promises. Re-estimate CPU-hours from pilots on the current machine. Use one BLAS thread per worker; begin heavy filters with one or two workers on the 8 GB laptop. Increase concurrency only after measuring combined RSS. Prioritize core comparisons over overnight seed expansion of every old policy.

Every work package should save its design, model/graph manifests, raw runs, per-time summaries, checks, and measured resources in its experiment folder. Do not overwrite released historical results. Keep prespecified primary comparisons separate from exploratory follow-ups; if analysis changes after viewing outcomes, disclose the change.

## Expected paper evidence, without assuming positive outcomes

The final package should contain:

1. A real-data baseline/paired-comparison figure showing the contribution of temporal modelling, forgetting, common factors, and actual graph topology.
2. A general-AR certificate figure separating known models, learned models, and misspecification, with false-decision rates and uncertainty.
3. A correlation/alignment map with fixed marginal variance, plus objective-specific mean-regret/PCS results.
4. A targeted false-elimination/regret figure and a simultaneous-versus-staggered contrast-information figure.
5. A logged-click application table with its censored-feedback or frozen-policy estimand, and a measured cost table.

This set directly tests the bridge, algorithm value, graph correctness, and practical modelling assumptions. It also retains the possibility that strong forgetting baselines win, learned certificates under-cover, or real graphs add little decision value. Those outcomes should determine the paper's claims.
