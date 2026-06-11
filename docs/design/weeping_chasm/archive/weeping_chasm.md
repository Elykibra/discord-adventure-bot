# Weeping Chasm — Design Document
# Status: LOCKED (brainstorm session, no code changes yet)
# For: coding session implementation reference

---

## Overview

The Weeping Chasm is a Remnant between Oakhaven Outpost and Whisperwood Grove.
It is the most significant remnant on this road — the Gloom's origin point in Aethelgard.
It should feel like a short side story, not a road stop.

Current code state: skeleton exists in `data/remnants.py`. 
Gloom level: 25. NPC: Warden Orin (day only). Explore zone key set but NO explore events written yet.

---

## UI Layout

Same layout as towns — NOT a special case:

```
[ Locations dropdown ]
[ Explore Area ]  [ Travel ]
```

No Rest button — the Chasm has no rest service.

Travel button opens a destination select pulling from the remnant's `connections` dict:
- Back: Oakhaven Outpost (always open)
- Forward: Mirefields (requires `quest_a_guildsmans_first_steps_completed`)

---

## Locations Dropdown

Four slots. All always visible. Greyed out based on conditions.

| # | Label | NPC / Service | Availability |
|---|---|---|---|
| 1 | The Chasm's Edge | Explore zone | Always |
| 2 | The Warden's Post | Warden Orin | Day only — greyed out at night |
| 3 | The Scholar's Camp | Lore-Keeper Kael | Quest-gated — greyed out until `echoes_from_below` is active |
| 4 | The Lookout Hollow | "Grim" Gretta | Always |

Greyed-out slots are intentional — player sees there is more here, which creates pull.

---

## NPCs

### Warden Orin
- Role: Guild Warden
- Emoji: 🛡️
- Availability: Day only
- Permanent — always here during the day, Guild-assigned post
- Tone: tired but reliable, not scared, adjusted to the wrongness of this place

Dialogue variants:
- `default`: Road warning. The Gloom draws creatures here. He keeps watch so travelers can pass. Mostly.
- `lore_prompt`: References Guild records. Says he's felt the Gloom "thinking" on certain nights. Doesn't put that in reports.
- `returning_recruit`: If player has `quest_a_guildsmans_first_steps_completed` — acknowledges them as a Guild recruit, slightly warmer.
- `night_note` (shown instead of NPC when it's night): A note pinned to the Warden's post. Short, dry. Classic Orin. Something like: "Gone at dark. You should be too. — O."

---

### Lore-Keeper Kael
- Role: Guild Scholar (field researcher, unsanctioned)
- Availability: Only present when player has quest `echoes_from_below` active
- Tone: intellectually excited, slightly reckless, genuinely cares about understanding the Gloom
- He is never in a town — always at remnants, always at the edge of something dangerous

Quest flow (`echoes_from_below`):
1. Player sent to the Chasm by Elder Vexia to find Kael
2. Kael asks player to collect 3x `gloom_mist_sample` from The Chasm's Edge (explore events)
3. Samples collected → Kael processes them, hands player his findings (quest item or lore doc)
4. Kael tells player: "When you reach the Oasis — find the Monoliths. I'll be there."
5. Kael disappears from the Chasm. Thread dangles toward Sunstone Oasis.

This establishes Kael as a recurring NPC chain across remnants (Chasm → Obsidian Monoliths → further).

Dialogue variants:
- `default` (quest active, samples not collected): Explains the sample task, why the origin point matters
- `samples_collected`: Processes findings, delivers the forward hook to the Oasis
- `lore_gloom_origin`: His theory on why the Gloom first breached here specifically
- `lore_hollowed_vs_corrupted`: Scholar perspective on the difference — corrupted pets can still be reached, Hollowed cannot

---

### "Grim" Gretta
- Role: Chasm Watcher (self-appointed, no Guild affiliation)
- Emoji: TBD — something weathered. 🪨 or 🗡️
- Availability: Always — day and night
- Permanent — she never leaves. Has been here longer than Orin.
- Tone: blunt, world-weary, no patience for idealism. Not hostile, just honest in a way that cuts.
- Backstory hook: Watched the Gloom take someone she knew. Decided rehabilitation was a fairy tale.

Purpose: Introduce the **Subdue path** for corrupted pets. She is the counterweight to Guild philosophy.

Dialogue variants:
- `default`: Blunt greeting. Immediately challenges the player's assumptions about the Gloom.
- `player_has_pet`: Comments on the player's active pet specifically. Respects strength, skeptical of "healing" anything.
- `subdue_path_intro`: Explains her philosophy — controlling a corrupted creature is not cruelty, it is honesty. Offers to teach the Subdue method.
- `returning_high_rank`: Same hollow, same view. She acknowledges the player has survived. That's all she'll give.

NOTE: The Five Paths system is not yet implemented in code. 
Gretta should be placed now and her Subdue path dialogue written, but the mechanical unlock 
can be wired later when the Five Paths system is built.

---

## Explore Events — The Chasm's Edge

Target: ~10 events. Zone key: `weeping_chasm` (already set in `data/remnants.py`).
Tone: cold, ominous, vertigo-inducing. Something is aware here.

### Flavor Events
```
- The chasm exhales cold air in a slow rhythm. Your pet refuses to approach the edge.
- A Guild marker post — cracked, the rune barely holding. Someone scratched a tally into the wood. Thirty-seven marks.
- A sound rises from below. Not a creature — more like a voice, too deep and too slow to understand. It stops when you move.
```

### Flavor Event (night only — requires time_of_day filter)
```
- The mist curls upward around your ankles. Nothing attacks. Something is just checking.
```

### Pet Sighting Events
```
- A Corroder sits at the chasm's lip, staring down into the dark instead of at you. 
  It doesn't react to your presence. It seems drawn to the source.

- Something pale drifts upward from the chasm on the thermal — translucent, slow, gone 
  before you can focus on it.
```

### Hazard Events
```
- A cold updraft hits without warning — disorienting, wrong. Your pet stumbles.
  outcome: { hp: -8 }

- The ground near the sealed section shifts. A crack opens, runs three feet, stops. 
  You step back slowly.
  outcome: { energy: -1 }
```

### Loot Bonus Event
```
- A Guild emergency cache, bolted to a post near the sealed section. Still stocked.
  outcome: { item: tether_orb or moss_balm, qty: 1 }
```

### Choice Events
```
1. A sealed Guild journal wedged in a crack near the edge.
   - "Pry it open": risk a stumble, gain lore fragment. outcome: { gloom_tick: +5, item: lore_fragment }
   - "Leave it": nothing happens.

2. Gloom-mist pools in a hollow in the rock — dense enough to collect.
   ONLY fires during quest `echoes_from_below`.
   - "Fill a sample vial": outcome: { quest_item: gloom_mist_sample, qty: 1 }
   - "Walk past": nothing.
```

---

## New Items Needed

| Item ID | Name | Type | Notes |
|---|---|---|---|
| `gloom_mist_sample` | Gloom-mist Sample | Quest item | Collected at Chasm's Edge during Kael's quest. No other use. |
| `lore_fragment` | Guild Record Fragment | Lore item | Optional — from choice event. Could display lore text when used. |

---

## New Quest Needed

Quest ID: `echoes_from_below` (name subject to change — placeholder)

- Giver: Elder Vexia (Oakhaven Outpost)
- Step 1: Travel to the Weeping Chasm
- Step 2: Find Lore-Keeper Kael at The Scholar's Camp
- Step 3: Collect 3x `gloom_mist_sample` from The Chasm's Edge
- Step 4: Return to Kael
- Reward: TBD (XP, lore doc, item) + forward hook to Obsidian Monoliths / Sunstone Oasis
- Section: Section 1 main quest arc

---

## Implementation Notes for Coding Session

1. `explore_events.py` — add `weeping_chasm` key with the events above
2. `data/remnants.py` — Warden Orin already exists. Add Kael and Gretta to `npcs` dict with quest-gate flag for Kael.
3. `data/quests.py` — add `echoes_from_below` quest
4. `data/items.py` — add `gloom_mist_sample` (and optionally `lore_fragment`)
5. Explore event system — check if `time_of_day` filter exists for night-only events. If not, that's a small system addition needed before night-exclusive events can fire.
6. Gretta's Subdue path dialogue — write now, wire to Five Paths system later when it's built.
7. Kael's quest-gate in the dropdown — the locations dropdown needs to support a `required_flag` or `required_quest` condition per slot to grey out Kael's camp.

---

## Remnant Design Philosophy (applies to ALL future remnants)

Every remnant has a story. Not a town, not a quest hub — a beat.

Rules:
- 1-2 permanent NPCs who BELONG to that specific place. They wouldn't exist anywhere else.
- 6-10 explore events (flavor, hazard, loot, choice, pet sighting)
- One quest thread max — either a hook into the remnant from a town, or a thread leading out
- Optional: one time-of-day distinction (night behavior, night-only NPC, night-only events)

What remnants are NOT:
- Not mini-towns. No inn. Shops are rare exceptions (Sable at Mirefields is the model — sparse).
- Not quest hubs. One thread max.
- Not filler. If a remnant has nothing to say, it doesn't get built yet.

The dropdown is NOT conditional. Every remnant has a locations dropdown because every remnant
has content. Complexity varies — Glade of Whispers might have 2 slots, Weeping Chasm has 4 — 
but the pattern is consistent.

---

## Travel System Design (going forward)

Button layout — consistent across ALL remnants:
```
[ Locations dropdown ]
[ Explore Area ]  [ Rest* ]  [ Travel ]
```
*Rest only renders if remnant has a rest service defined.

Travel button behavior:
- Opens destination select (Discord select menu)
- Options pulled automatically from remnant's `connections` dict — no hardcoding
- Back connection: always open
- Forward connection: respects `connection_requirements` dict (same pattern as towns.py)

This is the same pattern already used in towns. No new UI system needed — just apply the 
existing pattern to remnants consistently.
