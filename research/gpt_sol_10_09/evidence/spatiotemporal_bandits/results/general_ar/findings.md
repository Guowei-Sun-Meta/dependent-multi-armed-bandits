# Fixed-mean selection with graph-correlated AR(p_i) innovations

200 independent paired noise trajectories per configuration, 6 arms, and 60 samples.
Each mean vector is fixed across all runs. Only stationary states, innovations, sensor noise, and policy randomization vary.
Innovation covariance carries spatial correlation. A separate deterministic graph-energy bound constrains the unknown mean.
All substantive AR models have order 2 or 3; the iid model is a misspecification baseline.

| Dynamics | Fixed mean | Policy | Opportunity loss | SE | PCS | MSE |
|---|---|---|---|---|---|---|
| lag_two | smooth | graph_ar_contrast | 0.0675 | 0.0079 | 0.420 | 0.1426 |
| lag_two | smooth | unstructured_ar_contrast | 0.0748 | 0.0086 | 0.405 | 0.1870 |
| lag_two | smooth | diagonal_noise_ar_contrast | 0.0718 | 0.0085 | 0.395 | 0.1563 |
| lag_two | smooth | wrong_mean_graph_ar_contrast | 0.0835 | 0.0098 | 0.390 | 0.1537 |
| lag_two | smooth | graph_iid_contrast | 0.1030 | 0.0110 | 0.365 | 0.1647 |
| lag_two | smooth | round_robin | 0.0785 | 0.0083 | 0.380 | 0.1085 |
| lag_two | smooth | block_cyclic | 0.0720 | 0.0083 | 0.415 | 0.0757 |
| lag_two | rough | graph_ar_contrast | 0.0510 | 0.0045 | 0.360 | 0.1492 |
| lag_two | rough | unstructured_ar_contrast | 0.0613 | 0.0071 | 0.365 | 0.1770 |
| lag_two | rough | diagonal_noise_ar_contrast | 0.0515 | 0.0057 | 0.395 | 0.1550 |
| lag_two | rough | wrong_mean_graph_ar_contrast | 0.0595 | 0.0064 | 0.340 | 0.1511 |
| lag_two | rough | graph_iid_contrast | 0.0630 | 0.0077 | 0.345 | 0.1638 |
| lag_two | rough | round_robin | 0.0978 | 0.0121 | 0.335 | 0.1194 |
| lag_two | rough | block_cyclic | 0.0583 | 0.0071 | 0.380 | 0.0830 |
| oscillatory | smooth | graph_ar_contrast | 0.0393 | 0.0031 | 0.455 | 0.0898 |
| oscillatory | smooth | unstructured_ar_contrast | 0.0508 | 0.0047 | 0.415 | 0.1121 |
| oscillatory | smooth | diagonal_noise_ar_contrast | 0.0393 | 0.0033 | 0.465 | 0.0950 |
| oscillatory | smooth | wrong_mean_graph_ar_contrast | 0.0453 | 0.0042 | 0.445 | 0.0931 |
| oscillatory | smooth | graph_iid_contrast | 0.0555 | 0.0058 | 0.420 | 0.0970 |
| oscillatory | smooth | round_robin | 0.0665 | 0.0059 | 0.360 | 0.0510 |
| oscillatory | smooth | block_cyclic | 0.0568 | 0.0051 | 0.375 | 0.0598 |
| oscillatory | rough | graph_ar_contrast | 0.0350 | 0.0026 | 0.470 | 0.0917 |
| oscillatory | rough | unstructured_ar_contrast | 0.0315 | 0.0026 | 0.520 | 0.1166 |
| oscillatory | rough | diagonal_noise_ar_contrast | 0.0345 | 0.0026 | 0.470 | 0.0917 |
| oscillatory | rough | wrong_mean_graph_ar_contrast | 0.0400 | 0.0037 | 0.450 | 0.1041 |
| oscillatory | rough | graph_iid_contrast | 0.0393 | 0.0037 | 0.455 | 0.0962 |
| oscillatory | rough | round_robin | 0.0410 | 0.0028 | 0.415 | 0.0541 |
| oscillatory | rough | block_cyclic | 0.0478 | 0.0048 | 0.385 | 0.0586 |
| heterogeneous | smooth | graph_ar_contrast | 0.0578 | 0.0056 | 0.380 | 0.1074 |
| heterogeneous | smooth | unstructured_ar_contrast | 0.0703 | 0.0067 | 0.370 | 0.1281 |
| heterogeneous | smooth | diagonal_noise_ar_contrast | 0.0635 | 0.0062 | 0.385 | 0.1130 |
| heterogeneous | smooth | wrong_mean_graph_ar_contrast | 0.0663 | 0.0060 | 0.335 | 0.1106 |
| heterogeneous | smooth | graph_iid_contrast | 0.0615 | 0.0065 | 0.380 | 0.1071 |
| heterogeneous | smooth | round_robin | 0.0763 | 0.0076 | 0.355 | 0.0569 |
| heterogeneous | smooth | block_cyclic | 0.0638 | 0.0067 | 0.420 | 0.0607 |
| heterogeneous | rough | graph_ar_contrast | 0.0475 | 0.0051 | 0.390 | 0.1045 |
| heterogeneous | rough | unstructured_ar_contrast | 0.0403 | 0.0028 | 0.425 | 0.1237 |
| heterogeneous | rough | diagonal_noise_ar_contrast | 0.0425 | 0.0045 | 0.455 | 0.1080 |
| heterogeneous | rough | wrong_mean_graph_ar_contrast | 0.0428 | 0.0038 | 0.435 | 0.1101 |
| heterogeneous | rough | graph_iid_contrast | 0.0515 | 0.0057 | 0.400 | 0.1081 |
| heterogeneous | rough | round_robin | 0.0675 | 0.0090 | 0.440 | 0.0561 |
| heterogeneous | rough | block_cyclic | 0.0478 | 0.0052 | 0.420 | 0.0631 |

Positive paired loss differences favor graph AR contrast sampling.

| Dynamics | Fixed mean | Comparator | Loss difference | Approx. 95% half-width |
|---|---|---|---|---|
| lag_two | smooth | unstructured_ar_contrast | 0.0073 | 0.0159 |
| lag_two | smooth | diagonal_noise_ar_contrast | 0.0043 | 0.0149 |
| lag_two | smooth | wrong_mean_graph_ar_contrast | 0.0160 | 0.0183 |
| lag_two | smooth | graph_iid_contrast | 0.0355 | 0.0193 |
| lag_two | smooth | round_robin | 0.0110 | 0.0207 |
| lag_two | smooth | block_cyclic | 0.0045 | 0.0209 |
| lag_two | rough | unstructured_ar_contrast | 0.0103 | 0.0142 |
| lag_two | rough | diagonal_noise_ar_contrast | 0.0005 | 0.0136 |
| lag_two | rough | wrong_mean_graph_ar_contrast | 0.0085 | 0.0128 |
| lag_two | rough | graph_iid_contrast | 0.0120 | 0.0174 |
| lag_two | rough | round_robin | 0.0467 | 0.0231 |
| lag_two | rough | block_cyclic | 0.0073 | 0.0158 |
| oscillatory | smooth | unstructured_ar_contrast | 0.0115 | 0.0108 |
| oscillatory | smooth | diagonal_noise_ar_contrast | 0.0000 | 0.0076 |
| oscillatory | smooth | wrong_mean_graph_ar_contrast | 0.0060 | 0.0095 |
| oscillatory | smooth | graph_iid_contrast | 0.0162 | 0.0121 |
| oscillatory | smooth | round_robin | 0.0272 | 0.0120 |
| oscillatory | smooth | block_cyclic | 0.0175 | 0.0112 |
| oscillatory | rough | unstructured_ar_contrast | -0.0035 | 0.0057 |
| oscillatory | rough | diagonal_noise_ar_contrast | -0.0005 | 0.0047 |
| oscillatory | rough | wrong_mean_graph_ar_contrast | 0.0050 | 0.0082 |
| oscillatory | rough | graph_iid_contrast | 0.0042 | 0.0077 |
| oscillatory | rough | round_robin | 0.0060 | 0.0068 |
| oscillatory | rough | block_cyclic | 0.0127 | 0.0113 |
| heterogeneous | smooth | unstructured_ar_contrast | 0.0125 | 0.0143 |
| heterogeneous | smooth | diagonal_noise_ar_contrast | 0.0057 | 0.0115 |
| heterogeneous | smooth | wrong_mean_graph_ar_contrast | 0.0085 | 0.0137 |
| heterogeneous | smooth | graph_iid_contrast | 0.0038 | 0.0122 |
| heterogeneous | smooth | round_robin | 0.0185 | 0.0171 |
| heterogeneous | smooth | block_cyclic | 0.0060 | 0.0149 |
| heterogeneous | rough | unstructured_ar_contrast | -0.0073 | 0.0114 |
| heterogeneous | rough | diagonal_noise_ar_contrast | -0.0050 | 0.0078 |
| heterogeneous | rough | wrong_mean_graph_ar_contrast | -0.0048 | 0.0101 |
| heterogeneous | rough | graph_iid_contrast | 0.0040 | 0.0130 |
| heterogeneous | rough | round_robin | 0.0200 | 0.0176 |
| heterogeneous | rough | block_cyclic | 0.0002 | 0.0119 |

The fixed supplied bounds B=2 and S=2 contain both mean vectors. The all-time confidence audit tests graph_ar_contrast only; its coverage and terminal certificate rates are repeated across policy rows.
PCS is the repeated-noise success probability at a fixed truth. It is not averaged over a mean prior. Final recommendations without a passed certificate do not inherit the fixed-confidence stopping guarantee.
The contrast rule reduces inverse regularized information for a selected comparison. It is a heuristic, with no general finite-budget optimality claim.
Numerical checks: 1525; details in checks.json.
