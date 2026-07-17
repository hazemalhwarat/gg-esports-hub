"""
StarCraft II source via the Aligulac API (free).
Get a free API key at http://aligulac.com/about/api/ and set ALIGULAC_KEY.
Reliability: API-based (solid, niche).
"""
import os
import requests

from config import match_priority
from models import Match

BASE = "http://aligulac.com/api/v1/match"
UA = {"User-Agent": "GGNewsAR-Hub/1.0"}


def fetch(limit: int = 30) -> list[Match]:
    key = os.getenv("ALIGULAC_KEY")
    if not key:
        print("[aligulac] skipped: missing ALIGULAC_KEY")
        return []
    try:
        r = requests.get(BASE, params={
            "apikey": key, "limit": limit, "order_by": "-date",
            "format": "json",
        }, headers=UA, timeout=20)
        r.raise_for_status()
        rows = r.json().get("objects", []) or []
    except Exception as e:
        print(f"[aligulac] error: {e}")
        return []

    out = []
    for m in rows:
        pla = (m.get("pla") or {}).get("tag") or "TBD"
        plb = (m.get("plb") or {}).get("tag") or "TBD"
        event = m.get("eventobj") or {}
        tour = event.get("fullname") or m.get("event") or "StarCraft II"
        mid = m.get("id")
        prio = match_priority(pla) or match_priority(plb) or match_priority(tour)
        out.append(Match(
            id=f"aligulac:{mid}",
            game="StarCraft II",
            tournament=tour,
            team_a=pla, team_b=plb,
            score_a=m.get("sca"), score_b=m.get("scb"),
            status="finished",
            start_time=m.get("date", "") or "",
            source="aligulac",
            url=f"http://aligulac.com/results/{mid}/",
            tier="regular",
            is_priority=bool(prio), priority_org=prio,
        ))
    print(f"[aligulac] {len(out)} matches")
    return out
