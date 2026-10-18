"""Harvest accepted papers matching search terms from OpenReview venues (API v2).

Writes openreview_raw.json: one record per (group, note id) with title, abstract,
venue label, pdf url, forum url, keywords, primary area, authors.
"""
import json, sys, time, urllib.request, urllib.parse

GROUPS = [
    "NeurIPS.cc/2023/Conference", "NeurIPS.cc/2024/Conference", "NeurIPS.cc/2025/Conference",
    "ICLR.cc/2024/Conference", "ICLR.cc/2025/Conference", "ICLR.cc/2026/Conference",
    "ICML.cc/2024/Conference", "ICML.cc/2025/Conference", "ICML.cc/2026/Conference",
    "aistats.org/AISTATS/2024/Conference", "aistats.org/AISTATS/2025/Conference", "aistats.org/AISTATS/2026/Conference",
    "learningtheory.org/COLT/2024/Conference", "learningtheory.org/COLT/2025/Conference", "learningtheory.org/COLT/2026/Conference",
    "KDD.org/2024/Research_Track", "KDD.org/2025/Research_Track", "KDD.org/2025/August_Cycle", "KDD.org/2025/February_Cycle",
    "KDD.org/2026/Research_Track", "KDD.org/2026/Research_Track_Cycle_1", "KDD.org/2026/Research_Track_Cycle_2",
    "KDD.org/2026/February_Cycle", "KDD.org/2026/August_Cycle",
]
TERMS = ["bandit", "confidence sequence", "anytime-valid", "restless", "autoregressive",
         "non-stationary", "nonstationary", "correlated arms", "graph-structured", "spectral bandit",
         "time-uniform", "sequential testing", "Markov reward"]
BAD = ("Submitted", "Rejected", "Withdrawn", "Desk", "withdrawn", "rejected", "submitted")

def fetch(url):
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lit-scan/0.1"}), timeout=60) as r:
                time.sleep(1.2)
                return json.load(r)
        except Exception as e:  # noqa
            time.sleep(10 + 10 * attempt)
            err = e
    print("FAIL", url, err, file=sys.stderr)
    return {"notes": []}

records = {}
group_hits = {}
for g in GROUPS:
    for term in TERMS:
        offset = 0
        while True:
            q = urllib.parse.urlencode({"term": term, "content": "all", "group": g, "source": "forum", "limit": 100, "offset": offset})
            data = fetch("https://api2.openreview.net/notes/search?" + q)
            notes = data.get("notes", [])
            for n in notes:
                c = n.get("content", {})
                venue = (c.get("venue") or {}).get("value", "")
                if any(b in venue for b in BAD) or not venue:
                    continue
                key = n["id"]
                rec = records.setdefault(key, {
                    "group": g, "id": key, "forum": "https://openreview.net/forum?id=" + n.get("forum", key),
                    "pdf": "https://openreview.net" + ((c.get("pdf") or {}).get("value") or "") if (c.get("pdf") or {}).get("value") else "",
                    "title": (c.get("title") or {}).get("value", ""),
                    "abstract": (c.get("abstract") or {}).get("value", ""),
                    "venue": venue, "keywords": (c.get("keywords") or {}).get("value", []),
                    "area": (c.get("primary_area") or {}).get("value", ""),
                    "authors": (c.get("authors") or {}).get("value", []),
                    "terms": []})
                rec["terms"].append(term)
            group_hits[g] = group_hits.get(g, 0) + len(notes)
            if len(notes) < 100:
                break
            offset += 100
            time.sleep(0.5)
        time.sleep(0.3)
    print(g, group_hits.get(g, 0), file=sys.stderr)
    json.dump(list(records.values()), open("openreview_raw.json", "w"), indent=1)

json.dump(list(records.values()), open("openreview_raw.json", "w"), indent=1)
print(len(records), "records", file=sys.stderr)
