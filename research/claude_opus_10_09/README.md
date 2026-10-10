# Correlated Arms on the Web: Compiled Findings (9 October 2026)

This directory collects everything developed in the 9 October 2026 session into one place.

| Item | What it is |
| --- | --- |
| [paper/paper.pdf](paper/paper.pdf) ([source](paper/paper.tex)) | Long working paper with every finding, theorem, table and figure, written to be condensed into a WWW 2027 submission |
| [figures/](figures) | Paper figures (PDF and PNG), produced by `experiments/paper_figures.py` |
| [wikipedia/](wikipedia) | The new application: Wikipedia attention over the hyperlink graph (data, diagnostics, results) |

Supporting material elsewhere in the repository:
- [research/correlated_arms](../correlated_arms/README.md): theory map, with the bridging results B1–B3 and their proofs
- [research/kuairec_graphs](../kuairec_graphs/README.md): KuaiRec report
- [research/st_toy](../st_toy/README.md): spatiotemporal benchmark and the algorithm catalog
- [www/](../../www): proposal, experiment plans and application designs

## Headline findings

1. **Web graphs differ in what they encode.** Collaborative and co-engagement graphs carry correlated appeal on KuaiRec. Social, profile, location, demographic and tag graphs carry little beyond popularity.
2. **Pooling gains come mostly from shrinkage.** Rewired graphs match real ones on average.
3. **Uncertified pooling: good median, heavy tail.** Oracle-certified pooling removes the tail and halves UCB1's regret, but practical certificates are still too wide or invalid.
4. **Persistence breaks iid certificates under bursty exposure.**
    - iid certificates are violated in 75–90% of runs, and wrongly eliminate the best arm in 40–75%.
    - Innovation-regression certificates (B1′ for independent shocks, B1″ for correlated shocks) are never violated, at comparable regret.
5. **Modelling dynamics pays.**
    - Benchmark: joint predictive sampling closes 37% of the gap to the innovation lower bound; spatial correlation adds 15%.
    - KuaiRec daily: modelling persistence cuts regret 38–43% against iid TS.
    - Exploration must target persistent uncertainty and be matched to the number of observations per arm.
6. **Wikipedia attention.** Strong persistence and weekly cycles. Shocks are strongly correlated, but mostly through a domain-wide common factor; hyperlinks add little beyond it. Policy results are in [wikipedia/README.md](wikipedia/README.md).
