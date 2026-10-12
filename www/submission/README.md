# WWW 2027 Submission Draft

12 October 2026. This is the first submission-format draft of the long paper. It condenses [revision 3](../../research/claude_opus_10_12_v3/README.md) (23 pages) into the ACM `sigconf` format: anonymous, review mode, 8 pages plus references and appendix.

| File | What it is |
| --- | --- |
| [main.tex](main.tex) / [main.pdf](main.pdf) | The paper: 6 pages of main text, then references, then a 2-page appendix (proofs, data, extra results) |
| [references.bib](references.bib) | 36 entries: the 30 papers in [../related_work_abstracts.md](../related_work_abstracts.md), plus 6 background references |
| [abstract.md](abstract.md) | Text to paste into OpenReview by **18 October**, with the source of each number |
| [figures/](figures) | Revision 3's `r1`, `r3`, `r4` and `r5` figures, cropped to remove their built-in titles |

Compile from this folder:

```sh
tectonic -X compile main.tex
```

## How it differs from revision 3

- **Structure.** The paper follows the proposal's channel order: model, mean channel, bridge, fluctuation channel, related work. Revision 3's Q1 (which graphs carry taste) is folded into the mean-channel section as one table and one paragraph.
- **Claims.** They follow the verdicts in [experiments/report §10](../../experiments/report/README.md#10-what-this-means-for-the-paper):
    - "Shrinkage helps; structure helps only through certified rejection."
    - "Persistence pays; the last observed value captures most of it."
    - Valid certificates are "too wide to act" at Web persistence.
    - B3(2) uses the general long-run contrast formula.
    - Two claims are dropped: that hyperlinks improve decisions, and that the joint filter beats forgetting baselines on real data.
- **Anonymity.** The [A]/[S]/[P] provenance labels and all repository paths are removed. The results are presented as the authors' own.
- **Related work** is new. It is built from the 30-paper index and positions the paper against the novelty risks the proposal names: Gornet and Sinopoli, TV-GP-UCB, and Trella et al.

## To do before 25 October

1. **Path-against-clique proof.** Appendix A points to "supplementary material" for the separation result. Either add the proof from [research/alignment_paper](../../research/alignment_paper/manuscript.tex) (section "How alignment changes the information lower bound") or cut the claim.
2. **Prior unpublished manuscripts.** The innovation regression (Theorem 4.1) and SP-UCB (Theorem 3.1) come from the alignment and spatiotemporal manuscripts. If either is public (arXiv) under the authors' names, cite it in the third person as the double-blind rules require. Otherwise keep the proofs in the appendix as they are now.
3. **Figures.** The `r*` figures are cropped PNGs. For the final version, regenerate them as PDF without titles from [experiments/report/code/build_report.py](../../experiments/report/code/build_report.py).
4. **Space.** There are about 2 free pages. The best candidates to bring back are the toy benchmark table (now Appendix C), the B1 regret table from revision 3 (cost of validity at low and high persistence), and the energy-certificate result (A4).
5. **Go/no-go on 20 October.** This draft states B1 as proved, following revision 3. If B1 is withdrawn, use the fallback in [../st_short_paper.md](../st_short_paper.md).
6. **Overfull lines.** Review mode reports several overfull lines of 2–16 pt, which still need tidying.
