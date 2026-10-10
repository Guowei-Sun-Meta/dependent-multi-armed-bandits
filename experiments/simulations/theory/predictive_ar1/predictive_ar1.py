"""Known-parameter restless AR(1) policies versus a full-current-state oracle.

Only the standard library is required. Every policy observes one current state;
all policies share each exogenous trajectory and cannot see unselected states.
PS is the exact-observation specialization of Liu, Van Roy, and Xu (2023),
not a new algorithm. The two-step policy solves a rolling two-period problem.

    python3 experiments/simulations/theory/predictive_ar1/predictive_ar1.py --verify
    python3 experiments/simulations/theory/predictive_ar1/predictive_ar1.py --runs 40 --horizon 30000 --burn 5000
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import json
import math
from pathlib import Path
import random
import statistics
import time


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = ROOT / "research" / "predictive_ar1" / "results"
POLICIES = ("fixed", "greedy", "ts", "ps", "two_step", "refresh")
SQRT_TWO_PI = math.sqrt(2 * math.pi)


def normal_cdf(x):
    return 0.5 * math.erfc(-x / math.sqrt(2))


def expected_positive(mean, sd):
    if sd == 0:
        return max(mean, 0.0)
    z = mean / sd
    return mean * normal_cdf(z) + sd * math.exp(-0.5 * z * z) / SQRT_TWO_PI


def simpson(function, lower, upper, steps=8000):
    assert steps % 2 == 0
    dx = (upper - lower) / steps
    total = function(lower) + function(upper)
    total += 4 * sum(function(lower + i * dx) for i in range(1, steps, 2))
    total += 2 * sum(function(lower + i * dx) for i in range(2, steps, 2))
    return total * dx / 3


def expected_max(means, sds):
    """Independent Gaussian order statistic; exact degenerate baseline handling."""
    random_indices = [i for i, sd in enumerate(sds) if sd > 0]
    fixed_values = [means[i] for i, sd in enumerate(sds) if sd == 0]
    if not random_indices:
        return max(means)

    def distribution(x):
        probability = 1.0
        for i in random_indices:
            probability *= normal_cdf((x - means[i]) / sds[i])
        return probability

    endpoint = max(abs(value) for value in means) + 10 * max(sds)
    if fixed_values:
        baseline = max(fixed_values)
        return baseline + simpson(lambda x: 1 - distribution(x), baseline, endpoint)
    return simpson(lambda x: 1 - distribution(x) - distribution(-x), 0, endpoint)


def ps_variance(phi, variance, innovation_variance):
    return phi * phi * variance * variance / (phi * phi * variance + innovation_variance)


def make_cases():
    cases = []
    for phi in (0.0, 0.1, 0.5, 0.9, 0.99, 0.995):
        cases.append({"name": f"homogeneous_{phi:g}", "means": [0.0] * 5,
                      "phis": [phi] * 5, "stationary_variances": [1.0] * 5})
    cases.append({"name": "fast_noise_decoy", "means": [0.0] * 4 + [0.2],
                  "phis": [0.99] * 4 + [0.0],
                  "stationary_variances": [1.0] * 4 + [4.0]})
    return cases


def prepare_case(case, horizon, burn):
    result = dict(case)
    means, phis, stationary = [case[key] for key in
                               ("means", "phis", "stationary_variances")]
    k = len(means)
    innovations = [v * (1 - phi * phi) for v, phi in zip(stationary, phis)]
    oracle = expected_max(means, [math.sqrt(v) for v in stationary])
    past = expected_max(means, [abs(phi) * math.sqrt(v)
                               for phi, v in zip(phis, stationary)])
    blind = oracle - max(means)
    # A deterministic K-probe / (H-K)-greedy block has a valid coefficient bound.
    best_bound, period = blind, None
    for candidate in range(k, 2001):
        max_variance = max(v * (1 - phi ** (2 * candidate))
                           for v, phi in zip(stationary, phis))
        fraction = k / candidate
        bound = fraction * (oracle - statistics.mean(means)) \
            + (1 - fraction) * math.sqrt(2 * max_variance * math.log(k))
        if bound < best_bound:
            best_bound, period = bound, candidate
    # Entry zero denotes the unobserved stationary prior, not a fresh observation.
    ages = horizon + burn + 2
    lookup = []
    for phi, v, q in zip(phis, stationary, innovations):
        values = [v] + [v * (1 - phi ** (2 * h)) for h in range(1, ages)]
        lookup.append({"variance": values,
                       "ts_sd": [math.sqrt(value) for value in values],
                       "ps_sd": [math.sqrt(ps_variance(phi, value, q)) for value in values],
                       "future_sd": [abs(phi) * math.sqrt(value) for value in values]})
    result.update({"innovations": innovations, "oracle_rate": oracle,
                   "full_past_lower_bound": oracle - past,
                   "blind_coefficient": blind, "refresh_bound": best_bound,
                   "refresh_period": period, "lookup": lookup})
    return result


class BeliefPolicy:
    def __init__(self, name, case, seed):
        self.name, self.case = name, case
        self.means, self.phis = case["means"], case["phis"]
        self.k = len(self.means)
        self.predictions = self.means[:]
        self.ages = [0] * self.k
        self.counts = [0] * self.k
        # TS and PS use the same auxiliary Gaussian draws for paired comparisons.
        self.rng = random.Random(seed + (19 if name in ("ts", "ps") else 37))

    def choose(self, t):
        m, ages, tables = self.predictions, self.ages, self.case["lookup"]
        if self.name == "fixed":
            return max(range(self.k), key=self.means.__getitem__)
        if self.name == "refresh":
            period = self.case["refresh_period"]
            if period is None:
                return max(range(self.k), key=self.means.__getitem__)
            phase = t % period
            if phase < self.k:
                return phase
        if self.name in ("greedy", "refresh"):
            scores = m
        elif self.name in ("ts", "ps"):
            field = self.name + "_sd"
            scores = [m[i] + tables[i][field][ages[i]] * self.rng.gauss(0, 1)
                      for i in range(self.k)]
        elif self.name == "two_step":
            projected = [mu + phi * (value - mu)
                         for mu, phi, value in zip(self.means, self.phis, m)]
            scores = []
            for i in range(self.k):
                competitor = max(projected[j] for j in range(self.k) if j != i)
                sd = tables[i]["future_sd"][ages[i]]
                scores.append(m[i] + competitor
                              + expected_positive(projected[i] - competitor, sd))
        elif self.name == "long_kg":
            if len(set(self.phis)) != 1 or len(set(self.means)) != 1 or self.phis[0] < 0:
                raise ValueError("The closed-form long-horizon KG requires common nonnegative persistence and means.")
            lifetime = self.phis[0] / (1 - self.phis[0])
            scores = []
            for i in range(self.k):
                competitor = max(m[j] for j in range(self.k) if j != i)
                gap = abs(m[i] - competitor)
                information_value = expected_positive(-gap, tables[i]["ts_sd"][ages[i]])
                scores.append(m[i] + lifetime * information_value)
        else:
            raise ValueError(self.name)
        # Fixed ordering is deterministic, non-anticipating tie-breaking.
        return max(range(self.k), key=scores.__getitem__)

    def observe_and_advance(self, arm, reward):
        self.predictions[arm] = reward
        self.counts[arm] += 1
        for i, (mu, phi) in enumerate(zip(self.means, self.phis)):
            self.predictions[i] = mu + phi * (self.predictions[i] - mu)
            self.ages[i] = 1 if i == arm else (self.ages[i] + 1 if self.ages[i] else 0)


def simulate_run(case, horizon, burn, run, policy_names=POLICIES):
    seed = 7919 * (run + 1) + 20261008
    environment = random.Random(seed)
    means, phis = case["means"], case["phis"]
    states = [mu + math.sqrt(v) * environment.gauss(0, 1)
              for mu, v in zip(means, case["stationary_variances"])]
    innovation_sds = [math.sqrt(q) for q in case["innovations"]]
    policies = {name: BeliefPolicy(name, case, seed + 100_003) for name in policy_names}
    names = policy_names + ("past_state_genie",)
    regret, tail, reward_sum = [{name: 0.0 for name in names} for _ in range(3)]
    measured_counts = {name: [0] * len(means) for name in names}
    checkpoints = sorted({min(horizon, h) for h in (1000, 2500, 5000, 10000, 20000, horizon)})
    curves = []
    oracle_sum = 0.0
    tail_start = horizon - min(horizon, 10000)
    for t in range(burn + horizon):
        # All actions are chosen before the current state vector is generated.
        actions = {name: policy.choose(t) for name, policy in policies.items()}
        genie_predictions = [mu + phi * (state - mu)
                             for mu, phi, state in zip(means, phis, states)]
        actions["past_state_genie"] = max(range(len(means)), key=genie_predictions.__getitem__)
        states = [mu + phi * (state - mu) + sd * environment.gauss(0, 1)
                  for mu, phi, state, sd in zip(means, phis, states, innovation_sds)]
        oracle = max(states)
        measured_t = t - burn + 1
        if measured_t > 0:
            oracle_sum += oracle
        for name, arm in actions.items():
            reward = states[arm]
            if name in policies:
                policies[name].observe_and_advance(arm, reward)
            if measured_t > 0:
                gap = oracle - reward
                assert gap >= 0
                regret[name] += gap
                reward_sum[name] += reward
                measured_counts[name][arm] += 1
                if measured_t > tail_start:
                    tail[name] += gap
        if measured_t in checkpoints:
            for name in names:
                curves.append({"case": case["name"], "run": run, "policy": name,
                               "t": measured_t, "regret": regret[name]})
    rows = []
    for name in names:
        rows.append({"case": case["name"], "run": run, "policy": name,
                     "horizon": horizon, "regret": regret[name],
                     "coefficient": regret[name] / horizon,
                     "tail_coefficient": tail[name] / (horizon - tail_start),
                     "reward_rate": reward_sum[name] / horizon,
                     "oracle_rate": oracle_sum / horizon,
                     "last_arm_fraction": measured_counts[name][-1] / horizon,
                     "counts": json.dumps(measured_counts[name])})
    return rows, curves


def run_case(case, horizon, burn, runs, policy_names=POLICIES):
    prepared = prepare_case(case, horizon, burn)
    rows, curves = [], []
    for run in range(runs):
        a, b = simulate_run(prepared, horizon, burn, run, policy_names)
        rows.extend(a)
        curves.extend(b)
    metadata = {key: value for key, value in prepared.items() if key != "lookup"}
    return metadata, rows, curves


def estimate(values):
    mean = statistics.mean(values)
    # Approximate normal 95% intervals over independent replications.
    ci = 1.96 * statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return mean, ci


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(directory, rows, curves, metadata):
    summaries = []
    for case in metadata:
        for name in POLICIES + ("past_state_genie",):
            selected = [row for row in rows if row["case"] == case["name"] and row["policy"] == name]
            rate, ci = estimate([row["coefficient"] for row in selected])
            tail_rate, tail_ci = estimate([row["tail_coefficient"] for row in selected])
            fraction, _ = estimate([row["last_arm_fraction"] for row in selected])
            summaries.append({"case": case["name"], "policy": name,
                              "coefficient": rate, "ci95_halfwidth": ci,
                              "tail_coefficient": tail_rate, "tail_ci95_halfwidth": tail_ci,
                              "last_arm_fraction": fraction,
                              "full_past_lower_bound": case["full_past_lower_bound"],
                              "blind_coefficient": case["blind_coefficient"]})
    trajectory = []
    keys = sorted({(row["case"], row["policy"], row["t"]) for row in curves})
    for case, name, t in keys:
        values = [row["regret"] for row in curves
                  if row["case"] == case and row["policy"] == name and row["t"] == t]
        mean, ci = estimate(values)
        trajectory.append({"case": case, "policy": name, "t": t,
                           "mean_regret": mean, "ci95_halfwidth": ci,
                           "coefficient": mean / t})
    paired = []
    for case in metadata:
        for baseline in ("greedy", "ts", "two_step", "refresh"):
            differences = []
            for run in range(max(row["run"] for row in rows) + 1):
                matching = {row["policy"]: row["coefficient"] for row in rows
                            if row["case"] == case["name"] and row["run"] == run}
                differences.append(matching[baseline] - matching["ps"])
            mean, ci = estimate(differences)
            paired.append({"case": case["name"], "baseline": baseline,
                           "baseline_minus_ps": mean, "ci95_halfwidth": ci})
    write_csv(directory / "summary.csv", summaries)
    write_csv(directory / "curves.csv", trajectory)
    write_csv(directory / "paired.csv", paired)
    return summaries


def verify():
    assert math.isclose(expected_max([0, 0], [1, 1]), 1 / math.sqrt(math.pi), abs_tol=1e-10)
    assert expected_max([0, 0.2], [0, 0]) == 0.2
    assert math.isclose(expected_max([0, 0], [1, 0]), 1 / SQRT_TWO_PI, abs_tol=1e-10)
    for phi in (0, 0.1, 0.9, 0.99):
        q = 1 - phi * phi
        for h in (1, 3, 20):
            v = 1 - phi ** (2 * h)
            # Gaussian regression identity: Var(E[X | next X]) = Cov^2 / Var(next X).
            posterior_residual = v * q / (phi * phi * v + q)
            assert math.isclose(ps_variance(phi, v, q), v - posterior_residual, abs_tol=1e-12)
        if phi == 0:
            assert ps_variance(phi, 1.0, q) == 0
    # Independent Monte Carlo check of the two-period continuation value.
    rng = random.Random(13)
    samples = [max(0.4, -0.1 + 0.7 * rng.gauss(0, 1)) for _ in range(100_000)]
    analytic = 0.4 + expected_positive(-0.5, 0.7)
    assert abs(statistics.mean(samples) - analytic) < 5 * statistics.stdev(samples) / math.sqrt(len(samples))
    # Two-arm oracle gap: actual current states and auxiliary PS scores are independent.
    means, variances, phi, q = [0.6, 0.1], [0.2, 0.7], 0.9, 0.19
    score_variances = [ps_variance(phi, v, q) for v in variances]
    delta = abs(means[0] - means[1])
    current_sd, score_sd = math.sqrt(sum(variances)), math.sqrt(sum(score_variances))
    gap_formula = (current_sd * math.exp(-0.5 * (delta / current_sd)**2) / SQRT_TWO_PI
                   - delta * normal_cdf(-delta / current_sd)
                   + delta * normal_cdf(-delta / score_sd))
    gaps = []
    for _ in range(100_000):
        current = [mu + math.sqrt(v) * rng.gauss(0, 1) for mu, v in zip(means, variances)]
        scores = [mu + math.sqrt(v) * rng.gauss(0, 1) for mu, v in zip(means, score_variances)]
        chosen = max(range(2), key=scores.__getitem__)
        gaps.append(max(current) - current[chosen])
    assert abs(statistics.mean(gaps) - gap_formula) < 5 * statistics.stdev(gaps) / math.sqrt(len(gaps))
    # Exact pathwise scale equivariance for all feasible policies.
    base = make_cases()[3]
    scaled = dict(base, stationary_variances=[9.0] * 5)
    a = run_case(base, 250, 50, 1)[1]
    b = run_case(scaled, 250, 50, 1)[1]
    for first, second in zip(a, b):
        assert first["counts"] == second["counts"]
        assert math.isclose(3 * first["regret"], second["regret"], rel_tol=1e-12)
    print("Verified Gaussian prediction, oracle expectation, two-period value, two-arm PS regret, and policy scale equivariance.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--runs", type=int, default=40)
    parser.add_argument("--horizon", type=int, default=30000)
    parser.add_argument("--burn", type=int, default=5000)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    if args.runs < 2 or args.horizon < 1 or args.burn < 0 or args.workers < 1:
        parser.error("Need at least two runs, positive horizon/workers, and nonnegative burn.")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    metadata, rows, curves = [], [], []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        pending = {executor.submit(run_case, case, args.horizon, args.burn, args.runs): case["name"]
                   for case in make_cases()}
        for future in as_completed(pending):
            case, run_rows, run_curves = future.result()
            metadata.append(case)
            rows.extend(run_rows)
            curves.extend(run_curves)
            print(f"Finished {case['name']} ({time.monotonic() - started:.1f}s)", flush=True)
    metadata.sort(key=lambda case: case["name"])
    rows.sort(key=lambda row: (row["case"], row["run"], row["policy"]))
    curves.sort(key=lambda row: (row["case"], row["run"], row["policy"], row["t"]))
    write_csv(args.output / "runs.csv", rows)
    write_csv(args.output / "run_curves.csv", curves)
    summarize(args.output, rows, curves, metadata)
    (args.output / "metadata.json").write_text(json.dumps(
        {"runs": args.runs, "horizon": args.horizon, "burn": args.burn,
         "seed_rule": "7919*(run+1)+20261008; common states across policies",
         "known_parameters": True, "exact_observations": True,
         "stationary_initialization": True, "interval": "normal 95% across independent runs",
         "ps_reference": "https://proceedings.mlr.press/v206/liu23e.html",
         "cases": metadata, "elapsed_seconds": time.monotonic() - started}, indent=2) + "\n")
    print("Saved reproducible results to", args.output)


if __name__ == "__main__":
    main()
