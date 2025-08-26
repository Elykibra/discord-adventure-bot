# data/abilities.py
# This file contains the library of shared passive abilities, organized by pet type.


# =================================================================================
#  STARTER PET INNATE TALENTS (Tier 1)
# =================================================================================
# These are the unique, choice-based passives for the starter pets.

STARTER_TALENTS = {
    "Pyrelisk": [
        {
            "name": "Blazing Fury", "playstyle": "Relentless Attacker",
            "description": "Focus on overwhelming opponents with relentless, ever-increasing fiery power.",
            "mechanic_name": "Singeing Fury",
            "mechanic_desc": "Fire attacks get 5% stronger per use in battle. (Stacks)"
        },
        {
            "name": "Flame Body", "playstyle": "Punishing Defender",
            "description": "Use your intense heat as a shield to punish those who get too close.",
            "mechanic_name": "Flame Body",
            "mechanic_desc": "Has a 30% chance to burn an opponent who makes physical contact."
        },
        {
            "name": "Blaze", "playstyle": "Desperate Gambit",
            "description": "Channel your energy into a single, devastating final gambit when pushed to your limit.",
            "mechanic_name": "Blaze",
            "mechanic_desc": "When HP is below 1/3, the power of this pet's Fire-type moves is greatly increased."
        },
        {
            "name": "Molten Armor", "playstyle": "Resilient Tank",
            "description": "Harden your rocky hide with internal heat, making you tougher to take down.",
            "mechanic_name": "Molten Armor",
            "mechanic_desc": "This pet is immune to taking damage from critical hits."
        },
        {
            "name": "Draconic Spark", "playstyle": "Early Evolution",
            "description": "Awaken your latent draconic power early, granting you a spark of your future strength.",
            "mechanic_name": "Draconic Spark",
            "mechanic_desc": "Attacks have a 10% chance to deal a small amount of bonus Dragon-type damage."
        }
    ],
    "Dewdrop": [
        {
            "name": "Temporal Wellspring", "playstyle": "Masterful Controller",
            "description": "Manipulate the flow of battle, ensuring your debilitating effects linger on your foes.",
            "mechanic_name": "Temporal Wellspring",
            "mechanic_desc": "Non-damaging status effects and debuffs you apply last one extra turn."
        },
        {
            "name": "Soothing Aura", "playstyle": "Supportive Healer",
            "description": "Become a beacon of tranquility, mending your own wounds with a gentle, persistent energy.",
            "mechanic_name": "Soothing Aura",
            "mechanic_desc": "At the end of each turn, this pet restores 5% of its maximum HP."
        },
        {
            "name": "Liquid Form", "playstyle": "Elusive Defender",
            "description": "Your body becomes fluid and unpredictable, allowing you to gracefully avoid physical blows.",
            "mechanic_name": "Liquid Form",
            "mechanic_desc": "This pet has a 15% chance to evade incoming physical attacks."
        },
        {
            "name": "Fae Blessing", "playstyle": "Mystic Guardian",
            "description": "Channel your latent fairy magic to create a protective ward that repels debilitating energies.",
            "mechanic_name": "Fae Blessing",
            "mechanic_desc": "This pet is immune to all stat-lowering effects from opponents."
        },
        {
            "name": "Deep Current", "playstyle": "Relentless Special Attacker",
            "description": "Draw power from the depths, building a current of overwhelming special energy.",
            "mechanic_name": "Deep Current",
            "mechanic_desc": "Using a Water-type attack permanently raises this pet's Special Attack in battle. (Stacks)"
        }
    ],
    "Terran": [
        {
            "name": "Fortress Form", "playstyle": "Pure Tank",
            "description": "Your pet's body hardens instinctively upon impact, shrugging off the force of enemy blows.",
            "mechanic_name": "Fortress Form",
            "mechanic_desc": "When hit by a direct attack, its defenses are temporarily increased for the turn."
        },
        {
            "name": "Terra Firma", "playstyle": "Regenerative Tank",
            "description": "By planting its feet firmly, your pet draws restorative energy directly from the earth itself.",
            "mechanic_name": "Terra Firma",
            "mechanic_desc": "If this pet doesn't move, it restores 10% of its max HP at the end of the turn."
        },
        {
            "name": "Rocky Rebuke", "playstyle": "Retaliatory Tank",
            "description": "Your pet's hide is covered in sharp, rocky protrusions that punish any foe foolish enough to get too close.",
            "mechanic_name": "Rocky Rebuke",
            "mechanic_desc": "Attackers making physical contact take a small amount of Rock-type damage."
        },
        {
            "name": "Tectonic Force", "playstyle": "Disruptive Tank",
            "description": "Every step your pet takes shakes the ground, making it difficult for opponents to keep their footing.",
            "mechanic_name": "Tectonic Force",
            "mechanic_desc": "This pet's Ground and Rock-type moves have a 20% chance to lower the target's Speed."
        },
        {
            "name": "Solid Rock", "playstyle": "Unyielding Survivor",
            "description": "Your pet possesses an unbreakable will and a body as solid as a mountain.",
            "mechanic_name": "Solid Rock",
            "mechanic_desc": "If at full health, this pet will survive any single hit with 1 HP remaining."
        }
    ]
}

# =================================================================================
#  SHARED PASSIVE ABILITIES
# =================================================================================
# A library of common, type-based passives for Tier 2 pets.
# Each type has 3 options that can be randomly assigned.

SHARED_PASSIVES_BY_TYPE = {
    "Normal": [
        {"name": "Scrappy", "description": "Deals 10% more damage to opponents with a higher level."},
        {"name": "Adaptable", "description": "After being hit by an attack, gains a small amount of resistance to that attack's type for the rest of the battle."},
        {"name": "Vigor", "description": "This pet is immune to effects that would lower its stats."},
    ],
    "Fire": [
        {"name": "Kindle", "description": "Has a 10% chance to burn an attacker who makes physical contact."},
        {"name": "Flash Fire", "description": "When hit by a Fire-type move, this pet takes no damage and its own Fire moves are powered up."},
        {"name": "White Smoke", "description": "Prevents other pets from lowering this pet's stats."},
    ],
    "Water": [
        {"name": "Hydration", "description": "Heals for a small amount at the end of each turn if the weather is rainy."},
        {"name": "Swift Swim", "description": "This pet's Speed is doubled in rainy weather."},
        {"name": "Aqua Veil", "description": "Prevents this pet from being burned."},
    ],
    "Grass": [
        {"name": "Natural Remedy", "description": "At the end of each turn, has a 10% chance to cure itself of a status condition."},
        {"name": "Chlorophyll", "description": "This pet's Speed is doubled in sunny weather."},
        {"name": "Leaf Guard", "description": "Prevents status conditions in sunny weather."},
    ],
    "Electric": [
        {"name": "Static Charge", "description": "Has a 30% chance to paralyze an attacker who makes physical contact."},
        {"name": "Motor Drive", "description": "Absorbs Electric-type moves, taking no damage and increasing its Speed."},
        {"name": "Volt Absorb", "description": "Absorbs Electric-type moves, taking no damage and restoring a small amount of HP."},
    ],
    "Ice": [
        {"name": "Ice Body", "description": "Heals for a small amount at the end of each turn if it is hailing."},
        {"name": "Thick Fat", "description": "Reduces incoming damage from Fire and Ice-type moves by 50%."},
        {"name": "Slush Rush", "description": "This pet's Speed is doubled in hailing weather."},
    ],
    "Fighting": [
        {"name": "Guts", "description": "If this pet has a status condition, its Attack is increased by 50%."},
        {"name": "Inner Focus", "description": "This pet cannot be made to flinch."},
        {"name": "Iron Fist", "description": "Increases the power of punching moves by 20%."},
    ],
    "Poison": [
        {"name": "Corrosive Touch", "description": "Physical contact moves have a 10% chance to lower the target's Defense."},
        {"name": "Poison Point", "description": "Has a 30% chance to poison an attacker who makes physical contact."},
        {"name": "Liquid Ooze", "description": "An opponent that uses a draining move on this pet will take damage instead of healing."},
    ],
    "Ground": [
        {"name": "Tremorsense", "description": "This pet's Ground-type moves have slightly increased accuracy."},
        {"name": "Sand Veil", "description": "Increases this pet's evasion during a sandstorm."},
        {"name": "Earth Eater", "description": "Absorbs Ground-type moves, taking no damage and restoring a small amount of HP."},
    ],
    "Flying": [
        {"name": "Keen Eye", "description": "Prevents this pet's accuracy from being lowered."},
        {"name": "Gale Wings", "description": "Gives priority to Flying-type moves when this pet is at full health."},
        {"name": "Wind Rider", "description": "When hit by a Wind-type move, this pet takes no damage and its Attack is raised."},
    ],
    "Psychic": [
        {"name": "Synchronize", "description": "When this pet is burned, poisoned, or paralyzed, the opponent also gets that status condition."},
        {"name": "Magic Guard", "description": "This pet only takes damage from direct attacks, not from status effects like poison or burn."},
        {"name": "Telepathy", "description": "This pet anticipates and dodges attacks from its allies in a double battle."},
    ],
    "Bug": [
        {"name": "Swarm Tactics", "description": "When this pet's HP is low, the power of its Bug-type moves is increased."},
        {"name": "Shed Skin", "description": "At the end of each turn, has a 30% chance to cure itself of a status condition."},
        {"name": "Compound Eyes", "description": "Increases the accuracy of this pet's moves by 30%."},
    ],
    "Rock": [
        {"name": "Sturdy", "description": "If this pet is at full health, it will survive any single hit with 1 HP remaining."},
        {"name": "Rock Head", "description": "This pet does not take recoil damage from its own moves."},
        {"name": "Sand Force", "description": "Increases the power of Rock, Ground, and Steel-type moves during a sandstorm."},
    ],
    "Ghost": [
        {"name": "Cursed Body", "description": "When hit by an attack, has a 30% chance to disable that move for a few turns."},
        {"name": "Infiltrator", "description": "This pet's moves ignore the effects of the opponent's defensive barriers and stat boosts."},
        {"name": "Pressure", "description": "The opponent uses twice as much energy when attacking this pet."},
    ],
    "Dragon": [
        {"name": "Multiscale", "description": "If this pet is at full health, the damage it takes from an attack is halved."},
        {"name": "Rough Skin", "description": "An attacker who makes physical contact with this pet will take a small amount of damage."},
        {"name": "Dragon's Maw", "description": "Increases the power of Dragon-type moves by 50%."},
    ],
    "Fairy": [
        {"name": "Mystic Veil", "description": "This pet and its allies are immune to status conditions."},
        {"name": "Pixilate", "description": "Normal-type moves used by this pet become Fairy-type and receive a power boost."},
        {"name": "Flower Veil", "description": "Prevents Grass-type allies from having their stats lowered by opponents."},
    ]
}
