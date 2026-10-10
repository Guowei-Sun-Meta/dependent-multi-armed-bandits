# Wikipedia Attention over the Hyperlink Graph

9 October 2026. A second real application of the correlated-arms framework, sized for a laptop: a "featured article" slot over programming-language articles on English Wikipedia.

## Design

| Element | Choice |
| --- | --- |
| Arms | The 150 most-viewed articles linked from "List of programming languages" with complete daily data (512 of 691 had complete series) |
| Panel | Daily user page views, all access, 1 January 2022 to 31 December 2025 (1,461 days), from the public Wikimedia REST API |
| Graph | Hyperlinks among the 150 articles (MediaWiki links API), symmetrized: 3,037 edges, mean degree 40.5 |
| Reward | log(1 + daily views) of each featured article. Featuring is assumed not to change organic attention |
| Decisions | 10 featured slots per day; the featured articles' rewards are observed (noise sd 0.05) |
| Fit and test | For each origin F ∈ {365, 730, 1,095}: fit on days F − 365 to F − 1, test on the next 120 days |
| Model | AR lags {1, 2, 7}, pooled; innovation covariance shrunk toward a hyperlink-graph resolvent plus a common shock; joint Kalman filter over long-run levels and lags |
| Variants | Real, rewired and no-graph covariance; a drifting level (per-day variance 0.0005); sparse history (10 articles seen per fit day) |

Code: [collect.py](../../../experiments/wikipedia/collect.py) and [attention.py](../../../experiments/wikipedia/attention.py). Data: [data/](data). Results: [results/runs.csv](results/runs.csv) and [results/diagnostics.json](results/diagnostics.json).

## What the data looks like

- **Persistence with a weekly cycle.** Lag-1 autocorrelation is 0.72, lag-7 is 0.74 and lag-30 is 0.37. The fitted AR coefficients are 0.46 (lag 1), −0.05 (lag 2) and 0.47 (lag 7); the spectral radius is 0.97.
- **Shocks are strongly correlated, through a common factor.** Innovations of all article pairs correlate at 0.218. Hyperlinked pairs correlate at 0.256 and rewired pairs at 0.250. Attention to the whole domain moves together (weekly and seasonal traffic, platform-wide effects), and hyperlinks add almost nothing beyond that and beyond degree.
- **Levels dominate fluctuations in scale.** The spread of long-run levels across articles is 1.05 on the log scale, against 0.41 for deviations.

## Results

Regret per day: the oracle's top-10 sum of log views minus the chosen sum. 5 seeds for stochastic policies.

| Policy | F = 365 | F = 730 | F = 1,095 | Mean |
| --- | ---: | ---: | ---: | ---: |
| Spatiotemporal filter with drifting level, greedy | 0.045 | 0.828 | 0.254 | **0.376** |
| Joint predictive sampling | 0.085 | 0.848 | 0.287 | 0.407 |
| Spatiotemporal UCB, 1 sd | 0.054 | 0.999 | 0.256 | 0.436 |
| Sparse history: UCB 1 sd / greedy | | | | 0.438 / 0.438 |
| Spatiotemporal greedy, hyperlink / rewired / no graph | 0.050 | 1.015 | 0.258 | 0.441 / 0.441 / 0.441 |
| AR filter (temporal only), greedy | 0.053 | 1.028 | 0.262 | 0.448 |
| Sparse history: iid TS / joint predictive sampling | | | | 0.472 / 0.475 |
| Last observed value | 0.045 | 1.012 | 0.400 | 0.486 |
| Fit-window means | 0.045 | 1.340 | 0.256 | 0.547 |
| iid Thompson sampling | 0.062 | 1.340 | 0.256 | 0.553 |

![Wikipedia regret by policy](../figures/fig6_wikipedia.png)

## Reading

1. **Modelling dynamics pays.** The filter with a drifting level cuts regret 32% against iid TS and 23% against the last-value rule.
2. **Exploration pays here, unlike on KuaiRec daily.** Joint predictive sampling is second best (−26% against TS, 8% better than greedy without drift). Each article gets about 8 observations in the 120-day test window, against about 1 per video on KuaiRec. This supports matching exploration to observations per arm.
3. **The hyperlink graph adds nothing to the fluctuation model.** Real, rewired and no-graph covariances tie, because the shared shock is domain-wide. Correlated fluctuations matter (spatiotemporal greedy beats temporal-only by about 1.5% through the common factor), but here the correlation is not link-specific.
4. **Difficulty is concentrated in one period.** At F = 365 and F = 1,095 the top-10 set is stable and every model is near the oracle. At F = 730 (the test window starts January 2024) rankings shifted, and drift and predictive sampling matter most.
5. **Sparse history costs little here.** A 365-day window of 10 articles a day (3,650 observations) is enough to estimate levels.

## Limitations

- Featuring is assumed not to change organic views.
- Articles were selected from one domain and by popularity; a different domain may have link-specific shocks, such as current events spreading along links.
- Bots and spiders are excluded through the API's "user" agent filter only.
