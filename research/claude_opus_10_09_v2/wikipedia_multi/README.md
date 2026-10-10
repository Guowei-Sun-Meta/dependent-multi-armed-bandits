# Wikipedia Attention Across Six Communities

9 October 2026. A hypothesis-driven second application, designed after the first Wikipedia panel returned a null.

## Why this experiment

On 150 programming-language articles, daily attention shocks were strongly correlated, but through a domain-wide factor: hyperlinked pairs correlated no more than rewired pairs (0.256 against 0.250), and a common-factor covariance fit held-out shocks best. One explanation is that a single domain shares one rhythm, so a graph has nothing to add. If so, a panel spanning communities with different calendars should show shocks shared **within** communities, and hyperlinks, which mostly stay within a community, should carry them. This experiment tests that.

## Design

| Element | Choice |
| --- | --- |
| Arms | 25 articles from each of six communities, the most viewed with complete data: NFL teams, NBA teams, MLB teams, Premier League clubs, UN member states, programming languages |
| Panel | Daily user page views, 1 January 2022 to 31 December 2025 (Wikimedia REST API) |
| Graph | Hyperlinks among the 150 articles: 1,990 undirected edges, mean degree 26.5, 84% within a community |
| Reference graphs | Degree-preserving rewiring (null); community blocks (all articles of a community connected; an oracle-like reference); common factor only |
| Reward and decisions | log(1 + views); 10 featured slots per day; featuring assumed not to change organic attention |
| Fit and test | Rolling 365-day fit window (AR lags {1, 2, 7}, shrunk innovation covariance), 120-day test window at origins January 2023, January 2024 and December 2024; 5 noise seeds for every policy |

Code: [collect_multi.py](../../../experiments/wikipedia/collect_multi.py), [attention.py](../../../experiments/wikipedia/attention.py) `--dataset multi`. Data: [data/](data). Results: [results/](results).

## Results

**Shocks are community-specific, and hyperlinks carry them** ([diagnostics.json](results/diagnostics.json)):

| Measure | Value |
| --- | ---: |
| Shock correlation, same community / different communities | 0.320 / 0.000 |
| Shock correlation, hyperlinked / rewired / all pairs | **0.273** / 0.051 / 0.051 |
| Held-out log-likelihood per day: hyperlinks / community blocks / common factor / rewired | **22.16** / 22.13 / 21.92 / 21.67 |

Hyperlinks fit held-out shocks best at all three origins. The one-domain panel showed the opposite (52.88 for hyperlinks against 53.76 for the common factor).

**Policies** (regret per day, mean over 3 origins × 5 seeds):

| Policy | Regret / day |
| --- | ---: |
| Spatiotemporal UCB, 1 sd | **1.205** |
| Drifting level, greedy | 1.257 |
| Greedy: community blocks / common factor / rewired / hyperlinks | 1.290 / 1.299 / 1.307 / 1.327 |
| Temporal-only filter, greedy | 1.309 |
| Last observed value | 1.434 |
| Predictive sampling: community blocks / hyperlinks / common factor | 1.456 / 1.470 / 1.500 |
| iid Thompson sampling | 1.588 |
| Fit-window means | 1.625 |

**The graph's effect on decisions is small** ([paired differences](../analysis/wikipedia_multi_graph_effect.md)):

| Policy | Change in regret against the common factor |
| --- | ---: |
| Predictive sampling, hyperlinks | −2.0% (s.e. 1.3%) |
| Predictive sampling, community blocks | −2.9% (s.e. 1.7%) |
| Greedy, hyperlinks | +2.2% (s.e. 1.1%) |
| Greedy, community blocks | −0.7% (s.e. 0.9%) |

## Reading

1. **The hypothesis holds for the shock model.** Across communities with different rhythms, hyperlinks carry correlated shocks (five times the rewired level) and give the best held-out fit, matching the community-block reference.
2. **The decision payoff is small.** Neighbours explain about a third of a shock's variance (R² 0.36, against 0.46 in the benchmark), but which articles lead is decided mostly by long-run levels: fluctuation sd 0.48 against level spread 0.91, versus 1.0 against 0.5 in the benchmark, where the graph gave 15%.
3. **Mild optimism wins.** Rankings turn over fast (22% of the top 10 per day) and the 10th and 11th articles are nearly tied (gap 0.03). A 1-sd bonus that refreshes stale items beats greedy by 9%. Predictive sampling's larger draws shuffle near-ties and lose 11%.
4. **Modelling dynamics still pays:** the best model has 24% less regret than iid Thompson sampling.
