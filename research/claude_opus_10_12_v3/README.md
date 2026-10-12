# When Can a Bandit Trust Correlation? Revision 3

12 October 2026. This revision updates [revision 2](../claude_opus_10_09_v2/README.md) with every experiment run on 10–11 October. Revision 2 is kept unchanged for comparison.

| Item | What it is |
| --- | --- |
| [paper/paper.pdf](paper/paper.pdf) ([source](paper/paper.tex)) | The long working paper, 23 pages, still organized around four questions |
| [figures/](figures) | Revision 2's figures (`f*`), plus five cross-experiment figures (`r*`) from [experiments/report](../../experiments/report/README.md) |

The evidence behind every number is in [experiments/report](../../experiments/report/README.md). That report maps each theory result to its tests and gives a verdict.

## What changed from revision 2

| Area | Revision 2 | Revision 3 |
| --- | --- | --- |
| Q2 certified pooling | 60 users (Setting A v1), 60 instances (v2); per-instance dose-response with UCB1 | 360 instances, with both summaries (ratio of means and mean of ratios). The dose-response holds across certificates (Spearman −0.87) and replicates on the Open Bandit Dataset (−0.81). The per-instance link is weak (−0.09) |
| Q2 structure | "Average gains are shrinkage" | Real graphs beat rewired nulls only under certification: 0.916 [0.905, 0.926]. Graph-free empirical-Bayes shrinkage is the best average policy |
| Q2 second platform | — | Open Bandit Dataset (semi-synthetic, real click rates): the three predictions replicate |
| Q3 estimated dynamics | Not tested | Valid with a long prefix. A 100-round prefix gives 13% violations; a missed weekly lag gives 23–73% |
| Q3 real dynamics | Toy only | Real Wikipedia inflation is 3.6–5.3× for 7-day blocks, predicted by full-ACF fits. On Wikipedia-calibrated worlds, iid certificates fail in 56–95% of runs and innovation certificates hold (0–1%) |
| Q3 cost of validity | "Comparable regret" | Valid but too wide at Web persistence: widths are 10–25× the information limit. Valid elimination never acts |
| Q3 B2 consequence | Toy, 20 seeds | 100 worlds per cell: 28–89% best-arm drops under bursty exposure, then linear regret. The invalid rule still has lower total regret at T = 20,000 |
| B3 slate | (1 − ρ) | General long-run contrast formula, checked exactly. Staggered observations keep the gain under persistence |
| Q4 KuaiRec | Retrospective panel (look-ahead graph, survivor cohort): −38% against iid TS | Chronological panel with standard baselines: −49% to −54%, but the last observed value ties the filter |
| Q4 Wikipedia | Main real-data evidence | Flagged as retrospective; the parallel chronological study is summarized (panel-dependent) |
| Q4 Open Bandit Dataset | — | No persistence to exploit |
| Open problems | A narrow mean-channel certificate | First: a tighter anytime-valid certificate under correlated persistent shocks |

## Compile

The PDF was built with tectonic 0.15. This machine has no system TeX, so a standalone binary was used. From `research/claude_opus_10_12_v3/paper`:

```sh
tectonic -X compile paper.tex
```
