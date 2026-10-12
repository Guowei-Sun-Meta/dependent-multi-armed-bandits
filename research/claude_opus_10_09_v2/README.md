# When Can a Bandit Trust Correlation? Updated Working Draft

Updated 12 October 2026 (revision 3, in the existing revision-2 folder). The [paper](paper/paper.pdf) and [source](paper/paper.tex) incorporate the completed 10--11 October experiments. Both this draft and the [extended synthesis](../gpt_sol_10_09/manuscript.pdf) include a [shared results section](../../experiments/report_2026_10_11/paper/latest_results.tex), seven generated tables and five new figures. The original draft remains in [claude_opus_10_09](../claude_opus_10_09/README.md).

Current headlines: oracle-certified I-mf pooling has average regret 0.640 times matched conservative KL-UCB but 1.456 times Bernoulli TS; graph-free shrinkage explains much of spectral performance. Chronological KuaiRec gains against iid TS do not establish superiority over last value. Full-year Wikipedia gains depend on panel and budget. Known-model confidence is conditional; fitted-model coverage and useful elimination remain unresolved. OBD mean-channel simulations and the underpowered actual-log pilot are reported separately.

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

## Updated predictions and tests

| Prediction (from theory) | Test | Result |
| --- | --- | --- |
| Certified pooling gains only through components with width below gap (SP-UCB theorem) | Setting A: gain against the share of rejectable components | Median ratio to UCB1 falls from 0.84 to 0.40 as the share rises (Spearman −0.48). Energy certificates rarely make components rejectable and gain only 2–11% |
| Incorrect widths can cause dilution failures | Static KuaiRec, cold users and OBD | Heavy tails and failure to identify the best item occur in selected settings; no sample with zero failures establishes safety for all random graphs |
| iid certificates under bursty persistence miscover by B2's inflation | Coverage sweeps, blocks of 25 | Predicted inflation 1.7× / 3.5× / 4.4× at φ = 0.5 / 0.9 / 0.97; runs violated 0% / 85% / 90–95% |
| Correct-model innovation confidence has conditional guarantees | Fresh general-AR confirmation and real-calibrated worlds | Known AR(20): 1/100 failures; fitted: 5/100; wrong order plus diagonal covariance: 40/100. Conservative elimination can retain all arms |
| The value of predictive exploration depends on continuation information, gaps and initialization | Legacy five-environment analysis | Performance varies across settings; these retrospectively selected panels motivate hypotheses rather than a general exploration rule |
| Better shock fit need not improve decisions | Historical covariance diagnostics and current topology controls | Legacy six-domain hyperlinks fit shocks better, but chronological KuaiRec and historical small-panel Wikipedia do not establish a real-topology advantage over appropriate controls |
| Persistence-aware rules can improve on iid policies | Chronological KuaiRec and full-year historical Wikipedia | KuaiRec joint UCB is 49–54% below iid TS, but comparisons with last value are inconclusive. Wikipedia is panel- and budget-dependent |

The older five-environment exploration analysis and retrospective shock-correlation diagnostics remain historical context, not a universal algorithm claim. Primary performance in the updated section uses ratios of mean losses and user-level uncertainty; legacy tables that average instance ratios are explicitly labelled. Empirical residual resampling has a nonzero-mean audit qualification, and practical calibration diagnostics are not simultaneous coverage guarantees.

## Reproduce

From the repository root, after the experiments listed in the paper's appendix:

Generate the latest shared tables with `.venv/bin/python -I experiments/report_2026_10_11/paper/build_latest.py`, then compile the draft. The generated input fingerprints are in `experiments/report_2026_10_11/paper/source_manifest.json`.

```sh
OPENBLAS_NUM_THREADS=2 .venv/bin/python -I experiments/paper/deepdive.py
.venv/bin/python -I experiments/paper/paper_figures_v2.py
cd research/claude_opus_10_09_v2/paper && tectonic paper.tex
```
