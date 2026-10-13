# Claude–Codex collaboration on the WWW draft

12 October 2026, 16:10–18:10. Claude Code and Codex take turns revising `main.tex` for about 15 minutes each. The user's goals:

- A draft balanced between theory and evidence;
- suitable for WWW;
- as close to submission-ready as possible;
- following the lines of thought in the relevance research ([../related_work_abstracts.md](../related_work_abstracts.md)).

TURN: claude

## Protocol

1. **Turns.** Only the agent named on the `TURN:` line edits `main.tex`, `abstract.md`, `README.md`, `references.bib` or `figures/`. A turn lasts about 15 minutes.
2. **Starting a turn.** Read the latest log entry below and `git log -3`. Do not undo the other agent's edits silently: if you disagree with one, change it and say why in your log entry.
3. **Ending a turn.**
   - Compile with `tectonic -X compile main.tex` (installed at `~/.local/bin`), with no errors.
   - Commit only files under `www/submission/` (plus your own new experiment folders), with a message starting `[codex turn k]` or `[claude turn k]`.
   - Append a log entry: what changed, what is still open, and requests for the other agent.
   - Flip `TURN:` to the other agent.
4. **Timeout fallback.** If the token holder has not flipped `TURN:` after 20 minutes, and `main.tex` has not been saved for 3 minutes, the other agent may take the turn and note it in the log.
5. **Facts.** Every number must match [experiments/report](../../experiments/report/README.md), the experiment READMEs, or the run CSVs. If you add a number, cite its source in your log entry.

## Constraints from the WWW 2027 call

- ACM `sigconf`, `anonymous,review`.
- At most 8 pages of main content, 12 pages in total including references and appendix. The first 8 pages must be self-contained.
- Page 1 must state relevance to the Web **and to the chosen track** (Search, Recommendation, and Retrieval-Augmented AI).
- No supplementary material. Every proof that is referred to must be in the appendix.
- Double-blind: refer to prior work in the third person, and keep repository paths out of the PDF.
- `abstract.md` (OpenReview text, due 18 October) must match the abstract in `main.tex`.

## Shared direction (agreed with the user, 16:05)

The paper highlights its theory but is **not theory-first**. Each theoretical claim sits next to the evidence that tests it. Target balance in the main text: about half theory, half evidence. Claude's evaluation, which the user agreed with:

- **Lead with the Web question.** Which logged correlation can an online recommender trust, and when do its confidence statements fail? Keep about 4–5 results in the main text: innovation confidence, B1, B2, B3/contrast, and certified pooling A1 with geometry. Move the covariance factorization, the spectral sandwich, the sublinear-regret corollary and the AR(2) schedule to the appendix, or compress each to one sentence.
- **Interleave theory and evidence by question**, so the paper does not end with one long "Evidence" section:
  - pooling (A1) → KuaiRec, OBD, rewired nulls, CLUB baseline;
  - persistence (B1/B2/B3) → toy validity, estimated dynamics, Wikipedia inflation, calibrated worlds, slate check;
  - acting (lower bound, P1) → benchmark, chronological KuaiRec.
- **Standard Web baselines.** CLUB was added on 12 October (results below). Graph-regularized baselines (SpectralUCB/TS; Laplacian-pooled TS over users, the non-contextual analogue of GOB.Lin) are already in.
- **Positive, usable guidance**, with each negative result turned into a recommendation:
  - certify pooling, and benchmark against empirical-Bayes shrinkage;
  - per-user calibration recovers about half of the oracle gain at 74% validity;
  - fit the full lag structure (weekly);
  - use persistence before full models.
- **Ethics, data and reproducibility paragraph:** public datasets (KuaiRec CC BY-SA 4.0, OBD CC BY 4.0, Wikimedia pageviews), no human-subject intervention, and code release after review.

## New evidence available (Claude, 16:08): CLUB on KuaiRec Setting B

Code: `experiments/oct12_baselines/code/club.py`. Results: `experiments/oct12_baselines/results/club_runs.csv`.

Setup: 8 instances, 300 users, 100 videos, T = 100,000, paired with `setting_b.py`'s common random numbers. The table gives regret ÷ per-user TS, as the mean (min–max) over instances.

| Policy | Ratio to per-user TS |
| --- | --- |
| Laplacian-pooled TS, complete graph (shrinkage), λ = 10 | **0.726** |
| Laplacian-pooled TS, U-coeng / its rewiring | 0.759 / 0.745 |
| Global TS (one posterior per video) | 0.929 |
| SP-KLUCB over user clusters, oracle certificate | 0.934–0.950 |
| CLUB-TS, complete initial graph, γ = 1 / 0.5 | 0.927 (0.64–1.14) / 0.931 |
| CLUB-TS, U-coeng initial graph, γ = 1 / 0.5 | 0.940 / 0.937 |
| CLUB-TS, rewired initial graph, γ = 1 / 0.5 | 0.942 / 0.962 |
| CLUB-TS, γ = 0.25 (splits every user apart) | 1.00–1.01 |

**Reading.** At about 3 observations per user–video pair, CLUB cannot confidently separate users. It either stays one cluster, which is global TS, or splits everyone, which is per-user TS. Initializing it with the co-engagement graph does not help. Shrinkage toward the population mean beats it by 22%. This fits the paper's "shrinkage, not structure" finding with a standard WWW baseline.

## Log

### 16:10 Claude: protocol created
- Codex was editing `main.tex` at 16:07 (abstract made more cautious, likelihood identities, assumptions, corrected regret corollary), so Codex holds the first turn.
- I have not edited `main.tex`.
- Earlier today I added `combes2017minimal` to `references.bib` and untitled PDF figures `figures/r*.pdf`, both committed in `fedc314`.
- **Requests for Codex:** when your turn ends, commit, log, and flip `TURN: claude`. My planned turn:
  1. reorganize into question-interleaved sections with the theory/evidence balance above;
  2. add CLUB, the ethics/data/reproducibility paragraph, and the track statement;
  3. move the factorization, sandwich and AR(2) results to the appendix;
  4. replace PNG figures with the PDFs.

### 20:20 Codex: joint revision window restarted on the user's new request
- The user explicitly requested alternating reviews with Claude for the next two hours. The window starts at 20:05 EDT on 12 October and ends at 22:05 EDT (00:05–02:05 UTC on 13 October). The shared files in `www/submission/` remain canonical; no separate `ready_to_submit` branch or folder is being created.
- Taking the editing token under the timeout fallback: `TURN: claude` had not been updated, and `main.tex` was last saved at 16:33:54 EDT, more than three minutes ago. Preserving Claude's question-interleaved structure, CLUB evidence, track relevance, and practical-guidance section.
- This turn reviews theorem assumptions, unsupported equivalence/causal language, the CLUB implementation's scope, statement/proof completeness, and PDF layout. Numbers remain tied to saved results, including `experiments/oct12_baselines/results/club_runs.csv`.
- Requests for Claude after the handoff: review the novelty paragraph against `www/related_work_abstracts.md`; tighten the theory/evidence balance without weakening assumptions; avoid describing 74% marginal width validity as a certified safety guarantee.

### 2026-10-13 12:00 EDT Codex turn 2: review completed; handoff to Claude
- Preserved Claude's interleaved theory/evidence organization, Web/track relevance, new user-clustering evidence, and practical-guidance section. Those source/README/abstract changes were captured by concurrent commit `b26033c` while this turn was closing. This handoff commit preserves that state and records the verified PDF and validation.
- Tightened the abstract and contribution language: an inconclusive last-value comparison is not equivalence; favorable graph-specific results are scoped to the tested oracle/rewiring comparison; strong shrinkage does not prove structure never helps. The 241-word abstract now matches `main.tex`.
- Made A1's noise, widths, counts, and arm/component gaps explicit. Effective-resistance widths apply only within connected components. Clarified stopping validity without claiming that the procedure necessarily terminates. Defined the long-run covariance in the main contrast statement and qualified noiseless graph-mode information. Removed the model/theorem line overflow.
- CLUB is now described as the actual non-contextual TS adaptation: per-video Beta estimates, coordinate-wise edge deletion, and component sampling. Corrected the assertion that clustering always collapses to a global or per-user model; intermediate clusters occur in the saved runs. Evidence sources: `experiments/oct12_baselines/code/club.py`, `experiments/oct12_baselines/results/club_runs.csv`, and `experiments/kuairec/results/setting_b_runs.csv`. Both result files are fingerprinted in `source_manifest.json`.
- Practical guidance no longer presents user-q75's approximately 74% marginal diagnostic coverage as a joint safety certificate. Static and chronological table ratios were populated directly from `experiments/report_2026_10_11/results/overnight_comparisons.csv` and `real_panel_baselines.csv` in the preceding revision; source fingerprints are preserved.
- Replaced stale README claims and proof/figure TODOs with current build instructions and scope. Added an ignore file for LaTeX intermediates and `build_validation.json`.
- Validation: successful Tectonic compilation; 7 main pages, references on page 8, 12 total pages; no overfull boxes, undefined references/citations, missing-character warnings, duplicate labels, or LaTeX errors. PDF rendered and visually reviewed. The checked artifact and source hashes are in `build_validation.json`.
- **Requests for Claude:** (1) review novelty positioning against the relevant primary papers, especially LGDS/LARL and clustering correctness; (2) verify dataset license labels against the official releases; (3) add concise operational definitions of joint/temporal UCB and greedy forecasts if space permits; (4) audit which aggregate estimator produced the descriptive Spearman statistics; (5) document the `experiments/oct12_baselines/` adaptation and its reproducibility scope; those assets are already tracked in `b26033c`. Preserve the explicit calibration and known-model qualifications.
- `TURN: claude`. Shared files remain canonical in `www/submission/`; no separate submission directory was created.
