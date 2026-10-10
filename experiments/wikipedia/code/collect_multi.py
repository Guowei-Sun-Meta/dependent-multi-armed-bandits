"""Collect a multi-domain Wikipedia attention panel: six communities with distinct rhythms.

Usage (from the repo root):
    .venv/bin/python -I experiments/wikipedia/code/collect_multi.py

Hypothesis tested downstream: in the single-domain panel (programming languages) shocks were
shared domain-wide, so hyperlinks could add nothing beyond a common factor. With several
communities whose attention follows different calendars (NFL autumn Sundays, NBA and MLB
seasons, Premier League weekends, news-driven countries, weekday programming languages),
shocks should be shared within communities, and hyperlinks, which mostly stay within a
community, should carry correlation that a single common factor cannot.

Domains (25 articles each: the most viewed by median daily views with complete data):
NFL and NBA teams (listed explicitly; their categories hold only subcategories), MLB teams
(Category:Major League Baseball teams), Premier League clubs (Category:Premier League clubs),
UN member states (Category:Member states of the United Nations), programming languages
(the single-domain panel). Views: 1 January 2022 to 31 December 2025. Graph: hyperlinks.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect import END, START, daily_views, get_json, hyperlinks  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1] / "data" / "six_domains"
SINGLE = Path(__file__).resolve().parents[1] / "data" / "one_domain" / "views.csv"
PER_DOMAIN = 25

NFL = ["Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills", "Carolina Panthers",
       "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns", "Dallas Cowboys", "Denver Broncos",
       "Detroit Lions", "Green Bay Packers", "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars",
       "Kansas City Chiefs", "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
       "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants", "New York Jets",
       "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers", "Seattle Seahawks",
       "Tampa Bay Buccaneers", "Tennessee Titans", "Washington Commanders"]
NBA = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
       "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors",
       "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
       "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
       "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
       "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"]
CATEGORIES = {"MLB": "Major League Baseball teams", "Premier League": "Premier League clubs",
              "Countries": "Member states of the United Nations"}


def category_pages(cat: str) -> list[str]:
    params = {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{cat}", "cmtype": "page",
              "cmlimit": "max", "format": "json"}
    d = get_json("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params))
    titles = [m["title"] for m in d["query"]["categorymembers"]]
    return [t for t in titles if not t.startswith(("List of", "Performance record", "Member states"))]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    days = pd.date_range(START, END).strftime("%Y%m%d")
    candidates = {"NFL": NFL, "NBA": NBA, **{k: category_pages(v) for k, v in CATEGORIES.items()}}
    frames, domain_of, stats = [], {}, {}
    for dom, titles in candidates.items():
        series = []
        for t in titles:
            s = daily_views(t)
            if s is not None and s.reindex(days).notna().all():
                series.append(s.reindex(days))
        panel = pd.concat(series, axis=1)
        keep = panel.median().sort_values(ascending=False).index[:PER_DOMAIN]
        frames.append(panel[keep])
        domain_of.update({t: dom for t in keep})
        stats[dom] = {"candidates": len(titles), "complete": len(series), "kept": len(keep)}
        print(dom, stats[dom], flush=True)
    single = pd.read_csv(SINGLE, index_col="date")
    single.index = single.index.astype(str)
    keep = single.median().sort_values(ascending=False).index[:PER_DOMAIN]
    frames.append(single[keep].reindex(days))
    domain_of.update({t: "Programming languages" for t in keep})
    stats["Programming languages"] = {"candidates": single.shape[1], "complete": single.shape[1], "kept": len(keep)}
    views = pd.concat(frames, axis=1)
    views.index.name = "date"
    views.to_csv(OUT / "views.csv")
    pd.Series(domain_of, name="domain").rename_axis("title").to_csv(OUT / "domains.csv")
    edges = hyperlinks(list(views.columns))
    pd.DataFrame(edges, columns=["source", "target"]).drop_duplicates().to_csv(OUT / "links.csv", index=False)
    meta = {"domains": stats, "articles": views.shape[1], "days": views.shape[0], "directed_links": len(edges),
            "start": START, "end": END}
    (OUT / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
