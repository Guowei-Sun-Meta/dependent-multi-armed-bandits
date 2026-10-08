"""Graph-geometry theory checks and cumulative-regret experiments (stdlib only).

The main experiment supplies a fixed energy bound S=0.2; it does not learn it.
Path and clique weights are normalized to the same resistance diameter, 2.
The width-profile comparator is a Gaussian analogue, not the Bernoulli Clus-UCB
implementation. Independent per-arm reward streams couple policies by pull count.
"""

import argparse
import bisect
import csv
import hashlib
import heapq
import json
import math
import random
import statistics
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "alignment_paper" / "results" / "geometry"


def solve(matrix, vector):
    n = len(vector)
    rows = [list(row) + [value] for row, value in zip(matrix, vector)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(rows[i][j]))
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        if abs(divisor) < 1e-18:
            raise ValueError("Singular system")
        rows[j] = [value / divisor for value in rows[j]]
        for i in range(n):
            if i != j:
                multiplier = rows[i][j]
                rows[i] = [a - multiplier * b for a, b in zip(rows[i], rows[j])]
    return [row[-1] for row in rows]


def quadratic(matrix, vector):
    return sum(x * sum(a * y for a, y in zip(row, vector))
               for x, row in zip(vector, matrix))


def laplacian(m, edges):
    result = [[0.0] * m for _ in range(m)]
    for i, j, weight in edges:
        result[i][i] += weight
        result[j][j] += weight
        result[i][j] -= weight
        result[j][i] -= weight
    return result


def resistance_matrix(lap):
    m = len(lap)
    grounded = [[lap[i][j] + 1.0 / m for j in range(m)] for i in range(m)]
    columns = [solve(grounded, [float(i == j) for i in range(m)]) for j in range(m)]
    inverse = [[columns[j][i] - 1.0 / m for j in range(m)] for i in range(m)]
    return [[max(0.0, inverse[i][i] + inverse[j][j] - 2 * inverse[i][j])
             for j in range(m)] for i in range(m)]


def radius_squared(resistance, p):
    products = [sum(a * b for a, b in zip(row, p)) for row in resistance]
    variance = sum(a * b for a, b in zip(p, products)) / 2.0
    return max(products) - variance, variance


def resistance_design(resistance, tolerance=1e-8, iterations=30000):
    """Frank-Wolfe for max graph variance; returns rigorous primal/dual gap."""
    m = len(resistance)
    p = [1.0 / m] * m
    products = [sum(row) / m for row in resistance]
    for iteration in range(iterations):
        average = sum(a * b for a, b in zip(p, products))
        vertex = max(range(m), key=products.__getitem__)
        gap = products[vertex] - average
        if gap <= tolerance:
            break
        step = min(1.0, gap / (2 * products[vertex] - average))
        p = [(1 - step) * value for value in p]
        p[vertex] += step
        products = [(1 - step) * value + step * resistance[i][vertex]
                    for i, value in enumerate(products)]
    upper, lower = radius_squared(resistance, p)
    return {"p": p, "rho_squared_lower": lower, "rho_squared_upper": upper,
            "gap": upper - lower, "iterations": iteration + 1}


def inner_information(lap, p, s, vertex):
    """Solve the least-informative boundary alternative by multiplier bisection."""
    m = len(p)
    if s == 0:
        return 1.0, [1.0] * m
    if lap[vertex][vertex] <= s * s:
        z = [float(i == vertex) for i in range(m)]
        return p[vertex], z
    others = [i for i in range(m) if i != vertex]

    def candidate(multiplier):
        matrix = [[multiplier * lap[i][j] + (p[i] if i == j else 0.0)
                   for j in others] for i in others]
        values = solve(matrix, [-multiplier * lap[i][vertex] for i in others])
        z = [0.0] * m
        z[vertex] = 1.0
        for i, value in zip(others, values):
            z[i] = value
        return z

    lower, upper = 0.0, 1.0
    while quadratic(lap, candidate(upper)) > s * s:
        upper *= 2.0
    for _ in range(55):
        middle = (lower + upper) / 2.0
        if quadratic(lap, candidate(middle)) > s * s:
            lower = middle
        else:
            upper = middle
    z = candidate(upper)
    return sum(a * b * b for a, b in zip(p, z)), z


def graph_spec(kind, m):
    if kind == "path":
        p = [0.5] + [0.0] * (m - 2) + [0.5]
        rho = math.sqrt(0.5)
    elif kind == "clique":
        p = [1.0 / m] * m
        rho = math.sqrt((m - 1) / m)
    else:
        raise ValueError(kind)
    return p, rho


def profile_root(locations, ns, ys, yys, empirical, count, width, budget, raw_upper):
    """Exact piecewise-quadratic root using sorted hinge breakpoints."""
    if raw_upper <= locations[0]:
        return raw_upper

    def cost(value):
        n = bisect.bisect_right(locations, value)
        result = ns[n] * value * value - 2 * ys[n] * value + yys[n]
        return result + count * (max(0.0, value - empirical) ** 2
                                  - max(0.0, value - empirical - width) ** 2)

    own_active = cost(empirical) <= budget
    left, right = 0, bisect.bisect_right(locations, raw_upper)
    while left < right:
        middle = (left + right) // 2
        if cost(locations[middle]) <= budget:
            left = middle + 1
        else:
            right = middle
    a, b, c = ns[left], ys[left], yys[left]
    if left and empirical + width <= locations[left - 1]:
        a -= count
        b -= count * (empirical + width)
        c -= count * (empirical + width) ** 2
    if own_active:
        a += count
        b += count * empirical
        c += count * empirical ** 2
    root = (b + math.sqrt(max(0.0, b * b - a * (c - budget)))) / a
    return min(root, raw_upper)


def simulate(kind, m, policy, horizon, seed, sigma=0.05, means=None, certificate=0.2):
    means = means or [0.8] + [0.6] * m
    k = len(means)
    groups = [[0], list(range(1, k))]
    p, rho = graph_spec(kind, m)
    designs = [{0: 1.0}, {i + 1: weight for i, weight in enumerate(p) if weight > 0}]
    design_bias = [0.0, certificate * rho]
    widths = [0.0, min(1.0, certificate * math.sqrt(2.0))]
    delta = 1.0 / horizon
    ell = math.log(2.0 * (k + 2) * horizon / delta)
    radius = [math.inf] + [sigma * math.sqrt(2 * ell / n) for n in range(1, horizon + 1)]
    counts, sums = [0] * k, [0.0] * k
    streams = [random.Random(seed * 1009 + i * 9176 + 43) for i in range(k)]
    raw = [math.inf] * k
    heap = [(-math.inf, i, 0) for i in range(k)]
    inner = [[(-math.inf, i, 0) for i in members] for members in groups]
    for entries in [heap, *inner]:
        heapq.heapify(entries)
    group_counts, group_sums = [0, 0], [0.0, 0.0]
    group_versions = [0, 0]
    profile_cache = {}
    regret, t = 0.0, 0
    trajectory = {}
    checkpoints = {horizon, *[n for n in (100, 250, 500, 1000, 2000, 5000, 10000)
                             if n <= horizon]}
    coverage, max_ratio = True, 0.0
    pilot_counts = [0] * k
    eliminated = []
    survivors = list(range(k))
    best = max(means)

    def peek(entries):
        while entries and entries[0][2] != counts[entries[0][1]]:
            heapq.heappop(entries)
        return entries[0][1] if entries else None

    def pull(arm, pilot=False):
        nonlocal t, regret, coverage, max_ratio
        reward = means[arm] + streams[arm].gauss(0.0, sigma)
        counts[arm] += 1
        sums[arm] += reward
        if pilot:
            pilot_counts[arm] += 1
        t += 1
        regret += best - means[arm]
        raw[arm] = sums[arm] / counts[arm] + radius[counts[arm]]
        entry = (-raw[arm], arm, counts[arm])
        heapq.heappush(heap, entry)
        q = int(arm > 0)
        heapq.heappush(inner[q], entry)
        group_counts[q] += 1
        group_sums[q] += reward
        group_versions[q] += 1
        ratio = abs(sums[arm] / counts[arm] - means[arm]) / radius[counts[arm]]
        max_ratio = max(max_ratio, ratio)
        coverage = coverage and ratio <= 1.0
        if t in checkpoints:
            trajectory[t] = regret

    if policy == "design":
        largest = max(design_bias)
        if largest == 0:
            # Under a valid zero-energy certificate each component is constant.
            survivors = [members[0] for members in groups]
            heap = [(-raw[i], i, counts[i]) for i in survivors]
            heapq.heapify(heap)
        else:
            cap = min(horizon, 1 + math.ceil(512 * sigma * sigma * ell / largest ** 2))
            active, target = [0, 1], 1
            while t < horizon:
                targets = {i: math.ceil(target * weight)
                           for q in active for i, weight in designs[q].items()}
                needed = sum(max(0, n - counts[i]) for i, n in targets.items())
                if needed > horizon - t:
                    break
                for i, n in targets.items():
                    while counts[i] < n:
                        pull(i, pilot=True)
                bounds = {}
                for q in active:
                    estimate = sum(weight * sums[i] / counts[i]
                                   for i, weight in designs[q].items())
                    truth = sum(weight * means[i] for i, weight in designs[q].items())
                    width = sigma * math.sqrt(2 * ell * sum(weight ** 2 / counts[i]
                                                           for i, weight in designs[q].items()))
                    ratio = abs(estimate - truth) / width
                    coverage = coverage and ratio <= 1.0
                    max_ratio = max(max_ratio, ratio)
                    bounds[q] = (estimate - width, estimate + width + design_bias[q])
                lower = max(pair[0] for pair in bounds.values())
                remaining = [q for q in active if bounds[q][1] >= lower]
                eliminated.extend(q for q in active if q not in remaining)
                active = remaining
                if len(active) == 1 or target == cap:
                    break
                target = min(2 * target, cap)
            survivors = [i for q in active for i in groups[q]]
            if len(active) == 1 and design_bias[active[0]] == 0:
                survivors = [groups[active[0]][0]]
            heap = [(-raw[i], i, counts[i]) for i in survivors]
            heapq.heapify(heap)

    def profile_index(arm):
        q = int(arm > 0)
        if q == 0:
            return raw[arm]
        cache = profile_cache.get(q)
        if cache is None or cache[0] != group_versions[q]:
            thresholds = sorted((sums[i] / counts[i] + widths[q], counts[i])
                                for i in groups[q])
            locations = [value for value, _ in thresholds]
            ns, ys, yys = [0.0], [0.0], [0.0]
            for value, n in thresholds:
                ns.append(ns[-1] + n)
                ys.append(ys[-1] + n * value)
                yys.append(yys[-1] + n * value * value)
            cache = (group_versions[q], locations, ns, ys, yys)
            profile_cache[q] = cache
        _, locations, ns, ys, yys = cache
        empirical = sums[arm] / counts[arm]
        budget = 2 * sigma * sigma * ell
        return profile_root(locations, ns, ys, yys, empirical, counts[arm],
                            widths[q], budget, raw[arm])

    while t < horizon:
        if policy == "width_pool":
            if t < 2:
                arm = groups[t][0]
            else:
                inners = [peek(entries) for entries in inner]
                uppers = [min(raw[i], group_sums[q] / group_counts[q]
                              + radius[group_counts[q]] + widths[q])
                          for q, i in enumerate(inners)]
                arm = inners[max(range(2), key=uppers.__getitem__)]
        elif policy == "width_profile" and t < k:
            arm = t
        elif policy == "width_profile":
            candidates = []
            chosen, score = None, -math.inf
            while heap:
                candidate = peek(heap)
                if candidate is None:
                    break
                if chosen is not None and raw[candidate] <= score:
                    break
                candidates.append(heapq.heappop(heap))
                value = profile_index(candidate)
                if value > score:
                    chosen, score = candidate, value
            for entry in candidates:
                heapq.heappush(heap, entry)
            arm = chosen
        elif policy in ("ucb", "design"):
            arm = peek(heap)
        else:
            raise ValueError(policy)
        pull(arm)
    return {"regret": regret, "counts": counts, "pilot_counts": pilot_counts,
            "eliminated": eliminated, "survivors": survivors, "coverage": coverage,
            "max_coverage_ratio": max_ratio, "trajectory": trajectory}


def verify():
    rng = random.Random(41)
    # Compare the fast comparator oracle with an independent direct bisection.
    for m in (2, 5, 20):
        for _ in range(50):
            estimates = [rng.uniform(-0.2, 1.2) for _ in range(m)]
            counts = [rng.randrange(1, 100) for _ in range(m)]
            width, budget = rng.random(), 0.45
            arm = rng.randrange(m)
            ordered = sorted((value + width, n) for value, n in zip(estimates, counts))
            locations = [value for value, _ in ordered]
            ns, ys, yys = [0.0], [0.0], [0.0]
            for value, n in ordered:
                ns.append(ns[-1] + n)
                ys.append(ys[-1] + n * value)
                yys.append(yys[-1] + n * value * value)
            raw = estimates[arm] + math.sqrt(budget / counts[arm])
            fast = profile_root(locations, ns, ys, yys, estimates[arm], counts[arm],
                                width, budget, raw)
            low, high = min(estimates[arm], locations[0]), raw
            for _ in range(60):
                value = (low + high) / 2
                cost = sum(n * max(0.0, value - estimate - (0 if i == arm else width)) ** 2
                           for i, (estimate, n) in enumerate(zip(estimates, counts)))
                if cost > budget:
                    high = value
                else:
                    low = value
            assert math.isclose(fast, (low + high) / 2, abs_tol=1e-10)
    for m in (3, 5, 8):
        for kind in ("path", "clique"):
            edges = ([(i, i + 1, (m - 1) / 2) for i in range(m - 1)] if kind == "path"
                     else [(i, j, 1 / m) for i in range(m) for j in range(i + 1, m)])
            lap = laplacian(m, edges)
            resistance = resistance_matrix(lap)
            p, rho = graph_spec(kind, m)
            upper, lower = radius_squared(resistance, p)
            assert math.isclose(max(map(max, resistance)), 2.0, abs_tol=1e-10)
            assert math.isclose(upper, rho ** 2, abs_tol=1e-10)
            assert math.isclose(lower, rho ** 2, abs_tol=1e-10)
            numerical = resistance_design(resistance, iterations=3000)
            assert numerical["rho_squared_lower"] <= rho ** 2 + 1e-9
            assert numerical["rho_squared_upper"] >= rho ** 2 - 1e-9
            for s in (0.005, 0.05, 0.4, 1.0):
                values = [inner_information(lap, p, s, i) for i in range(m)]
                f = min(value for value, _ in values)
                assert f >= max(0, 1 - s * rho) ** 2 - 1e-9
                if s * math.sqrt(2) <= 1:
                    assert 1 - 2 * s * rho - 1e-9 <= f <= 1 - 2 * s * rho + 2 * s * s + 1e-9
                if kind == "clique":
                    expected = (1 + (m - 1) * max(0, 1 - s / math.sqrt((m - 1) / m)) ** 2) / m
                    assert math.isclose(f, expected, abs_tol=1e-9)
                for _, z in values:
                    assert quadratic(lap, z) <= s * s + 1e-8
            for _ in range(20):
                mu = [rng.random() for _ in range(m)]
                bound = math.sqrt(quadratic(lap, mu)) * rho
                average = sum(a * b for a, b in zip(p, mu))
                assert max(abs(value - average) for value in mu) <= bound + 1e-9
    # General non-symmetric weighted geometry and first-order bounds.
    lap = laplacian(5, [(0, 1, 1.3), (1, 2, 0.4), (2, 3, 2.0),
                        (3, 4, 0.7), (0, 4, 0.9), (1, 4, 0.2)])
    resistance = resistance_matrix(lap)
    design = resistance_design(resistance)
    p = design["p"]
    rho = math.sqrt(design["rho_squared_upper"])
    diameter = max(map(max, resistance))
    for s in (0.01, 0.05, 0.2):
        f = min(inner_information(lap, p, s, i)[0] for i in range(5))
        assert 1 - 2 * s * rho - 1e-8 <= f <= 1 - 2 * s * rho + s * s * diameter + 1e-8
    # Small topology comparison and fallback with a heterogeneous optimal component.
    for kind in ("path", "clique"):
        for policy in ("ucb", "width_pool", "width_profile", "design"):
            result = simulate(kind, 8, policy, 3000, 5)
            assert sum(result["counts"]) == 3000
            assert result["coverage"]
        means = [0.8, 0.9] + [0.6] * 7
        energy = quadratic(laplacian(8, ([(i, i + 1, 3.5) for i in range(7)]
                                         if kind == "path" else
                                         [(i, j, 0.125) for i in range(8) for j in range(i + 1, 8)])), means[1:])
        result = simulate(kind, 8, "design", 3000, 5, means=means,
                          certificate=math.sqrt(energy))
        assert 1 in result["survivors"] and result["coverage"]
    # Large-profile searches can temporarily remove every current heap entry.
    for seed in range(6):
        result = simulate("path", 256, "width_profile", 3000, seed)
        assert sum(result["counts"]) == 3000 and result["coverage"]
    print("Verified resistance geometry, design dual gaps, graph-information alternatives, "
          "first-order bounds, confidence coverage, and heterogeneous fallback.")


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(runs, horizon, sizes, output):
    output.mkdir(parents=True, exist_ok=True)
    rows, summaries, curves, shared = [], [], [], {}
    started = time.monotonic()
    for m in sizes:
        for kind in ("path", "clique"):
            for policy in ("ucb", "width_pool", "width_profile", "design"):
                # Width-only policies have identical inputs on both normalized graphs.
                if policy != "design" and (m, policy) in shared:
                    results = shared[m, policy]
                else:
                    results = [simulate(kind, m, policy, horizon, seed) for seed in range(runs)]
                    if policy != "design":
                        shared[m, policy] = results
                values = [r["regret"] for r in results]
                se = statistics.stdev(values) / math.sqrt(runs) if runs > 1 else 0.0
                summary = {"graph": kind, "m": m, "policy": policy, "runs": runs,
                           "horizon": horizon, "mean_regret": statistics.mean(values),
                           "se_regret": se, "ci95_halfwidth": 1.96 * se,
                           "mean_sampled_suboptimal_arms": statistics.mean(
                               sum(n > 0 for n in r["counts"][1:]) for r in results),
                           "elimination_rate": statistics.mean(1 in r["eliminated"] for r in results)}
                summaries.append(summary)
                print(json.dumps(summary), flush=True)
                for seed, result in enumerate(results):
                    rows.append({"graph": kind, "m": m, "policy": policy, "seed": seed,
                                 "horizon": horizon, "regret": result["regret"],
                                 "coverage": result["coverage"],
                                 "max_coverage_ratio": result["max_coverage_ratio"],
                                 "counts": json.dumps(result["counts"]),
                                 "pilot_counts": json.dumps(result["pilot_counts"]),
                                 "eliminated": json.dumps(result["eliminated"])})
                for t in sorted(results[0]["trajectory"]):
                    vals = [r["trajectory"][t] for r in results]
                    curves.append({"graph": kind, "m": m, "policy": policy, "t": t,
                                   "mean_regret": statistics.mean(vals),
                                   "se_regret": statistics.stdev(vals) / math.sqrt(runs) if runs > 1 else 0})
    write_csv(output / "runs.csv", rows)
    write_csv(output / "summary.csv", summaries)
    write_csv(output / "curves.csv", curves)
    # Wide plot data keep PGFPlots free of any statistical computation.
    for kind in ("path", "clique"):
        wide = []
        for m in sizes:
            entry = {"m": m}
            for summary in summaries:
                if summary["graph"] == kind and summary["m"] == m:
                    entry[summary["policy"]] = summary["mean_regret"]
                    entry[summary["policy"] + "_ci"] = summary["ci95_halfwidth"]
            wide.append(entry)
        write_csv(output / (kind + "_scaling.csv"), wide)
    information = []
    for step in range(131):
        s, m = step / 100, max(sizes)
        information.append({"s": s,
                            "clique_constant_ratio": m / (1 + (m - 1) * max(0, 1 - s / math.sqrt((m - 1) / m)) ** 2),
                            "path_constant_upper": min(m, 1 / (1 - s / math.sqrt(2)) ** 2),
                            "classical_ratio": m})
    write_csv(output / "information.csv", information)
    stress = []
    m = 8
    means = [0.8, 0.4, 0.4, 0.4, 0.9, 0.4, 0.4, 0.4, 0.4]
    lap = laplacian(m, [(i, i + 1, (m - 1) / 2) for i in range(m - 1)])
    true_s = math.sqrt(quadratic(lap, means[1:]))
    for current_horizon in (horizon // 2, horizon):
        for label, certificate in (("valid", true_s), ("invalid_zero", 0.0)):
            values = [simulate("path", m, "design", current_horizon, seed,
                               means=means, certificate=certificate)["regret"] for seed in range(runs)]
            se = statistics.stdev(values) / math.sqrt(runs) if runs > 1 else 0
            stress.append({"condition": label, "horizon": current_horizon,
                           "supplied_S": certificate, "true_S": true_s,
                           "mean_regret": statistics.mean(values), "se_regret": se,
                           "regret_per_round": statistics.mean(values) / current_horizon})
    write_csv(output / "certificate_stress.csv", stress)
    metadata = {"runs": runs, "horizon": horizon, "sizes": sizes, "sigma": 0.05,
                "best_mean": 0.8, "suboptimal_mean": 0.6, "supplied_S": 0.2,
                "resistance_diameter": 2.0, "path_edge_weight": "(m-1)/2",
                "clique_edge_weight": "1/m", "delta": "1/T",
                "ell": "log(2*(K+M)*T/delta)", "pilot_cap_constant": 512,
                "width_profile": "Gaussian one-sided KL analogue; not published Bernoulli Clus-UCB",
                "coupling": "independent per-arm streams, shared by arm and pull count across policies",
                "seed_formula": "seed*1009 + arm*9176 + 43", "seeds": list(range(runs)),
                "seconds": time.monotonic() - started,
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print("Saved results to", output, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--runs", type=int, default=40)
    parser.add_argument("--horizon", type=int, default=20000)
    parser.add_argument("--sizes", type=int, nargs="+", default=[16, 64, 256])
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    if arguments.verify:
        verify()
    else:
        if arguments.runs < 1 or arguments.horizon < 2 or min(arguments.sizes) < 2:
            parser.error("Require runs >= 1, horizon >= 2, and sizes >= 2")
        run(arguments.runs, arguments.horizon, arguments.sizes, arguments.output)
