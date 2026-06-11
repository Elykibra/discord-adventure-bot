# data/classifications.py
# Aethelgard — Creature Classification & Gloom State frameworks.
#
# Source design docs:
#   - docs/design/aethelgard_classification.md  (Classification Tier / Encounter Rarity)
#   - docs/design/whisperwood_grove.md          (Gloom Sickness — State / Type / Mark)
#
# STATUS: Narrative scaffolding. These are the world's *current* in-world
# understanding — they read as "hearsay," not absolute scientific fact, and
# names/descriptions/order can still be adjusted as the story develops.
# Putting them here (instead of leaving them only in design docs) just gives
# the rest of the codebase one place to reference them consistently, and one
# place to update if they change.
#
# Nothing in this file is wired into game logic yet. It's reference data —
# for flavor text, future tooltips/encyclopedia entries, lore commands, etc.

# =================================================================================
#  CLASSIFICATION TIER
# =================================================================================
# What a creature fundamentally *is* — its place in the world's power/
# significance hierarchy. A species' tier is mostly fixed.

CLASSIFICATION_TIERS = [
    "Ordinary",
    "Prime",
    "Apex",
    "Elder",
    "Ancient",
    "Primordial",
    "Eternal",
]

CLASSIFICATION_TIER_INFO = {
    "Ordinary": {
        "description": "Everyday wildlife. The baseline of the world.",
        "example": "Mossling, Sunmoth, most starter-line species",
    },
    "Prime": {
        "description": "A step above ordinary — more capable, still common enough to encounter regularly.",
        "example": "Mid-evolution-line species",
    },
    "Apex": {
        "description": "The \"top of the food chain\" for a given habitat — strong, but still part of the normal ecosystem.",
        "example": "Late-evolution-line species, strong standalones",
    },
    "Elder": {
        "description": (
            "A creature that embodies a quality of its territory — not just strong, but a "
            "living expression of something about the place. Neutral term: an Elder can "
            "embody growth, decay, memory, etc. — good or ill is not implied by the tier itself."
        ),
        "example": "Verdanthorn / Hollowthorn (Whisperwood), Pyrehart / Cindermaw (Ashen Verge)",
    },
    "Ancient": {
        "description": (
            "A being a territory is built around — foundational to that region's identity, "
            "history, and balance. Effectively one-per-major-territory."
        ),
        "example": "Sylven Heartwood (Whisperwood)",
    },
    "Primordial": {
        "description": (
            "Reserved / unused so far. A being whose significance extends beyond a single "
            "territory — possibly tied to Aethelgard-wide forces. No confirmed example yet."
        ),
        "example": None,
    },
    "Eternal": {
        "description": (
            "Reserved / unused so far. The theoretical ceiling — something that predates or "
            "transcends current territorial structures entirely. No confirmed example yet."
        ),
        "example": None,
    },
}

# Tiers with at least one confirmed/used example. Primordial and Eternal are
# intentionally excluded — "don't force an example into existence just to fill the table."
ACTIVE_CLASSIFICATION_TIERS = ["Ordinary", "Prime", "Apex", "Elder", "Ancient"]


# =================================================================================
#  ENCOUNTER RARITY
# =================================================================================
# How often a creature is actually seen/caught — independent of Classification
# Tier. A creature's tier rarely changes; its encounter rarity can shift by
# context (e.g. a Withering-Marked Mossling is still Ordinary tier, but a Rare sighting).

ENCOUNTER_RARITIES = [
    "Common",
    "Uncommon",
    "Rare",
    # Further tiers TBD as needed.
]


# =================================================================================
#  GLOOM STATE — The Seven Gloom States
# =================================================================================
# What relationship a being has with the Gloom (separate axis from
# Classification Tier — same number of rungs so the two can be discussed in
# the same breath, e.g. "Gloom State reads as Elder-equivalent").

GLOOM_STATES = [
    "Touched",
    "Shorn",
    "Hollow",
    "Wrought",
    "Forsaken",
    "Unbound",
    "Oblivion",
]

GLOOM_STATE_INFO = {
    "Touched": {
        "title": "The Invitation",
        "description": (
            "The Gloom has entered the being. Something has changed, but the self is still "
            "largely intact. Some believe the Touched can be healed. Some believe they have "
            "been chosen."
        ),
        "example_phrase": "The beast is Touched.",
    },
    "Shorn": {
        "title": "The Erosion",
        "description": (
            "Something essential has been cut away — memories, instincts, identity, "
            "emotions, or connections begin to fray. The being still exists, but it is no "
            "longer whole."
        ),
        "example_phrase": "The Shorn forget familiar paths.",
    },
    "Hollow": {
        "title": "The Shell",
        "description": (
            "The original self has been emptied. What once was remains only as a vessel. "
            "Whether anything still lingers inside is a matter of belief."
        ),
        "example_phrase": "The Hollow still walk.",
    },
    "Wrought": {
        "title": "The Remaking",
        "description": (
            "The empty shell is reshaped. The Gloom no longer merely consumes — it creates. "
            "A Wrought being often embodies the wound of its territory."
        ),
        "example_phrase": "The Wrought become the wound.",
    },
    "Forsaken": {
        "title": "The Separation",
        "description": (
            "The being no longer belongs to the ordinary order of the world. Some pity "
            "them. Some fear them. Some envy them."
        ),
        "example_phrase": "The Forsaken have no place left.",
    },
    "Unbound": {
        "title": "The Release",
        "description": (
            "The Gloom is no longer fully restrained by host, body, or place. Identity "
            "dissolves into something larger. Some see this as the ultimate tragedy. Others "
            "see it as freedom."
        ),
        "example_phrase": "The Unbound answer to nothing.",
    },
    "Oblivion": {
        "title": "The Absolute",
        "description": (
            "The final horizon. The distinction between being, place, memory, and force "
            "begins to disappear. An Oblivion may no longer be merely a creature — it may "
            "become a phenomenon, a scar, or a forgotten law of the world itself."
        ),
        "example_phrase": "Of the Oblivion, no trustworthy account survives.",
    },
}

# States 1-3 are the active, in-use rungs — the values gloom["state"] holds on
# pets/NPCs today. Wrought (4) is lore-confirmed (Hollowthorn, Cindermaw) but
# not yet used as a pet-data value. Forsaken/Unbound/Oblivion (5-7) are
# reserved/lore-only, mirroring Primordial/Eternal above.
ACTIVE_GLOOM_STATES = ["Touched", "Shorn", "Hollow"]

# Parallel framing, NOT a direct equivalence — "Classification asks: what is
# this being? Gloom asks: what relationship does this being have with the Gloom?"
CLASSIFICATION_GLOOM_PARALLEL = dict(zip(CLASSIFICATION_TIERS, GLOOM_STATES))


def gloom_state_index(state: str) -> int:
    """Return the 0-based rung index of a Gloom State (0 = Touched ... 6 = Oblivion).

    Useful for comparisons like "is this State further along than that one?"
    without hardcoding the ordering elsewhere. Raises ValueError for unknown states.
    """
    return GLOOM_STATES.index(state)


def classification_tier_index(tier: str) -> int:
    """Return the 0-based rung index of a Classification Tier (0 = Ordinary ... 6 = Eternal)."""
    return CLASSIFICATION_TIERS.index(tier)
