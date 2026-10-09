# Spatiotemporal Bandits on the Web: Application Scenarios and Experiment Designs

As of 9 October 2026. Companion to the [algorithm catalog and toy benchmark](../research/st_toy/README.md) and the [graph-bandit proposal](CLAUDE.md).

Seven web scenarios suit spatiotemporal bandits. Two can run this week: Wikipedia attention and KuaiRec daily engagement. Both are complete panels, so every arm's reward is known at every time step, together with a real web graph. Yahoo! R6 adds the one setting with real bandit feedback. The others follow as data preparation allows.

## What makes a scenario a good fit

A scenario needs all four properties. The fourth is the one most datasets fail.

1. **Restless arms.** Rewards change whether or not an arm is shown: news interest, page attention, zone demand, server load.
2. **Persistence at the decision interval.** Today's level predicts tomorrow's, so an observation stays useful for several rounds.
3. **Fluctuations that move together across related arms**, through a graph the web already provides: links, navigation, co-engagement, geography or network topology.
4. **Every arm's reward at every time step** (a full panel), or logs with uniform-random exposure. Then a policy can be evaluated exactly, against the oracle that knows all current rewards.

The modelling assumption shared by the panel-based designs: **showing an item does not change its future organic demand.** The reward of choosing item i at time t is its organic engagement level f(i, t). This is standard for semi-synthetic evaluation and is stated as a limitation.

## Scenarios

Rows are ordered by how soon they can run.

| # | Scenario | Arm and decision | Reward | Interval | Graph across arms | Public data | Evaluation | WWW track |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Featured or trending article slot** | One of 300–500 articles to promote each day | log daily page views | Day; 803 days | **Wikipedia clickstream**: monthly counts of reader navigation between articles | [Kaggle Web Traffic](https://www.nixtla.io/blog/wiki-traffic-forecast) (145,063 articles, July 2015 to September 2017); [clickstream dumps](https://meta.wikimedia.org/wiki/Research:Wikipedia_clickstream) | Exact, from the full panel | Graph Algorithms; Web Mining |
| 2 | **Daily trending-video slot** | One of 300 videos per day | Daily play-completion or like rate | Day; about 60 days | Co-engagement or factorization item graph (already built) | KuaiRec `item_daily_features.csv` (343,341 video-days) | Exact, from the full panel | Search & Recommendation |
| 3 | **News headline slot** | One of the live articles (about 20) per visit | Click | Visit; rates move hour to hour | Article feature similarity | Yahoo! R6A/B, uniform-random logging over about 10 days | Unbiased replay of real bandit feedback | Search & Recommendation |
| 4 | **Driver repositioning on a ride-hailing platform** | Which of 69 Manhattan taxi zones to send a driver to | Pickups in the zone over the next hour | Hour | Zone adjacency (literally spatial) | [NYC TLC trip records](https://www.bu.edu/cs/groups/dblab/ride-hailing) (public, monthly files) | Exact, from the hourly panel | Web Economics |
| 5 | **Regional featured song** | One of the songs charting in a country | log daily streams | Day; 2017 to 2021 | Co-charting across countries; shared artist | [Spotify daily Top 200 by country](https://hyper.ai/en/datasets/34663) | Panel truncated at rank 200; songs leaving the chart are censored | Search & Recommendation |
| 6 | **Daily homepage promotion in e-commerce** | One of 100 items in a store category | Daily units sold (log) | Day; about 5 years | Product hierarchy; co-sales correlation from a training window | M5 / Walmart (Kaggle) | Exact for organic sales; the promotion effect is not modelled | Web Economics |
| 7 | **CDN, DNS or anycast site selection** | Which server or site a client queries | Negative round-trip time | Minutes | Geographic or network (AS) proximity | RIPE Atlas built-in measurements (public) | Exact where probes measure all targets on schedule | Web Infrastructure |

Not included for now:
- **LLM and API routing for agentic web systems.** Strongly spatiotemporal, but no public panel of latency and quality per endpoint exists.
- **Social-media trending topics.** Data access is restricted.

## Shared experiment protocol

The same design is used for every panel scenario, so results compare across domains.

1. **Rewards.**
    - Transform to an approximately Gaussian scale: log1p for counts, logit for rates.
    - Subtract a fitted day-of-week (or hour-of-day) seasonal profile. The bandit acts on the residual plus the long-run mean.
    - Report regret back on the original scale too.
2. **Rolling origins.** Use 10 start dates per scenario. For each start date:
    - The preceding 120 days, or 30 days for KuaiRec, form the **fit window**.
    - The next T steps form the **test window**: 120 days for Wikipedia, 30 for KuaiRec, 7 days of hourly steps for NYC taxi.
    - Paired comparisons share the same windows.
3. **What the model learns in the fit window.**
    - AR coefficients for lags {1, 2, 7, 14, 21} (sparse seasonal AR), pooled across arms with per-arm shrinkage.
    - Innovation covariance: the sample covariance shrunk toward the graph kernel (I + γL)⁻¹, with γ chosen by held-out likelihood.
    - A mean prior from fit-window averages.
    - A second variant refits these online every 7 steps, so dynamics are not handed to the learner.
4. **Arms.** N = 300 per instance, sampled stratified by popularity. With 5 lags the filter state has N × 6 = 1,800 dimensions, the same scale as the toy. A 20-factor low-rank variant tests scaling to N = 2,000.
5. **Decisions.** One arm per step; a k = 3 slate variant uses cascade feedback.
6. **Feedback.** The pulled arm's reward plus Gaussian noise, with noise variance set to the scenario's measurement noise. For Yahoo! R6, feedback is the real click.

### Policies

| Family | Policies |
| --- | --- |
| iid | UCB1, Gaussian TS, KL-UCB (Bernoulli scenarios) |
| Non-stationary, model-free | Sliding-window UCB, discounted TS, change-detection UCB |
| Non-stationary, model-based | AR-based bandit of [Chen et al., NeurIPS 2023](https://arxiv.org/abs/2210.16386); latent-AR bandit (Trella et al., RLC 2025) |
| Spatial only | SpectralTS / graph-kernel GP-UCB |
| Temporal only | Per-arm AR filter with TS or the two-period score |
| **Spatiotemporal (ours)** | Joint filter with TS, the two-period score, or UCB; with dynamics given, and refit online |

### Metrics

- **Dynamic regret per step** against the full-state oracle, and **mean regret** against the best long-run arm.
- **Share of the gap closed:** (regret of TS − regret of the policy) / (regret of TS − innovation lower bound). This shows how close a policy gets to the best any causal policy could do.
- **Top-1 and top-5 hit rate** on the original reward scale.
- **Wall-clock time per step.**

### Ablations

Each answers one question:

| Ablation | Question |
| --- | --- |
| Real graph against degree-preserving rewiring | Does the web graph carry the cross-arm signal, or does any covariance shrinkage do as well? |
| Spatial innovation covariance on or off | Is the gain from correlated fluctuations or only from smooth means? |
| AR lags {1} against {1, 7} against {1, 2, 7, 14, 21} | How much persistence structure is needed? |
| Dynamics given (fit on the test window) against refit online | What does learning the dynamics cost? |
| N = 100, 300, 1,000 (low-rank) | Does the method scale, and how do gains change with catalog size? |

## Scenario-specific designs

### 1. Wikipedia featured-article slot

- **Arms:** 300 English articles per instance, sampled from the 5,000 with the most views in the fit window. Mobile and desktop access are combined; bots and spiders are excluded.
- **Graph:**
    - Clickstream navigation counts between those articles, symmetrized: log(1 + count), then kNN with k = 10.
    - Use the clickstream month that matches the fit window. If 2015–2017 months are unavailable, use the earliest available month and treat that as a stated limitation.
- **Why it fits:** attention bursts spread along links, such as an event article and its related pages, so innovations are graph-correlated. Weekly seasonality is strong.
- **Data note:** the Kaggle panel lists articles by title, so join to clickstream titles. Titles were renamed over 2015–2017, so report the join rate.

### 2. KuaiRec daily trending-video slot

- **Arms:** 300 of the 3,327 evaluation videos with complete daily records.
- **Reward:** daily `complete_play_cnt / play_cnt`, or `like_cnt / play_cnt`, both on the logit scale.
- **Graph:** I-coeng and I-mf from the existing pipeline. Both are already leakage-free, and both are already measured for alignment.
- **Bonus:** it links the two halves of the paper. The same graphs evaluated for static alignment are now tested for dynamic correlation.

### 3. Yahoo! R6 news slot (real feedback)

- **Arms:** the live article pool (about 20), with births and deaths. The filter adds a new arm with the mean prior when an article appears.
- **Reward:** click. The filter runs on a Gaussian approximation of the logit click-through rate per 10-minute block, from pooled clicks.
- **Evaluation:** Li et al. replay on the uniform-random logs, which is unbiased per event under uniform logging.
- **Why it matters:** it is the only scenario with real counterfactual-valid bandit feedback and real non-stationarity. Daily and evening click-rate cycles are documented in the non-stationary bandit literature.

### 4–7. Later scenarios

- **NYC taxi:** 69 Manhattan zones, hourly pickups from one month of trips, zone adjacency graph, weekly and daily seasonality. The cleanest literal spatial case and a natural fit for web-platform economics.
- **Spotify:** use only songs that stay in the Top 200 for the whole window, to avoid censoring. The graph links songs that chart together across countries.
- **M5:** one store, one category (about 100 items), daily sales.
- **RIPE Atlas:** built-in ping measurements from probes to root DNS server sites. Arms are anycast instances, and the graph is geographic proximity.

## Expected findings and risks

- **Expected:** spatiotemporal policies close most of the gap between TS and the innovation lower bound where persistence is high (Wikipedia, KuaiRec, taxi). They help little where daily noise dominates (Spotify's lower ranks).
- **Expected:** much of the gain comes from temporal modelling alone. The spatial part matters most where shocks spread along the graph (Wikipedia links, taxi zones). The rewired-graph ablation tests this directly.
- **Risk: Gaussian AR assumptions on heavy-tailed counts.** Spikes are common in page views. Mitigation: log scale, Student-t robust filtering as a sensitivity check, and reporting the share of steps with innovations over 4 standard deviations.
- **Risk: the "showing doesn't change demand" assumption.** Mitigation: state it, and use Yahoo! R6 as the scenario where it is not needed.
- **Risk: compute at large N.** Mitigation: the 20-factor low-rank state and sparse seasonal lags.

## Schedule

The KuaiRec queue and the toy benchmark finish in about 1–2 hours. Then:

| Step | Work | Estimate |
| --- | --- | --- |
| 1 | Shared panel-bandit harness (`experiments/st_apps/`): fit-window estimation, rolling origins, all policies, the gap-closed metric | 3–4 h |
| 2 | KuaiRec daily trending slot | 1 h of data work, 1–2 h of compute |
| 3 | Wikipedia featured-article slot (Kaggle panel and clickstream download, title join) | 2 h of data work, 2–3 h of compute |
| 4 | Yahoo! R6 news slot. Needs the user to accept the Yahoo! Webscope licence and download the data | 3 h once data is available |
| 5 | NYC taxi, then M5, Spotify and RIPE Atlas | Later |

**Decided: merged into the WWW 2027 long paper** on correlated arms ([CLAUDE.md](CLAUDE.md)). KuaiRec daily is in the long paper. Wikipedia, Yahoo! R6 and NYC taxi are follow-up work.

## Sources

- [Kaggle Web Traffic Time Series dataset description](https://www.nixtla.io/blog/wiki-traffic-forecast)
- [Wikipedia Clickstream (Wikimedia Research)](https://meta.wikimedia.org/wiki/Research:Wikipedia_clickstream); [clickstream readme](https://cdimage.debian.org/mirror/wikimedia.org/other/clickstream/readme.html)
- [Non-Stationary Multi-Armed Bandits for News Recommendations (uses Yahoo! R6)](https://ceur-ws.org/Vol-3929/paper2.pdf)
- [Non-Stationary Bandits with Auto-Regressive Temporal Dependency, NeurIPS 2023](https://arxiv.org/abs/2210.16386)
- [Spotify Daily Top 200 charts dataset](https://hyper.ai/en/datasets/34663)
- [Optimizing Earnings for On-Demand Ride-Hailing (NYC TLC data)](https://www.bu.edu/cs/groups/dblab/ride-hailing)
- [Characterizing a Meta-CDN (RIPE Atlas latency measurements)](https://arxiv.org/abs/1803.09990)
- [Algorithm catalog and toy benchmark](../research/st_toy/README.md)
