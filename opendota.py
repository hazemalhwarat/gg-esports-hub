"""
OpenDota source (free, no API key required).
Pulls recent professional Dota 2 matches. Great, reliable baseline for
the "results" feed. Docs: https://docs.opendota.com
"""
from datetime import datetime, timezone
import requests

from config import match_priority
from models import Match

PRO_MATCHES = "https://api.opendota.com/api/proMatches"


def fetch(limit: int = 40) -> list[Match]:
    try:
        r = requests.get(PRO_MATCHES, timeout=20)
        r.raise_for_status()
        rows = r.json()
    except Exception as e:
        print(f"[opendota] fetch error: {e}")
        return []

    matches: list[Match] = []
    for m in rows[:limit]:
        radiant = m.get("radiant_name") or "TBD"
        dire = m.get("dire_name") or "TBD"
        radiant_win = m.get("radiant_win")
        league = m.get("league_name") or "Dota 2 Pro"
        mid = m.get("match_id")
        start = m.get("start_time")
        start_iso = ""
        if start:
            start_iso = datetime.fromtimestamp(start, tz=timezone.utc).isoformat()

        # OpenDota proMatches are finished games; encode winner via score 1/0
        score_a = score_b = None
        if radiant_win is not None:
            score_a, score_b = (1, 0) if radiant_win else (0, 1)

        prio = match_priority(radiant) or match_priority(dire) or match_priority(league)
        matches.append(Match(
            id=f"opendota:{mid}",
            game="Dota 2",
            tournament=league,
            team_a=radiant,
            team_b=dire,
            score_a=score_a,
            score_b=score_b,
            status="finished",
            start_time=start_iso,
            source="opendota",
            url=f"https://www.opendota.com/matches/{mid}",
            tier="regular",
            is_priority=bool(prio),
            priority_org=prio,
        ))

    print(f"[opendota] {len(matches)} recent pro matches")
    return matches
