# Same-day experiment results — 10 October 2026

Completed: 108 full-year Wikipedia policy runs; 480 general-AR coverage screen runs; 400 fresh AR(20) confirmation runs; 600 false-elimination runs; 2,520 correlation-screen runs; 142 OBD censored-learner trajectories. The slate-variance check uses 20,000 independent worlds per cell. These are new executions, not a repackaging of old results.

## Findings

**Real-data gains depend on panel and budget.** At one reading/day, static ranking and iid TS remain strongest or match the best rule on these two mature panels. At five readings/day, joint UCB is 25.1% below iid TS in astronomy, but EWMA is only about 2.6% above joint UCB. In football, temporal-only greedy is about 40.9% below iid TS and outperforms joint UCB. Thus a universal graph advantage or a universal need for filtering is not supported.

| policy        |   astronomy |   football |
|:--------------|------------:|-----------:|
| ar_greedy     |      0.0544 |     0.1302 |
| discounted_ts |      0.0698 |     0.2181 |
| ewma          |      0.0414 |     0.2321 |
| iid_ts        |      0.0539 |     0.2203 |
| st_ucb        |      0.0404 |     0.1455 |
| static        |      0.0535 |     0.2215 |

Loss is observed-oracle log1p-view loss per selected item, averaged over the full 365-day 2025 field. All policies receive 8,784 full-history readings in 2024, with no full-field test refresh. Development parameters are frozen before test. Five TS seeds are conditional randomization, not independent Web histories. Paired block sensitivities are saved for block lengths 7, 14 and 28 days. Astronomy joint UCB versus EWMA is inconclusive when the interval crosses zero; this does not establish equivalence. Historical graphs are reused from the released study; the newly acquired series and archived source matrices have hashes.

**Wrong-order dynamics break nominal innovation coverage.** The independent 100-world AR(20) follow-up is below: known-model failure is 1/100, versus 40/100 under the wrong model. Fitted-model failure is 5/100 and inflated-model failure is 3/100; these counts do not establish a learned-model coverage guarantee or a reliable inflation remedy. Fitted-model rows use a 365-day independent prefix; inflated rows multiply fitted innovation covariance by 1.5. The wrong model is AR(1) with diagonal innovations. Exact-model confidence is very wide (maximum arm interval widths can exceed the entire [0,1] mean range), so safety alone does not demonstrate useful decisions.

| mode                    |   worlds |   failures |   failure_rate |   ci_low |   ci_high |   mean_final_max_width |
|:------------------------|---------:|-----------:|---------------:|---------:|----------:|-----------------------:|
| fitted                  |      100 |          5 |         0.0500 |   0.0215 |    0.1118 |                 4.9186 |
| fitted_inflated         |      100 |          3 |         0.0300 |   0.0103 |    0.0845 |                 5.8839 |
| known                   |      100 |          1 |         0.0100 |   0.0018 |    0.0545 |                 5.0099 |
| wrong_order_or_diagonal |      100 |         40 |         0.4000 |   0.3094 |    0.4980 |                 2.7224 |

This follow-up was selected after the four-profile screen and uses fresh seeds (offset 10,000). Pointwise nominal 95% diagnostics are recorded separately from the all-time confidence sets. The four-profile screen includes AR(1), AR(7), dense AR(20), and heterogeneous AR orders; it does not complete the heavy-tail or online-refitting agenda.

**Bursty exposure causes irreversible wrong decisions with iid confidence.** At persistence 0.97 and 0.995, iid elimination drops the best arm in 30/100 and 47/100 worlds; innovation elimination drops it in 0/100. The 95% upper failure bound for 0/100 is 3.7%, not zero. The innovation rule does not eliminate at these horizons and has mean regret 400; iid mean regret is about 323 and 390 respectively. This is a safety/usefulness tradeoff, not evidence that the valid rule has lower average regret. Arm ordering is randomized. Horizon curves illustrate lasting loss after failure; they do not prove an asymptotic theorem.

**Spatial correlation helps in a controlled persistent setting, with limits.** In the AR(1) screen at persistence 0.9 and graph strength 0.8, joint UCB improves on matched temporal-only UCB by 0.039 latent-oracle loss per round in the smaller-gap regime (95% paired interval: -0.070 to -0.008 for joint minus temporal-only). In the larger-gap regime the difference is -0.028 (interval: -0.062 to +0.005), which is inconclusive. Corrupting only the learner graph weakens this advantage. This is a 16-arm exploratory mechanism screen with fixed constants, not the planned general-AR factorial or a tuned comparison against all published algorithms. The final run matches the true sensor variance in the filter and scores the latent field, excluding sensor noise from the oracle.

**The slate-contrast calculation checks out.** Across 8 configurations, simulated contrast variance is within 1.8% of the exact finite-sample prediction. Equal marginal variance and matched simultaneous AR(1) observations show the expected (1-rho) gain. Dense-Gaussian checks cover general-AR staggered and simultaneous conditional observations; arbitrary schedules must use their conditional covariance.

**OBD is feasible for a narrow logged-feedback pilot, but hourly Gaussian filtering is poorly supported.** All three full uniform-random campaign logs were audited (2,691,861 rows). In the men’s campaign at position 1, 91.7% of training hourly item bins have no click; 60.8% of six-hour bins have no click; daily bins have only three clicks at the median. Null or noisy temporal diagnostics are retained. The executed test compares stationary/forgetting and graph/shrinkage heuristics, not a validated general-AR click filter.

| policy        |   mean_ips_ctr |   seed_sd |   mean_matches |   mean_clicks |
|:--------------|---------------:|----------:|---------------:|--------------:|
| discounted_ts |         0.0068 |    0.0032 |      1931.5000 |       12.8500 |
| graph_ts      |         0.0064 |    0.0021 |      1837.4500 |       12.0000 |
| random        |         0.0062 |    0.0028 |      1912.9000 |       11.7000 |
| rewired_ts    |         0.0061 |    0.0019 |      1831.7500 |       11.6000 |
| shrink_ts     |         0.0061 |    0.0019 |      1827.2000 |       11.6000 |
| static        |         0.0069 |  nan      |      1667.0000 |       13.0000 |
| ts            |         0.0062 |    0.0023 |      1835.7000 |       11.7500 |
| ucb           |         0.0085 |  nan      |      2021.0000 |       16.0000 |
| window_ts     |         0.0052 |    0.0033 |      1881.4000 |        9.7500 |

OBD training is November 24–26 UTC, development November 27, and test November 28–30. The pilot uses 34 supported items at position 1. Every policy chooses before each hour, sees only matching randomized feedback and advances through empty bins. Most trajectories obtain only roughly 10–16 test clicks: the apparent CTR ordering is underpowered. Seed SD is conditional algorithmic variation; the date-block file is descriptive sensitivity, not a confidence guarantee for deployment. Graph transfer uses a fixed 100 pseudo-impressions and is explicitly uncertified. Real, relabelled and graph-free shrinkage controls are retained. The target is the censored learner receiving these sparse observations, not a deployed learner with full selected feedback. Position-specific IPS identity and hidden-label invariance passed.

## What remains

- KuaiRec chronology and reruns: raw data are absent from this checkout. No corrected KuaiRec claim is made.
- AR2-p, dense general-AR correlation confirmation, heavy-tail/blocked-innovation stress tests, and practical non-oracle certificates remain outstanding.
- No Retailrocket acquisition or low-rank/Web-scale claim; no latent PCS or oracle regret claim from OBD logs.
- Next priority: useful learned-dynamics uncertainty and stronger rare-click estimation, then broader independently predefined panels. Keep the new evidence’s panel-dependent conclusions in the abstract.

## Files and reproduction

- `design.md`: protocol and explicit scope.
- `results/wikipedia/`: 39,420 daily decisions, tuning records, model matrices, inflation diagnostics and paired differences.
- `results/certificates*`, `false_elimination`, `factorial`, `slate`: raw runs, summaries, checks and measured runtimes.
- `results/obd/`: hourly aggregates, chronology/support manifest, precision diagnostics, 10,224 decisions, IPS summaries and checks.
- `results/validation.json` and `results/manifest.json`: integrity checks and source hashes.
- `figures/`: standalone PNG figures.

Run from the repository root after data acquisition:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export MPLCONFIGDIR=experiments/today_2026_10_10/.mplconfig
.venv/bin/python -I experiments/today_2026_10_10/code/wikipedia.py
.venv/bin/python -I experiments/today_2026_10_10/code/obd.py
.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py coverage
.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py coverage --profiles ar20 --worlds 100 --seed-offset 10000
.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py elimination
.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py factorial
.venv/bin/python -I experiments/today_2026_10_10/code/controlled.py slate
.venv/bin/python -I experiments/today_2026_10_10/code/analyze.py
```

Source data: [OBD release](https://research.zozo.com/data.html), Saito et al. [dataset paper](https://arxiv.org/abs/2008.07146), and Wikimedia per-article pageviews. The OBD archive is CC BY 4.0; released acknowledgement is retained in `results/obd/source_readme.txt`.

The local NumPy/Apple BLAS emitted floating-point status warnings on some matrix products. Explicit finiteness assertions and dense-equivalence checks pass; no nonfinite raw numeric result is accepted. Scientific conclusions remain bounded by the study designs and replication sizes above.
