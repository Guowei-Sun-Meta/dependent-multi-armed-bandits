"""List every paper in the CISS proceedings 2022-2026 from Crossref.

Crossref has no exact container filter, so we page through a container-title
query and keep records whose container title matches one of the CISS volumes.
Output: crossref_raw.json in the working directory (run from a scratch dir).
"""
import json
import time
import urllib.parse
import urllib.request

VOLUMES = {
    2022: "2022 56th Annual Conference on Information Sciences and Systems (CISS)",
    2023: "2023 57th Annual Conference on Information Sciences and Systems (CISS)",
    2024: "2024 58th Annual Conference on Information Sciences and Systems (CISS)",
    2025: "2025 59th Annual Conference on Information Sciences and Systems (CISS)",
    2026: "2026 60th Annual Conference on Information Sciences and Systems (CISS)",
}
API = "https://api.crossref.org/works"
UA = {"User-Agent": "ciss-related-work-scan/1.0 (research use)"}


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)["message"]
        except Exception as exc:  # network hiccup or 429
            print("retry", attempt, exc)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(url)


def harvest(year, title):
    keep, offset = {}, 0
    while True:
        msg = fetch({
            "query.container-title": title,
            "filter": "prefix:10.1109",
            "rows": 1000,
            "offset": offset,
            "sort": "score",
            "select": "DOI,title,author,container-title,page,abstract",
        })
        items = msg["items"]
        for it in items:
            if (it.get("container-title") or [""])[0].strip() == title:
                keep[it["DOI"].lower()] = {
                    "doi": it["DOI"].lower(),
                    "year": year,
                    "title": " ".join((it.get("title") or [""])[0].split()),
                    "authors": [" ".join(filter(None, [a.get("given"), a.get("family")]))
                                for a in it.get("author", [])],
                    "pages": it.get("page"),
                    "abstract": it.get("abstract"),
                }
        # Results are ranked by relevance (a cursor would drop the ranking, so page
        # by offset); stop once a page has no matches.
        if not items or not any((i.get("container-title") or [""])[0].strip() == title for i in items):
            break
        offset += 1000
        time.sleep(1)
    return list(keep.values())


def main():
    out = []
    for year, title in VOLUMES.items():
        recs = harvest(year, title)
        print(year, len(recs))
        out.extend(recs)
    with open("crossref_raw.json", "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
