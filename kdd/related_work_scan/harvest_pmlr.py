"""Harvest PMLR volumes: index page -> titles, abs and pdf links; fetch abstracts for titles that
match topic keywords. Writes pmlr_raw.json."""
import html, json, re, sys, time, urllib.request

VOLUMES = {"v238": "AISTATS 2024", "v258": "AISTATS 2025", "v300": "AISTATS 2026",
           "v247": "COLT 2024", "v291": "COLT 2025", "v336": "COLT 2026",
           "v235": "ICML 2024", "v267": "ICML 2025", "v306": "ICML 2026"}
KW = re.compile(r"bandit|confidence|sequential|non-?stationar|restless|anytime|time-uniform|markov|autoregress|"
                r"graph|spatio|temporal|correlat|cluster|drift|switching|changing|time-varying|e-process|"
                r"martingale|ville|adaptive|online learning|exploration|regret|thompson|ucb|kalman|time series|"
                r"recommend|experiment|a/b|causal|delayed", re.I)

def get(url):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lit-scan/0.1"}), timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:  # noqa
            time.sleep(3 + 3 * attempt)
    print("FAIL", url, file=sys.stderr)
    return ""

out = []
for vol, name in VOLUMES.items():
    page = get(f"https://proceedings.mlr.press/{vol}/")
    items = re.findall(r'<p class="title">(.*?)</p>.*?<span class="authors">(.*?)</span>.*?href="(https://proceedings.mlr.press/'
                       + vol + r'/[^"]+\.html)">abs</a>\]\[<a href="([^"]+\.pdf)"', page, re.S)
    print(name, len(items), "papers", file=sys.stderr)
    n = 0
    for title, authors, abs_url, pdf in items:
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        if not KW.search(title):
            continue
        ap = get(abs_url)
        m = re.search(r'<div class="abstract">(.*?)</div>', ap, re.S)
        abstract = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""
        out.append({"venue": name, "title": title, "authors": html.unescape(authors).replace("&nbsp;", " "),
                    "abs": abs_url, "pdf": pdf, "abstract": abstract})
        n += 1
        time.sleep(0.4)
    print(name, n, "fetched", file=sys.stderr)
    json.dump(out, open("pmlr_raw.json", "w"), indent=1)
print(len(out), "records", file=sys.stderr)
