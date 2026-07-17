"""
Liquipedia universal source — the spine that makes "all games" real.

Liquipedia covers every esports title with a consistent structure, so one
module here can pull matches for any game just by adding its wiki name to
LIQUIPEDIA_WIKIS in config.py (counterstrike, dota2, valorant, rainbowsix,
rocketleague, mobilelegends, honorofkings, pubgmobile, freefire, ...).

Method: the free MediaWiki parse API on each wiki's Main Page match ticker.
This is BEST-EFFORT scraping of rendered HTML (the structured LPDB API is
Enterprise-only). It never raises and returns [] on any problem.

IMPORTANT — Liquipedia API terms (respected here):
  - descriptive User-Agent with contact info (edit LP_UA below)
  - max 1 parse request every 2 seconds, no concurrency
See: https://liquipedia.net/api-terms-of-use
"""
import time
import requests
from bs4 import BeautifulSoup

from config import LIQUIPEDIA_WIKIS, normalize_game, match_priority
from models import Match

# EDIT THIS: put your real contact so Liquipedia can reach you if needed.
LP_UA = {"User-Agent": "GGNewsAR-Hub/1.0 (contact: ggnewsar@example.com)"}
RATE_LIMIT_SECONDS = 2.1


def _parse_wiki(wiki: str) -> list[Match]:
    url = f"https://liquipedia.net/{wiki}/api.php"
    params = {
        "action": "parse", "page": "Main Page",
        "prop": "text", "format": "json",
    }
    try:
        r = requests.get(url, params=params, headers=LP_UA, timeout=25)
        r.raise_for_status()
        html = r.json().get("parse", {}).get("text", {}).get("*", "")
    except Exception as e:
        print(f"[liquipedia/{wiki}] error: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    game = normalize_game(wiki)
    out = []

    # Match ticker blocks use the infobox_matches_content table structure.
    for tbl in soup.select("table.infobox_matches_content"):
        try:
            left = tbl.select_one(".team-left")
            right = tbl.select_one(".team-right")
            if not left or not right:
                continue
            t1 = left.get_text(" ", strip=True) or "TBD"
            t2 = right.get_text(" ", strip=True) or "TBD"
            versus = tbl.select_one(".versus")
            score = versus.get_text(" ", strip=True) if versus else ""
            tour_el = tbl.select_one(".league-icon-small-image a, .match-filler a")
            tour = tour_el.get("title") if tour_el and tour_el.get("title") else game
            key = f"{wiki}:{t1}:{t2}:{tour}"
            prio = match_priority(t1) or match_priority(t2) or match_priority(tour)
            out.append(Match(
                id=f"liquipedia:{key}",
                game=game,
                tournament=tour,
                team_a=t1, team_b=t2,
                status="upcoming",
                source="liquipedia",
                url=f"https://liquipedia.net/{wiki}/",
                tier="regular",
                is_priority=bool(prio), priority_org=prio,
            ))
        except Exception:
            continue
    print(f"[liquipedia/{wiki}] {len(out)} matches")
    return out


def fetch() -> list[Match]:
    out = []
    for i, wiki in enumerate(LIQUIPEDIA_WIKIS):
        if i:
            time.sleep(RATE_LIMIT_SECONDS)  # respect Liquipedia rate limit
        out.extend(_parse_wiki(wiki))
    print(f"[liquipedia] {len(out)} matches across {len(LIQUIPEDIA_WIKIS)} wikis")
    return out
