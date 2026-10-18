# Related-work scan: scripts

The scripts that produced [../related_work_abstracts.md](../related_work_abstracts.md) on 18 October 2026. They use only the standard library, except `extract_intros.py`, which needs `pypdf` (install it in a scratch venv, not the project `.venv`). Run them from a scratch directory, because they download PDFs (untrusted data) into `pdfs/`.

| Script | What it does | Output |
| --- | --- | --- |
| `harvest_openreview.py` | Searches the OpenReview v2 API for 13 topic terms in NeurIPS 2023–2025, ICLR 2024–2026, ICML 2024–2026 and AISTATS 2025–2026, keeping accepted papers only (the venue field excludes submitted, rejected and withdrawn). COLT and KDD are not on OpenReview under any group id we tried | `openreview_raw.json` |
| `harvest_pmlr.py` | Parses the PMLR volume pages for AISTATS 2024–2026 (v238, v258, v300), COLT 2024–2026 (v247, v291, v336) and ICML 2024–2026 (v235, v267, v306); fetches abstracts for titles matching a broad keyword list | `pmlr_raw.json` |
| `harvest_arxiv.py` | arXiv API queries with the venue name in the comment field (`co:KDD` and so on) as a cross-check and for NeurIPS 2026 accepted papers | `arxiv_raw.json` |
| (inline in the session) | OpenAlex `works` queries filtered to the three KDD source ids, 2024–2026, eight topic terms | `openalex_kdd_raw.json` |
| `merge_score.py` | Merges and dedupes by normalized title; scores relevance by topic buckets; writes a screening list | `candidates.json`, `candidates.md` |
| `resolve_arxiv.py` | Finds arXiv versions by title for records whose PDF is behind OpenReview or the ACM DL | updates `selected.json` |
| `extract_intros.py` | Downloads each selected PDF and extracts the abstract and introduction (first four pages, up to the second section heading) | `intros.json` |
| `notes.py` | Our relevance notes, one per kept paper, keyed to the theory labels | — |
| `build_index.py` | Writes the markdown index from `selected.json` and `notes.py` | `related_work_abstracts.md` |

Rate limits: OpenReview allows 180 requests per minute and blocks PDF downloads; arXiv asks for about one request every three seconds; the free OpenAlex budget is about 100 requests per day per IP; DBLP and Semantic Scholar were unusable (bot check and 429s).
