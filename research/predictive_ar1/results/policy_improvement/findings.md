# Long-horizon knowledge-gradient comparison

The multiplier φ/(1−φ) is derived from retaining one new observation and ignoring subsequent feedback in the continuation calculation. It is not tuned to these results. This approximation does not solve the full Bellman equation.

Matched to the original 40 runs, 5,000-round burn-in, and 30,000 measured rounds. Common means zero and stationary variance one.

| φ | Greedy | Two-step | Predictive Sampling | Long-horizon KG | PS minus KG (paired) |
|---|---|---|---|---|---|
| 0 | 1.1636 | 1.1636 ± 0.0017 | 1.1636 ± 0.0017 | 1.1636 ± 0.0017 | 0.0000 ± 0.0000 |
| 0.1 | 1.1196 | 1.1196 ± 0.0021 | 1.1409 ± 0.0020 | 1.1195 ± 0.0021 | 0.0214 ± 0.0020 |
| 0.5 | 0.8926 | 0.8927 ± 0.0019 | 1.0203 ± 0.0020 | 0.8932 ± 0.0018 | 0.1271 ± 0.0025 |
| 0.9 | 0.4613 | 0.4334 ± 0.0022 | 0.5669 ± 0.0017 | 0.4574 ± 0.0016 | 0.1095 ± 0.0018 |
| 0.99 | 0.2687 | 0.1997 ± 0.0050 | 0.1495 ± 0.0010 | 0.1659 ± 0.0011 | -0.0164 ± 0.0010 |
| 0.995 | 0.2566 | 0.1795 ± 0.0079 | 0.0951 ± 0.0010 | 0.1171 ± 0.0011 | -0.0219 ± 0.0009 |

Positive paired differences favor long-horizon KG. Intervals are approximate 95% intervals over independent replications. Homogeneous positive-persistence models only; these comparisons do not certify an optimal long-run coefficient.

The lifetime-weighted rule improves on PS at moderate persistence but loses at φ=0.99 and 0.995. Two-step control is strongest among these tested policies at φ=0.9; PS is strongest at 0.99 and 0.995. The one-observation continuation ignores future feedback, so its geometric information value is an approximation when used repeatedly.
