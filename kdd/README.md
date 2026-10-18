# KDD 2027 target

18 October 2026. The correlated-arms paper is retargeted from WWW 2027 (Dublin, 10–14 May 2027) to **KDD 2027, research track, second cycle** (San Jose, CA, 1–5 August 2027), because the authors can only attend conferences held in the United States. SIGIR 2027 (Silicon Valley, deadline expected mid-January 2027) is the backup; RecSys 2027 (Honolulu, spring deadline) the fallback.

## Call for papers (research track)

Source: [kdd2027.kdd.org/research-track-call-for-papers](https://kdd2027.kdd.org/research-track-call-for-papers/), read on 18 October 2026.

- **Cycle 2 deadline:** "February 2027"; the exact day is not yet published. Cycle 1 closed 26 July 2026 (abstract 19 July), with notification on 14 November 2026. Deadlines are end-of-day AoE, strict, no extensions.
- **The author list is final at the abstract deadline.** Every author needs a complete OpenReview profile (affiliations for five years, homepage, ORCID, DBLP); incomplete profiles are desk-rejected, and profiles without an institutional email take up to two weeks to moderate.
- **Format:** one PDF, `\documentclass[sigconf,anonymous,review]{acmart}`, **8 content pages**, then references and an **appendix with no page limit** in the same format. The first 8 pages must be self-contained. Camera-ready: 12 pages, of which 9 are content.
- **Double-blind:** no author names, affiliations, acknowledgments or identifying self-citations; refer to own prior work in the third person. Organizations that supplied data may be named. Anonymized arXiv preprints are allowed.
- **Code:** an anonymized repository is "highly recommended"; code and data release on acceptance earns an Artifacts Available badge.
- **Other rules:** one track per paper, no track transfers, at most 7 submissions per author per cycle, each submission nominates one qualified reviewer (an author with three or more KDD-level papers), no placeholder abstracts. Resubmissions of cycle-1 "Resubmit" decisions must give the previous forum id and a one-page change summary.
- **Topics named in the call** that the paper fits: probabilistic and statistical methods; structured and relational learning; reinforcement learning; time series; graphs; recommender systems. Bandits are not named explicitly; the paper is positioned under statistical methods and time-series/graph applications, with recommendation as the use case.

## Folders

| Path | What it is |
| --- | --- |
| [submission/](submission/README.md) | The KDD draft (`main.tex`, figures, data snapshots), converted from `www/submission` |
| [related_work_abstracts.md](related_work_abstracts.md) | Indexed abstracts from ICLR, ICML, NeurIPS, COLT, AISTATS and KDD, 2024–2026, with PDF links |
| [experiment_proposals.md](experiment_proposals.md) | New experiments suited to KDD that use the certified-pooling and innovation-confidence methodology |

## Timeline to the February deadline

1. Now to mid-November: tighter anytime-valid certificate (the top open problem in [experiments/report](../experiments/report/README.md)); choose two new experiments from the proposals and run them.
2. Mid-November: cut the draft to the certification-under-persistence story; move the fluctuation-channel policy comparison to the appendix or a short paper.
3. December: full experiment freeze; chronological Wikipedia rerun if still needed.
4. January: internal review; SIGIR backup decision by its deadline.
5. February: submit, with the anonymized repository.
