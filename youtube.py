"""
YouTube source (official Data API v3, free quota = 10,000 units/day).
Needs YOUTUBE_API_KEY (https://console.cloud.google.com -> enable
"YouTube Data API v3" -> create API key).

Note on quota: search.list costs 100 units/call. We resolve each @handle
to a channelId once and cache it in youtube_cache.json to avoid repeat
resolves. Keep the channel list focused so you stay inside the free quota.
"""
import os
import json
import requests

from config import YOUTUBE_CHANNELS, normalize_game, match_priority
from models import Stream

BASE = "https://www.googleapis.com/youtube/v3"
CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "youtube_cache.json")


def _load_cache() -> dict:
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"[youtube] cache save error: {e}")


def _resolve_channel_id(entry: str, key: str, cache: dict) -> str | None:
    if entry.startswith("UC"):
        return entry
    if entry in cache:
        return cache[entry]
    handle = entry.lstrip("@")
    try:
        r = requests.get(f"{BASE}/channels", params={
            "part": "id", "forHandle": handle, "key": key,
        }, timeout=15)
        r.raise_for_status()
        items = r.json().get("items", [])
        if items:
            cid = items[0]["id"]
            cache[entry] = cid
            return cid
    except Exception as e:
        print(f"[youtube] resolve error for {entry}: {e}")
    return None


def fetch() -> list[Stream]:
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        print("[youtube] skipped: missing YOUTUBE_API_KEY")
        return []

    cache = _load_cache()
    streams: list[Stream] = []

    for entry in YOUTUBE_CHANNELS:
        cid = _resolve_channel_id(entry, key, cache)
        if not cid:
            continue
        try:
            r = requests.get(f"{BASE}/search", params={
                "part": "snippet", "channelId": cid, "eventType": "live",
                "type": "video", "key": key, "maxResults": 1,
            }, timeout=15)
            r.raise_for_status()
            items = r.json().get("items", [])
        except Exception as e:
            print(f"[youtube] search error for {entry}: {e}")
            continue

        if not items:
            continue

        it = items[0]
        vid = it["id"].get("videoId")
        snip = it.get("snippet", {})
        title = snip.get("title", "")
        channel_name = snip.get("channelTitle", entry)
        thumb = snip.get("thumbnails", {}).get("high", {}).get("url", "")
        prio = match_priority(channel_name) or match_priority(title)

        # optional viewer count via videos.list liveStreamingDetails
        viewers = 0
        try:
            vr = requests.get(f"{BASE}/videos", params={
                "part": "liveStreamingDetails", "id": vid, "key": key,
            }, timeout=15)
            vr.raise_for_status()
            v_items = vr.json().get("items", [])
            if v_items:
                cc = v_items[0].get("liveStreamingDetails", {}).get("concurrentViewers")
                viewers = int(cc) if cc else 0
        except Exception:
            pass

        streams.append(Stream(
            id=f"youtube:{vid}",
            platform="youtube",
            channel=channel_name,
            title=title,
            game=normalize_game(""),  # YouTube doesn't tag the game reliably
            viewers=viewers,
            url=f"https://www.youtube.com/watch?v={vid}",
            thumbnail=thumb,
            is_priority=bool(prio),
            priority_org=prio,
        ))

    _save_cache(cache)
    print(f"[youtube] {len(streams)} live channels")
    return streams
