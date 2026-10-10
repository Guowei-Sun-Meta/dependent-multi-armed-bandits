# Short Paper Plan: Spatiotemporal Bandits for Web Attention (fallback only)

**Superseded on 9 October 2026: the spatiotemporal work is merged into the long paper** ([CLAUDE.md](CLAUDE.md)). This plan is the fallback if bridging theorem B1 is not ready by the 20 October go/no-go point.

Original decision, kept for reference: a separate WWW 2027 short paper.

## Deadlines and format

From the [WWW 2027 important dates](https://www2027.thewebconf.org/important-dates/):

- **Abstract: 9 November 2026. Paper: 16 November 2026.** Both 11:59 pm AoE, on OpenReview (`ACM.org/TheWebConf/2027/Conference_Short_Papers`).
- Notification 4 January 2027; final version 31 January 2027.
- **4 pages including references and any appendix.** Double-blind.
- At most 7 short-paper submissions per author. Authors are frozen after the abstract deadline, and placeholder abstracts are forbidden.

## Why separate, not merged

| Criterion | Merge into the long paper (25 October) | Separate short paper (16 November) |
| --- | --- | --- |
| Time to finish the spatiotemporal experiments | 16 days, shared with the long paper's theory and writing | 5 weeks |
| Fit with the long paper's story (certified static graph pooling) | Dilutes it; 8 pages cannot hold both | Each paper has one message |
| Risk to the long paper | High | None |
| Second publication | No | Yes |

**Overlap rule.** The call bars papers "under review at" another venue with proceedings, and gives no explicit rule for two submissions from the same authors. To stay safe:

- The short paper must not reuse the long paper's results or claims.
- It may reuse the KuaiRec item graphs as inputs, described independently.
- Its contribution is spatiotemporal dynamics, not static alignment or certification.

If in doubt, ask pcchairs-www2027@acm.org.

## Working title and claim

*Bandits for Restless Web Attention: Joint Spatiotemporal Filtering over Web Graphs.*

**Claim.** Web rewards are rarely iid. Page attention, video engagement and news interest persist from day to day and move together along links and co-engagement. Policies that use one joint Gaussian state over long-run means, AR lags and graph-correlated shocks close most of the gap between iid bandits and the innovation lower bound. They do so on real web panels, with dynamics learned online.

**Contributions** (sized for 4 pages):

1. **Model.** Graph-correlated AR(p) attention with unknown means, a joint filter, and three decision rules (posterior sampling, the two-period score, UCB). Credit the established tools: Kalman filtering, TV-GP-UCB, knowledge gradient.
2. **Benchmark metric.** The share of the gap closed between Thompson sampling and the innovation lower bound, which every causal policy obeys. This makes results comparable across domains.
3. **Evidence on two real web panels:**
    - Wikipedia page views with the clickstream graph.
    - KuaiRec daily engagement with co-engagement item graphs.
   Ablations separate the temporal gain from the spatial gain (real graph against its rewiring), and dynamics given from dynamics learned.
4. **Theory content.** Cite and state the existing bounds from the repo notes: the innovation lower bound and the generic GP-UCB bound, with its caveat that it can be linear. No new regret theorem is claimed; a short paper does not need one if the evidence is strong.

## Page budget

| Section | Space |
| --- | --- |
| Introduction and Web relevance: restless attention, web graphs | 0.5 page |
| Model, filter, policies, lower bound | 1 page |
| Setup: datasets, graphs, protocol, metric | 0.5 page |
| Results: one table across the toy, KuaiRec and Wikipedia; one figure with the gap closed and ablations | 1.25 pages |
| Related work, conclusion | 0.25 page |
| References | 0.5 page |

## Experiments needed

Designs are in [st_applications.md](st_applications.md).

| Priority | Experiment | Status |
| --- | --- | --- |
| 1 | Toy benchmark (100-arm grid, AR(20)) | Running (`experiments/simulations/spatiotemporal_benchmark/code/`) |
| 2 | Shared panel harness: fit window, rolling origins, learned dynamics, policies, gap-closed metric | To build (`experiments/st_apps/`) |
| 3 | KuaiRec daily trending slot | After 2 |
| 4 | Wikipedia featured-article slot (Kaggle panel and clickstream graph) | After 2 |
| 5 | Ablations: rewired graph, spatial covariance on or off, AR lag sets, given against learned dynamics | After 3–4 |
| 6 | Baselines: sliding-window UCB, discounted TS, AR bandit (NeurIPS 2023) | With 2 |
| Optional | Yahoo! R6 replay (needs the Webscope licence) or NYC taxi | If time allows |

## Schedule

The 18 and 25 October long-paper deadlines take priority. Spatiotemporal compute runs in the background during that window.

| Dates | Work |
| --- | --- |
| 9–12 Oct | Toy results; harness; KuaiRec daily data preparation |
| 12–18 Oct | KuaiRec daily and Wikipedia runs in the background, while the long-paper abstract is written |
| 18–25 Oct | Long-paper writing has priority; ablation runs continue in the background |
| 26 Oct – 2 Nov | Analysis, learned-dynamics variant, final runs |
| 2–9 Nov | Short-paper draft; **abstract submitted by 9 Nov** |
| 9–16 Nov | Polish and reproducibility; **paper submitted by 16 Nov** |
