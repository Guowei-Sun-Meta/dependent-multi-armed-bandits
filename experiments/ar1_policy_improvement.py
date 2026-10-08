"""Evaluate a model-derived long-horizon knowledge-gradient policy.

Reuse the original exogenous seeds and compare against saved baseline runs.
There is no fitted multiplier: the lifetime is phi / (1 - phi).
    python3 experiments/ar1_policy_improvement.py --verify
    python3 experiments/ar1_policy_improvement.py
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import json
import math

import predictive_ar1 as base


DIRECTORY = base.DEFAULT_OUTPUT / "policy_improvement"


def load_csv(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))


def verify():
    case = base.make_cases()[4]
    prepared = base.prepare_case(case, 100, 0)
    policy = base.BeliefPolicy("long_kg", prepared, 7)
    policy.predictions = [0.8, 0.0, -0.3, 0.1, 0.2]
    policy.ages = [1, 20, 3, 10, 4]
    phi = case["phis"][0]
    for i in range(5):
        m = policy.predictions
        v = prepared["lookup"][i]["variance"][policy.ages[i]]
        competitor = max(m[j] for j in range(5) if j != i)
        kg = base.expected_positive(-abs(m[i] - competitor), math.sqrt(v))
        direct = 0.0
        for s in range(1, 4001):
            retention = phi**s
            c = retention * competitor
            after_observation = c + base.expected_positive(retention * (m[i] - competitor), retention * math.sqrt(v))
            direct += after_observation - retention * max(m)
        assert math.isclose(direct, phi / (1 - phi) * kg, abs_tol=1e-10)
    # Check that adding or removing other policies leaves baseline trajectories unchanged.
    both = base.simulate_run(prepared, 100, 0, 0, ("ps", "long_kg"))[0]
    single = base.simulate_run(prepared, 100, 0, 0, ("ps",))[0]
    first = next(row for row in both if row["policy"] == "ps")
    second = next(row for row in single if row["policy"] == "ps")
    assert first == second
    print("Verified geometric information value and invariance of paired baseline trajectories.")


def render(rows, curves, baseline, metadata):
    comparison, pairs, table = [], [], []
    old = {(row["case"], int(row["run"]), row["policy"]): row for row in baseline}
    for case in sorted(metadata["cases"], key=lambda item: item["phis"][0]):
        name, phi = case["name"], case["phis"][0]
        chosen = [row for row in rows if row["case"] == name and row["policy"] == "long_kg"]
        rate, ci = base.estimate([float(row["coefficient"]) for row in chosen])
        tail, tail_ci = base.estimate([float(row["tail_coefficient"]) for row in chosen])
        ps, ps_ci = base.estimate([float(old[name, int(row["run"]), "ps"]["coefficient"]) for row in chosen])
        greedy, _ = base.estimate([float(old[name, int(row["run"]), "greedy"]["coefficient"]) for row in chosen])
        two_step, two_step_ci = base.estimate([float(old[name, int(row["run"]), "two_step"]["coefficient"]) for row in chosen])
        improvement, paired_ci = base.estimate([float(old[name, int(row["run"]), "ps"]["coefficient"]) - float(row["coefficient"]) for row in chosen])
        comparison.append({"case": name, "phi": phi, "long_kg": rate, "ci95_halfwidth": ci,
                           "tail_coefficient": tail, "tail_ci95_halfwidth": tail_ci,
                           "ps": ps, "ps_ci": ps_ci, "greedy": greedy,
                           "two_step": two_step, "two_step_ci": two_step_ci,
                           "ps_minus_long_kg": improvement, "paired_ci": paired_ci})
        table.append(f"{phi:g} & {greedy:.4f} & ${two_step:.4f}\\pm{two_step_ci:.4f}$ & ${ps:.4f}\\pm{ps_ci:.4f}$ & "
                     f"${rate:.4f}\\pm{ci:.4f}$ & ${improvement:.4f}\\pm{paired_ci:.4f}$" + r" \\")
        for baseline_name in ("ps", "greedy", "ts", "two_step"):
            differences = [float(old[name, int(row["run"]), baseline_name]["coefficient"]) - float(row["coefficient"]) for row in chosen]
            mean, width = base.estimate(differences)
            pairs.append({"case": name, "baseline": baseline_name,
                          "baseline_minus_long_kg": mean, "ci95_halfwidth": width})
    base.write_csv(DIRECTORY / "comparison.csv", comparison)
    base.write_csv(DIRECTORY / "paired.csv", pairs)
    base.write_csv(DIRECTORY / "runs.csv", rows)
    base.write_csv(DIRECTORY / "curves.csv", curves)
    (DIRECTORY / "results_table.tex").write_text("\n".join(table) + "\n")
    lines = ["# Long-horizon knowledge-gradient comparison", "",
             "The multiplier φ/(1−φ) is derived from retaining one new observation and ignoring "
             "subsequent feedback in the continuation calculation. It is not tuned to these results. "
             "This approximation does not solve the full Bellman equation.", "",
             f"Matched to the original {metadata['runs']} runs, {metadata['burn']:,}-round burn-in, "
             f"and {metadata['horizon']:,} measured rounds. Common means zero and stationary variance one.", "",
             "| φ | Greedy | Two-step | Predictive Sampling | Long-horizon KG | PS minus KG (paired) |",
             "|---|---|---|---|---|---|"]
    for row in comparison:
        lines.append(f"| {row['phi']:g} | {row['greedy']:.4f} | {row['two_step']:.4f} ± {row['two_step_ci']:.4f} | {row['ps']:.4f} ± {row['ps_ci']:.4f} | "
                     f"{row['long_kg']:.4f} ± {row['ci95_halfwidth']:.4f} | "
                     f"{row['ps_minus_long_kg']:.4f} ± {row['paired_ci']:.4f} |")
    lines.extend(["", "Positive paired differences favor long-horizon KG. Intervals are approximate 95% "
                  "intervals over independent replications. Homogeneous positive-persistence models only; "
                  "these comparisons do not certify an optimal long-run coefficient.", "",
                  "The lifetime-weighted rule improves on PS at moderate persistence but loses at φ=0.99 "
                  "and 0.995. Two-step control is strongest among these tested policies at φ=0.9; PS is "
                  "strongest at 0.99 and 0.995. The one-observation continuation ignores future feedback, "
                  "so its geometric information value is an approximation when used repeatedly."])
    (DIRECTORY / "findings.md").write_text("\n".join(lines) + "\n")
    representative = next(row for row in comparison if row["phi"] == 0.99)
    verb = "lower" if representative["long_kg"] < representative["ps"] else "higher"
    (DIRECTORY / "findings.tex").write_text(
        "At $\\phi=0.99$, long-horizon KG has measured coefficient "
        f"${representative['long_kg']:.4f}\\pm{representative['ci95_halfwidth']:.4f}$, "
        f"{verb} than PS's ${representative['ps']:.4f}\\pm{representative['ps_ci']:.4f}$. "
        "This is a paired comparison on the same exogenous trajectories. "
        "It does not establish optimality of either policy.\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--render-only", action="store_true", help="Regenerate tables from saved runs.")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.verify:
        verify()
        return
    protocol = json.loads((base.DEFAULT_OUTPUT / "metadata.json").read_text())
    baseline = load_csv(base.DEFAULT_OUTPUT / "runs.csv")
    if args.render_only:
        render(load_csv(DIRECTORY / "runs.csv"), load_csv(DIRECTORY / "curves.csv"), baseline,
               json.loads((DIRECTORY / "metadata.json").read_text()))
        return
    cases = [case for case in base.make_cases() if case["name"].startswith("homogeneous")]
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    rows, curves, case_metadata = [], [], []
    # First replication verifies exact replay against the saved baseline data.
    check_case = base.prepare_case(cases[-1], protocol["horizon"], protocol["burn"])
    replay = base.simulate_run(check_case, protocol["horizon"], protocol["burn"], 0, ("ps",))[0][0]
    saved = next(row for row in baseline if row["case"] == check_case["name"] and int(row["run"]) == 0 and row["policy"] == "ps")
    assert replay["regret"] == float(saved["regret"]) and replay["counts"] == saved["counts"]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        pending = [executor.submit(base.run_case, case, protocol["horizon"], protocol["burn"], protocol["runs"], ("long_kg",)) for case in cases]
        for future in as_completed(pending):
            meta, a, b = future.result()
            case_metadata.append(meta)
            rows.extend(a)
            curves.extend(b)
            print("Finished", meta["name"], flush=True)
    metadata = {"runs": protocol["runs"], "horizon": protocol["horizon"], "burn": protocol["burn"],
                "cases": case_metadata, "parameter_fitting": False,
                "baseline_replay_verified": True, "lifetime_multiplier": "phi/(1-phi)"}
    (DIRECTORY / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    render(rows, curves, baseline, metadata)
    print("Saved policy comparison to", DIRECTORY)


if __name__ == "__main__":
    main()
