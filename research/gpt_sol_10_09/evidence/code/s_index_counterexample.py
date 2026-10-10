"""A deterministic check of graph smoothing bias in bandit selection.

Run with Python 3; no third-party packages are required:
    python3 experiments/s_index_counterexample.py

Three arms have means (1, 0.9, 0). The supplied graph connects arms 1 and
3 with weight 1 and leaves arm 2 isolated. For lambda=1, the original
S-index is Q*y, where Q=(I+L)^(-1). This graph is deliberately misaligned.

Compare ordinary UCB, a naive S-index plus the ordinary arm bonus, and
the bias-corrected intersection index derived in the accompanying note.
The last policy uses the valid supplied bound mu.T*L*mu <= 1. Rewards are
deterministic; sigma=1 is a conservative sub-Gaussian noise bound.

This is a failure demonstration, not a performance benchmark or a claim
that the proposed policy improves regret on informative graphs.
"""

import argparse
import math


MEANS = (1.0, 0.9, 0.0)
Q = (
    (2.0 / 3.0, 0.0, 1.0 / 3.0),
    (0.0, 1.0, 0.0),
    (1.0 / 3.0, 0.0, 2.0 / 3.0),
)
# lambda*S*sqrt(diag(Q*L*Q)), with lambda=S=1.
BIAS_BOUNDS = (1.0 / 3.0, 0.0, 1.0 / 3.0)


def transform(values):
    return [sum(weight * value for weight, value in zip(row, values)) for row in Q]


def simulate(policy, horizon):
    if horizon < len(MEANS):
        raise ValueError("The horizon must allow one initial pull of each arm.")
    counts = [1] * len(MEANS)
    sums = list(MEANS)
    delta = 1.0 / horizon
    log_term = math.log(2.0 * len(MEANS) * horizon / delta)

    for _ in range(len(MEANS), horizon):
        averages = [total / count for total, count in zip(sums, counts)]
        radii = [math.sqrt(2.0 * log_term / count) for count in counts]
        raw_upper = [mean + radius for mean, radius in zip(averages, radii)]
        if policy == "ordinary_ucb":
            scores = raw_upper
        else:
            smoothed = transform(averages)
            if policy == "naive_s_index_ucb":
                scores = [mean + radius for mean, radius in zip(smoothed, radii)]
            elif policy == "bias_corrected_intersection":
                propagated_radii = transform(radii)
                scores = [
                    min(raw, mean + radius + bias)
                    for raw, mean, radius, bias in zip(
                        raw_upper, smoothed, propagated_radii, BIAS_BOUNDS
                    )
                ]
            else:
                raise ValueError(f"Unknown policy: {policy}")
        arm = max(range(len(MEANS)), key=scores.__getitem__)
        counts[arm] += 1
        sums[arm] += MEANS[arm]

    regret = sum((max(MEANS) - mean) * count for mean, count in zip(MEANS, counts))
    return counts, regret


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizons", type=int, nargs="+", default=[1000, 10000, 100000])
    args = parser.parse_args()
    if any(horizon < len(MEANS) for horizon in args.horizons):
        parser.error("Every horizon must be at least 3.")

    smoothed = transform(MEANS)
    print(f"True means: {MEANS}")
    print(f"Exact S-index: {tuple(round(value, 6) for value in smoothed)}")
    print("True best arm: 1; smoothed best arm: 2")
    print("policy,horizon,arm_1_pulls,arm_2_pulls,arm_3_pulls,regret,regret_per_round")
    for horizon in args.horizons:
        for policy in (
            "ordinary_ucb",
            "naive_s_index_ucb",
            "bias_corrected_intersection",
        ):
            counts, regret = simulate(policy, horizon)
            print(
                f"{policy},{horizon},{counts[0]},{counts[1]},{counts[2]},"
                f"{regret:.6f},{regret / horizon:.6f}"
            )


if __name__ == "__main__":
    main()
