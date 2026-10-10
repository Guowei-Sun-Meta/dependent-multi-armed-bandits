"""Check exact two-arm AR(1) selection allocations and short-horizon control.

The simulations distinguish unknown-mean identification from known-mean
terminal-state identification. All arms evolve each calendar round.

    python3 experiments/simulations/theory/ar_allocation/two_arm_ar1_allocation.py --verify
    python3 experiments/simulations/theory/ar_allocation/two_arm_ar1_allocation.py --runs 40000 --budget 10
"""

import argparse
import csv
from itertools import product
import json
import math
from pathlib import Path
import random
import statistics


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "research" / "two_arm_ar1" / "results"
NORMAL = statistics.NormalDist()
POLICIES = ("alternate", "block", "greedy", "greedy_final_refresh")


def information_factor(phi, gap):
    power = phi**gap
    return (1 - power) / (1 + power)


def information(times, phi, variance=1.0):
    if not times:
        return 0.0
    return (1 + sum(information_factor(phi, b - a)
                    for a, b in zip(times, times[1:]))) / variance


def schedule_information(schedule, phi, variance=1.0):
    return [information([t for t, a in enumerate(schedule, 1) if a == arm], phi, variance)
            for arm in range(2)]


def alternating_information(budget, phi, variance=1.0):
    if budget % 2:
        raise ValueError("The sharp alternating-allocation formula requires an even budget.")
    return (1 + (budget / 2 - 1) * information_factor(phi, 2)) / variance


def gaussian_bayes_pcs(prior_variance, information_per_arm):
    return 0.5 + math.atan(math.sqrt(prior_variance * information_per_arm)) / math.pi


def terminal_state_pcs(phi, budget):
    if budget == 0:
        return 0.5
    correlation = phi / math.sqrt(2) if budget == 1 else phi * math.sqrt((1 + phi**2) / 2)
    return 0.5 + math.asin(correlation) / math.pi


def positive_part(mean, sd):
    if sd == 0:
        return max(mean, 0.0)
    z = mean / sd
    return mean * NORMAL.cdf(z) + sd * math.exp(-z*z/2) / math.sqrt(2*math.pi)


def two_step_scores(means, variances, phi):
    common = phi * max(means)
    gap = abs(means[0] - means[1])
    return [means[i] + common + phi * positive_part(-gap, math.sqrt(variances[i]))
            for i in range(2)]


def solve(matrix, right):
    """Small independent covariance check; pivoted Gaussian elimination."""
    rows = [list(a) + [b] for a, b in zip(matrix, right)]
    n = len(rows)
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(rows[r][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        for j in range(col, n + 1):
            rows[col][j] /= scale
        for r in range(n):
            if r == col:
                continue
            scale = rows[r][col]
            for j in range(col, n + 1):
                rows[r][j] -= scale * rows[col][j]
    return [row[-1] for row in rows]


def verify():
    checks = 0
    for phi in (0.0, 0.1, 0.5, 0.9, 0.99):
        for times in ([1], [1, 2, 3, 4], [1, 3, 8, 10]):
            covariance = [[phi**abs(a-b) for b in times] for a in times]
            from_matrix = sum(solve(covariance, [1.0]*len(times)))
            assert math.isclose(from_matrix, information(times, phi), abs_tol=1e-10)
            checks += 1
        for budget in (2, 4, 6, 8, 10, 12):
            info_star = alternating_information(budget, phi)
            frequentist_variance = 2 / info_star
            bayesian_variance = 2 / (4 + info_star)  # tau^2 = 1/4
            for tail in product((0, 1), repeat=budget-1):
                ii = schedule_information((0,) + tail, phi)
                if min(ii) > 0:
                    assert sum(1 / x for x in ii) >= frequentist_variance - 1e-11
                assert sum(1 / (4 + x) for x in ii) >= bayesian_variance - 1e-11
                checks += 1
    # An odd budget has a genuine timing exception to strict alternation.
    odd_alt = schedule_information((0, 1, 0, 1, 0), 0.9)
    odd_shift = schedule_information((0, 1, 0, 0, 1), 0.9)
    assert sum(1/x for x in odd_shift) < sum(1/x for x in odd_alt)
    # Reachable two-period control example: recent slightly positive observation.
    q = 1 - 0.99**2
    scores = two_step_scores([0.05, 0], [q, 1], 0.99)
    assert scores[1] > scores[0]
    return {"matrix_and_exhaustive_checks": checks,
            "odd_budget_alternation_counterexample": True,
            "two_period_greedy_counterexample": {"means": [0.05, 0], "variances": [q, 1],
                                                  "phi": 0.99, "scores": scores},
            "novelty_claim": False}


class MeanBelief:
    def __init__(self, phi, prior_variance):
        self.phi = phi
        self.precision = [1 / prior_variance] * 2
        self.weighted = [0.0, 0.0]
        self.last_time = [None, None]
        self.last_value = [0.0, 0.0]

    def means(self):
        return [a / b for a, b in zip(self.weighted, self.precision)]

    def observe(self, arm, time, value):
        if self.last_time[arm] is None:
            self.precision[arm] += 1
            self.weighted[arm] += value
        else:
            power = self.phi**(time-self.last_time[arm])
            coefficient = 1 - power
            variance = 1 - power**2
            self.precision[arm] += coefficient**2 / variance
            self.weighted[arm] += coefficient * (value-power*self.last_value[arm]) / variance
        self.last_time[arm], self.last_value[arm] = time, value


def prescribed(name, time, budget, predictions, last_arm):
    if name == "alternate":
        return (time - 1) % 2
    if name == "block":
        return 0 if time <= budget // 2 else 1
    if name == "greedy_final_refresh" and time == budget:
        return 1 - last_arm
    return 0 if predictions[0] >= predictions[1] else 1


def simulate(phi, budget, runs, prior_variance):
    rng = random.Random(8108 + round(phi*1e6))
    names = [f"{target}:{policy}" for target in ("mean", "state") for policy in POLICIES]
    correct = {name: 0 for name in names}
    forecast_sum = {name: 0.0 for name in names}
    q = 1-phi**2
    for _ in range(runs):
        unknown_means = [math.sqrt(prior_variance) * rng.gauss(0, 1) for _ in range(2)]
        deviations = [rng.gauss(0, 1) for _ in range(2)]
        mean_beliefs = {p: MeanBelief(phi, prior_variance) for p in POLICIES}
        state_observations = {p: [None, None] for p in POLICIES}
        last_mean = {p: None for p in POLICIES}
        last_state = {p: None for p in POLICIES}
        for time in range(1, budget+1):
            # Actions use only past observations. States evolve exogenously.
            mean_actions, state_actions = {}, {}
            for policy in POLICIES:
                mean_actions[policy] = prescribed(policy, time, budget,
                                                  mean_beliefs[policy].means(), last_mean[policy])
                predictions = [0.0 if x is None else phi**(time-x[0])*x[1]
                               for x in state_observations[policy]]
                state_actions[policy] = prescribed(policy, time, budget, predictions, last_state[policy])
            deviations = [phi*x + math.sqrt(q)*rng.gauss(0, 1) for x in deviations]
            for policy in POLICIES:
                arm = mean_actions[policy]
                mean_beliefs[policy].observe(arm, time, unknown_means[arm]+deviations[arm])
                last_mean[policy] = arm
                arm = state_actions[policy]
                state_observations[policy][arm] = (time, deviations[arm])
                last_state[policy] = arm
        future_states = [phi*x + math.sqrt(q)*rng.gauss(0, 1) for x in deviations]
        true_mean = 0 if unknown_means[0] > unknown_means[1] else 1
        true_state = 0 if future_states[0] > future_states[1] else 1
        for policy in POLICIES:
            mean = mean_beliefs[policy].means()
            sd = math.sqrt(sum(1/x for x in mean_beliefs[policy].precision))
            name = "mean:" + policy
            correct[name] += int((0 if mean[0] >= mean[1] else 1) == true_mean)
            forecast_sum[name] += NORMAL.cdf(abs(mean[0]-mean[1])/sd)
            observations = state_observations[policy]
            mean = [0.0 if x is None else phi**(budget+1-x[0])*x[1] for x in observations]
            variance = [1.0 if x is None else 1-phi**(2*(budget+1-x[0])) for x in observations]
            name = "state:" + policy
            correct[name] += int((0 if mean[0] >= mean[1] else 1) == true_state)
            forecast_sum[name] += NORMAL.cdf(abs(mean[0]-mean[1])/math.sqrt(sum(variance)))
    rows = []
    info_star = alternating_information(budget, phi)
    for name in names:
        target, policy = name.split(":")
        pcs = correct[name] / runs
        optimum = gaussian_bayes_pcs(prior_variance, info_star) if target == "mean" else terminal_state_pcs(phi, budget)
        rows.append({"phi": phi, "budget": budget, "runs": runs, "target": target, "policy": policy,
                     "empirical_pcs": pcs, "ci95_halfwidth": 1.96*math.sqrt(pcs*(1-pcs)/runs),
                     "average_posterior_pcs": forecast_sum[name]/runs, "theoretical_optimum": optimum})
    return rows


def render_paper_inputs(rows, budget, prior_variance):
    """Generate the paper's table and exact-formula plot from the saved cases."""
    table = []
    for phi in (0.0, 0.5, 0.9, 0.99):
        cases = [next(row for row in rows if row["phi"] == phi
                      and row["target"] == target and row["policy"] == "alternate")
                 for target in ("mean", "state")]
        values = [f"{phi:g}"]
        for row in cases:
            values.extend([f"{row['theoretical_optimum']:.5f}",
                           f"${row['empirical_pcs']:.5f} \\pm {row['ci95_halfwidth']:.5f}$"])
        table.append(" & ".join(values) + r" \\")
    (OUTPUT / "summary_table.tex").write_text("\n".join(table) + "\n")
    with (OUTPUT / "pcs_curve.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["phi", "mean_pcs", "state_pcs"])
        for index in range(201):
            phi = index * 0.999 / 200
            info = alternating_information(budget, phi)
            writer.writerow([phi, gaussian_bayes_pcs(prior_variance, info),
                             terminal_state_pcs(phi, budget)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--runs", type=int, default=40000)
    parser.add_argument("--budget", type=int, default=10)
    parser.add_argument("--render-only", action="store_true")
    args = parser.parse_args()
    checks = verify()
    if args.verify:
        print(json.dumps(checks, indent=2))
        return
    if args.render_only:
        with (OUTPUT / "selection.csv").open() as handle:
            rows = [{key: value if key in ("target", "policy") else float(value)
                     for key, value in row.items()} for row in csv.DictReader(handle)]
        metadata = json.loads((OUTPUT / "metadata.json").read_text())
        render_paper_inputs(rows, metadata["budget"], metadata["mean_prior_variance"])
        print("Rendered", OUTPUT)
        return
    if args.budget < 2 or args.budget % 2 or args.runs < 2:
        parser.error("Use a positive even budget at least 2 and at least 2 runs.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for phi in (0.0, 0.5, 0.9, 0.99):
        rows.extend(simulate(phi, args.budget, args.runs, 0.25))
        print("Finished", phi, flush=True)
    with (OUTPUT / "selection.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {"stationary_noise_variance": 1, "mean_prior_variance": 0.25,
                "budget": args.budget, "runs": args.runs, "checks": checks,
                "sampling_clock": "restless, one exact observation each calendar round",
                "state_target": "largest state at budget+1", "mean_target": "largest latent long-run mean",
                "intervals": "approximate binomial 95% intervals, no asymptotic policy claim"}
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    text = ["# Checks of two-arm AR(1) allocation formulas", "",
            f"{args.runs:,} independent replications, budget {args.budget}, stationary noise variance one. "
            "Mean identification uses independent N(0, 0.25) priors; terminal-state identification has known zero means.", "",
            "| Target | φ | Policy | Exact optimal PCS | Empirical PCS | Mean conditional PCS |",
            "|---|---|---|---|---|---|"]
    for row in rows:
        text.append(f"| {row['target']} | {row['phi']:g} | {row['policy']} | {row['theoretical_optimum']:.5f} | "
                    f"{row['empirical_pcs']:.5f} ± {row['ci95_halfwidth']:.5f} | {row['average_posterior_pcs']:.5f} |")
    text.extend(["", "Mean identification: strict alternation attains the proven even-budget optimum. "
                 "State identification: alternating and any policy that observes different arms in the last two rounds "
                 "attain the proven optimum. The binomial intervals concern simulations, while the optimality claims "
                 "come from the proofs in the research note. The greedy policies here are diagnostic comparators."])
    (OUTPUT / "findings.md").write_text("\n".join(text)+"\n")
    render_paper_inputs(rows, args.budget, 0.25)
    print("Saved", OUTPUT)


if __name__ == "__main__":
    main()
