# scripts/patch_min_schema.py
import os, asyncio, asyncpg

DB_URL = os.getenv("DATABASE_URL")  # read from env

SQL = """
ALTER TABLE players
  ADD COLUMN IF NOT EXISTS section_id text,
  ADD COLUMN IF NOT EXISTS story_step_id text,
  ADD COLUMN IF NOT EXISTS flags jsonb DEFAULT '[]'::jsonb;

CREATE TABLE IF NOT EXISTS story_state (
  user_id bigint PRIMARY KEY,
  section_id text NOT NULL,
  story_step_id text NOT NULL,
  updated_at timestamptz DEFAULT now()
);
"""

async def main():
    if not DB_URL:
        raise SystemExit("Set DATABASE_URL env var first.")
    conn = await asyncpg.connect(DB_URL)
    try:
        await conn.execute(SQL)
        print("Schema patch applied.")
    finally:
        await conn.close()

asyncio.run(main())
