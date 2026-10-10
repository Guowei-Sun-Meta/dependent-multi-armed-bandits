# Certificates under Persistence: Report

9 October 2026. Do confidence certificates for certified pooling stay valid when rewards persist? 20 arms in 4 components, AR(1) fluctuations with φ up to 0.97, independent or graph-correlated shocks, and one-at-a-time or bursty (blocks of 25) exposure. The design and the list of sweeps are in [design.md](design.md); the theory (B1, B1′, B1″, B2) is in [research/correlated_arms](../../../research/correlated_arms/README.md). Code is in [code/](code), outputs in [results/](results).

## Findings

1. **iid certificates fail under bursty persistent exposure, as B2 predicts.** With blocks of 25, the iid certificate is violated in 85–95% of runs at φ ≥ 0.9 (B2's variance inflation is 3.5× at φ = 0.9 and 4.4× at φ = 0.97). With one-at-a-time sampling it stays covered, because interleaving keeps repeat pulls about 20 rounds apart.
2. **Innovation-regression certificates are never violated.** B1, B1′ and B1″ have no violations in 2,080 SP-UCB and UCB runs across all sweeps, with independent or correlated shocks, in either exposure.
3. **Invalid certificates threaten irrevocable decisions more than regret.** Successive elimination with iid certificates removes the best arm in 35–45% of bursty runs at φ = 0.9 and in 90% at φ = 0.97; with B1″, never. Mean regret moves less, because the under-covered arms are mostly suboptimal.
4. **Tight certificates cost little regret.** B1's log-determinant ellipsoid is about 2× too wide at low persistence. The scalar bounds B1′ and B1″ remove most of that cost and beat iid pooling when persistence is low (10–16% lower regret at φ = 0). With bursty exposure at φ ≥ 0.5, where the iid certificate is the invalid one, B1″ costs 9–21% more regret with correlated shocks and at most 13% with independent shocks.

## Main sweep: B1′ and B1″ against iid certificates

20 seeds, T = 5,000, arm order shuffled ([coverage_runs_plugin.csv](results/coverage_runs_plugin.csv)). Mean regret of SP-UCB with each certificate, and the share of runs with any violation of the iid certificate. B1′ and B1″ were never violated.

| Shocks | Exposure | φ | iid | B1′ | B1″ | iid violated |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Correlated | One at a time | 0 | 357 | 317 | **313** | 0% |
| | | 0.5 | 460 | **383** | 412 | 0% |
| | | 0.9 | 642 | 646 | **606** | 0% |
| | | 0.97 | 693 | **683** | 760 | 0% |
| | Blocks of 25 | 0 | 372 | **319** | 330 | 0% |
| | | 0.5 | **395** | 497 | 479 | 0% |
| | | 0.9 | **706** | 841 | 792 | 85% |
| | | 0.97 | **816** | 939 | 889 | 90% |
| Independent | One at a time | 0 | 354 | **312** | 320 | 0% |
| | | 0.5 | 470 | 399 | **396** | 0% |
| | | 0.9 | 593 | 553 | **547** | 0% |
| | | 0.97 | **625** | 676 | 717 | 0% |
| | Blocks of 25 | 0 | 386 | 341 | **326** | 0% |
| | | 0.5 | **392** | 492 | 443 | 0% |
| | | 0.9 | **712** | 787 | 741 | 85% |
| | | 0.97 | 887 | **816** | 881 | 95% |

Successive elimination on the same worlds: the share of runs in which the best arm was eliminated.

| Shocks | Exposure | φ = 0.9, iid / B1″ | φ = 0.97, iid / B1″ |
| --- | --- | ---: | ---: |
| Correlated | Blocks of 25 | 35% / 0% | 90% / 0% |
| Independent | Blocks of 25 | 45% / 0% | 90% / 0% |
| Either | One at a time | 0% / 0% | 0% / 0% |

## Earlier sweeps

**v1: B1 against iid, one at a time** (30 seeds; [coverage_runs.csv](results/coverage_runs.csv)). Neither certificate was violated (0 of 240 runs each). B1's ellipsoid is conservative: mean regret 742–765 against 352–660 for iid SP-UCB with independent shocks. This showed that B2's failure needs bursty exposure.

**v2: bursty exposure** (20 seeds; [coverage_runs_v2.csv](results/coverage_runs_v2.csv)):

| Exposure | φ | Runs with a violation, iid SP-UCB | Rounds violated, iid SP-UCB | Runs with a violation, B1 | Mean regret, iid / B1 (independent shocks) |
| --- | ---: | ---: | ---: | ---: | --- |
| One at a time | 0.97 | 0% | 0% | 0% | 649 / 755 |
| Blocks of 25 | 0.5 | 5% | 5% | 0% | 406 / 916 |
| Blocks of 25 | 0.9 | 70–75% | 58–59% | 0% | 629 / 1,023 |
| Blocks of 25 | 0.97 | 90–100% | 86–88% | 0% | 853 / 1,034 |

The empirical-variance radius at level log t violates even at φ = 0, because variance estimates from 2–3 samples are tiny. That is a small-sample artifact, not persistence, and is excluded from the B2 claim.

**Elimination with B1** (20 seeds; [coverage_runs_elim.csv](results/coverage_runs_elim.csv), [coverage_runs_elim_long.csv](results/coverage_runs_elim_long.csv)). iid certificates eliminate the best arm in 40–75% of bursty runs at φ ≥ 0.9. B1 never does, but it also eliminates nothing, at T = 5,000 or at T = 20,000: its regret equals round-robin's. This motivated the tighter scalar bounds.

**B1′ for independent shocks** (20 seeds; [coverage_runs_scalar.csv](results/coverage_runs_scalar.csv)). Mean regret of SP-UCB with iid / B1 / B1′ certificates:

| Exposure | φ | iid / B1 / B1′ | iid violated | B1, B1′ violated |
| --- | ---: | --- | ---: | ---: |
| One at a time | 0 | 353 / 753 / **295** | 0% | 0% |
| One at a time | 0.5 | 457 / 752 / **396** | 0% | 0% |
| One at a time | 0.9 | 533 / 759 / 564 | 0% | 0% |
| One at a time | 0.97 | 649 / 755 / 679 | 0% | 0% |
| Blocks of 25 | 0 | 380 / 766 / **338** | 0% | 0% |
| Blocks of 25 | 0.5 | 406 / 916 / 510 | 5% | 0% |
| Blocks of 25 | 0.9 | 629 / 1,023 / 818 | 75% | 0% |
| Blocks of 25 | 0.97 | 853 / 1,034 / **828** | 90% | 0% |

## What the papers use

The B2 coverage figure and the certificate comparison in [research/claude_opus_10_09_v2](../../../research/claude_opus_10_09_v2/README.md) (Q3) come from `coverage_runs_plugin.csv`. Their predicted-against-observed inflation table is in [analysis/b2_prediction_vs_observed.md](../../../research/claude_opus_10_09_v2/analysis/b2_prediction_vs_observed.md).

## Reproduce

From the repository root:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/simulations/certificates_under_persistence/code/coverage.py --verify
OPENBLAS_NUM_THREADS=1 .venv/bin/python -I experiments/simulations/certificates_under_persistence/code/coverage.py --seeds 20 --jobs 2 --tag _plugin
# earlier sweeps: --tag _v2 | _elim | _scalar (--seeds 20); --tag _elim_long --horizon 20000; no tag with --seeds 30 for v1
```
