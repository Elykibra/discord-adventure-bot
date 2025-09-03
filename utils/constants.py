# utils/constants.py
# This file contains all shared constants and data dictionaries.

from typing import Dict
import discord

VERSION = "v0.4.0" # Updated version for new inventory system

# A dictionary to hold pet image URLs.
PET_IMAGE_URLS = {
    "Pyrelisk": "https://cdn.discordapp.com/attachments/1409390172918910976/1409393442932654080/test.png?ex=68ad376e&is=68abe5ee&hm=12b2f6109e76ef47c5dae55c42475bf8ccf8ab4385f03ccc98a7e12dc9469702&",
    "Dewdrop": "https://cdn.discordapp.com/attachments/1409396022022770759/1409396721762701373/Dewdrop_v3.png?ex=68ad3a7b&is=68abe8fb&hm=97f9eacb1730829cc27d4169f71b953223b4d2ba24beacf09e4cb09736426588&",
    "Terran": "https://cdn.discordapp.com/attachments/1409396022022770759/1409398196920385546/Terran.png?ex=68ad3bdb&is=68abea5b&hm=ef1a5caf4151319aac747b76e99e86d397cb1923b076c9ecd81ad41e5aca9538&",
    "Mossling": "https://placehold.co/100x100/32CD32/ffffff?text=Mossling",
    "Sunpetal Moth": "https://placehold.co/100x100/DAA520/ffffff?text=Moth",
    "Gloom Weaver": "https://placehold.co/100x100/4B0082/ffffff?text=Weaver",
    "Moonpetal Sprite": "https://placehold.co/100x100/9370DB/ffffff?text=Sprite",
    "Rock Golem": "https://placehold.co/100x100/6c757d/ffffff?text=Golem",
    "Wind Whisperer": "https://placehold.co/100x100/17a2b8/ffffff?text=Wind",
    "Spark Snail": "https://placehold.co/100x100/ffc107/ffffff?text=Snail",
    "Phoenix": "https://placehold.co/100x100/dc3545/ffffff?text=Phoenix",
    "Shadow Serpent": "https://placehold.co/100x200/343a40/ffffff?text=Serpent",
    "Hydro Hydra": "https://placehold.co/100x100/007bff/ffffff?text=Hydra",
    "Funglow": "https://placehold.co/100x100/A0A0A0/000000?text=Funglow",
    "Rockpup": "https://placehold.co/100x100/808080/FFFFFF?text=Rockpup",
    "Sproutling": "https://placehold.co/100x100/228B22/FFFFFF?text=Sproutling",
    "Tide Wisp": "https://placehold.co/100x100/4682B4/FFFFFF?text=Tide+Wisp",
    "Ignis": "https://placehold.co/100x100/D22B2B/FFFFFF?text=Ignis",
    "Chronomus": "https://placehold.co/100x100/9400D3/FFFFFF?text=Chronomus",
    "Nexus": "https://placehold.co/100x100/FFD700/000000?text=Nexus",
    "Corroder": "https://placehold.co/100x100/696969/ffffff?text=Corroder",
}

#Pet types
PET_TYPES = [
    "Normal", "Fire", "Water", "Grass", "Electric", "Ice", "Fighting",
    "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost",
    "Dragon", "Fairy"
]
DEFENSIVE_TYPE_CHART = {
    "Normal":   {"weak_to": ["Fighting"], "resists": [], "immune_to": ["Ghost"]},
    "Fire":     {"weak_to": ["Water", "Rock", "Ground"], "resists": ["Fire", "Grass", "Ice", "Bug", "Fairy"], "immune_to": []},
    "Water":    {"weak_to": ["Grass", "Electric"], "resists": ["Fire", "Water", "Ice"], "immune_to": []},
    "Grass":    {"weak_to": ["Fire", "Ice", "Poison", "Flying", "Bug"], "resists": ["Water", "Grass", "Electric", "Ground"], "immune_to": []},
    "Electric": {"weak_to": ["Ground"], "resists": ["Electric", "Flying"], "immune_to": []},
    "Ice":      {"weak_to": ["Fire", "Fighting", "Rock"], "resists": ["Ice"], "immune_to": []},
    "Fighting": {"weak_to": ["Flying", "Psychic", "Fairy"], "resists": ["Bug", "Rock"], "immune_to": []},
    "Poison":   {"weak_to": ["Ground", "Psychic"], "resists": ["Grass", "Fighting", "Poison", "Bug", "Fairy"], "immune_to": []},
    "Ground":   {"weak_to": ["Water", "Grass", "Ice"], "resists": ["Poison", "Rock"], "immune_to": ["Electric"]},
    "Flying":   {"weak_to": ["Electric", "Ice", "Rock"], "resists": ["Grass", "Fighting", "Bug"], "immune_to": ["Ground"]},
    "Psychic":  {"weak_to": ["Bug", "Ghost"], "resists": ["Fighting", "Psychic"], "immune_to": []},
    "Bug":      {"weak_to": ["Fire", "Flying", "Rock"], "resists": ["Grass", "Fighting", "Ground"], "immune_to": []},
    "Rock":     {"weak_to": ["Water", "Grass", "Fighting", "Ground"], "resists": ["Normal", "Fire", "Poison", "Flying"], "immune_to": []},
    "Ghost":    {"weak_to": ["Ghost"], "resists": ["Poison", "Bug"], "immune_to": ["Normal", "Fighting"]},
    "Dragon":   {"weak_to": ["Ice", "Dragon", "Fairy"], "resists": ["Fire", "Water", "Grass", "Electric"], "immune_to": []},
    "Fairy":    {"weak_to": ["Poison"], "resists": ["Fighting", "Bug"], "immune_to": ["Dragon"]},
}

TYPE_EMOJIS = {
    "Bug": "🪲",
    "Dragon": "🐉",
    "Electric": "⚡",
    "Fairy": "🌸",
    "Fighting": "💪",
    "Fire": "🔥",
    "Flying": "🪶",
    "Ghost": "👻",
    "Grass": "🌿",
    "Ground": "⛰️",
    "Ice": "❄️",
    "Normal": "⭐",
    "Poison": "🧪",
    "Psychic": "🔮",
    "Rock": "🪨",
    "Steel": "⚙️",
    "Water": "🌊"
}

# Define descriptions for starter pets and new catchable pets
PET_DESCRIPTIONS = {
    "Pyrelisk": "A small, lizard-like creature with a body made of fiery rock. It's an aggressive attacker, specializing in powerful, single-target fire damage.",
    "Dewdrop": "A small, gelatinous creature made of pure water. It is a strategic pet that focuses on self-preservation and weakening the opponent.",
    "Terran": "A small, turtle-like pet with a shell made of hardened earth. It is a durable tank with very high health and armor, designed to outlast its opponent.",
    "Mossling": "A small, unassuming creature made of moss and twigs. It blends perfectly with the forest floor.",
    "Sunpetal Moth": "Its wings shimmer with iridescent dust, reflecting the sunlight. Sunpetal Moths flit gracefully through the sun-dappled canopy.",
    "Gloom Weaver": "A reclusive spider that spins almost invisible webs between the shadowed branches.",
    "Moonpetal Sprite": "An elusive, ethereal being formed from pure moonlight and forest magic. It dances among the Moonpetals.",
    "Corroder": "A foul creature born from the tainted sludge of the Rotting Pits, its rocky hide drips with a weak poison.",
}

# Define pet evolutions (to be used later)
PET_EVOLUTIONS = {
    "Mossling": {
        "level": 20,
        "species": "Verdant Golem"
    }
}

XP_REWARD_BY_RARITY = {
    "Common": 20,
    "Uncommon": 30,
    "Rare": 45,
    "Legendary": 100,
}

## --- REFACTORING CHANGES ---
# Centralized item categories. "Gear" is used instead of "Equipment" for consistency.
ITEM_CATEGORIES = {
    "Consumables": "Items that are used up and have a direct effect on the player or their pets.",
    "Crafting Materials": "Items used in crafting, for quests, or for trading.",
    "Gear": "Gear that a player or their pets can equip to gain stat bonuses.",
    "Key Items": "Unique, un-consumable items that are critical for progress or provide reusable abilities."
}

# --- Crest Definitions and Emojis ---
CREST_DATA = {
    "The Ember Crest": "🔥",
    "The Glacial Crest": "❄️",
    "The Tide Crest": "🌊",
    "The Verdant Crest": "🌿",
    "The Venom Crest": "🐍",
    "The Obsidian Crest": "🪨",
    "The Stratos Crest": "💨",
    "The Ethereal Crest": "🔮",
    "The Current Crest": "⚡",
    "The Wyrm Crest": "🐉",
}
UNEARNED_CREST_EMOJI = "⚫"

# Updated CREST_DESCRIPTIONS to match the game document lore.
CREST_DESCRIPTIONS = {
    "The Ember Crest": "Earned in Sunstone Oasis, it symbolizes an Adventurer's ability to master powerful Fire-type companions and endure the scorching heat of the desert.",
    "The Glacial Crest": "From Frostfall Peak, this crest is a mark of resilience. It proves you have overcome the harsh cold of the mountains and triumphed against Ice-type companions.",
    "The Tide Crest": "A reward from Aethelgard's Rest, it signifies a mastery of strategy against the tactical challenges of Water-type companions in the bustling port city.",
    "The Verdant Crest": "From Whisperwood Grove, this crest is a symbol of an Adventurer's respect for nature, demonstrating their triumph over the elusive Bug and Grass-type pets.",
    "The Venom Crest": "This crest from Blackwater Marsh proves an Adventurer can be both clever and quick. It is a reward for outsmarting the deceptive poisons and clever traps of the swamp.",
    "The Obsidian Crest": "Forged in Ironforge, it is a testament to raw power and durability, a symbol of defeating the defensive, high-HP Rock-type companions of the volcano's shadow.",
    "The Stratos Crest": "Earned in Skylight Spire, it signifies agility and speed. It proves an Adventurer has conquered the quick and difficult-to-hit Flying-type companions of the sky.",
    "The Ethereal Crest": "The reward for conquering Silvermoon Glade, this crest represents a keen mind and an ability to navigate the unusual abilities of Ghost and Psychic-type companions.",
    "The Current Crest": "This unique crest from The Sunken City is a symbol of strategic genius, earned by defeating a powerful combination of Water and Electric-type companions.",
    "The Wyrm Crest": "Forged from the scale of an ancient dragon, this crest radiates a primal power that shakes the soul. It is the final key to becoming a Legend, earned by defeating the ultimate Dragon-type challenges of Dragon's Tooth.",
}

# --- Crest-Based Rank System ---
RANK_DISPLAY_DATA = {
    "Novice": {
        "color": discord.Color.dark_grey(),
        "title_prefix": "🗡️ Novice Adventurer",
        "description": "Just beginning their journey in the world of Aethelgard. The path ahead is long and full of challenges!",
        "stat_emoji_coins": "💰",
        "stat_emoji_reputation": "✨"
    },
    "Journeyman": {
        "color": discord.Color.gold(),
        "title_prefix": "🛡️ Journeyman Explorer",
        "description": "Has proven their mettle and is now a respected explorer of the land. Their legend is just beginning to be told.",
        "stat_emoji_coins": "🪙",
        "stat_emoji_reputation": "🌟"
    },
    "Wanderer": {
        "color": discord.Color.darker_grey(),
        "title_prefix": "🗺️ Wanderer of the Wilds",
        "description": "A seasoned traveler, unafraid to venture into the unknown. Their name is whispered in taverns across the realm.",
        "stat_emoji_coins": "🔲",
        "stat_emoji_reputation": "💫"
    },
    "Veteran": {
        "color": discord.Color.dark_red(),
        "title_prefix": "⚔️ Veteran Champion",
        "description": "A seasoned hero, their armor dented and their spirit unyielding. They have faced great foes and emerged victorious.",
        "stat_emoji_coins": "🏆",
        "stat_emoji_reputation": "🔥"
    },
    "Master": {
        "color": discord.Color.orange(),
        "title_prefix": "✨ Master of the Realm",
        "description": "A true master of their craft, commanding respect from all corners of the world. They are a force to be reckoned with.",
        "stat_emoji_coins": "👑",
        "stat_emoji_reputation": "🌟🌟"
    },
    "Champion": {
        "color": discord.Color.purple(),
        "title_prefix": "👑 Champion of Aethelgard",
        "description": "The peak of power and prestige. Their deeds are legendary, their name a beacon of hope.",
        "stat_emoji_coins": "💎",
        "stat_emoji_reputation": "✨✨✨"
    },
    "Legend": {
        "color": discord.Color.from_rgb(255, 215, 0),
        "title_prefix": "🌌 LEGEND",
        "description": "A myth made real. A true master of the world, having earned every Crest. Their legacy is etched in the annals of Aethelgard!",
        "stat_emoji_coins": "🌠",
        "stat_emoji_reputation": "🌌"
    }
}

CREST_RANKS = [
    {"rank": "Novice", "crest_count": 0, "next_crest_count": 1,
     "description": "Your journey is just beginning! Collect your first crest to rank up."},
    {"rank": "Journeyman", "crest_count": 1, "next_crest_count": 3,
     "description": "You've earned your first crest! You are now a seasoned traveler. New challenges await!"},
    {"rank": "Wanderer", "crest_count": 3, "next_crest_count": 5,
     "description": "You're a true wanderer, exploring the furthest reaches of the world. Keep going to uncover more secrets."},
    {"rank": "Veteran", "crest_count": 5, "next_crest_count": 7,
     "description": "You're a veteran adventurer, your name is known across the lands. The most dangerous quests are now within your grasp."},
    {"rank": "Master", "crest_count": 7, "next_crest_count": 9,
     "description": "A true master of the adventure world! Legends speak of your deeds. There is no challenge you can't overcome."},
    {"rank": "Champion", "crest_count": 9, "next_crest_count": 10,
     "description": "You are a champion! Only one more crest stands between you and true legend."},
    {"rank": "Legend", "crest_count": 10, "next_crest_count": None,
     "description": "A true Legend! You have conquered all the lands and earned every crest. Their legacy is etched in the annals of Aethelgard!"}
]