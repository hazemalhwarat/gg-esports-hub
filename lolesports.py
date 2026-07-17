"""
League of Legends source via the lolesports public API.
No account needed; uses the well-known public web API key.
Endpoints:
  /getLive      -> currently live matches
  /getSchedule  -> upcoming/completed schedule
Reliability: API-based (solid, unofficial-public).
"""
import requests

from config import match_priority
from models import Match

BASE = "https://esports-api.lolesports.com/persisted/gw"
HEADERS = {
    # public web key used by lolesports.com itself
    "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z",
    "User-Agent": "GGNewsAR-Hub/1.0",
}


def _event_to_match(ev, status):
    match = ev.get("match") or {}
    teams = match.get("teams") or []
    if len(teams) < 2:
        return None
    t1, t2 = teams[0], teams[1]
    name1 = t1.get("name") or t1.get("code") or "TBD"
    name2 = t2.get("name") or t2.get("code") or "TBD"
    s1 = (t1.get("result") or {}).get("gameWins")
    s2 = (t2.get("result") or {}).get("gameWins")
    league = (ev.get("league") or {}).get("name") or "LoL"
    block = ev.get("blockName") or ""
    tour = f"{league} {block}".strip()
    mid = match.get("id") or ev.get("id") or f"{name1}{name2}"
    prio = match_priority(name1) or match_priority(name2) or match_priority(tour)
    return Match(
        id=f"lol:{mid}",
        game="LoL",
        tournament=tour,
        team_a=name1, team_b=name2,
        score_a=s1, score_b=s2,
        status=status,
        start_time=ev.get("startTime", "") or "",
        source="lolesports",
        url="https://lolesports.com/schedule",
        tier="regular",
        is_priority=bool(prio), priority_org=prio,
    )


def _live():
    try:
        r = requests.get(f"{BASE}/getLive", params={"hl": "en-US"}, headers=HEADERS, timeout=20)
        r.raise_for_status()
        events = (((r.json().get("data") or {}).get("schedule") or {}).get("events")) or []
        out = [_event_to_match(e, "live") for e in events]
        return [m for m in out if m]
    except Exception as e:
        print(f"[lolesports] live error: {e}")
        return []


def _schedule():
    try:
        r = requests.get(f"{BASE}/getSchedule", params={"hl": "en-US"}, headers=HEADERS, timeout=20)
        r.raise_for_status()
        events = (((r.json().get("data") or {}).get("schedule") or {}).get("events")) or []
        out = []
        for e in events[-40:]:
            state = e.get("state")
            status = "finished" if state == "completed" else ("live" if state == "inProgress" else "upcoming")
            m = _event_to_match(e, status)
            if m:
                out.append(m)
        return out
    except Exception as e:
        print(f"[lolesports] schedule error: {e}")
        return []


def fetch() -> list[Match]:
    seen, out = set(), []
    for m in _live() + _schedule():
        if m.id in seen:
            continue
        seen.add(m.id)
        out.append(m)
    print(f"[lolesports] {len(out)} matches")
    return out
