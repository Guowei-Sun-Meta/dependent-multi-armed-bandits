# Dependent Multi-Armed Bandits: Project Context

Read this first in a new session. Last updated 9 October 2026.

## Goal

The research studies bandits whose arms are dependent:

- **Across arms:** graph or spatial similarity between arms or users.
- **Over time:** AR or Markov rewards.

The current deliverable is a **WWW 2027 paper on graph-based bandits for recommendation**: certified user and item graphs, tested on KuaiRec. The deadlines are fixed:

- **Abstract: 18 October 2026, AoE.** Placeholder abstracts are forbidden, and authors are frozen after this date.
- **Full paper: 25 October 2026, AoE.** 8 pages plus appendix, double-blind, submitted through OpenReview. The paper must state its Web relevance on page 1.

The proposal, sprint plan and WWW precedent are in [www/CLAUDE.md](www/CLAUDE.md). The KuaiRec design is in [www/kuairec_experiment_plan.md](www/kuairec_experiment_plan.md).

## Repository map

| Path | What it is |
| --- | --- |
| `research/alignment_paper/` | Theory for graph alignment: SP-UCB, GDE-UCB, certified energy bounds, resistance geometry (manuscript.tex/pdf). Supplies T1–T3 of the WWW paper |
| `research/graph_spectral_bandits.md` | Note linking the S-index (Sun, Li and Fu 2019) to cumulative regret; contains the misalignment counterexample |
| `research/kuairec_graphs/` | **Active.** KuaiRec experiments: report (README.md) and results/ |
| `experiments/kuairec/` | **Active.** Code for the KuaiRec pipeline (see below) |
| `research/temporal_bandits.md`, `predictive_ar1/`, `two_arm_ar1/`, `ar_p_bandits/`, `spatiotemporal_bandits/` | Temporal-dependence thread, maintained by the user in parallel. **Don't edit these unless asked**; the user often has uncommitted work there |
| `www/` | WWW proposal and experiment plan |
| `data/` | Raw and cached data (git-ignored) |

## Working conventions

- **Git:** work on branch `kuairec-alignment` (remote `dependent_mab`). Commit and push periodically. Never stage the user's in-progress files; stage paths explicitly. End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Documents** are local markdown files in the repo, never Claude Docs.
- **Math in markdown:** GitHub does not render `\( \)` or `\[ \]`. Use ```` ```math ```` fenced blocks for display math and `` $`...`$ `` for inline math.
- **Python:**
    - Use `.venv/bin/python -I` (Python 3.9; packages in `experiments/kuairec/requirements.txt`). Scripts add their own directory to `sys.path` because `-I` drops it.
    - For parallel runs, set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1` to avoid oversubscribing the 8 cores (8 GB RAM).
- **The original repo scripts** (`experiments/*.py` outside `kuairec/`) use only the standard library. Keep it that way.

## KuaiRec pipeline (`experiments/kuairec/`)

Data:

- KuaiRec 2.0 from Zenodo record 18164998, unzipped into `data/kuairec_raw/`.
- `user_features_raw.csv` and `kuairec_caption_category.csv` are separate downloads.
- Caches go to `data/kuairec_cache/`: the evaluation matrix, `node_features.pkl`, and graphs in `graphs/k{5,10,20}/`.

| Script | Role | Runtime (idle machine) |
| --- | --- | --- |
| `data.py` | Loads data, runs Step 0 checks, caches the 1,411 × 3,327 watch-ratio matrix; reward models R1 (min(wr, 5)/5), R2, R3 | 10 s |
| `graphs.py` | Defines node features for 16 graphs (11 U2U, 5 I2I), all leakage-free; builds union-kNN graphs on any node subset; rewired and Erdős–Rényi nulls; `--k 5 10 20` | 1 min |
| `alignment.py` | Phase 1 diagnostics: smoothness quotient (Laplacian scaled to mean degree 1, so random ≈ 1), personal-taste edge correlation (double-centered), choice cost after smoothing; `--model`, `--k`, `--quick` | 8 min |
| `render_alignment.py` | Tables and figure for Phase 1 | seconds |
| `setting_a.py` / `analyze_a.py` | Setting A: one user, 300 videos, item graph rebuilt on the subset; UCB1, TS, SpectralUCB/TS, SP-UCB with oracle, energy or no certificate | about 1 h for 60 users at T = 20,000 on 6 workers |
| `setting_a2.py`, `setting_b.py` | Next experiments; see "Current status" | — |

Leakage rule:

- Evaluation pairs never appear in the big matrix; this was verified.
- User-side graph signals use only non-evaluation videos.
- Video-side signals use only non-evaluation users.
- The users are split 50/50 with seed 20261009: the first half is for tuning and calibration, the second half for testing.

## Findings so far

Details and tables are in [research/kuairec_graphs/README.md](research/kuairec_graphs/README.md).

1. **Data.** The evaluation matrix is 99.6% dense. The social graph covers only 80 of the 1,411 evaluation users with 47 edges, so the social-graph result must come from Last.fm.
2. **Alignment (Phase 1).**
    - The best user graph is co-engagement, **U-coeng** (Jaccard on fully watched videos): quotient 0.649 against 0.791 for its rewired null.
    - The best item graphs are **I-mf** (factorization) and **I-coeng**.
    - Tag, category and same-author graphs mostly group videos by popularity. Profile, location, demographic and time-of-day user graphs are near random.
    - Results are stable over k and the R3 reward model.
3. **Smoother than chance is not safe to smooth.** Smoothing on real item graphs changes each user's best video more than smoothing on rewired graphs does.
4. **Setting A (bandits).**
    - Gains come from shrinkage: rewired graphs match real ones for spectral methods.
    - Uncertified pooling, meaning Spectral TS at λ = 10 or SP-UCB without a certificate, beats Thompson sampling for most users but has heavy tails, with 90th percentiles up to 18–30× TS.
    - Oracle-certified SP-UCB halves UCB1's regret with no blow-ups.
    - The energy certificate is too loose: the energy-to-gap ratio is about 5, above the threshold of about 1.
    - **The main open problem is a practical certificate between the oracle and energy bounds.**
5. **Known handicap.** UCB-style methods use σ = 0.5 while means average about 0.18, so TS beats them by about 8×. Compare within families, or use KL-based indices.

## Current status and next steps

Kept up to date by whoever runs experiments. Check `research/kuairec_graphs/README.md` for the latest numbers.

- [x] Phase 1 alignment for 16 graphs, k ∈ {5, 10, 20}, with R1 and R3
- [x] Setting A v1 (60 users, T = 20,000)
- [ ] **Setting A v2.** Adds KL-UCB, graph-free shrinkage (Gaussian TS on a complete graph), SP-KLUCB (KL confidence bounds, fixing the σ handicap), and a **calibrated certificate**: the 90th percentile of each component's within-component range over tuning users. Three video subsets per user.
- [ ] **Setting B.** 300 users × 100 videos, users arrive at random, T = 100,000. User graphs U-coeng, U-mf, U-coauthor, U-geo, the U-coeng rewiring, and a complete graph. Policies: per-user TS, global TS, user-graph Gaussian TS, and user-side SP-KLUCB with oracle, calibrated and no certificate.
- [ ] Setting C (product graph), Last.fm social graph, R2 sensitivity
- [ ] Theory: T4 (product-graph regret), T5 (certificate for embedding graphs), and the calibrated certificate's validity statement
- [ ] Abstract (by 18 October) and paper draft (by 25 October)

How to check running jobs: `ps aux | grep kuairec`. Logs from the 3-hour queue go to `data/logs/` (git-ignored).
