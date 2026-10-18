# KDD 2027 submission draft

Converted on 18 October 2026 from the WWW draft (`www/submission`, final state at commit `ab4139a`). The content is unchanged except where noted; the format follows the [KDD 2027 research-track call](../README.md#call-for-papers-research-track).

| Artifact | Purpose |
| --- | --- |
| [main.tex](main.tex) / `main.pdf` | Anonymous ACM `sigconf,anonymous,review` paper; 8 content pages, 12 pages total at the last build |
| [references.bib](references.bib) | Bibliography |
| [build_figures.py](build_figures.py), [data/](data/), [figures/](figures/) | Figure sources and result snapshots, copied from the WWW draft |
| [source_manifest.json](source_manifest.json) | Checksums of the experiment tables behind the numerical claims |

Compile from this directory with `tectonic -X compile main.tex` (tectonic is at `~/.local/bin`).

## Changes from the WWW draft

1. Conference metadata, header comments and title: "Web Bandits" became "Bandits on Logged Platform Data".
2. The page-1 paragraph "Relevance to the Web", which the WWW call required, is now "Why this is a data-mining problem": the same facts, framed as graph mining, time-series estimation and sequential inference on logged data, without the WWW track statement.
3. "Web platforms" became "online platforms"; "WWW systems" became "platform systems"; the related-work heading "Confidence and Web evaluation" became "Confidence and evaluation on logged data".
4. The reproducibility statement promises an anonymized repository at submission, as the call recommends.

Not yet done: the related-work section still cites the WWW-era index; it will be revised against [kdd/related_work_abstracts.md](../related_work_abstracts.md). KDD's appendix has no page limit, so the proofs and protocols that were compressed for WWW's 12-page cap can be expanded.
