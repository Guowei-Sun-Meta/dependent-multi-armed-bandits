# Next Experiments: Is the Evidence Sufficient?

> **Superseded for priorities** by [experiment_plan.md](experiment_plan.md), which merges this review with [recommended_spatiotemporal_experiments.md](recommended_spatiotemporal_experiments.md). The evidence review below still stands.

10 October 2026. Reviewed against the claims of the current long paper ([research/claude_opus_10_09_v2](../research/claude_opus_10_09_v2/README.md)), with the WWW deadlines in mind: abstract on 18 October, full paper on 25 October.

## Verdict

**The evidence is broad enough for a coherent submission, but not yet deep enough to survive a critical review.**

- **Breadth is good.**
    - Two real platforms: KuaiRec, plus Wikipedia with two panels.
    - Two simulation families.
    - Each theorem is matched to a named, quantitative test.
- **Three gaps would draw reviewer objections.** Each is cheap to close on the laptop.
    1. **The bridging contribution (Q3) is tested only in simulation, with known dynamics.** The claims that iid certificates fail and innovation certificates stay valid come from a 20-arm toy where the learner knows φ and Q. Nothing yet shows this on real web dynamics, or with dynamics the learner had to estimate. Yet the real panels sit in the failure regime. At the measured lag-1 autocorrelations (0.72 on Wikipedia, 0.78 on KuaiRec), B2's formula predicts that a week of consecutive exposure inflates the variance of a sample mean 3.8× to 4.3×. In the toy, that much inflation broke iid certificates in most bursty runs.
    2. **The real-data baselines are weak.** On the daily panels, the policies are compared with iid Thompson sampling, last value, fit-window means and our own ablations. No standard non-stationary bandit is run (discounted or sliding-window TS, the AR bandit of Chen et al. 2023), and no practical forecaster is either. The headline "modelling dynamics cuts regret 24–44%" could be mostly a gain from *forgetting*, which a discounted bandit also gets.
    3. **Real-panel comparisons rest on 3 forecast origins each.** The noise seeds vary only observation noise, so the effective sample size is 3. Differences of a few percent (graph ±3%, drift 2%, ST against AR-only 1–1.5%) cannot be told apart from zero. The paper reports them as small, but it has no intervals to back that up.
- **Two weaker gaps.**
    - **No logged-feedback evidence.** Every real experiment is a full-information panel that assumes featuring does not change demand.
    - **No scale evidence.** The largest panel has 253 arms.

## Claims against evidence

| Paper claim | Current evidence | Gap | Experiment |
| --- | --- | --- | --- |
| Q1: collaborative graphs carry long-run appeal; profile, social and content graphs carry popularity | 16 graphs, k ∈ {5, 10, 20}, rewards R1 and R3, against rewired nulls | None that matters | — |
| Q1: shocks are correlated, mostly through a common factor; hyperlinks carry community shocks | 3 panels, held-out likelihood | Minor | [E4](#e4-rolling-origins-paired-intervals-and-more-seeds) intervals |
| Q2: certified gains track the rejectable share; uncertified pooling fails by dilution; average gains are shrinkage | Setting A: 60 users (v1), 30 users × 2 subsets (v2); Setting B: 8 instances | Tail percentiles from few users; no multi-user graph-bandit baseline | [E4](#e4-rolling-origins-paired-intervals-and-more-seeds), [E3](#e3-standard-baselines-on-the-real-panels) |
| Q3: iid certificates fail under bursty persistence (B2); innovation certificates stay valid (B1, B1′, B1″) | 20-arm simulation, known dynamics, 2,080 runs with no violation | **No real dynamics, no estimated dynamics, no misspecification** | [E1](#e1-certificates-on-real-web-dynamics), [E2](#e2-certificates-with-estimated-and-misspecified-dynamics), [E6](#e6-two-missing-theory-instances) |
| Q4: modelling dynamics beats iid policies by 24–44%; exploration must match observations per arm | Benchmark (8 seeds); KuaiRec daily and two Wikipedia panels (3 origins each) | **Weak baselines; 3 origins** | [E3](#e3-standard-baselines-on-the-real-panels), [E4](#e4-rolling-origins-paired-intervals-and-more-seeds) |
| Q4: a graph helps decisions only when shocks are community-specific and fluctuations rival level spread | Benchmark +15%; three real panels at 0–3% | Explanation fitted after the fact, not tested | [E5](#e5-when-does-a-graph-help-the-fluctuation-channel) |
| Limitations: exogenous demand; scale | Stated only | Untested | [E7](#e7-exogeneity-sensitivity-featuring-effects), [E8](#e8-scale-filter-cost-and-a-low-rank-approximation) |

## Tier 1: needed for the claims as written (by 16 October)

### E1. Certificates on real web dynamics

**Question.** Do iid certificates fail, and innovation certificates hold, on real attention and engagement dynamics with a daily slate? This gives Q3 a real-data leg.

**E1a. Inflation check (half a day, no bandit).**
- For every article (Wikipedia, both panels) and video (KuaiRec daily), compute the variance of b-day block means for b ∈ {1, 3, 7, 14}, relative to the iid value.
- Compare with B2's prediction from the fitted dynamics, using both the full AR(1, 2, 7) model and its AR(1) approximation.
- **Output:** one figure of predicted against observed inflation per panel. It shows the real panels sit in the regime where iid certificates break, without running a bandit.

**E1b. Certified pooling on real dynamics (semi-synthetic, about 1.5 days of coding).**
- **Worlds.** Simulate panels from the fitted models: the six-community Wikipedia model and the KuaiRec daily model.
    - Use the fitted levels, AR coefficients and graph-shrunk innovation covariance.
    - Draw the innovations by resampling real innovation vectors in weekly blocks. This keeps heavy tails and cross-sectional correlation.
    - The true long-run means are known by construction. The horizon is free, so use 365 to 730 days.
- **Learner.** Re-estimates the dynamics from a simulated 365-day fit window, as on the real panels.
- **Components.** Communities (Wikipedia), or graph clusters (KuaiRec). ε_c is the oracle within-component range.
- **Policies.**
    - SP-UCB and successive elimination over a 10-slot daily slate.
    - Certificates: iid, B1″ (correlated shocks), and B1′ as the "shocks independent" approximation.
- **Measures.** Share of runs with any violation, rounds violated, wrong eliminations of a top-10 article, and mean regret.
- **Code.** Reuse the filter in [wikipedia/code/attention.py](wikipedia/code/attention.py) and the bounds in [certificates_under_persistence/code/coverage.py](simulations/certificates_under_persistence/code/coverage.py). The innovation regression needs extending from AR(1) with single pulls to AR(1, 2, 7) with slates.
- **Cost.** A few CPU-hours (150–253 arms; one panel run takes 3–13 s now).
- **Where.** A new folder, `experiments/simulations/certificates_on_real_dynamics/`.

**What the outcomes mean.**
- If iid certificates miscover here, Q3's answer gains its strongest sentence: on fitted Wikipedia and KuaiRec dynamics with a daily slate, iid certificates are violated in X% of runs and remove a top article in Y%.
- If they do not (for example, because slates rotate items fast enough), report the exposure pattern under which they fail. In that case, soften "bursty exposure is the norm for slates" in the paper.

### E2. Certificates with estimated and misspecified dynamics

**Question.** Is B1″ still valid when φ, Q and r are estimated, or when the model is wrong? The paper currently says "never violated" only under correct specification.

**Design.** Extend [certificates_under_persistence](simulations/certificates_under_persistence/design.md) with new tags (`_estimated`, `_misspecified`).

**Estimation.**
- Plug-in from round-robin burn-ins of 200 or 1,000 rounds.
- An online plug-in, re-estimated every 250 rounds.

**Misspecification.**

| Condition | Truth | Model |
| --- | --- | --- |
| Biased persistence | AR(1), φ | AR(1), φ − 0.05 (too little persistence) |
| Wrong order | AR(20) with weights ∝ exp(−r/6), sum 0.97 (the benchmark's) | AR(1) |
| Heavy tails | Student-t shocks, 3 degrees of freedom, unit variance | Gaussian |
| Ignored correlation | Correlated shocks | B1′ (assumes independent shocks) |
| Level shift | μ jumps by 0.1 for one component at T/2 | Fixed μ |

**Remedy arm.** Plug in a conservative persistence, φ̂ plus 2 standard errors, and an inflated β.

**Cost.** About 8,000 runs at about 0.7 s each (the current plug-in sweep's rate), so roughly 1.5 CPU-hours, or 20 minutes on 6 workers.

**What the outcomes mean.**
- If B1″ stays valid with estimated dynamics, say so in the abstract.
- If it breaks under some condition, report that condition and show that the conservative plug-in restores validity. The claim then becomes "valid when dynamics are estimated conservatively". That is still a contribution, and more honest.

### E3. Standard baselines on the real panels

**Question.** Is the gain from modelling dynamics, or merely from forgetting old data?

**Daily panels** (KuaiRec daily and both Wikipedia panels), each run as a 10-slot top-k version:
- **Non-stationary bandits:**
    - discounted Thompson sampling (Raj and Kalyani 2017);
    - sliding-window Thompson sampling (Trovò et al. 2020);
    - discounted and sliding-window UCB (Garivier and Moulines 2011).
  Tune the discount or window on the fit window of the first origin, then freeze it.
- **AR bandit:** AR2 (Chen, Golrezaei and Bouneffouf, NeurIPS 2023), with AR parameters fitted in the fit window.
- **Forecast-then-greedy:**
    - seasonal naive (same weekday last week);
    - a per-item exponentially weighted mean;
    - a pooled gradient-boosted forecaster on lag features (scikit-learn's `HistGradientBoostingRegressor`, already in the requirements). Unobserved lags are filled with the model's own forecasts.

**Setting B (optional; the most expensive item).**
- Add CLUB (Gentile et al. 2014) and GOB.Lin (Cesa-Bianchi et al. 2013).
- Use 16-dimensional I-mf item embeddings as contexts, so GOB.Lin's matrix is 4,800 × 4,800.
- Several CPU-hours per instance. Run it only if the panels finish early.

**Cost.** Current panel runs take 9 (KuaiRec) to 42 (six-community Wikipedia) CPU-minutes for the whole grid, and the new baselines are cheaper than the filters. About 1 day, mostly coding.

**What the outcomes mean.**
- If a tuned discounted bandit matches the filter, the Q4 headline must change from "modelling dynamics pays" to "forgetting pays". The filter's remaining case is then its certificates and interpretability.
- If the filter still wins clearly, the claim becomes much harder to dismiss.

### E4. Rolling origins, paired intervals and more seeds

**Question.** Which differences are real?

**Real panels.**
- **KuaiRec daily:** origins F = 21, 23, …, 49, with 14-day test windows (15 origins).
- **Wikipedia:** origins every 60 days from day 365 to day 1,341 (17 origins), with 120-day test windows.
- 3 noise seeds per stochastic policy.
- Report every policy as a paired difference against iid TS and against the best model. Use 95% intervals from a moving-block bootstrap over origins; overlapping windows make a naive interval too narrow.
- Any difference whose interval covers zero is called a tie.

**Simulations.**
- **Benchmark:** 22 more seeds (30 in total) for the six headline policies (ST and AR predictive sampling, ST UCB at 2 sd, UCB1, TS, SpectralUCB). The three filter policies took 330–380 s per run on the loaded machine, and the others under a second, so this is about 20 CPU-hours: one night on 6 workers.
- **Setting A v2:** 120 test users × 3 subsets instead of 30 × 2, to stabilise the 90th-percentile tails and the certificate-gap table. About 90–220 s per task, so 9–22 CPU-hours: one night.

**Cost.**
- Real panels: about 3–4 CPU-hours (mostly the six-community panel).
- Simulations: two overnight jobs.
- Code changes are small: `ORIGINS` and a test-window argument in `daily.py` and `attention.py`, plus one bootstrap function in `experiments/paper/deepdive.py`.

**Likely casualties.** The graph's ±3% on six communities, drift's 2%, and ST against AR-only at 1–1.5% will probably become ties. The paper already calls them small, so the intervals make that statement rigorous instead of changing the story.

## Tier 2: sharpen the story (16–21 October)

### E5. When does a graph help the fluctuation channel?

**Question.** The synthesis explains, after the fact, why the graph helped on the benchmark (+15%) but barely on real panels. The graph's value should grow with two quantities: the share of a shock explained by neighbours (R²), and the ratio of fluctuation sd to level spread. Test that explanation as a prediction.

**Design.**
- **Simulation.** Benchmark sweep over level spread sd ∈ {0.25, 0.5, 1, 2} and spatial strength (resolvent parameter ∈ {0, 1, 5}).
    - Policies: ST against AR-only predictive sampling only.
    - 10 seeds, T = 2,000: about 24 CPU-hours (about 365 s per run), one night on 6 workers. Halve T if the night is short.
- **Real data.** Place the four environments on the resulting map:
    - benchmark: 1.0 against 0.5, R² 0.46;
    - six communities: 0.48 against 0.91, R² 0.36;
    - one domain: 0.41 against 1.05;
    - KuaiRec: 0.46 against 0.54, weak shock correlation.
- **Real-data intervention.** Re-run the six-community panel on level-matched subsets: articles within a narrow band of long-run level. This raises the ratio without changing the graph. Minutes, with an article-subset option in `attention.py`.

**Outcome.** If the real gains fall where the map predicts, the "when does the graph help" paragraph becomes a quantitative, tested statement.

### E6. Two missing theory instances

- **B2 regret consequence.** In the current toy, invalid iid certificates mostly under-cover suboptimal arms, so regret barely moves.
    - Build the instance the theory map asks for: the optimal component is the under-covered one, with a larger best-arm gap (0.55 against 0.35) and bursty exposure.
    - Show linear mean regret in a constant share of iid-certified runs, and none with B1″.
    - This also serves the open "B2 linear-regret instance" item in the theory map.
- **B3 slate contrast gain.** Use slates of k arms with shock correlation ρ ∈ {0, 0.3, 0.6, 0.9}.
    - Compare the empirical variance of long-run contrasts with the predicted factor (1 − ρ), and the rounds needed to certify a component rejection.
    - The theory map lists this as having no dedicated test yet.
- **Cost.** Minutes each, with the existing `coverage.py`.

### E7. Exogeneity sensitivity: featuring effects

**Question.** Every panel experiment assumes featuring does not change organic demand, the paper's main stated limitation. How much does that assumption drive the results?

**Design.**
- On both Wikipedia panels, add a featuring effect: a featured article gains τ ∈ {0, 0.1, 0.3} in log views, decaying with the fitted AR dynamics.
- The oracle accounts for the effect.
- Check whether the policy ranking and the gaps survive.

**Cost.** Minutes.

### E8. Scale: filter cost and a low-rank approximation

**Question.** Does the method reach web scale? The exact joint filter's state has dimension N(p + 1), and its cost grows like N²p². The largest panel has 253 arms.

**Design.**
- Time the exact filter and measure its memory for N ∈ {100, 300, 1,000, 3,000} with 3 lags.
- Implement one approximation: the top-r eigenvectors of Q_G plus a diagonal, with r ∈ {10, 50}.
- Report the speed-up and the regret lost on the benchmark and the six-community panel.

**Cost.** About 1 day of coding; minutes of compute.

## Tier 3: after submission, or only if ahead of schedule

- **E9. Logged-feedback replay on the Open Bandit Dataset.**
    - The data: about 26 million impressions over 7 days on ZOZOTOWN (late November 2019), three campaigns, each logged by a uniform-random or Bernoulli TS policy. The "all" campaign has 80 items and 3 positions.
    - Uniform-random logs allow unbiased replay (Li et al., WSDM 2011) of context-free policies. This is the standard answer to "show us real feedback", and WWW reviewers know it.
    - **Feasibility first (1 day):** build an hourly click-rate panel per item from the random-policy logs. Check for persistence beyond sampling noise, and for cross-item shock correlation.
    - **Risk:** clicks are rare and the log covers only 7 days, so the fluctuation channel may be invisible. Go ahead only if the feasibility check finds persistence.
- **E10. Yahoo! R6 news slot.** It needs a Webscope licence, which is your decision. The design is in [www/st_applications.md](../www/st_applications.md).
- **E11. A practical certificate (method work).** Per-user calibration recovers about half of the oracle's gain. A narrow, valid certificate learned online is the paper's main open problem. It needs a method, not just a run, so it is out of scope before 25 October.
- **Kept cut:** Setting C (product graph), the Last.fm social graph, and R2 sensitivity. They are listed as future work in the proposal.

## Schedule

The machine has 8 cores and 8 GB, so at most 6 workers. Heavy jobs run overnight, one at a time.

| Dates | Daytime | Overnight |
| --- | --- | --- |
| 10–11 Oct | E1a; E2 (code and runs); rolling-origin code for E4 | E4: benchmark seeds |
| 12–13 Oct | E3 baselines (code, then runs on the three panels); E4 real-panel runs | E4: Setting A v2 at 120 users × 3 subsets |
| 13–15 Oct | E1b (semi-synthetic certified pooling) | E5: simulation sweep |
| 16 Oct | E4 analysis (paired intervals); update the paper's tables | — |
| 17–18 Oct | **Abstract**, worded from the E1–E3 outcomes; E6 | — |
| 19–21 Oct | E5 real-data part; E7; E8. **Experiment freeze on 21 October** | — |
| 22–25 Oct | Writing and figures | — |

**Decide by 16 October (before the abstract):**
- whether Q3 claims real-data validity (E1);
- whether the certificate claim needs the "estimated conservatively" qualifier (E2);
- whether Q4's headline is "modelling" or "forgetting" (E3).

## What not to do before the deadline

- Add new datasets beyond the E9 feasibility check.
- Widen the benchmark grid beyond E5.
- Run large hyperparameter searches. Tune each baseline once on the first origin's fit window, freeze it, and report that protocol.

## Sources

- Open Bandit Dataset: Saito et al., "Open Bandit Dataset and Pipeline: Towards Realistic and Reproducible Off-Policy Evaluation", NeurIPS 2021 Datasets and Benchmarks ([arXiv:2008.07146](https://arxiv.org/abs/2008.07146); [documentation](https://zr-obp.readthedocs.io/en/stable/about.html)).
- AR2: Chen, Golrezaei and Bouneffouf, "Non-Stationary Bandits with Auto-Regressive Temporal Dependency", NeurIPS 2023 ([proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/186a213d720568b31f9b59c085a23e5a-Abstract-Conference.html); [arXiv:2210.16386](https://arxiv.org/abs/2210.16386)).
- Discounted TS: Raj and Kalyani, "Taming Non-stationary Bandits: A Bayesian Approach", 2017. Sliding-window TS: Trovò, Paladino, Restelli and Gatti, JAIR 2020. Discounted and sliding-window UCB: Garivier and Moulines, ALT 2011.
- CLUB: Gentile, Li and Zappella, ICML 2014. GOB.Lin: Cesa-Bianchi, Gentile and Zappella, NeurIPS 2013.
- Replay evaluation: Li, Chu, Langford and Wang, "Unbiased Offline Evaluation of Contextual-Bandit-Based News Article Recommendation Algorithms", WSDM 2011.
