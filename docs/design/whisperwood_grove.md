# Whisperwood Grove — Design Document
# Status: LOCKED (brainstorm session, no code changes yet) — except where marked OPEN/TBD
# For: coding session implementation reference

---

## Overview

Whisperwood Grove is **Town 2** — the first full town in Aethelgard. Home of the Verdant Crest
and Elder Vexia. First town with: 6 NPCs, two explore zones (Whispering Thicket + Whisperwood
Wilds), a main quest (`whisperwoods_plea`), and (per this doc) two attached remnants.

**Current code state** (`data/towns.py`, lines ~214-401):
- 5 locations exist: Leaf-Lit Lodge (Arboreal), Verdant Spire (Vexia + Linden),
  Root & Branch Emporium (Slithers), Moonpetal Inn (Mira), Whispering Thicket (Fae Whisper).
- Connections: Mirefields (back), Whisperwood Wilds (Explore Wilds button).
- `whisperwoodGrove` zone (Whispering Thicket) has `gloom_level: 15` set, but **no explore
  events written**. `whisperwoodWilds` has **no encounter table at all**.
- Pets in code: Mossling, Sunpetal Moth (no evolution), Gloom Weaver, Duskspinner,
  Moonpetal Sprite, Lunarblossom, Thornmoss, Ferngale.
- Quest: only `forest_cleanup` exists. `whisperwoods_plea` is referenced in Vexia's dialogue
  (`quest_whisperwoods_plea_active`, `quest_whisperwoods_plea_complete`, `crest_earned`)
  but the quest itself is **not yet written**.

**What this doc adds:**
1. Renames: Sunpetal Moth → **Sunmoth**, Moonpetal Sprite → **Moonwisp**,
   Gloom Weaver → **Grimweave**, Dreadspinner → **Duskspinner** (already partially renamed in code —
   confirm during implementation).
2. New pet lines: Sunmoth → Gilmoth → Solmoth, Serpentine → Serpumbra, Glamorose → Malicea →
   Aberraflora, Verdanthorn (standalone Ancient).
3. New NPC: **Luna** (Mira's twin, Moonpetal Inn night shift).
4. Full NPC pet roster + nicknames for all 6 existing/new town NPCs.
5. Explore events for `whisperwoodGrove` (Whispering Thicket) and `whisperwoodWilds`.
6. Lore lock: **the Whispering Thicket IS Sylven Heartwood's resting form** — the ancient
   Treant Legendary, source of Arboreal's healing, and the thing the Heart of Decay quest
   ultimately concerns.
7. Rough sketches of the two attached remnants — **The Ashen Verge** (free) and
   **The Blind Well** (quest-gated). Marked OPEN where decisions are still pending.

**Still open / not yet designed (flagged inline below):**
- `whisperwoods_plea` quest structure — what the "Heart of Decay" actually is mechanically,
  and the full step-by-step (only the start/end dialogue beats exist in code today).
- Side story beat (Luna/Mira, Fae Whisper, Arboreal/Sylven thread).
- Ashen Verge: Cinderkit→Ashveil wild-catchable vs NPC-only; Kaelen's bounty target species.
- Blind Well: full dialogue trees for Anora / Scribe / Elowen.
- Verdanthorn's Reflection: lore-seeded only, mechanically deferred (Veilmother/Chasmbane pattern).

---

## Locations Dropdown (current, unchanged)

| # | Label | Who / Service | Availability |
|---|---|---|---|
| 1 | The Leaf-Lit Lodge | Arboreal — free pet HP restore | All |
| 2 | The Verdant Spire Guild Hall | Elder Vexia + Linden | Day |
| 3 | The Root & Branch Emporium | Slithers — shop | Day |
| 4 | The Moonpetal Inn | Mira (day) / **Luna (night, NEW)** — paid full rest | All |
| 5 | The Whispering Thicket | Fae Whisper — explore zone (`whisperwoodGrove`, gloom_level 15) | All |

Plus **Explore Wilds** button → Whisperwood Wilds (`whisperwoodWilds` zone).

---

## Lore Lock — Sylven Heartwood & the Whispering Thicket

**Sylven Heartwood** (🌿) — Legendary, no evolutions. A colossal, ancient Treant that embodies
the spirit of the forest.

**The Whispering Thicket IS Sylven's resting form.** The ancient growth, the unnatural density
of the canopy, the "something is wrong underneath" feeling — all of it is Sylven. The corruption
growing in the Thicket is growing *inside* Sylven. This is the Heart of Decay.

This recontextualizes everything else in the Thicket:
- **Verdanthorn** lives in the Thicket because Sylven's presence protects ancient creatures.
- **Arboreal's** healing ability draws from Sylven's roots — this is why the Lodge works.
- **Fae Whisper** lives in the Thicket, knows Sylven, and has been watching the corruption.
  She's been to the Blind Well before — alone.
- The corruption arc (`whisperwoods_plea` / Heart of Decay) isn't "clear a forest problem" —
  it's "something ancient and protective is dying/corrupting from the inside, and the player
  has to deal with that."

Gameplay note: Sylven is **never an encounter inside the Thicket**. After `whisperwoods_plea`,
Sylven remains a passive presence (see Pet Sighting events below — "something large moves
through the undergrowth... it is part of the ground").

---

## NPC: Arboreal (existing — Leaf-Lit Lodge)

No changes to dialogue. Per the NPC Pets design rule (see below), Arboreal does not get an
assigned companion pet — his connection is directly to Sylven, not to a personal pet. This is
intentional and should be called out if revisited later (he's the one NPC whose "pet" is
arguably the entire forest).

---

## NPC: Elder Vexia (existing — Verdant Spire)

No dialogue changes beyond what's already in code. Confirmed pet assignment below.

### Her Pet — Ferngale, "Fen"

She's had this Ferngale since it was a Mossling — a long relationship, and the Crest battle
companion referenced in `quest_whisperwoods_plea_complete`. She has a nickname but doesn't
volunteer it; if a player asks directly about her companion, she answers as Guild Master.
If they ask its *name* specifically, she pauses first — "Fen. I've called it that since it
was young." That's all she gives. Old, quiet, never used in official contexts.

---

## NPC: Linden (existing — Verdant Spire)

No dialogue changes beyond what's in code.

### His Pet — Mossling, "Frond"

A Mossling wandered into the Verdant Spire once. Linden documented it. There is a filed
report with an entry number. He named it Frond — botanically accurate, technically correct,
and it ended up in the documentation verbatim: *"Subject designated 'Frond' continues to
occupy the lower-left corner of the desk. No further action taken."* Said with complete
sincerity — bureaucratic naming that accidentally became affectionate.

---

## NPC: Slithers (existing — Root & Branch Emporium)

No dialogue changes beyond what's in code.

### His Pet — Moonwisp, "Glim"

Flits between the shop displays. Slithers thinks it helps attract customers — the way it
drifts and draws the eye. "Glim knows the good merchandise. Always hovers near the best
stock." Completely unverified. Slithers has never questioned it. Short for "glimmer."

---

## NPC: Mira (existing — Moonpetal Inn, day shift)

No changes to existing dialogue (`default`, `night`, `after_rest`). Confirmed pet assignment
below; Luna (new) takes the night shift — see next section.

### Who She Is (refined)

Mira is the day half of the inn — bright, bubbly, the innkeeper who lights up the room. She
talks about moonpetals and Lumina-moths as something beautiful (matches her existing `night`
dialogue line, which she delivers describing the night from behind the counter — she doesn't
*experience* it the way Luna does).

### Her Pet — Sunmoth, "Petal"

Sunmoth is literally a creature drawn to light — fits Mira's energy completely. The nickname
"Petal" is a holdover: the species used to be called "Sunpetal Moth," she called it Petal,
the species got renamed to Sunmoth, and she never noticed. Uses the nickname constantly,
without thinking — *"Petal, not on the linens."*

---

## NPC: Luna — NEW (Moonpetal Inn, evening/night shift)

### Concept

Mira's twin sister. Mira runs the inn during the day; Luna takes over for evening and night.
Players who only visit during the day never meet Luna. Players who stay the night get a
completely different person behind the counter.

### Who She Is

Luna didn't choose nights because of a schedule — she's a night person the way some people
just are. The forest after dark feels more honest to her than the managed pleasantness of
the daytime Grove. She's been watching the Thicket from the inn window long enough to notice
when things changed: she notices the Glamorose appearing more frequently, and she feels the
weight of the forest differently now.

She doesn't tell guests any of this. People come to the inn to rest, not to worry.
*"Mira's warmth handles the day. Luna handles the quiet, and everything the quiet carries."*

### Relationship with Mira

They don't compete — they complement. Mira's brightness keeps Luna from sinking too deep into
what she's observed. Luna's steadiness keeps Mira from being naive about what the forest is
becoming. Neither of them talks about this directly. The inn just works.

### Relationship with Fae Whisper

They've crossed paths during the hours when the inn is empty — Luna is awake when Fae Whisper
is most active. Luna doesn't repeat what Fae Whisper has told her, but a player paying
attention to both characters will notice the threads connect. (Side story material.)

### Her Pet — Lunarblossom (no nickname)

Lunarblossom is the fully evolved form of Moonwisp — drifts through the inn at night, leaving
faint glowing petals. Guests assume it's decoration. It isn't. Lunarblossom is a night creature
and logically belongs with Luna (the one who's been awake when the forest is at its worst),
not Mira — the inn's creature "grew up" alongside Luna more than Mira.

She doesn't name what she doesn't need to name. *"They exist in the same space."* If asked
why it has no name: *"It knows what it is."*

### Voice / Dialogue Variants

Measured. Says less than she knows. Not cold — careful.

```
- default: "You're up late. Most guests don't make it past the second hour."
- thicket_visited: "You've been in the Thicket. I can tell. How far did you go?"
  (fires if player has explored the Thicket)
- returning_high_rank: She opens up slightly — tells the player the forest feels
  different "at the roots" than it did a season ago. Doesn't explain what that means.
- night_observation: "The Thicket's been louder this week. Not loud like creatures —
  loud like something breathing differently."
```

### Implementation note

Luna should appear as an `npcs` entry on `moonpetal_inn` with `availability: "night"`
(Mira stays `availability: "all"` per existing code, OR Mira becomes `"day"` and Luna
`"night"` — pick whichever matches how `availability` is checked elsewhere; the goal is
day visitors see Mira, night visitors see Luna, not both).

---

## NPC: Fae Whisper (existing — Whispering Thicket)

No dialogue changes beyond what's in code (`default` line about following the lights).
Per the NPC Pets design rule, Fae Whisper does **not** get an assigned companion pet — she's
a pixie sprite, arguably a creature herself. Her role is lore/atmosphere + (per the lore lock
above) she's tied directly to Sylven and the Blind Well. Side story material.

---

## NPC Pet Roster — Summary Table

| NPC | Pet | Nickname | Notes |
|---|---|---|---|
| Elder Vexia | Ferngale | "Fen" | Crest battle companion. Nickname not used officially. |
| Linden | Mossling | "Frond" | Documented. Has a case number. |
| Slithers | Moonwisp | "Glim" | Flits between shop displays. |
| Mira | Sunmoth | "Petal" | Day, warm, bright. Holdover name from "Sunpetal Moth." |
| Luna | Lunarblossom | *(none)* | Night, knowledgeable, leaves glowing petals. |
| Arboreal | *(none)* | — | Connection is to Sylven directly, not a personal pet. |
| Fae Whisper | *(none)* | — | Pixie sprite — arguably a creature herself. |

---

## Pets — New Species & Lines

### Renames (apply in `data/pets.py`)

- Sunpetal Moth → **Sunmoth**
- Moonpetal Sprite → **Moonwisp**
- Gloom Weaver → **Grimweave**
- Dreadspinner → **Duskspinner**

### Sunmoth → Gilmoth → Solmoth (NEW evolution line)

- Type: Bug → Bug → Bug/Fire
- Rarity: Common → Uncommon → Rare
- Sunmoth: small, sunflower-patterned wings, drifts, day only (existing species, now gets a line).
- Gilmoth: larger, wings thicker and deeper in color, gilt/golden, starts producing faint warmth.
- Solmoth: fully radiant — wings cast light like a lantern, doesn't drift anymore, moves
  with purpose.
- Evolution level: TBD (coding session)

### Serpentine → Serpumbra (NEW — "vine predator," Whisperwood Wilds)

- Type: Grass/Dark
- Rarity: Uncommon → Rare
- Serpentine: coils through the root network like a living vine, strikes from below or
  from above. Indistinguishable from a vine until it turns one eye toward you.
- Serpumbra: grows larger, more vine than snake — harder to distinguish, more dangerous.
- Active in Wilds day **and** night (a forest predator hunts whenever).
- Evolution level: TBD (coding session)

### Glamorose → Malicea → Aberraflora (NEW — "Thicket night" creature)

- Type: Grass/Poison
- Rarity: Common → Uncommon → Ancient
- Naming locked: botanical-genus names that read like a nature guide entry — "looks like it
  belongs in a nature guide. That's worse than looking obviously dangerous."
- Glamorose (Stage 1, Common): soft, floating, delicate petal — deceptive. The toxic-beautiful
  corruption aesthetic starts here.
- Malicea (Stage 2, Uncommon): fully open, radiates quiet malice while sounding like
  something you'd plant in a garden.
- Aberraflora (Stage 3, Ancient): ancient and overwhelming — fills the space around it.
- Night only, Whispering Thicket. Naming note: any earlier "Glamourise"/"Hollow-" prefix
  references should be corrected to **Glamorose** wherever they appear (carries forward into
  Elowen's material at the Blind Well).

### Verdanthorn (NEW — standalone Ancient, "Thicket day")

- Type: Grass/Normal
- Rarity: Ancient (standalone, no evolution line — like Briarfawn → Verdanthorn naming
  considered and folded into a single standalone entity)
- Lives under Sylven's protection — has been here a long time. Day encounter, rare weight.
- Behavior: stands motionless between massive trees, watching. When you move, it doesn't.
  When you stop, it already isn't there.
- Aligned with the "good guy" side of the forest — protected by/aligned with Sylven.

### Sylven Heartwood (existing concept, confirmed)

- 🌿 Legendary, no evolutions. The Whispering Thicket itself (see Lore Lock above).
  Never a combat encounter inside the Thicket.

---

## Encounter Tables

### Whispering Thicket (`whisperwoodGrove`, gloom_level 15)

| Time | Pets |
|---|---|
| Day | Mossling, Sunmoth, Verdanthorn |
| Night | Mossling, Grimweave, Moonwisp, Glamorose (line) |

### Whisperwood Wilds (`whisperwoodWilds`)

| Time | Pets |
|---|---|
| Day | Mossling, Serpentine |
| Night | Mossling, Serpentine, Grimweave |

Note: the Wilds night already feels different from day because Grimweave joins. Serpentine
being active both times makes sense for a forest predator — it hunts whenever. No separate
Wilds-only night creature needed; this keeps the new species count to 3 total
(Sunmoth line is an addition to an existing species, not a new base species).

**Rarity tier check (full Whisperwood roster):**

| Tier | Species |
|---|---|
| Common | Mossling, Sunmoth, Glamorose |
| Uncommon | Thornmoss, Gilmoth, Grimweave, Moonwisp, Serpentine, Malicea |
| Rare | Ferngale, Solmoth, Duskspinner, Lunarblossom, Serpumbra |
| Ancient | Verdanthorn, Aberraflora |
| Legendary | Sylven Heartwood |

---

## Explore Events — Whispering Thicket

Zone key: `whisperwoodGrove`, gloom_level 15. Tone: ancient, beautiful, something is wrong
underneath.

### Flavor

```
- The canopy is so dense that noon looks like dusk. The light that filters through
  is green and old.

- Something has woven vines across the path overnight — not blocking it, just
  crossing it. Like a boundary marker that wasn't there yesterday.

- The bark of the nearest tree has a shallow indent — like a handprint. Too large
  to be human.

- A cluster of Glamorose drifts past at eye level. You hold your breath. It
  continues without slowing.
```

### Pet Sighting Events

```
- Verdanthorn stands motionless between two massive oaks, watching. When you move,
  it doesn't. When you stop, it already isn't there.

- Something large moves through the undergrowth — slow, deliberate. The ground
  doesn't crack under it. It is part of the ground. (Sylven passive seed)
```

### Hazard Events

```
- Hollow petals across the path. You don't see them until you've walked through.
  Your pet pulls back from the residue.
  outcome: { hp: -6 }

- A branch shifts above you — no wind. Something heavy was resting there.
  outcome: { energy: -1 }
```

### Loot Bonus Event

```
- A Guild researcher's cache, half-buried in moss. Old but sealed.
  outcome: { item: capture_orb or moss_balm, qty: 1 }
```

### Choice Events

```
1. The oldest tree in the Thicket has something carved into the bark. Not words.
   A map, or a warning. You could take a rubbing.

   - "Take a rubbing": item: lore_fragment — something shifts in the canopy above you
   - "Leave it": nothing

2. (Night only) Glamorose has surrounded a frozen Mossling in the middle of the bloom.
   You could pull it free.

   - "Pull it free": outcome: { hp: -5 }, Mossling escapes, outcome: { energy: +1 }
   - "Walk past": nothing. You feel it for a while after.
```

---

## Explore Events — Whisperwood Wilds

Zone key: `whisperwoodWilds`. Tone: untamed, primordial, not corrupted — just old and
unmanaged.

### Flavor

```
- The path here isn't a path. It's a gap that was cleared once and hasn't been
  cleared since. The forest is taking it back.

- A split oak struck by lightning has grown back around the scar. Something lives
  in the hollow where the wood rejoined.

- Tracks in the mud — three toes, deep. Something heavy passed here recently.

- The further you go, the quieter it gets. Not peaceful quiet. Waiting quiet.
```

### Pet Sighting Events

```
- A Serpentine hangs perfectly still from an overhead branch, indistinguishable
  from a vine until it turns one eye toward you.

- Two Mosslings chase each other through the undergrowth at the edge of your
  vision, then vanish into the moss without sound.
```

### Hazard Events

```
- You step on what looks like solid ground. A root hollow collapses beneath you.
  outcome: { energy: -1 }

- Something drops from the canopy — not a branch. You can't tell what it was.
  outcome: { hp: -5 }
```

### Loot Bonus Event

```
- A traveller's pack wedged in a root hollow. Whoever left it isn't coming back.
  outcome: { item: trail_morsels or tether_orb, qty: 1 }
```

### Choice Events

```
1. A Serpentine is coiled around the base of a tree, pinning a sealed tin beneath
   it. The Serpentine isn't moving.

   - "Try to retrieve it": risk outcome: { hp: -8 }, chance of getting an item
   - "Leave it": the Serpentine doesn't even look at you as you pass

2. A perfectly circular clearing — no trees within it, old ash marks on the ground.
   Something has happened here before.

   - "Examine the marks": item: lore_fragment, unsettling
   - "Keep moving": you look at it for a long time before you do
```

**IMPORTANT continuity note:** Choice Event #2 above (the ash circle clearing) **is or leads
to The Ashen Verge** — see Remnants section below. This is intentional connective tissue,
not a duplicate.

~10 events per zone — tone confirmed, fine-tuning deferred to coding session.

---

## Items (new, referenced above)

| Item ID | Name | Type | Source | Notes |
|---|---|---|---|---|
| `lore_fragment` | Lore Fragment | Lore item | Thicket + Wilds choice events | Generic lore-text item, multiple flavor variants possible. |

(`capture_orb`, `moss_balm`, `trail_morsels`, `tether_orb` already exist in items/Mirefields doc.)

---

## NPC Pets — Design Rule (carried forward from Mirefields)

Applies here too:

- Field NPCs default to having a pet reflecting their personality/history. Town NPCs are
  case-by-case — Whisperwood's town NPCs (Vexia, Linden, Slithers, Mira, Luna) **all** got
  pets because each pairing does real character work (see table above).
- Arboreal and Fae Whisper are the exceptions — both have a more direct lore connection
  (Sylven) that supersedes a personal-pet assignment.
- Nickname (or absence of one) is character writing: Vexia hides hers, Linden's is
  accidental bureaucracy, Slithers' is unverified shopkeeper lore, Mira's is a holdover
  she never noticed, Luna deliberately has none.

---

## whisperwoods_plea — Quest Structure (OPEN / TBD)

**What exists in code today** (Vexia dialogue only):
- `quest_whisperwoods_plea_active`: "The Thicket grows darker by the day. Find the source
  of the corruption — the Heart of Decay. The forest is counting on you."
- `quest_whisperwoods_plea_complete`: "You've shown kindness and understanding. Now, let us
  see the strength of your bond. Face my companion — and prove yourself worthy."
- `crest_earned`: "The Verdant Crest rests with a worthy guardian."

**Implied shape:** find the Heart of Decay → return to Vexia → crest battle vs. Ferngale →
earn the Verdant Crest.

**Locked context (from Lore Lock above):** the Heart of Decay is Sylven Heartwood itself —
the Whispering Thicket is Sylven's resting form, and the corruption is growing inside Sylven.

**Still undecided:**
- How the player actually "finds" the Heart of Decay mechanically (explore trigger? item?
  NPC dialogue chain?).
- What "kindness and understanding" means mechanically before the crest battle.
- Whether/how the Blind Well (see below) ties into this quest as the location where the
  Heart of Decay's source is actually confronted.

---

## Side Story Beat (OPEN / TBD)

Identified threads, not yet written into a structured beat:
- The Luna/Mira dynamic (day/night halves of the same inn, complementary knowledge).
- Fae Whisper's role — she's been to the Blind Well before, alone, and has crossed paths
  with Luna at night. Neither repeats what the other said, but attentive players connect them.
- Arboreal and Sylven — Arboreal's healing draws from Sylven's roots; does he know what's
  happening to Sylven?

---

# Remnants — Rough Sketches (NOT LOCKED — separate design pass)

Both remnants are attached to Whisperwood Grove only (not through-stops). Style direction
locked: **Style A — The Ashen & Deep-Root Path** ("upstairs vs downstairs": beautiful canopy
town above, rotting roots below — the inversion of Whisperwood's existing verticality).

## The Ashen Verge (free remnant)

**Status:** Free remnant — accessible from first arrival at Whisperwood Grove, like an
explore zone (no quest gate). Treat as primarily a **side-story location** for now: no main
quest dependency. This can be revisited later as a soft "quest lock" if the main arc ever
needs a reason to point players here, but for v1 it's open.

**Visuals:** A sharp, unnatural boundary line where green grass stops and a perfect circle of
cold, gray, perpetual ritual ash begins. Dead silent. Air smells faintly of smoldering embers.

**Continuity:** This IS (or directly leads from) the Wilds Choice Event #2 — "a perfectly
circular clearing... old ash marks on the ground. Something has happened here before."
Free continuity, no extra invention needed.

### Lore Spine (locked)

Whisperwood's corruption (Glamorose→Malicea→Aberraflora, the Heart of Decay, Serpentine as
"indistinguishable from a vine") is fundamentally about things that **mimic and blend into
living growth**. Fire is the one thing in a forest that *can't* disguise itself as something
else.

Generations ago, something came up out of the ground at this spot — the first surface
appearance of what would become the Heart of Decay. The people here didn't (and still don't)
fully understand it, but they had **Pyrehart** — a powerful, ancient Fire creature — who
fought it back. The fight was costly: Pyrehart was badly wounded and has been dormant near
The First Ring ever since. What was left behind — a severed fragment of the corruption that
fire couldn't fully erase — became **Cindermaw**, also dormant, also at The First Ring.

Afterward, Kaelen's ancestors lit a containment ring of fire around the site — not as the
real defense (Pyrehart was), but as ongoing maintenance/ritual to keep the boundary "clean"
in case anything tried to regrow. *"My grandmother's grandmother lit the first ring. Said
fire was the only thing the roots couldn't pretend to be."*

Generations later: the ritual continues, but its original purpose has been mostly forgotten.
Kaelen tends it out of inherited duty. Bram & Pip have noticed the boundary slowly
shrinking — without Pyrehart at full strength, the containment is quietly weakening. This
line is meant to pay off later in the Blind Well — the player goes from "huh, ash circle" up
top to "oh, THAT'S why" down below.

### NPC 1 — Kaelen, the Hearth-Steward (anchor NPC)

Soot-stained hermit living in a deadwood shack at the edge of the ash circle. Tends the
boundary because something taught the people here that fire keeps the rot from spreading
past it. He doesn't fully understand *why* it works — just that it does, and that the circle
needs to stay clean.

- Mechanics: lore-keeper of the ash circle; hands out a repeatable culling bounty
  (target species: **Serpentine** — vines/roots encroaching on the boundary).
- Pet: **"Soot"** — a Cinderkit he raised from a kit near the fire ring. Cinderkit→Ashveil
  is also wild-catchable in the Ashen Verge encounter table — Soot is one Kaelen raised
  personally, same species as the wild population (Sable/Murkback pattern).
- Dialogue drafted: `default`, `lore_circle`, `lore_pressed`, `bounty_complete`,
  `player_has_cinderkit`.
- `bounty_active`: *"Serpentine's been working its way toward the line again. Vines
  don't respect boundaries — never have. Clear a few out, would you? Keeps the ash
  where it belongs."*

### NPC 2 — Bram & Pip (foraging duo)

Their caravan is caked in salt and ash to ward off spirits. They survive by stripping old
ruins right at the forest's edge. Right home for them — an abandoned-but-not-dead remnant
benefits from two characters who chose to stay and bicker about it rather than one solemn
lore-keeper.

- **Shared pet — Tindertail** (Fire, Uncommon, standalone — no evolution). Found together
  as a single companion, splits time between the two of them. Smart rather than strong —
  it senses when the boundary line has shifted, which is how Pip knows.
- **Nickname — unresolved, on purpose**: Bram calls it "Match" (practical — it lights
  things). Pip calls it "Wisp" (it senses things, drifts off on its own). Neither has
  ever conceded to the other's name. If a player asks what it's called, Bram and Pip
  answer at the same time with different names and then start arguing about it — a
  small recurring bit, never resolved.
- **Side story — "the choosing"**: at some point (a hazard, a quiet returning-player moment),
  Tindertail has to pick who to follow/protect in the moment. No stakes, nothing bad happens
  either way — it's about how Bram and Pip each react, not about "winning." Warm, low-key
  character texture in the Sable/Ledge and Mira/Luna tradition.
- **Side story — "the line is moving"**: Pip has been quietly marking the ash circle's edge
  with small stones over time. At higher player rank, one more stone has been added — the
  circle is shrinking, very slowly. Neither Bram nor Pip tells Kaelen (don't want him
  "doing rituals" again). Ties directly into the Lore Spine above (Pyrehart weakening).
- Idle-expedition mechanic (feed Pip, send him on expeditions for seeds/currency/timber):
  benched as a separate future design pass — a new system, not part of this remnant's
  initial scope. Bram & Pip exist now with normal dialogue/flavor; the mechanic gets
  "bolted onto them later."

### Locations (4)

1. **Kaelen's Shack** — NPC location, dialogue + bounty board.
2. **Bram & Pip's Caravan** — NPC location, shared dialogue + Tindertail side stories.
3. **The Ash Circle** — explore zone (encounter table + explore events live here).
4. **The First Ring** — no-NPC, pure environmental lore (Mirefields' Old Crossroads
   pattern). Older, deeper ash. Home to rare Cindermaw/Pyrehart sightings and the
   "what burned, who burned it" lore choice event. **Marked as a lore zone for now —
   layout/role may still change** (e.g., could later become a sub-area of The Ash
   Circle rather than its own dropdown entry, depending on how explore zones are
   structured in code).

### Pets (5, locked)

| Pet | Type | Rarity | Role |
|---|---|---|---|
| Cinderkit → Ashveil | Fire | Common → Uncommon | Ambient wildlife / Kaelen's "Soot" |
| Tindertail | Fire | Uncommon (standalone) | Bram & Pip's shared companion |
| Smolderoot → Pyrethorn | Grass/Fire | Uncommon → Rare | Forest's failed regrowth attempts (mainly The First Ring) |
| Cindermaw | Grass/Fire | Ancient (standalone) | The contained fragment — rare sighting at The First Ring |
| Pyrehart | Fire | Ancient (standalone) | The guardian that helped contain it — rare sighting at The First Ring |

### Pet Appearances & Passives (rough — locked as foundation, numbers TBD)

**Cinderkit** (Common, Fire)
- Appearance: small fox-kit-like creature, ash-gray fur with faint ember-orange streaks
  along the spine and tail-tip. Curls up near warm ash to sleep — looks like a smudge
  until it moves. Big ears, low body heat except the streaks.
- Passive: *Ember Curl* — small resistance to energy drain from cold/hazard events. It
  generates its own warmth; the Verge's cold ash doesn't bother it.

**Ashveil** (Uncommon, Fire)
- Appearance: bigger, leaner than Cinderkit. Ember streaks become trailing wisps of
  smoke/ash that drift behind it as it moves, partially obscuring its silhouette —
  genuinely a little hard to track. Embers glow through the haze when alert.
- Passive: *Ash Shroud* — small evasion chance (Pallefin's Mist Veil pattern, but
  smoke/ash instead of mist). The trailing haze makes it hard to land a clean hit.

**Tindertail** (Uncommon, Fire, standalone — "smart, not strong")
- Appearance: small, quick, alert — more "scout" than "pet." Slim, weasel/lemur-like,
  with a single ember permanently lit at the very tip of its tail, used historically to
  relight dead fire-rings. Twitchy ears, always seems to be listening for something.
- Passive: *Boundary Sense* — small chance to avoid a hazard event outcome entirely.
  Utility over raw strength — fits its lore role (senses when the line has shifted).

**Smolderoot** (Uncommon, Grass/Fire)
- Appearance: looks like a charred sapling that somehow kept growing — blackened
  bark-skin with one thin vein of orange-red glow running through it like lava in
  stone. Stiff, slow-moving, faint smoke when it "breathes."
- Passive: *Smolder* — small chance to inflict a minor burn (DoT) on the opponent.
  It's literally still on fire, quietly.

**Pyrethorn** (Rare, Grass/Fire)
- Appearance: Smolderoot's larger form — gnarled, root-legged, hunched, walks on four
  thorned root-limbs with low flame constantly licking along its back like a smoldering
  log. Leaves smoking footprints. Looks like part of the burned forest got up and
  started walking.
- Passive: *Wildfire Roots* — upgraded Smolder (higher burn chance/damage) plus minor
  self-HP regen each turn (Siltborn's Reclaim pattern, fire-flavored). The smolder
  sustains it as much as it damages others.

**Cindermaw** (Ancient, standalone — lore/rare encounter)
- Appearance: massive, mostly inert charred root-mass, half-buried in deep ash. Looks
  like a dead, fused tangle of burned roots — until you notice the single faint ember
  glow deep within, like a heartbeat that's almost stopped. Doesn't visibly breathe.
- Passive: *Ash Lock* — reduces healing effectiveness on the opponent for the fight.
  Whatever this corruption touches doesn't recover cleanly, even partially burned.
  Dangerous, "wrong" feeling rather than just strong.

**Pyrehart** (Ancient, standalone — lore/rare encounter)
- Appearance: large, lion/wolf-shaped guardian, "fur" made of slow-moving embers and
  ash rather than hair — like a campfire holding the shape of an animal. Visibly
  scarred/dimmer than it should be — patches where the ember-fur has gone cold and
  gray. Sleeping, curled, near The First Ring.
- Passive: *Last Light* — stat boost (attack/defense) that increases as its own HP
  drops. Wounded, dimmer than it should be, but fights hardest when it matters most —
  echoes the original fight against what became Cindermaw.

All damage values, percentages, and exact trigger conditions deferred to coding session —
this locks the *flavor* of each ability to its lore role: Cinderkit/Ashveil = ambient
survival, Tindertail = utility/sensing, Smolderoot/Pyrethorn = sustain+burn, Cindermaw =
corruption that resists cleansing, Pyrehart = wounded guardian that fights hardest when
desperate.

### Encounter Table

**The Ash Circle (main explore zone):**

| Time | Pets |
|---|---|
| Day | Mossling, Cinderkit |
| Night | Mossling, Cinderkit, Grimweave, Smolderoot (rare) |

**The First Ring (lore zone, very rare sightings only — not a normal encounter pool):**

| Time | Pets |
|---|---|
| Any | Pyrethorn (rare), Cindermaw (very rare), Pyrehart (very rare) |

Tindertail is not in the general encounter table — it's tied specifically to Bram & Pip
as their shared companion, not a wild-catchable population.

### Items (Ashen Verge)

| Item ID | Name | Type | Source | Notes |
|---|---|---|---|---|
| `ash_ember` | Ash Ember | Crafting material | Cinderkit/Ashveil/Smolderoot/Pyrethorn drop | "Still warm. Doesn't cool down." Future crafting use — keep flexible. |
| `ember_charm` | Ember Charm | Consumable / utility | Explore loot, possibly Kaelen's bounty reward | Small warmth charm. Exact effect TBD (coding session) — likely minor cold/hazard resistance, mirrors Cinderkit's Ember Curl passive. |

### Explore Events — The Ash Circle

Zone key: TBD (e.g. `ashenVerge`). Tone: quiet, smoky, cold, *managed* — not hostile.

**Flavor**
```
- The grass ends in a perfectly straight line. On one side, green. On the other,
  gray ash that doesn't shift in the wind.

- Old fire-rings, dozens of them, in concentric circles fading outward. Most look
  decades old.

- Your footprints are the only mark on the ash. It hasn't rained here in a long
  time — or the ash doesn't let it show.

- A faint smell of smoke that never quite fades, even this far from any fire.
```

**Pet Sighting**
```
- A Cinderkit sits at the edge of a cold fire-ring, warming itself against embers
  that aren't there.

- Something with smoking footprints crossed here recently. The tracks lead toward
  the deeper ash and don't come back.
```

**Hazard**
```
- A patch of ash gives way to a bed of still-hot coals underneath.
  outcome: { hp: -6 }

- The wind shifts and a wall of ash dust rolls over you. Hard to see, harder to
  breathe for a moment.
  outcome: { energy: -1 }
```

**Loot Bonus**
```
- Half-buried near an old ring: something someone left as an offering, a long
  time ago.
  outcome: { item: lore_fragment or ash_ember, qty: 1 }
```

**Choice Events**
```
1. One of the fire-rings looks recently relit — ash disturbed, faint warmth.
   Kaelen didn't mention doing this.
   - "Investigate": item: lore_fragment, unsettling (ties to Pip's "the line
     moved" thread)
   - "Leave it": nothing

2. (The First Ring) The ash here is older — packed dense, almost glassy in
   places. At the center, something is half-buried: scorched, root-shaped, too
   large to be a tree stump. Nearby, barely visible under the ash, the shape of
   something else — curled, still, also half-buried.
   - "Brush away the ash": you recognize enough of both shapes to know they're
     not natural formations. Neither moves, but you feel watched anyway.
     item: lore_fragment, unsettling
   - "Leave it buried": nothing
```

~10 events total — tone confirmed, fine-tuning deferred to coding session.

### Still TBD

- Evolution levels for Cinderkit→Ashveil and Smolderoot→Pyrethorn
- `ember_charm` exact effect/value
- Exact zone key naming (`ashenVerge` vs alternative) and how The First Ring is
  structured in the locations dropdown (own entry vs sub-area of The Ash Circle)

---

## The Blind Well (quest-gated remnant)

**Visuals:** A pitch-black subterranean abyss beneath the oldest roots of Sylven the Treant.
Air thick with a sweet, sickening smell of decay, illuminated entirely by intense,
bruised-purple bioluminescent sap oozing from giant, pulsating root veins.

**Connection:** This is where the `whisperwoods_plea` / Heart of Decay quest leads — because
this is where the corruption goes to its source. Fae Whisper knows the path because she's
been here before, alone.

### NPC 1 — Anora, the Hollowed Weaver (quest climax / boss encounter)

The visible symptom of the Heart of Decay, not the source itself. Lean: a **Guild scout who
went looking for the source of the corruption decades ago and didn't come back the same** —
gives players a gut-punch if they ever cross-reference old Guild records (future hook).

- Visual: physically fused into the central root wall of the abyss, eyes weeping glowing,
  toxic sap into the earth.
- Mechanics: main narrative milestone/boss of Town 2. Defeating or purifying her
  vine-manifestations stabilizes the region (and may unlock further progression).

### NPC 2 — The Root-Eaten Scribe (hidden historian / lore)

A pre-Guild scholar trapped in a deep cavern pocket decades ago, surrounded by calcified,
petrified journals. Gives the player the "before" picture while Anora is the "after" — could
literally be the journal/remains of whoever was with Anora when it happened.

- Lore-seeds **Verdanthorn's Reflection** here: *"It showed me what Sylven could become, and
  I haven't been able to stop seeing it."* Don't fully build the encounter yet — keeps the
  door open for "the other connected location" in a future main-quest pairing.

### NPC 3 — Elowen

Forbidden magic + a literal corrupted limb (left arm transforming into dark wooden bark).
Conducts forbidden magic right outside the town's jurisdiction.

- Mechanics: plant/pet merchant — sells seeds, spores, and evolution items (ties to the
  Glamorose → Malicea → Aberraflora line; naming fix Glamourise → **Glamorose** applies here).
  Offers dangerous, high-risk bounties.
- Narrative: she'd recognize what Anora's becoming because she's a few steps behind on the
  same path — a "warning of what could happen to YOU" beat for the player too.

### Verdanthorn's Reflection (lore-seeded, mechanically deferred)

A towering knight of jagged black thorns patrolling the pulsing veins of the deep earth.
Treated like Veilmother/Chasmbane — lore-seeded now (via the Scribe's line above), not a
designed boss fight yet. Seed for "the other connected location" in a future main-quest
pairing alongside the Blind Well.

---

## Implementation Notes for Coding Session

1. `data/pets.py` — apply renames (Sunpetal Moth → Sunmoth, Moonpetal Sprite → Moonwisp,
   Gloom Weaver → Grimweave, Dreadspinner → Duskspinner). Add new lines: Sunmoth → Gilmoth →
   Solmoth, Serpentine → Serpumbra, Glamorose → Malicea → Aberraflora, Verdanthorn (standalone).
2. `data/pets.py` ENCOUNTER_TABLES — add `whisperwoodGrove` (Thicket) day/night and
   `whisperwoodWilds` day/night tables per tables above.
3. `data/towns.py` — add Luna to `moonpetal_inn.npcs` with night availability; adjust Mira's
   availability if needed so they don't both show at once.
4. `data/towns.py` — add NPC pet entries (Ferngale "Fen", Mossling "Frond", Moonwisp "Glim",
   Sunmoth "Petal", Lunarblossom) per the roster table.
5. `explore_events.py` — add `whisperwoodGrove` and `whisperwoodWilds` keys with events above.
6. `data/items.py` — add `lore_fragment`.
7. `whisperwoods_plea` quest — needs full design pass before implementation (see OPEN section).
8. Side story beat — needs design pass.
9. Remnants (Ashen Verge, Blind Well) — rough sketches only; need full design pass
   (NPC dialogue trees, encounter tables, items, explore events) before implementation.
   Two open questions flagged inline above.
