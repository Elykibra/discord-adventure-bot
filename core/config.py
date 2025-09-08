import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read token safely
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = os.getenv("GUILD_IDS")

# --- NEW: Database Configuration ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not DISCORD_TOKEN:
    raise ValueError("⚠️ DISCORD_TOKEN is missing! Check your .env file.")

if GUILD_IDS:
    GUILD_IDS = [int(g.strip()) for g in GUILD_IDS.split(",")]
else:
    GUILD_IDS = []