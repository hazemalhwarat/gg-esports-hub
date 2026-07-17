"""
Twitch source (official Helix API, free).
Needs TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET (create an app at
https://dev.twitch.tv/console/apps). We use the client-credentials
(app access token) flow, which is enough for public stream data.
"""
import os
import requests

from config import TWITCH_CHANNELS, normalize_game, match_priority
from models import Stream

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
STREAMS_URL = "https://api.twitch.tv/helix/streams"


def _get_app_token(client_id: str, client_secret: str) -> str | None:
    try:
        r = requests.post(TOKEN_URL, params={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }, timeout=15)
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception as e:
        print(f"[twitch] token error: {e}")
        return None


def fetch() -> list[Stream]:
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("[twitch] skipped: missing TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET")
        return []

    token = _get_app_token(client_id, client_secret)
    if not token:
        return []

    headers = {"Client-ID": client_id, "Authorization": f"Bearer {token}"}
    streams: list[Stream] = []

    # Helix accepts up to 100 user_login params per call.
    for i in range(0, len(TWITCH_CHANNELS), 100):
        batch = TWITCH_CHANNELS[i:i + 100]
        params = [("user_login", c) for c in batch] + [("first", 100)]
        try:
            r = requests.get(STREAMS_URL, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json().get("data", [])
        except Exception as e:
            print(f"[twitch] fetch error: {e}")
            continue

        for s in data:
            login = s.get("user_login", "")
            game = normalize_game(s.get("game_name", ""))
            title = s.get("title", "")
            prio = match_priority(login) or match_priority(title)
            thumb = (s.get("thumbnail_url", "")
                     .replace("{width}", "440").replace("{height}", "248"))
            streams.append(Stream(
                id=f"twitch:{login}",
                platform="twitch",
                channel=s.get("user_name", login),
                title=title,
                game=game,
                viewers=int(s.get("viewer_count", 0)),
                url=f"https://twitch.tv/{login}",
                thumbnail=thumb,
                is_priority=bool(prio),
                priority_org=prio,
                started_at=s.get("started_at", ""),
            ))

    print(f"[twitch] {len(streams)} live channels")
    return streams
