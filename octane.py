"""
Rocket League source via the Octane.gg public API (zsr.octane.gg).
No key required. Docs: https://zsr.octane.gg
Reliability: API-based (solid).
"""
import requests

from config import match_priority
from models import Match

BASE = "https://zsr.octane.gg"
UA = {"User-Agent": "GGNewsAR-Hub/1.0"}


def fetch(limit: int = 40) -> list[Match]:
    try:
        r = requests.get(f"{BASE}/matches", params={
            "sort": "date:desc", "perPage": limit,
        }, headers=UA, timeout=20)
        r.raise_for_status()
        rows = r.json().get("matches", []) or []
    except Exception as e:
        print(f"[octane] error: {e}")
        return []

    out = []
    for m in rows:
        blue = ((m.get("blue") or {}).get("team") or {}).get("team") or {}
        orange = ((m.get("orange") or {}).get("team") or {}).get("team") or {}
        name1 = blue.get("name") or "TBD"
        name2 = orange.get("name") or "TBD"
        s1 = (m.get("blue") or {}).get("score")
        s2 = (m.get("orange") or {}).get("score")
        event = (m.get("event") or {}).get("name") or "Rocket League"
        mid = m.get("_id") or f"{name1}{name2}"
        finished = s1 is not None and s2 is not None
        prio = match_priority(name1) or match_priority(name2) or match_priority(event)
        out.append(Match(
            id=f"octane:{mid}",
            game="Rocket League",
            tournament=event,
            team_a=name1, team_b=name2, score_a=s1, score_b=s2,
            status="finished" if finished else "upcoming",
            start_time=m.get("date", "") or "",
            source="octane",
            url=f"https://octane.gg/matches/{mid}",
            tier="regular",
            is_priority=bool(prio), priority_org=prio,
        ))
    print(f"[octane] {len(out)} matches")
    return out
