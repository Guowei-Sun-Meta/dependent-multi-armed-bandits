# WWW 2027 submission draft

The canonical shared draft is [main.pdf](main.pdf), with source in [main.tex](main.tex). Claude and Codex coordinate alternating edits through [COLLAB.md](COLLAB.md).

The current manuscript interleaves theory and evidence by question: trusting a graph for persistent appeal; keeping confidence valid under persistent rewards; and acting on predictable rewards. Spectral information, the mean-regret corollary, long-run graph modes, and the AR(2) schedule example are in the appendix. The retained claims have proofs in the same PDF.

| Artifact | Purpose |
| --- | --- |
| [main.pdf](main.pdf) / [main.tex](main.tex) | Anonymous ACM `sigconf,review` paper |
| [abstract.md](abstract.md) | Matching 250-word OpenReview abstract |
| [references.bib](references.bib) | Bibliography, grounded in the [related-work index](../related_work_abstracts.md) |
| [build_figures.py](build_figures.py) and [data/](data/) | Rebuild the two vector figures from included result snapshots |
| [source_manifest.json](source_manifest.json) | Checksums of the saved experiment tables behind current numerical claims |
| [build_validation.json](build_validation.json) | Compilation, page-limit, reference, abstract, and figure checks |

Compile from this directory:

```sh
tectonic -X compile main.tex
```

Rebuild figures from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -I www/submission/build_figures.py
```

The [official call](https://www2027.thewebconf.org/research-track-papers/) permits at most eight main-text pages and twelve pages total. The draft uses the anonymous review template, with explicit Web and track relevance on page one. [Official dates](https://www2027.thewebconf.org/important-dates/): abstract 18 October 2026, paper 25 October 2026, Anywhere on Earth.

Current scope: oracle pooling improves on a matched conservative baseline, graph-free shrinkage is strong, persistence helps against iid policies, and graph-specific and last-value comparisons remain inconclusive in the chronological test. Width diagnostics and fitted-model coverage are empirical, not joint safety guarantees. The CLUB comparison uses a non-contextual TS adaptation and does not test the original contextual theorem. Linear TS, LinUCB and a hybrid feature prior on leakage-free I-mf embeddings were tuned on held-out users and run on the same 360 KuaiRec instances; the hybrid prior ties graph-free shrinkage.

The remaining review items and handoff requests are in COLLAB.md. The manuscript has not been externally submitted.

## Status at the end of the Claude–Codex review window (13 October, 13:35 EDT)

**The draft meets the formal requirements of the call:**
- ACM `sigconf,anonymous,review`;
- main text ends on page 8, 12 pages in total;
- Web and track relevance on page 1;
- every cited proof is in the appendix;
- no LaTeX errors, unresolved references or overfull lines;
- an anonymity scan of the PDF text and metadata is clean;
- the 250-word abstract matches `abstract.md`.

**Evidence added during the window** (all in `experiments/oct12_baselines/`):
- CLUB on Setting B;
- LinTS, LinUCB and a hybrid feature prior on Setting A;
- a gradient-boosted forecast-then-rank baseline on chronological KuaiRec.

**Decisions only the authors can make before submission:**
1. **The abstract and author list on OpenReview by 18 October.** Authors are frozen after that date, and every author needs an up-to-date OpenReview profile.
2. **Prior manuscripts.** If the alignment or spatiotemporal manuscripts the theory builds on are public (for example on arXiv), cite them in the third person. If they are not, the self-contained proofs in the appendix are enough.
3. **Go/no-go on B1 (20 October).** The appendix proves validity and the realized-information rejection condition (Theorem 4.3), given the cited self-normalized bound. Confirm the proof before 20 October.
4. **Optional, if time allows:** a chronological rerun of our own Wikipedia panels, with dated links and prefix selection. The paper currently labels those panels retrospective.

The comments at the top of `main.tex` name repository folders. They do not appear in the PDF. Remove them if source files are ever uploaded before acceptance.
