# Oakhaven Outpost — Design Document
# Status: LOCKED (brainstorm session, no code changes yet)
# For: coding session implementation reference

---

## Current Code State (main branch verified)

Already implemented:
- Full locations dict (4 slots): recruitment_hut, supply_chest, rest_point, rotting_pits
- Recruitment Officer Elara with dialogue (default, quest_the_first_step_step_1) — day only
- Bea (Supply Merchant) with minimal dialogue — day only
- Grit Galen with dialogue (default, quest_offer, quest_active, quest_complete) — day only
- Explore events: oakhavenOutpost_rottingPits and outpostWilds both fully written
- Encounter tables: outpostWilds = Pineling (day+night), rottingPits = Corroder (day+night)
- Quests: report_to_elara, a_guildsmans_first_steps, head_to_whisperwood, sunk_cost, forest_cleanup
- starter_pack on supply_chest (3-use, fully implemented)
- connection to weeping_chasm (requires quest_a_guildsmans_first_steps_completed)

Still missing (this doc covers everything below):
- NPC pets for all three NPCs
- Encounter table depth (single species per zone is too thin)
- Galen additional dialogue variants
- Pet rename: Pineling → Bristlecone, Barkback → Burlback (codebase-wide)

---

## Pet Rename — Codebase Wide

These are name changes only. Types, stats, skill trees, and descriptions unchanged.

| Old Name   | New Name    | Notes                                          |
|------------|-------------|------------------------------------------------|
| Pineling   | Bristlecone | Common, Normal type. Starter zone creature.    |
| Barkback   | Burlback    | Uncommon, Normal/Grass. Bristlecone evolution. |

Affects everywhere these names appear:
- data/pets.py — species names, evolution keys
- data/pets.py ENCOUNTER_TABLES — outpostWilds entry
- explore_events.py — outpostWilds events reference "Pineling" by name (multiple)
- Any NPC pet references in towns.py or remnants.py

---

## Amendment — Weeping Chasm v2 Doc

weeping_chasm_v2.md lists Warden Orin's pet as Barkback (no nickname).
That entry is now superseded by this doc.

**Orin's pet is Frostbile (nickname: none).**
Frostbile is the evolved form of Rimecrawl — a Chasm-native species (Ice/Poison).
It followed him along the chasm wall for weeks until he stopped chasing it off.
He does not consider that a bonding experience.
See weeping_chasm_v2.md for Rimecrawl/Frostbile species design.

Burlback (formerly Barkback) is now freed for Bea at Oakhaven. See NPC Pets below.

---

## NPC Pets

### Recruitment Officer Elara — Thornmoss, nicknamed "Spur"

Elara didn't go looking for a pet. A Mossling wandered in from the Wilds road years ago
and decided the recruitment hut doorstep was home. She named it when she was still a recruit
herself. Thought she'd be embarrassed by the name later. She wasn't.

Thornmoss has the quiet, unmovable confidence of something that chose where it stood and
hasn't reconsidered. It sits in the corner of the recruitment hut while Elara briefs new
recruits. It does not react to nervousness. Neither does she.

If player asks what it's called: *"I named him when I was a recruit. Figured I'd regret it.
I didn't."*

Spur is the only soft thing Elara ever lets you see about her.

---

### Grit Galen — Grimplate, nicknamed "Slag"

Galen pulled a Corroder out of the Pits seven years ago because it had a claw caught in
collapsed tar-stone and was going to lose the limb. He freed it. It followed him home.
He called it Slag — the same thing he called all Corroders, a leftover word from the
smelting trade. By the time he realized he was only using the name for this one, it was
too late to change it.

It evolved at some point. Galen doesn't remember when. He wasn't keeping track.

Slag still smells like tar. Always will. Galen stopped caring about that a long time ago.

If player asks about the pet: *"It came out of the pits. The pits are mine. So it's mine."*
He doesn't explain further.

Slag is with Galen during the day. At night — neither of them is at the Pits entrance.

---

### Bea — Burlback, nicknamed "Knot"

Bea brought a Bristlecone seedling-creature when the outpost was being built and it stayed.
It evolved somewhere along the years. She barely noticed. It just got bigger and slower
and harder to step around.

She named it Knot because it was always in the way, like a knot in a floorboard. She steps
around it every morning without thinking about it anymore.

If player asks about it: *"Oh, it's been here longer than most of the furniture."*

Burlback is behind the supply chest counter. It does not move for customers.

---

## Additional Dialogue — Grit Galen

Add to existing dialogue dict in towns.py:

- `pit_growth` (fires after sunk_cost quest complete):
  *"The far edge moved another foot this week. Don't put that in any report."*

- `returning_high_rank` (fires at Veteran rank or above):
  *"You made it this far. Good. Come back when you've seen the Chasm. Tell me if what's
  down there looks anything like what's in the Pits."*

Note: Galen suspects the Rotting Pits and the Weeping Chasm share a Gloom source — same
breach, different surface points. He will never say this directly. A player who has been
to both will understand the question. This is a lore thread, not a quest hook. No quest
needed here.

---

## Side Story — Galen's Vigil

Oakhaven doesn't have a dramatic side story. It has a quiet one.

The Pits are expanding. The explore event already seeds this:
*"Grit Galen's scratched warning marker — a stick with a strip of red cloth — stands at
the pit's edge. Someone keeps moving it further back. The pits are growing."*

That someone is Galen. He moves the marker without filing reports because reports bring
investigators, investigators close the Pits, and closing the Pits removes the only thing
that still makes this post worth watching. He has been here long enough to know that
the Guild responds to paperwork, not to slow disasters.

He walks the perimeter at night. Elara knows. She doesn't ask about it.
Slag goes with him.

This is expressed through explore event flavor and the new dialogue variants above.
It does not need a quest wrapper.

---

## Encounter Tables — Updates

### outpostWilds

```
Day:   Bristlecone (common), Mossling (low chance — forest edge creature, not its territory)
Night: Bristlecone (common), Mossling (rare — lost)
```

Mossling justification: the outpost sits on the road toward Whisperwood. Mossling already
appears in a choice event in the Wilds ("a wounded Mossling sits in the path"). It is
primarily a Whisperwood creature but its presence at the forest edge is geographically
natural. Gives players an early glimpse of what's ahead. Rare enough to not overshadow
Bristlecone.

### oakhavenOutpost_rottingPits

```
Day:   Corroder (common)
Night: Corroder (common), Grimplate (rare — larger, surfaces after dark)
```

Grimplate at night is already seeded in the explore events: "something large and dark shifts
beneath the surface of the largest pit." Night only, rare weight. Gives returning players
something to find. Grimplate is the renamed Sludge Shell — see weeping_chasm_v2.md for
full rename notes on the Corroder evolution line.

### Starter Pets (Dewdrop)

Dewdrop appears as a pet_sighting flavor event in outpostWilds. It is NOT in the encounter
table and is NOT capturable here.

Starter pets (Dewdrop, Bristlecone, and the third starter) are intended to be capturable
in the late game — location and method TBD. They remain flavor-only in the wild until that
system is designed.

---

## Implementation Notes for Coding Session

1. data/pets.py — rename Pineling → Bristlecone, Barkback → Burlback everywhere.
   Name change only. Types, stats, skill trees, descriptions unchanged.

2. explore_events.py — find all "Pineling" references in outpostWilds events and update
   to "Bristlecone."

3. data/pets.py ENCOUNTER_TABLES:
   - outpostWilds: add Mossling as low-chance encounter (day + night)
   - oakhavenOutpost_rottingPits: add Grimplate to night encounters (rare weight)

4. data/towns.py — add pet data to existing NPC entries:
   - Elara: Thornmoss, nickname "Spur"
   - Grit Galen: Grimplate, nickname "Slag"
   - Bea: Burlback, nickname "Knot"

5. data/towns.py — add new dialogue variants to Grit Galen:
   - pit_growth (post sunk_cost)
   - returning_high_rank (Veteran rank+)

6. data/remnants.py — update Warden Orin's pet entry:
   - Remove Barkback (if already added from v2 doc)
   - Add Frostbile, no nickname
   - See weeping_chasm_v2.md for Frostbile species details

7. Bristlecone/Burlback rename is a grep-and-replace across the codebase.
   Recommended: do this in a single dedicated commit before other Oakhaven changes
   to keep the diff clean.
