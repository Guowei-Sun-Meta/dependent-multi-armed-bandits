"""Collect the Wikipedia attention panel: programming-language articles, daily views, hyperlinks.

Usage (from the repo root):
    .venv/bin/python -I experiments/wikipedia/collect.py

1. Articles: every main-namespace link on "List of programming languages".
2. Daily user page views (all access), 1 January 2022 to 31 December 2025, from the Wikimedia
   REST API (public, no login).
3. Keep the N most-viewed articles (by median daily views) with views on every day.
4. Hyperlinks among the kept articles (MediaWiki links API), symmetrized: the web graph.
Raw responses are cached in data/wikipedia/ (git-ignored); the panel and graph are saved
to research/claude_opus_10_09/wikipedia/data/.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "wikipedia"
OUT = ROOT / "research" / "claude_opus_10_09" / "wikipedia" / "data"
UA = "dependent-mab-research/0.1 (https://github.com/Guowei-Sun-Meta/dependent-multi-armed-bandits)"
START, END = "20220101", "20251231"
N_KEEP = 150
LIST_PAGE = "List of programming languages"


def get_json(url: str, tries: int = 4):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            if "404" in str(e):
                return None
            time.sleep(1.5 * (k + 1))
    return None


def list_links(title: str) -> list[str]:
    links, cont = [], {}
    while True:
        params = {"action": "query", "titles": title, "prop": "links", "plnamespace": 0, "pllimit": "max",
                  "format": "json", **cont}
        d = get_json("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))
        for page in d["query"]["pages"].values():
            links += [l["title"] for l in page.get("links", [])]
        if "continue" not in d:
            return links
        cont = d["continue"]


def daily_views(title: str) -> pd.Series | None:
    cache = RAW / "views" / (urllib.parse.quote(title, safe="") + ".json")
    if cache.exists():
        d = json.loads(cache.read_text())
    else:
        art = urllib.parse.quote(title.replace(" ", "_"), safe="")
        d = get_json(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/"
                     f"all-access/user/{art}/daily/{START}/{END}")
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(d))
        time.sleep(0.05)
    if not d or "items" not in d:
        return None
    return pd.Series({it["timestamp"][:8]: it["views"] for it in d["items"]}, name=title)


def hyperlinks(titles: list[str]) -> list[tuple[str, str]]:
    keep, edges = set(titles), []
    for i in range(0, len(titles), 50):
        batch, cont = titles[i:i + 50], {}
        while True:
            params = {"action": "query", "titles": "|".join(batch), "prop": "links", "plnamespace": 0,
                      "pllimit": "max", "redirects": 1, "format": "json", **cont}
            d = get_json("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))
            for page in d["query"]["pages"].values():
                for l in page.get("links", []):
                    if l["title"] in keep and l["title"] != page["title"]:
                        edges.append((page["title"], l["title"]))
            if "continue" not in d:
                break
            cont = d["continue"]
    return edges


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    titles = sorted(set(list_links(LIST_PAGE)))
    print(f"{len(titles)} linked articles", flush=True)
    days = pd.date_range(START, END).strftime("%Y%m%d")
    series = []
    for k, t in enumerate(titles):
        s = daily_views(t)
        if s is not None and s.reindex(days).notna().all():
            series.append(s.reindex(days))
        if k % 100 == 0:
            print(f"views {k}/{len(titles)}; complete so far {len(series)}", flush=True)
    panel = pd.concat(series, axis=1)
    keep = panel.median().sort_values(ascending=False).index[:N_KEEP]
    panel = panel[keep]
    panel.index.name = "date"
    panel.to_csv(OUT / "views.csv")
    edges = hyperlinks(list(keep))
    pd.DataFrame(edges, columns=["source", "target"]).drop_duplicates().to_csv(OUT / "links.csv", index=False)
    meta = {"list_page": LIST_PAGE, "linked_articles": len(titles), "complete_series": len(series),
            "kept": N_KEEP, "days": len(days), "start": START, "end": END, "directed_links": len(edges)}
    (OUT / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
