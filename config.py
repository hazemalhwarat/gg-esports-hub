"""
GG Esports Hub - Configuration
All tunable settings in one place: priority orgs, channel seed lists,
game map, and collection tiers.
"""

# ---------------------------------------------------------------------------
# Priority organizations (Arab / MENA focus).
# Any match or stream involving these names is flagged is_priority=True,
# highlighted in the dashboard, and can trigger Discord alerts.
# Each entry: canonical name -> list of aliases used for loose matching.
# ---------------------------------------------------------------------------
PRIORITY_ORGS = {
    "Team Falcons": ["falcons", "team falcons"],
    "Twisted Minds": ["twisted minds", "twisted", "tm"],
    "Geekay Esports": ["geekay", "geekay esports", "gk"],
    "Nigma Galaxy": ["nigma", "nigma galaxy"],
    "Team Vision": ["team vision", "vision esports"],
    "Anubis Gaming": ["anubis", "anubis gaming"],
    "The Ultimates": ["the ultimates", "ultimates"],
    "Villainous": ["villainous", "villainous esports"],
}


def flatten_priority_aliases():
    """Return a lowercase alias -> canonical-name map for fast lookup."""
    out = {}
    for canonical, aliases in PRIORITY_ORGS.items():
        out[canonical.lower()] = canonical
        for a in aliases:
            out[a.lower()] = canonical
    return out


PRIORITY_ALIAS_MAP = flatten_priority_aliases()


def match_priority(text: str):
    """Return the canonical priority org name if text mentions one, else None."""
    if not text:
        return None
    low = text.lower()
    # longest aliases first to avoid partial collisions (e.g. "tm")
    for alias in sorted(PRIORITY_ALIAS_MAP.keys(), key=len, reverse=True):
        if len(alias) <= 2:
            # ultra-short aliases only match as standalone tokens
            if alias in low.split():
                return PRIORITY_ALIAS_MAP[alias]
        elif alias in low:
            return PRIORITY_ALIAS_MAP[alias]
    return None


# ---------------------------------------------------------------------------
# Twitch channel seed list (login names, lowercase).
# Tournament / broadcaster channels + Arab org channels.
# Grow this list over time exactly like your RSS source list.
# ---------------------------------------------------------------------------
TWITCH_CHANNELS = [
    # CS2
    "esl_csgo", "blastpremier", "pgl", "faceit", "gamersclub",
    "eslcs", "b8_esports",
    # Dota 2
    "esl_dota2", "beyondthesummit", "epicenter_en1", "pgl_dota2",
    "dota2ti", "blastpremierdota",
    # Valorant / Riot
    "valorant", "riotgames", "lolesports", "vct", "valorant_arabic",
    # Rocket League
    "rocketleague", "rlcs",
    # Rainbow Six
    "rainbow6", "ubisoft",
    # Call of Duty
    "callofduty", "cdl",
    # Mobile titles
    "pubgmobileesports", "freefireesports", "mobilelegends",
    "honorofkingsofficial",
    # Fighting / others
    "capcomfighters", "ea_fc", "overwatchleague",
    # Aggregators / broadcasters
    "dreamhack", "ogaming", "esl", "gamersclubtv",
    # Esports World Cup
    "esportsworldcup", "esports_world_cup",
    # Arab / MENA orgs & scene
    "teamfalcons", "twistedmindsgg", "geekayesports",
    "nigmagalaxy", "anubisgaming", "power_league_gaming",
]

# ---------------------------------------------------------------------------
# YouTube channels to watch for live esports streams.
# You can use @handles (resolved automatically) or raw channel IDs (UC...).
# Handles are easier to add; IDs are faster (skip a resolve call).
# ---------------------------------------------------------------------------
YOUTUBE_CHANNELS = [
    "@ESportsWorldCup",
    "@Valorant",
    "@LoLEsports",
    "@BLASTPremier",
    "@PGLOfficial",
    "@RocketLeague",
    "@Rainbow6Esports",
    "@CallofDuty",
    "@PUBGMOBILEEsports",
    "@MobileLegendsBangBang",
    "@HonorofKingsGlobal",
    "@FreeFireEsports",
    "@TeamFalcons",
    "@TwistedMindsgg",
    "@GeekayEsports",
]

# ---------------------------------------------------------------------------
# Kick channels (login slugs) to watch for live esports streams.
# ---------------------------------------------------------------------------
KICK_CHANNELS = [
    "esl-csgo", "blast", "valorant", "rocketleague",
    "team-falcons", "twisted-minds",
]

# ---------------------------------------------------------------------------
# Liquipedia game wikis to pull matches from (the universal spine).
# Add any wiki name here and that entire game is covered — nothing else needed.
# Full list of wiki names: https://liquipedia.net (subdomain path per game).
# ---------------------------------------------------------------------------
LIQUIPEDIA_WIKIS = [
    "counterstrike",   # CS2
    "dota2",
    "valorant",
    "leagueoflegends",
    "rocketleague",
    "rainbowsix",
    "overwatch",
    "mobilelegends",
    "honorofkings",
    "pubgmobile",
    "freefire",
    "callofduty",
    "apexlegends",
    "fortnite",
    "starcraft2",
    "clashroyale",
    "brawlstars",
]

# ---------------------------------------------------------------------------
# Game normalization: map many source-specific names to one clean label.
# ---------------------------------------------------------------------------
GAME_ALIASES = {
    "counter-strike": "CS2",
    "counter-strike 2": "CS2",
    "cs:go": "CS2",
    "cs2": "CS2",
    "valorant": "Valorant",
    "dota 2": "Dota 2",
    "dota2": "Dota 2",
    "league of legends": "LoL",
    "lol": "LoL",
    "rocket league": "Rocket League",
    "rainbow six siege": "R6",
    "tom clancy's rainbow six siege": "R6",
    "overwatch 2": "Overwatch",
    "pubg mobile": "PUBG Mobile",
    "mobile legends: bang bang": "Mobile Legends",
    "honor of kings": "Honor of Kings",
    "free fire": "Free Fire",
    "apex legends": "Apex Legends",
    "fortnite": "Fortnite",
}


def normalize_game(name: str) -> str:
    if not name:
        return "Other"
    return GAME_ALIASES.get(name.strip().lower(), name.strip())


# ---------------------------------------------------------------------------
# Collection tiers. The GitHub Actions workflow calls run.py with --tier.
#   live  : cheap sources only, high frequency (every ~2-3 min).
#   full  : everything, moderate frequency (every ~15 min).
# ---------------------------------------------------------------------------
TIERS = {
    # cheap, fast API sources for high-frequency polling (streams + live scores)
    "live": ["twitch", "kick", "opendota", "vlr", "lolesports"],
    # everything, including scrapers and the Liquipedia spine, run less often
    "full": [
        "twitch", "youtube", "kick",          # streams
        "opendota", "vlr", "lolesports",       # per-game APIs
        "octane", "aligulac",                  # per-game APIs
        "hltv",                                # CS2 scrape (best-effort)
        "liquipedia",                          # universal spine (best-effort)
        "startgg",                             # tournaments
    ],
}

# start.gg: which titles to pull tournaments for (videogame IDs on start.gg).
# 1386 = CS2 area varies; leave broad and filter by name. Empty => featured.
STARTGG_PER_PAGE = 40
