# Correlated Arms on the Web: Research Proposal (WWW 2027 long paper)

As of 9 October 2026; restructured to merge the spatiotemporal work. Working title: *Certified Learning with Correlated Arms: When Web Graphs and Persistence Make Bandits Share Information*.

Target: The ACM Web Conference 2027 (Dublin, 10–14 May 2027). **Abstract due 18 October 2026, full paper due 25 October 2026**, AoE, on OpenReview (`Conference_Long_Papers`). 8 pages plus references and appendix, double-blind. Reviewers need not read past page 8, so theorem statements go in the main text and proofs in the appendix. Recommended track: "Search, Recommendation, and Retrieval-Augmented AI" (it lists online learning for recommendation). The alternative is "Graph Algorithms and Modeling for the Web".

**Go/no-go: 20 October.** If the new bridging theorem (B1 below) is not proved by then, fall back to two papers: correlated means here, and a dynamics short paper (abstract 9 November, paper 16 November; plan in [st_short_paper.md](st_short_paper.md)).

## Summary

The subject is **correlated arms**. On the web, arms are almost never independent:

- Similar items have similar long-run appeal.
- Engagement shocks persist for days and spread across related items.

Graphs (co-engagement, factorization, links, geography) are the **tool** for encoding that correlation. They are not the object of study.

One model covers both kinds of correlation:

```math
Y_t=f_{a_t,t}+\xi_t,\qquad f_{i,t}=\mu_i+z_{i,t},\qquad z_t=\sum_{r=1}^{p}A_r z_{t-r}+\eta_t,\quad \eta_t\sim N(0,Q_G)
```

- **Mean channel:** the long-run means μ are correlated across arms. A graph supplies a certified restriction, an energy bound μᵀLμ ≤ S² or component diameters.
- **Fluctuation channel:** the deviations z are persistent (AR) and correlated across arms (Q_G built from a graph).
- **iid bandits** are the special case with no persistence and diagonal Q_G. **Static graph bandits** add the mean channel only.

**Message.** Correlation is valuable but dangerous:

- Graph structure lets a learner reject groups of arms without sampling them, but only with a valid certificate.
- Persistence makes every observation worth less for learning means (the long-run variance) and more for predicting near-term rewards.
- Methods that ignore persistence produce invalid certificates. Methods that trust an unverified graph incur linear regret.

We give certified policies and guarantees for both channels, lower bounds, and evidence on KuaiRec.

## Contributions

Each theorem is labelled by where it comes from: **[A]** the alignment paper (`research/alignment_paper/`), **[S]** the spatiotemporal paper (`research/spatiotemporal_bandits/`), **[P]** the predictive and AR notes (`research/predictive_ar1/`, `two_arm_ar1/`, `ar_p_bandits/`), **[New]** this paper. The detailed map and proofs are in [research/correlated_arms/README.md](../research/correlated_arms/README.md).

1. **One model for correlated arms** with two channels, and two regret notions:
    - **Mean regret:** against the best long-run mean.
    - **Dynamic regret:** against the oracle that knows every arm's current reward.
2. **Mean channel, with iid noise.**
    - Certified pooling regret bound (SP-UCB, GDE-UCB) **[A]**.
    - Path-versus-clique information separation: graph geometry, not diameter, sets the cost **[A]**.
    - Misaligned graphs cause linear regret **[A, repo note]**.
    - Certified graph-error inflation **[A]**.
3. **Bridge: both channels together.**
    - **B1 [New, built from A and S].** Certified pooling stays valid under persistent, spatially correlated, restless rewards when its confidence sets come from the innovation regression **[S]** instead of sample means. Its regret bound is the iid bound with counts replaced by realized information.
    - **B2 [New].** iid-certified pooling fails under persistence: its coverage collapses as persistence grows.
    - **B3 [New, built from A and S].** Every information constant of the mean channel carries over with σ² replaced by the long-run covariance (Q_G scaled by the AR polynomial at 1). Graph-correlated shocks reduce the variance of contrasts by (1 − ρ_LR), so correlated fluctuations help certify component rejection.
4. **Fluctuation channel.**
    - Innovation lower bound on dynamic regret **[S, P]**.
    - Exact contrast information: common shocks cancel **[S]**.
    - Joint-filter policies (posterior sampling, the exact two-period score) **[S, P]**, credited to established filtering and knowledge-gradient tools.
5. **Evidence.**
    - **KuaiRec static:** which web graphs align with persistent appeal; heavy-tailed failures of uncertified pooling; certified pooling halves UCB1's regret.
    - **Toy:** a 100-arm grid with AR(20) fluctuations, including a coverage test of B1 against B2.
    - **KuaiRec daily:** 253 videos × 63 days with correlated persistent engagement.

## Why this is a Web paper (for page 1)

The 2027 call desk-rejects papers that "merely use a Web artifact". The Web-specific problem here:

- Platforms hold correlation structure as by-products: social networks, co-engagement logs, embeddings, hyperlinks.
- Their rewards are restless. Attention and engagement persist and spread.
- Online learners on those platforms must decide what correlation they can trust, and how much each observation is worth.

## WWW precedent on theory

Recent research-track bandit papers state regret guarantees alongside real-data experiments:

| Paper | Venue | Theory | Experiments |
| --- | --- | --- | --- |
| [LinUCB](https://arxiv.org/abs/1003.0146) | WWW 2010 | None new | Yahoo! front-page logs, offline replay |
| [Conversational Contextual Bandit](https://arxiv.org/abs/1906.01219) | WWW 2020 | Regret bound | Synthetic data, Yelp, Toutiao |
| [Local Clustering in Contextual Bandits](https://arxiv.org/abs/2103.00063) | WWW 2021 | Clustering correctness and regret | Synthetic data, MovieLens |
| [Expected Value of Information Meets Bandit Learning](https://dl.acm.org/doi/10.1145/3696410.3714773) | WWW 2025 | Tighter regret bounds | Not checked |

The industry track favours applicability over theory but requires a deployment, which we do not have.

## Page plan (8 pages)

| Section | Pages | Content |
| --- | --- | --- |
| 1. Introduction | 1 | Correlated arms on the web; two channels; contributions; Web relevance |
| 2. Model | 0.75 | f = μ + z; graph certificates for μ; Q_G for z; two regrets |
| 3. Mean channel | 1.25 | Certified pooling (A), separation (A), misalignment (A), graph error (A) |
| 4. Bridge | 1.25 | Innovation regression (S); B1 regret; B2 failure; B3 long-run constants and contrast gain |
| 5. Fluctuation channel | 0.75 | Innovation lower bound (S, P); contrast information (S); policies |
| 6. Experiments | 2.5 | KuaiRec static (alignment table, Setting A tails); toy (coverage and regret); KuaiRec daily |
| 7. Related work and conclusion | 0.5 | Spectral and clustered bandits; time-varying GP; latent-AR bandits; graph learning |

Appendix: proofs, graph construction, Setting B (user graphs), sensitivity checks.

## Experiments

Existing results are in [experiments/kuairec/README.md](../experiments/kuairec/README.md) and [experiments/simulations/spatiotemporal_benchmark/README.md](../experiments/simulations/spatiotemporal_benchmark/README.md).

| Experiment | Purpose | Status |
| --- | --- | --- |
| KuaiRec Phase 1: alignment of 16 graphs | Which web graphs encode the mean channel | Done |
| KuaiRec Setting A: item-graph pooling | Uncertified tails; certified pooling gains | Done (v1); v2 with KL bounds and calibrated certificates running |
| KuaiRec Setting B: user graphs | Pooling across users | Running; appendix |
| Toy: 100-arm grid, AR(20) | Fluctuation-channel policies against iid, spatial-only and temporal-only baselines | Running |
| **Toy coverage (B1 against B2)** | Certificates under persistence: iid radius against innovation-regression radius; coverage and regret against φ | **To build** |
| **KuaiRec daily** | Real correlated persistence: 253 videos × 63 days, 10 daily slots, co-engagement Q_G; ST policies and certified pooling | **To build** |

Cut from the long paper:
- Setting C (product graph), Last.fm, and theory T4/T5 for user-graph products: future work.
- Wikipedia, Yahoo! R6, NYC taxi: follow-up work; designs in [st_applications.md](st_applications.md).

## Schedule

| Dates | Work |
| --- | --- |
| 9–11 Oct | Merged proposal (this file); theory map and B1–B3 statements; toy coverage experiment |
| 11–14 Oct | KuaiRec daily panel; B1 proof; B2 proof |
| 14–18 Oct | KuaiRec daily runs; B3; **abstract submitted by 18 Oct** under the unified framing |
| 18–20 Oct | **Go/no-go on B1**; experiment figures |
| 20–25 Oct | Writing; appendix proofs; reproducibility; **paper submitted by 25 Oct** |

## Risks

| Risk | Mitigation |
| --- | --- |
| B1's regret bound needs a per-pull information lower bound that is messy with spatial shocks | State the bound in realized information (always valid). Give the clean per-pull constant for independent-arm AR(1) as a corollary; for correlated shocks, state the contrast form |
| Too much content for 8 pages | Mean-channel proofs and Setting B go to the appendix; the page plan above is binding |
| KuaiRec daily is short (63 days) and slot rewards are aggregate | State the exogenous-demand assumption; report sensitivity to the fit window |
| The energy certificate is loose on real graphs (ratio about 5) | Report it as a finding; calibrated certificates (Setting A v2) as the practical variant, with their validity rate measured |
| Theory novelty versus Gornet and Sinopoli (L4DC 2024), TV-GP-UCB, and Trella et al. (RLC 2025) | Credit joint filtering and confidence tools. Claim only the certified-pooling bridge (B1–B3) and the mean-channel separation |

## Sources

- The Web Conference 2027: [Call for Research Track Papers](https://www2027.thewebconf.org/?p=296); [Important dates](https://www2027.thewebconf.org/important-dates/).
- Related work and dataset sources are listed in [research/correlated_arms/README.md](../research/correlated_arms/README.md), [experiments/kuairec/README.md](../experiments/kuairec/README.md) and [experiments/simulations/spatiotemporal_benchmark/README.md](../experiments/simulations/spatiotemporal_benchmark/README.md).
