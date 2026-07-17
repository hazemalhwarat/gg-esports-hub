"""
Valorant source via vlrggapi (community-hosted free REST wrapper over VLR.gg).
No key required. Endpoints:
  /match?q=live_score , /match?q=upcoming , /match?q=results
Docs: https://github.com/axsddlr/vlrggapi

Reliability: API-based (solid). If the public instance is down, this source
just returns [] and the rest of the run continues.
"""
import requests

from config import match_priority
from models import Match

BASE = "https://vlrggapi.vercel.app/match"
UA = {"User-Agent": "GGNewsAR-Hub/1.0"}


def _seg(seg, status):
    t1 = (seg.get("team1") or "TBD").strip()
    t2 = (seg.get("team2") or "TBD").strip()
    event = seg.get("match_event") or seg.get("tournament_name") or "Valorant"
    series = seg.get("match_series") or ""
    tour = f"{event} {series}".strip()
    url = seg.get("match_page") or ""
    if url and url.startswith("/"):
        url = "https://www.vlr.gg" + url
    sa = _int(seg.get("score1"))
    sb = _int(seg.get("score2"))
    prio = match_priority(t1) or match_priority(t2) or match_priority(tour)
    return Match(
        id=f"vlr:{url or t1+t2+series}",
        game="Valorant",
        tournament=tour,
        team_a=t1, team_b=t2, score_a=sa, score_b=sb,
        status=status,
        start_time=seg.get("unix_timestamp", "") or "",
        source="vlr",
        url=url or "https://www.vlr.gg",
        tier="regular",
        is_priority=bool(prio), priority_org=prio,
    )


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _pull(q, status):
    try:
        r = requests.get(BASE, params={"q": q}, headers=UA, timeout=20)
        r.raise_for_status()
        segs = (r.json().get("data", {}) or {}).get("segments", []) or []
        return [_seg(s, status) for s in segs]
    except Exception as e:
        print(f"[vlr] {q} error: {e}")
        return []


def fetch() -> list[Match]:
    out = _pull("live_score", "live") + _pull("upcoming", "upcoming") + _pull("results", "finished")
    print(f"[vlr] {len(out)} matches")
    return out
