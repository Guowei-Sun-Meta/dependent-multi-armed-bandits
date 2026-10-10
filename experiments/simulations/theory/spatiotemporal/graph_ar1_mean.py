"""Persistent graph means under graph-correlated AR(1) observation noise.

Only Python's standard library is required. Implements online innovation
regression, graph Bayesian/ridge estimates, mean knowledge gradient, and exact
two-arm design checks. Reports PCS for the largest posterior mean, not the
multi-arm Bayes-PCS recommendation.

    python3 experiments/simulations/theory/spatiotemporal/graph_ar1_mean.py --verify
    python3 experiments/simulations/theory/spatiotemporal/graph_ar1_mean.py --runs 200 --budget 48
"""

import argparse
import csv
from itertools import product
import json
import math
from pathlib import Path
import random
import statistics

from spatiotemporal_bandits import (cholesky, dot, expected_max_lines,
    gaussian_draw, graph_covariance, inverse, solve)

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "research" / "spatiotemporal_bandits" / "results" / "mean_selection"
POLICIES = ("graph_ar_kg", "unstructured_ar_kg", "diagonal_mean_ar_kg", "graph_iid_kg",
            "wrong_mean_graph_ar_kg", "graph_ar_contrast", "round_robin")


def identity(n):
    return [[float(i == j) for j in range(n)] for i in range(n)]


def laplacian(n):
    result = [[0.0]*n for _ in range(n)]
    for i in range(n-1):
        result[i][i] += 1
        result[i+1][i+1] += 1
        result[i][i+1] -= 1
        result[i+1][i] -= 1
    return result


def graph_precision(n, alpha=1.0, strength=2.0):
    l = laplacian(n)
    return [[alpha*float(i == j)+strength*l[i][j] for j in range(n)] for i in range(n)]


def quadratic(a, x):
    return sum(x[i]*a[i][j]*x[j] for i in range(len(x)) for j in range(len(x)))


def logdet(a):
    return 2*sum(math.log(row[i]) for i, row in enumerate(cholesky(a)))


class InnovationBelief:
    """Affine conditional noise filter plus conjugate static-mean posterior."""
    def __init__(self, residual_covariance, phi, measurement_variance, prior_precision):
        self.n = len(residual_covariance)
        self.kz = residual_covariance
        self.phi = phi
        self.r = measurement_variance
        self.p = [list(row) for row in residual_covariance]
        self.g = [0.0]*self.n
        self.derivative = [[0.0]*self.n for _ in range(self.n)]
        self.mean = [0.0]*self.n
        self.covariance = inverse(prior_precision)
        self.prior_precision = prior_precision
        self.information = [[0.0]*self.n for _ in range(self.n)]
        self.score = [0.0]*self.n

    def experiment(self, arm):
        sensitivity = [self.derivative[arm][j]+float(j == arm) for j in range(self.n)]
        variance = self.p[arm][arm]+self.r
        return sensitivity, variance

    def target_slopes(self, arm):
        sensitivity, variance = self.experiment(arm)
        column = [dot(row, sensitivity) for row in self.covariance]
        denominator = math.sqrt(variance+dot(sensitivity, column))
        return [x/denominator for x in column]

    def observe(self, arm, observation):
        sensitivity, variance = self.experiment(arm)
        residual = observation-self.g[arm]
        for i in range(self.n):
            self.score[i] += sensitivity[i]*residual/variance
            for j in range(self.n):
                self.information[i][j] += sensitivity[i]*sensitivity[j]/variance
        column = [dot(row, sensitivity) for row in self.covariance]
        denominator = variance+dot(sensitivity, column)
        innovation = residual-dot(sensitivity, self.mean)
        self.mean = [m+c*innovation/denominator for m, c in zip(self.mean, column)]
        self.covariance = [[self.covariance[i][j]-column[i]*column[j]/denominator
                            for j in range(self.n)] for i in range(self.n)]
        noise_column = [row[arm] for row in self.p]
        gain = [x/variance for x in noise_column]
        self.g = [self.phi*(g+k*residual) for g, k in zip(self.g, gain)]
        self.derivative = [[self.phi*(self.derivative[i][j]-gain[i]*sensitivity[j])
                           for j in range(self.n)] for i in range(self.n)]
        self.p = [[self.phi**2*(self.p[i][j]-noise_column[i]*noise_column[j]/variance)
                   +(1-self.phi**2)*self.kz[i][j] for j in range(self.n)] for i in range(self.n)]

    def confidence_radius(self, norm_bound, energy_bound, strength, alpha=1.0, delta=0.05):
        j = [[self.prior_precision[i][k]+self.information[i][k]
              for k in range(self.n)] for i in range(self.n)]
        stochastic = math.sqrt(max(0.0, logdet(j)-logdet(self.prior_precision)+2*math.log(1/delta)))
        return stochastic+math.sqrt(alpha*norm_bound**2+strength*energy_bound**2)


def dense_information(actions, kz, phi, noise, values=None):
    n, t = len(kz), len(actions)
    xi = [[kz[actions[i]][actions[j]]*phi**abs(i-j)+noise*float(i == j)
           for j in range(t)] for i in range(t)]
    m = [[float(j == a) for j in range(n)] for a in actions]
    xi_inverse_m = [solve(xi, list(col)) for col in zip(*m)]
    information = [[dot(list(col), solved) for solved in xi_inverse_m] for col in zip(*m)]
    score = None if values is None else [dot(list(col), solve(xi, values)) for col in zip(*m)]
    return information, score


def posterior_difference(actions, covariance, phi, noise, precision):
    info, _ = dense_information(actions, covariance, phi, noise)
    posterior = inverse([[info[i][j]+precision[i][j] for j in range(2)] for i in range(2)])
    return posterior[0][0]+posterior[1][1]-2*posterior[0][1]


def choose_mean_action(policy, belief, time, rng):
    n = belief.n
    if policy == "round_robin":
        return time % n
    # One forced observation every n+1 rounds; forced locations cycle.
    if time % (n+1) == 0:
        return (time//(n+1)) % n
    if policy == "graph_ar_contrast":
        leader = max(range(n), key=lambda i: belief.mean[i])
        def standardized_gap(j):
            variance = belief.covariance[leader][leader]+belief.covariance[j][j]-2*belief.covariance[leader][j]
            return (belief.mean[leader]-belief.mean[j])/math.sqrt(max(variance, 1e-15))
        challenger = min((j for j in range(n) if j != leader), key=standardized_gap)
        scores = [(slopes[leader]-slopes[challenger])**2
                  for slopes in (belief.target_slopes(a) for a in range(n))]
    else:
        scores = [expected_max_lines(belief.mean, belief.target_slopes(a))-max(belief.mean)
                  for a in range(n)]
    highest = max(scores)
    return rng.choice([i for i, score in enumerate(scores) if abs(score-highest) < 1e-12])


def verify():
    rng, checks = random.Random(9112026), 0
    # Innovation information, score and posterior agree with the batch AR likelihood.
    for n in (2, 3, 5):
        kz, h = graph_covariance(n, 2), graph_precision(n)
        for phi in (0.0, 0.5, 0.95, -0.6):
            for noise in (0.0, 0.1):
                belief = InnovationBelief(kz, phi, noise, h)
                actions, values = [], []
                for _ in range(10):
                    actions.append(rng.randrange(n))
                    values.append(rng.gauss(0, 1))
                    belief.observe(actions[-1], values[-1])
                    info, score = dense_information(actions, kz, phi, noise, values)
                    batch_covariance = inverse([[info[i][j]+h[i][j] for j in range(n)] for i in range(n)])
                    batch_mean = [dot(row, score) for row in batch_covariance]
                    for i in range(n):
                        assert abs(belief.score[i]-score[i]) < 1e-8
                        assert abs(belief.mean[i]-batch_mean[i]) < 1e-8
                        checks += 2
                        for j in range(n):
                            assert abs(belief.information[i][j]-info[i][j]) < 1e-8
                            assert abs(belief.covariance[i][j]-batch_covariance[i][j]) < 1e-8
                            checks += 2
    # Hard energy constraint: scalar dual solution actually enforces the supplied radius.
    n, l, mu = 5, laplacian(5), [0.0, 0.2, 0.4, 0.6, 0.8]
    info = [[float(i == j)*(i+1) for j in range(n)] for i in range(n)]
    score = [dot(row, mu) for row in info]
    radius = math.sqrt(quadratic(l, mu))/2
    fitted, multiplier = constrained_mean(info, score, l, radius)
    assert abs(quadratic(l, fitted)-radius**2) < 1e-10
    assert multiplier > 0
    checks += 2
    # Exact fixed-design bias and contrast noise variance of Laplacian ridge.
    for strength in (0.0, 0.1, 1.0, 10.0):
        h = [[info[i][j]+strength*l[i][j] for j in range(n)] for i in range(n)]
        a = inverse(h)
        c = [1.0, 0.0, 0.0, 0.0, -1.0]
        estimate = [dot(row, score) for row in a]
        error = dot(c, [estimate[i]-mu[i] for i in range(n)])
        ac = [dot(row, c) for row in a]
        predicted_bias = -strength*dot(ac, [dot(row, mu) for row in l])
        assert abs(error-predicted_bias) < 1e-10
        bias_bound = strength*math.sqrt(quadratic(l, mu)*quadratic(l, ac))
        assert abs(error) <= bias_bound+1e-10
        checks += 2
    # Sharp two-observation Bayes-PCS design comparison on a broad parameter grid.
    two_arm_rows = []
    for phi, rho, alpha, strength, noise in product((0.0, 0.5, 0.9, 0.99),
            (-0.9, 0.0, 0.5, 0.9), (0.2, 1.0, 5.0), (0.0, 0.5, 2.0), (0.0, 0.1)):
        kz = [[1.0, rho], [rho, 1.0]]
        h = graph_precision(2, alpha, strength)
        hm = alpha+2*strength
        s0 = 2/hm
        vminus = 1-rho*phi+noise
        switch = 2/(hm+1/vminus)
        block_noise = (1+phi+noise)/2
        repeat = 1/(1/s0+1/(4*(1/(2*alpha)+block_noise)))
        assert abs(switch-posterior_difference((0, 1), kz, phi, noise, h)) < 1e-9
        assert abs(repeat-posterior_difference((0, 0), kz, phi, noise, h)) < 1e-9
        assert switch <= repeat+1e-10
        pcs = 0.5+math.atan(1/math.sqrt(hm*vminus))/math.pi
        assert abs(pcs-(0.5+math.asin(math.sqrt(1-switch/s0))/math.pi)) < 1e-10
        checks += 4
        if alpha == 1.0 and strength == 0.5 and noise == 0.1:
            two_arm_rows.append({"phi": phi, "rho": rho, "posterior_difference_variance": switch,
                                 "bayes_pcs": pcs, "repeat_variance": repeat})
    # Graph-free posterior information when phi=0: off-diagonal noise cannot help.
    for strength in (0.0, 2.0, 20.0):
        info, _ = dense_information((0, 1, 0, 2), graph_covariance(3, strength), 0.0, 0.1)
        counts = (2, 1, 1)
        for i in range(3):
            for j in range(3):
                assert abs(info[i][j]-float(i == j)*counts[i]/1.1) < 1e-9
                checks += 1
    # Full-field information spectrum and temporal effective sample size.
    for phi in (0.0, 0.5, 0.9, -0.5):
        for t in (1, 2, 5, 20):
            r = [[phi**abs(i-j) for j in range(t)] for i in range(t)]
            actual = sum(solve(r, [1.0]*t))
            exact = (t*(1-phi)+2*phi)/(1+phi)
            assert abs(actual-exact) < 1e-8
            checks += 1
    # Independent prior-predictive draws check selection probabilities, rather
    # than comparing only equivalent analytic expressions for variance.
    pcs_draws = []
    trials = 50000
    pcs_rng = random.Random(20101989)
    for phi, rho in ((0.0, 0.9), (0.99, 0.9), (0.9, -0.9)):
        alpha, strength, noise = 1.0, 0.5, 0.1
        hm, successful = alpha+2*strength, 0
        correlation = phi*rho
        for _ in range(trials):
            common = pcs_rng.gauss(0, math.sqrt(1/(2*alpha)))
            difference = pcs_rng.gauss(0, math.sqrt(2/hm))
            first_noise = pcs_rng.gauss(0, 1)
            second_noise = correlation*first_noise+math.sqrt(1-correlation**2)*pcs_rng.gauss(0, 1)
            first = common+difference/2+first_noise+pcs_rng.gauss(0, math.sqrt(noise))
            second = common-difference/2+second_noise+pcs_rng.gauss(0, math.sqrt(noise))
            successful += int((first-second)*difference > 0)
        theory = 0.5+math.atan(1/math.sqrt(hm*(1-correlation+noise)))/math.pi
        observed = successful/trials
        se = math.sqrt(theory*(1-theory)/trials)
        assert abs(observed-theory) < 6*se
        checks += 1
        pcs_draws.append({"phi": phi, "rho": rho, "trials": trials,
                          "theoretical_pcs": theory, "observed_pcs": observed,
                          "monte_carlo_standard_error": se})
    return {"checks": checks, "innovation_regression_matches_batch": True,
            "constrained_mean_enforces_energy": True,
            "two_arm_other_location_optimal_with_two_observations": True,
            "two_arm_closed_forms": two_arm_rows,
            "independent_two_arm_pcs_checks": pcs_draws,
            "phi_zero_removes_transient_cross_location_information": True}


def constrained_mean(information, score, l, radius):
    """Connected graph, positive definite information in this implementation."""
    def fit(multiplier):
        return solve([[information[i][j]+multiplier*l[i][j]
                       for j in range(len(l))] for i in range(len(l))], score)
    initial = fit(0.0)
    if quadratic(l, initial) <= radius**2:
        return initial, 0.0
    if radius <= 0:
        ones = [1.0]*len(l)
        constant = sum(score)/quadratic(information, ones)
        return [constant]*len(l), math.inf
    left, right = 0.0, 1.0
    while quadratic(l, fit(right)) > radius**2:
        right *= 2
    for _ in range(80):
        midpoint = (left+right)/2
        if quadratic(l, fit(midpoint)) > radius**2:
            left = midpoint
        else:
            right = midpoint
    return fit(right), right


def simulate(runs, budget, seed, n=6):
    kz, l = graph_covariance(n, 2.0), laplacian(n)
    fitted_h = graph_precision(n, 1.0, 2.0)
    fitted_kmu = inverse(fitted_h)
    diagonal_h = [[float(i == j)/fitted_kmu[i][i] for j in range(n)] for i in range(n)]
    permutation = [0, 2, 4, 1, 3, 5]
    wrong_h = [[fitted_h[permutation[i]][permutation[j]] for j in range(n)] for i in range(n)]
    rows, paired = [], []
    for true_strength in (0.0, 2.0):
        true_kmu = inverse(graph_precision(n, 1.0, true_strength))
        mean_lower, residual_lower = cholesky(true_kmu), cholesky(kz)
        for phi in (0.0, 0.9, 0.99):
            losses = {p: [] for p in POLICIES}
            mses = {p: [] for p in POLICIES}
            successes = {p: [] for p in POLICIES}
            coverages = {p: [] for p in POLICIES}
            confidence_passes = []
            for run in range(runs):
                rng = random.Random(seed+run+int(true_strength)*100000+round(phi*100)*10000)
                mu = gaussian_draw(true_kmu, rng, mean_lower)
                state = gaussian_draw(kz, rng, residual_lower)
                best = max(mu)
                beliefs = {p: InnovationBelief(kz, 0.0 if p == "graph_iid_kg" else phi, 0.1,
                    identity(n) if p == "unstructured_ar_kg" else diagonal_h if p == "diagonal_mean_ar_kg"
                    else wrong_h if p == "wrong_mean_graph_ar_kg"
                    else fitted_h) for p in POLICIES}
                streams = {p: random.Random(seed+run*97+index*9173) for index, p in enumerate(POLICIES)}
                norm, energy = math.sqrt(dot(mu, mu)), math.sqrt(max(quadratic(l, mu), 0.0))
                path_confidence = True
                for time in range(budget):
                    noises = [rng.gauss(0, math.sqrt(0.1)) for _ in range(n)]
                    for p in POLICIES:
                        belief = beliefs[p]
                        action = choose_mean_action(p, belief, time, streams[p])
                        belief.observe(action, mu[action]+state[action]+noises[action])
                    # Oracle-supplied valid norm/energy radii audit the frequentist theorem;
                    # these are not provided to the action policies.
                    b = beliefs["graph_ar_kg"]
                    beta = b.confidence_radius(norm, energy, 2.0)
                    error = [x-y for x, y in zip(b.mean, mu)]
                    j = [[fitted_h[i][k]+b.information[i][k] for k in range(n)] for i in range(n)]
                    path_confidence = path_confidence and quadratic(j, error) <= beta**2+1e-9
                    innovation = gaussian_draw(kz, rng, residual_lower)
                    state = [phi*x+math.sqrt(1-phi**2)*y for x, y in zip(state, innovation)]
                confidence_passes.append(int(path_confidence))
                for p, belief in beliefs.items():
                    recommendation = max(range(n), key=lambda i: belief.mean[i])
                    losses[p].append(best-mu[recommendation])
                    successes[p].append(int(mu[recommendation] == best))
                    mses[p].append(sum((x-y)**2 for x, y in zip(belief.mean, mu))/n)
                    cvar = belief.covariance[0][0]+belief.covariance[-1][-1]-2*belief.covariance[0][-1]
                    cerror = (belief.mean[0]-belief.mean[-1])-(mu[0]-mu[-1])
                    coverages[p].append(int(abs(cerror) <= 1.96*math.sqrt(cvar)))
            for p in POLICIES:
                rows.append({"true_mean_graph_strength": true_strength, "phi": phi, "policy": p,
                    "opportunity_loss": statistics.mean(losses[p]),
                    "opportunity_loss_se": statistics.stdev(losses[p])/math.sqrt(runs),
                    "pcs_max_posterior_mean": statistics.mean(successes[p]),
                    "pcs_se": statistics.stdev(successes[p])/math.sqrt(runs),
                    "mean_squared_error": statistics.mean(mses[p]),
                    "contrast_credible_coverage": statistics.mean(coverages[p]),
                    "valid_confidence_path_coverage": statistics.mean(confidence_passes),
                    "runs": runs, "budget": budget})
            for p in POLICIES[1:]:
                differences = [x-y for x, y in zip(losses[p], losses["graph_ar_kg"])]
                paired.append({"true_mean_graph_strength": true_strength, "phi": phi,
                    "comparator": p, "opportunity_loss_difference": statistics.mean(differences),
                    "standard_error": statistics.stdev(differences)/math.sqrt(runs)})
            print(f"mean strength={true_strength:g} phi={phi:g}: {runs} paired runs", flush=True)
    metadata = {"runs": runs, "budget": budget, "seed": seed, "arms": n,
        "true_residual_graph": "normalized path resolvent, strength 2, marginal variance 1",
        "true_mean_prior": "inverse(I + true_strength * path_L)",
        "fitted_graph_mean_prior": "inverse(I + 2 * path_L)",
        "unstructured_mean_prior": "I; marginal variances differ from graph prior",
        "diagonal_mean_prior": "same marginal mean variances as fitted graph prior, zero cross-covariance",
        "measurement_variance": 0.1, "forced_cadence": n+1,
        "recommendation": "largest posterior mean: opportunity-loss optimal, not generally PCS optimal",
        "frequentist_confidence_audit": "graph_ar_kg only; uses true norm and graph energy solely for a valid supplied-radius diagnostic; coverage repeated across policy rows",
        "wrong_mean_graph_permutation": permutation}
    return rows, paired, metadata


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render(rows, paired, metadata, checks):
    lines = ["# Permanent-mean selection under spatial AR(1) fluctuations", "",
        f"{metadata['runs']} independent paired runs per configuration; six nodes and {metadata['budget']} measurements.",
        "Means are drawn once and held fixed. All policies see the same possible readings within a run. Residual variance is one and measurement variance is 0.1.",
        "True mean graph strength 2 matches the fitted prior; strength 0 is an unstructured prior and stresses the imposed smoothing.",
        "PCS below evaluates the largest-posterior-mean recommendation. This decision minimizes Bayesian opportunity loss under a correct model; it is not the general multi-arm Bayes-PCS rule.", "",
        "| True mean strength | phi | Policy | Opportunity loss | SE | PCS | MSE per mean | Contrast coverage |",
        "|---|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['true_mean_graph_strength']:g} | {row['phi']:g} | {row['policy']} | {row['opportunity_loss']:.4f} | {row['opportunity_loss_se']:.4f} | {row['pcs_max_posterior_mean']:.3f} | {row['mean_squared_error']:.4f} | {row['contrast_credible_coverage']:.3f} |")
    lines += ["", "Positive paired opportunity-loss differences favor graph AR knowledge gradient.", "",
        "| True mean strength | phi | Comparator | Difference | Approx. 95% half-width |", "|---|---|---|---|---|"]
    for row in paired:
        lines.append(f"| {row['true_mean_graph_strength']:g} | {row['phi']:g} | {row['comparator']} | {row['opportunity_loss_difference']:.4f} | {1.96*row['standard_error']:.4f} |")
    lines += ["", "## Interpretation and scope", "",
        "The diagonal-mean baseline retains the graph prior's marginal variances while removing its cross-covariances. The separate unstructured prior is I and matches the rough-mean generative model.",
        "The confidence theorem audit tests graph_ar_kg and supplies each trajectory's actual mean norm and energy as valid radii, independently of measurement noise. The sampling policies do not use those radii; this does not demonstrate learning or validating them. Its per-configuration coverage is repeated in CSV policy rows and does not audit misspecified filters.",
        "Contrast coverage refers to a fixed endpoint contrast and Gaussian posterior 95% intervals. Those intervals have a Bayesian interpretation only under the matched generative model. All-time frequentist confidence uses a distinct, bias-aware radius and is generally conservative.",
        "The KG rule is exact with one observation remaining for opportunity loss; rolling KG and the selected-contrast heuristic have no fixed-budget optimality guarantee. Forced probes ensure asymptotic observation of every arm.",
        "No real traffic data, hyperparameter fitting, unknown AR dynamics, general PCS-optimal control, or matching lower/upper bound is evaluated.",
        f"Separate exact checks: {checks['checks']}; see checks.json.", ""]
    (OUTPUT / "findings.md").write_text("\n".join(lines))
    table = [r"\begin{tabular}{rrlrrr}", r"\toprule", r"$\lambda_{\rm true}$ & $\phi$ & Policy & EOC & PCS & MSE \\", r"\midrule"]
    labels = {"graph_ar_kg": "Graph--AR KG", "unstructured_ar_kg": "Unstructured--AR KG",
        "graph_iid_kg": "Graph--iid KG", "wrong_mean_graph_ar_kg": "Wrong-graph--AR KG",
        "graph_ar_contrast": "Contrast rule", "round_robin": "Round robin"}
    for row in rows:
        if row["policy"] in ("graph_ar_kg", "unstructured_ar_kg", "graph_iid_kg", "round_robin"):
            table.append(f"{row['true_mean_graph_strength']:g} & {row['phi']:g} & {labels[row['policy']]} & {row['opportunity_loss']:.3f} & {row['pcs_max_posterior_mean']:.3f} & {row['mean_squared_error']:.3f}" + r" \\")
    table += [r"\bottomrule", r"\end{tabular}"]
    (OUTPUT / "table.tex").write_text("\n".join(table)+"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--runs", type=int, default=200)
    parser.add_argument("--budget", type=int, default=48)
    parser.add_argument("--seed", type=int, default=9112026)
    args = parser.parse_args()
    checks = verify()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "checks.json").write_text(json.dumps(checks, indent=2)+"\n")
    if args.verify:
        print(json.dumps(checks, indent=2))
        return
    if args.render_only:
        def read(path):
            with path.open(newline="") as file:
                return [{key: value if key in ("policy", "comparator") else float(value)
                         for key, value in row.items()} for row in csv.DictReader(file)]
        render(read(OUTPUT / "summary.csv"), read(OUTPUT / "paired.csv"),
               json.loads((OUTPUT / "metadata.json").read_text()), checks)
        return
    if args.runs < 2 or args.budget < 2:
        parser.error("runs and budget must be at least two")
    rows, paired, metadata = simulate(args.runs, args.budget, args.seed)
    write_csv(OUTPUT / "summary.csv", rows)
    write_csv(OUTPUT / "paired.csv", paired)
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    render(rows, paired, metadata, checks)


if __name__ == "__main__":
    main()
