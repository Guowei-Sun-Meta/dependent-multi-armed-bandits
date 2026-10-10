# Open Bandit Dataset: calendar-time recommendation experiment

10 October 2026. Status: proposed study; no dataset ingestion or benchmark run has been performed for this design.

## Why include it

Open Bandit Dataset (OBD) is the first new application priority for recommendation relevance and genuine randomized click feedback. The [publisher](https://research.zozo.com/data.html) documents about 26 million impressions, timestamps, item IDs, display positions, click outcomes, and true propensities from ZOZOTOWN. The [official README](https://github.com/st-tech/zr-obp/blob/master/obd/README.md) describes the seven-day release. It directly addresses the logged-feedback gap left by the Wikipedia and KuaiRec daily panels.

The previous exclusion prioritized reuse of complete count-panel machinery. A bounded OBD experiment can use aggregated click observations and a clearly defined censored-feedback policy; a new exact Bernoulli filtering theorem is not a prerequisite. Retailrocket becomes an optional subsequent demand-panel study.

## Pilot and fixed scope

Start with the uniform-random policy, one campaign, and one fixed display position. Count the actual supported item IDs rather than relying on documentation's inclusive index ranges. Prefer a campaign with roughly 30–50 supported items. Preserve original action probabilities if retaining a subset; do not renormalize them as though the logger only served that subset.

Stream the CSV into chronological aggregates; the full archive's previously verified compressed size is about 413 MB. Save the source checksum, timezone/timestamp audit, duplicate/impression-unit checks, position coding, logging-policy probabilities, item support, and per-bin impression/click counts. No full-data download is implied by the earlier header check.

Use days 1–3 for fitting, day 4 for development, and days 5–7 for test, subject to the actual timestamps. Select a 10-, 30-, or 60-minute bin width using training/development coverage. Seven days support many bins but do not supply many independent weeks; report within-week evaluation rather than long-horizon generalization.

Bound the initial engineering pilot to about half a day plus a timing run. Check support, per-item exposure precision, prefix-only graph construction, and residual persistence beyond binomial sampling noise. Include common-factor controls for changes in the visitor population. Retain null temporal/graph findings; a policy gain is not an eligibility criterion.

## Arms, state, graph, and observations

Arms are campaign items at the chosen position. Fit general AR models for transformed aggregate click propensities, with a sparse/shared AR(7) primary fit and a regularized AR(20) sensitivity where coverage supports it. Physical calendar time advances for every arm, including bins with no observed clicks or no matching feedback.

Build item similarities from training-only response profiles across prespecified visitor-feature cohorts. Use shrinkage for sparse cohort cells. Compare real, degree-preserving rewired, temporal-only, and common/low-rank-factor covariance models. Released item features without timestamp provenance are a retrospective metadata sensitivity. Innovation correlation does not certify smooth fixed means.

For selected-arm feedback, retain successes and impression counts. When exposure is sufficient, an exposure-aware Gaussian approximation to a transformed click rate lets us reuse the general-AR filter. Use a prespecified continuity correction and variance floor; zero clicks with positive impressions is a valid observation, while zero impressions means no observation. Gaussian approximation/calibration is empirical here; the manuscript's exact Gaussian confidence guarantees do not transfer to Bernoulli clicks. A binomial likelihood with a latent AR propensity is a later extension if approximation diagnostics are poor.

## Primary target: an adaptive learner with censored feedback

At the beginning of bin b, policy pi chooses one item a_b using only its allowed training data and previous selected-item feedback. It receives no current-bin labels before choosing. It holds that item fixed throughout the bin.

The historical random logger chose an item A_j for each eligible impression j, with recorded propensity p_j for its chosen item, and observed click Y_j. The learner updates only from impressions where A_j = a_b. Other click labels stay hidden from its filtering and decisions. At the end of the bin it receives the matching impression/click counts and advances to the next physical bin. There is no accepted-event clock and no skipping time when feedback is absent.

For M_b eligible logged impressions in that bin, estimate the selected item's average click value by

```math
\widehat v_b
=\frac{1}{M_b}\sum_{j\in b}
\frac{\mathbf 1\{A_j=a_b\}Y_j}{p_j}.
```

Pool the numerator and denominator across bins for impression-weighted CTR, and report bin-averaged value separately. Matching rows use their actual propensities. Primary use of uniform logging simplifies the learning-rate observation; a nonuniform logger would also require correcting exposure selection in the learner's observation model.

The conditional propensity identity motivates this estimate under correct randomization probabilities, action support, and consistent potential outcomes. State evolution must be exogenous to the hypothetical policy for this historical-field comparison. Fixing one position also requires defining other positions' behaviour: the target changes one item while preserving the logger's conditional distribution of the remaining slate. Do not interpret the result as evaluation of a separately optimized full slate.

**Estimand:** the value of a policy that learns from randomly available selected-item feedback while calendar time continues. Its feedback rate differs from deployment where every selected impression returns an outcome. The experiment evaluates this censored learner, not the fully observed deployment learner or a counterfactual policy that changes future user demand. Demonstrate the distinction in controlled simulation with both feedback regimes.

The [classic replay theorem](https://arxiv.org/pdf/1003.5956) assumes iid logged events. That theorem alone does not justify compressing our temporal process to matching events. Propensity weighting preserves the calendar-time target, but does not identify a different adaptive feedback history for free.

## Secondary evidence and controls

1. **Frozen-policy OPE:** fit rules before test and evaluate their current-context/calendar decisions with IPS and a training-fitted doubly robust reward model. This is a separate, easier target; current test labels never tune a rule or reward model.
2. **Aggregate-field diagnostic:** form random-policy click-rate panels and measure held-out temporal forecast error and innovation dependence, accounting for varying impression counts. Full aggregate test labels belong to diagnostics/evaluation, not the primary learner's feedback. A maximum of noisy recorded CTRs is an empirical diagnostic oracle, not the latent optimal click propensity.
3. **Controlled simulations:** calibrate the existing fixed-mean general-AR worlds to prefix scales and graphs, and compare censored versus full selected-arm feedback. Known true means/states support PCS, stationary mean pseudo-regret, and current-state oracle regret here. No true PCS or full-state reward oracle is asserted for the raw OBD logs.

Compare static popularity; random selection; discounted/window UCB and TS; temporal-only filtering; matched spatiotemporal UCB/TS; and real-versus-rewired/common-factor controls. Give every method the same training information, censoring, support, and measurement precision. Count historical fitting impressions separately from test observations.

## Uncertainty, checks, and deliverables

Report actual matched observations, matching fraction, weight distribution, effective sample size, zero-feedback bins, and per-item support. Preserve conditional randomization/IPS uncertainty separately from model and time-series uncertainty. Dependence-aware block analyses are descriptive within the seven-day field, with block-length sensitivity; policy seeds do not create independent weeks. Avoid applying an iid impression bootstrap to a serially correlated adaptive trajectory. An adaptive estimator's confidence method needs its own assumption check.

Before the real run, check the propensity estimator on a tiny known-counterfactual simulation, verify that decisions are unchanged when hidden nonmatching click labels change, and verify that time advances through empty bins. Use one BLAS thread, stream raw rows, and measure RSS/runtime on a small campaign pilot before increasing policy replications.

Deliver the chronology/support manifest; graph and dynamics fits; raw bin decisions and matching feedback; IPS/DR value tables with their exact estimands; persistence/covariance diagnostics; approximation checks; measured resources; and a short report retaining negative findings. Data-model inadequacy changes the conclusions and scope, rather than being hidden by selecting a favourable campaign.
