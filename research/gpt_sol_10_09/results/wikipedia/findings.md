# Wikipedia attention: completed laptop experiment

Two fixed 24-article panels, 2024 fitting and 181 test days in 2025. Graphs use revisions before 2024.

**352 completed runs**, 63,712 recorded daily decisions, 197.9s experiment wall time, 166.8 MB peak RSS.

The main model is sparse AR(7), with dense AR(20) sensitivity. Feedback is exact observed log1p human page views on selected arms; batches are chosen before current feedback. All methods receive 366 days of full historical initialization, which costs 8,784 readings per panel. Test budgets are 181 or 905 observations.

## Main AR(7) results

Regret against the current observed full-field oracle **per slot**. This is an exogenous attention proxy, not promotion lift.

| Policy | Astronomy, b=1 | Astronomy, b=5 | Football, b=1 | Football, b=5 |
| --- | ---: | ---: | ---: | ---: |
| Static ranking | 0.0603 | 0.0726 | 0.1364 | 0.1783 |
| Last value | 0.0623 | 0.0726 | 0.1460 | 0.1803 |
| Round robin | 1.2396 | 0.7498 | 1.5487 | 0.9725 |
| IID UCB | 0.0603 | 0.0730 | 0.1364 | 0.1808 |
| IID TS | 0.0603 | 0.0721 | 0.1364 | 0.1811 |
| Window UCB | 0.0603 | 0.1119 | 0.6193 | 0.2994 |
| AR greedy | 0.0625 | 0.0800 | 0.1453 | 0.1296 |
| AR predictive UCB | 0.0650 | 0.0714 | 0.1803 | 0.1437 |
| AR predictive TS | 0.0823 | 0.0817 | 0.5313 | 0.2336 |
| Joint greedy | 0.0603 | 0.0670 | 0.1408 | 0.1417 |
| Joint state UCB | 0.0603 | 0.0528 | 0.1507 | 0.1315 |
| Joint state TS | 0.0797 | 0.0811 | 0.4872 | 0.2515 |
| Joint predictive UCB | 0.0603 | 0.0539 | 0.1647 | 0.1362 |
| Joint predictive TS | 0.0628 | 0.0663 | 0.3911 | 0.2053 |
| Rewired predictive TS | 0.0628 | 0.0653 | 0.3871 | 0.2059 |
| Graph-free factor/shrink TS | 0.0712 | 0.0716 | 0.4302 | 0.2107 |
| Graph-free shrink/factor TS | 0.0712 | 0.0716 | 0.4302 | 0.2107 |

## Interpretation

- With five observations/day, joint predictive UCB improves on temporal-only predictive UCB by 24.5% in astronomy and 5.2% in football. In football it improves on static ranking by 23.6%; temporal-only greedy is still slightly better than the joint UCB rules.
- With one observation/day, static ranking and iid policies are exceptionally strong. Joint methods do not establish an advantage over that baseline. Most uncertainty concerns transient events, while one item dominates ordinary days.
- Predictable-state TS consistently improves on full-current-state TS in these panels. It still over-explores relative to strong static or greedy rules in the mature-catalog setting.
- Real and degree-preserving rewired graphs give almost identical predictive-TS performance. Off-diagonal covariance helps versus a diagonal filter in some comparisons, but these data do not establish a benefit from the actual hyperlink topology.
- The common-factor and empirical variants share the same target family and select identical fits here; they are two overlapping parameterizations of a graph-free covariance control, not two independent sources of supporting evidence.
- Dense AR(20) fits are stable and inexpensive at 24 arms. Astronomy five-arm predictive UCB improves by 20.4% versus its AR-only counterpart, but greater order is not a uniform improvement across endpoints.

## Uncertainty and limits

Ten stochastic seeds quantify Monte Carlo variation conditional on each fixed observed field. The three-seed AR(20) sensitivity is smaller. Summary intervals and paired intervals do not represent independent Web histories or population significance. Deterministic rows have no policy-randomization interval.

There are two purposive topic panels, one test half-year, privileged full-history initialization, Gaussian approximations to logged attention, and potential drift. Historical hyperlinks are direct binary within-panel links; dense graph nulls can be similar to the original. No permanent-mean PCS or theoretical innovation floor is identifiable from these data.

## Reproduction and evidence

See [raw run summaries](runs.csv), [daily action traces](daily.csv), [summary with conditional intervals](summary.csv), [paired comparisons](paired.csv), [model metadata](metadata.json), [checks](checks.json), and [data/revision provenance](../../data/wikipedia/manifest.json). Model NPZ files contain both graph variants, seasonality, coefficients, and covariance matrices.
