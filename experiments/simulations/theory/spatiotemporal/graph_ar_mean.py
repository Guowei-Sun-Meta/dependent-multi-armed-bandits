"""Fixed graph-smooth means with heterogeneous AR(p_i) correlated innovations.

Standard library only. The mean vector is fixed across every repeated-noise
experiment. Graph regularization is not a distribution for the means.
    python3 experiments/simulations/theory/spatiotemporal/graph_ar_mean.py --verify
    python3 experiments/simulations/theory/spatiotemporal/graph_ar_mean.py --runs 200 --budget 60
"""
import argparse
import cmath
import csv
import json
import math
from pathlib import Path
import random
import statistics

from spatiotemporal_bandits import (
    cholesky, dot, gaussian_draw, graph_covariance, inverse, matmul, solve, transpose)

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "research" / "spatiotemporal_bandits" / "results" / "general_ar"
NORMAL = statistics.NormalDist()
POLICIES = ("graph_ar_contrast", "unstructured_ar_contrast",
            "diagonal_noise_ar_contrast", "wrong_mean_graph_ar_contrast",
            "graph_iid_contrast", "round_robin", "block_cyclic")
ALPHA, STRENGTH, NOISE = 0.05, 0.5, 0.1
DYNAMICS = {
    "lag_two": [(0.0, 0.75)]*6,
    "oscillatory": [(0.7, -0.45)]*6,
    "heterogeneous": [(0.6, -0.2), (0.35, 0.1, 0.2),
                      (0.0, 0.75), (0.1, 0.4, -0.1),
                      (0.7, -0.3), (0.2, 0.0, 0.45)]}
MEANS = {"smooth": [0.0, 0.2, 0.45, 0.65, 0.75, 0.7],
         "rough": [0.0, 0.65, 0.2, 0.75, 0.1, 0.7]}


def regularizer(l, alpha=ALPHA, strength=STRENGTH):
    return [[alpha*float(i == j)+strength*l[i][j]
             for j in range(len(l))] for i in range(len(l))]


def laplacian(n):
    result = [[0.0]*n for _ in range(n)]
    for i in range(n-1):
        result[i][i] += 1
        result[i+1][i+1] += 1
        result[i][i+1] -= 1
        result[i+1][i] -= 1
    return result


def quadratic(matrix, vector):
    return sum(vector[i]*matrix[i][j]*vector[j]
               for i in range(len(vector)) for j in range(len(vector)))


def logdet(matrix):
    return 2*sum(math.log(row[i]) for i, row in enumerate(cholesky(matrix)))


def constrained_mean(information, score, l, radius):
    """Scalar dual implementation for positive definite information."""
    def fit(multiplier):
        return solve([[information[i][j]+multiplier*l[i][j]
                       for j in range(len(l))] for i in range(len(l))], score)
    initial = fit(0.0)
    if quadratic(l, initial) <= radius**2:
        return initial, 0.0
    if radius <= 0:
        constant = sum(score)/quadratic(information, [1.0]*len(l))
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


class GraphAR:
    """Block companion state; Q correlates contemporaneous innovations."""
    def __init__(self, coefficients, innovation_covariance):
        self.coefficients = [list(a) for a in coefficients]
        self.n = len(coefficients)
        self.current, self.d = [], 0
        for a in coefficients:
            if not a:
                raise ValueError("An AR lag vector must be supplied.")
            self.current.append(self.d)
            self.d += len(a)
        self.q = [list(row) for row in innovation_covariance]
        self.f = [[0.0]*self.d for _ in range(self.d)]
        self.w = [[0.0]*self.d for _ in range(self.d)]
        for i, a in enumerate(coefficients):
            start = self.current[i]
            self.f[start][start:start+len(a)] = a
            for j in range(1, len(a)):
                self.f[start+j][start+j-1] = 1.0
            for j in range(self.n):
                self.w[start][self.current[j]] = self.q[i][j]
        self.sparse = [[(j, x) for j, x in enumerate(row) if x != 0]
                       for row in self.f]
        # Independent stationary Lyapunov solve, not a filtering recursion.
        matrix, rhs = [], []
        for i in range(self.d):
            for j in range(self.d):
                matrix.append([float(i == k and j == m)-self.f[i][k]*self.f[j][m]
                               for k in range(self.d) for m in range(self.d)])
                rhs.append(self.w[i][j])
        flat = solve(matrix, rhs)
        self.gamma = [[flat[i*self.d+j] for j in range(self.d)] for i in range(self.d)]
        cholesky(self.gamma)  # Reject non-positive stationary solutions.

    def transition_vector(self, x):
        return [sum(weight*x[j] for j, weight in row) for row in self.sparse]

    def transition_rows(self, a):
        cols = len(a[0])
        return [[sum(weight*a[j][k] for j, weight in row)
                 for k in range(cols)] for row in self.sparse]

    def transition_covariance(self, p):
        left = self.transition_rows(p)
        return [[sum(weight*left[i][k] for k, weight in row)
                 for row in self.sparse] for i in range(self.d)]

    def covariance_sequence(self, horizon):
        result, current = [], self.gamma
        for _ in range(horizon+1):
            result.append([[current[i][j] for j in self.current] for i in self.current])
            current = self.transition_rows(current)
        return result

    def covariance(self, actions, times=None, noise=NOISE):
        times = list(range(len(actions))) if times is None else times
        sequence = self.covariance_sequence(max(times, default=0)-min(times, default=0))
        result = []
        for i, (a, t) in enumerate(zip(actions, times)):
            row = []
            for j, (b, s) in enumerate(zip(actions, times)):
                value = sequence[t-s][a][b] if t >= s else sequence[s-t][b][a]
                row.append(value+noise*float(i == j))
            result.append(row)
        return result

    def spectral_bounds(self, points=4096):
        # A Lipschitz correction certifies a lower bound between grid points.
        minimum = math.inf
        maximum = 0.0
        for a in self.coefficients:
            grid_min = min(abs(1-sum(x*cmath.exp(-1j*k*2*math.pi*j/points)
                                    for k, x in enumerate(a, 1)))
                           for j in range(points))
            lower = grid_min-math.pi/points*sum(k*abs(x) for k, x in enumerate(a, 1))
            if lower <= 0:
                raise ValueError("Increase spectral grid resolution.")
            minimum = min(minimum, lower)
            maximum = max(maximum, 1+sum(map(abs, a)))
        qmax = max(sum(map(abs, row)) for row in self.q)
        qmin = 1/max(sum(map(abs, row)) for row in inverse(self.q))
        return qmin/maximum**2, qmax/minimum**2


class MeanFilter:
    """Conditional lag-state likelihood for a fixed unknown mean."""
    def __init__(self, model, h, noise=NOISE):
        self.model, self.n, self.d, self.r = model, model.n, model.d, noise
        self.p = [list(row) for row in model.gamma]
        self.g = [0.0]*self.d
        self.dmean = [[0.0]*self.n for _ in range(self.d)]
        self.h = h
        self.v = inverse(h)  # Inverse regularized information, not a mean prior.
        self.mean = [0.0]*self.n
        self.info = [[0.0]*self.n for _ in range(self.n)]
        self.score = [0.0]*self.n

    def experiment(self, arm):
        loc = self.model.current[arm]
        vector = [self.dmean[loc][j]+float(j == arm) for j in range(self.n)]
        return loc, vector, self.p[loc][loc]+self.r

    def contrast_gain(self, arm, leader, challenger):
        _, vector, variance = self.experiment(arm)
        column = [dot(row, vector) for row in self.v]
        return (column[leader]-column[challenger])**2/(variance+dot(vector, column))

    def observe(self, arm, observation):
        loc, vector, variance = self.experiment(arm)
        residual = observation-self.g[loc]
        for i in range(self.n):
            self.score[i] += vector[i]*residual/variance
            for j in range(self.n):
                self.info[i][j] += vector[i]*vector[j]/variance
        column = [dot(row, vector) for row in self.v]
        total = variance+dot(vector, column)
        innovation = residual-dot(vector, self.mean)
        self.mean = [m+x*innovation/total for m, x in zip(self.mean, column)]
        self.v = [[self.v[i][j]-column[i]*column[j]/total
                   for j in range(self.n)] for i in range(self.n)]
        pc = [row[loc] for row in self.p]
        updated_g = [g+x*residual/variance for g, x in zip(self.g, pc)]
        updated_d = [[self.dmean[i][j]-pc[i]*vector[j]/variance
                      for j in range(self.n)] for i in range(self.d)]
        updated_p = [[self.p[i][j]-pc[i]*pc[j]/variance
                      for j in range(self.d)] for i in range(self.d)]
        self.g = self.model.transition_vector(updated_g)
        self.dmean = self.model.transition_rows(updated_d)
        moved = self.model.transition_covariance(updated_p)
        self.p = [[moved[i][j]+self.model.w[i][j]
                   for j in range(self.d)] for i in range(self.d)]

    def beta(self, norm, energy, alpha=ALPHA, strength=STRENGTH, delta=0.05):
        j = [[self.h[i][k]+self.info[i][k] for k in range(self.n)] for i in range(self.n)]
        return math.sqrt(max(0.0, logdet(j)-logdet(self.h)+2*math.log(1/delta))) + math.sqrt(
            alpha*norm**2+strength*energy**2)

    def certified(self, beta):
        best = max(range(self.n), key=lambda i: self.mean[i])
        return all(self.mean[best]-self.mean[j] > beta*math.sqrt(max(0.0,
                   self.v[best][best]+self.v[j][j]-2*self.v[best][j]))
                   for j in range(self.n) if j != best)


def dense_information(model, actions, values=None, times=None, noise=NOISE):
    xi = model.covariance(actions, times, noise)
    n = model.n
    m = [[float(a == i) for i in range(n)] for a in actions]
    solved = [solve(xi, list(col)) for col in zip(*m)]
    info = [[dot(list(col), v) for v in solved] for col in zip(*m)]
    score = None if values is None else [
        dot(list(col), solve(xi, values)) for col in zip(*m)]
    return info, score


def choose(policy, belief, time, rng):
    n = belief.n
    if policy == "round_robin":
        return time % n
    if policy == "block_cyclic":
        block = max(map(len, belief.model.coefficients))
        return (time//block) % n
    if time % (n+1) == 0:
        return (time//(n+1)) % n
    best = max(range(n), key=lambda i: belief.mean[i])
    def standardized(j):
        var = belief.v[best][best]+belief.v[j][j]-2*belief.v[best][j]
        return (belief.mean[best]-belief.mean[j])/math.sqrt(max(var, 1e-14))
    challenger = min((j for j in range(n) if j != best), key=standardized)
    scores = [belief.contrast_gain(a, best, challenger) for a in range(n)]
    highest = max(scores)
    return rng.choice([i for i, value in enumerate(scores) if abs(value-highest) < 1e-12])


def verify():
    rng, checks = random.Random(1402026), 0
    qs = [[[0.3, 0.12], [0.12, 0.3]],
          [[0.3, 0.08, 0.04], [0.08, 0.3, 0.1], [0.04, 0.1, 0.3]]]
    specifications = [
        [(0.0, 0.7), (0.0, 0.7)],
        [(0.7, -0.45), (0.3, 0.2, 0.15)],
        [(0.6, -0.2), (0.3, 0.1, 0.2), (0.0, 0.7)]]
    for coefficients in specifications:
        n = len(coefficients)
        model = GraphAR(coefficients, qs[n-2])
        stationary_rhs = model.transition_covariance(model.gamma)
        for i in range(model.d):
            for j in range(model.d):
                assert abs(model.gamma[i][j]-stationary_rhs[i][j]-model.w[i][j]) < 1e-10
                checks += 1
        # Independent impulse-response covariance; delayed shocks correlate arms.
        impulse_cov = [[0.0]*model.d for _ in range(model.d)]
        impulse = [[float(i == j) for j in model.current] for i in range(model.d)]
        for _ in range(160):
            contribution = matmul(matmul(impulse, model.q), transpose(impulse))
            impulse_cov = [[x+y for x, y in zip(ar, br)]
                           for ar, br in zip(impulse_cov, contribution)]
            impulse = model.transition_rows(impulse)
        for i in range(model.d):
            for j in range(model.d):
                assert abs(model.gamma[i][j]-impulse_cov[i][j]) < 1e-9
                checks += 1
        for noise in (0.0, 0.1):
            h = regularizer(laplacian(n))
            belief = MeanFilter(model, h, noise)
            actions, values = [], []
            for t in range(12):
                # Actions depend on past measurements.
                action = (max(range(n), key=lambda i: belief.mean[i])+t) % n
                actions.append(action)
                values.append(rng.gauss(0, 1))
                belief.observe(action, values[-1])
                info, score = dense_information(model, actions, values, noise=noise)
                jmatrix = [[h[i][j]+info[i][j] for j in range(n)] for i in range(n)]
                batch_v = inverse(jmatrix)
                batch_mean = [dot(row, score) for row in batch_v]
                for i in range(n):
                    assert abs(belief.score[i]-score[i]) < 1e-8
                    assert abs(belief.mean[i]-batch_mean[i]) < 1e-8
                    checks += 2
                    for j in range(n):
                        assert abs(belief.info[i][j]-info[i][j]) < 1e-8
                        assert abs(belief.v[i][j]-batch_v[i][j]) < 1e-8
                        checks += 2
            # Full-field finite-n innovation information identity.
            p, periods = max(map(len, coefficients)), 7
            all_actions = list(range(n))*periods
            times = [t for t in range(periods) for _ in range(n)]
            whole, _ = dense_information(model, all_actions, times=times, noise=0.0)
            initial, _ = dense_information(model, all_actions[:n*p],
                                            times=times[:n*p], noise=0.0)
            qinverse = inverse(model.q)
            c = [1-sum(a) for a in coefficients]
            for i in range(n):
                for j in range(n):
                    predicted = initial[i][j]+(periods-p)*c[i]*qinverse[i][j]*c[j]
                    assert abs(whole[i][j]-predicted) < 1e-8
                    checks += 1
        lower, upper = model.spectral_bounds()
        # Selected covariance obeys certified spectral bounds.
        actions = [rng.randrange(n) for _ in range(12)]
        xi = model.covariance(actions, noise=0.0)
        for _ in range(40):
            vector = [rng.gauss(0, 1) for _ in actions]
            value = quadratic(xi, vector)/dot(vector, vector)
            assert lower-1e-10 <= value <= upper+1e-10
            checks += 1

    # Exact correlated AR(2) schedule comparison, independent dense GLS.
    schedule_rows = []
    for a in (0.2, 0.5, 0.8):
        for rho in (0.0, 0.4, 0.8):
            q = [[1-a*a, rho*(1-a*a)], [rho*(1-a*a), 1-a*a]]
            model = GraphAR([(0.0, a)]*2, q)
            for noise in (0.0, 0.1):
                for name, actions in (("AABB", (0, 0, 1, 1)), ("ABAB", (0, 1, 0, 1))):
                    info, _ = dense_information(model, actions, noise=noise)
                    covariance = inverse(info)
                    actual = covariance[0][0]+covariance[1][1]-2*covariance[0][1]
                    exact = 1+noise-a*rho if name == "AABB" else 1+noise+a
                    assert abs(actual-exact) < 1e-9
                    checks += 1
                    if a == 0.8 and noise == 0.1:
                        schedule_rows.append({"a": a, "rho": rho, "schedule": name,
                            "contrast_variance": exact, "gap": 0.4,
                            "fixed_mean_pcs": NORMAL.cdf(0.4/math.sqrt(exact))})
    # A hard mean constraint is an estimation constraint, not a mean prior.
    l = laplacian(3)
    info = [[2.0, 0, 0], [0, 3.0, 0], [0, 0, 4.0]]
    mu = [0.0, 0.3, 0.5]
    score = [dot(row, mu) for row in info]
    radius = math.sqrt(quadratic(l, mu))/2
    fitted, multiplier = constrained_mean(info, score, l, radius)
    assert multiplier > 0 and abs(quadratic(l, fitted)-radius**2) < 1e-10
    checks += 1
    # At fixed means, prior-free PCS agrees with direct AR trajectory draws.
    model = GraphAR([(0.0, 0.8)]*2, [[0.36, 0.216], [0.216, 0.36]])
    lower = cholesky(model.gamma)
    noise_lower = cholesky(model.q)
    trials, successes = 30000, {"AABB": 0, "ABAB": 0}
    for _ in range(trials):
        state = gaussian_draw(model.gamma, rng, lower)
        observations = []
        for t in range(4):
            observations.append([mean+state[loc]+rng.gauss(0, math.sqrt(0.1))
                                  for mean, loc in zip((0.4, 0.0), model.current)])
            innovation = gaussian_draw(model.q, rng, noise_lower)
            state = model.transition_vector(state)
            for i, loc in enumerate(model.current):
                state[loc] += innovation[i]
        for name, schedule in (("AABB", (0, 0, 1, 1)), ("ABAB", (0, 1, 0, 1))):
            contrast = sum((1 if arm == 0 else -1)*observations[t][arm]
                           for t, arm in enumerate(schedule))/2
            successes[name] += int(contrast > 0)
    simulation_pcs = []
    for name, variance in (("AABB", 0.62), ("ABAB", 1.9)):
        theory, observed = NORMAL.cdf(0.4/math.sqrt(variance)), successes[name]/trials
        se = math.sqrt(theory*(1-theory)/trials)
        assert abs(theory-observed) < 6*se
        checks += 1
        simulation_pcs.append({"schedule": name, "trials": trials,
            "theoretical_pcs": theory, "observed_pcs": observed, "standard_error": se})
    return {"checks": checks, "means_are_fixed": True,
        "all_non_iid_validation_orders": [2, 3],
        "innovation_filter_matches_dense_likelihood": True,
        "stationary_covariance_matches_impulse_response_sum": True,
        "full_field_information_identity": True,
        "general_ar2_schedule_comparison": schedule_rows,
        "fixed_mean_pcs_monte_carlo": simulation_pcs}


def simulate(runs, budget, seed):
    n, l = 6, laplacian(6)
    q = [[0.25*x for x in row] for row in graph_covariance(n, 2.0)]
    diagonal_q = [[q[i][i]*float(i == j) for j in range(n)] for i in range(n)]
    h = regularizer(l)
    permutation = [0, 2, 4, 1, 3, 5]
    wrong_l = [[l[permutation[i]][permutation[j]] for j in range(n)] for i in range(n)]
    rows, paired = [], []
    for case_index, (name, coefficients) in enumerate(DYNAMICS.items()):
        model = GraphAR(coefficients, q)
        diagonal_model = GraphAR(coefficients, diagonal_q)
        stationary_current = [[model.gamma[i][j] for j in model.current] for i in model.current]
        iid_model = GraphAR([[0.0]*len(a) for a in coefficients], stationary_current)
        lower, innovation_lower = cholesky(model.gamma), cholesky(q)
        for mean_index, (mean_name, mu) in enumerate(MEANS.items()):
            losses = {p: [] for p in POLICIES}
            mses = {p: [] for p in POLICIES}
            correct = {p: [] for p in POLICIES}
            audits, certificates = [], []
            # Conservative, fixed, externally supplied bounds shared by both means.
            norm_bound, energy_bound = 2.0, 2.0
            assert dot(mu, mu) <= norm_bound**2 and quadratic(l, mu) <= energy_bound**2
            for run in range(runs):
                rng = random.Random(seed+run+case_index*100000+mean_index*1000000)
                state = gaussian_draw(model.gamma, rng, lower)
                beliefs = {p: MeanFilter(
                    diagonal_model if p == "diagonal_noise_ar_contrast"
                    else iid_model if p == "graph_iid_contrast" else model,
                    regularizer(l, strength=0.0) if p == "unstructured_ar_contrast"
                    else regularizer(wrong_l) if p == "wrong_mean_graph_ar_contrast" else h)
                    for p in POLICIES}
                streams = {p: random.Random(seed+run*97+idx*971)
                           for idx, p in enumerate(POLICIES)}
                passed = True
                for time in range(budget):
                    readings = [mu[i]+state[loc]+rng.gauss(0, math.sqrt(NOISE))
                                for i, loc in enumerate(model.current)]
                    for p in POLICIES:
                        action = choose(p, beliefs[p], time, streams[p])
                        beliefs[p].observe(action, readings[action])
                    b = beliefs["graph_ar_contrast"]
                    beta = b.beta(norm_bound, energy_bound)
                    j = [[h[i][k]+b.info[i][k] for k in range(n)] for i in range(n)]
                    passed = passed and quadratic(j, [x-y for x, y in zip(b.mean, mu)]) <= beta**2+1e-9
                    innovation = gaussian_draw(q, rng, innovation_lower)
                    state = model.transition_vector(state)
                    for i, loc in enumerate(model.current):
                        state[loc] += innovation[i]
                audits.append(int(passed))
                certificates.append(int(b.certified(beta)))
                for p, b in beliefs.items():
                    recommendation = max(range(n), key=lambda i: b.mean[i])
                    losses[p].append(max(mu)-mu[recommendation])
                    correct[p].append(int(mu[recommendation] == max(mu)))
                    mses[p].append(sum((x-y)**2 for x, y in zip(b.mean, mu))/n)
            for p in POLICIES:
                rows.append({"dynamics": name, "mean_case": mean_name, "policy": p,
                    "opportunity_loss": statistics.mean(losses[p]),
                    "opportunity_loss_se": statistics.stdev(losses[p])/math.sqrt(runs),
                    "pcs": statistics.mean(correct[p]),
                    "pcs_se": statistics.stdev(correct[p])/math.sqrt(runs),
                    "mean_squared_error": statistics.mean(mses[p]),
                    "graph_policy_confidence_path_coverage": statistics.mean(audits),
                    "graph_policy_final_certificate_rate": statistics.mean(certificates),
                    "runs": runs, "budget": budget})
            for p in POLICIES[1:]:
                values = [x-y for x, y in zip(losses[p], losses["graph_ar_contrast"])]
                paired.append({"dynamics": name, "mean_case": mean_name, "comparator": p,
                    "loss_difference": statistics.mean(values),
                    "standard_error": statistics.stdev(values)/math.sqrt(runs)})
            print(f"{name}, fixed {mean_name} means: {runs} paired noise runs", flush=True)
    return rows, paired, {"runs": runs, "budget": budget, "seed": seed, "arms": n,
        "means_are_fixed": True, "fixed_mean_vectors": MEANS, "ar_coefficients": DYNAMICS,
        "innovation_covariance": q, "measurement_variance": NOISE,
        "mean_regularizer_alpha": ALPHA, "mean_graph_penalty": STRENGTH,
        "supplied_norm_bound": 2.0, "supplied_graph_energy_radius": 2.0,
        "confidence_audit": "graph_ar_contrast only; per-configuration values repeated across policy rows",
        "forced_probe_cadence": n+1, "wrong_mean_graph_permutation": permutation,
        "recommendation": "largest regularized mean; no Bayesian mean distribution",
        "models": "all substantive AR processes have order 2 or 3; iid is a misspecification baseline"}


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render(rows, paired, metadata, checks):
    write_csv(OUTPUT/"pcs_schedule.csv", [
        {"rho": j*0.95/100,
         "pcs_aabb": NORMAL.cdf(0.4/math.sqrt(1.1-0.8*j*0.95/100)),
         "pcs_abab": NORMAL.cdf(0.4/math.sqrt(1.9))}
        for j in range(101)])
    lines = ["# Fixed-mean selection with graph-correlated AR(p_i) innovations", "",
        f"{metadata['runs']} independent paired noise trajectories per configuration, {metadata['arms']} arms, and {metadata['budget']} samples.",
        "Each mean vector is fixed across all runs. Only stationary states, innovations, sensor noise, and policy randomization vary.",
        "Innovation covariance carries spatial correlation. A separate deterministic graph-energy bound constrains the unknown mean.",
        "All substantive AR models have order 2 or 3; the iid model is a misspecification baseline.", "",
        "| Dynamics | Fixed mean | Policy | Opportunity loss | SE | PCS | MSE |",
        "|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['dynamics']} | {row['mean_case']} | {row['policy']} | {row['opportunity_loss']:.4f} | {row['opportunity_loss_se']:.4f} | {row['pcs']:.3f} | {row['mean_squared_error']:.4f} |")
    lines += ["", "Positive paired loss differences favor graph AR contrast sampling.", "",
              "| Dynamics | Fixed mean | Comparator | Loss difference | Approx. 95% half-width |",
              "|---|---|---|---|---|"]
    for row in paired:
        lines.append(f"| {row['dynamics']} | {row['mean_case']} | {row['comparator']} | {row['loss_difference']:.4f} | {1.96*row['standard_error']:.4f} |")
    lines += ["", "The fixed supplied bounds B=2 and S=2 contain both mean vectors. The all-time confidence audit tests graph_ar_contrast only; its coverage and terminal certificate rates are repeated across policy rows.",
              "PCS is the repeated-noise success probability at a fixed truth. It is not averaged over a mean prior. Final recommendations without a passed certificate do not inherit the fixed-confidence stopping guarantee.",
              "The contrast rule reduces inverse regularized information for a selected comparison. It is a heuristic, with no general finite-budget optimality claim.",
              f"Numerical checks: {checks['checks']}; details in checks.json.", ""]
    (OUTPUT/"findings.md").write_text("\n".join(lines))
    labels = {"graph_ar_contrast": "Graph--AR contrast",
              "unstructured_ar_contrast": "Unstructured--AR",
              "graph_iid_contrast": "Graph--iid contrast",
              "round_robin": "Round robin", "block_cyclic": "Block cyclic"}
    table = [r"\begin{tabular}{lllrrr}", r"\toprule",
             r"Dynamics & Mean & Policy & Loss & PCS & MSE \\", r"\midrule"]
    for row in rows:
        if row["policy"] in labels:
            table.append(f"{row['dynamics'].replace('_',' ')} & {row['mean_case']} & {labels[row['policy']]} & {row['opportunity_loss']:.3f} & {row['pcs']:.3f} & {row['mean_squared_error']:.3f}" + r" \\")
    table += [r"\bottomrule", r"\end{tabular}"]
    (OUTPUT/"table.tex").write_text("\n".join(table)+"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--runs", type=int, default=200)
    parser.add_argument("--budget", type=int, default=60)
    parser.add_argument("--seed", type=int, default=14102026)
    args = parser.parse_args()
    checks = verify()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT/"checks.json").write_text(json.dumps(checks, indent=2)+"\n")
    if args.verify:
        print(json.dumps(checks, indent=2))
        return
    if args.render_only:
        def read(name):
            with (OUTPUT/name).open(newline="") as handle:
                return [{k: v if k in ("dynamics", "mean_case", "policy", "comparator") else float(v)
                         for k, v in row.items()} for row in csv.DictReader(handle)]
        render(read("summary.csv"), read("paired.csv"),
               json.loads((OUTPUT/"metadata.json").read_text()), checks)
        return
    if args.runs < 2 or args.budget < 2:
        parser.error("runs and budget must be at least two")
    rows, paired, metadata = simulate(args.runs, args.budget, args.seed)
    write_csv(OUTPUT/"summary.csv", rows)
    write_csv(OUTPUT/"paired.csv", paired)
    (OUTPUT/"metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    render(rows, paired, metadata, checks)


if __name__ == "__main__":
    main()
