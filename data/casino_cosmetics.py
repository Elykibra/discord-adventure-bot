# data/casino_cosmetics.py
#
# The cosmetics shop catalog — one dict per category plus a registry
# tying them together, same "one dict, iterate everywhere" pattern as
# CASINO_GAMES/CASINO_BADGES, one level up: COSMETIC_CATEGORIES lets
# cogs/casino.py's shop views stay generic (one class, not one per
# category), so adding a 7th category later is a new catalog dict plus
# one registry entry and its own render hook — no new UI code.
#
# cosmetic_key (each item's dict key) must be globally unique across
# every category combined — it's what casino_cosmetics.cosmetic_key
# stores, and categories share one ownership table.
#
# Prices are rough placeholders, deliberately high — this is a gambling
# game, cosmetics are where accumulated chips go. Easy to retune later,
# they're just data.

CARD_BACKS = {
    "cardback_hanafuda": {
        "name": "Hanafuda", "emoji": "🎴", "price": 30_000,
        "description": "The colorful illustrated flower-card back — Blackjack's original look, before 🂠 became the default.",
    },
}

TITLES = {
    "title_high_roller": {
        "name": "🏆 High Roller", "price": 50_000,
        "description": "Shown under your name on your Casino Profile.",
    },
    "title_lucky_star": {
        "name": "🌟 Lucky Star", "price": 50_000,
        "description": "Shown under your name on your Casino Profile.",
    },
}

# Each theme remaps the same 5 canonical symbols from data/slots.py's
# SYMBOL_WEIGHTS/TRIPLE_PAYOUT to themed glyphs. SYMBOL_WEIGHTS and
# TRIPLE_PAYOUT never change — a theme is purely what gets drawn on
# screen for each of the same 5 weighted/paid tiers.
SLOT_THEMES = {
    "slot_theme_lucky": {
        "name": "Lucky", "price": 75_000,
        "description": "A four-leaf-clover reskin of the reels — same odds, same payouts, different symbols.",
        "symbols": {"🍒": "🍀", "🍋": "🍄", "🔔": "⭐", "7️⃣": "🎃", "💎": "👑"},
    },
}

WEAPON_SKINS = {
    "weaponskin_pistol_gold": {
        "name": "Golden Pistol", "emoji": "✨", "weapon_key": "pistol", "price": 100_000,
        "description": "A cosmetic reskin of the Pistol — same stats, flashier look.",
    },
}

TABLE_FLAIR = {
    "flair_crown": {
        "name": "Crown", "emoji": "👑", "price": 40_000,
        "description": "Shown next to your name at Baccarat and Poker tables — everyone seated sees it.",
    },
}

TAUNTS = {
    "taunt_mic_drop": {
        "name": "Mic Drop", "text": "🎤 ...and that's how it's done.", "price": 25_000,
        "description": "Appended to your result screen in Blackjack, Slots, Video Poker, and the Dungeon.",
    },
}

COSMETIC_CATEGORIES = {
    "card_back": {
        # NOT 🂠 — that's the real "playing card back" glyph used as plain
        # embed TEXT elsewhere (Blackjack's hidden card, proven safe there),
        # but it's not an Emoji-Data-qualified codepoint, so Discord's
        # component API rejects it in a SelectOption's `emoji=` field with
        # "Invalid emoji" (confirmed live). 🃏 is a certified emoji from the
        # same Playing Cards Unicode block and already proven safe as a
        # component emoji (CasinoSelect's Blackjack option).
        "label": "Card Backs", "emoji": "🃏", "items": CARD_BACKS, "wallet_column": "equipped_card_back",
    },
    "title": {
        "label": "Titles", "emoji": "📛", "items": TITLES, "wallet_column": "equipped_title",
    },
    "slot_theme": {
        "label": "Slot Themes", "emoji": "🎰", "items": SLOT_THEMES, "wallet_column": "equipped_slot_theme",
    },
    "weapon_skin": {
        "label": "Weapon Skins", "emoji": "🔫", "items": WEAPON_SKINS, "wallet_column": "equipped_weapon_skin",
    },
    "table_flair": {
        "label": "Table Flair", "emoji": "🪑", "items": TABLE_FLAIR, "wallet_column": "equipped_table_flair",
    },
    "taunt": {
        "label": "Taunt Lines", "emoji": "💬", "items": TAUNTS, "wallet_column": "equipped_taunt",
    },
}

# Every valid wallet_column, for validating set_equipped_cosmetic's
# dynamic column name before it's interpolated into SQL (asyncpg can't
# parameterize a column name) — these are our own fixed literals here,
# never user input, but validated anyway before touching a query string.
VALID_WALLET_COLUMNS = frozenset(cat["wallet_column"] for cat in COSMETIC_CATEGORIES.values())


def find_category_for_cosmetic(cosmetic_key: str) -> str | None:
    """Which category a cosmetic_key belongs to, or None if it's not in
    the catalog at all."""
    for category_key, category in COSMETIC_CATEGORIES.items():
        if cosmetic_key in category["items"]:
            return category_key
    return None
