"""Merge the three harvests, dedupe by normalized title, score relevance, write candidates.json and candidates.md."""
import json, re, collections

def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()

BUCKETS = {
    "bandit": r"\bbandits?\b|best[- ]arm|arm identification|pure exploration",
    "structure": r"\bgraph|spectral|cluster|correlat|similar|side[- ]information|structured arms|network|neighbo|smooth|spillover|interference|low[- ]rank|shared structure|meta-?learn|multi-?task|transfer",
    "temporal": r"non-?stationar|restless|autoregress|markov(?!ian decision)|drift|switching|time-?varying|temporal|dynamic|changing|piecewise|rotting|rising|seasonal|time series|forgetting|abrupt",
    "inference": r"confidence sequence|anytime[- ]valid|time-uniform|sequential test|e-?process|e-?value|always[- ]valid|ville|self-normalized|martingale|safe anytime|test martingale|adaptive(?:ly)? collected|inference after adaptive|post-bandit|bandit data",
    "exposure": r"\bbatch|delayed|slate|ranking|recommend|a/b test|online experiment|carryover|interleav",
    "spatiotemporal": r"spatio|kriging|sensor|traffic|gaussian process|kernel|kalman|state[- ]space|linear dynamical",
}
BUCKETS = {k: re.compile(v, re.I) for k, v in BUCKETS.items()}

def load():
    recs = []
    for r in json.load(open("openreview_raw.json")):
        recs.append({"src": "openreview", "venue": r["venue"], "group": r["group"], "title": r["title"], "abstract": r["abstract"],
                     "pdf": r["pdf"], "url": r["forum"], "authors": r["authors"], "keywords": r.get("keywords", []), "area": r.get("area", "")})
    for r in json.load(open("pmlr_raw.json")):
        recs.append({"src": "pmlr", "venue": r["venue"], "title": r["title"], "abstract": r["abstract"], "pdf": r["pdf"],
                     "url": r["abs"], "authors": r["authors"].split(", "), "keywords": [], "area": ""})
    for r in json.load(open("arxiv_raw.json")):
        recs.append({"src": "arxiv", "venue": "arXiv (" + r["comment"][:80] + ")", "title": r["title"], "abstract": r["abstract"],
                     "pdf": r["pdf"], "url": r["id"], "authors": r["authors"], "keywords": [], "area": "", "published": r["published"]})
    for r in json.load(open("openalex_kdd_raw.json")):
        recs.append({"src": "openalex", "venue": f"KDD {r['year']}", "title": r["title"] or "", "abstract": r["abstract"], "pdf": r["pdf"] or (r["doi"] or ""),
                     "url": r["doi"] or "", "authors": [], "keywords": [], "area": ""})
    return recs

recs = load()
merged = {}
for r in recs:
    k = norm(r["title"])
    if k in merged:
        m = merged[k]
        # prefer openreview/pmlr venue labels over arXiv comments
        if m["src"] == "arxiv" and r["src"] != "arxiv":
            r["alt"] = m; merged[k] = r
        else:
            m.setdefault("alt_src", []).append(r["src"] + ":" + r["venue"])
        continue
    merged[k] = r

cands = []
for r in merged.values():
    text = r["title"] + " " + r["abstract"]
    hits = {b: bool(p.search(text)) for b, p in BUCKETS.items()}
    tb = {b: bool(p.search(r["title"])) for b, p in BUCKETS.items()}
    score = 0
    if hits["bandit"]:
        score += 1
        score += 2 * hits["structure"] + 2 * hits["temporal"] + 2 * hits["inference"] + 1 * hits["exposure"] + 1 * hits["spatiotemporal"]
        score += 2 * (tb["structure"] or tb["temporal"] or tb["inference"])
    if hits["inference"]:
        score += 3 + 2 * tb["inference"]
    if hits["temporal"] and hits["spatiotemporal"] and not hits["bandit"]:
        score += 1
    r["hits"] = [b for b, v in hits.items() if v]
    r["score"] = score
    cands.append(r)

cands.sort(key=lambda r: -r["score"])
json.dump(cands, open("candidates.json", "w"), indent=1)
print(len(recs), "records,", len(merged), "unique titles")
print(collections.Counter(min(r["score"], 9) for r in cands))
with open("candidates.md", "w") as f:
    for i, r in enumerate(c for c in cands if c["score"] >= 4):
        f.write(f"{i:4d} [{r['score']}] {r['venue'][:28]:28s} | {r['title'][:110]} | {','.join(r['hits'])}\n")
