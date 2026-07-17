"""
Store layer: keeps a small SQLite db for state (mainly: which alerts we
already fired, so Discord doesn't repeat) and writes the JSON snapshot
that the dashboard reads.
"""
import os
import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "state.db")
# The dashboard reads this file. It is written into the Next.js public folder
# so Vercel can serve it directly at /data.json.
SNAPSHOT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "dashboard", "public", "data.json"
)


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS alerted (
            key TEXT PRIMARY KEY,
            created_at TEXT
        )
    """)
    return con


def was_alerted(key: str) -> bool:
    con = _conn()
    try:
        cur = con.execute("SELECT 1 FROM alerted WHERE key = ?", (key,))
        return cur.fetchone() is not None
    finally:
        con.close()


def mark_alerted(key: str):
    con = _conn()
    try:
        con.execute(
            "INSERT OR IGNORE INTO alerted (key, created_at) VALUES (?, ?)",
            (key, datetime.now(tz=timezone.utc).isoformat()),
        )
        con.commit()
    finally:
        con.close()


def prune_alerted(days: int = 3):
    """Drop alert records older than N days to keep the table small."""
    con = _conn()
    try:
        con.execute(
            "DELETE FROM alerted WHERE created_at < datetime('now', ?)",
            (f"-{days} days",),
        )
        con.commit()
    finally:
        con.close()


def write_snapshot(snapshot):
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"[store] snapshot written -> {os.path.relpath(SNAPSHOT_PATH)}")
