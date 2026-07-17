"""
GG Esports Hub - collector entry point.

Usage:
    python run.py --tier live   # cheap, high-frequency (streams + Dota)
    python run.py --tier full   # everything

The chosen sources come from config.TIERS. Each source degrades gracefully:
a missing API key or a network error just logs and returns [], so one broken
source never takes down the whole run.
"""
import argparse
from datetime import datetime, timezone

from config import TIERS
from models import Snapshot
import store
import discord_alerts

from sources import (
    twitch, youtube, kick,
    startgg, opendota, vlr, lolesports, octane, aligulac,
    hltv, liquipedia,
)

SOURCE_MAP = {
    "twitch": twitch.fetch,
    "youtube": youtube.fetch,
    "kick": kick.fetch,
    "startgg": startgg.fetch,
    "opendota": opendota.fetch,
    "vlr": vlr.fetch,
    "lolesports": lolesports.fetch,
    "octane": octane.fetch,
    "aligulac": aligulac.fetch,
    "hltv": hltv.fetch,
    "liquipedia": liquipedia.fetch,
}


def run(tier: str):
    sources = TIERS.get(tier, TIERS["full"])
    print(f"=== run tier={tier} sources={sources} ===")

    streams, matches, tournaments = [], [], []

    for name in sources:
        fetch = SOURCE_MAP.get(name)
        if not fetch:
            continue
        try:
            result = fetch()
        except Exception as e:
            print(f"[{name}] unexpected error: {e}")
            continue
        for item in result:
            cls = type(item).__name__
            if cls == "Stream":
                streams.append(item)
            elif cls == "Match":
                matches.append(item)
            elif cls == "Tournament":
                tournaments.append(item)

    # Sort: priority first, then by viewers / recency.
    streams.sort(key=lambda s: (not s.is_priority, -s.viewers))
    matches.sort(key=lambda m: (not m.is_priority, m.start_time), reverse=False)

    snapshot = Snapshot(
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        streams=streams,
        matches=matches,
        tournaments=tournaments,
    )
    store.write_snapshot(snapshot)

    # Alerts (no-op if DISCORD_WEBHOOK_URL is unset).
    discord_alerts.alert_streams(streams)
    discord_alerts.alert_matches(matches)
    store.prune_alerted(days=3)

    print(f"=== done: {len(streams)} streams, {len(matches)} matches, "
          f"{len(tournaments)} tournaments ===")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=list(TIERS.keys()), default="full")
    args = ap.parse_args()
    run(args.tier)
