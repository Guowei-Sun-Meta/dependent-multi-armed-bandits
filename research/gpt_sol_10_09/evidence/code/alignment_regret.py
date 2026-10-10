"""Reproducible alignment experiments for the accompanying working manuscript.

Only Python's standard library is needed. These are controlled synthetic
experiments, including explicitly oracle-supplied graph energy certificates.
They do not learn a graph or certify its smoothness from bandit observations.

    python3 experiments/alignment_regret.py --verify
    python3 experiments/alignment_regret.py --runs 40 --horizon 20000
"""

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "research" / "alignment_paper" / "results"
SIGMA = 0.15


def clique_energy(means, members):
    """Each edge has weight 1/m, so nonzero Laplacian eigenvalues equal 1."""
    m = len(members)
    return sum((means[i] - means[j]) ** 2 for p, i in enumerate(members)
               for j in members[p + 1:]) / m


def oracle_certificates(means, groups):
    energies = [clique_energy(means, members) for members in groups]
    # For w=1/m, pairwise effective resistance is 2; singleton width is zero.
    widths = [min(1.0, math.sqrt(2.0 * energy)) if len(members) > 1 else 0.0
              for energy, members in zip(energies, groups)]
    return widths, energies


def make_instance():
    means = [0.8] + [0.65] * 8 + [0.5] * 8 + [0.35] * 8
    groups = [[0], list(range(1, 9)), list(range(9, 17)), list(range(17, 25))]
    return means, groups


def corrupt_partition(groups, swaps):
    """Exchange high/low suboptimal members; keep the optimal arm isolated."""
    result = [members[:] for members in groups]
    for j in range(swaps):
        result[1][j], result[3][j] = result[3][j], result[1][j]
    return result


def simulate(means, groups, widths, energies, policy, horizon, seed, checkpoints):
    k, c = len(means), len(groups)
    delta = 1.0 / horizon
    log_term = math.log(2.0 * (k + c) * horizon / delta)
    radii = [math.inf] + [SIGMA * math.sqrt(2.0 * log_term / n)
                          for n in range(1, horizon + 1)]
    counts, sums = [0] * k, [0.0] * k
    group_counts, group_sums, group_truth_sums = [0] * c, [0.0] * c, [0.0] * c
    owner = {i: q for q, members in enumerate(groups) for i in members}
    # Separate arm streams, reproducibly coupled across policies by pull number.
    rngs = [random.Random(seed * 1009 + i * 9176 + 43) for i in range(k)]
    raw_upper = [math.inf] * k
    group_upper = [math.inf] * c
    inner_best = [members[0] for members in groups]
    regret = 0.0
    trajectory = {}
    checkpoint_set = set(checkpoints)
    confidence_ok = True
    max_coverage_ratio = 0.0
    best_mean = max(means)
    # Graph regularized least squares, computed by a diagonal/rank-one inverse.
    eta, regularization = 0.01, 1000.0
    fitted, stds = [0.0] * k, [0.0] * k
    logdets = [0.0] * c
    logdet_prior = sum(math.log(eta) + (len(g) - 1) * math.log(eta + regularization)
                       for g in groups)
    norm_bound = math.sqrt(eta * k + regularization * sum(energies))

    def update_spectral(q):
        members = groups[q]
        m = len(members)
        a = regularization / m
        diagonal = [counts[i] + eta + regularization for i in members]
        inverse = [1.0 / value for value in diagonal]
        denominator = 1.0 - a * sum(inverse)
        correction = a / denominator
        projected = sum(sums[i] * v for i, v in zip(members, inverse))
        for i, v in zip(members, inverse):
            fitted[i] = sums[i] * v + correction * v * projected
            stds[i] = math.sqrt(v + correction * v * v)
        logdets[q] = sum(math.log(value) for value in diagonal) + math.log(denominator)

    if policy == "spectral_ucb":
        for q in range(c):
            update_spectral(q)

    for t in range(1, horizon + 1):
        if policy == "ucb":
            arm = max(range(k), key=raw_upper.__getitem__)
        elif policy == "pool":
            if t <= c:
                arm = groups[t - 1][0]
            else:
                q = max(range(c), key=group_upper.__getitem__)
                arm = inner_best[q]
        elif policy == "spectral_ucb":
            beta = SIGMA * math.sqrt(max(0.0, sum(logdets) - logdet_prior)
                                     + 2.0 * math.log(1.0 / delta)) + norm_bound
            arm = max(range(k), key=lambda i: fitted[i] + beta * stds[i])
        else:
            raise ValueError(policy)
        q = owner[arm]
        reward = means[arm] + rngs[arm].gauss(0.0, SIGMA)
        counts[arm] += 1
        sums[arm] += reward
        group_counts[q] += 1
        group_sums[q] += reward
        group_truth_sums[q] += means[arm]
        regret += best_mean - means[arm]
        raw_upper[arm] = sums[arm] / counts[arm] + radii[counts[arm]]
        raw_ratio = abs(sums[arm] / counts[arm] - means[arm]) / radii[counts[arm]]
        pool_ratio = abs((group_sums[q] - group_truth_sums[q]) / group_counts[q]) \
            / radii[group_counts[q]]
        max_coverage_ratio = max(max_coverage_ratio, raw_ratio, pool_ratio)
        confidence_ok = confidence_ok and max(raw_ratio, pool_ratio) <= 1.0
        if policy == "pool":
            inner_best[q] = max(groups[q], key=raw_upper.__getitem__)
            group_upper[q] = min(raw_upper[inner_best[q]],
                                 group_sums[q] / group_counts[q]
                                 + radii[group_counts[q]] + widths[q])
        elif policy == "spectral_ucb":
            update_spectral(q)
        if t in checkpoint_set:
            trajectory[t] = regret

    if policy == "pool" and confidence_ok:
        for i, count in enumerate(counts):
            gap = best_mean - means[i]
            if gap > 0.0:
                assert count <= 1.0 + 8.0 * SIGMA ** 2 * log_term / gap ** 2 + 1e-8
        for q, members in enumerate(groups):
            gap = best_mean - max(means[i] for i in members)
            if gap > widths[q]:
                bound = 1.0 + 8.0 * SIGMA ** 2 * log_term / (gap - widths[q]) ** 2
                assert group_counts[q] <= bound + 1e-8
    return {"regret": regret, "counts": counts, "confidence_ok": confidence_ok,
            "max_coverage_ratio": max_coverage_ratio, "trajectory": trajectory}


def verify():
    # Rank-preserving complete-graph smoothing leaves every comparison unchanged.
    rng = random.Random(7)
    for k in (2, 5, 12):
        values = [rng.uniform(-2.0, 2.0) for _ in range(k)]
        for strength in (0.01, 1.0, 100.0):
            factor = 1.0 / (1.0 + strength * k)
            average = statistics.mean(values)
            scores = [factor * value + (1.0 - factor) * average for value in values]
            for i in range(k):
                for j in range(k):
                    assert math.isclose(scores[i] - scores[j], factor * (values[i] - values[j]),
                                        rel_tol=1e-9, abs_tol=1e-12)
    # Closed-form least informative clique alternatives and nested complexity.
    for m in (2, 3, 8, 20):
        gap, weight = 0.2, 1.0 / m
        last = 0.0
        for step in range(21):
            a = step / 10.0
            s = a * gap * math.sqrt(weight * (m - 1))
            shift = max(0.0, gap - s / math.sqrt(weight * (m - 1)))
            movement = [gap] + [shift] * (m - 1)
            energy = weight * sum((movement[i] - movement[j]) ** 2
                                  for i in range(m) for j in range(i + 1, m))
            assert energy <= s ** 2 + 1e-12
            coefficient = 2.0 * SIGMA ** 2 * m * gap / (gap ** 2 + (m - 1) * shift ** 2)
            assert coefficient >= last - 1e-12
            last = coefficient
    means, groups = make_instance()
    for swaps in range(9):
        perturbed = corrupt_partition(groups, swaps)
        widths, energies = oracle_certificates(means, perturbed)
        for members, width in zip(perturbed, widths):
            actual = max(means[i] for i in members) - min(means[i] for i in members)
            assert actual <= width + 1e-12
        # Verify the policy's derived arm/cluster count bounds on covered paths.
        for seed in range(4):
            result = simulate(means, perturbed, widths, energies, "pool", 1000, seed, [1000])
            assert result["confidence_ok"]
    # Both endpoints of the explicit asymptotic lower-bound interpolation.
    assert math.isclose(2 * SIGMA ** 2 * 8 * 0.2 / (8 * 0.2 ** 2), 2 * SIGMA ** 2 / 0.2)
    print("Verified rank cancellation, clique alternatives, certificate coverage, and count bounds.")


def run_experiments(runs, horizon, output):
    output.mkdir(parents=True, exist_ok=True)
    means, groups = make_instance()
    checkpoints = sorted({horizon, *[n for n in (100, 250, 500, 1000, 2000, 5000, 10000)
                                    if n <= horizon]})
    conditions = []
    zero_widths, zero_energies = oracle_certificates(means, groups)
    conditions.append(("certificate", "ucb", groups, zero_widths, zero_energies, "ucb"))
    conditions.append(("certificate", "spectral_ucb", groups, zero_widths, zero_energies,
                       "spectral_ucb"))
    for epsilon in (0.0, 0.05, 0.1, 0.2, 0.4):
        widths = [0.0] + [epsilon] * 3
        # Energies represent a declared bound, not an empirical estimate.
        energies = [0.0] + [epsilon ** 2 / 2.0] * 3
        conditions.append(("certificate", "pool_eps_" + str(epsilon), groups,
                           widths, energies, "pool"))
    conditions.append(("graph_corruption", "ucb", groups, zero_widths, zero_energies, "ucb"))
    for swaps in (0, 1, 2, 4):
        perturbed = corrupt_partition(groups, swaps)
        widths, energies = oracle_certificates(means, perturbed)
        conditions.append(("graph_corruption", "pool_swaps_" + str(swaps), perturbed,
                           widths, energies, "pool"))
    rows, curves, summaries = [], {}, []
    start = time.monotonic()
    for experiment, label, partition, widths, energies, policy in conditions:
        values = []
        trajectories = {n: [] for n in checkpoints}
        for seed in range(runs):
            result = simulate(means, partition, widths, energies, policy, horizon, seed, checkpoints)
            values.append(result["regret"])
            for n, value in result["trajectory"].items():
                trajectories[n].append(value)
            rows.append({"experiment": experiment, "policy": label, "seed": seed,
                         "horizon": horizon, "regret": result["regret"],
                         "confidence_ok": result["confidence_ok"],
                         "max_coverage_ratio": result["max_coverage_ratio"],
                         "counts": json.dumps(result["counts"])})
        sd = statistics.stdev(values) if runs > 1 else 0.0
        summary = {"experiment": experiment, "policy": label, "runs": runs,
                   "horizon": horizon, "mean_regret": statistics.mean(values),
                   "sd_regret": sd, "se_regret": sd / math.sqrt(runs),
                   "ci95_halfwidth": 1.96 * sd / math.sqrt(runs)}
        summaries.append(summary)
        curves[(experiment, label)] = trajectories
        print(f"{experiment}: {label}: {summary['mean_regret']:.3f} +/- "
              f"{summary['ci95_halfwidth']:.3f}; elapsed {time.monotonic() - start:.1f}s", flush=True)
    for filename, records in (("runs.csv", rows), ("summary.csv", summaries)):
        with (output / filename).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
    for experiment in ("certificate", "graph_corruption"):
        labels = [label for ex, label, *_ in conditions if ex == experiment]
        with (output / (experiment + "_curves.csv")).open("w", newline="") as handle:
            columns = ["t"] + [label for label in labels] + [label + "_se" for label in labels]
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for n in checkpoints:
                row = {"t": n}
                for label in labels:
                    values = curves[(experiment, label)][n]
                    row[label] = statistics.mean(values)
                    row[label + "_se"] = (statistics.stdev(values) / math.sqrt(runs)
                                             if runs > 1 else 0.0)
                writer.writerow(row)
    with (output / "lower_bound_curve.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["alignment_ratio", "gain_m2", "gain_m8", "gain_m32"])
        for step in range(151):
            a = step / 100.0
            writer.writerow([a] + [1.0 + (m - 1) * max(0.0, 1.0 - a) ** 2
                                    for m in (2, 8, 32)])
    with (output / "results_table.tex").open("w") as handle:
        for row in summaries:
            label = row["policy"].replace("_", r"\_")
            experiment = "Certificate" if row["experiment"] == "certificate" else "Perturbed graph"
            handle.write(f"{experiment} & {label} & {row['mean_regret']:.2f} & "
                         f"{row['ci95_halfwidth']:.2f} \\\\\n")
    metadata = {"runs": runs, "horizon": horizon, "sigma": SIGMA, "means": means,
                "base_groups": groups, "checkpoints": checkpoints,
                "elapsed_seconds": time.monotonic() - start,
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "confidence_delta": "1/T", "noise": "independent Gaussian N(0,sigma^2)",
                "seeds": list(range(runs)), "coupling": "per-arm noise streams by pull number",
                "certificates": "supplied oracle bounds; no online graph learning",
                "spectral_ucb": {"eta": 0.01, "lambda": 1000.0,
                                 "energy_certificate": "0 (exact aligned graph)"},
                "conditions": [{"experiment": ex, "label": label, "groups": g,
                                "width_certificates": widths, "energy_certificates": energies}
                               for ex, label, g, widths, energies, _ in conditions]}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Wrote reproducible results to {output}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--runs", type=int, default=40)
    parser.add_argument("--horizon", type=int, default=20000)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.runs < 2 or args.horizon < 25:
        parser.error("Use at least two replications and a horizon of at least 25.")
    if args.verify:
        verify()
    else:
        run_experiments(args.runs, args.horizon, args.output)


if __name__ == "__main__":
    main()
