# Permanent-mean selection under spatial AR(1) fluctuations

200 independent paired runs per configuration; six nodes and 48 measurements.
Means are drawn once and held fixed. All policies see the same possible readings within a run. Residual variance is one and measurement variance is 0.1.
True mean graph strength 2 matches the fitted prior; strength 0 is an unstructured prior and stresses the imposed smoothing.
PCS below evaluates the largest-posterior-mean recommendation. This decision minimizes Bayesian opportunity loss under a correct model; it is not the general multi-arm Bayes-PCS rule.

| True mean strength | phi | Policy | Opportunity loss | SE | PCS | MSE per mean | Contrast coverage |
|---|---|---|---|---|---|---|---|
| 0 | 0 | graph_ar_kg | 0.0424 | 0.0073 | 0.765 | 0.3094 | 0.850 |
| 0 | 0 | unstructured_ar_kg | 0.0379 | 0.0076 | 0.805 | 0.1508 | 0.970 |
| 0 | 0 | diagonal_mean_ar_kg | 0.0516 | 0.0108 | 0.825 | 0.2124 | 0.925 |
| 0 | 0 | graph_iid_kg | 0.0440 | 0.0077 | 0.780 | 0.3009 | 0.850 |
| 0 | 0 | wrong_mean_graph_ar_kg | 0.0420 | 0.0086 | 0.805 | 0.3096 | 0.895 |
| 0 | 0 | graph_ar_contrast | 0.0669 | 0.0122 | 0.780 | 0.3986 | 0.840 |
| 0 | 0 | round_robin | 0.1039 | 0.0166 | 0.720 | 0.2171 | 0.870 |
| 0 | 0.9 | graph_ar_kg | 0.0988 | 0.0156 | 0.730 | 0.3635 | 0.910 |
| 0 | 0.9 | unstructured_ar_kg | 0.1037 | 0.0149 | 0.710 | 0.2452 | 0.970 |
| 0 | 0.9 | diagonal_mean_ar_kg | 0.1230 | 0.0179 | 0.690 | 0.2884 | 0.925 |
| 0 | 0.9 | graph_iid_kg | 0.1618 | 0.0202 | 0.625 | 0.4396 | 0.755 |
| 0 | 0.9 | wrong_mean_graph_ar_kg | 0.1220 | 0.0169 | 0.690 | 0.3278 | 0.905 |
| 0 | 0.9 | graph_ar_contrast | 0.1327 | 0.0181 | 0.670 | 0.4463 | 0.890 |
| 0 | 0.9 | round_robin | 0.1140 | 0.0166 | 0.700 | 0.2960 | 0.920 |
| 0 | 0.99 | graph_ar_kg | 0.2915 | 0.0353 | 0.570 | 0.5832 | 0.855 |
| 0 | 0.99 | unstructured_ar_kg | 0.2535 | 0.0319 | 0.605 | 0.4216 | 0.945 |
| 0 | 0.99 | diagonal_mean_ar_kg | 0.2509 | 0.0303 | 0.595 | 0.4999 | 0.875 |
| 0 | 0.99 | graph_iid_kg | 0.2878 | 0.0339 | 0.570 | 0.7183 | 0.610 |
| 0 | 0.99 | wrong_mean_graph_ar_kg | 0.3298 | 0.0380 | 0.540 | 0.5861 | 0.805 |
| 0 | 0.99 | graph_ar_contrast | 0.3071 | 0.0365 | 0.555 | 0.6093 | 0.865 |
| 0 | 0.99 | round_robin | 0.3221 | 0.0380 | 0.545 | 0.5733 | 0.860 |
| 2 | 0 | graph_ar_kg | 0.0667 | 0.0105 | 0.735 | 0.1069 | 0.980 |
| 2 | 0 | unstructured_ar_kg | 0.0845 | 0.0121 | 0.680 | 0.1316 | 0.965 |
| 2 | 0 | diagonal_mean_ar_kg | 0.0737 | 0.0108 | 0.670 | 0.1213 | 0.945 |
| 2 | 0 | graph_iid_kg | 0.0718 | 0.0111 | 0.725 | 0.1059 | 0.985 |
| 2 | 0 | wrong_mean_graph_ar_kg | 0.0761 | 0.0110 | 0.665 | 0.1272 | 0.950 |
| 2 | 0 | graph_ar_contrast | 0.0815 | 0.0121 | 0.685 | 0.1324 | 0.930 |
| 2 | 0 | round_robin | 0.0883 | 0.0121 | 0.655 | 0.0931 | 0.935 |
| 2 | 0.9 | graph_ar_kg | 0.1913 | 0.0206 | 0.500 | 0.1978 | 0.930 |
| 2 | 0.9 | unstructured_ar_kg | 0.2104 | 0.0216 | 0.500 | 0.2444 | 0.970 |
| 2 | 0.9 | diagonal_mean_ar_kg | 0.2017 | 0.0214 | 0.515 | 0.2299 | 0.920 |
| 2 | 0.9 | graph_iid_kg | 0.2047 | 0.0225 | 0.530 | 0.2791 | 0.720 |
| 2 | 0.9 | wrong_mean_graph_ar_kg | 0.2027 | 0.0229 | 0.520 | 0.2287 | 0.880 |
| 2 | 0.9 | graph_ar_contrast | 0.1872 | 0.0206 | 0.525 | 0.2133 | 0.940 |
| 2 | 0.9 | round_robin | 0.1745 | 0.0193 | 0.520 | 0.1810 | 0.940 |
| 2 | 0.99 | graph_ar_kg | 0.2739 | 0.0271 | 0.385 | 0.2534 | 0.975 |
| 2 | 0.99 | unstructured_ar_kg | 0.2467 | 0.0251 | 0.420 | 0.3178 | 0.980 |
| 2 | 0.99 | diagonal_mean_ar_kg | 0.2746 | 0.0265 | 0.400 | 0.2697 | 0.955 |
| 2 | 0.99 | graph_iid_kg | 0.2928 | 0.0274 | 0.405 | 0.5191 | 0.620 |
| 2 | 0.99 | wrong_mean_graph_ar_kg | 0.2667 | 0.0254 | 0.415 | 0.2718 | 0.930 |
| 2 | 0.99 | graph_ar_contrast | 0.2764 | 0.0274 | 0.400 | 0.2556 | 0.975 |
| 2 | 0.99 | round_robin | 0.2856 | 0.0278 | 0.390 | 0.2510 | 0.970 |

Positive paired opportunity-loss differences favor graph AR knowledge gradient.

| True mean strength | phi | Comparator | Difference | Approx. 95% half-width |
|---|---|---|---|---|
| 0 | 0 | unstructured_ar_kg | -0.0045 | 0.0175 |
| 0 | 0 | diagonal_mean_ar_kg | 0.0092 | 0.0244 |
| 0 | 0 | graph_iid_kg | 0.0016 | 0.0097 |
| 0 | 0 | wrong_mean_graph_ar_kg | -0.0005 | 0.0185 |
| 0 | 0 | graph_ar_contrast | 0.0245 | 0.0238 |
| 0 | 0 | round_robin | 0.0614 | 0.0343 |
| 0 | 0.9 | unstructured_ar_kg | 0.0050 | 0.0246 |
| 0 | 0.9 | diagonal_mean_ar_kg | 0.0243 | 0.0284 |
| 0 | 0.9 | graph_iid_kg | 0.0630 | 0.0372 |
| 0 | 0.9 | wrong_mean_graph_ar_kg | 0.0232 | 0.0326 |
| 0 | 0.9 | graph_ar_contrast | 0.0340 | 0.0270 |
| 0 | 0.9 | round_robin | 0.0153 | 0.0300 |
| 0 | 0.99 | unstructured_ar_kg | -0.0381 | 0.0504 |
| 0 | 0.99 | diagonal_mean_ar_kg | -0.0407 | 0.0516 |
| 0 | 0.99 | graph_iid_kg | -0.0037 | 0.0499 |
| 0 | 0.99 | wrong_mean_graph_ar_kg | 0.0383 | 0.0760 |
| 0 | 0.99 | graph_ar_contrast | 0.0156 | 0.0287 |
| 0 | 0.99 | round_robin | 0.0306 | 0.0415 |
| 2 | 0 | unstructured_ar_kg | 0.0178 | 0.0307 |
| 2 | 0 | diagonal_mean_ar_kg | 0.0070 | 0.0258 |
| 2 | 0 | graph_iid_kg | 0.0052 | 0.0098 |
| 2 | 0 | wrong_mean_graph_ar_kg | 0.0094 | 0.0281 |
| 2 | 0 | graph_ar_contrast | 0.0148 | 0.0293 |
| 2 | 0 | round_robin | 0.0216 | 0.0292 |
| 2 | 0.9 | unstructured_ar_kg | 0.0192 | 0.0334 |
| 2 | 0.9 | diagonal_mean_ar_kg | 0.0104 | 0.0378 |
| 2 | 0.9 | graph_iid_kg | 0.0134 | 0.0384 |
| 2 | 0.9 | wrong_mean_graph_ar_kg | 0.0114 | 0.0458 |
| 2 | 0.9 | graph_ar_contrast | -0.0041 | 0.0347 |
| 2 | 0.9 | round_robin | -0.0168 | 0.0321 |
| 2 | 0.99 | unstructured_ar_kg | -0.0272 | 0.0393 |
| 2 | 0.99 | diagonal_mean_ar_kg | 0.0008 | 0.0381 |
| 2 | 0.99 | graph_iid_kg | 0.0189 | 0.0329 |
| 2 | 0.99 | wrong_mean_graph_ar_kg | -0.0072 | 0.0435 |
| 2 | 0.99 | graph_ar_contrast | 0.0025 | 0.0211 |
| 2 | 0.99 | round_robin | 0.0117 | 0.0242 |

## Interpretation and scope

The diagonal-mean baseline retains the graph prior's marginal variances while removing its cross-covariances. The separate unstructured prior is I and matches the rough-mean generative model.
The confidence theorem audit supplies each trajectory's actual mean norm and energy as valid radii, independently of measurement noise. The sampling policies do not use those radii; this does not demonstrate learning or validating them.
Contrast coverage refers to a fixed endpoint contrast and Gaussian posterior 95% intervals. Those intervals have a Bayesian interpretation only under the matched generative model. All-time frequentist confidence uses a distinct, bias-aware radius and is generally conservative.
The KG rule is exact with one observation remaining for opportunity loss; rolling KG and the selected-contrast heuristic have no fixed-budget optimality guarantee. Forced probes ensure asymptotic observation of every arm.
No real traffic data, hyperparameter fitting, unknown AR dynamics, general PCS-optimal control, or matching lower/upper bound is evaluated.
Separate exact checks: 8597; see checks.json.
