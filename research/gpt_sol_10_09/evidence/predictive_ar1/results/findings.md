# Full-state oracle regret: generated results

40 independent runs per case; 5,000 burn-in rounds followed by 30,000 measured rounds. All parameters are known. Values are measured regret per round with approximate 95% intervals across runs.

| φ | Lower bound | Greedy | Thompson | Predictive Sampling | Two-step | Refresh |
|---|---|---|---|---|---|---|
| 0 | 1.1630 | 1.1636 ± 0.0017 | 1.1616 ± 0.0021 | 1.1636 ± 0.0017 | 1.1636 ± 0.0017 | 1.1636 ± 0.0017 |
| 0.1 | 1.0467 | 1.1196 ± 0.0017 | 1.1590 ± 0.0020 | 1.1409 ± 0.0020 | 1.1196 ± 0.0021 | 1.1638 ± 0.0018 |
| 0.5 | 0.5815 | 0.8926 ± 0.0018 | 1.0881 ± 0.0019 | 1.0203 ± 0.0020 | 0.8927 ± 0.0019 | 1.1646 ± 0.0026 |
| 0.9 | 0.1163 | 0.4613 ± 0.0025 | 0.6159 ± 0.0017 | 0.5669 ± 0.0017 | 0.4334 ± 0.0022 | 1.1695 ± 0.0069 |
| 0.99 | 0.0116 | 0.2687 ± 0.0060 | 0.1548 ± 0.0009 | 0.1495 ± 0.0010 | 0.1997 ± 0.0050 | 0.6031 ± 0.0041 |
| 0.995 | 0.0058 | 0.2566 ± 0.0094 | 0.0979 ± 0.0011 | 0.0951 ± 0.0010 | 0.1795 ± 0.0079 | 0.4322 ± 0.0046 |

At φ=0.99, Predictive Sampling has coefficient 0.1495 ± 0.0010, compared with Thompson 0.1548 ± 0.0009, greedy 0.2687 ± 0.0060, and two-step 0.1997 ± 0.0050. The point-estimate reduction relative to Thompson is 3.5%.
For the same φ with innovation variance 10^-4, exact scaling gives the PS coefficient 0.0106 ± 0.0001. The universal lower bound is 0.000824; the fixed-arm coefficient is 0.082440. These scaled values are not a separate simulation.

## Paired comparisons

Positive baseline-minus-PS values favor PS. Intervals use differences within each shared-trajectory run; comparison is at the measured horizon.

| Case | Baseline | Baseline minus PS |
|---|---|---|
| fast_noise_decoy | Greedy | 0.7456 ± 0.0143 |
| fast_noise_decoy | Thompson | 0.2234 ± 0.0032 |
| fast_noise_decoy | Two-step | 0.1849 ± 0.0055 |
| fast_noise_decoy | Refresh | 0.7456 ± 0.0143 |
| homogeneous_0.99 | Greedy | 0.1192 ± 0.0058 |
| homogeneous_0.99 | Thompson | 0.0054 ± 0.0005 |
| homogeneous_0.99 | Two-step | 0.0503 ± 0.0050 |
| homogeneous_0.99 | Refresh | 0.4536 ± 0.0046 |
| homogeneous_0.995 | Greedy | 0.1614 ± 0.0095 |
| homogeneous_0.995 | Thompson | 0.0028 ± 0.0003 |
| homogeneous_0.995 | Two-step | 0.0843 ± 0.0078 |
| homogeneous_0.995 | Refresh | 0.3371 ± 0.0052 |

## High-variance white-noise arm

Four zero-mean arms have φ=0.99 and stationary variance one. The fifth has mean 0.2, φ=0, and stationary variance four. Its current state cannot be predicted from past rewards.

| Policy | Regret per round | Fraction selecting white-noise arm |
|---|---|---|
| Fixed arm | 1.3308 ± 0.0103 | 1.000 |
| Greedy | 1.3308 ± 0.0103 | 1.000 |
| Thompson | 0.8086 ± 0.0032 | 0.347 |
| Predictive Sampling | 0.5852 ± 0.0044 | 0.112 |
| Two-step | 0.7701 ± 0.0067 | 0.381 |
| All-past-state observer | 0.4696 ± 0.0040 | 0.111 |

## Horizon sensitivity

These are coefficient estimates after the same burn-in, using different lengths of the measured trajectory. They assess finite-horizon stability, not convergence of a limiting coefficient.

| φ=0.99 policy | 10,000 rounds | 20,000 rounds | 30,000 rounds | Final 10,000 rounds |
|---|---|---|---|---|
| Greedy | 0.2740 | 0.2722 | 0.2687 | 0.2617 ± 0.0095 |
| Thompson | 0.1554 | 0.1555 | 0.1548 | 0.1536 ± 0.0022 |
| Predictive Sampling | 0.1498 | 0.1502 | 0.1495 | 0.1479 ± 0.0023 |
| Two-step | 0.2025 | 0.2005 | 0.1997 | 0.1981 ± 0.0087 |

The observed ranking is not a proof that Predictive Sampling or two-step control minimizes the long-run coefficient. Parameters are supplied; noisy observations and parameter learning are not evaluated.

![Coefficient versus memory](coefficients.svg)

![Cumulative regret at φ=0.99](cumulative.svg)
