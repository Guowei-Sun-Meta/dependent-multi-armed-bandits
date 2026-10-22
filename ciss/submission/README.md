# CISS 2027 practice draft

Condensed on 22 October 2026 from the KDD draft ([kdd/submission/main.tex](../../kdd/submission/main.tex), at commit `45577bb`) into the CISS format: IEEE conference template, at most 6 pages including references, not anonymous ([../README.md](../README.md#call-for-papers)).

| Artifact | Purpose |
| --- | --- |
| [main.tex](main.tex) / `main.pdf` | `IEEEtran` conference paper; 5 pages at the last build |
| [references.bib](references.bib) | The KDD bibliography plus 8 CISS 2022–2025 papers from the [index](../related_work_abstracts.md) |
| [figures/](figures/) | `r1_dose_response.pdf` and `coverage_cost.pdf`, copied from the KDD draft |

Compile from this directory with `tectonic -X compile main.tex`. Tectonic reruns BibTeX up to its limit with an "internal consistency" warning about `main.bbl`; the output has no undefined references.

## What changed from the KDD draft

The CISS audience is information theory, signal processing and statistical inference, and the page budget is about 40% of KDD's 8 pages plus appendix. So the paper keeps the theory and compresses the evidence.

1. **Title and framing.** "Spatial and Temporal Dependence in Bandits on Logged Platform Data" became "Certified Pooling and Valid Confidence under Spatiotemporal Dependence". The page-1 paragraph "Why this is a data-mining problem" is dropped.
2. **Theory kept, with proof sketches in the body** (CISS has no appendix): Proposition 1 (node–time covariance), Theorem 1 (alignment-sensitive regret), the path–clique separation, Theorems 2–4 (innovation design, all-time confidence, valid pooling), the information sandwich and sublinear mean-regret bound (from the KDD appendix), Proposition 2 (inflation) and the exact AR(2) schedule comparison (from the KDD appendix, now Proposition 3).
3. **Evidence compressed** to one section: the KuaiRec certificate table (7 rows of 12), Fig. 1 (rejectability), one sentence on Setting B, the OBD simulator in one paragraph, Wikipedia inflation, Fig. 2 (coverage on calibrated worlds), and the chronological KuaiRec result in one paragraph. Dropped: the OBD table and actual-log pilot, the linear and hybrid feature baselines, the mechanism checks and factorial screen, the chronological policy table and Fig. on paired controls, the Wikipedia policy panels, the scalar nuisance construction, and all appendices.
4. **Related work** cut to one paragraph, with the CISS papers that matter to this audience: graph bandits on movement graphs, graph-signal smoothness priors, the innovation representation, expected-versus-observed Fisher information, misspecified Cramér–Rao and Barankin bounds, and particle Thompson sampling.
5. **Dropped:** the practitioner rules, the data and licensing statement, and the reproducibility statement. Add a one-line data statement back if the page budget allows.
