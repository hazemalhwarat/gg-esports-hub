"""
Kick source (free public API). Expands stream coverage beyond Twitch/YouTube.
No key required, but Kick sits behind Cloudflare and may rate-limit; each
channel is checked independently and failures are skipped.
Reliability: best-effort (public endpoint, occasional Cloudflare blocks).
"""
import requests

from config import KICK_CHANNELS, normalize_game, match_priority
from models import Stream

BASE = "https://kick.com/api/v2/channels"
UA = {"User-Agent": "Mozilla/5.0 (GGNewsAR-Hub/1.0)", "Accept": "application/json"}


def fetch() -> list[Stream]:
    streams = []
    for slug in KICK_CHANNELS:
        try:
            r = requests.get(f"{BASE}/{slug}", headers=UA, timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
        except Exception as e:
            print(f"[kick] {slug} error: {e}")
            continue

        livestream = data.get("livestream")
        if not livestream or not livestream.get("is_live"):
            continue

        title = livestream.get("session_title", "")
        cats = livestream.get("categories") or []
        game = normalize_game(cats[0].get("name", "")) if cats else "Other"
        viewers = int(livestream.get("viewer_count", 0))
        username = (data.get("user") or {}).get("username", slug)
        thumb = (livestream.get("thumbnail") or {}).get("url", "")
        prio = match_priority(username) or match_priority(title)
        streams.append(Stream(
            id=f"kick:{slug}",
            platform="kick",
            channel=username,
            title=title,
            game=game,
            viewers=viewers,
            url=f"https://kick.com/{slug}",
            thumbnail=thumb,
            is_priority=bool(prio), priority_org=prio,
        ))
    print(f"[kick] {len(streams)} live channels")
    return streams
