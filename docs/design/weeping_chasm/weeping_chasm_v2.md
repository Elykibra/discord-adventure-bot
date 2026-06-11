# Weeping Chasm — Design Document (Revisit)
# Status: LOCKED (brainstorm session, no code changes yet)
# For: coding session implementation reference
# Note: Supersedes weeping_chasm.md for all new content below.
#       Existing code (locations, NPCs, dialogue) already implemented — see code state below.

---

## Current Code State (main branch verified)

Already implemented:
- Full locations dict (4 slots): Chasm's Edge, Warden's Post, Scholar's Camp, Lookout Hollow
- Warden Orin with dialogue (default, lore_prompt, returning_recruit, night note)
- Lore-Keeper Kael with dialogue (default, samples_collected) + required_quest gate
- Grim Gretta with dialogue (default, player_has_pet, subdue_path_intro) + rough camp rest
- Inline travel dropdown live (PR #25)
- connection_costs defined

Still missing (this doc covers everything below):
- Explore events — weeping_chasm key does not exist in explore_events.py
- Encounter table — no pets assigned to zone in pets.py
- New pets (all new species below)
- NPC pet assignments
- Renamed evolution lines
- Ancient rarity tier
- Apex creature lore + rank-gated encounters
- Quest echoes_from_below
- Items

---

## Rarity System Update

Add Ancient tier between Rare and Legendary:

```
Starter → Common → Uncommon → Rare → Ancient → Legendary
```

Ancient = powerful regional creatures. Not Great Spirits. Can theoretically be captured
at extremely low rates at high rank. No evolutions in most cases — they are already
near their final form.

---

## Renamed Evolution Lines (existing pets — name changes only)

### Corroder line
- Corroder (Common) → **Grimplate** (Uncommon) → **Blightcrust** (Rare)
- Was: Corroder → Sludge Shell → Ossuary Golem
- Corroder base name stays. Evolutions renamed only. Skill trees unchanged.

### Grimweave line (was Gloom Weaver)
- **Grimweave** (Uncommon) → **Duskspinner** (Rare) → **Veilmother** (Ancient)
- Was: Gloom Weaver → Dreadspinner (code) / Shadow Spinner → Venomfang Broodmother (docs)
- Rename Gloom Weaver → Grimweave everywhere in code
- Veilmother is Ancient — lore hint only for now, not in encounter table yet

---

## New Pets — Weeping Chasm

### Gauntling → Waneling
- Type: Ghost / Normal
- Rarity: Common → Uncommon
- Gloom-touched: Yes
- Personality: Timid

Gauntling: A creature that has lived too close to the Gloom source for generations.
Not violently corrupted — born already fading. Partially translucent, slow-moving, like
something losing its physical definition over time. It isn't Hollowed yet. It's on the way
there and doesn't know it. Tone: sad more than scary. The Chasm's most common creature
and somehow its most unsettling.

Waneling: Further faded. More ghost than creature now. Barely there. Still moves. Still hunts.
At this stage it barely registers on the eye — you sense it more than see it.

Passive ability idea: Small chance to phase through incoming physical attacks.
Evolution level: ~15
Encounter: Day and night.

---

### Rimecrawl → Frostbile
- Type: Ice / Poison
- Rarity: Uncommon → Rare
- Gloom-touched: Yes
- Personality: Defensive

Rimecrawl: Moves along the chasm walls, slow and methodical. Leaves trails of frost-laced
Gloom residue. Where it passes, the stone gets colder. You notice the trails before you
notice the creature. Patient. Creeping. Wrong in a quiet way.

Frostbile: Larger, slower. The trail it leaves now crystallizes into something that damages
anything walking through it. Turns the terrain into a weapon.

Passive ability idea: Trail effect — minor damage and slow to anything following its path.
Evolution level: ~16
Encounter: Day and night.

---

### Threshling → Threshbound
- Type: Dark / Ghost
- Rarity: Rare → Ancient
- Gloom-touched: Yes — perpetually, irreversibly
- Personality: Aggressive

Threshling: Caught at the threshold between existence and full Gloom consumption.
Parts of it solid, parts of it mist. One eye clear, one eye dark. Not fully Hollowed —
locked in between states. Gretta caught one at this exact moment and has held it there.
The Subdue path made physical.

Threshbound: Stage 2 is Ancient rarity — not because it grew larger, but because it became
something that defies classification. Has been held at the threshold so long it IS the
threshold. Barely contained. Seeing one should feel like a warning.

Passive ability idea: Drains opponent Gloom Meter passively each turn.
Evolution level: ~20
Encounter: Threshling — night only, Rare.
Threshbound — NOT in encounter table. Gretta has one. Nobody else does.

---

## Encounter Table

| Time | Pets |
|---|---|
| Day | Gauntling, Rimecrawl, Corroder |
| Night | Gauntling, Rimecrawl, Grimweave, Corroder |

Evolution stages as low-chance encounters:
- Waneling: low chance, night weighted
- Frostbile: low chance, both times
- Grimplate: low chance, night weighted
- Threshling: night only, rare

NOT in table: Threshbound, Veilmother, Chasmbane

---

## NPC Pets

Rule: field NPCs in dangerous zones default to having a pet. The pet reflects who they are.
See mirefields.md for full NPC pet design rule documentation.

### Warden Orin — Barkback (no nickname)
Guild wardens don't name working partners officially. This Barkback evolved from a Pineling
issued to Orin early in his posting. Tough, quiet, reliable. Doesn't flinch at the cold air
anymore. Neither does Orin. They've both adjusted.
If player asks what it's called: *"It's a warden's pet. Doesn't need a name, needs to work."*

### Lore-Keeper Kael — Duskspinner, nicknamed "Threnody"
A scholar who keeps a Gloom-adjacent spider as a companion says everything about who he is.
Duskspinner is the second evolution of Grimweave — Kael has been doing this long enough for
his companion to evolve alongside him. He named it Threnody — a funeral song — referencing
the Gloom's origin in collective sorrow. He will explain the etymology if asked. You didn't ask.
Having a Duskspinner (not base Grimweave) shows experience and commitment.

### "Grim" Gretta — Threshling (no nickname)
She didn't purify it. She made it clear who was in charge. It stays because she makes it stay.
The player sees it before she explains anything and already understands her philosophy.
If asked what it's called: *"It isn't."*

---

## Additional Dialogue to Add (existing NPCs)

### Warden Orin (add to existing dialogue dict)
- `lore_east_wall`: *"The east section of the wall is webbed over some mornings. Something
  large made that overnight. I don't go near it."* — passive Veilmother hint.
- `lore_breathing`: *"Some mornings the mist is different. Heavier. Like something exhaled
  the whole of it at once."* — passive Chasmbane hint.

### Lore-Keeper Kael (add to existing dialogue dict)
- `lore_gloom_origin`: His theory on why the Gloom first breached here specifically.
- `lore_hollowed_vs_corrupted`: Scholar's perspective — corrupted pets can still be reached,
  Hollowed cannot. Key distinction for the player to understand early.
- `lore_east_wall`: References his research notes — *"A specimen of unusual scale observed
  on east face. Preliminary classification impossible."* One entry. No follow-up. Next page blank.
  — Veilmother hint through his research.

### "Grim" Gretta (add to existing dialogue dict)
- `lore_deep_chasm`: *"Nothing worth finding out there."*
  If pressed second time: *"The breathing. You've heard it. Don't go looking for what makes it."*
  — Chasmbane hint.
- `returning_high_rank`: Same hollow, same view. She acknowledges the player survived.
  That's all she gives.

---

## Two Apex Ancients

Both reside within The Chasm's Edge explore zone — no separate dropdown slot needed.
Both exist in lore from day one through NPC dialogue and explore events.
Both are NOT in the encounter table at early stages.

The Tainted Ledge and Whispering Stones (from original design docs) are referenced
as named locations within explore event text — not separate slots.

### Veilmother (Ancient)
- Third evolution of the Grimweave line
- Lives on the east wall face of the chasm
- Passive — doesn't hunt, waits. Everything that falls into the chasm finds its web.
- The east wall webbing is visible from the Edge. Orin doesn't go near it.
- Kael has one research note entry. No follow-up. The next page is blank.
- Capturable at Legend rank (theoretically)

### Chasmbane (Ancient — lore entity)
- Unique Ancient, no evolution line
- Lives at the bottom of the Chasm
- The cold mist rising from the Chasm IS its breath — seeded in location description day one
- Surfaces near the rim occasionally. When it does, everything in the area goes silent.
- No Guild classification. No species name in any record.
- Orin calls it nothing — he doesn't acknowledge it in writing.
- Gretta calls it "the breathing."
- Kael has one note that stops mid-sentence.
- NOT capturable at any rank — permanent lore entity only

### Rank-Gated Encounter Logic

| Rank | Novice / Journeyman | Wanderer | Veteran | Master / Champion | Legend |
|---|---|---|---|---|---|
| Veilmother | Not in table | Scare encounter — Gloom spike, forced retreat, no battle | Battle starts, flees after a few turns, capture rate 0 | Full encounter, capture near impossible | Theoretically capturable |
| Chasmbane | Not in table | Scare encounter — Gloom spike, forced retreat, no battle | Same — flees, cannot capture | Same | Never capturable |

Scare encounter design: special flavor message, Gloom Meter spikes hard, player is forced
to retreat. No battle UI opens. Player walks away knowing something is there they can't touch.
This recontextualises all the lore hints they've been reading since Novice rank.

TAG FOR IMPLEMENTATION REVIEW: Confirm rank-gating logic is feasible with current encounter
system before building. Lore hints in events and dialogue go in regardless.

---

## Explore Events — The Chasm's Edge

Target: ~12 events. Zone key: `weeping_chasm`
Tone: cold, ominous, vertigo-inducing. Something is aware here.
The Tainted Ledge and Whispering Stones are referenced within event text as named spots.

### Flavor Events
```
- The chasm exhales cold air in a slow rhythm. Your pet refuses to approach the edge.

- A Guild marker post — cracked, the rune barely holding. Someone scratched a tally into
  the wood. Thirty-seven marks. You don't know what they're counting.

- A sound rises from below. Not a creature — more like a voice, too deep and too slow to
  understand. It stops when you move.

- Near the Whispering Stones — a cluster of rounded rocks at the sealed section — the air
  hums faintly. Guild records say this is where the first ward was placed. Whatever it was
  holding, it's still holding.
```

### Flavor Events (night only — requires time_of_day filter)
```
- The mist curls upward around your ankles. Nothing attacks. Something is just checking.

- The breathing from below changes rhythm. Slower. Deeper. Your pet goes completely still
  and won't move until it resumes its normal pace.
```

### Pet Sighting Events
```
- A Corroder sits at the chasm's lip, staring down into the dark instead of at you.
  It doesn't react to your presence. It seems drawn to the source.

- Something pale drifts upward from the chasm on the cold thermal — translucent, barely
  there, gone before you can focus on it.

- The east wall of the Chasm is covered in thick, dark silk from rim to rock face.
  Something enormous spun this overnight. The webbing is still faintly warm.
```

### Hazard Events
```
- A cold updraft hits without warning — disorienting, wrong. Not wind. An exhale from below.
  Your pet stumbles.
  outcome: { hp: -8 }

- The ground near the Tainted Ledge shifts. A crack opens, runs three feet, stops.
  You step back slowly.
  outcome: { energy: -1 }
```

### Loot Bonus Event
```
- A Guild emergency cache bolted to a post near the sealed section. Still stocked.
  outcome: { item: tether_orb or moss_balm, qty: 1 }
```

### Choice Events
```
1. A sealed Guild journal wedged in a crack near the Tainted Ledge.
   - "Pry it open": gain lore_fragment, minor risk.
     outcome: { gloom_tick: +5, item: lore_fragment }
   - "Leave it": nothing.

2. Gloom-mist pools in a hollow in the rock — dense enough to collect.
   ONLY fires during quest echoes_from_below.
   - "Fill a sample vial": outcome: { quest_item: gloom_mist_sample, qty: 1 }
   - "Walk past": nothing.
```

---

## New Items Needed

| Item ID | Name | Type | Source | Notes |
|---|---|---|---|---|
| `gloom_mist_sample` | Gloom-mist Sample | Quest item | Chasm's Edge explore event (quest only) | 3 needed for echoes_from_below. No other use. |
| `lore_fragment` | Guild Record Fragment | Lore item | Choice event — sealed journal | Displays lore text when used. Optional. |

---

## New Quest Needed

Quest ID: `echoes_from_below` (name subject to change)

- Giver: Elder Vexia (Oakhaven Outpost)
- Step 1: Travel to the Weeping Chasm
- Step 2: Find Lore-Keeper Kael at The Scholar's Camp
  (required_quest gate already wired in code — quest data just needs writing)
- Step 3: Collect 3x gloom_mist_sample from The Chasm's Edge
- Step 4: Return to Kael
- Reward: TBD (XP + lore item) + forward hook to Obsidian Monoliths / Sunstone Oasis
- Section: Section 1 main quest arc

---

## Implementation Notes for Coding Session

1. Add Ancient to rarity constants wherever rarity is defined in code.

2. `data/pets.py` — rename existing evolution lines:
   - Gloom Weaver → Grimweave (everywhere in code)
   - Dreadspinner → Duskspinner
   - Add Veilmother as Ancient stub on Grimweave line
   - Sludge Shell → Grimplate
   - Ossuary Golem → Blightcrust
   Skill trees unchanged — name changes only.

3. `data/pets.py` — add new species with stub stats:
   - Gauntling → Waneling (Ghost/Normal, Common/Uncommon)
   - Rimecrawl → Frostbile (Ice/Poison, Uncommon/Rare)
   - Threshling → Threshbound (Dark/Ghost, Rare/Ancient)

4. `data/pets.py` ENCOUNTER_TABLES — add weeping_chasm:
   Day: Gauntling, Rimecrawl, Corroder
   Night: Gauntling, Rimecrawl, Grimweave, Corroder
   Evolution stages as low-chance encounters.
   Threshling: night only, rare weight.
   Threshbound / Veilmother / Chasmbane: NOT in table.

5. `data/remnants.py` — add pet data to existing NPC entries:
   Orin: Barkback, no nickname
   Kael: Duskspinner, nickname "Threnody"
   Gretta: Threshling, no nickname

6. `data/remnants.py` — add dialogue variants to existing NPCs:
   Orin: lore_east_wall, lore_breathing
   Kael: lore_gloom_origin, lore_hollowed_vs_corrupted, lore_east_wall
   Gretta: lore_deep_chasm, returning_high_rank

7. `explore_events.py` — add weeping_chasm key (~12 events above).
   Check if time_of_day filter exists — needed for night-only events.
   If not implemented: add time_of_day field to event schema first.

8. `data/items.py` — add gloom_mist_sample, lore_fragment

9. `data/quests.py` — add echoes_from_below quest

10. Rank-gated apex encounters — review feasibility first.
    Lore hints in events and NPC dialogue go in regardless of system readiness.
    Chasmbane is never capturable — lore entity only.
