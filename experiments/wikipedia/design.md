# Wikipedia Attention: Experiment Design

9 October 2026. A second real application of the correlated-arms model, sized for a laptop and built on public data: a "featured article" slot over English Wikipedia articles, with hyperlinks as the web graph.

## Questions

1. Does daily attention behave like the fluctuation channel: persistent deviations from long-run levels, with shocks correlated across articles?
2. Do hyperlinks carry that shock correlation beyond a common factor and beyond degree?
3. Do policies that model persistence and correlation beat iid bandits, and when does exploration pay?

## Shared protocol

| Element | Choice |
| --- | --- |
| Panel | Daily user page views (agent "user", all access), 1 January 2022 to 31 December 2025 (1,461 days), from the Wikimedia REST API |
| Graph | Hyperlinks among the panel's articles (MediaWiki links API), symmetrized |
| Reward | log(1 + daily views) of each featured article |
| Decisions | 10 featured slots per day; the featured articles' rewards are observed with noise sd 0.05 |
| Assumption | Featuring does not change organic attention (exogenous, restless arms) |
| Fit and test | For each origin F ∈ {365, 730, 1,095}: fit on days F − 365 to F − 1, test on the next 120 days |
| Model | Pooled AR on lags {1, 2, 7}; innovation covariance shrunk toward a graph resolvent plus a common shock; a joint Kalman filter over long-run levels and lags, run through the fit window |
| Metric | Regret per day: the oracle's top-10 sum of log views minus the chosen sum |
| Seeds | 5 noise seeds per stochastic policy (every policy on the six-community panel) |

Policies (names as in [code/attention.py](code/attention.py)):

| Policy | Family |
| --- | --- |
| `fit_mean`, `last_value` | Static fit-window means; the last observed value |
| `ts_iid` | iid Gaussian Thompson sampling |
| `ar_greedy` | Temporal-only filter (independent AR per article), greedy |
| `st_greedy`, `st_greedy_rewired`, `st_greedy_nograph`, `st_greedy_block` | Spatiotemporal filter, greedy, with hyperlink, rewired, common-factor-only or community-block covariance |
| `st_ucbm1` | Spatiotemporal filter, UCB with a 1-sd bonus |
| `st_jps`, `st_jps_block`, `st_jps_nograph` | Joint predictive sampling: samples only the information that persists |
| `dr_greedy` | Filter with a drifting long-run level (per-day variance 0.0005), greedy |
| `sh_*` | Sparse history: in the fit window only 10 articles per day were seen (one-domain panel only) |

## Panel 1: one domain

| Element | Choice |
| --- | --- |
| Arms | The 150 most-viewed articles linked from "List of programming languages" with complete daily data (512 of 691 had complete series) |
| Graph | 3,037 hyperlink edges, mean degree 40.5 |
| Graph conditions | Real, degree-preserving rewiring, none |

## Panel 2: six communities

**Why.** On the one-domain panel shocks were strongly correlated, but through a domain-wide factor: hyperlinked pairs correlated no more than rewired pairs, and a common-factor covariance fitted held-out shocks best. One explanation is that one domain shares one rhythm, so a graph has nothing to add. Communities with different calendars (NFL autumn Sundays, NBA and MLB seasons, Premier League weekends, news-driven countries, weekday programming languages) should share shocks *within* communities. Hyperlinks mostly stay within a community, so they should carry correlation that one common factor cannot.

| Element | Choice |
| --- | --- |
| Arms | 25 articles from each of six communities, the most viewed with complete data: NFL teams, NBA teams, MLB teams, Premier League clubs, UN member states, programming languages |
| Graph | 1,990 undirected hyperlink edges, mean degree 26.5, 84% within a community |
| Graph conditions | Hyperlinks; degree-preserving rewiring (null); community blocks (all articles of a community connected; an oracle-like reference); common factor only |
| Diagnostics | Shock correlation by pair type; held-out log-likelihood of each covariance at every origin |
| Origins | Test windows start January 2023, January 2024 and December 2024 |

## Data and caches

- The panels are in [data/one_domain](data/one_domain) and [data/six_domains](data/six_domains): `views.csv` (days × articles), `links.csv` (edges), `metadata.json`, and `domains.csv` for the six-community panel.
- Raw API responses are cached in `data/wikipedia/` at the repository root, and fitted filters in `data/wikipedia/filters*` (both git-ignored).
