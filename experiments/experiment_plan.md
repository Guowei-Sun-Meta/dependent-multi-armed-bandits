# Experiment Plan to 21 October: Merged Recommendation

10 October 2026. This plan merges two proposals into one set of experiments for the long paper:

- [next_experiments.md](next_experiments.md): an evidence review of the paper's claims (E1–E11).
- [recommended_spatiotemporal_experiments.md](recommended_spatiotemporal_experiments.md): five application studies and a validation protocol, adapted from the other agent's [design](../www/spatiotemporal_experiment_design.md).

Experiments freeze on 21 October. The abstract is due 18 October and the paper 25 October.

## Revisions, 10 October afternoon: one plan

[optimal_experiment_plan.md](optimal_experiment_plan.md) is folded in here; this file is the single plan. First results for experiments 3a, 4, 6 and 8 are in [oct10_runs/](oct10_runs/README.md).

**Open Bandit Dataset: the limited form (experiment 8) stands.** The censored-feedback, calendar-time study in [open_bandit/design.md](open_bandit/design.md) is deferred. The feasibility check settles it:
- Item click rates do vary from day to day more than binomial noise allows, with Pearson dispersion about 2.
- But the day-to-day residuals do not persist. Their lag-1 autocorrelation is −0.14 to −0.22 by day and about 0 by 6-hour bin.
- At 1–2 clicks per item per 6-hour bin, there is no fluctuation channel to filter.

**Corrections adopted from the optimal plan:**

1. **Availability must be known before selection.** Masking zero-play days in experiment 1 uses that day's outcome. Define availability from the prefix, or label the setup as retrospective.
2. **3a uses the full fitted autocovariance**, at block lengths 1, 3, 7, 14 and 28. The AR(1) shortcut from lag 1 is reported separately; it underpredicts at long blocks.
3. **3b's main worlds resample innovations independently over time.** Weekly blocks of residuals break B1's assumption, so they move to the stress test.
4. **Experiment 4 reports observed coverage with binomial intervals.** "Fitted φ plus 2 SE" is a heuristic, not a theorem.
5. **Replication units.** Disjoint windows still share global shocks and fitted parameters, so the analysis must be dependence-aware. An interval that crosses zero means inconclusive, not tied.
6. **B3: (1 − ρ) holds only for equal pairs.** Use the long-run covariance Ω, and add unequal-variance, heterogeneous-persistence and staggered controls. Done in 6.
7. **Tuning.** Freeze exploration constants on development runs. The benchmark's UCB multiplier was picked on evaluation runs.
8. **Wikipedia links.** Old revisions parsed today expand templates at their current versions. Use literal links from the dated revision, or disclose the mismatch.

## Bottom line

The recommended file's most important point is one my review missed: **the KuaiRec daily results use future information, and the Wikipedia panels do too.** Fixing that comes first, because every real-data number in Q1 and Q4 depends on it.

- **KuaiRec daily.** `daily.py` builds its I-coeng graph from the full interaction log. At the first cutoff (1 August 2020), 79.1% of the graph's input rows are later than the cutoff ([audit](../research/gpt_sol_10_09/evidence/st_applications/results/feasibility/findings.md)). The panel also keeps only videos observed on all 63 days.
- **Wikipedia.** Articles were selected by 2022–2025 popularity and completeness, and the hyperlinks are a 2026 snapshot.

The recommended file says nothing about the mean channel or certificates, which are the paper's distinctive bridge (Q2, Q3). So my certificate experiments stay in the set. Of its five datasets, two earn a place:

- **The Open Bandit Dataset**, in a limited form: certified pooling calibrated on its real e-commerce click rates. Its click signal is too thin for the full logged-feedback study.
- **Retailrocket**, conditionally.

RIPE Atlas is deferred.

**The optimal set: ten experiments, four of them required.**

| # | Experiment | From | Priority | Work | Compute |
| --- | --- | --- | --- | --- | --- |
| 1 | [Chronological real-panel protocol](#1-chronological-real-panel-protocol), then re-run KuaiRec daily and Wikipedia | Recommended (gap 3); replaces my E4 | **Required** | 2 days | < 2 CPU-hours |
| 2 | [Standard baselines](#2-standard-baselines) inside that protocol | Both (my E3) | **Required** | 1 day | < 1 CPU-hour |
| 3 | [Certificates on real dynamics](#3-certificates-on-real-dynamics) | Mine (E1) | **Required** | 1.5 days | a few CPU-hours |
| 4 | [Robustness to estimated and misspecified dynamics](#4-robustness-to-estimated-and-misspecified-dynamics), for certificates and for filter policies | Both (my E2) | **Required** | 0.5 day | 2–4 CPU-hours |
| 5 | [Controlled factorial](#5-controlled-factorial-separate-spatial-from-temporal): innovation correlation × persistence × learner-graph corruption × gap profile | Recommended (gaps 1, 2), trimmed; absorbs my E5 | Recommended | 1 day | about 20 CPU-hours (pilot first) |
| 6 | [Two theory instances](#6-two-theory-instances): B2 regret consequence, B3 slate gain | Mine (E6) | Recommended | 2 hours | minutes |
| 7 | [Setting A v2 at 120 users × 3 subsets](#7-setting-a-v2-at-120-users--3-subsets) | Mine (E4) | Recommended | none | one night |
| 8 | [Open Bandit Dataset](#8-open-bandit-dataset-e-commerce-click-rates): certified pooling on real e-commerce click rates, after a feasibility check | Both, limited form | Recommended | 2 hours + half a day | a few CPU-hours (pilot first) |
| 9 | [Retailrocket e-commerce panel](#9-retailrocket-conditional) | Recommended | If ahead on 16 October | 1.5–2 days | a few CPU-hours |
| 10 | [Scale timing table](#10-scale-timing) | Mine (E8), reduced | Optional | 2 hours | minutes |

## How the two plans compare

| Idea | Source | Verdict | Reason |
| --- | --- | --- | --- |
| Build graphs and eligibility from the training prefix only | Recommended | **Adopt; do first** | Verified in `daily.py` and the audit. Look-ahead in the graph biases results toward the graph, so the positive six-community result (hyperlinks fit held-out shocks best) is the most exposed |
| Zero-play days as missing; availability masks | Recommended | Adopt | 6 zero-play cells in the KuaiRec cohort; `daily.py` currently maps them to a 0.5 rate |
| Frame panels as a monitoring or inspection budget | Recommended | Adopt in the writing | Observing does not change demand, so the exogeneity assumption holds by design. This removes the paper's main stated limitation and my featuring-effect check (E7) |
| Replicate across predefined disjoint panels × disjoint time windows; tune on a development period; policy seeds are not replications | Recommended | **Adopt**; replaces my rolling, overlapping origins | Independent units instead of 3 correlated ones, and no tuning on test |
| Non-stationary, AR and forecaster baselines | Both | Adopt | Same as my E3. The other design adds LARL (RLC 2025) for the latent-factor case, which is optional here |
| Factorial over innovation correlation and persistence, with marginal variance held fixed | Recommended | Adapt (trimmed) | The current benchmark varies one factor at a time. Its full grid (N, T and budgets crossed with ρ, profiles, corruption and gaps, at 100–200 worlds) does not fit on a laptop by 21 October |
| Corrupt the learner's graph while keeping the true environment fixed | Recommended | Adopt | A cleaner test of graph quality than our real-against-rewired comparisons |
| Known, fitted, wrong-order, wrong-covariance and heavy-tailed parameters | Both | Adopt; merged with my E2 | Run the same misspecifications for certificates and for filter policies |
| 100 paired worlds for primary contrasts, 200 for probability-of-correct-selection (PCS) contrasts | Recommended | Partly | 100 worlds for the four primary regret contrasts only. The long paper's metric is regret; PCS studies at 200 worlds belong to the spatiotemporal manuscript |
| AR(7) and 32–64-arm panels primary, AR(20) selective | Recommended | Adopt | Exact filters become about 15× cheaper, which pays for the replications |
| Certificates on real dynamics; B2 and B3 instances; mean-channel depth | Mine | Keep | The recommended file covers the fluctuation channel only. Q2 and Q3 are what the paper adds beyond prior spatiotemporal bandits |
| Retailrocket | Recommended | Conditional | The best new dataset: e-commerce, sessions give a dated co-view graph, and several disjoint test windows. Worth adding only after 1–4 are finished |
| RIPE Atlas DNS | Recommended | Defer | Historical coverage is unverified, it has only 13 arms per client, and it needs a new pipeline. Use it as motivation in the text instead |
| Open Bandit Dataset | Both | **Adopt in a limited form** (experiment 8) | A real e-commerce recommender with randomized logging, known to WWW reviewers. Its uniform-random logs hold only about 60 clicks per item over 7 days (All campaign: 1,374,327 impressions, 80 items, 0.35% click rate). That fits a calibrated mean-channel instance, but not the fluctuation channel or an online-learner replay |

## The experiments

### 1. Chronological real-panel protocol

Applies to both platforms; the shared rules come at the end.

**KuaiRec daily** (changes to `experiments/kuairec/code/daily.py` and `graphs.py`):
- **Graph.** Per origin, rebuild I-coeng and its rewiring from big-matrix rows with timestamps before the cutoff (still non-evaluation users only).
- **Eligibility.** Keep videos with at least 10 plays on every fit-window day: about 250 videos (the audit found 247–255 at origins 28–42).
- **Missing cells.** Zero-play and missing test cells are unavailable: they cannot be chosen and are left out of the oracle.
- **Windows.** Three disjoint 11-day test windows (origins 30, 41 and 52), each fitted on days 1 to F.
- **Panels.** Five predefined, disjoint panels of about 50 videos, stratified by prefix popularity and prefix-graph community. Budgets of 1 and 5 videos per day.
- **Units.** 15 panel-window units.

**Wikipedia** (changes to `experiments/wikipedia/code/`):
- **Selection.** Re-select articles by 2022–2023 median views, requiring complete 2022–2023 data. Later gaps are masked.
- **Graph.** Hyperlinks from each article's revision as of 1 January 2024 (MediaWiki revisions and parse APIs; about two calls per article). Templates expand at their current versions, which we disclose. Optionally, add the September 2023 clickstream as a second dated graph.
- **Protocol.** Fit through 2023 and tune exploration on 2024 development windows. Then refit through 2024 with the hyperparameters frozen, and test on four disjoint 90-day windows in 2025.
- **Panels.** Keep the existing one-domain and six-community panels, re-selected chronologically. Add about six predefined panels of 48 articles, each 4 communities × 12 articles. Publish the panel lists before running, and report every panel, including those where the graph loses.
- **Units.** About 32 panel-window units.

**Shared rules.**
- The unit of replication is a panel × window; seeds are averaged within a unit.
- Report paired differences against iid TS and against the best model, with intervals from a bootstrap over panels, treating windows as blocks.
- Full-history and sparse-history initializations are reported as separate protocols.

**Outcome.** These chronological numbers replace the current ones in the paper, whichever way they move.

### 2. Standard baselines

Run inside protocol 1, with hyperparameters tuned only on development data:

- seasonal naive (same weekday last week);
- per-item exponentially weighted mean;
- discounted and sliding-window Thompson sampling and UCB;
- AR2, with lags fitted on the prefix;
- a pooled gradient-boosted forecaster on lag features, followed by greedy selection;
- LARL, if time allows.

**Decision.** If a tuned discounted bandit matches the filter, the Q4 headline changes from "modelling the dynamics pays" to "forgetting pays".

### 3. Certificates on real dynamics

**a. Inflation check.** Run on the chronological panels: the observed variance inflation of b-day block means against B2's prediction from the prefix fits. At the current panels' lag-1 autocorrelations (0.72 and 0.78), B2 predicts 3.8–4.3× for a 7-day block.

**b. Semi-synthetic certified pooling.**
- **Worlds.** Simulated from the prefix-fitted Wikipedia and KuaiRec models, with weekly block-resampled real innovations and 365–730-day horizons.
- **Learner.** Dynamics re-estimated from a simulated prefix.
- **Pooling.** Components are communities, or prefix-graph clusters. The slates hold 5 or 10 items.
- **Policies.** SP-UCB and successive elimination with iid, B1′ and B1″ certificates.
- **Measures.** Violations, wrong eliminations and regret.

**Decision.** Can Q3's answer cite real web dynamics?

### 4. Robustness to estimated and misspecified dynamics

One sweep, two kinds of learner.

**Conditions:**
- Estimation: prefix plug-in, or online plug-in.
- Misspecification: persistence biased by −0.05; AR(20) truth fitted as AR(1); Student-t shocks with 3 degrees of freedom; graph-correlated truth fitted as independent or as a single factor; a level shift at T/2.

**Learners:**
- **Certificates:** new tags in `coverage.py`, plus the conservative remedy (persistence plus 2 standard errors, and an inflated β).
- **Filter policies:** the factorial world of experiment 5, fitted from a prefix of each simulated world.

**Decision.** Does the abstract say "valid", or "valid when dynamics are estimated conservatively"?

### 5. Controlled factorial: separate spatial from temporal

**World.**
- 64 arms; true lags {1, 2, 7}, plus one AR(20) profile on a subset; marginal variance held fixed.
- Graphs: a grid, plus the two prefix-built real graphs with parameters calibrated to their fits.

**Factors:**
- innovation correlation ρ ∈ {0, 0.4, 0.8};
- persistence: none (iid) or strong;
- learner-graph corruption: 0%, 50% or 100% degree-preserving rewiring, with the true environment unchanged;
- gap profile: separated (level spread twice the fluctuation sd) or near-tie (half).

**Policies.** ST predictive sampling, ST UCB at 1 sd, temporal-only predictive sampling, iid TS, discounted TS.

**Replication.**
- 20 paired worlds per cell, to screen.
- 100 worlds for the four primary contrasts:
    - ST against temporal-only at ρ = 0.8;
    - the real graph against a fully corrupted one;
    - near-tie against separated gaps;
    - iid against persistent.

**Cost.** Measure the timing on a pilot before scaling up. This replaces adding seeds to the 100-arm AR(20) grid, which stays in the paper as the stress test.

### 6. Two theory instances

- **B2 regret consequence.** The optimal component is the under-covered one, the best-arm gap is 0.55 against 0.35, and exposure is bursty. We expect linear mean regret in a share of iid-certified runs.
- **B3 slate gain.** Slates with shock correlation ρ ∈ {0, 0.3, 0.6, 0.9}. Compare the variance of long-run contrasts with the predicted factor (1 − ρ).

Both use the existing `coverage.py`.

### 7. Setting A v2 at 120 users × 3 subsets

This stabilises the 90th-percentile tails and the certificate-gap table. It needs no new code, so it can run tonight.

### 8. Open Bandit Dataset: e-commerce click rates

ZOZOTOWN fashion recommendations, 7 days in late November 2019, logged by a uniform-random policy and by Bernoulli Thompson sampling, with known propensities. Each step is gated by the one before.

Published figures for the uniform-random logs, from Table 1 of [Saito et al., arXiv:2008.07146](https://arxiv.org/abs/2008.07146). Clicks are computed as impressions × click rate:

| Campaign | Impressions | Items | Click rate | Clicks per item over 7 days |
| --- | ---: | ---: | ---: | ---: |
| All | 1,374,327 | 80 | 0.35% | about 60 |
| Men's | 452,949 | 34 | 0.51% | about 68 |
| Women's | 864,585 | 46 | 0.48% | about 90 |

**a. Feasibility check (2 hours).**
- Download the archive (about 413 MB) into the git-ignored `data/obd/`, and stream the uniform-random logs of the three campaigns.
- Count impressions and clicks per item, position and day.
- Measure three things:
    - the spread of item click rates against their sampling error, using a random-effects variance estimate (is there a ranking to learn?);
    - position effects;
    - whether daily item click rates move beyond binomial noise.
- Check the release's licence terms.
- **Go** to step b if the spread of click rates is clearly larger than the sampling error.

**b. Calibrated certified pooling (half a day; the main use).**
- **Truth.** Each item's click rate, estimated from the uniform-random logs of days 4–7 for one position. As in KuaiRec Setting A, the estimates are treated as the true means; we say so.
- **Graphs.** Built from days 1–3 only, so they never see the data that defines the truth:
    - an item-attribute graph from the released item features;
    - an audience-response graph, from each item's click profile across user-feature segments;
    - degree-preserving rewirings of both.
- **Policies.** Reuse Setting A v2 (`setting_a2.py`), which already has bounds for 0/1 rewards:
    - KL-UCB and Bernoulli Thompson sampling;
    - graph-free shrinkage;
    - SP-KLUCB with oracle, calibrated, energy and no certificate. The calibrated widths come from days 1–3.
- **Horizon.** Click rates are low, so regret needs long horizons. Target T = 200,000 rounds with 20 seeds per campaign, after a timing pilot.
- **Outcome.** Q2 in a real recommender at click rates near 0.4%, the regime where pooling should matter most. Does uncertified pooling still fail by dilution, and how wide is the certificate gap there?
- **Labelling.** Report it as semi-synthetic: real click rates, simulated feedback. It is not logged-feedback evidence.

**c. Replay sanity check (optional; one hour after step b).**
- Replay the step-b policies on the uniform-random logs (Li et al., WSDM 2011).
- A single-slot policy matches about 1 in 80 impressions in the All campaign, so a replay sees about 17,000 rounds and about 60 clicks.
- **Expectation:** underpowered. Use it only to check that the rankings do not contradict step b. Report it in the appendix only if its intervals are informative.

**Not attempted before the deadline:**
- fluctuation-channel policies on clicks, which would need a Bernoulli observation filter;
- replay of restless learners, which compresses calendar time and needs a censored-learner estimand.

**Where.** A new folder, `experiments/open_bandit/`, with `README.md`, `design.md`, `code/` and `results/`.

### 9. Retailrocket (conditional)

**Go** on 16 October only if experiments 1–4 are finished and analysed.

**Data and panel.**
- About 4.5 months of events (CC BY-NC-SA 4.0). Start with an ingestion audit.
- Arms: 32–64 product groups selected on the prefix. Reward: hourly log(1 + views).
- Remove the hour-of-week seasonality estimated on training data, so the filter keeps only a few lags. Exact filters cannot carry 168 lags per arm.
- Graph: a co-view graph from training sessions.

**Protocol.** Train 4 weeks, develop on 2 weeks, then test on several disjoint 2-week windows. Use the harness from experiment 1 and the baselines from experiment 2.

**Outcome.** A third real platform, in e-commerce, with a chronologically valid web graph.

### 10. Scale timing

One table: the exact filter's step time and memory for N ∈ {64, 256, 1,024} with 3 lags. The low-rank approximation is deferred.

## Deferred, with reasons

| Item | Reason |
| --- | --- |
| RIPE Atlas DNS | Coverage pilot first; new pipeline; small arm set. Post-submission |
| Open Bandit Dataset: fluctuation channel, and replay of restless learners | Needs a Bernoulli observation filter and a censored-learner estimand, and each item gets only about 9 clicks a day. Post-submission |
| PCS at 200 worlds; N × T × budget grids | For the spatiotemporal manuscript, not the long paper |
| More seeds on the AR(20) grid | Superseded by experiment 5's 100-world contrasts |
| Featuring-effect sensitivity (my E7) | Made unnecessary by the monitoring framing |
| CLUB and GOB.Lin in Setting B; Setting C; Last.fm; R2; Yahoo! R6 | Appendix-level or needs a licence |
| A practical narrow certificate | Method work, not an experiment |

## Schedule and decision gates

| Date | Daytime | Overnight |
| --- | --- | --- |
| 10 Oct | KuaiRec chronology (1); inflation check (3a) on the current panels as a pilot | Setting A v2 expansion (7) |
| 11 Oct | Wikipedia chronology: dated links, prefix selection, new panel lists and collection; harness masks, panels and windows (1). Open Bandit Dataset download and feasibility check (8a) | — |
| 12 Oct | Baselines (2); chronological runs (1, 2) | Remaining runs of 1 and 2 |
| 13 Oct | **Gate A**; certificate robustness (4); factorial code and timing pilot (5) | Factorial screen (5) |
| 14 Oct | Certificates on real dynamics (3b); theory instances (6) | Factorial primary contrasts; filter robustness (4, 5) |
| 15 Oct | 3b runs and analysis; Open Bandit Dataset calibrated instance, code and timing pilot (8b) | Longer 3b horizons; 8b runs |
| 16 Oct | Tables and figures with intervals; replay check (8c), optional; **Gates B and C** | — |
| 17–18 Oct | **Abstract**; Retailrocket ingestion, if go (9) | Retailrocket runs |
| 19–20 Oct | Retailrocket analysis; scale table (10); update the paper | — |
| 21 Oct | **Experiment freeze** | — |

- **Gate A (13 October).** Do the chronological results change a headline: the dynamics gain over iid TS, or the six-community hyperlink advantage? If so, revise the Q1 and Q4 claims before drafting the abstract.
- **Gate B (16 October).** Fix the abstract's three uncertain claims: real-data certificate behaviour (3), the conservative-estimation qualifier (4), and modelling against forgetting (2).
- **Gate C (16 October).** Retailrocket goes ahead only if experiments 1–4 are finished. The Open Bandit Dataset instance (8b) does not wait for this gate: it reuses existing code and is cheap.

## Your decision: who builds the chronological harness

The other agent's [design](../www/spatiotemporal_experiment_design.md) schedules the same KuaiRec chronology fix for 9–11 October. It plans a shared harness in `experiments/st_apps/`, with results in `research/st_applications/`. So far only the audit script exists there. To avoid two diverging implementations, choose one owner:

- **This plan's layout:** fixes in `experiments/kuairec/code` and `experiments/wikipedia/code`, keeping each experiment's design, code, results and report together.
- **The other agent's harness.**

Either works. Running both would split the evidence.
