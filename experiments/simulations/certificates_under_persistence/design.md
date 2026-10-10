# Certificates under Persistence: Experiment Design

9 October 2026. A simulation that tests the bridging results of the correlated-arms theory ([research/correlated_arms](../../../research/correlated_arms/README.md)). Certified pooling (SP-UCB, [A]) needs confidence bounds that hold at every round. Persistent rewards break the iid bounds, so:

- **B2** predicts that iid certificates miscover once φ > 0, and badly under bursty exposure: consecutive pulls inflate the variance of a sample mean by up to (1 + φ)/(1 − φ).
- **B1** (innovation-regression ellipsoid), **B1′** (scalar mixture bounds, independent shocks) and **B1″** (iterated nuisance plug-in, correlated shocks) claim valid certificates under any adaptive, restless schedule.

The experiment measures validity, regret and the correctness of irrevocable decisions for each certificate.

## World

| Element | Choice |
| --- | --- |
| Arms | N = 20 in 4 components of 5. Component means are 0.45, 0.25, 0.20 and 0.15 plus a uniform draw on [0, 0.1]; arm 0 is the unique best at 0.55 |
| Certificate | Component diameter ε_c = 0.1 (the oracle width) |
| Fluctuations | AR(1) with persistence φ ∈ {0, 0.5, 0.9, 0.97} and Var(z) = 1 |
| Shocks | "independent" (identity covariance) or "correlated" (unit-diagonal resolvent (I + 3L)⁻¹ of a path graph over the arms) |
| Observation noise | sd 0.1 |
| Exposure | One arm per round (b = 1), or commit blocks of b = 25 consecutive pulls, as with daily slates or batched updates |
| Horizon | T = 5,000 (20,000 for the long elimination run) |

## Policies and certificates

| Name in [code/coverage.py](code/coverage.py) | Index | Certificate |
| --- | --- | --- |
| `ucb_iid`, `sp_ucb_iid` | Arm UCB, SP-UCB | iid radius σ√(2ℓ/n), with σ² = V + r |
| `sp_ucb_emp` | SP-UCB | Empirical-variance radius at level log t |
| `ucb_st`, `sp_ucb_st` | Arm UCB, SP-UCB | B1: innovation regression with the all-time ellipsoid of [S] |
| `sp_ucb_st1` | SP-UCB | B1′: per-arm and per-component scalar mixture bounds (independent shocks) |
| `sp_ucb_st2` | SP-UCB | B1″: scalar bounds with other arms' means as bounded nuisances, iterated from [0, 1] |
| `se_iid`, `se_st`, `se_st1`, `se_st2` | Successive elimination | The same certificates; eliminating an arm is irrevocable |

## Measurements

- **Violation:** at some round, an arm's or a component's upper bound lies below its target (μ_i or the component maximum v_c). Recorded per run (any violation) and as the share of rounds violated.
- **Mean regret** against the best long-run mean.
- **Elimination:** whether the best arm was eliminated, when, and how many arms remain active at the end.

## Sweeps

| Tag | Output | Seeds | Configurations | Policies | Purpose |
| --- | --- | ---: | --- | --- | --- |
| (none) | `coverage_runs.csv` | 30 | both, b = 1 | UCB and SP-UCB with iid and B1 certificates | v1: B1 against B2 with one-at-a-time sampling |
| `_v2` | `coverage_runs_v2.csv` | 20 | both, b ∈ {1, 25} | v1 plus the empirical-variance radius | Bursty exposure |
| `_elim` | `coverage_runs_elim.csv` | 20 | both, b ∈ {1, 25} | Successive elimination, iid and B1 | Irrevocable decisions |
| `_elim_long` | `coverage_runs_elim_long.csv` | 20 | both, b ∈ {1, 25}, T = 20,000 | Same | Does B1 ever eliminate? |
| `_scalar` | `coverage_runs_scalar.csv` | 20 | independent, b ∈ {1, 25} | iid, B1, B1′ (SP-UCB and elimination) | Tight certificate for independent shocks |
| `_plugin` | `coverage_runs_plugin.csv` | 20 | both, b ∈ {1, 25}, arm order shuffled | iid, B1′, B1″ (SP-UCB and elimination) | Correlated shocks; the run used in the papers' figures |

The v1 file predates the block option. The current script always sweeps b ∈ {1, 25}, so its b = 1 rows reproduce v1's design. The `_plugin` sweep shuffles arm order, so that ties between unclipped upper bounds are not broken toward the best arm.

`--verify` checks the B2 variance formula against simulation, and the innovation information against dense GLS.
