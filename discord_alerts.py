"""
Discord alerts via webhook (free).
Create a webhook in your server: Channel settings -> Integrations ->
Webhooks -> New Webhook -> copy URL into DISCORD_WEBHOOK_URL.

We alert when:
  - a priority org goes live on Twitch/YouTube (once per stream).
  - a priority-org match appears live (once per match).
De-duplication is handled through store.was_alerted / mark_alerted.
"""
import os
import requests

import store

COLOR_LIVE = 0x9146FF   # purple
COLOR_MATCH = 0x00C2A8  # teal


def _send(embed: dict) -> bool:
    url = os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        return False
    try:
        r = requests.post(url, json={"embeds": [embed]}, timeout=15)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"[discord] send error: {e}")
        return False


def alert_streams(streams):
    for s in streams:
        if not s.is_priority:
            continue
        key = f"stream:{s.id}"
        if store.was_alerted(key):
            continue
        embed = {
            "title": f"🔴 {s.priority_org} live on {s.platform.title()}",
            "description": s.title[:300],
            "url": s.url,
            "color": COLOR_LIVE,
            "fields": [
                {"name": "Channel", "value": s.channel, "inline": True},
                {"name": "Game", "value": s.game or "—", "inline": True},
                {"name": "Viewers", "value": f"{s.viewers:,}", "inline": True},
            ],
        }
        if s.thumbnail:
            embed["thumbnail"] = {"url": s.thumbnail}
        if _send(embed):
            store.mark_alerted(key)
            print(f"[discord] alerted stream {s.id}")


def alert_matches(matches):
    for m in matches:
        if not m.is_priority or m.status != "live":
            continue
        key = f"match:{m.id}"
        if store.was_alerted(key):
            continue
        embed = {
            "title": f"🎮 {m.priority_org} match live — {m.game}",
            "description": f"**{m.team_a}** vs **{m.team_b}**\n{m.tournament}",
            "url": m.url,
            "color": COLOR_MATCH,
        }
        if _send(embed):
            store.mark_alerted(key)
            print(f"[discord] alerted match {m.id}")
