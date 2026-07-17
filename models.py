"""
GG Esports Hub - Unified data models.
Every source normalizes its output into these shapes so the dashboard
only ever sees one consistent schema regardless of where data came from.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Stream:
    id: str                     # stable unique id, e.g. "twitch:teamfalcons"
    platform: str               # "twitch" | "youtube"
    channel: str                # channel login / handle
    title: str
    game: str                   # normalized game label
    viewers: int
    url: str
    thumbnail: str = ""
    is_priority: bool = False   # involves a priority org / channel
    priority_org: Optional[str] = None
    started_at: str = ""        # ISO timestamp if known

    def to_dict(self):
        return asdict(self)


@dataclass
class Match:
    id: str                     # stable unique id per source, e.g. "opendota:78321"
    game: str
    tournament: str
    team_a: str
    team_b: str
    score_a: Optional[int] = None
    score_b: Optional[int] = None
    status: str = "upcoming"    # "upcoming" | "live" | "finished"
    start_time: str = ""        # ISO timestamp
    source: str = ""            # "opendota" | "startgg" | ...
    url: str = ""
    tier: str = "regular"       # "premier" | "regular" (rough importance)
    is_priority: bool = False
    priority_org: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Tournament:
    id: str
    name: str
    game: str
    status: str = "upcoming"    # "upcoming" | "ongoing" | "finished"
    start_time: str = ""
    end_time: str = ""
    source: str = ""
    url: str = ""
    prize: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Snapshot:
    """The full payload the dashboard reads."""
    generated_at: str = ""
    streams: list = field(default_factory=list)
    matches: list = field(default_factory=list)
    tournaments: list = field(default_factory=list)

    def to_dict(self):
        return {
            "generated_at": self.generated_at,
            "streams": [s.to_dict() if hasattr(s, "to_dict") else s for s in self.streams],
            "matches": [m.to_dict() if hasattr(m, "to_dict") else m for m in self.matches],
            "tournaments": [t.to_dict() if hasattr(t, "to_dict") else t for t in self.tournaments],
        }
