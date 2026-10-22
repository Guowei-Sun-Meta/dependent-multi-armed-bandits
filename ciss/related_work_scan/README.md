# Related-work scan: scripts

The scripts that produced [../related_work_abstracts.md](../related_work_abstracts.md) on 22 October 2026. Standard library only. Run them in order from a scratch directory, which receives the intermediate JSON:

| Script | What it does | Output |
| --- | --- | --- |
| `harvest_crossref.py` | Lists every Crossref record in the CISS 2022–2026 IEEE volumes. Crossref has no exact container filter, so it pages a container-title query by offset (a cursor drops the relevance ranking) and keeps exact container matches | `crossref_raw.json` |
| `harvest_abstracts.py` | Attaches verbatim abstracts from OpenAlex by DOI (rebuilt from the inverted index), and searches arXiv comment fields for preprints of CISS papers | `records.json` |
| `build_index.py` | Holds the hand-screened selection and our relevance notes; writes the markdown index | `../related_work_abstracts.md` |

```
cd <scratch> && python3 <repo>/ciss/related_work_scan/harvest_crossref.py
python3 <repo>/ciss/related_work_scan/harvest_abstracts.py
python3 <repo>/ciss/related_work_scan/build_index.py <repo>/ciss
```

Gaps: CISS 2026 has no proceedings in Crossref or OpenAlex yet; the CISS sites and IEEE Xplore refuse automated access, so full texts were not read. The 2026 entry in `VOLUMES` is a guess at the volume title; correct it once IEEE Xplore lists the proceedings.
