# WWW 2027 Submission Draft

12 October 2026. This is the submission-format draft of the long paper; its theory core was revised the same evening (see below). It condenses [revision 3](../../research/claude_opus_10_12_v3/README.md) (23 pages) into the ACM `sigconf` format: anonymous, review mode, 8 pages plus references and appendix.

| File | What it is |
| --- | --- |
| [main.tex](main.tex) / [main.pdf](main.pdf) | The paper: about 6 pages of main text, then references, then a 2-page appendix (proofs, data, extra results) |
| [references.bib](references.bib) | 36 entries: the 30 papers in [../related_work_abstracts.md](../related_work_abstracts.md), plus 6 background references |
| [abstract.md](abstract.md) | Text to paste into OpenReview by **18 October**, with the source of each number |
| [figures/](figures) | Revision 3's `r1`, `r3`, `r4` and `r5` figures, cropped to remove their built-in titles |

Compile from this folder:

```sh
tectonic -X compile main.tex
```

## Theory core (revised 12 October, evening)

At the user's request, the draft now makes spatial and temporal correlation its main theoretical focus. The theory comes from the GPT/Codex package [research/gpt_sol_10_09](../../research/gpt_sol_10_09/README.md) (its synthesis section and spatiotemporal appendix) and from the alignment manuscript. The main text is organized as model → information → pooling → evidence:

| Section | Spatial | Temporal | Interaction |
| --- | --- | --- | --- |
| §2 Model | Two graph roles: $`L_\mu`$ restricts means; $`Q_G`$ (graph kernel) shapes shocks; only the first identifies unobserved arms | Heterogeneous AR($`p_i`$), lag-state form | **Prop 2.1**: $`(G_h)_{ij}=(Q_G)_{ij}\sum_k\psi_i(k+h)\psi_j(k)`$; spectral density; separable only under identical dynamics |
| §3 Information | Graph-regularized confidence (**Thm 3.2**), graph-error repair | Innovation regression (**Thm 3.1**); B2 inflation from the full ACF (**Prop 3.6**) | **Prop 3.3** spectral sandwich ($`v_\pm`$ combines $`\lambda(Q_G)`$ with $`\lvert A_i(e^{-i\omega})\rvert`$) → **Cor 3.4** sublinear regret; **Prop 3.5** long-run information by graph Fourier mode; **Prop 3.7** contrasts and staggering; **Prop 3.8** AR(2): AABB beats ABAB |
| §4 Pooling | A1 regret; graph-energy constant, resistance radius, path against clique | — | **B1** valid under any $`Q_G`$ and restless schedule; **B3(1)** constants with long-run covariance |
| §5 Evidence | Predictions (a)–(b) | (c)–(d) | (e)–(f) |

The draft applies the package's two corrections to the bridge notes. A pooled component's per-pull information keeps the same lower bound ι, with no factor of $`\lvert C\rvert`$. Partial slates use $`Q_{SS}`$, not the full-field precision restricted to $`S`$.

## How it differs from revision 3

- **Structure.** The theory sections are organized by kind of dependence (above). The evidence section tests predictions (a)–(f). The graph-alignment table, the robustness table and the toy benchmark are in the appendix.
- **Claims.** They follow the verdicts in [experiments/report §10](../../experiments/report/README.md#10-what-this-means-for-the-paper):
    - "Shrinkage helps; structure helps only through certified rejection."
    - "Persistence pays; the last observed value captures most of it."
    - Valid certificates are "too wide to act" at Web persistence.
    - B3(2) uses the general long-run contrast formula.
    - Two claims are dropped: that hyperlinks improve decisions, and that the joint filter beats forgetting baselines on real data.
- **Anonymity.** The [A]/[S]/[P] provenance labels and all repository paths are removed. The results are presented as the authors' own.
- **Related work** is new. It is built from the 30-paper index and positions the paper against the novelty risks the proposal names: Gornet and Sinopoli, TV-GP-UCB, and Trella et al.

## To do before 25 October

1. **Path-against-clique and resistance-radius proofs.** Appendix A sketches these and points to "supplementary material" for the full statements. Either add the proof from [research/alignment_paper](../../research/alignment_paper/manuscript.tex) (section "How alignment changes the information lower bound") or cut the claim.
2. **Prior unpublished manuscripts.** The innovation regression (Theorem 3.1) and SP-UCB (Theorem 4.1) come from the alignment and spatiotemporal manuscripts. If either is public (arXiv) under the authors' names, cite it in the third person as the double-blind rules require. Otherwise keep the proofs in the appendix as they are now.
3. **Figures.** `main.tex` still uses the cropped PNGs. Title-free PDFs (`figures/r*.pdf`) appeared on 12 October from a concurrent session running `build_report.py`. Once that run is finished, switch the `\includegraphics` paths to them.
4. **Space.** There are still about 2 free pages. Good uses are a figure of PCS against ρ for Proposition 3.8 (data in `research/gpt_sol_10_09/evidence/spatiotemporal_bandits/results/general_ar/pcs_schedule.csv`), a numeric check of Proposition 3.5 on the grid benchmark, and the energy-certificate result (A4).
5. **Theory provenance.** Propositions 2.1, 3.3, 3.5 and 3.8, Theorem 3.2 and Corollary 3.4 come from the GPT/Codex package, with proofs condensed in Appendix A. Check the condensed proofs against the full ones before submission. The converse in Proposition 2.1 (separable only under identical dynamics) is a new one-line argument via spectral factorization.
6. **Go/no-go on 20 October.** This draft states B1 as proved, following revision 3. If B1 is withdrawn, use the fallback in [../st_short_paper.md](../st_short_paper.md).
7. **Overfull lines.** Three remain, of 17–24 pt (one in §2, two in the appendix).
