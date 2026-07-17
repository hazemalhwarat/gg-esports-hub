"""
start.gg source (free GraphQL API).
Needs STARTGG_TOKEN (https://start.gg/admin/profile/developer -> create token).
Pulls featured / ongoing tournaments across titles. start.gg is the backbone
for open tournaments and the FGC, and covers many titles beyond that.
Docs: https://developer.start.gg
"""
import os
from datetime import datetime, timezone
import requests

from config import normalize_game, STARTGG_PER_PAGE
from models import Tournament

GQL = "https://api.start.gg/gql/alpha"

QUERY = """
query FeaturedTournaments($perPage: Int!, $afterDate: Timestamp!) {
  tournaments(query: {
    perPage: $perPage
    page: 1
    sortBy: "startAt asc"
    filter: { upcoming: true, afterDate: $afterDate }
  }) {
    nodes {
      id
      name
      slug
      startAt
      endAt
      numAttendees
      events { videogame { name } }
    }
  }
}
"""


def fetch() -> list[Tournament]:
    token = os.getenv("STARTGG_TOKEN")
    if not token:
        print("[startgg] skipped: missing STARTGG_TOKEN")
        return []

    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    headers = {"Authorization": f"Bearer {token}"}
    variables = {"perPage": STARTGG_PER_PAGE, "afterDate": now_ts}

    try:
        r = requests.post(GQL, json={"query": QUERY, "variables": variables},
                          headers=headers, timeout=20)
        r.raise_for_status()
        payload = r.json()
        nodes = (payload.get("data", {}) or {}).get("tournaments", {}).get("nodes", []) or []
    except Exception as e:
        print(f"[startgg] fetch error: {e}")
        return []

    tours: list[Tournament] = []
    for n in nodes:
        games = {normalize_game(e["videogame"]["name"])
                 for e in (n.get("events") or []) if e.get("videogame")}
        game_label = ", ".join(sorted(games)) if games else "Other"
        start_iso = end_iso = ""
        if n.get("startAt"):
            start_iso = datetime.fromtimestamp(n["startAt"], tz=timezone.utc).isoformat()
        if n.get("endAt"):
            end_iso = datetime.fromtimestamp(n["endAt"], tz=timezone.utc).isoformat()
        tours.append(Tournament(
            id=f"startgg:{n['id']}",
            name=n.get("name", "Tournament"),
            game=game_label,
            status="upcoming",
            start_time=start_iso,
            end_time=end_iso,
            source="startgg",
            url=f"https://start.gg/{n.get('slug', '')}",
        ))

    print(f"[startgg] {len(tours)} upcoming tournaments")
    return tours
