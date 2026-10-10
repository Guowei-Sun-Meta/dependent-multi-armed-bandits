"""Render exact AR(1) formula illustrations using the standard library.

Run from any directory: python3 experiments/simulations/theory/temporal_information/temporal_information.py
Stationary variance is fixed at one, so innovation variance is 1 - phi**2.
The mean-information fraction is a large-sample consecutive-observation formula,
not a regret bound or an adaptive-sampling confidence guarantee.
"""

import csv
import math
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[4]
COLORS = ("#0072b2", "#d55e00", "#009e73")
PHIS = (0.2, 0.8, 0.95)


def check_identities():
    for phi in (-0.7, 0.0, 0.2, 0.8, 0.95):
        q = 1 - phi * phi
        for age in (1, 2, 5, 25):
            geometric = q * sum(phi ** (2 * j) for j in range(age))
            closed = 1 - phi ** (2 * age)
            assert math.isclose(geometric, closed, rel_tol=1e-12)
            direct_kl = (1 - phi**age) ** 2 / (2 * geometric)
            reduced_kl = (1 - phi**age) / (2 * (1 + phi**age))
            assert math.isclose(direct_kl, reduced_kl, rel_tol=1e-12)
        # Independent covariance-sum calculation of n Var(sample mean), V=1.
        n = 100_000
        finite = 1 + 2 * sum((1 - lag / n) * phi**lag for lag in range(1, 2_000))
        limiting = (1 + phi) / (1 - phi)
        assert abs(finite / limiting - 1) < 0.001


def render():
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="490" '
        'viewBox="0 0 1200 490" role="img" aria-labelledby="title desc">',
        '<title id="title">Two effects of persistence in an AR(1) process</title>',
        '<desc id="desc">At fixed stationary variance, higher positive persistence '
        'slows forecast uncertainty growth but reduces the asymptotic effective '
        'sample fraction for estimating the mean from consecutive observations.</desc>',
        '<rect width="1200" height="490" fill="white"/>',
        '<g font-family="Arial, sans-serif" fill="#172b4d">',
    ]

    def label(x, y, value, size=15, anchor="start", extra=""):
        pieces.append(f'<text x="{x}" y="{y}" font-size="{size}" '
                      f'text-anchor="{anchor}" {extra}>{escape(value)}</text>')

    def line(x1, y1, x2, y2, color="#dce3ea", width=1):
        pieces.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                      f'stroke="{color}" stroke-width="{width}"/>')

    label(40, 31, "Persistence preserves forecasts and slows mean estimation", 24)
    label(40, 57, "Stationary variance V = 1; innovation variance q = 1 − φ²; exact state observations", 16)
    panels = ((85, 122, 465, 275, 25), (680, 122, 465, 275, 1))
    label(85, 100, "Forecast uncertainty after an observation", 19)
    label(680, 100, "Mean information in consecutive samples", 19)

    for index, (left, top, width, height, xmax) in enumerate(panels):
        for tick in range(6):
            fraction = tick / 5
            y = top + height * (1 - fraction)
            line(left, y, left + width, y)
            label(left - 10, y + 5, f"{fraction:.1f}", anchor="end")
            x = left + width * fraction
            line(x, top, x, top + height)
            label(x, top + height + 24,
                  str(int(fraction * xmax)) if index == 0 else f"{fraction:.1f}",
                  anchor="middle")
        line(left, top, left, top + height, "#66788a")
        line(left, top + height, left + width, top + height, "#66788a")
        label(left + width / 2, top + height + 49,
              "Age h since last observation" if index == 0 else "Persistence φ",
              16, "middle")
        ylabel = "Forecast variance / V" if index == 0 else "Asymptotic effective sample fraction"
        label(left - 51, top + height / 2, ylabel, 15, "middle",
              f'transform="rotate(-90 {left - 51} {top + height / 2})"')

    for phi, color in zip(PHIS, COLORS):
        left, top, width, height, xmax = panels[0]
        points = []
        for step in range(501):
            age = 25 * step / 500
            ratio = 1 - phi ** (2 * age)
            points.append(f"{left + width * age / xmax:.2f},{top + height * (1 - ratio):.2f}")
        pieces.append(f'<polyline points="{" ".join(points)}" fill="none" '
                      f'stroke="{color}" stroke-width="3"/>')
        legend_x = 112 + PHIS.index(phi) * 132
        line(legend_x, 158, legend_x + 25, 158, color, 3)
        label(legend_x + 32, 163, f"φ = {phi}", 15)

    left, top, width, height, xmax = panels[1]
    points = []
    for step in range(501):
        phi = step / 500
        ratio = (1 - phi) / (1 + phi)
        points.append(f"{left + width * phi:.2f},{top + height * (1 - ratio):.2f}")
    pieces.append(f'<polyline points="{" ".join(points)}" fill="none" '
                  'stroke="#576b85" stroke-width="3"/>')
    for phi, color in zip(PHIS, COLORS):
        ratio = (1 - phi) / (1 + phi)
        x, y = left + width * phi, top + height * (1 - ratio)
        pieces.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/>')
        label(x - 9, y - 12, f"φ = {phi}", 14, "end")

    label(318, 475, "v(h) / V = 1 − φ²ʰ", 17, "middle")
    label(913, 475, "n_eff / n ≈ (1 − φ) / (1 + φ)", 17, "middle")
    pieces.append("</g></svg>")
    destination = ROOT / "research" / "temporal_information.svg"
    destination.write_text("\n".join(pieces) + "\n", encoding="utf-8")

    with (ROOT / "research" / "temporal_information.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("phi", "age", "forecast_variance_over_stationary_variance",
                         "asymptotic_effective_sample_fraction"))
        for phi in PHIS:
            for age in range(26):
                writer.writerow((phi, age, 1 - phi ** (2 * age), (1 - phi) / (1 + phi)))
    print(f"Checked AR(1) identities and wrote {destination}")


if __name__ == "__main__":
    check_identities()
    render()
