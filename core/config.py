import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read token safely
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = os.getenv("GUILD_IDS")

if not DISCORD_TOKEN:
    raise ValueError("⚠️ DISCORD_TOKEN is missing! Check your .env file.")

if GUILD_IDS:
    GUILD_IDS = [int(g.strip()) for g in GUILD_IDS.split(",")]
else:
    GUILD_IDS = []