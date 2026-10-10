"""Graph-correlated Gaussian AR(1) reward policies and exact bridge checks.

Standard library only. The experiment has known zero means/dynamics, one noisy
measurement per calendar round, and regret against the full latent-state oracle.
It does not test unknown-mean PCS, graph learning, or general-horizon optimality.

    python3 experiments/spatiotemporal_bandits.py --verify
    python3 experiments/spatiotemporal_bandits.py --runs 24 --horizon 1200
"""

import argparse
import csv
import json
import math
from pathlib import Path
import random
import statistics


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "spatiotemporal_bandits" / "results"
NORMAL = statistics.NormalDist()
POLICIES = ("joint_greedy", "joint_two_step", "independent_two_step",
            "wrong_graph_two_step", "joint_predictive", "tv_gp_ucb")


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def transpose(a):
    return list(map(list, zip(*a)))


def matmul(a, b):
    return [[dot(row, col) for col in zip(*b)] for row in a]


def solve(a, b):
    rows = [list(row)+[value] for row, value in zip(a, b)]
    for col in range(len(rows)):
        pivot = max(range(col, len(rows)), key=lambda i: abs(rows[i][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        if abs(divisor) < 1e-14:
            raise ValueError("Singular system")
        rows[col] = [x/divisor for x in rows[col]]
        for i in range(len(rows)):
            if i != col:
                factor = rows[i][col]
                rows[i] = [x-factor*y for x, y in zip(rows[i], rows[col])]
    return [row[-1] for row in rows]


def inverse(a):
    n = len(a)
    return transpose([solve(a, [float(i == j) for i in range(n)]) for j in range(n)])


def cholesky(a):
    result = [[0.0]*len(a) for _ in a]
    for i in range(len(a)):
        for j in range(i+1):
            value = a[i][j]-dot(result[i][:j], result[j][:j])
            if i == j:
                if value < -1e-10:
                    raise ValueError("Covariance is not positive semidefinite")
                result[i][j] = math.sqrt(max(value, 0.0))
            elif result[j][j] > 1e-14:
                result[i][j] = value/result[j][j]
            elif abs(value) > 1e-10:
                raise ValueError("Inconsistent singular covariance")
    return result


def gaussian_draw(covariance, rng, lower=None):
    lower = cholesky(covariance) if lower is None else lower
    z = [rng.gauss(0, 1) for _ in covariance]
    return [dot(row, z) for row in lower]


def density(z):
    return math.exp(-z*z/2)/math.sqrt(2*math.pi)


def expected_max_lines(intercepts, slopes):
    """Exact Gaussian integral of an upper envelope of affine functions."""
    unique = {}
    for intercept, slope in zip(intercepts, slopes):
        unique[slope] = max(intercept, unique.get(slope, -math.inf))
    hull = []  # slope, intercept, left endpoint
    for slope, intercept in sorted(unique.items()):
        start = -math.inf
        while hull:
            previous_slope, previous_intercept, previous_start = hull[-1]
            start = (previous_intercept-intercept)/(slope-previous_slope)
            if start > previous_start:
                break
            hull.pop()
        if not hull:
            start = -math.inf
        hull.append((slope, intercept, start))
    value = 0.0
    for i, (slope, intercept, left) in enumerate(hull):
        right = hull[i+1][2] if i+1 < len(hull) else math.inf
        value += intercept*(NORMAL.cdf(right)-NORMAL.cdf(left))
        value += slope*(density(left)-density(right))
    return value


def two_step_scores(means, covariance, phi, measurement_variance=0.0):
    next_means = [phi*m for m in means]
    return [means[a]+expected_max_lines(
        next_means, [phi*row[a]/math.sqrt(covariance[a][a]+measurement_variance)
                     for row in covariance]) for a in range(len(means))]


def condition(means, covariance, arm, observation, measurement_variance):
    denominator = covariance[arm][arm]+measurement_variance
    column = [row[arm] for row in covariance]
    innovation = observation-means[arm]
    return ([m+c*innovation/denominator for m, c in zip(means, column)],
            [[covariance[i][j]-column[i]*column[j]/denominator
              for j in range(len(means))] for i in range(len(means))])


def propagate(means, covariance, transition, process_covariance):
    predicted = [dot(row, means) for row in transition]
    p = matmul(matmul(transition, covariance), transpose(transition))
    return predicted, [[p[i][j]+process_covariance[i][j]
                        for j in range(len(means))] for i in range(len(means))]


def graph_covariance(size, strength):
    """Diagonal-normalized resolvent of an undirected path Laplacian."""
    precision = [[float(i == j) for j in range(size)] for i in range(size)]
    for i in range(size-1):
        precision[i][i] += strength
        precision[i+1][i+1] += strength
        precision[i][i+1] -= strength
        precision[i+1][i] -= strength
    raw = inverse(precision)
    return [[raw[i][j]/math.sqrt(raw[i][i]*raw[j][j])
             for j in range(size)] for i in range(size)]


def predictive_covariance(covariance, process_covariance, phi):
    future = [[phi*phi*covariance[i][j]+process_covariance[i][j]
               for j in range(len(covariance))] for i in range(len(covariance))]
    result = matmul(matmul(covariance, inverse(future)), covariance)
    return [[phi*phi*(result[i][j]+result[j][i])/2
             for j in range(len(covariance))] for i in range(len(covariance))]


def choose(policy, means, covariance, process_covariance, phi, noise, time, rng, remaining=2):
    if policy == "joint_greedy" or ("two_step" in policy and remaining == 1):
        values = means
    elif policy == "joint_predictive":
        score_covariance = predictive_covariance(covariance, process_covariance, phi)
        draw = gaussian_draw(score_covariance, rng)
        values = [m+d for m, d in zip(means, draw)]
    elif policy == "tv_gp_ucb":
        beta = 2*math.log(len(means)*math.pi**2*(time+1)**2/(3*0.05))
        values = [m+math.sqrt(beta*covariance[i][i]) for i, m in enumerate(means)]
    else:
        values = two_step_scores(means, covariance, phi, noise)
    highest = max(values)
    return rng.choice([i for i, value in enumerate(values) if abs(value-highest) < 1e-12])


def close(a, b, tolerance=1e-9):
    return abs(a-b) <= tolerance


def verify():
    rng = random.Random(9102026)
    checks = 0
    # Scalar integration identity, dominance, shared slope, and two-arm formula.
    for _ in range(80):
        means = [rng.gauss(0, 2) for _ in range(2)]
        slopes = [rng.gauss(0, 2) for _ in range(2)]
        d, s = abs(means[0]-means[1]), abs(slopes[0]-slopes[1])
        expected = max(means)+s*density(d/s)-d*NORMAL.cdf(-d/s)
        actual = expected_max_lines(means, slopes)
        assert close(actual, expected)
        assert close(actual, expected_max_lines(means, [s+9 for s in slopes]))
        checks += 2
    for size in range(2, 8):
        slopes = [rng.gauss(0, 1) for _ in range(size)]
        assert close(expected_max_lines([0.0]*size, slopes),
                     (max(slopes)-min(slopes))/math.sqrt(2*math.pi))
        assert close(expected_max_lines(list(range(size)), [3.0]*size), size-1)
        checks += 2
    # Independent numerical quadrature tests for multi-arm upper envelopes.
    for _ in range(16):
        means = [rng.gauss(0, 1) for _ in range(6)]
        slopes = [rng.gauss(0, 1) for _ in range(6)]
        intervals, step = 16000, 18/16000
        integral = step/3*sum((1 if k in (0, intervals) else 4 if k % 2 else 2)
            *density(-9+k*step)*max(m+s*(-9+k*step) for m, s in zip(means, slopes))
            for k in range(intervals+1))
        assert close(integral, expected_max_lines(means, slopes), 2e-6)
        checks += 1
    # Kalman filtering agrees with dense GP conditioning after each fixed history.
    for phi in (0.0, 0.3, 0.9, 0.99, -0.6):
        k = graph_covariance(4, 2.0)
        for noise in (0.0, 0.1):
            m, p = [0.0]*4, k
            actions = [0, 2, 1, 0, 3, 2]
            values = [rng.gauss(0, 1) for _ in actions]
            for t, arm in enumerate(actions):
                m, p = condition(m, p, arm, values[t], noise)
                m = [phi*x for x in m]
                p = [[phi**2*p[i][j]+(1-phi**2)*k[i][j]
                      for j in range(4)] for i in range(4)]
                xi = [[k[actions[r]][actions[s]]*phi**abs(r-s)
                       +noise*float(r == s) for s in range(t+1)] for r in range(t+1)]
                c = [[k[i][actions[r]]*phi**(t+1-r) for r in range(t+1)] for i in range(4)]
                weights = solve(xi, values[:t+1])
                for i in range(4):
                    assert close(m[i], dot(c[i], weights))
                    for j in range(4):
                        assert close(p[i][j], k[i][j]-dot(c[i], solve(xi, c[j])))
                        checks += 1
                    checks += 1
    # A mean prior plus a temporally correlated spatial residual needs one joint filter.
    size, phi, noise = 3, 0.8, 0.05
    kmu, kz = graph_covariance(size, 1.0), graph_covariance(size, 2.0)
    augmented = [[(kmu if i < size and j < size else kz if i >= size and j >= size
                   else [[0.0]*size for _ in range(size)])[i % size][j % size]
                  for j in range(2*size)] for i in range(2*size)]
    f = [[float(i == j)*(1 if i < size else phi) for j in range(2*size)]
         for i in range(2*size)]
    q = [[(1-phi**2)*kz[i-size][j-size] if i >= size and j >= size else 0.0
          for j in range(2*size)] for i in range(2*size)]
    means = [0.0]*(2*size)
    actions, values = [0, 2, 0, 1, 2], [0.4, -0.3, 1.2, 0.1, -0.1]
    for t, arm in enumerate(actions):
        h = [float(j in (arm, arm+size)) for j in range(2*size)]
        column = [dot(row, h) for row in augmented]
        d = dot(h, column)+noise
        innovation = values[t]-dot(h, means)
        means = [m+c*innovation/d for m, c in zip(means, column)]
        augmented = [[augmented[i][j]-column[i]*column[j]/d for j in range(2*size)]
                     for i in range(2*size)]
        means, augmented = propagate(means, augmented, f, q)
        xi = [[kmu[actions[r]][actions[s]]+kz[actions[r]][actions[s]]*phi**abs(r-s)
               +noise*float(r == s) for s in range(t+1)] for r in range(t+1)]
        c = [[kmu[i][actions[r]]+kz[i][actions[r]]*phi**(t+1-r)
              for r in range(t+1)] for i in range(size)]
        weights = solve(xi, values[:t+1])
        for i in range(size):
            assert close(means[i]+means[i+size], dot(c[i], weights))
            for j in range(size):
                projected = sum(augmented[a][b] for a in (i, i+size) for b in (j, j+size))
                assert close(projected, kmu[i][j]+kz[i][j]-dot(c[i], solve(xi, c[j])))
                checks += 1
            checks += 1
    # Two-arm joint coefficient, ranking information and common-mode cancellation.
    example = []
    for rho in (0.0, 0.5, 0.9, 0.99):
        phi, variance = 0.9, 1.0
        k = [[variance, rho*variance], [rho*variance, variance]]
        scores = two_step_scores([0.0, 0.0], k, phi)
        expected_reward = phi*math.sqrt(variance)*(1-rho)/math.sqrt(2*math.pi)
        assert all(close(value, expected_reward) for value in scores)
        reduction = phi**2*variance*(1-rho)**2
        prior_difference = 2*variance*(1-rho)
        pcs = 0.5+math.asin(math.sqrt(reduction/prior_difference))/math.pi
        residual = prior_difference-reduction
        intervals, step = 16000, 18/16000
        pcs_integral = step/3*sum((1 if j in (0, intervals) else 4 if j % 2 else 2)
            *density(-9+j*step)*NORMAL.cdf(abs(math.sqrt(reduction)*(-9+j*step))
                                          /math.sqrt(residual))
            for j in range(intervals+1))
        assert close(pcs, pcs_integral, 1e-9)
        oracle = math.sqrt(variance*(1-rho)/math.pi)
        example.append({"rho": rho, "two_period_optimal_reward": expected_reward,
                        "oracle_reward_per_round": oracle,
                        "two_period_optimal_regret": 2*oracle-expected_reward,
                        "one_sample_next_state_pcs": pcs,
                        "full_past_lower_coefficient": oracle*(1-phi)})
        checks += 3
    assert close(expected_max_lines([1, 0], [100, 100]), 1.0)
    k = graph_covariance(4, 2)
    q = [[0.19*x for x in row] for row in k]
    b = predictive_covariance(k, q, 0.9)
    for i in range(4):
        for j in range(4):
            assert close(b[i][j], 0.81*k[i][j])
            checks += 1
    # A certified joint-covariance perturbation bounds the true prediction MSE.
    for _ in range(40):
        raw = [[rng.gauss(0, 1) for _ in range(4)] for _ in range(4)]
        true = matmul(raw, transpose(raw))
        true = [[true[i][j]+float(i == j) for j in range(4)] for i in range(4)]
        direction = [rng.gauss(0, 1) for _ in range(4)]
        length = math.sqrt(dot(direction, direction))
        direction = [x/length for x in direction]
        u = [dot(row, direction) for row in cholesky(true)]
        eta = 0.3
        for signed_eta in (-eta, eta):
            fitted = [[true[i][j]+signed_eta*u[i]*u[j] for j in range(4)] for i in range(4)]
            fitted_y = [row[1:] for row in fitted[1:]]
            w = solve(fitted_y, fitted[0][1:])
            s_hat = fitted[0][0]-dot(w, fitted[0][1:])
            a = [1.0]+[-x for x in w]
            true_mse = sum(a[i]*true[i][j]*a[j] for i in range(4) for j in range(4))
            s_true = true[0][0]-dot(true[0][1:], solve([row[1:] for row in true[1:]], true[0][1:]))
            assert true_mse <= s_hat/(1-eta)+1e-9
            assert (1-eta)*s_true-1e-9 <= s_hat <= (1+eta)*s_true+1e-9
            checks += 2
    return {"checks": checks, "two_arm_spatial_temporal_example": example,
            "dense_gp_filter_agreement": True,
            "unknown_mean_augmented_filter_agreement": True,
            "multi_arm_envelope_quadrature_agreement": True,
            "two_arm_pcs_quadrature_agreement": True,
            "fixed_design_covariance_error_certificate": True,
            "common_mode_has_zero_ranking_value": True}


def simulate(runs, horizon, seed, size=6, noise=0.04):
    rows, paired = [], []
    for strength in (0.0, 2.0):
        covariance = graph_covariance(size, strength)
        lower = cholesky(covariance)
        permutation = [0, 2, 4, 1, 3, 5]
        wrong = [[covariance[permutation[i]][permutation[j]] for j in range(size)]
                 for i in range(size)]
        independent = [[float(i == j) for j in range(size)] for i in range(size)]
        for phi in (0.0, 0.9, 0.99):
            samples = {policy: [] for policy in POLICIES}
            for run in range(runs):
                rng = random.Random(seed+100000*int(strength)+10000*round(phi*100)+run)
                state = gaussian_draw(covariance, rng, lower)
                model_covariances = {policy: independent if policy == "independent_two_step"
                    else wrong if policy == "wrong_graph_two_step" else covariance for policy in POLICIES}
                beliefs = {policy: ([0.0]*size, model_covariances[policy]) for policy in POLICIES}
                # Common tie draws make identical covariance models agree exactly.
                policy_rngs = {policy: random.Random(seed+run*1009+
                    (1 if "two_step" in policy else index)*9176)
                    for index, policy in enumerate(POLICIES)}
                process = {policy: [[(1-phi**2)*x for x in row]
                                     for row in model_covariances[policy]] for policy in POLICIES}
                losses = {policy: 0.0 for policy in POLICIES}
                for time in range(horizon):
                    oracle = max(state)
                    measurement_noise = [rng.gauss(0, math.sqrt(noise)) for _ in range(size)]
                    for policy in POLICIES:
                        m, p = beliefs[policy]
                        a = choose(policy, m, p, process[policy], phi, noise, time,
                                   policy_rngs[policy], remaining=horizon-time)
                        losses[policy] += oracle-state[a]
                        m, p = condition(m, p, a, state[a]+measurement_noise[a], noise)
                        beliefs[policy] = ([phi*x for x in m],
                            [[phi**2*p[i][j]+process[policy][i][j] for j in range(size)]
                             for i in range(size)])
                    innovation = gaussian_draw(covariance, rng, lower)
                    state = [phi*x+math.sqrt(1-phi**2)*z for x, z in zip(state, innovation)]
                for policy in POLICIES:
                    samples[policy].append(losses[policy]/horizon)
                if strength == 0:
                    assert close(losses["joint_two_step"], losses["independent_two_step"], 1e-8)
                    assert close(losses["joint_two_step"], losses["wrong_graph_two_step"], 1e-8)
            for policy in POLICIES:
                values = samples[policy]
                rows.append({"graph_strength": strength, "phi": phi, "policy": policy,
                             "mean_regret_per_round": statistics.mean(values),
                             "standard_error": statistics.stdev(values)/math.sqrt(runs),
                             "runs": runs, "horizon": horizon})
            for comparator in ("joint_greedy", "independent_two_step", "wrong_graph_two_step", "joint_predictive", "tv_gp_ucb"):
                differences = [x-y for x, y in zip(samples[comparator], samples["joint_two_step"])]
                paired.append({"graph_strength": strength, "phi": phi,
                               "comparator_minus_joint_two_step": comparator,
                               "mean_paired_difference": statistics.mean(differences),
                               "standard_error": statistics.stdev(differences)/math.sqrt(runs)})
            print(f"strength={strength:g} phi={phi:g} completed {runs} paired runs", flush=True)
    return rows, paired, {"runs": runs, "horizon": horizon, "seed": seed, "arms": size,
                         "measurement_variance": noise, "known_means": [0]*size,
                         "stationary_marginal_variances": [1]*size,
                         "true_graph": "path", "normalization": "diagonal-normalized resolvent",
                         "terminal_action": "two-step policies maximize current predictive mean on the final round",
                         "wrong_graph_permutation": permutation,
                         "confidence_intervals": "normal approximation across independent runs; paired differences saved separately"}


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render_findings(rows, paired, metadata, checks):
    lines = ["# Spatial and temporal reward experiment", "",
             "Known zero means and known Gaussian AR(1) dynamics; six path locations, one noisy measurement per round.",
             f"{metadata['runs']} paired independent runs per configuration, horizon {metadata['horizon']}; measurement variance 0.04.",
             "All policies see the same underlying trajectory and potential measurement noises within each run.",
             "Numbers below are cumulative regret divided by the finite horizon, not a proved limiting coefficient.", "",
             "| Graph strength | Persistence | Policy | Regret/round | SE |",
             "|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['graph_strength']:g} | {row['phi']:g} | {row['policy']} | {row['mean_regret_per_round']:.4f} | {row['standard_error']:.4f} |")
    lines += ["", "## Paired comparisons", "", "Positive differences favor joint two-step.", "",
              "| Graph strength | Persistence | Comparator | Difference | Approx. 95% half-width |",
              "|---|---|---|---|---|"]
    for row in paired:
        lines.append(f"| {row['graph_strength']:g} | {row['phi']:g} | {row['comparator_minus_joint_two_step']} | {row['mean_paired_difference']:.4f} | {1.96*row['standard_error']:.4f} |")
    lines += ["", "## Limits", "",
              "The rolling two-step rule is exact only with two reward periods remaining; its last-round action maximizes the current predictive mean. Joint predictive sampling uses the latent next field; no performance theorem is transferred automatically from published Predictive Sampling.",
              "TV-GP-UCB uses the correct finite-domain Gaussian posterior and a specified confidence parameter delta=0.05; the bonus is not tuned. It is a baseline, not a claim to reproduce every convention in the original experiments.",
              "The independent and wrong-graph rules use misspecified covariance models. At graph strength zero their two-step predictions coincide exactly with the correct model.",
              "There is no mean learning, PCS experiment, AR(p) experiment, real traffic data, graph validation, hyperparameter learning, or general optimality benchmark in this experiment.",
              "Sampling reduces variance at every location but can mostly reveal a shared fluctuation rather than a ranking-relevant contrast.", "",
              f"The separate exact-calculation checks passed {checks['checks']} assertions; see checks.json and the derivations in ../README.md.", ""]
    (OUTPUT / "findings.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--runs", type=int, default=24)
    parser.add_argument("--horizon", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=9102026)
    args = parser.parse_args()
    checks = verify()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "checks.json").write_text(json.dumps(checks, indent=2)+"\n")
    if args.verify:
        print(json.dumps(checks, indent=2))
        return
    if args.render_only:
        def read_rows(path):
            with path.open(newline="") as handle:
                return [{key: value if "policy" in key or "comparator" in key
                         else float(value) for key, value in row.items()}
                        for row in csv.DictReader(handle)]
        render_findings(read_rows(OUTPUT / "summary.csv"), read_rows(OUTPUT / "paired.csv"),
                        json.loads((OUTPUT / "metadata.json").read_text()), checks)
        return
    if args.runs < 2 or args.horizon < 2:
        parser.error("runs and horizon must be at least two")
    rows, paired, metadata = simulate(args.runs, args.horizon, args.seed)
    write_csv(OUTPUT / "summary.csv", rows)
    write_csv(OUTPUT / "paired.csv", paired)
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    render_findings(rows, paired, metadata, checks)


if __name__ == "__main__":
    main()
