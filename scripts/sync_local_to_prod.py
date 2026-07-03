#!/usr/bin/env python3
"""
One-off sync: push difficulty / duration_sec / is_favorite from the local
SQLite database to the production Postgres database, matched by
youtube_video_id.

The production DB was seeded fresh from seed_youtube_playlist.py and is missing
the difficulty reclassification and duration fixes that were applied locally.
Both apps now share the production DB, so this only needs to run once.

Usage:
    DATABASE_URL="postgresql://..." python3 scripts/sync_local_to_prod.py
"""
import os
import sqlite3
import sys

import psycopg2

LOCAL_DB = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "piano_app.db")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    sys.exit("ERROR: set DATABASE_URL to the production Postgres connection string.")

# ── Read local values ───────────────────────────────────────────────────────
local = sqlite3.connect(LOCAL_DB)
local.row_factory = sqlite3.Row
rows = local.execute(
    "SELECT youtube_video_id, title, difficulty, duration_sec, is_favorite "
    "FROM songs WHERE youtube_video_id IS NOT NULL AND youtube_video_id != ''"
).fetchall()
local.close()

print(f"Read {len(rows)} songs from local SQLite ({LOCAL_DB}).")

# ── Connect to production Postgres ──────────────────────────────────────────
pg = psycopg2.connect(DATABASE_URL)
pg.autocommit = False
cur = pg.cursor()

updated = 0
unmatched = []

for r in rows:
    vid = r["youtube_video_id"]
    cur.execute(
        """
        UPDATE songs
        SET difficulty = %s,
            duration_sec = %s,
            is_favorite = %s
        WHERE youtube_video_id = %s
        """,
        (
            str(r["difficulty"]),
            int(r["duration_sec"]),
            bool(r["is_favorite"]),
            vid,
        ),
    )
    if cur.rowcount == 1:
        updated += 1
    elif cur.rowcount == 0:
        unmatched.append((vid, r["title"]))
    else:
        # More than one prod row shares this video id — surface it, don't hide it.
        print(f"  WARNING: {cur.rowcount} prod rows matched video id {vid} ({r['title']})")
        updated += cur.rowcount

pg.commit()

# ── Report ──────────────────────────────────────────────────────────────────
print(f"\n✓ Updated {updated} production rows.")
if unmatched:
    print(f"\n{len(unmatched)} local songs had NO matching production row (not synced):")
    for vid, title in unmatched:
        print(f"  {vid} | {title}")

cur.close()
pg.close()
