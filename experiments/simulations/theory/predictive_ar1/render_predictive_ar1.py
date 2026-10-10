"""Render AR(1) coefficient comparisons directly from saved experiment outputs."""

import csv
from html import escape
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DIRECTORY = ROOT / "research" / "predictive_ar1" / "results"
LABELS = {"fixed": "Fixed arm", "greedy": "Greedy", "ts": "Thompson",
          "ps": "Predictive Sampling", "two_step": "Two-step", "refresh": "Refresh",
          "past_state_genie": "All-past-state observer"}
COLORS = {"greedy": "#009e73", "ts": "#d55e00", "ps": "#0072b2", "two_step": "#cc79a7"}


def read_csv(name):
    with (DIRECTORY / name).open() as handle:
        return list(csv.DictReader(handle))


def interval(row, scale=1.0):
    return f"{scale * float(row['coefficient']):.4f} ± {scale * float(row['ci95_halfwidth']):.4f}"


def svg_plot(path, title, subtitle, rows, x_field, y_fields, x_max, y_max, x_label,
             logarithmic=False):
    width, height = 1050, 565
    left, top, plot_width, plot_height = 85, 115, 860, 340
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
              f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
              '<rect width="100%" height="100%" fill="white"/>',
              '<g font-family="Arial, sans-serif" fill="#172b4d">']

    def text(x, y, value, size=15, anchor="start", extra=""):
        pieces.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
                      f'{extra}>{escape(value)}</text>')

    def line(x1, y1, x2, y2, color="#dce3ea", dash=False, stroke=1):
        pieces.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                      f'stroke="{color}" stroke-width="{stroke}" '
                      + ('stroke-dasharray="6 4"' if dash else '') + '/>')

    def xp(x):
        fraction = math.log10(x) / math.log10(x_max) if logarithmic else x / x_max
        return left + fraction * plot_width

    def yp(y):
        return top + plot_height * (1 - y / y_max)

    text(35, 34, title, 24)
    text(35, 62, subtitle, 15)
    for tick in range(6):
        y = y_max * tick / 5
        line(left, yp(y), left + plot_width, yp(y))
        text(left - 10, yp(y) + 5, f"{y:.2f}" if logarithmic else f"{y / 1000:.0f}k", anchor="end")
    x_ticks = (1, 2, 10, 100, 200) if logarithmic else (0, 10000, 20000, 30000)
    for x in x_ticks:
        line(xp(x), top, xp(x), top + plot_height)
        text(xp(x), top + plot_height + 25, f"{x:g}" if logarithmic else f"{x / 1000:.0f}k", anchor="middle")
    text(left + plot_width / 2, 510, x_label, 16, "middle")
    ylabel = "Expected regret per round" if logarithmic else "Cumulative oracle regret"
    text(22, top + plot_height / 2, ylabel, 16, "middle",
         f'transform="rotate(-90 22 {top + plot_height / 2})"')
    for field, label, color, dash in y_fields:
        ordered = sorted(rows, key=lambda row: row[x_field])
        points = " ".join(f"{xp(row[x_field]):.2f},{yp(row[field]):.2f}" for row in ordered)
        pieces.append(f'<polyline points="{points}" fill="none" stroke="{color}" '
                      f'stroke-width="2.6" ' + ('stroke-dasharray="6 4"' if dash else '') + '/>')
        if not dash:
            for row in ordered:
                x, y = xp(row[x_field]), yp(row[field])
                pieces.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{color}"/>')
                if logarithmic:
                    ci = row[field + "_ci"]
                    line(x, yp(row[field] - ci), x, yp(row[field] + ci), color)
        j = [item[0] for item in y_fields].index(field)
        x, y = 88 + (j % 3) * 292, 87 + (j // 3) * 19
        line(x, y, x + 25, y, color, dash, 2.6)
        text(x + 32, y + 5, label, 14)
    text(35, 547, "Synthetic known-parameter experiments; uncertainty intervals across independent runs.", 14)
    pieces.append("</g></svg>")
    path.write_text("\n".join(pieces) + "\n")


def main():
    metadata = json.loads((DIRECTORY / "metadata.json").read_text())
    summaries, trajectories, pairs = [read_csv(name) for name in ("summary.csv", "curves.csv", "paired.csv")]
    index = {(row["case"], row["policy"]): row for row in summaries}
    cases = sorted((case for case in metadata["cases"] if case["name"].startswith("homogeneous")),
                   key=lambda case: case["phis"][0])
    rows, table = [], []
    findings = ["# Full-state oracle regret: generated results", "",
                f"{metadata['runs']} independent runs per case; {metadata['burn']:,} burn-in rounds followed by "
                f"{metadata['horizon']:,} measured rounds. All parameters are known. Values are measured "
                "regret per round with approximate 95% intervals across runs.", "",
                "| φ | Lower bound | Greedy | Thompson | Predictive Sampling | Two-step | Refresh |",
                "|---|---|---|---|---|---|---|"]
    for case in cases:
        name, phi = case["name"], case["phis"][0]
        selected = [index[name, policy] for policy in ("greedy", "ts", "ps", "two_step", "refresh")]
        findings.append(f"| {phi:g} | {case['full_past_lower_bound']:.4f} | "
                        + " | ".join(interval(row) for row in selected) + " |")
        table.append(f"{phi:g} & {case['full_past_lower_bound']:.4f} & "
                     + " & ".join(f"${float(row['coefficient']):.4f}\\pm{float(row['ci95_halfwidth']):.4f}$"
                                  for row in selected) + r" \\")
        row = {"phi": phi, "memory": 1 / (1 - phi), "lower": case["full_past_lower_bound"],
               "blind": case["blind_coefficient"], "refresh_bound": case["refresh_bound"]}
        for policy in ("greedy", "ts", "ps", "two_step"):
            row[policy] = float(index[name, policy]["coefficient"])
            row[policy + "_ci"] = float(index[name, policy]["ci95_halfwidth"])
        rows.append(row)
    (DIRECTORY / "results_table.tex").write_text("\n".join(table) + "\n")
    with (DIRECTORY / "coefficient_plot.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    name = "homogeneous_0.99"
    ps, ts, greedy, lookahead = [index[name, p] for p in ("ps", "ts", "greedy", "two_step")]
    reduction = 100 * (1 - float(ps["coefficient"]) / float(ts["coefficient"]))
    scale = math.sqrt(1e-4 / (1 - 0.99**2))
    selected_case = next(case for case in cases if case["name"] == name)
    paragraphs = [
        f"At φ=0.99, Predictive Sampling has coefficient {interval(ps)}, compared with "
        f"Thompson {interval(ts)}, greedy {interval(greedy)}, and two-step {interval(lookahead)}. "
        f"The point-estimate reduction relative to Thompson is {reduction:.1f}%.",
        f"For the same φ with innovation variance 10^-4, exact scaling gives the PS coefficient "
        f"{interval(ps, scale)}. The universal lower bound is "
        f"{scale * selected_case['full_past_lower_bound']:.6f}; the fixed-arm coefficient is "
        f"{scale * selected_case['blind_coefficient']:.6f}. These scaled values are not a separate simulation.",
    ]
    findings.extend(["", *paragraphs, "", "## Paired comparisons", "",
                     "Positive baseline-minus-PS values favor PS. Intervals use differences within each "
                     "shared-trajectory run; comparison is at the measured horizon.", "",
                     "| Case | Baseline | Baseline minus PS |", "|---|---|---|"])
    for row in pairs:
        if row["case"] in (name, "homogeneous_0.995", "fast_noise_decoy"):
            findings.append(f"| {row['case']} | {LABELS[row['baseline']]} | "
                            f"{float(row['baseline_minus_ps']):.4f} ± {float(row['ci95_halfwidth']):.4f} |")

    findings.extend(["", "## High-variance white-noise arm", "",
                     "Four zero-mean arms have φ=0.99 and stationary variance one. The fifth has mean "
                     "0.2, φ=0, and stationary variance four. Its current state cannot be predicted from past rewards.",
                     "", "| Policy | Regret per round | Fraction selecting white-noise arm |", "|---|---|---|"])
    for policy in ("fixed", "greedy", "ts", "ps", "two_step", "past_state_genie"):
        row = index["fast_noise_decoy", policy]
        findings.append(f"| {LABELS[policy]} | {interval(row)} | {float(row['last_arm_fraction']):.3f} |")

    findings.extend(["", "## Horizon sensitivity", "",
                     "These are coefficient estimates after the same burn-in, using different lengths of "
                     "the measured trajectory. They assess finite-horizon stability, not convergence of a limiting coefficient.",
                     "", "| φ=0.99 policy | 10,000 rounds | 20,000 rounds | 30,000 rounds | Final 10,000 rounds |",
                     "|---|---|---|---|---|"])
    curve_index = {(row["case"], row["policy"], int(row["t"])): row for row in trajectories}
    for policy in ("greedy", "ts", "ps", "two_step"):
        row = index[name, policy]
        horizons = [h for h in (10000, 20000, 30000) if h <= metadata["horizon"]]
        values = [f"{float(curve_index[name, policy, h]['coefficient']):.4f}" for h in horizons]
        findings.append(f"| {LABELS[policy]} | " + " | ".join(values)
                        + f" | {float(row['tail_coefficient']):.4f} ± {float(row['tail_ci95_halfwidth']):.4f} |")
    findings.extend(["", "The observed ranking is not a proof that Predictive Sampling or two-step control minimizes "
                     "the long-run coefficient. Parameters are supplied; noisy observations and parameter learning are not evaluated.",
                     "", "![Coefficient versus memory](coefficients.svg)", "",
                     "![Cumulative regret at φ=0.99](cumulative.svg)"])
    (DIRECTORY / "findings.md").write_text("\n".join(findings) + "\n")

    decoy_ps, decoy_ts = [index["fast_noise_decoy", p] for p in ("ps", "ts")]
    tex_paragraphs = [
        "With $\\phi=0.99$, Predictive Sampling has measured regret per round "
        f"${float(ps['coefficient']):.4f}\\pm{float(ps['ci95_halfwidth']):.4f}$, compared with "
        f"Thompson Sampling's ${float(ts['coefficient']):.4f}\\pm{float(ts['ci95_halfwidth']):.4f}$, "
        f"greedy predictions' ${float(greedy['coefficient']):.4f}\\pm{float(greedy['ci95_halfwidth']):.4f}$, "
        f"and two-step control's ${float(lookahead['coefficient']):.4f}\\pm{float(lookahead['ci95_halfwidth']):.4f}$. "
        f"The point estimate is {reduction:.1f}\\% lower than Thompson Sampling's. "
        "This comparison is empirical and does not establish an optimal policy.",
        "For $\\phi=0.99$ and innovation variance $q=10^{-4}$, scale equivariance gives a PS coefficient "
        f"${scale * float(ps['coefficient']):.6f}\\pm{scale * float(ps['ci95_halfwidth']):.6f}$, "
        f"a lower bound ${scale * selected_case['full_past_lower_bound']:.6f}$, and a fixed-arm coefficient "
        f"${scale * selected_case['blind_coefficient']:.6f}$. This is a rescaling, not an independent experiment.",
        "In the white-noise-arm case, PS has coefficient "
        f"${float(decoy_ps['coefficient']):.4f}\\pm{float(decoy_ps['ci95_halfwidth']):.4f}$ and Thompson "
        f"${float(decoy_ts['coefficient']):.4f}\\pm{float(decoy_ts['ci95_halfwidth']):.4f}$. "
        f"They select the white-noise arm in {100 * float(decoy_ps['last_arm_fraction']):.1f}\\% and "
        f"{100 * float(decoy_ts['last_arm_fraction']):.1f}\\% of measured rounds, respectively.",
    ]
    # Explicitly report any stronger comparator; avoid implying PS wins universally.
    better = [(p, float(index[name, p]["coefficient"])) for p in ("greedy", "two_step", "refresh")
              if float(index[name, p]["coefficient"]) < float(ps["coefficient"])]
    if better:
        tex_paragraphs.append("At this persistence, the point estimates of "
                              + ", ".join(LABELS[p] for p, _ in better)
                              + " are lower than PS. Predictive randomization should therefore be treated as "
                              "a candidate rather than an optimizer of the linear coefficient.")
    (DIRECTORY / "findings.tex").write_text("\n\n".join(tex_paragraphs) + "\n")

    svg_plot(DIRECTORY / "coefficients.svg", "The coefficient of linear regret decreases with temporal memory",
             f"Five arms; stationary variance 1; {metadata['runs']} runs × {metadata['horizon']:,} measured rounds; 95% intervals",
             rows, "memory", [(p, LABELS[p], COLORS[p], False) for p in COLORS]
             + [("blind", "Fixed-arm coefficient", "#666666", True),
                ("lower", "Universal lower bound", "#111111", True)],
             240, 1.3, "Memory scale 1 / (1 − φ), logarithmic axis", logarithmic=True)

    trajectory_rows = []
    for t in sorted({int(row["t"]) for row in trajectories if row["case"] == name}):
        row = {"t": t}
        for policy in COLORS:
            row[policy] = float(curve_index[name, policy, t]["mean_regret"])
        row["blind"] = selected_case["blind_coefficient"] * t
        row["lower"] = selected_case["full_past_lower_bound"] * t
        trajectory_rows.append(row)
    with (DIRECTORY / "cumulative_plot.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(trajectory_rows[0]))
        writer.writeheader()
        writer.writerows(trajectory_rows)
    svg_plot(DIRECTORY / "cumulative.svg", "Cumulative regret remains linear: φ = 0.99",
             "Each policy sees one arm per round; the oracle sees all current states",
             trajectory_rows, "t", [(p, LABELS[p], COLORS[p], False) for p in COLORS]
             + [("blind", "Fixed-arm expectation", "#666666", True),
                ("lower", "Universal lower bound", "#111111", True)],
             metadata["horizon"], 1.05 * selected_case["blind_coefficient"] * metadata["horizon"],
             "Measured rounds after burn-in")
    print("Rendered tables, findings, and figures from", DIRECTORY)


if __name__ == "__main__":
    main()
