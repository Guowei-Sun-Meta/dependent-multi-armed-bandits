# Experiments for the KDD 2027 paper

18 October 2026. Proposals for new experiments that suit KDD's research track and use the methodology of the correlated-arms paper. Nothing here has been run; each entry says what the data is, what decision it supports, which theory result it tests, and what it costs on the 8-core laptop. The existing experiments and their verdicts are in [experiments/report](../experiments/report/README.md); the earlier application designs (Wikipedia, KuaiRec, Retailrocket, RIPE Atlas, OBD) are in [experiments/recommended_spatiotemporal_experiments.md](../experiments/recommended_spatiotemporal_experiments.md) and are not repeated.

## What KDD rewards, and what the method offers

KDD reviewers look for a decision problem on real logged data, a method that is tested where it is supposed to fail as well as where it works, standard public datasets, and a release of code. The paper's methodology gives four reusable tools:

| Tool | Theory | What it needs from a dataset |
| --- | --- | --- |
| **T1. Certified pooling** along a mined graph: pool only components whose certified diameter is below their gap, and measure gains against a rewired null and graph-free shrinkage | A1, A4, N1 | A graph mined from a prefix of the log; many arms with a shared mean structure |
| **T2. Innovation-regression confidence**, valid at every round under adaptive, restless sampling | S1, S2, B1, B1″ | Rewards that persist; a fitted AR or state-space model; irrevocable decisions (drop, stop, promote) |
| **T3. The inflation diagnostic**: the long-run variance of a block mean relative to its iid variance, from the fitted autocovariance | B2, B3.1 | Arms observed in consecutive blocks (daily slates, experiment cells, sensor dwell) |
| **T4. Slate contrasts**: correlated shocks make within-slate comparisons cheaper by the long-run contrast formula | B3.2, S6 | Several arms observed per round with correlated shocks |

The experiments below are chosen so that at least one of T2–T3, the bridge results, is the headline, because those are the results the current evidence supports most strongly and the ones no prior work covers.

## Ranked proposals

| Rank | Experiment | Dataset (public) | Decision | Tools | Headline question | Effort |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | [Sequential stopping in online experiments with day-to-day carryover](#1-sequential-stopping-in-online-controlled-experiments) | ASOS Digital Experiments (78 A/B tests, daily aggregates); Upworthy Research Archive (32,487 headline tests) | When to stop a test or drop a variant | T2, T3, T1 | Do iid always-valid p-values stop early too often when daily metrics are autocorrelated, and does innovation confidence fix it? | 4–6 days |
| 2 | [Replay of certified pooling on randomly exposed videos](#2-certified-pooling-with-real-feedback-kuairand) | KuaiRand (Kuaishou, two weeks of randomly inserted videos) | Which video to insert | T1, T3 | Does certified pooling along a prefix co-engagement graph beat shrinkage on *real* click feedback, not semi-synthetic means? | 5–7 days |
| 3 | [Budgeted sensing on road networks](#3-budgeted-sensing-on-road-and-air-quality-sensor-networks) | METR-LA (207 sensors) and PEMS-BAY (325 sensors), 5-minute speeds, road-distance graph; KDD Cup 2018 Beijing air quality (35 stations, hourly) | Which k sensors to query per interval | T2, T3, T4 | Does the innovation certificate stay valid with estimated dynamics at N = 200–300, and does the road graph shape shocks or means? | 4–6 days |
| 4 | [Pooling across users on a real social graph](#4-pooling-across-users-on-a-social-graph-lastfm) | HetRec 2011 Last.fm (1,892 users, 12,717 friendships, listening counts, tags) | Which artist to recommend to a cold user | T1 | Does a friendship graph carry mean correlation, where KuaiRec's social graph was too sparse to tell? | 3 days |
| 5 | [News slates under bursty exposure](#5-news-slates-under-bursty-exposure-mind) | MIND (Microsoft News, six weeks of impression logs) | Which k articles to show per day | T3, T4 | Do daily slates of the same articles inflate iid confidence by the predicted factor, and do correlated shocks help within-slate ranking? | 4–5 days |
| 6 | [Rebalancing budget on a bike-share network](#6-rebalancing-budget-on-a-bike-share-network-citi-bike) | Citi Bike trip data (monthly CSVs, station coordinates) | Which stations to service each shift | T2, T4 | A second physical network with strong daily seasonality; a check on lag-order misspecification | 3–4 days |

**Recommended set for the February paper:** 1 and 2, with 3 as the appendix robustness study. Experiment 1 gives the bridge results a decision problem that every KDD reader has (stopping an A/B test), experiment 2 gives the mean-channel results their first logged-feedback evidence, and experiment 3 puts the certificate on the field's canonical spatiotemporal data at ten times the current arm count. Experiments 4–6 are fallbacks if 1 or 2 fail a feasibility check.

## 1. Sequential stopping in online controlled experiments

**Why KDD.** Online experimentation is a recurring KDD applied topic, always-valid inference (mSPRT, confidence sequences) is its standard tool, and the assumption those tools make, iid observations across days, is exactly what B2 says fails when daily metrics carry over. The paper would be the first to measure the inflation on public experiment logs and to supply a valid replacement.

**Data.**
- *ASOS Digital Experiments Dataset* (Liu, Cardoso, Couturier and McCoy, [arXiv 2111.10198](https://arxiv.org/abs/2111.10198); data at [osf.io/64jsb](https://osf.io/64jsb), datasheet at [osf.io/vyuce](https://osf.io/vyuce)): 78 A/B tests from a fashion e-commerce platform, 2019–2020, with daily checkpoints of sample size, mean and variance per arm, several metrics per test (241 test–metric series). No user-level data; the binary metric's meaning is withheld. Seventeen tests have more than two arms.
- *Upworthy Research Archive* (Matias, Munger, Aubin Le Quere and Ebersole, *Scientific Data* 2021, [doi:10.1038/s41597-021-00934-7](https://doi.org/10.1038/s41597-021-00934-7); data at [osf.io/jd64p](https://osf.io/jd64p)): 32,487 headline tests, 150,817 arms, 538 million assignments, January 2013 to April 2015; impressions and clicks per arm per test. Tests between 25 June 2013 and 10 January 2014 have randomization problems and a `randomization_imbalance_risk` flag; exclude them.

**Decision and arms.** Each experiment is a bandit whose arms are its variants and whose reward is the daily metric. The decision is irrevocable: stop the test and ship a variant, or drop a variant. The analyst's tool is a confidence statement checked daily.

**Observation model.** ASOS reports daily means for *every* arm, so every arm is observed every day: the full-field case in which S3 is exact and the long-run variance of the running mean is the zero-frequency spectral density. Fit AR(p) with p ≤ 7 to the daily treatment–control difference series per test, on the first half of each test, and estimate the inflation factor f(b) of a b-day block mean (T3). Upworthy tests are short (hours to days), so there the unit is the test, not the day; use it for T1 below.

**What is tested.**
- *B2 (T3).* Compute the iid mSPRT or iid confidence-sequence stopping rule on each ASOS series at α = 0.05 and record how often it stops in the first half of the test on a metric whose second-half estimate reverses the sign. Compare the realized early-stop rate with the rate predicted from the fitted inflation factor. The claim to test: the early-stop rate exceeds its nominal level by about the factor 2Φ(−√(2ℓ(1 − φ)/(1 + φ)))/2Φ(−√(2ℓ)) of B2, with φ the fitted lag-one persistence of the difference series.
- *B1 (T2).* Run the innovation-regression confidence sequence on the same series with the fitted dynamics. Record coverage against the end-of-test estimate and the stopping time. The expected finding, from the Wikipedia-calibrated worlds, is that it is valid and slower; the question is by how much on daily-granularity experiments with 30–60 checkpoints, where the N-dimensional log-determinant cost does not arise (N = 2).
- *Certified pooling across experiments (T1), on Upworthy.* Headlines within one package share a story; the package is a component with a certified diameter taken from the historical distribution of within-package click-rate ranges (a calibrated certificate, as in Setting A v2). Pool clicks within a package when the certificate is below the gap to the leading package, and measure how many fewer impressions the certified rule needs to reach a fixed-confidence choice of the best headline than per-arm successive elimination. Compare with uncertified package pooling (N1's failure) and with empirical-Bayes shrinkage toward the package mean.

**Protocol.** Chronological within each test. Tuning (AR order, α regularization, calibration quantile) on the first third of the tests by start date; report on the rest. Replication units are tests (61 two-arm ASOS tests; thousands of Upworthy packages), which are the independent units the current paper lacks.

**Risks.** ASOS daily aggregates may show little autocorrelation after the cumulative-mean trend is removed; the first task is to measure the lag-one correlation of daily differences across the 241 series, and the experiment proceeds only if the median |φ| exceeds about 0.2. The withheld metric meaning limits interpretation to "a binary conversion-type metric".

**Effort.** Data download is minutes; the analysis is standard-library Python over small tables; 4–6 working days including the write-up.

## 2. Certified pooling with real feedback (KuaiRand)

**Why KDD.** The present evidence for the mean channel is semi-synthetic: one observed watch ratio per user–video stands in for the true mean. KuaiRand (Gao et al., CIKM 2022, [arXiv 2208.08696](https://arxiv.org/abs/2208.08696); data at [kuairand.com](https://kuairand.com), Zenodo [10439422](https://zenodo.org/records/10439422), 11 GB) inserts randomly chosen videos into users' feeds for two weeks and logs twelve feedback signals with timestamps. Random exposure allows unbiased replay evaluation of a bandit policy (the rejection-sampling replay of Li et al.), so certified pooling can be scored on *logged clicks* rather than a simulator.

**Decision and arms.** For each user session with a random insertion, the bandit chooses the video to insert from the random-exposure pool; replay accepts the round when the logged random video matches the policy's choice. Arms are the pool videos (KuaiRand-1K has about 7,000 random-exposure videos; restrict to the 300–1,000 most exposed so each arm has enough matches). Reward is `is_click` or a long-view indicator.

**Graph.** Item co-engagement and factorization graphs built only from the *normal* (non-random) log before the random-exposure window, so the graph is chronologically valid and leakage-free in the same sense as the KuaiRec pipeline. Rewired and Erdős–Rényi nulls as in Phase 1.

**What is tested.**
- *A1 and N1 (T1).* Certified SP-KLUCB with calibrated certificates (quantiles of within-component click-rate ranges over a tuning half of the users) against KL-UCB, Thompson sampling, graph-free shrinkage, Spectral TS and CLUB-style clustering, scored by replay reward per accepted round. The prediction from Setting A v2: shrinkage carries the average gain; certified pooling adds a few percent over its rewiring; uncertified pooling has heavy tails across users.
- *B2 (T3) on the daily click-rate panel.* Aggregate the random-exposure clicks per video per day; fit AR dynamics on the first week; measure block-mean inflation on the second week and compare with the Wikipedia numbers (a week of views carried the information of 1.3–1.9 days). This tells whether short-video click rates persist as attention does.

**Protocol.** Users split 50/50 by a fixed seed for tuning and test; replay over the test users' random insertions in timestamp order. Report per-accepted-round reward with user-cluster bootstrap intervals, and the number of accepted rounds per policy (replay acceptance falls with pool size, which bounds the usable arm count).

**Risks.** Replay acceptance: with a pool of 300 arms and about a million random insertions, each policy gets on the order of 3,000 accepted rounds, enough for a bandit with components but not for per-arm learning of 300 arms; the design should use 100–300 arms. The random-exposure videos were inserted into a feed whose position effects are logged but not controlled; condition on position or use position-1 only, as the OBD pilot did.

**Effort.** Download and preprocessing 1 day (11 GB; keep only the random-exposure table and the prefix of the normal log); graph building reuses `experiments/kuairec/code/graphs.py`; policy code reuses Setting A v2; 5–7 days.

## 3. Budgeted sensing on road and air-quality sensor networks

**Why KDD.** METR-LA and PEMS-BAY are the field's standard spatiotemporal datasets (Li, Yu, Shahabi and Liu, ICLR 2018, [arXiv 1707.01926](https://arxiv.org/abs/1707.01926); data and road-distance adjacency in the [DCRNN repository](https://github.com/liyaguang/DCRNN)). Every KDD reviewer knows them. They give the paper a setting with a *physical* graph that unambiguously shapes shocks (congestion propagates along the road), hundreds of arms, strong persistence, and natural bursty exposure.

**Data.** METR-LA: 207 loop detectors on Los Angeles highways, 5-minute average speeds, 1 March to 30 June 2012, directed adjacency from driving distance. PEMS-BAY: 325 Bay Area sensors, 1 January to 31 May 2017. Both have missing readings (sensor failures), which the innovation regression handles as unobserved coordinates. Air quality: the KDD Cup 2018 panel, 35 Beijing stations, hourly PM2.5 for 2017 to March 2018 ([Zenodo 3902671](https://zenodo.org/record/3902671)), with a distance kNN graph; it adds a daily seasonal lag (24) that tests lag-order selection.

**Decision and arms.** A monitoring budget: each interval the learner may query k sensors (bandwidth-limited telemetry, or dispatching k incident-response units), and the reward is the congestion signal (speed deficit below free flow, or PM2.5 above a threshold). The learner observes only the queried sensors; the unqueried field is hidden until queried. This is the KuaiRec daily-slot design at ten times the arm count, with a graph whose role is known.

**What is tested.**
- *B1 validity with estimated dynamics at scale (T2).* Fit AR(p) with graph-correlated innovations on month 1; run the certificate on months 2–4 with k ∈ {5, 20}; coverage of the long-run mean deficit per sensor. The report flags that B1 holds with a 365-round prefix and fails with a 100-round prefix; here the prefix is 8,000 five-minute rounds, so validity should be clean, and the question becomes the width.
- *Two graph roles (T1 against T2).* Is the long-run mean deficit smooth on the road graph (role 1, certifiable pooling) or only the shocks (role 2)? Compute the energy quotient of the mean field against rewired nulls as in Phase 1. Prediction: the mean field is smooth on PEMS-BAY (homogeneous freeway) and not on METR-LA (mixed), so certified pooling helps on one and not the other, and both show shock correlation.
- *Bursty exposure (T3).* Compare one-at-a-time querying with dwell blocks of 12 intervals (one hour on the same sensors). Measure iid-certificate miscoverage against the B2 prediction from the fitted autocovariance.
- *Slate contrasts (T4).* With k = 20, compare the variance of within-slate contrasts for neighbouring and distant sensor pairs against the long-run contrast formula.

**Protocol.** Chronological: fit on the first month, tune on the second, test on the rest, with three weekly test windows as replication units per dataset. Policies: iid TS, iid UCB, last value, EWMA, joint Kalman UCB, with and without the graph in the innovation covariance.

**Risks.** The policy comparison may again show last value matching the filter, as on KuaiRec; that is a result, not a failure, if the certificate story holds. Memory: a 325-dimensional Kalman filter at 5-minute resolution over 4 months is about 35,000 steps of 325 × 325 updates, a few minutes per policy run in NumPy.

**Effort.** 4–6 days; the panel harness from `experiments/kuairec/code/daily.py` applies with a loader change.

## 4. Pooling across users on a social graph (Last.fm)

**Why KDD.** Setting B on KuaiRec could not test a social graph: 80 of 1,411 users and 47 edges. HetRec 2011 Last.fm ([grouplens.org/datasets/hetrec-2011](https://grouplens.org/datasets/hetrec-2011/), 2.5 MB, non-commercial licence) has 1,892 users, 12,717 bidirectional friendships, listening counts for 92,834 user–artist pairs and tag assignments. It is the standard small social-recommendation benchmark, and the social graph is the one Web graph that comes from users rather than from the platform's own logging.

**Decision and arms.** Setting B: users arrive at random, the policy recommends one of 100 artists, the reward is the normalized listening count (semi-synthetic, as in Setting B). The user graph is friendship; comparison graphs are tag co-usage and listening co-engagement, with rewired nulls and a complete graph.

**What is tested.** A1 and N1 for user-side pooling: certified SP-KLUCB with oracle and calibrated certificates against per-user TS, global TS and user-graph Gaussian TS. The alignment diagnostics (energy quotient, taste correlation) come first and decide whether friendship carries mean correlation at all; the paper can report the quotient even if the bandit result is null.

**Risks.** Listening counts are heavy-tailed and sparse (49 artists per user on average); the semi-synthetic truth is a 1,892 × 100 matrix with many zeros, so a reward model (log counts, or implicit-feedback probability) must be fixed before any run.

**Effort.** 3 days; everything reuses `setting_b.py`.

## 5. News slates under bursty exposure (MIND)

**Why KDD.** MIND (Wu et al., ACL 2020; [msnews.github.io](https://msnews.github.io), Microsoft Research licence; details not re-verified for this note) logs about six weeks of Microsoft News impressions in late 2019, with the articles shown in each impression and the clicks. Articles are shown in slates, the same articles recur for days, and their click rates decay: the bursty, persistent regime of B2 with real slates.

**Decision and arms.** Each day, choose k articles for a slot from the articles live that day; arms are articles, the reward is the day's click-through rate from the logged impressions (a panel, as in the KuaiRec daily slot, since impressions are not randomized). The graph is the entity and category graph from the article metadata, with a co-click graph from the first two weeks.

**What is tested.** T3: block-mean inflation of article CTR over consecutive days against the fitted autocovariance; T4: within-slate contrast variance for articles sharing entities against the long-run contrast formula; the slate policies from the toy benchmark against last value and EWMA.

**Risks.** Impressions are policy-biased, so the panel is an observed field, not causal feedback. Article lifetimes are short (days), so the stationary AR model needs an explicit decay term; that is a model extension, not a reuse.

**Effort.** 4–5 days.

## 6. Rebalancing budget on a bike-share network (Citi Bike)

**Why KDD.** Urban computing is a KDD staple, and Citi Bike publishes every trip ([citibikenyc.com/system-data](https://citibikenyc.com/system-data), monthly CSVs with start and end stations and times). Arms are stations, the hourly reward is net outflow (bikes leaving minus arriving), the graph is station proximity and the trip-flow graph, and the decision is which k stations a rebalancing crew visits each shift.

**What is tested.** T2 and T4 with strong daily and weekly seasonality, which stresses lag-order selection (the report's open item 4). Fit on one month, test on the next two; a certificate that ignores the lag-24 and lag-168 autocovariance should fail the coverage check by a predictable margin, and one with weekly lags should hold.

**Risks.** Net outflow is a proxy; the actual rebalancing objective involves capacity. Treat it as a monitoring benchmark like Wikipedia.

**Effort.** 3–4 days.

## Feasibility checks before committing (one day in total)

1. ASOS: download, compute the lag-one autocorrelation of the daily treatment–control differences over the 241 series. Go if the median |φ| > 0.2.
2. KuaiRand: download the random-exposure table only; count random insertions per video; confirm that 100–300 videos have at least 2,000 random exposures each.
3. METR-LA: load `adj_mx.pkl` and the speed panel from the DCRNN repository; compute the energy quotient of the mean speed-deficit field against a rewired null.

## What the paper gains

With experiments 1–3 the evidence section would have: logged-feedback evidence for the mean channel (KuaiRand, replacing semi-synthetic KuaiRec as the headline), a decision problem for the bridge results that KDD readers run themselves (A/B stopping), and a canonical spatiotemporal dataset with hundreds of arms for the certificate at scale. The replication units become tests, users and weeks, which fixes the "15 units sharing windows" weakness in the current threats-to-validity list.
