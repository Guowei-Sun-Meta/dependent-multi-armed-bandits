"""Exact Gaussian calculations and checks for multiple heterogeneous AR arms.

Uses only the Python standard library. Calendar-time schedules and separately
advanced simulation streams are deliberately kept distinct.

    python3 experiments/ar_p_extension.py --verify
    python3 experiments/ar_p_extension.py --runs 40000
"""

import argparse
import csv
from itertools import product
import json
import math
from pathlib import Path
import random
import statistics

from two_arm_ar1_allocation import information, positive_part, solve, two_step_scores


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "ar_p_bandits" / "results"
NORMAL = statistics.NormalDist()


def transpose(a):
    return list(map(list, zip(*a)))


def matmul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def matvec(a, x):
    return [sum(u*v for u, v in zip(row, x)) for row in a]


def add(a, b, scale=1.0):
    return [[x+scale*y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def power(a, exponent):
    result = [[float(i == j) for j in range(len(a))] for i in range(len(a))]
    while exponent:
        if exponent % 2:
            result = matmul(result, a)
        a = matmul(a, a)
        exponent //= 2
    return result


def cholesky(a):
    lower = [[0.0]*len(a) for _ in a]
    for i in range(len(a)):
        for j in range(i+1):
            value = a[i][j]-sum(lower[i][k]*lower[j][k] for k in range(j))
            lower[i][j] = math.sqrt(value) if i == j else value/lower[j][j]
    return lower


class ARModel:
    """Stable, known AR coefficients; stationary noise variance is normalized."""
    def __init__(self, coefficients, variance=1.0):
        self.coefficients = list(coefficients)
        self.order = len(coefficients)
        p = self.order
        self.transition = [list(coefficients)] + [
            [float(j == i-1) for j in range(p)] for i in range(1, p)]
        matrix, right = [], []
        for i in range(p):
            for j in range(p):
                matrix.append([float(i == r and j == s)
                               - self.transition[i][r]*self.transition[j][s]
                               for r in range(p) for s in range(p)])
                right.append(float(i == 0 and j == 0))
        unit = solve(matrix, right)
        self.q = variance/unit[0]
        self.stationary = [[unit[i*p+j]*self.q for j in range(p)] for i in range(p)]
        self.variance = self.stationary[0][0]
        self.noise = [[self.q*float(i == 0 and j == 0) for j in range(p)] for i in range(p)]
        self.longrun_variance = self.q/(1-sum(coefficients))**2
        self.initial_information = self.information(list(range(1, p+1)))
        self.offset = self.longrun_variance*self.initial_information-p

    def covariance(self, lag):
        return matmul(power(self.transition, abs(lag)), self.stationary)[0][0]

    def observation_covariance(self, times):
        return [[self.covariance(a-b) for b in times] for a in times]

    def information(self, times):
        return sum(solve(self.observation_covariance(times), [1.0]*len(times))) if times else 0.0

    def propagate_covariance(self, covariance, gap):
        f = power(self.transition, gap)
        return add(self.stationary, matmul(matmul(f, add(covariance, self.stationary, -1)), transpose(f)))

    def filter_information(self, times):
        covariance = self.stationary
        derivative = [0.0]*self.order
        info, previous = 0.0, None
        for time in times:
            if previous is not None:
                gap = time-previous
                covariance = self.propagate_covariance(covariance, gap)
                derivative = matvec(power(self.transition, gap), derivative)
            sensitivity = 1+derivative[0]
            variance = covariance[0][0]
            column = [row[0] for row in covariance]
            info += sensitivity**2/variance
            derivative = [d-c*sensitivity/variance for d, c in zip(derivative, column)]
            covariance = [[covariance[i][j]-column[i]*column[j]/variance
                           for j in range(self.order)] for i in range(self.order)]
            previous = time
        return info

    def terminal_variance(self, times, target):
        covariance, previous = self.stationary, None
        for time in times:
            if previous is not None:
                covariance = self.propagate_covariance(covariance, time-previous)
            column = [row[0] for row in covariance]
            variance = covariance[0][0]
            covariance = [[covariance[i][j]-column[i]*column[j]/variance
                           for j in range(self.order)] for i in range(self.order)]
            previous = time
        return self.variance if previous is None else self.propagate_covariance(covariance, target-previous)[0][0]

    def predictive_score_variance(self, covariance, future_length=None):
        length = self.order if future_length is None else future_length
        future_covariance = []
        rows = [power(self.transition, r)[0] for r in range(1, length+1)]
        coefficients = [power(self.transition, r)[0][0] for r in range(length)]
        cross = [sum(covariance[0][j]*row[j] for j in range(self.order)) for row in rows]
        for r in range(1, length+1):
            line = []
            for s in range(1, length+1):
                state_part = sum(rows[r-1][i]*covariance[i][j]*rows[s-1][j]
                                 for i in range(self.order) for j in range(self.order))
                noise_part = self.q*sum(coefficients[r-k]*coefficients[s-k]
                                        for k in range(1, min(r, s)+1))
                line.append(state_part+noise_part)
            future_covariance.append(line)
        return sum(a*b for a, b in zip(cross, solve(future_covariance, cross)))


def normal_expectation(function, points=160):
    """Composite Simpson integration; ±9 truncation has negligible normal mass."""
    assert points % 2 == 0
    step = 18/points
    return step/3 * sum((1 if j in (0, points) else 4 if j % 2 else 2)
                        * math.exp(-(-9+j*step)**2/2)/math.sqrt(2*math.pi)
                        * function(-9+j*step) for j in range(points+1))


def adaptive_normal_expectation(function, tolerance=2e-8):
    """Resolve kinks caused by maximizing posterior best probabilities."""
    def integrand(z):
        return math.exp(-z*z/2)/math.sqrt(2*math.pi)*function(z)
    def subdivide(left, right, fl, fm, fr, whole, tol, depth):
        midpoint = (left+right)/2
        quarter, three_quarters = (left+midpoint)/2, (midpoint+right)/2
        fq, ft = integrand(quarter), integrand(three_quarters)
        first = (midpoint-left)*(fl+4*fq+fm)/6
        second = (right-midpoint)*(fm+4*ft+fr)/6
        difference = first+second-whole
        if depth == 0 or abs(difference) <= 15*tol:
            return first+second+difference/15
        return (subdivide(left, midpoint, fl, fq, fm, first, tol/2, depth-1)
                +subdivide(midpoint, right, fm, ft, fr, second, tol/2, depth-1))
    result = 0.0
    for left in (-9, -6, -3, 0, 3, 6):
        right, midpoint = left+3, left+1.5
        fl, fm, fr = integrand(left), integrand(midpoint), integrand(right)
        whole = (right-left)*(fl+4*fm+fr)/6
        result += subdivide(left, right, fl, fm, fr, whole, tolerance/6, 22)
    return result


def two_period_scores(models, state_means, covariances, longrun_means):
    current = [mu+state[0] for mu, state in zip(longrun_means, state_means)]
    next_means = [mu+matvec(model.transition, state)[0]
                  for mu, model, state in zip(longrun_means, models, state_means)]
    scores = []
    for i, (model, covariance) in enumerate(zip(models, covariances)):
        cross = sum(model.transition[0][j]*covariance[j][0] for j in range(model.order))
        spread = abs(cross)/math.sqrt(covariance[0][0])
        competitor = max(next_means[j] for j in range(len(models)) if j != i)
        scores.append(current[i]+max(next_means[i], competitor)
                      +positive_part(-abs(next_means[i]-competitor), spread))
    return scores


def best_probabilities(means, variances, points=160):
    sd = [math.sqrt(v) for v in variances]
    return [normal_expectation(
        lambda z, i=i: math.prod(NORMAL.cdf((means[i]-means[j]+sd[i]*z)/sd[j])
                                 for j in range(len(means)) if j != i), points)
            for i in range(len(means))]


def final_sample_pcs(means, variances, arm, observation_variance=1.0, points=160):
    next_variances = list(variances)
    next_variances[arm] = variances[arm]*observation_variance/(variances[arm]+observation_variance)
    mean_sd = variances[arm]/math.sqrt(variances[arm]+observation_variance)
    def value(z):
        next_means = list(means)
        next_means[arm] += mean_sd*z
        return max(best_probabilities(next_means, next_variances, points))
    return adaptive_normal_expectation(value)


def exponent(gaps, longrun_variances, weights):
    return min(gap**2/(2*(longrun_variances[0]/weights[0]+longrun_variances[i]/weights[i]))
               for i, gap in enumerate(gaps, 1))


def best_exponent_weights(gaps, longrun_variances):
    lower, upper = 0.0, min(g*g for g in gaps)
    for _ in range(100):
        r = (lower+upper)/2
        derivative = -longrun_variances[0]/r**2 + sum(
            k/(gap*gap-r)**2 for gap, k in zip(gaps, longrun_variances[1:]))
        if derivative > 0:
            upper = r
        else:
            lower = r
    r = (lower+upper)/2
    unnormalized = [longrun_variances[0]/r] + [
        k/(gap*gap-r) for gap, k in zip(gaps, longrun_variances[1:])]
    total = sum(unnormalized)
    return [x/total for x in unnormalized]


def rested_variance_allocation(models, budget):
    counts = [model.order for model in models]
    if budget < sum(counts):
        raise ValueError("The affine-information regime requires at least each arm's AR order.")
    while sum(counts) < budget:
        improvements = [model.longrun_variance/((n+model.offset)*(n+1+model.offset))
                        for model, n in zip(models, counts)]
        counts[max(range(len(models)), key=lambda i: improvements[i])] += 1
    return counts


def verify():
    assert math.isclose(adaptive_normal_expectation(abs), math.sqrt(2/math.pi), abs_tol=1e-8)
    assert math.isclose(normal_expectation(lambda z: z*z), 1.0, abs_tol=1e-10)
    models = [ARModel(a) for a in ([0], [.7], [-.4], [.3, .6], [0, .8], [.3, -.4], [.4, .15, .1])]
    checks = 0
    for model in models:
        reconstructed = add(matmul(matmul(model.transition, model.stationary), transpose(model.transition)), model.noise)
        assert max(abs(a-b) for ar, br in zip(reconstructed, model.stationary) for a, b in zip(ar, br)) < 1e-10
        cholesky(model.stationary)
        for times in ([1], [1, 2, 3, 4], [2, 4, 9, 12], [1, 2, 6, 7, 11]):
            assert math.isclose(model.information(times), model.filter_information(times), rel_tol=1e-9)
            checks += 1
        for n in range(model.order, model.order+7):
            affine = (n+model.offset)/model.longrun_variance
            assert math.isclose(model.information(list(range(1, n+1))), affine, rel_tol=1e-9)
            checks += 1
        initial_score = model.predictive_score_variance(model.stationary)
        assert 0 <= initial_score < model.variance
        assert math.isclose(initial_score, model.predictive_score_variance(model.stationary, model.order+3), abs_tol=1e-9)
        observed = [[model.stationary[i][j]-model.stationary[i][0]*model.stationary[j][0]/model.variance
                     for j in range(model.order)] for i in range(model.order)]
        for horizon in range(1, model.order+3):
            cross = matmul(power(model.transition, horizon), model.stationary)[0][0]
            reduction = model.variance-model.propagate_covariance(observed, horizon)[0][0]
            assert math.isclose(reduction, cross*cross/model.variance, abs_tol=1e-9)
        for age in (1, 2, 5, 10):
            observed_times = list(range(1, model.order+1))
            reconstructed_variance = model.terminal_variance(observed_times, model.order+age)
            impulse_variance = model.q*sum(power(model.transition, r)[0][0]**2 for r in range(age))
            assert math.isclose(reconstructed_variance, impulse_variance, abs_tol=1e-9)
        checks += 1
    for arms, budgets in ((3, (3, 6, 9)), (4, (4, 8))):
        for phi in (.2, .8):
            for budget in budgets:
                per_arm = 1+(budget/arms-1)*(1-phi**arms)/(1+phi**arms)
                for tail in product(range(arms), repeat=budget-1):
                    schedule = (0,)+tail
                    information_values = [information([t for t, a in enumerate(schedule, 1) if a == i], phi)
                                          for i in range(arms)]
                    assert sum(information_values) <= arms*per_arm+1e-9
                    # Proper prior precision one includes never-observed arms.
                    assert sum(1/(1+x) for x in information_values) >= arms/(1+per_arm)-1e-9
                    checks += 1
    ar1 = ARModel([.7])
    assert math.isclose(ar1.predictive_score_variance(ar1.stationary), .7**2, abs_tol=1e-10)
    scores = two_period_scores([ARModel([.99])]*2, [[.05], [0]], [[[1-.99**2]], [[1]]], [0, 0])
    assert all(math.isclose(a, b, abs_tol=1e-10) for a, b in zip(scores, two_step_scores([.05, 0], [1-.99**2, 1], .99)))
    delayed = ARModel([0, .8])
    assert math.isclose(delayed.covariance(1), 0, abs_tol=1e-12)
    assert delayed.predictive_score_variance(delayed.stationary, 1) == 0
    assert math.isclose(delayed.predictive_score_variance(delayed.stationary), .8**2, abs_tol=1e-10)
    block_info = delayed.information([1, 2])
    cycle_info = delayed.information([1, 3])
    assert block_info > cycle_info
    good_variance = delayed.terminal_variance([1, 2], 5)+delayed.terminal_variance([3, 4], 5)
    bad_variance = delayed.terminal_variance([2, 4], 5)+delayed.terminal_variance([1, 3], 5)
    assert good_variance < bad_variance
    assert math.isclose(good_variance, 2-.8**2-.8**4, abs_tol=1e-10)
    probabilities = best_probabilities([.1, 0, -.2], [.04, .04, 4], points=640)
    assert probabilities[2] > probabilities[0]
    assert math.isclose(sum(probabilities), 1, abs_tol=1e-8)
    equal_gap_weights = best_exponent_weights([1, 1], [1, 1, 1])
    assert math.isclose(equal_gap_weights[0], 1/(1+math.sqrt(2)), abs_tol=1e-10)
    assert exponent([1, 1], [1, 1, 1], equal_gap_weights) > exponent([1, 1], [1, 1, 1], [1/3]*3)
    heterogeneous = [ARModel([.85]), ARModel([.3, .6]), ARModel([.4, .15, .1])]
    budget = 20
    counts = rested_variance_allocation(heterogeneous, budget)
    objective = lambda nn: sum(m.longrun_variance/(n+m.offset) for m, n in zip(heterogeneous, nn))
    for n1 in range(heterogeneous[0].order, budget):
        for n2 in range(heterogeneous[1].order, budget-n1):
            n3 = budget-n1-n2
            if n3 >= heterogeneous[2].order:
                assert objective(counts) <= objective((n1, n2, n3))+1e-9
    return {"matrix_filter_schedule_checks": checks,
            "ar2_information": {"consecutive_pair": block_info, "gap_two_pair": cycle_info},
            "ar2_terminal_difference_variances": {"AABB": good_variance, "BABA": bad_variance},
            "unequal_variance_best_probabilities": probabilities,
            "equal_gap_three_arm_weights": equal_gap_weights,
            "rested_variance_optimal_counts_budget_20": counts,
            "scope": "exact formulas and stated design criteria; no general PCS or regret optimality claim"}


def simulate_fixed_mean_pcs(runs):
    models = [ARModel([.85]), ARModel([.3, .6]), ARModel([.4, .15, .1])]
    means = [.35, 0, -.3]
    budget, arms = 12, len(models)
    times = [[t for t in range(1, budget+1) if (t-1) % arms == i] for i in range(arms)]
    weights, variances = [], []
    for model, tt in zip(models, times):
        precision_weights = solve(model.observation_covariance(tt), [1.0]*len(tt))
        info = sum(precision_weights)
        weights.append([x/info for x in precision_weights])
        variances.append(1/info)
    exact = best_probabilities(means, variances)[0]
    rng, correct = random.Random(9100926), 0
    roots = [cholesky(m.stationary) for m in models]
    for _ in range(runs):
        states = [matvec(root, [rng.gauss(0, 1) for _ in range(m.order)]) for m, root in zip(models, roots)]
        observations = [[] for _ in models]
        for t in range(1, budget+1):
            for i, model in enumerate(models):
                states[i] = matvec(model.transition, states[i])
                states[i][0] += math.sqrt(model.q)*rng.gauss(0, 1)
            arm = (t-1) % arms
            observations[arm].append(means[arm]+states[arm][0])
        estimates = [sum(w*x for w, x in zip(ww, yy)) for ww, yy in zip(weights, observations)]
        correct += int(max(range(arms), key=lambda i: estimates[i]) == 0)
    empirical = correct/runs
    return {"runs": runs, "budget": budget, "means": means, "AR_coefficients": [m.coefficients for m in models],
            "stationary_variances": [m.variance for m in models], "estimator_variances": variances,
            "exact_pcs": exact, "empirical_pcs": empirical,
            "ci95_halfwidth": 1.96*math.sqrt(empirical*(1-empirical)/runs)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--runs", type=int, default=40000)
    parser.add_argument("--render-only", action="store_true")
    args = parser.parse_args()
    checks = verify()
    if args.verify:
        print(json.dumps(checks, indent=2))
        return
    if args.runs < 2:
        parser.error("Use at least two replications.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    conditional = []
    for a in (0, 1, 2, 3, 5, 10):
        values = [final_sample_pcs([a, a, 0], [.5, .5, 1], arm) for arm in (0, 2)]
        conditional.append({"a": a, "resample_arm_1": values[0], "sample_arm_3": values[1]})
        print("Conditional PCS checked at", a, flush=True)
    simulation = (json.loads((OUTPUT / "checks.json").read_text())["simulation"]
                  if args.render_only else simulate_fixed_mean_pcs(args.runs))
    results = {"verification": checks, "conditional_pcs": conditional, "simulation": simulation,
               "date": "2026-10-09", "clock": "calendar time, except explicitly rested allocation results",
               "parameters_known": "AR coefficients and innovation variance; means unknown for mean selection",
               "numerical_integration": "Inner composite Simpson, [-9,9], 160 intervals; outer adaptive Simpson "
               "target tolerance 2e-8; unequal-variance example uses 640 intervals; not certified quadrature bounds"}
    (OUTPUT / "checks.json").write_text(json.dumps(results, indent=2)+"\n")
    table = [f"{r['a']:g} & {r['resample_arm_1']:.6f} & {r['sample_arm_3']:.6f} \\\\" for r in conditional]
    (OUTPUT / "conditional_table.tex").write_text("\n".join(table)+"\n")
    with (OUTPUT / "ar2_pcs.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["lag2", "mean_block", "mean_cycle", "state_block", "state_bad_cycle"])
        for n in range(100):
            a = .99*n/99
            writer.writerow([a, NORMAL.cdf(.5), NORMAL.cdf(.5/math.sqrt(1+a)),
                             .5+math.asin(a*math.sqrt((1+a*a)/2))/math.pi,
                             .5+math.asin(a/math.sqrt(2))/math.pi])
    findings = ["# Multiple-arm AR(p) extension checks", "", "9 October 2026.", "",
                f"{checks['matrix_filter_schedule_checks']:,} covariance, Kalman-information, affine-information, "
                "predictive-sampling, and exhaustive AR(1) schedule checks passed.", "",
                "## Three-arm adaptive PCS example", "",
                "Independent N(0,1) mean priors and iid observation variance one. "
                "After observing arms 1 and 2 once, posterior means are (a,a,0) and variances (1/2,1/2,1). "
                "One sample remains. Values integrate the Bayes-optimal terminal recommendation.", "",
                "| a | Resample arm 1 | Sample arm 3 |", "|---|---:|---:|"]
    findings.extend(f"| {r['a']} | {r['resample_arm_1']:.6f} | {r['sample_arm_3']:.6f} |" for r in conditional)
    findings.extend(["", "The proof uses the limiting values as a tends to infinity: "
                     "resampling approaches 1/2 + asin(sqrt(1/6))/pi, while sampling arm 3 approaches 1/2. "
                     "Continuity gives a positive-probability region of strict improvement. "
                     "The numerical table illustrates the proof; it is not a global optimal-policy claim.", "",
                     "## Heterogeneous AR(1), AR(2), AR(3) mean identification", "",
                     f"Budget {simulation['budget']}, {simulation['runs']:,} independent stationary replications, fixed round-robin schedule. "
                     f"Exact PCS integral: {simulation['exact_pcs']:.6f}. "
                     f"Simulated PCS: {simulation['empirical_pcs']:.6f} ± {simulation['ci95_halfwidth']:.6f} "
                     "(approximate 95% binomial interval). This checks schedule evaluation, not optimality of round-robin PCS.", "",
                     "The saved JSON contains coefficients, variances, counterexamples, and numerical conventions. "
                     "The derivations are in the research note and manuscript."])
    (OUTPUT / "findings.md").write_text("\n".join(findings)+"\n")
    print("Saved", OUTPUT)


if __name__ == "__main__":
    main()
