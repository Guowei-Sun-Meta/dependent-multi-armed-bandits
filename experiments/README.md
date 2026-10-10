# Experiments

Every experiment behind the correlated-arms papers ([research/claude_opus_10_09_v2](../research/claude_opus_10_09_v2/README.md)), grouped by data source. Each experiment folder holds its design (`design.md`), report (`README.md`), code (`code/`) and results (`results/`).

The [recommended spatiotemporal experiments](recommended_spatiotemporal_experiments.md) describe five application studies, their priorities, laptop-sized scopes, and the shared validation protocol. These are proposed designs, separate from the completed reports below.

```
experiments/
  README.md                          this index
  requirements.txt                   Python packages for everything below
  kuairec/                           KuaiRec (Kuaishou short videos): real rewards for every user–video pair
    README.md  design.md  code/  results/
  wikipedia/                         Wikipedia daily attention over the hyperlink graph
    README.md  design.md  code/  data/  results/
  simulations/
    spatiotemporal_benchmark/        100-arm grid with AR(20) fluctuations: fluctuation-channel policies
    certificates_under_persistence/  validity of certified-pooling certificates under persistence (B1, B2)
    theory/                          numerical checks behind the theory notes in research/
  paper/                             cross-experiment analyses and paper figures
```

`st_apps/` belongs to another agent's work and is not part of this organization.

## Experiments

| Experiment | Question | Channel | Report |
| --- | --- | --- | --- |
| KuaiRec Phase 1: alignment of 16 graphs | Which web graphs encode correlated long-run appeal? | Mean | [kuairec](kuairec/README.md#phase-1-alignment-of-16-graphs) |
| KuaiRec Setting A and A v2: item graphs, one user | Does pooling help, when is it safe, and how good are practical certificates? | Mean | [kuairec](kuairec/README.md#setting-a-single-user-bandits-on-item-graphs) |
| KuaiRec Setting B: user graphs, cold users | Does pooling across users help? | Mean | [kuairec](kuairec/README.md#setting-b-pooling-across-users-with-user-graphs) |
| KuaiRec daily slot: 253 videos × 63 days | Does modelling persistent, correlated engagement pay? | Fluctuation | [kuairec](kuairec/README.md#daily-trending-slot-the-fluctuation-channel) |
| Wikipedia, one domain: 150 articles | Same, on attention; do hyperlinks carry shocks? | Fluctuation | [wikipedia](wikipedia/README.md#panel-1-one-domain) |
| Wikipedia, six communities: 6 × 25 articles | Do hyperlinks carry shocks when communities have different rhythms? | Fluctuation | [wikipedia](wikipedia/README.md#panel-2-six-communities) |
| Spatiotemporal benchmark | How close do fluctuation-channel policies get to the innovation lower bound? | Fluctuation | [simulations/spatiotemporal_benchmark](simulations/spatiotemporal_benchmark/README.md) |
| Certificates under persistence | Do certificates stay valid when rewards persist? | Both (bridge) | [simulations/certificates_under_persistence](simulations/certificates_under_persistence/README.md) |
| Theory checks | Numerical checks of the theory notes | Both | [simulations/theory](simulations/theory/README.md) |
| Paper analyses | Theory-to-data analyses across experiments | Both | [paper](paper/README.md) |

## Environment

- Python 3.9 in `.venv/` at the repository root: `python3 -m venv .venv && .venv/bin/pip install -r experiments/requirements.txt`.
- Run every script from the repository root as `.venv/bin/python -I <script>`. Scripts add their own folder to `sys.path`, because `-I` drops it. The theory scripts are the exception (see [simulations/theory](simulations/theory/README.md)).
- For parallel runs, set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, because the pools already use every core.
- Large or regenerable data stays outside this folder, in the git-ignored `data/` at the repository root:
    - KuaiRec 2.0 raw files go in `data/kuairec_raw/` (Zenodo record 18164998), and caches in `data/kuairec_cache/`.
    - Wikipedia API responses and fitted filters are cached in `data/wikipedia/`.
- The Wikipedia panels (2 MB) are committed in `wikipedia/data/`.

## Path changes (10 October 2026)

Files were moved with `git mv`, so `git log --follow` shows the history of moved code and results. Documents that were split or merged (the benchmark and Wikipedia reports) start a new history.

| Old path | New path |
| --- | --- |
| `experiments/kuairec/*.py`, `queue_oct9.sh` | `experiments/kuairec/code/` |
| `experiments/kuairec/requirements.txt` | `experiments/requirements.txt` |
| `research/kuairec_graphs/README.md` | `experiments/kuairec/README.md` |
| `research/kuairec_graphs/results/` | `experiments/kuairec/results/` |
| `www/kuairec_experiment_plan.md` | `experiments/kuairec/design.md` |
| `experiments/wikipedia/*.py` | `experiments/wikipedia/code/` |
| `research/claude_opus_10_09/wikipedia/{data,results}/` | `experiments/wikipedia/{data,results}/one_domain/` |
| `research/claude_opus_10_09_v2/wikipedia_multi/{data,results}/` | `experiments/wikipedia/{data,results}/six_domains/` |
| `research/claude_opus_10_09/wikipedia/README.md`, `research/claude_opus_10_09_v2/wikipedia_multi/README.md` | merged into `experiments/wikipedia/README.md` and `design.md` |
| `experiments/st_toy/{toy,analyze}.py` | `experiments/simulations/spatiotemporal_benchmark/code/` |
| `research/st_toy/README.md` | `experiments/simulations/spatiotemporal_benchmark/README.md` and `design.md` |
| `research/st_toy/results/` (except `coverage_runs*`) | `experiments/simulations/spatiotemporal_benchmark/results/` |
| `experiments/st_toy/coverage.py` | `experiments/simulations/certificates_under_persistence/code/` |
| `research/st_toy/results/coverage_runs*.csv` | `experiments/simulations/certificates_under_persistence/results/` |
| `experiments/{alignment_regret,resistance_geometry,render_geometry_results,s_index_counterexample}.py` | `experiments/simulations/theory/graph_alignment/` |
| `experiments/{predictive_ar1,render_predictive_ar1,ar1_policy_improvement}.py` | `experiments/simulations/theory/predictive_ar1/` |
| `experiments/{two_arm_ar1_allocation,ar_p_extension}.py` | `experiments/simulations/theory/ar_allocation/` |
| `experiments/temporal_information.py` | `experiments/simulations/theory/temporal_information/` |
| `experiments/{spatiotemporal_bandits,graph_ar1_mean,graph_ar_mean,spatiotemporal_policies,spatiotemporal_policies_analysis}.py` | `experiments/simulations/theory/spatiotemporal/` |
| `experiments/spatiotemporal_requirements.txt` | `experiments/simulations/theory/spatiotemporal/requirements.txt` |
| `experiments/{deepdive,paper_figures,paper_figures_v2}.py` | `experiments/paper/` |

Path constants, imports, reproduction commands and links in the papers and notes were updated to match. The theory notes' outputs did not move (see [simulations/theory](simulations/theory/README.md)). Files that still use the old paths: `experiments/st_apps/audit_kuairec.py` (reads `research/kuairec_graphs/results/daily_runs.csv`) and the source manifest in `research/gpt_sol_10_09/`. Both belong to another agent and were left unchanged.
