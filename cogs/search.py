# cogs/search.py
# Encyclopedia / search command for Aethelgard.
# Covers: Pets, Skills, Items, Passives, Personalities

import discord
from discord import app_commands
from discord.ext import commands

from data.pets import PET_DATABASE, PET_LOOKUP
from data.skills import PET_SKILLS
from data.items import ITEMS
from data.abilities import SHARED_PASSIVES_BY_TYPE, STARTER_TALENTS

# ---------------------------------------------------------------------------
# Static data not stored elsewhere
# ---------------------------------------------------------------------------

PERSONALITIES = {
    "Aggressive": {
        "emoji": "⚔️",
        "description": "A relentless fighter that always goes for the kill. Every turn it picks the strongest available attack with no second-guessing.",
        "battle_behavior": "Always uses the highest-power move available. No defensive considerations."
    },
    "Defensive": {
        "emoji": "🛡️",
        "description": "A cautious fighter that knows when to hold back. It will attempt to shore up its defenses when pushed into a corner.",
        "battle_behavior": "When HP drops below 40%, tries to use a defensive move first. Otherwise attacks with the strongest move."
    },
    "Tactical": {
        "emoji": "🧠",
        "description": "A smart fighter that adapts to the flow of battle. It mixes offense with status pressure to keep opponents off-balance.",
        "battle_behavior": "When HP drops below 50%, has a 50% chance to use a Status-type move. Otherwise attacks with the strongest move."
    },
    "Timid": {
        "emoji": "🐇",
        "description": "A skittish fighter that prioritises speed and evasion. It prefers to strike fast and retreat rather than slug it out.",
        "battle_behavior": "Favours faster, lower-power moves and will look for opportunities to flee or stall."
    },
}

TYPE_COLORS = {
    "Fire": 0xFF4500, "Water": 0x1E90FF, "Grass": 0x228B22,
    "Electric": 0xFFD700, "Ground": 0xCD853F, "Rock": 0x808080,
    "Poison": 0x9400D3, "Normal": 0xA8A878, "Fighting": 0xB22222,
    "Bug": 0x6B8E23, "Flying": 0x87CEEB, "Psychic": 0xFF69B4,
    "Ice": 0xADD8E6, "Dragon": 0x8B008B, "Ghost": 0x4B0082, "Fairy": 0xFF1493,
}

TYPE_EMOJIS = {
    "Fire": "🔥", "Water": "🌊", "Grass": "🌿", "Electric": "⚡",
    "Ground": "🪨", "Rock": "🪨", "Poison": "☠️", "Normal": "⬜",
    "Fighting": "🥊", "Bug": "🐛", "Flying": "🌪️", "Psychic": "🔮",
    "Ice": "❄️", "Dragon": "🐉", "Ghost": "👻", "Fairy": "✨",
}

CATEGORY_EMOJIS = {
    "Physical": "💥",
    "Special": "✨",
    "Status": "🔄",
}

CLASSIFICATION_TIER_EMOJIS = {
    "Ordinary": "⚪",
    "Prime": "🟢",
    "Apex": "🔵",
    "Elder": "🟣",
    "Ancient": "🟠",
    "Primordial": "🔴",
    "Eternal": "🟡",
}

# ---------------------------------------------------------------------------
# Index builder — runs once at cog load
# ---------------------------------------------------------------------------

def _build_search_index():
    """Returns a flat list of (label, value, category) for autocomplete."""
    index = []

    # Pets (including evolutions)
    def add_pet(data):
        name = data.get("species", "Unknown")
        index.append((f"{name} — Pet", f"pet:{name}"))
        for evo_data in data.get("evolutions", {}).values():
            add_pet(evo_data)

    for pet_data in PET_DATABASE.values():
        add_pet(pet_data)

    # Skills
    for skill_id, skill_data in PET_SKILLS.items():
        index.append((f"{skill_data['name']} — Skill", f"skill:{skill_id}"))

    # Items
    for item_id, item_data in ITEMS.items():
        index.append((f"{item_data['name']} — Item", f"item:{item_id}"))

    # Passives from SHARED_PASSIVES_BY_TYPE
    seen_passives = set()
    for passives in SHARED_PASSIVES_BY_TYPE.values():
        for p in passives:
            if p["name"] not in seen_passives:
                seen_passives.add(p["name"])
                index.append((f"{p['name']} — Passive", f"passive:{p['name']}"))

    # Passives from starter talents
    for talents in STARTER_TALENTS.values():
        for t in talents:
            mname = t.get("mechanic_name", t["name"])
            if mname not in seen_passives:
                seen_passives.add(mname)
                index.append((f"{mname} — Passive", f"passive:{mname}"))

    # Personalities
    for name in PERSONALITIES:
        index.append((f"{name} — Personality", f"personality:{name}"))

    return index


# Flat index used for autocomplete
_SEARCH_INDEX = _build_search_index()

# Passive lookup by name (built once)
def _build_passive_lookup():
    lookup = {}
    for type_name, passives in SHARED_PASSIVES_BY_TYPE.items():
        for p in passives:
            lookup[p["name"]] = {**p, "_type": type_name}
    for pet_name, talents in STARTER_TALENTS.items():
        for t in talents:
            mname = t.get("mechanic_name", t["name"])
            lookup[mname] = {
                "name": mname,
                "description": t.get("mechanic_desc", t.get("description", "")),
                "_type": None,
                "_talent_pet": pet_name,
                "_playstyle": t.get("playstyle"),
            }
    return lookup


_PASSIVE_LOOKUP = _build_passive_lookup()

# Pet lookup — use the shared flat lookup from data/pets.py, augmented with _parent info
def _build_search_pet_lookup():
    lookup = {}
    def _add(data, parent=None):
        name = data.get("species")
        if name:
            lookup[name] = {**data, "_parent": parent}
        for evo in data.get("evolutions", {}).values():
            _add(evo, parent=name)
    for pet in PET_DATABASE.values():
        _add(pet)
    return lookup

_PET_LOOKUP = _build_search_pet_lookup()

# ---------------------------------------------------------------------------
# Embed builders
# ---------------------------------------------------------------------------

def _pet_embed(species: str) -> discord.Embed:
    data = _PET_LOOKUP.get(species)
    if not data:
        return discord.Embed(title="Not found", description=f"No pet named **{species}** found.", color=discord.Color.red())

    pet_type = data.get("pet_type", "Normal")
    if isinstance(pet_type, list):
        primary_type = pet_type[0]
        type_str = " / ".join(f"{TYPE_EMOJIS.get(t, '')} {t}" for t in pet_type)
    else:
        primary_type = pet_type
        type_str = f"{TYPE_EMOJIS.get(pet_type, '')} {pet_type}"

    color = TYPE_COLORS.get(primary_type, 0x7289DA)
    classification_tier = data.get("classification_tier", "Ordinary")
    tier_emoji = CLASSIFICATION_TIER_EMOJIS.get(classification_tier, "⚪")

    embed = discord.Embed(
        title=f"🐾 {species}",
        description=data.get("description", "*No description available.*"),
        color=color
    )

    embed.add_field(name="Type", value=type_str, inline=True)
    embed.add_field(name="Classification", value=f"{tier_emoji} {classification_tier}", inline=True)

    personality = data.get("personality")
    if personality:
        p_data = PERSONALITIES.get(personality, {})
        embed.add_field(
            name="Personality",
            value=f"{p_data.get('emoji', '🎭')} {personality}",
            inline=True
        )

    # Base stats
    stats = data.get("base_stat_ranges", {})
    if stats:
        stat_lines = []
        stat_labels = {
            "hp": "❤️ HP", "attack": "⚔️ ATK", "defense": "🛡️ DEF",
            "special_attack": "✨ SP.ATK", "special_defense": "🔵 SP.DEF", "speed": "💨 SPD"
        }
        for key, label in stat_labels.items():
            if key in stats:
                lo, hi = stats[key]
                stat_lines.append(f"{label}: `{lo}–{hi}`")
        embed.add_field(name="Base Stats (at Lv.1)", value="\n".join(stat_lines), inline=False)

    # Passive — show name only (use /search <passive name> for full details)
    passive = data.get("passive_ability")
    if passive:
        if isinstance(passive, list):
            passive_names = "\n".join(f"• {p['name']}" for p in passive)
        else:
            passive_names = f"• {passive['name']}"
        embed.add_field(
            name="🛡️ Passive Ability",
            value=passive_names,
            inline=False
        )

    # Skill tree (condensed)
    skill_tree = data.get("skill_tree", {})
    if skill_tree:
        lines = []
        for level, skills in sorted(skill_tree.items(), key=lambda x: int(x[0])):
            if isinstance(skills, dict) and "choice" in skills:
                names = [PET_SKILLS.get(s, {}).get("name", s) for s in skills["choice"]]
                lines.append(f"Lv.**{level}** — Choose: {' / '.join(names)}")
            elif isinstance(skills, list):
                names = [PET_SKILLS.get(s, {}).get("name", s) for s in skills]
                lines.append(f"Lv.**{level}** — {', '.join(names)}")
        embed.add_field(name="📖 Skill Tree", value="\n".join(lines) if lines else "—", inline=False)

    # Evolution chain hint
    if data.get("evolutions"):
        evo_names = list(data["evolutions"].keys())
        embed.add_field(name="🔄 Evolves Into", value=" → ".join(evo_names), inline=False)
    if data.get("_parent"):
        embed.add_field(name="🔄 Evolves From", value=data["_parent"], inline=False)

    capture_rate = data.get("base_capture_rate")
    if capture_rate:
        embed.set_footer(text=f"Base Capture Rate: {capture_rate}%")

    return embed


def _skill_embed(skill_id: str) -> discord.Embed:
    data = PET_SKILLS.get(skill_id)
    if not data:
        return discord.Embed(title="Not found", color=discord.Color.red())

    skill_type = data.get("type", "Normal")
    color = TYPE_COLORS.get(skill_type, 0x7289DA)
    category = data.get("category", "Physical")

    embed = discord.Embed(
        title=f"⚔️ {data['name']}",
        description=data.get("description", "*No description available.*"),
        color=color
    )

    embed.add_field(name="Type", value=f"{TYPE_EMOJIS.get(skill_type, '')} {skill_type}", inline=True)
    embed.add_field(name="Category", value=f"{CATEGORY_EMOJIS.get(category, '')} {category}", inline=True)

    power = data.get("power")
    if power:
        embed.add_field(name="Power", value=str(power), inline=True)

    # Effect summary
    effect = data.get("effect", {})
    if effect:
        effect_type = effect.get("type", "")
        chance = effect.get("chance")
        chance_str = f" ({int(chance * 100)}% chance)" if chance else ""
        target = effect.get("target", "opponent")

        if effect_type == "stat_change":
            stat = effect.get("stat", "stat").replace("_", " ").title()
            mod = effect.get("modifier", 1.0)
            direction = "lowers" if mod < 1.0 else "raises"
            duration = effect.get("duration")
            dur_str = f" for {duration} turns" if duration else ""
            embed.add_field(
                name="Effect",
                value=f"{chance_str.strip() or 'Always'} {direction} the {target}'s **{stat}**{dur_str}.{chance_str if chance else ''}",
                inline=False
            )
        elif effect_type == "status":
            status = effect.get("status_effect", "").replace("_", " ").title()
            duration = effect.get("duration")
            dur_str = f" for {duration} turns" if duration else ""
            embed.add_field(
                name="Effect",
                value=f"Inflicts **{status}** on the {target}{dur_str}.{chance_str}",
                inline=False
            )
        elif effect_type == "heal":
            value = effect.get("value", 0)
            embed.add_field(name="Effect", value=f"Restores **{value} HP** to the user.", inline=False)
        elif effect_type == "recoil":
            value = effect.get("value", 0)
            embed.add_field(name="Effect", value=f"User takes **{int(value * 100)}%** of damage dealt as recoil.", inline=False)

    # Which pets learn this?
    learners = []
    for pet_name, pet_data in _PET_LOOKUP.items():
        tree = pet_data.get("skill_tree", {})
        for level_skills in tree.values():
            skills_list = level_skills.get("choice", level_skills) if isinstance(level_skills, dict) else level_skills
            if skill_id in skills_list:
                learners.append(pet_name)
                break
    if learners:
        embed.add_field(name="Learned By", value=", ".join(learners), inline=False)

    return embed


def _item_embed(item_id: str) -> discord.Embed:
    data = ITEMS.get(item_id)
    if not data:
        return discord.Embed(title="Not found", color=discord.Color.red())

    embed = discord.Embed(
        title=f"🎒 {data['name']}",
        description=data.get("description", "*No description available.*"),
        color=discord.Color.gold()
    )

    embed.add_field(name="Category", value=data.get("category", "—"), inline=True)

    price = data.get("price")
    if price:
        sell_price = max(1, price // 2)
        embed.add_field(name="Buy Price", value=f"{price} 🪙", inline=True)
        embed.add_field(name="Sell Price", value=f"{sell_price} 🪙", inline=True)

    effect = data.get("effect", {})
    if effect:
        effect_type = effect.get("type", "")
        if effect_type == "heal_pet":
            embed.add_field(name="Effect", value=f"Heals your pet for **{effect.get('value', '?')} HP**.", inline=False)
        elif effect_type == "restore_energy":
            embed.add_field(name="Effect", value=f"Restores **{effect.get('value', '?')} Energy** to the player.", inline=False)
        elif effect_type == "capture":
            embed.add_field(name="Effect", value="Used to attempt to capture a wild pet in battle.", inline=False)
        elif effect_type == "teach_skill":
            embed.add_field(name="Effect", value="Teaches a pet a new skill when used.", inline=False)

    actions = data.get("actions", [])
    if actions:
        embed.set_footer(text="Actions: " + "  •  ".join(a.title() for a in actions))

    return embed


def _passive_embed(passive_name: str) -> discord.Embed:
    data = _PASSIVE_LOOKUP.get(passive_name)
    if not data:
        return discord.Embed(title="Not found", color=discord.Color.red())

    type_name = data.get("_type")
    color = TYPE_COLORS.get(type_name, 0x7289DA) if type_name else 0x7289DA

    embed = discord.Embed(
        title=f"🛡️ {passive_name}",
        description=data.get("description", "*No description available.*"),
        color=color
    )

    if type_name:
        embed.add_field(name="Type Affinity", value=f"{TYPE_EMOJIS.get(type_name, '')} {type_name}", inline=True)

    talent_pet = data.get("_talent_pet")
    if talent_pet:
        embed.add_field(name="Talent For", value=talent_pet, inline=True)

    playstyle = data.get("_playstyle")
    if playstyle:
        embed.add_field(name="Playstyle", value=playstyle, inline=True)

    # Which pets have this passive?
    holders = []
    for pet_name, pet_data in _PET_LOOKUP.items():
        pa = pet_data.get("passive_ability", {})
        if pa.get("name") == passive_name:
            holders.append(pet_name)
    if holders:
        embed.add_field(name="Pets with this Passive", value=", ".join(holders), inline=False)

    return embed


def _personality_embed(personality_name: str) -> discord.Embed:
    data = PERSONALITIES.get(personality_name)
    if not data:
        return discord.Embed(title="Not found", color=discord.Color.red())

    embed = discord.Embed(
        title=f"{data.get('emoji', '🎭')} {personality_name} Personality",
        description=data["description"],
        color=0x9B59B6
    )

    embed.add_field(name="⚔️ Battle Behaviour", value=data["battle_behavior"], inline=False)

    # Which pets have this personality?
    holders = [
        name for name, pet_data in _PET_LOOKUP.items()
        if pet_data.get("personality") == personality_name
    ]
    if holders:
        embed.add_field(name="Pets with this Personality", value=", ".join(holders), inline=False)

    return embed


# ---------------------------------------------------------------------------
# Cog
# ---------------------------------------------------------------------------

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="search", description="Look up any pet, skill, item, passive, or personality in Aethelgard.")
    @app_commands.describe(query="Start typing a name to search...")
    async def search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(ephemeral=True)

        # Parse category:value from autocomplete selection
        if ":" not in query:
            # Fallback: try to fuzzy-match by label
            lower = query.lower()
            match = next((v for label, v in _SEARCH_INDEX if lower in label.lower()), None)
            if not match:
                await interaction.followup.send(
                    f"❌ No results for **{query}**. Try using the autocomplete suggestions.",
                    ephemeral=True
                )
                return
            query = match

        category, _, value = query.partition(":")

        if category == "pet":
            embed = _pet_embed(value)
        elif category == "skill":
            embed = _skill_embed(value)
        elif category == "item":
            embed = _item_embed(value)
        elif category == "passive":
            embed = _passive_embed(value)
        elif category == "personality":
            embed = _personality_embed(value)
        else:
            embed = discord.Embed(title="Unknown category", color=discord.Color.red())

        embed.set_author(name="📖 Aethelgard Encyclopedia")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @search.autocomplete("query")
    async def search_autocomplete(self, interaction: discord.Interaction, current: str):
        lower = current.lower()
        matches = [
            app_commands.Choice(name=label, value=value)
            for label, value in _SEARCH_INDEX
            if lower in label.lower()
        ]
        # Discord caps autocomplete at 25
        return matches[:25]


async def setup(bot):
    await bot.add_cog(Search(bot))
