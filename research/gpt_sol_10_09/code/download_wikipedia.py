"""Acquire a small, frozen Wikipedia attention experiment with historical graphs.

Sequential public API requests; raw responses cached. Article choices are fixed
before fetching test values. The graph uses the final revision before 2024,
not current links. No clickstream bulk download is needed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PANELS = {
    "astronomy": ["Sun", "Moon", "Mars", "Venus", "Jupiter", "Saturn", "Mercury_(planet)",
                  "Neptune", "Uranus", "Earth", "Solar_System", "Milky_Way", "Galaxy",
                  "Black_hole", "Supernova", "Hubble_Space_Telescope", "James_Webb_Space_Telescope",
                  "International_Space_Station", "NASA", "SpaceX", "Apollo_11", "Falcon_9",
                  "Space_Shuttle", "Artemis_program"],
    "football": ["UEFA_Champions_League", "FIFA_World_Cup", "Premier_League", "Manchester_United_F.C.",
                 "Manchester_City_F.C.", "Liverpool_F.C.", "Real_Madrid_CF", "FC_Barcelona",
                 "FC_Bayern_Munich", "Borussia_Dortmund", "Arsenal_F.C.", "Chelsea_F.C.",
                 "Juventus_FC", "Paris_Saint-Germain_FC", "Atlético_Madrid", "AC_Milan", "Inter_Milan",
                 "Tottenham_Hotspur_F.C.", "Everton_F.C.", "Cristiano_Ronaldo", "Lionel_Messi",
                 "Kylian_Mbappé", "Erling_Haaland", "UEFA_European_Championship"],
}
UA = "dependent-mab/0.1 (https://github.com/Guowei-Sun-Meta/dependent-multi-armed-bandits) Python-urllib"


def fetch(url, path):
    if path.exists():
        return json.loads(path.read_text())
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                content = response.read()
            value = json.loads(content)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            time.sleep(2.)
            return value
        except Exception as error:
            if attempt == 3:
                raise
            delay = 10*2**attempt
            retry = getattr(error, "headers", {}).get("Retry-After")
            if retry and retry.isdigit():
                delay = max(delay, min(int(retry), 60))
            print(f"Public API retry after {type(error).__name__}; waiting {delay}s", flush=True)
            time.sleep(delay)


def main(output):
    raw = output / "raw"
    output.mkdir(parents=True, exist_ok=True)
    # Written first, before any test data is requested.
    (output / "frozen_panels.json").write_text(json.dumps(PANELS, ensure_ascii=False, indent=2)+"\n")
    manifest = {"status": "observed_public_attention_panel", "graph_cutoff": "2023-12-31T23:59:59Z",
                "train_range": ["2024-01-01", "2024-12-31"], "test_range": ["2025-01-01", "2025-06-30"],
                "views_license": "CC0 1.0", "revision_license": "Wikipedia attribution/share-alike terms",
                "view_agent": "user", "access": "all-access", "user_agent": UA, "articles": []}
    for panel, titles in PANELS.items():
        graph = []
        canonical = {x.replace("_", " ").casefold(): x for x in titles}
        for index, title in enumerate(titles):
            stem = f"{panel}_{index:02d}"
            views_url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
                         "en.wikipedia.org/all-access/user/"+urllib.parse.quote(title, safe="")+
                         "/daily/2024010100/2025063000")
            view_path = raw / (stem+"_views.json")
            view = fetch(views_url, view_path)
            params = {"action": "query", "format": "json", "prop": "revisions", "titles": title,
                      "rvstart": manifest["graph_cutoff"], "rvdir": "older", "rvlimit": 1,
                      "rvprop": "timestamp|ids|content", "rvslots": "main"}
            revision_url = "https://en.wikipedia.org/w/api.php?"+urllib.parse.urlencode(params)
            revision_path = raw / (stem+"_revision.json")
            revision = fetch(revision_url, revision_path)
            pages = list(revision["query"]["pages"].values())
            if len(pages) != 1 or "revisions" not in pages[0]:
                raise ValueError(f"No pre-2024 revision for {title}; do not replace based on test outcomes")
            rev = pages[0]["revisions"][0]
            if rev["timestamp"] > manifest["graph_cutoff"]:
                raise ValueError("Graph chronology failure")
            text = rev["slots"]["main"]["*"]
            linked = set()
            for target in re.findall(r"\[\[([^\]|#]+)", text):
                key = target.strip().replace("_", " ").casefold()
                if key in canonical and canonical[key] != title:
                    linked.add(canonical[key])
            graph.extend([[title, target] for target in sorted(linked)])
            item = {"panel": panel, "title": title, "index": index, "page_id": pages[0]["pageid"],
                    "revision_id": rev["revid"], "revision_timestamp": rev["timestamp"],
                    "is_redirect_revision": bool(re.match(r"\s*#redirect", text, flags=re.I)),
                    "views_url": views_url, "revision_url": revision_url,
                    "view_file": str(view_path.relative_to(ROOT)), "revision_file": str(revision_path.relative_to(ROOT)),
                    "views_sha256": hashlib.sha256(view_path.read_bytes()).hexdigest(),
                    "revision_sha256": hashlib.sha256(revision_path.read_bytes()).hexdigest(),
                    "days_returned": len(view["items"]), "within_panel_links": len(linked)}
            manifest["articles"].append(item)
            print(f"{panel} {index+1}/24: {title}, {item['days_returned']} days, {len(linked)} historical links", flush=True)
        (output / (panel+"_historical_links.json")).write_text(json.dumps(graph, ensure_ascii=False, indent=2)+"\n")
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data/wikipedia")
    main(parser.parse_args().output)
