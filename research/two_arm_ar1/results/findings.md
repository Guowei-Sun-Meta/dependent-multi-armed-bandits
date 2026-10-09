# Checks of two-arm AR(1) allocation formulas

40,000 independent replications, budget 10, stationary noise variance one. Mean identification uses independent N(0, 0.25) priors; terminal-state identification has known zero means.

| Target | φ | Policy | Exact optimal PCS | Empirical PCS | Mean conditional PCS |
|---|---|---|---|---|---|
| mean | 0 | alternate | 0.76772 | 0.76780 ± 0.00414 | 0.76749 |
| mean | 0 | block | 0.76772 | 0.76785 ± 0.00414 | 0.76820 |
| mean | 0 | greedy | 0.76772 | 0.74375 ± 0.00428 | 0.74558 |
| mean | 0 | greedy_final_refresh | 0.76772 | 0.75428 ± 0.00422 | 0.75371 |
| state | 0 | alternate | 0.50000 | 0.49850 ± 0.00490 | 0.50000 |
| state | 0 | block | 0.50000 | 0.49850 ± 0.00490 | 0.50000 |
| state | 0 | greedy | 0.50000 | 0.49850 ± 0.00490 | 0.50000 |
| state | 0 | greedy_final_refresh | 0.50000 | 0.49850 ± 0.00490 | 0.50000 |
| mean | 0.5 | alternate | 0.73708 | 0.73738 ± 0.00431 | 0.73696 |
| mean | 0.5 | block | 0.73708 | 0.70542 ± 0.00447 | 0.70816 |
| mean | 0.5 | greedy | 0.73708 | 0.70168 ± 0.00448 | 0.70278 |
| mean | 0.5 | greedy_final_refresh | 0.73708 | 0.71162 ± 0.00444 | 0.71470 |
| state | 0.5 | alternate | 0.62935 | 0.62745 ± 0.00474 | 0.62905 |
| state | 0.5 | block | 0.62935 | 0.61045 ± 0.00478 | 0.61506 |
| state | 0.5 | greedy | 0.62935 | 0.62038 ± 0.00476 | 0.62102 |
| state | 0.5 | greedy_final_refresh | 0.62935 | 0.62855 ± 0.00474 | 0.62880 |
| mean | 0.9 | alternate | 0.67103 | 0.66973 ± 0.00461 | 0.67171 |
| mean | 0.9 | block | 0.67103 | 0.66010 ± 0.00464 | 0.66113 |
| mean | 0.9 | greedy | 0.67103 | 0.64968 ± 0.00468 | 0.65148 |
| mean | 0.9 | greedy_final_refresh | 0.67103 | 0.66492 ± 0.00463 | 0.66678 |
| state | 0.9 | alternate | 0.82717 | 0.82520 ± 0.00372 | 0.82791 |
| state | 0.9 | block | 0.82717 | 0.76405 ± 0.00416 | 0.76555 |
| state | 0.9 | greedy | 0.82717 | 0.77123 ± 0.00412 | 0.77242 |
| state | 0.9 | greedy_final_refresh | 0.82717 | 0.82555 ± 0.00372 | 0.82793 |
| mean | 0.99 | alternate | 0.65011 | 0.65192 ± 0.00467 | 0.65001 |
| mean | 0.99 | block | 0.65011 | 0.65017 ± 0.00467 | 0.64877 |
| mean | 0.99 | greedy | 0.65011 | 0.63713 ± 0.00471 | 0.63048 |
| mean | 0.99 | greedy_final_refresh | 0.65011 | 0.65045 ± 0.00467 | 0.64941 |
| state | 0.99 | alternate | 0.94491 | 0.94330 ± 0.00227 | 0.94449 |
| state | 0.99 | block | 0.94491 | 0.91470 ± 0.00274 | 0.91638 |
| state | 0.99 | greedy | 0.94491 | 0.85852 ± 0.00342 | 0.85942 |
| state | 0.99 | greedy_final_refresh | 0.94491 | 0.94388 ± 0.00226 | 0.94459 |

Mean identification: strict alternation attains the proven even-budget optimum. State identification: alternating and any policy that observes different arms in the last two rounds attain the proven optimum. The binomial intervals concern simulations, while the optimality claims come from the proofs in the research note. The greedy policies here are diagnostic comparators.
