"""
CS2 source via HLTV.org (HTML scrape).
HLTV has no public API and sits behind Cloudflare, so this is BEST-EFFORT:
it may return [] when blocked. It never raises — failures are logged and
the rest of the run continues. When you do a live test run, adjust the
selectors below if HLTV's markup has shifted.
Reliability: best-effort (scrape, Cloudflare-protected).
"""
import requests
from bs4 import BeautifulSoup

from config import match_priority
from models import Match

RESULTS_URL = "https://www.hltv.org/results"
UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(limit: int = 30) -> list[Match]:
    try:
        r = requests.get(RESULTS_URL, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"[hltv] blocked/status {r.status_code}")
            return []
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"[hltv] error: {e}")
        return []

    out = []
    for row in soup.select("div.result-con")[:limit]:
        try:
            teams = row.select("div.team")
            scores = row.select("td.result-score span")
            event = row.select_one(".event-name")
            link = row.select_one("a.a-reset")
            if len(teams) < 2:
                continue
            t1 = teams[0].get_text(strip=True)
            t2 = teams[1].get_text(strip=True)
            s1 = int(scores[0].get_text(strip=True)) if len(scores) > 0 else None
            s2 = int(scores[1].get_text(strip=True)) if len(scores) > 1 else None
            tour = event.get_text(strip=True) if event else "CS2"
            href = link.get("href") if link else ""
            url = f"https://www.hltv.org{href}" if href else "https://www.hltv.org"
            prio = match_priority(t1) or match_priority(t2) or match_priority(tour)
            out.append(Match(
                id=f"hltv:{href or t1+t2+tour}",
                game="CS2",
                tournament=tour,
                team_a=t1, team_b=t2, score_a=s1, score_b=s2,
                status="finished",
                start_time="",
                source="hltv",
                url=url,
                tier="regular",
                is_priority=bool(prio), priority_org=prio,
            ))
        except Exception:
            continue
    print(f"[hltv] {len(out)} results")
    return out
