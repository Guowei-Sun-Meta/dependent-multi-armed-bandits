# When Can a Bandit Trust Correlation? Revision 2 of the Compiled Findings

9 October 2026. A rewrite of [claude_opus_10_09](../claude_opus_10_09/README.md) with a clearer story, deeper analysis of every experiment, explicit links between each theoretical result and the data that tests it, and a hypothesis-driven second application. The first version is kept unchanged for comparison.

| Item | What it is |
| --- | --- |
| [paper/paper.pdf](paper/paper.pdf) ([source](paper/paper.tex)) | The long working paper, organized around four questions |
| [analysis/](analysis) | Theory-to-data analyses, each a CSV plus a markdown table (`experiments/paper/deepdive.py`) |
| [figures/](figures) | One figure per bridge (`experiments/paper/paper_figures_v2.py`) |
| [experiments/wikipedia](../../experiments/wikipedia/README.md#panel-2-six-communities) | The new application: Wikipedia attention across six communities (moved to `experiments/` on 10 October) |
| [experiments/](../../experiments/README.md) | Design, code, results and report of every experiment in the paper |

## What changed from version 1

| Area | Version 1 | Version 2 |
| --- | --- | --- |
| Organization | Theory sections, then experiment sections | Four questions; each runs theory → testable prediction → evidence → answer |
| Theory–data link | Results reported next to the theory | Each theorem yields a named prediction that is tested quantitatively (table below) |
| Second application | Wikipedia, one domain: graph adds nothing | Diagnosed why (one domain shares one rhythm), then designed a six-community panel. Hyperlinks carry community shocks there |
| Deep dives | Averages per policy | Mechanisms: which instances certified pooling helps, which users uncertified pooling fails and why, where Wikipedia regret comes from, what KuaiRec's drift is |
| Corrections | "Drift grows with video age" | KuaiRec is one upload cohort whose engagement falls during days 21–42. Younger videos change faster early on, but drift does not grow with age |

## Each prediction and its test

| Prediction (from theory) | Test | Result |
| --- | --- | --- |
| Certified pooling gains only through components with width below gap (SP-UCB theorem) | Setting A: gain against the share of rejectable components | Median ratio to UCB1 falls from 0.84 to 0.40 as the share rises (Spearman −0.48). Energy certificates rarely make components rejectable and gain only 2–11% |
| Zero-width pooling fails when the optimal component is not the top component by average | Recompute every instance's partition | Safe when it is top (90th pct 0.37× UCB1); fails when not (90th pct 1.19×). Never fails on rewired graphs, up to 38% on informative ones |
| iid certificates under bursty persistence miscover by B2's inflation | Coverage sweeps, blocks of 25 | Predicted inflation 1.7× / 3.5× / 4.4× at φ = 0.5 / 0.9 / 0.97; runs violated 0% / 85% / 90–95% |
| Innovation certificates (B1, B1′, B1″) stay valid | Same sweeps, several thousand runs | Never violated |
| Exploring persistent uncertainty pays only with enough future observations per arm | Five environments | Refined: heavy exploration (predictive sampling) beats greedy with many observations and clear gaps (0.63× benchmark, 0.92× one-domain Wikipedia), but loses with near-ties or about 1 observation per arm (1.11×, 1.67–1.74×). Mild optimism (UCB, 1 sd) helps where rankings move (0.91× six-domain Wikipedia, sparse KuaiRec) |
| A graph helps the shock model only when shocks are community-specific | Shock correlation and held-out likelihood on three panels; paired policy runs | No help on KuaiRec or one-domain Wikipedia. On six domains hyperlinks fit shocks best (edges 0.273 against rewired 0.051), but change decisions by only ±3%, because long-run levels decide which articles lead |
| Modelling dynamics beats iid policies | Five environments | Best model 24–44% below iid Thompson sampling everywhere |

## Reproduce

From the repository root, after the experiments listed in the paper's appendix:

```sh
OPENBLAS_NUM_THREADS=2 .venv/bin/python -I experiments/paper/deepdive.py
.venv/bin/python -I experiments/paper/paper_figures_v2.py
cd research/claude_opus_10_09_v2/paper && tectonic paper.tex
```
