"""Attach abstracts and open PDFs to the Crossref CISS list, and add arXiv-only CISS papers.

1. OpenAlex, by DOI in batches of 50: verbatim abstract (rebuilt from the
   inverted index) and any open-access PDF location.
2. arXiv, comment field mentioning CISS: catches preprints of CISS papers,
   including CISS 2026, whose proceedings are not yet in Crossref.
Input crossref_raw.json; output records.json (working directory).
"""
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "ciss-related-work-scan/1.0 (research use)"}
ATOM = "{http://www.w3.org/2005/Atom}"


def get(url, retries=5):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as exc:
            print("retry", attempt, exc)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(url)


def norm(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def rebuild(inv):
    if not inv:
        return None
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)


def openalex(records):
    by_doi = {r["doi"]: r for r in records}
    dois = list(by_doi)
    for k in range(0, len(dois), 50):
        chunk = "|".join("https://doi.org/" + d for d in dois[k:k + 50])
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
            "filter": "doi:" + chunk, "per_page": 50,
            "select": "doi,abstract_inverted_index,best_oa_location,locations,cited_by_count"})
        for w in json.loads(get(url))["results"]:
            r = by_doi.get((w["doi"] or "").replace("https://doi.org/", "").lower())
            if r is None:
                continue
            r["abstract"] = rebuild(w["abstract_inverted_index"])
            r["abstract_source"] = "OpenAlex" if r["abstract"] else None
            r["cited_by"] = w.get("cited_by_count")
            for loc in w.get("locations") or []:
                if loc.get("pdf_url") and "arxiv" in loc["pdf_url"]:
                    r["arxiv_pdf"] = loc["pdf_url"]
        time.sleep(0.5)


def arxiv_ciss():
    """arXiv records whose comment names CISS (abstract and PDF are open)."""
    out, start = [], 0
    while True:
        q = urllib.parse.urlencode({"search_query": 'co:CISS OR co:"Information Sciences and Systems"',
                                    "start": start, "max_results": 200,
                                    "sortBy": "submittedDate", "sortOrder": "descending"})
        root = ET.fromstring(get("http://export.arxiv.org/api/query?" + q))
        entries = root.findall(ATOM + "entry")
        for e in entries:
            comment = e.find("{http://arxiv.org/schemas/atom}comment")
            comment = comment.text if comment is not None else ""
            year = re.search(r"20(2[2-6])", comment or "")
            if not re.search(r"CISS|Information Sciences and Systems", comment or ""):
                continue
            out.append({
                "arxiv_id": e.find(ATOM + "id").text.rsplit("/", 1)[-1],
                "title": " ".join(e.find(ATOM + "title").text.split()),
                "authors": [a.find(ATOM + "name").text for a in e.findall(ATOM + "author")],
                "abstract": " ".join(e.find(ATOM + "summary").text.split()),
                "comment": " ".join(comment.split()),
                "published": e.find(ATOM + "published").text[:10],
                "comment_year": int("20" + year.group(1)) if year else None,
            })
        if len(entries) < 200 or entries[-1].find(ATOM + "published").text[:4] < "2021":
            break
        start += 200
        time.sleep(3)
    return out


def main():
    records = json.load(open("crossref_raw.json"))
    for r in records:
        r["source"] = "IEEE Xplore (Crossref)"
    openalex(records)
    ax = arxiv_ciss()
    print("arXiv CISS-comment records:", len(ax))
    by_title = {norm(r["title"]): r for r in records}
    for a in ax:
        r = by_title.get(norm(a["title"]))
        if r:
            r["arxiv_id"] = a["arxiv_id"]
            if not r.get("abstract"):
                r["abstract"], r["abstract_source"] = a["abstract"], "arXiv"
        elif (re.search(r"Information Sciences and Systems \(CISS\)|CISS 202[2-6]", a["comment"])
              and 2022 <= (a["comment_year"] or 0) <= 2026 and "in part" not in a["comment"]):
            # Keeps only preprints that name a CISS 2022-2026 volume; journal
            # versions "presented in part" and other "CISS" symposia are dropped.
            records.append({"doi": None, "year": a["comment_year"] or int(a["published"][:4]),
                            "title": a["title"], "authors": a["authors"], "abstract": a["abstract"],
                            "abstract_source": "arXiv", "arxiv_id": a["arxiv_id"],
                            "comment": a["comment"], "source": "arXiv (comment names CISS)"})
    print("records:", len(records), "with abstract:", sum(1 for r in records if r.get("abstract")))
    json.dump(records, open("records.json", "w"), indent=1)


if __name__ == "__main__":
    main()
