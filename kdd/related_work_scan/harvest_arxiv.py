"""Harvest arXiv records whose comment field names a target venue (KDD, COLT, AISTATS, ICML, ICLR, NeurIPS)
and whose title or abstract matches a topic term. Writes arxiv_raw.json."""
import json, re, sys, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET

VENUE_TERMS = ["KDD", "COLT", "AISTATS", "ICML", "ICLR", "NeurIPS"]
TOPIC_TERMS = ['bandit', '"confidence sequence"', '"anytime-valid"', 'restless', '"non-stationary"', 'nonstationary',
               '"time-uniform"', '"sequential testing"', '"correlated arms"', '"spectral bandit"', '"graph bandit"']
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}

def q(query, start):
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": query, "start": start, "max_results": 100, "sortBy": "submittedDate", "sortOrder": "descending"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return ET.fromstring(r.read())
        except Exception as e:  # noqa
            time.sleep(5 + 5 * attempt)
    print("FAIL", url, file=sys.stderr)
    return None

recs = {}
for v in VENUE_TERMS:
    for t in TOPIC_TERMS:
        start = 0
        while True:
            root = q(f"(ti:{t} OR abs:{t}) AND co:{v}", start)
            if root is None:
                break
            entries = root.findall("a:entry", NS)
            for e in entries:
                aid = e.find("a:id", NS).text.strip()
                pub = e.find("a:published", NS).text[:10]
                if pub < "2023-06-01":
                    continue
                comment = (e.find("x:comment", NS).text if e.find("x:comment", NS) is not None else "") or ""
                rec = recs.setdefault(aid, {
                    "id": aid, "pdf": aid.replace("/abs/", "/pdf/"),
                    "title": re.sub(r"\s+", " ", e.find("a:title", NS).text.strip()),
                    "abstract": re.sub(r"\s+", " ", e.find("a:summary", NS).text.strip()),
                    "published": pub, "comment": comment,
                    "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
                    "venue_hits": [], "terms": []})
                rec["venue_hits"].append(v)
                rec["terms"].append(t)
            if len(entries) < 100:
                break
            start += 100
            time.sleep(3)
        time.sleep(3)
    print(v, len(recs), file=sys.stderr)
    json.dump(list(recs.values()), open("arxiv_raw.json", "w"), indent=1)
print(len(recs), "records", file=sys.stderr)
