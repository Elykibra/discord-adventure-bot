# Mirefields — Design Document
# Status: LOCKED (brainstorm session, no code changes yet)
# For: coding session implementation reference

---

## Overview

The Mirefields is a Remnant between Weeping Chasm and Whisperwood Grove.
Low Gloom presence (gloom_level: 8) — the danger here is physical, not supernatural.
Bad terrain, mean creatures, thick fog. Not everything dangerous needs to be cosmically threatening.

The Mirefields used to matter. It was a busy trading crossroads. It doesn't anymore.
The mire won. That's the whole story of this place — and the two people who stayed anyway.

Current code state: skeleton exists in `data/remnants.py`. Sable exists with 3 dialogue lines
and a shop. Explore zone key set but NO explore events written. No second NPC. No pets assigned.

---

## UI Layout

```
[ Locations dropdown ]
[ Explore Area ]  [ Rest* ]  [ Travel ]
```

No Rest button — the Mirefields has no rest service.

Travel button pulls from `connections` dict:
- Back: Weeping Chasm (always open)
- Forward: Whisperwood Grove (no requirement gate — open road)

---

## Locations Dropdown

| # | Label | Who / Service | Availability |
|---|---|---|---|
| 1 | The Mire Path | Explore zone | Always |
| 2 | Sable's Camp | Sable + shop | Always |
| 3 | The Old Crossroads | Ruins — lore + choice event | Always |
| 4 | The Reed Hollow | Ferryn — naturalist | Seasonal (see Ferryn notes) |

---

## NPC: Sable

### Who She Is

Sable grew up on the edge of the Mirefields when the crossroads waystation was still active.
Her family ran traps in the outer bog. She learned the mire young — completely, without thinking
about it, the way you learn a language when you're a child.

When the waystation collapsed — road fell out of use, traders rerouted, buildings sank — 
everyone left. Sable didn't. Not stubbornness exactly. More like: the version of this place
she'd always wanted finally existed. No noise. No traffic. No one telling her where to go.

She's been the mire's only permanent resident for years. She knows every soft patch, every
creature territory, every section that's expanded since she was a kid. Her camp doesn't sink.
Her traps don't fail. The creatures near her leave her alone because they've learned to.

She is not a hero. Not a villain. Just someone who always wanted to live alone, and finally got it.

### What She Does

Trapping. Bog creatures — not for Guild, not for any market. She catches what threatens her
camp, processes what she can use, trades the rest to travelers. Her shop isn't a business.
It's surplus.

She also actively manages the mire around her camp — creature territories, water channels,
seasonal trap placement. She is effectively the mire's only caretaker, though she'd never
describe it that way.

### What She Wants

On the surface: to be left alone.
Underneath: to keep the Mirefields exactly as it is. Forgotten. Off the main road. Hers.

This is her tension with Ferryn — Ferryn's research into the mire's expansion and potential
crossroads restoration is, to Sable, a threat dressed as curiosity. She's not hostile about it.
She just has zero interest in the mire becoming a waystation again.

There are sections of the mire Sable doesn't enter. Deeper in, past where travelers go.
She doesn't explain this. If asked directly: *"Nothing worth finding out there."*
Whether that's pragmatism or something she's decided not to think about — unclear to the player.

### Voice

Short sentences. No wasted words. Answers what you ask and nothing more unless she chooses to.
Not rude — economical. Occasionally dry in a way that takes a second to land. Doesn't perform
gruffness. Just genuinely not interested in pleasantries.

### Her Pet — Ledge (Murkwall)

Sable found a juvenile Murkback years ago — injured, probably driven from its territory.
She patched it up because leaving it to suffer was wasteful. Expected it to leave. It did.

Two seasons later it came back. Twice the size. Second evolution — a Murkwall now.
She recognized it by the scar on its left flank, still visible under the armor plating,
healed clean from where she had patched it.

She didn't make anything of it. It sat on a flat rock near the water's edge and didn't move.
It's been there since. She works around where it sleeps. There's a worn spot near her fire
that is clearly its spot.

She doesn't call it anything publicly. If the player asks what its name is: *"Doesn't need one."*

If the player returns at high rank and asks again — she might let something slip.
She calls it *Ledge*. Because it always sits on the same rock. That's all.
She won't repeat it.

Other creatures in the Mirefields don't cross into Sable's camp radius. Not because of Sable.
Because of Ledge. It doesn't patrol. It just exists there. Everything else has done the math.

**If the player has a Murkback:** Sable notices. One line —
*"Caught one of those, did you. Give it time."* That's all she says.

### Dialogue Variants

- `default`: *"You lost? Most people don't come through here by choice. I've got supplies if
  you need them — nothing fancy, but it'll keep you alive."* (keep existing line)

- `night`: *"You're braver than most, traveling through here at night. Or dumber. Hard to tell.
  Watch your step — the mire shifts after dark."* (keep existing line)

- `sell`: *"Take what you need and move on. I don't do small talk."* (keep existing line)

- `lore_crossroads`: Asked about the old camp. Factual, no sentiment. It was busy, then it
  wasn't. The mire came up one wet season and didn't stop. "Not everything's meant to last."

- `lore_ferryn`: If Ferryn is present —
  *"She's going to measure every reed in this bog and go home with a headache."*
  No malice. She just knows how this ends.

- `lore_deep_mire`: If pressed about the deep sections —
  *"Nothing worth finding out there."* If pressed a second time, she changes the subject.
  She does not explain further.

- `returning_player`: Small acknowledgment if player has been here before.
  She remembers faces that come back through. Most don't. She respects it without saying so.

- `player_has_murkback`: *"Caught one of those, did you. Give it time."*

### Shop

Items: `mire_balm`, `trail_morsels`, `tether_orb`

Night variant: `mire_balm` is out of stock.
No explanation — just *"Fresh out."* She'll have more tomorrow.
Scarcity is part of her character. She trades what she has, not what she wishes she had.

---

## NPC: Ferryn

### Who She Is

A young naturalist studying why the mire is expanding. She's cataloguing bog creatures,
mapping terrain, trying to understand if the growth is natural or something else.
Optimistic in a way that reads as slightly naive next to Sable.

She arrived recently. She has a methodical system for everything and the confidence of someone
who has not yet been wrong enough times to doubt her methods.

### What She Wants

To understand the mire's expansion — document it, explain it, and potentially make a case
for the crossroads being cleared and the road restored. She hasn't told Sable this directly.

Her instruments read wrong near certain sections of the mire. The expansion seems to radiate
from the Old Crossroads area. She wants to go document it up close.
Sable has told her flatly not to. Ferryn has noted this in her journal as a "local superstition."

### Seasonal Presence

Ferryn is not permanent. She's here for a season.

If the player returns at higher rank, she's gone. The Reed Hollow is empty except for her
field notes, left behind on the post. The notes contain her findings — including observations
about the expansion that she never fully understood, and a final entry that reads like
she got closer to the crossroads than she told Sable she would.

Her fate is deliberately ambiguous. She probably left. Probably.

### Her Pet — Silt (Pallefin)

Ferryn found it in the silt on her first day at the Mirefields. It has been in her coat pocket
since. She named it immediately and will tell the player this story unprompted.

She has documented everything about Silt — its diet, sleep patterns, barometric sensitivity.
She has noticed it behaves differently near the expanding sections of the mire:
refuses to enter certain water, agitated near the crossroads area. She's noted this in her
journals but hasn't drawn a conclusion yet.

Nickname: *Silt*. No hesitation, no backstory needed. It was in the silt. That's the name.

### Dialogue Variants

- `default`: Warm, curious, immediately tells the player about her research.
  Asks if they've noticed anything unusual in the explore zone.

- `about_sable`: Respects her, slightly frustrated by her.
  *"She knows this place better than anyone. She just doesn't seem curious about why it is
  the way it is."*

- `lore_expansion`: Explains her theory. The mire is growing faster than natural bog expansion
  rates. Something is accelerating it. She doesn't know what yet.

- `lore_crossroads`: She wants to document the Old Crossroads area. Her instruments point there.
  She hasn't gone. *"Sable says not to. I'm... taking that under advisement."*

- `quest_active`: Asks the player to retrieve her brass gauge from the mire edge.
  She dropped it near the crossroads boundary. She won't go get it herself. Not right now.

- `quest_complete`: Grateful, analyzes the gauge readings immediately.
  Tells the player the readings near that area are unlike anything else in the mire.
  Files it in her notes. Moves on.

### Quest: Ferryn's Fetch (name TBD — clean in implementation)

- Giver: Ferryn at the Reed Hollow
- Step 1: Retrieve `ferryn_equipment` (Ferryn's Brass Gauge) from The Mire Path
  (explore event fires only when quest is active — near the crossroads boundary)
- Step 2: Return to Ferryn
- Reward: XP + small item reward (TBD) + Ferryn's expansion lore dialogue unlocks fully
- Note: The retrieval point is near the Mirewarden's territory — tense, not dangerous.
  Players aren't fighting a Mirewarden here. Just close enough to feel it.

---

## The Old Crossroads

No NPC. Pure environmental storytelling.

The stone foundations of the old waystation are still visible — half-submerged, overgrown.
The signpost still stands. Three arrows, all pointing different directions. No legible names.
The collapsed structure has been reclaimed entirely by reeds and dark growth.

### Mirewarden Territory

The crossroads was not just abandoned because the mire expanded.
A Mirewarden claimed the ruins as its territory and people stopped coming.
The stone foundations are its den. The mire built up around the ruins over decades — and so
did the Mirewarden. It is unclear whether the creature shaped the ruins or the ruins shaped
the creature.

Sable knows. She respects that territory the way she respects all of the mire — practically.
It isn't hers. She doesn't go there.

Ferryn's instruments read the mire expansion as radiating from this area.
She wants to document it. Sable says no. This is the tension.

### What the Player Finds

- Overgrown stone foundations, half in water
- The signpost with illegible arrows
- Territorial markings — disturbed silt, drag marks, unnatural stillness
- Clear sense that something large was recently here

### Choice Event (interacting with the ruins)

*"The foundations of the old waystation are still here beneath the reeds. You can see the
outline of what it once was — storage alcoves, a firepit base, the corner of what might have
been a counter. Something has been dragging through here. Recently. There's an old ledger
wedged in a stone alcove, still dry. You could reach for it."*

- **"Take the ledger"**: You retrieve `waystation_ledger`. Minor HP drain from the tension
  of moving deeper into the space. The air feels watched.
- **"Step back"**: Nothing. You leave. Smart.

Note: Taking the ledger does not trigger a Mirewarden fight. It triggers unease.
The Mirewarden is present in the lore, not as a combat encounter at this location.
That encounter is reserved for a future arc if the Mirefields is expanded.

---

## Explore Events — The Mire Path

Target: ~10 events. Zone key: `mirefields` (set in `data/remnants.py`).
Tone: physical, oppressive, disorienting. The danger is the terrain.

### Flavor Events

```
- The path disappears under two inches of brown water. You can't tell if it continues
  forward or if you've already stepped off it.

- A territorial bog creature bursts from the reeds, takes one look at you and your pet,
  and retreats. You're bigger than its usual targets. Barely.

- The ruins of a signpost poke out of the muck — three arrows pointing different directions.
  None of the place names are legible. Someone has tried to scratch new ones in.
  You can't read those either.

- Sable's trail markers — knotted reed bundles tied to stakes — are the only reliable guide
  here. You spot one and orient yourself. Without these, you'd be walking in circles.
```

### Pet Sighting Events

```
- A Murkback watches you from a half-submerged log, perfectly still. It's not interested
  in fighting. It's waiting for you to leave its territory.

- Something moves under the surface in the deeper section of the mire. Not small.
  It tracks alongside you for about a minute, then veers off without surfacing.
```

### Hazard Events

```
- You sink into a soft patch up to your knee. Extracting yourself takes time and costs you.
  outcome: { energy: -1 }

- A bog creature you didn't see charges from the shallow water. Glancing hit — it was more
  startled than aggressive, but that doesn't help your ribs much.
  outcome: { hp: -10 }
```

### Loot Bonus Event

```
- You spot a waterlogged pack half-buried in the reed bed — old, probably from the waystation
  days. Still has something inside worth keeping.
  outcome: { item: trail_morsels or tether_orb, qty: 1 }
```

### Choice Events

```
1. A section of the old crossroads road is visible just beneath the water —
   stone paving, still intact. You could follow it deeper into the mire, or
   stick to Sable's markers.

   - "Follow the old road": chance of loot bonus (bog_reed_bundle or mire_balm) OR
     energy drain if the path becomes impassable
   - "Stick to the markers": safe, nothing happens

2. Ferryn's brass gauge — half-sunk in the mud near the crossroads boundary.
   ONLY fires when quest is active.

   - "Pull it out": minor HP drain from effort. Quest item retrieved.
     outcome: { quest_item: ferryn_equipment, hp: -5 }
   - "Leave it": nothing. Quest remains active.
```

---

## Pets

### New Species

**Murkback → Murkwall**
- Type: Water / Ground
- Rarity: Common → Uncommon
- Personality: Defensive
- Murkback: Squat, wide-bodied amphibian. Flat, toad-like, armored with mud and silt.
  Slow on land, fast in shallow water. Territorial. Doesn't attack unless you're in its space.
- Murkwall: Second evolution. Larger, hide thickened into layered mud-rock plating.
  Immovable-feeling. The apex non-Gloom creature of the mire. Everything else gives it room.
  Sable's Ledge is a Murkwall — recognizable by the healed scar on its left flank.
- Passive ability (Murkback): *Bog Anchor* — resistant to speed debuffs, reduced knockback
- Evolution level: ~15
- Encounter: Day and night. Common.

**Pallefin → Shimmerdeep**
- Type: Water
- Rarity: Uncommon → Rare
- Personality: Timid
- Pallefin: Small, almost translucent. Skims the water surface, barely disturbs it.
  Disappears into mist. Sensitive to pressure, temperature, environmental changes —
  reacts before any instrument does. Ferryn's Silt is one of these.
- Shimmerdeep: Stops skimming the surface, descends. Translucency becomes luminescence —
  generates faint light in dark water. Less ghost-like, more defined. Still environmentally
  sensitive but now draws attention to changes rather than fleeing from them.
- Passive ability: *Mist Veil* — small evasion chance in fog / night conditions
- Evolution level: ~16
- Encounter: Day only (Pallefin dives when dark). Uncommon.

**Siltborn → Mirewarden**
- Type: Poison / Grass
- Rarity: Rare → Very Rare
- Personality: Aggressive
- Siltborn: Roughly creature-shaped mass of compressed reeds, root tangles, dark silt.
  Low to the ground, slow, almost indistinguishable from the bog floor until it moves.
  Not Gloom-touched — the mire's wrongness is ancient and organic, not Gloom corruption.
  Ancient-feeling even as a young specimen. Night only.
- Mirewarden: Larger, denser. Reeds and roots have grown through it, not just coating it.
  Moves slower but hits like the terrain itself shifted. No longer looks like a creature
  blending in — looks like a landmark that happens to move.
  The Old Crossroads Mirewarden is implied to be beyond even this stage — lore only,
  not a combat encounter yet.
- Passive ability: *Reclaim* — small HP regeneration at end of each turn. The bog sustains it.
- Evolution level: ~18
- Encounter: Night only. Rare. Pushes deep into the zone.
- IMPORTANT: Not Gloom-touched. The `is_gloom_touched` flag should NOT be set.

### Encounter Table

| Time | Pets |
|---|---|
| Day | Murkback, Pallefin, Mossling, Corroder |
| Night | Murkback, Gloom Weaver, Siltborn, Corroder |

Note: Mossling and Corroder are borrowed from other zones — same species, different habitat
population. Corroder at gloom_level 8 fits — low Gloom presence, creature exists here too.

---

## Items

| Item ID | Name | Type | Source | Notes |
|---|---|---|---|---|
| `mire_balm` | Mire Balm | Consumable / Healing | Sable's shop, explore loot | Bog herb compress. Heals slightly less than Moss Balm but Sable always stocks it. |
| `bog_reed_bundle` | Bog Reed Bundle | Crafting material | Explore loot | Dense dried reeds. Future crafting use — keep flexible. |
| `murk_fragment` | Murk Fragment | Crafting material | Murkback / Murkwall drop | Mud-rock plating that flakes off naturally. Dense. Future use. |
| `pallefin_scale` | Pallefin Scale | Crafting material | Pallefin / Shimmerdeep drop | Translucent, faintly luminescent. Rare drop. Future use. |
| `waystation_ledger` | Waystation Ledger | Lore item | Old Crossroads choice event | Trader records from when the crossroads was active. Lore text only. Last entry cuts off mid-sentence. |
| `ferryn_equipment` | Ferryn's Brass Gauge | Quest item | Explore event (quest only) | Only appears during Ferryn's fetch quest. No other use. |

---

## NPC Pets — Design Rule (applies everywhere going forward)

Established here at the Mirefields. Apply to all future NPCs.

**The rule:** Field NPCs — those who live in or regularly work in dangerous territory
(remnants, wilds, guild outposts) — should default to having a pet. They live out here.
It makes no sense they don't.

Town NPCs: case by case. Shopkeepers maybe not. Guild Masters, wardens, hunters: yes.

**The pet should reflect who they are.** Not just the zone — the person.
History, personality, what they've been through. The pet is character writing.

**Nickname reflects personality:**
- Sable: has one, won't say it publicly. Let it slip at high rank only. Private, dry, fond.
- Ferryn: named it immediately, tells everyone, documented in her notes. Openly affectionate.
- Future NPCs should follow this logic — the nickname (or absence of one) says something.

**Some pets aren't immediately visible.** The player discovers them through dialogue depth,
returning at higher rank, or asking the right question. Not every NPC leads with their pet.

**Sable's specific note:** If the player has a Murkback, Sable notices and comments.
*"Caught one of those, did you. Give it time."* — one line, no elaboration.
This is the model for NPC pet reactions going forward: brief, in-character, not over-explained.

---

## Lore Thread — The Deep Mire (future arc)

Not for immediate implementation. Documented here for continuity.

The Mirewarden at the Old Crossroads is the gateway to the deep mire.
Sable doesn't go past it. Ferryn's research points toward it.
Ferryn's field notes (left behind if the player returns after she's gone) contain observations
about the expansion that she never fully explained — and a final entry suggesting she went
closer to the crossroads than she told Sable she would.

Her fate is ambiguous. She probably left. Probably.

If this thread is ever expanded: the deep mire's Siltborn/Mirewarden connection,
the mire expansion's unnatural cause, and what Sable actually knows but won't say
are all seeds planted and ready.

---

## Implementation Notes for Coding Session

1. `explore_events.py` — add `mirefields` key with events above
2. `data/remnants.py` — Sable exists. Add Ferryn to `npcs` dict with seasonal flag logic.
   Add Ledge (Murkwall) to Sable's NPC entry. Add Silt (Pallefin) to Ferryn's NPC entry.
3. `data/pets.py` — add Murkback→Murkwall, Pallefin→Shimmerdeep, Siltborn→Mirewarden
4. `data/pets.py` ENCOUNTER_TABLES — add `mirefields` day/night table
5. `data/quests.py` — add Ferryn's fetch quest (name TBD)
6. `data/items.py` — add mire_balm, bog_reed_bundle, murk_fragment, pallefin_scale,
   waystation_ledger, ferryn_equipment
7. Old Crossroads choice event — needs an interact trigger in the locations dropdown,
   not part of the standard explore zone. Separate interaction flow.
8. Sable shop night variant — `mire_balm` out of stock at night. Needs time-of-day
   check in shop rendering.
9. Siltborn — do NOT set `is_gloom_touched: True`. It is not a Gloom creature.
10. Ferryn seasonal logic — needs a flag or rank check to determine presence/absence.
    When absent: Reed Hollow slot still visible in dropdown, shows her notes instead of NPC.
