# Multiple-arm AR(p) extension checks

9 October 2026.

46,606 covariance, Kalman-information, affine-information, predictive-sampling, and exhaustive AR(1) schedule checks passed.

## Three-arm adaptive PCS example

Independent N(0,1) mean priors and iid observation variance one. After observing arms 1 and 2 once, posterior means are (a,a,0) and variances (1/2,1/2,1). One sample remains. Values integrate the Bayes-optimal terminal recommendation.

| a | Resample arm 1 | Sample arm 3 |
|---|---:|---:|
| 0 | 0.433658 | 0.488470 |
| 1 | 0.566712 | 0.459138 |
| 2 | 0.623042 | 0.490949 |
| 3 | 0.632981 | 0.499220 |
| 5 | 0.633860 | 0.499999 |
| 10 | 0.633860 | 0.500000 |

The proof uses the limiting values as a tends to infinity: resampling approaches 1/2 + asin(sqrt(1/6))/pi, while sampling arm 3 approaches 1/2. Continuity gives a positive-probability region of strict improvement. The numerical table illustrates the proof; it is not a global optimal-policy claim.

## Heterogeneous AR(1), AR(2), AR(3) mean identification

Budget 12, 40,000 independent stationary replications, fixed round-robin schedule. Exact PCS integral: 0.528698. Simulated PCS: 0.528175 ± 0.004892 (approximate 95% binomial interval). This checks schedule evaluation, not optimality of round-robin PCS.

The saved JSON contains coefficients, variances, counterexamples, and numerical conventions. The derivations are in the research note and manuscript.
