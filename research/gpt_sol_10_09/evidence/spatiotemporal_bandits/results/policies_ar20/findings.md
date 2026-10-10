# Fixed-mean spatial AR(20): UCB, Thompson-style sampling, and PCS

The study contains **100 arms**, order **20** per arm, **32 independent paired noise worlds per configuration**, and **1000 decisions** per world. There are 5 configurations and 14 learning policies plus 4 information benchmarks. Result completeness: **complete**.

The mean vector is deterministic and identical across noise worlds and configurations. Only deviations, sensor noise, and policy randomization change. Each learning rule receives only its selected reading after its action. All arms evolve every calendar round. Policies share latent paths and potential sensor noises within each replicate.

See [policy derivations](../../policies.md), [summary with intervals](summary.csv), [paired comparisons](paired.csv), [raw runs](runs.jsonl), [metadata](metadata.json), and [numerical checks](checks.json).

## Objectives and uncertainty

Oracle regret compares actual latent reward with the maximum current field. Mean pseudo-regret sums permanent mean gaps. Stationary mean reward regret subtracts actual reward from T times the best permanent mean and can be negative. Actual reward regret against always choosing the best-mean arm is reported separately and can be negative. PCS measures terminal selection of that fixed best mean. Known-mean benchmarks have artificial PCS one and are excluded from learning-policy selection comparisons.

Continuous-metric intervals use Student t across independent worlds. PCS intervals use Wilson's binomial formula. Paired differences use the same world for both policies and approximate Student t intervals, including PCS differences. These are pointwise 95% intervals, without simultaneous adjustment over policies or configurations. An observed winner is not proof of a universally best policy or a significant difference.

The budget includes one initial observation of every arm. Subsequent square-age forced probes have a vanishing fraction asymptotically; at this budget they still matter. UCB scale 0.7, Thompson scale 1, and H=0.1 I+0.5 L are fixed across all configurations. No per-configuration parameter optimization is performed.

## Terminal performance

All continuous regret entries below are **per decision**. Brackets are 95% intervals. The full CSV includes every policy and checkpoint.

### Persistent dense AR(20)

| Policy | Oracle regret | Mean pseudo-regret | PCS | Simple regret |
|---|---:|---:|---:|---:|
| IID UCB | 1.397 [1.356, 1.438] | 0.668 [0.614, 0.721] | 0.19 [0.09, 0.35] | 0.391 |
| Independent AR UCB | 1.429 [1.385, 1.472] | 0.701 [0.663, 0.740] | 0.25 [0.13, 0.42] | 0.327 |
| Joint mean UCB | 1.453 [1.404, 1.502] | 0.680 [0.607, 0.753] | 0.12 [0.05, 0.28] | 0.429 |
| Joint mean TS | 1.909 [1.872, 1.945] | 0.751 [0.713, 0.788] | 0.22 [0.11, 0.39] | 0.336 |
| Joint full-state UCB | 1.248 [1.207, 1.289] | 0.686 [0.636, 0.735] | 0.22 [0.11, 0.39] | 0.372 |
| Joint predictive UCB | 1.426 [1.393, 1.459] | 0.715 [0.680, 0.750] | 0.12 [0.05, 0.28] | 0.385 |
| Joint predictive TS | 1.675 [1.641, 1.710] | 0.768 [0.743, 0.792] | 0.22 [0.11, 0.39] | 0.339 |
| Contrast LUCB | 1.646 [1.595, 1.697] | 0.734 [0.692, 0.775] | 0.19 [0.09, 0.35] | 0.398 |
| Top-two contrast TS | 2.064 [2.042, 2.086] | 0.809 [0.790, 0.829] | 0.25 [0.13, 0.42] | 0.333 |
| Round robin | 2.486 [2.451, 2.520] | 0.910 [0.910, 0.910] | 0.16 [0.07, 0.32] | 0.396 |
| Known-mean greedy | 1.211 [1.144, 1.277] | 0.190 [0.151, 0.230] | knows truth | 0.000 |
| Best-mean arm | 1.618 [1.484, 1.751] | 0.000 [0.000, 0.000] | knows truth | 0.000 |
| Full-past genie | 0.502 [0.488, 0.515] | 0.667 [0.626, 0.707] | knows truth | 0.000 |

Observed learning-policy leaders: oracle regret—Joint full-state UCB; mean pseudo-regret—IID UCB; PCS—IID TS. Ties and overlapping uncertainty should be assessed in the CSV, not interpreted as rankings.

### Weak dense AR(20)

| Policy | Oracle regret | Mean pseudo-regret | PCS | Simple regret |
|---|---:|---:|---:|---:|
| IID UCB | 2.131 [2.102, 2.160] | 0.607 [0.585, 0.629] | 0.72 [0.55, 0.84] | 0.062 |
| Independent AR UCB | 1.890 [1.852, 1.928] | 0.367 [0.333, 0.402] | 0.66 [0.48, 0.80] | 0.082 |
| Joint mean UCB | 1.994 [1.963, 2.025] | 0.487 [0.459, 0.515] | 0.81 [0.65, 0.91] | 0.056 |
| Joint mean TS | 2.136 [2.104, 2.168] | 0.591 [0.563, 0.620] | 0.72 [0.55, 0.84] | 0.081 |
| Joint full-state UCB | 1.838 [1.781, 1.894] | 0.321 [0.267, 0.375] | 0.53 [0.36, 0.69] | 0.117 |
| Joint predictive UCB | 2.008 [1.980, 2.036] | 0.493 [0.468, 0.518] | 0.91 [0.76, 0.97] | 0.037 |
| Joint predictive TS | 2.160 [2.134, 2.186] | 0.608 [0.587, 0.629] | 0.72 [0.55, 0.84] | 0.068 |
| Contrast LUCB | 2.088 [2.061, 2.115] | 0.570 [0.548, 0.593] | 0.84 [0.68, 0.93] | 0.043 |
| Top-two contrast TS | 2.251 [2.232, 2.270] | 0.710 [0.694, 0.726] | 0.78 [0.61, 0.89] | 0.060 |
| Round robin | 2.474 [2.461, 2.488] | 0.910 [0.910, 0.910] | 0.34 [0.20, 0.52] | 0.253 |
| Known-mean greedy | 1.547 [1.531, 1.564] | 0.002 [0.001, 0.002] | knows truth | 0.000 |
| Best-mean arm | 1.547 [1.531, 1.564] | 0.000 [0.000, 0.000] | knows truth | 0.000 |
| Full-past genie | 1.535 [1.520, 1.549] | 0.035 [0.032, 0.038] | knows truth | 0.000 |

Observed learning-policy leaders: oracle regret—Joint full-state UCB; mean pseudo-regret—Joint full-state UCB; PCS—Joint predictive UCB. Ties and overlapping uncertainty should be assessed in the CSV, not interpreted as rankings.

### Lag-20 AR(20)

| Policy | Oracle regret | Mean pseudo-regret | PCS | Simple regret |
|---|---:|---:|---:|---:|
| IID UCB | 2.160 [2.122, 2.198] | 0.622 [0.591, 0.652] | 0.53 [0.36, 0.69] | 0.111 |
| Independent AR UCB | 1.841 [1.814, 1.869] | 0.545 [0.525, 0.565] | 0.66 [0.48, 0.80] | 0.081 |
| Joint mean UCB | 1.943 [1.899, 1.987] | 0.427 [0.389, 0.465] | 0.69 [0.51, 0.82] | 0.068 |
| Joint mean TS | 2.149 [2.120, 2.179] | 0.615 [0.591, 0.639] | 0.72 [0.55, 0.84] | 0.060 |
| Joint full-state UCB | 1.760 [1.735, 1.786] | 0.534 [0.511, 0.556] | 0.69 [0.51, 0.82] | 0.068 |
| Joint predictive UCB | 1.838 [1.814, 1.861] | 0.549 [0.530, 0.568] | 0.75 [0.58, 0.87] | 0.061 |
| Joint predictive TS | 2.230 [2.215, 2.246] | 0.773 [0.763, 0.783] | 0.56 [0.39, 0.72] | 0.117 |
| Contrast LUCB | 2.025 [1.993, 2.056] | 0.502 [0.477, 0.528] | 0.84 [0.68, 0.93] | 0.034 |
| Top-two contrast TS | 2.269 [2.248, 2.289] | 0.715 [0.699, 0.731] | 0.72 [0.55, 0.84] | 0.063 |
| Round robin | 2.480 [2.456, 2.503] | 0.910 [0.910, 0.910] | 0.28 [0.16, 0.45] | 0.314 |
| Known-mean greedy | 1.309 [1.288, 1.331] | 0.152 [0.145, 0.158] | knows truth | 0.000 |
| Best-mean arm | 1.577 [1.541, 1.612] | 0.000 [0.000, 0.000] | knows truth | 0.000 |
| Full-past genie | 0.340 [0.337, 0.344] | 0.676 [0.667, 0.684] | knows truth | 0.000 |

Observed learning-policy leaders: oracle regret—Joint full-state UCB; mean pseudo-regret—Joint mean UCB; PCS—Contrast LUCB. Ties and overlapping uncertainty should be assessed in the CSV, not interpreted as rankings.

### Heterogeneous AR(20)

| Policy | Oracle regret | Mean pseudo-regret | PCS | Simple regret |
|---|---:|---:|---:|---:|
| IID UCB | 1.717 [1.650, 1.785] | 0.705 [0.660, 0.749] | 0.00 [0.00, 0.11] | 0.631 |
| Independent AR UCB | 1.725 [1.683, 1.768] | 0.518 [0.478, 0.559] | 0.41 [0.26, 0.58] | 0.346 |
| Joint mean UCB | 1.659 [1.615, 1.703] | 0.624 [0.558, 0.689] | 0.12 [0.05, 0.28] | 0.379 |
| Joint mean TS | 2.085 [2.042, 2.128] | 0.681 [0.653, 0.709] | 0.47 [0.31, 0.64] | 0.166 |
| Joint full-state UCB | 1.647 [1.608, 1.686] | 0.397 [0.368, 0.426] | 0.47 [0.31, 0.64] | 0.175 |
| Joint predictive UCB | 1.617 [1.568, 1.666] | 0.700 [0.671, 0.729] | 0.25 [0.13, 0.42] | 0.291 |
| Joint predictive TS | 1.897 [1.842, 1.952] | 0.758 [0.739, 0.777] | 0.34 [0.20, 0.52] | 0.257 |
| Contrast LUCB | 1.817 [1.769, 1.866] | 0.605 [0.555, 0.656] | 0.41 [0.26, 0.58] | 0.245 |
| Top-two contrast TS | 2.211 [2.183, 2.239] | 0.751 [0.735, 0.767] | 0.56 [0.39, 0.72] | 0.139 |
| Round robin | 2.516 [2.497, 2.535] | 0.910 [0.910, 0.910] | 0.38 [0.23, 0.55] | 0.351 |
| Known-mean greedy | 1.328 [1.277, 1.378] | 0.133 [0.123, 0.144] | knows truth | 0.000 |
| Best-mean arm | 1.602 [1.574, 1.630] | 0.000 [0.000, 0.000] | knows truth | 0.000 |
| Full-past genie | 0.789 [0.754, 0.824] | 0.632 [0.599, 0.666] | knows truth | 0.000 |

Observed learning-policy leaders: oracle regret—Joint predictive UCB; mean pseudo-regret—Joint full-state UCB; PCS—Top-two contrast TS. Ties and overlapping uncertainty should be assessed in the CSV, not interpreted as rankings.

### Independent spatial innovations

| Policy | Oracle regret | Mean pseudo-regret | PCS | Simple regret |
|---|---:|---:|---:|---:|
| IID UCB | 1.453 [1.415, 1.492] | 0.582 [0.541, 0.624] | 0.19 [0.09, 0.35] | 0.396 |
| Independent AR UCB | 1.381 [1.335, 1.427] | 0.640 [0.612, 0.668] | 0.28 [0.16, 0.45] | 0.271 |
| Joint mean UCB | 1.506 [1.453, 1.559] | 0.498 [0.431, 0.565] | 0.28 [0.16, 0.45] | 0.291 |
| Joint mean TS | 1.964 [1.928, 2.000] | 0.626 [0.597, 0.655] | 0.31 [0.18, 0.49] | 0.234 |
| Joint full-state UCB | 1.270 [1.216, 1.325] | 0.583 [0.552, 0.615] | 0.31 [0.18, 0.49] | 0.275 |
| Joint predictive UCB | 1.491 [1.439, 1.544] | 0.633 [0.607, 0.659] | 0.38 [0.23, 0.55] | 0.196 |
| Joint predictive TS | 1.767 [1.712, 1.821] | 0.711 [0.693, 0.729] | 0.25 [0.13, 0.42] | 0.282 |
| Contrast LUCB | 1.691 [1.638, 1.744] | 0.581 [0.529, 0.632] | 0.25 [0.13, 0.42] | 0.326 |
| Top-two contrast TS | 2.151 [2.128, 2.174] | 0.724 [0.707, 0.741] | 0.38 [0.23, 0.55] | 0.213 |
| Round robin | 2.621 [2.593, 2.649] | 0.910 [0.910, 0.910] | 0.28 [0.16, 0.45] | 0.306 |
| Known-mean greedy | 1.107 [1.048, 1.165] | 0.160 [0.135, 0.185] | knows truth | 0.000 |
| Best-mean arm | 1.627 [1.503, 1.752] | 0.000 [0.000, 0.000] | knows truth | 0.000 |
| Full-past genie | 0.505 [0.481, 0.528] | 0.596 [0.562, 0.630] | knows truth | 0.000 |

Observed learning-policy leaders: oracle regret—Joint full-state UCB; mean pseudo-regret—Joint mean UCB; PCS—Joint predictive UCB. Ties and overlapping uncertainty should be assessed in the CSV, not interpreted as rankings.

## Actual reward against the stationary mean

Joint full-state UCB illustrates why permanent mean gaps and actual reward regret must be reported separately. Negative stationary reward regret means accumulated reward exceeds T times the best permanent mean. The fixed-arm path comparator has the same expectation, with additional finite-path noise from that arm.

| Configuration | Stationary reward regret / T [95% CI] | Mean pseudo-regret / T | Fixed-arm reward regret / T [95% CI] |
|---|---:|---:|---:|
| persistent | -0.308 [-0.375, -0.240] | 0.686 | -0.370 [-0.499, -0.241] |
| weak | 0.270 [0.212, 0.329] | 0.321 | 0.290 [0.241, 0.339] |
| seasonal | 0.185 [0.150, 0.219] | 0.534 | 0.184 [0.149, 0.218] |
| heterogeneous | 0.041 [-0.005, 0.088] | 0.397 | 0.045 [0.002, 0.087] |
| no_spatial | -0.443 [-0.518, -0.367] | 0.583 | -0.357 [-0.487, -0.228] |

## Paired comparisons

Positive improvement means lower regret/loss, or higher PCS. These comparisons are paired across noise worlds; a negative number favors the baseline.

| Configuration | Comparison | Metric | Improvement [95% CI] |
|---|---|---|---:|
| heterogeneous | Joint full-state UCB vs IID UCB | Oracle regret | 0.070 [0.001, 0.140] |
| heterogeneous | Joint predictive UCB vs IID UCB | Oracle regret | 0.101 [0.055, 0.146] |
| heterogeneous | Joint predictive UCB vs Independent AR UCB | Oracle regret | 0.108 [0.068, 0.149] |
| heterogeneous | Joint predictive TS vs Joint full-state TS | Oracle regret | 0.327 [0.286, 0.368] |
| heterogeneous | Joint mean UCB vs IID UCB | Mean regret | 0.081 [0.036, 0.126] |
| heterogeneous | Contrast LUCB vs Round robin | PCS | 0.031 [-0.219, 0.282] |
| heterogeneous | Top-two contrast TS vs Round robin | PCS | 0.188 [-0.062, 0.437] |
| no_spatial | Joint full-state UCB vs IID UCB | Oracle regret | 0.183 [0.134, 0.233] |
| no_spatial | Joint predictive UCB vs IID UCB | Oracle regret | -0.038 [-0.081, 0.004] |
| no_spatial | Joint predictive UCB vs Independent AR UCB | Oracle regret | -0.111 [-0.143, -0.078] |
| no_spatial | Joint predictive TS vs Joint full-state TS | Oracle regret | 0.199 [0.157, 0.240] |
| no_spatial | Joint mean UCB vs IID UCB | Mean regret | 0.084 [0.026, 0.142] |
| no_spatial | Contrast LUCB vs Round robin | PCS | -0.031 [-0.176, 0.113] |
| no_spatial | Top-two contrast TS vs Round robin | PCS | 0.094 [-0.074, 0.262] |
| persistent | Joint full-state UCB vs IID UCB | Oracle regret | 0.149 [0.108, 0.190] |
| persistent | Joint predictive UCB vs IID UCB | Oracle regret | -0.029 [-0.075, 0.017] |
| persistent | Joint predictive UCB vs Independent AR UCB | Oracle regret | 0.003 [-0.034, 0.039] |
| persistent | Joint predictive TS vs Joint full-state TS | Oracle regret | 0.163 [0.140, 0.187] |
| persistent | Joint mean UCB vs IID UCB | Mean regret | -0.013 [-0.087, 0.062] |
| persistent | Contrast LUCB vs Round robin | PCS | 0.031 [-0.140, 0.202] |
| persistent | Top-two contrast TS vs Round robin | PCS | 0.094 [-0.074, 0.262] |
| seasonal | Joint full-state UCB vs IID UCB | Oracle regret | 0.399 [0.365, 0.434] |
| seasonal | Joint predictive UCB vs IID UCB | Oracle regret | 0.322 [0.289, 0.355] |
| seasonal | Joint predictive UCB vs Independent AR UCB | Oracle regret | 0.003 [-0.027, 0.034] |
| seasonal | Joint predictive TS vs Joint full-state TS | Oracle regret | 0.043 [0.023, 0.064] |
| seasonal | Joint mean UCB vs IID UCB | Mean regret | 0.195 [0.167, 0.222] |
| seasonal | Contrast LUCB vs Round robin | PCS | 0.562 [0.339, 0.786] |
| seasonal | Top-two contrast TS vs Round robin | PCS | 0.438 [0.256, 0.619] |
| weak | Joint full-state UCB vs IID UCB | Oracle regret | 0.293 [0.233, 0.354] |
| weak | Joint predictive UCB vs IID UCB | Oracle regret | 0.123 [0.088, 0.157] |
| weak | Joint predictive UCB vs Independent AR UCB | Oracle regret | -0.119 [-0.152, -0.086] |
| weak | Joint predictive TS vs Joint full-state TS | Oracle regret | 0.185 [0.160, 0.209] |
| weak | Joint mean UCB vs IID UCB | Mean regret | 0.120 [0.087, 0.153] |
| weak | Contrast LUCB vs Round robin | PCS | 0.500 [0.276, 0.724] |
| weak | Top-two contrast TS vs Round robin | PCS | 0.438 [0.214, 0.661] |

## Irreducible oracle-regret coefficient

The full-past genie knows all arms' lag states and fixed means, but chooses before the fresh innovation. Its expected per-round regret is the proven lower bound G(mu,K0)-G(mu,K0-Q). We estimate it with 200,000 independent paired Gaussian samples per configuration. This calculation is independent of the policy experiment and its serial trajectory noise.

| Configuration | Innovation floor [MC 95% CI] | Sampled full-past genie | Best-mean arm |
|---|---:|---:|---:|
| persistent | 0.493 [0.491, 0.495] | 0.502 [0.488, 0.515] | 1.618 [1.484, 1.751] |
| weak | 1.556 [1.554, 1.559] | 1.535 [1.520, 1.549] | 1.547 [1.531, 1.564] |
| seasonal | 0.340 [0.338, 0.342] | 0.340 [0.337, 0.344] | 1.577 [1.541, 1.612] |
| heterogeneous | 0.789 [0.786, 0.791] | 0.789 [0.754, 0.824] | 1.602 [1.574, 1.630] |
| no_spatial | 0.515 [0.513, 0.516] | 0.505 [0.481, 0.528] | 1.627 [1.503, 1.752] |

Linear oracle regret and sublinear mean pseudo-regret are compatible: they use different comparators. A decreasing oracle-regret ratio over this finite budget does not establish convergence to a particular coefficient. The known-mean greedy filter is an implementable information benchmark, not a solved optimal causal policy.

Certified mean-UCB checkpoint confidence audits: persistent 1.000, weak 1.000, seasonal 1.000, heterogeneous 1.000, no_spatial 1.000. These are checks at recorded checkpoints, not a continuous empirical coverage audit and not a terminal selection certificate.

## What is established and what remains open

- Exact correlated-AR likelihood calculations are independently checked against dense Gaussian conditioning; mixed-filter covariance orientation, independent AR blocks, contrast information gains, and fixed physical means are verified.
- The certified mean-UCB policy has a conservative high-probability sublinear mean-regret bound under supplied graph/norm bounds and known correct dynamics. Practical UCB and Thompson-style rules do not inherit that guarantee.
- Gaussian uncertainty draws use inverse penalized information. They are not a physical mean population and are not automatically calibrated frequentist posterior draws.
- PCS rules are one-step contrast-information designs. The top-two rule is inspired by top-two Thompson sampling but differs from the published algorithm; its optimality theorems are not imported.
- Forecast policies removing Q ignore only independent fresh innovations, retaining uncertainty about all past lag states and permanent means. They remain myopic and can undervalue observations with delayed future relevance.
- This is one fixed mean surface with five noise/dynamics configurations. It does not establish robustness to arbitrary graph misspecification, unknown AR coefficients, unknown innovation covariance, other gap profiles, or non-Gaussian traffic counts.

![Oracle regret](oracle_regret.png)

![Mean pseudo-regret](mean_regret.png)

![Stationary mean reward regret](stationary_reward_regret.png)

![Fixed-truth PCS](pcs.png)

![Objective tradeoffs](tradeoffs.png)
