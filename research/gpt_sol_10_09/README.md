# Correlated and persistent rewards: extended research package

9 October 2026. This directory contains the requested long manuscript and a completed second application experiment. Original research manuscripts and experiments were read and collected without being overwritten.

Start with the [compiled paper](manuscript.pdf) or its [editable LaTeX source](manuscript.tex). The [integrated synthesis](sections/synthesis.tex) connects the model, estimators, policies, information limits, selection formulas, simulations, and applications. Five technical appendices retain the full derivations from the spatial/general-AR, graph-alignment, predictive AR(1), two-arm, and multiple-arm/general-AR papers. The main model permits heterogeneous AR orders; AR(1) appears only as a restricted analytical example.

The [evidence index](findings.md) maps findings to their source artifacts. The [source manifest](evidence_manifest.json) fingerprints the collected versions. Older Bayesian or iid results keep their original assumptions. Exploratory findings and incomplete theoretical extensions are explicitly identified, including two corrections to the original pooling/partial-feedback bridge notes.

## New application: selective Wikipedia attention monitoring

The [executed protocol](experiment_design.md) and [completed findings](results/wikipedia/findings.md) describe two fixed panels of 24 articles each, covering astronomy and football. Historical hyperlinks come from revisions before 2024. Models use 2024 fitting and development; test feedback is selectively masked over 181 days in January–June 2025. Rewards are observed human page views transformed by `log1p`.

- Main model: general AR(7) with lags 1, 2, and 7; sensitivity: dense AR(20).
- Budgets: one or five simultaneous observations per day, with no full-field test refresh.
- Completed: **352 runs and 63,712 daily decisions**.
- Measured experiment cost: **197.9 seconds and 166.8 MB peak process memory**, using one BLAS thread. This excludes acquisition, plotting, and PDF compilation.
- At five observations/day, joint predictive UCB reduces observed-oracle regret against its matched temporal-only UCB by **24.5% in astronomy and 5.2% in football**. Temporal-only greedy remains strongest in football; static ranking is very strong at one observation/day.
- Real and rewired graphs perform almost identically. The experiment does **not** establish an advantage from the actual hyperlink topology. Thompson policies can explore too much in this mature-catalog setting.

Every method receives the same full 2024 history: **8,784 historical readings per panel**, disclosed separately from the 181 or 905 test readings. Policy seeds quantify randomization conditional on a fixed observed field, rather than independent Web histories. The application evaluates exogenous attention opportunities; it does not estimate promotion lift, a true permanent-mean PCS, or a stationary innovation floor.

Results include [per-run records](results/wikipedia/runs.csv), [daily decisions](results/wikipedia/daily.csv), [conditional intervals](results/wikipedia/summary.csv), [paired comparisons](results/wikipedia/paired.csv), [calendar blocks](results/wikipedia/calendar_blocks.csv), [model metadata](results/wikipedia/metadata.json), and all fitted matrices in the model NPZ files. See the [comparison figure](results/wikipedia/comparison.pdf) and [cumulative loss figure](results/wikipedia/cumulative.pdf).

## Reproduce the new experiment

Run from the repository root. Tested with Python 3.9.6 and the versions in [requirements.txt](requirements.txt). The current repository virtual environment already has these dependencies. Acquisition uses only the Python standard library. About 13 MB of raw API responses and historical revisions are cached under `data/wikipedia`; running the downloader with that cache requires no new requests.

```sh
.venv/bin/python -I research/gpt_sol_10_09/code/download_wikipedia.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  .venv/bin/python -I research/gpt_sol_10_09/code/wikipedia_experiment.py \
  --seeds 10 --orders 7 20 --output /private/tmp/gpt_sol_wikipedia_repeat
.venv/bin/python -I research/gpt_sol_10_09/code/analyze_wikipedia.py \
  --results-dir /private/tmp/gpt_sol_wikipedia_repeat
```

The separate output preserves the released results. Omitting `--output` and `--results-dir` replaces the results in this directory, including measured timing. The analysis expects the complete released configuration of ten main stochastic seeds and three AR(20) seeds. The runner itself permits smaller timing pilots.

The downloader uses sequential requests, an identifying user agent, caching, and backoff. View statistics are CC0; revision text follows Wikipedia attribution/share-alike terms. The [data manifest](data/wikipedia/manifest.json) retains article IDs, revision IDs and dates, request URLs, and raw-file hashes. Historical article text is retained for graph reconstruction rather than reproduced in the manuscript.

## Build and edit the paper

The PDF builds entirely from files in this directory; it does not require the original papers or raw KuaiRec dataset. With a populated Tectonic cache:

```sh
cd research/gpt_sol_10_09
tectonic --only-cached --keep-logs manuscript.tex
```

Without a populated cache, use `tectonic --keep-logs manuscript.tex` and allow the initial TeX resource downloads. The compilation uses TeX Gyre Pagella and Latin Modern Math from the TeX bundle.

For later reduction, edit `sections/synthesis.tex` first, choose one primary objective and a small set of contributions, and move or remove detailed source appendices. The integrated sections are the current interpretation; historical evidence notes can contain superseded claims identified in the synthesis. A venue-specific version will still need a focused novelty argument and stronger application evidence where the current controls show no topology advantage.

`code/collect_sources.py` is an archival assembly utility, not a required reproduction step. Running it again takes a new snapshot of live repository sources; `--appendices-only` refreshes the five derivations and bibliography while retaining the compact evidence snapshot. Preserve this dated package before updating its sources.

## Verification

[Filter checks](results/wikipedia/checks.json) cover dense transition/update equivalence, complete panels, graph chronology, degree preservation, and positive semidefinite predictive covariance throughout the decisions. [Analysis checks](results/wikipedia/analysis_checks.json) cover complete run combinations, daily bookkeeping, observation budgets, and nonnegative oracle loss. [Package verification](verification.json) records source provenance, data hashes, build checks, and final artifact counts.

