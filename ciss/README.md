# CISS 2027 practice round

22 October 2026. A practice submission of the correlated-arms paper to the **Conference on Information Sciences and Systems (CISS 2027)**, Johns Hopkins University, Baltimore, MD, 24–26 March 2027. CISS is the only US conference found with a November–December 2026 deadline that fits the paper; CVPR 2027 (Seattle, 16 November) is the only other one, and it is off-topic. The main target remains [KDD 2027 cycle 2](../kdd/README.md).

## Call for papers

The 2027 call is not readable yet: ciss.jhu.edu lists the dates as 24–26 March 2027 with every deadline "TBD", and both CISS sites refuse automated access. The rules below come from the **CISS 2023 call** (Johns Hopkins, the previous meeting at this host), read from the Internet Archive copy of `ciss.jhu.edu/wp-content/uploads/2022/05/CISS-2023-CFP-04-19-22.pdf`. Check them against the 2027 call when it appears.

- **Format:** "Submissions in FINAL FORMAT and no longer than six (6) pages". Papers are "reproduced in full (up to six pages) in the conference proceedings" and must be uploaded "in IEEE PDF format", so the IEEE conference template (`IEEEtran`, `conference` option) is the format, and the 6 pages include references.
- **Not double-blind:** the submission is the final manuscript, so author names and affiliations are on it.
- **Deadline pattern:** submission 10 December 2022, notification 30 January 2023, final manuscript 6 February 2023. Earlier Johns Hopkins calls used 7 December 2020 and 11 December 2016. Expect early-to-mid December 2026.
- **Topics** include machine learning, statistical inference, reinforcement learning, systems and control, information theory, optimization and big data analytics.
- **Presentation:** about 18 minutes per paper. "IEEE reserves the right to exclude any paper from distribution after the conference, including removal from IEEE Xplore®, that is not presented by an author at the conference." Technical co-sponsor: IEEE Information Theory Society.

## Folders

| Path | What it is |
| --- | --- |
| [submission/](submission/README.md) | The 6-page IEEE version (`main.tex`), condensed from the KDD draft; 5 pages at the last build |
| [related_work_abstracts.md](related_work_abstracts.md) | 26 indexed abstracts from CISS 2022–2025, with relevance notes; 8 marked core and cited in the draft |
| [related_work_scan/](related_work_scan/README.md) | Scripts that produced the index |

## Before a real submission

1. **Dual submission with KDD.** A CISS paper is archival (IEEE Xplore), and CISS would still be in review or already published when the KDD cycle 2 deadline arrives in February 2027. Under typical prior-publication rules this can bar the same work from KDD. Either submit a narrower piece to CISS (for example, Theorems 2–4 and Propositions 2–3 as a theory note, without the KuaiRec and OBD experiments) and cite it at KDD, or keep this as an internal mock round. Read KDD 2027's dual-submission text before deciding.
2. **Authors:** fill in the `\author` block; CISS is single-blind.
3. **IEEE PDF eXpress:** final manuscripts are checked with PDF eXpress (the CISS 2025 final-paper page names a conference ID), which requires embedded Type 1/OpenType fonts. The draft uses TeX Gyre Termes through `fontspec` under tectonic; if PDF eXpress rejects it, compile with pdfLaTeX, where `IEEEtran` loads Times directly.
4. **Watch for the 2027 call** in early November and update the deadline in this file.

## Practice timeline (assuming a deadline around 10 December 2026)

- By 6 November: internal read of the draft; choose between the full version and the theory note (item 1 above).
- By 20 November: proofs checked against [research/correlated_arms](../research/correlated_arms/README.md); figures redrawn at single-column IEEE size.
- By 4 December: final read; PDF eXpress check; author list final.
- Submission day: upload through the CISS site.
