"""Render manuscript tables and factual prose directly from geometry CSVs."""

import csv
from pathlib import Path


DIRECTORY = Path(__file__).resolve().parents[4] / "research/alignment_paper/results/geometry"


def render(directory=DIRECTORY):
    with (directory / "summary.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    results = {(row["graph"], int(row["m"]), row["policy"]): row for row in rows}
    sizes = sorted({int(row["m"]) for row in rows})
    formatted = []

    def estimate(row):
        return "${:.2f}\\pm{:.2f}$".format(float(row["mean_regret"]),
                                            float(row["ci95_halfwidth"]))

    for graph in ("path", "clique"):
        for m in sizes:
            ucb, width, profile, design = [results[graph, m, name]
                                           for name in ("ucb", "width_pool", "width_profile", "design")]
            assert ucb["mean_regret"] == width["mean_regret"]
            formatted.append("{} & {} & {} & {} & {} & {:.0f} \\\\".format(
                graph.title(), m, estimate(ucb), estimate(profile), estimate(design),
                float(design["mean_sampled_suboptimal_arms"])))
    (directory / "results_table.tex").write_text("\n".join(formatted) + "\n")
    small, large = sizes[0], sizes[-1]
    rs, rl = results["path", small, "design"], results["path", large, "design"]
    us, ul = results["path", small, "ucb"], results["path", large, "ucb"]
    cl = results["clique", large, "design"]
    paragraphs = [
        "On paths, GDE-UCB's mean final regret is {:.2f} at $m={}$ and {:.2f} at $m={}$, "
        "compared with ordinary UCB's {:.2f} and {:.2f}, respectively. "
        "At the larger size the observed UCB/GDE-UCB regret ratio is {:.2f}; "
        "at the smaller size the design overhead makes GDE-UCB worse. "
        "This finite-horizon comparison supports the predicted arm-count dependence, "
        "not a universal speedup or an optimality claim.".format(
            float(rs["mean_regret"]), small, float(rl["mean_regret"]), large,
            float(us["mean_regret"]), float(ul["mean_regret"]),
            float(ul["mean_regret"]) / float(rl["mean_regret"])),
        "GDE-UCB samples exactly two suboptimal path arms in every condition and eliminates "
        "the path in every replication. The other policies sample every suboptimal arm. "
        "On cliques, the uniform design does not eliminate the component in these runs; "
        "it samples all its arms and incurs mean regret {:.2f} at $m={}$. "
        "Thus the same policy also exposes the cost of an unhelpful design regime. "
        "The width-profile comparator remains close to ordinary UCB because the shared "
        "width certificate cannot exclude independent near-optimal alternatives.".format(
            float(cl["mean_regret"]), large),
    ]
    for m in sizes:
        path = results["path", m, "design"]
        clique = results["clique", m, "design"]
        assert float(path["mean_sampled_suboptimal_arms"]) == 2
        assert float(path["elimination_rate"]) == 1
        assert float(clique["elimination_rate"]) == 0
        for policy in ("ucb", "width_pool", "width_profile"):
            assert float(results["path", m, policy]["mean_sampled_suboptimal_arms"]) == m
    (directory / "findings.tex").write_text("\n\n".join(paragraphs) + "\n")
    with (directory / "certificate_stress.csv").open() as handle:
        stress = list(csv.DictReader(handle))
    formatted = []
    for row in stress:
        label = "Valid oracle" if row["condition"] == "valid" else "Invalid zero"
        formatted.append("{} & {} & {:.2f} & {:.4f} \\\\".format(
            label, row["horizon"], float(row["mean_regret"]), float(row["regret_per_round"])))
    (directory / "stress_table.tex").write_text("\n".join(formatted) + "\n")
    print("Rendered geometry tables and findings from", directory)


if __name__ == "__main__":
    render()
