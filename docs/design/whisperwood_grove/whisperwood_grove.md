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
   **The Weeping Root** (quest-gated). Marked OPEN where decisions are still pending.

**Still open / not yet designed (flagged inline below):**
- `whisperwoods_plea` quest structure — what the "Heart of Decay" actually is mechanically,
  and the full step-by-step (only the start/end dialogue beats exist in code today).
- Side story beat (Luna/Mira, Fae Whisper, Arboreal/Sylven thread).
- Ashen Verge: Cinderkit→Ashveil wild-catchable vs NPC-only; Kaelen's bounty target species.
- Weeping Root: full dialogue trees for Anora / Scribe / Elowen.
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
  She's been to the Weeping Root before — alone.
- The corruption arc (`whisperwoods_plea` / Heart of Decay) isn't "clear a forest problem" —
  it's "something ancient and protective is dying/corrupting from the inside, and the player
  has to deal with that."

Gameplay note: Sylven is **never an encounter inside the Thicket**. After `whisperwoods_plea`,
Sylven remains a passive presence (see Pet Sighting events below — "something large moves
through the undergrowth... it is part of the ground").

---

## Gloom Sickness — Framework: State / Type / Mark

**Important framing:** This is presented as the *current* scholarly/in-world understanding of
how Gloom affects living things — not a locked taxonomy in the sense of "nothing can ever be
added." The Gloom should be able to **evolve, mutate, and reveal worse/stranger stages later**
as the story progresses. Treat everything below as "what characters in-world currently
believe," which may turn out to be incomplete or wrong. This gives future towns room to
escalate or add nuance without contradicting anything locked here.

**This is not a new system — it's a name for something already in the code**, just never
tied together into one framework before now. The framework has three independent layers:
**State** (degree of progression), **Type** (manner of manifestation), **Mark** (the visible
symptom).

### 1. Gloom State — The Seven Gloom States

Deliberately given the same number of rungs as Classification Tier (see
`aethelgard_classification.md`) — not because the two scales are equivalent, but so they can
be discussed in the same breath ("this creature's Gloom State reads as Elder-equivalent").
**Classification asks "what is this being?" Gloom asks "what relationship does this being
have with the Gloom?"** Two parallel frames over the same world, not one hierarchy.

1. **Touched** — *The Invitation.* The Gloom has entered the being. Something has changed,
   but the self is still largely intact. Some believe the Touched can be healed. Some believe
   they have been chosen. *"The beast is Touched."*
2. **Shorn** — *The Erosion.* Something essential has been cut away — memories, instincts,
   identity, emotions, or connections begin to fray. The being still exists, but it is no
   longer whole. *"The Shorn forget familiar paths."*
3. **Hollow** — *The Shell.* The original self has been emptied. What once was remains only
   as a vessel. Whether anything still lingers inside is a matter of belief. *"The Hollow
   still walk."*
4. **Wrought** — *The Remaking.* The empty shell is reshaped. The Gloom no longer merely
   consumes — it creates. A Wrought being often embodies the wound of its territory.
   *"The Wrought become the wound."*
5. **Forsaken** — *The Separation.* The being no longer belongs to the ordinary order of the
   world. Some pity them. Some fear them. Some envy them. *"The Forsaken have no place left."*
6. **Unbound** — *The Release.* The Gloom is no longer fully restrained by host, body, or
   place. Identity dissolves into something larger. Some see this as the ultimate tragedy.
   Others see it as freedom. *"The Unbound answer to nothing."*
7. **Oblivion** — *The Absolute.* The final horizon. The distinction between being, place,
   memory, and force begins to disappear. An Oblivion may no longer be merely a creature — it
   may become a phenomenon, a scar, or a forgotten law of the world itself. *"Of the Oblivion,
   no trustworthy account survives."*

**Narrative arc:** Touched (the Gloom enters) → Shorn (something is lost) → Hollow (the self
is emptied) → Wrought (the emptiness is remade) → Forsaken (it no longer belongs) → Unbound
(it escapes its restraints) → Oblivion (it passes beyond ordinary existence).

**What's active right now vs. reserved for later:**
- **States 1-3 (Touched / Shorn / Hollow)** are the active, in-use rungs. This is the old
  "Touched / Hollowing / Hollowed" 3-state scale, renamed for precision —
  Hollowing → Shorn, Hollowed → Hollow. The remap is a rename, not a redesign: anything
  previously written as "Hollowing" is now "Shorn," anything "Hollowed" is now "Hollow."
  These are the values `gloom.state` will actually hold on pets/NPCs for the foreseeable
  future.
- **State 4 (Wrought)** is lore-confirmed but not yet a usable pet-data value — Hollowthorn
  and Cindermaw are Wrought ("the Wrought become the wound" = Elder tier's "embodies a quality
  of its territory," near-verbatim). Both remain lore-seeded/mechanically deferred
  (Veilmother/Chasmbane pattern), so no stat block needs `gloom.state: "Wrought"` yet — but
  when one is built, this is the value to use.
- **States 5-7 (Forsaken / Unbound / Oblivion)** are reserved/lore-only, same spirit as
  Classification Tier's Primordial/Eternal — "don't force an example into existence just to
  fill the table."

### Anora — State determination

Anora's title, "the Hollowed Weaver," reads as a **legacy/colloquial name** — given decades
ago, before this framework existed, by someone using "Hollowed" the way people still use it
casually (cf. "the Hollowed Weaver" vs. the precise term "Hollow"). Her actual State is
**Shorn**, not Hollow: the quest's stakes (a person worth reaching, "kindness and
understanding," the Sever choice "arresting an active progression") all depend on there being
an undisputed *someone* still there to reach — which is Shorn's "still exists, but no longer
whole," not Hollow's "whether anything still lingers is a matter of belief." This is also a
non-change mechanically: she was already "Hollowing" under the old 3-state scale, and
Hollowing → Shorn was already the agreed rename. Updated mapping:

- **Elowen** — State: **Touched**. Type: **Withering**. Mark: the corrupted bark arm.
- **Anora** — State: **Shorn**. Type: **Withering**. Mark: root-fusion + weeping, glowing sap
  from the eyes. (Hollowthorn, separately, represents Wrought at this site — Anora doesn't
  need to "be" Wrought herself for Hollowthorn to exist as the site's Wrought entity.)
- **Corvin** — State: **Touched** (arguably never progressed further). Type: **Calcifying**.
  Mark: the petrified/calcified body.

### Frames as factions (future hook, not built yet)

The Core Philosophy underlying this framework: **the Gloom is not inherently good or evil —
it's a fundamental force, and different people construct different narratives around it.**
The Guild studies it. Hunters fear it. Healers mourn it. Some seek to become it. Some believe
the Unbound are finally free. Some believe Oblivion is the world's oldest truth. There may
never be a single absolute answer — only different frames observing the same mystery.

The seven-state vocabulary above (Touched/Shorn/Hollow/...) is presented as the **Guild's**
frame — clinical, scholarly. Other factions (Hunters, Healers, whoever "seeks to become it")
could use entirely different vocabulary for the *same* underlying states, without
contradicting this framework — just adding a lens on top of it. Not designed yet, but flagged
as a strong path for future faction/player-choice content layered over this same backbone.

### 2. Gloom Type — manner of manifestation (varies by exposure/region)

*How* the Gloom expresses itself — this is what makes "Touched" mean something different
depending on what you're looking at, and gives the State system room to feel less vague as
more Types get introduced over time. Two are named so far:

- **Withering** (NEW — native to the Weeping Root) — root/sap-based corruption; slow
  replacement of living tissue from the inside. This is the Type that originates here.
- **Calcifying** (NEW name, but already precedented in code) — works like a "stoneplate
  virus": stone-like plating/growths spread across parts of the body and then **stop
  spreading**, leaving permanent hardened patches without ever finishing. Critically, this is
  **not** immobility or unresponsiveness — the afflicted remains fully mobile, alert, and
  able to fight/communicate normally; only specific patches of the body are affected. The
  existing **Threshling → Threshbound** pet line (`data/pets.py`) — *"Caught at the threshold
  between existence and full Gloom consumption... locked in between states"* — is this Type,
  already in the roster, just not named until now (re-read as "partial calcification that
  stalled," not "frozen solid").
- (Likely more Types exist unnamed in the current codebase — e.g., Gauntling→Waneling reads
  like a "Fading" Type, Rimecrawl→Frostbile reads like a "Frostbound" Type. Not authored here;
  flagged for whoever picks up Gloom framework work next.)

### 3. Gloom Mark — the individual visible symptom

What you actually *see* on a specific creature/person — the physical "tell" of their State.
Two individuals in the same State can have completely different-looking Marks depending on
species/Type. The Mark is how players (and NPCs) identify a State at a glance.

(See "Anora — State determination" above for how the three Weeping Root NPCs — Elowen,
Anora, Corvin — map onto State/Type/Mark. Two Types coexist at that site because Corvin's
exposure (pre-Guild, long ago) predates the Withering Type that dominates there now.)

### Existing-code anchors (for the coding session)

- `is_gloom_touched` — boolean flag on pets (`data/pets.py`), used by `battle_engine.py` for
  the Gloom meter and capture-rate logic. Maps to "has *some* Gloom State" (i.e. not the
  baseline/unafflicted case). **Implemented this pass:** a parallel `gloom: {state, type,
  mark}` dict has now been added alongside `is_gloom_touched: True` on the relevant pet
  entries (Corroder/Blightcrust, Grimweave/Veilmother, Gauntling/Waneling,
  Rimecrawl/Frostbile, Threshling/Threshbound, Stillroot), using the State/Type/Mark
  vocabulary above. `is_gloom_touched` itself is unchanged and still drives existing battle
  logic — `gloom` is additive, descriptive data for now (not yet read by any code).
- **`data/classifications.py`** (NEW) — both frameworks (Classification Tier and the
  7-state Gloom State scale, with titles/descriptions/example phrases, the
  Classification↔Gloom parallel mapping, and `ACTIVE_*` lists marking which rungs are
  currently in use vs. lore-reserved) now live here as plain data, so the rest of the
  codebase has one place to reference them. Not wired into any game logic yet — reference
  data for future flavor text/tooltips/lore commands. Names/descriptions/order can still be
  adjusted; this is a structure to build on, not a final lock.
- `data/remnants.py` (Mirefields/Chasm content) already has an NPC dialogue line
  (`lore_hollowed_vs_corrupted`) that draws the Touched-vs-Hollowed distinction in-world:
  *"Corrupted pets can still be reached — the Gloom has touched them but hasn't consumed
  them. There's still something there to work with. Hollowed is different. When a creature
  Hollows, there's nothing left that remembers being a creature. That distinction matters."*
- The same Mirefields/Chasm content has a `lore_gloom_origin` line establishing Gloom has a
  **single breach site** ("the Chasm"), theorized to be caused by "collective grief — a
  catastrophic loss, enough souls in enough pain at once to tear something open." The Heart
  of Decay / Weeping Root is **not** that origin point — it's a separate growth of the same
  overarching Gloom phenomenon, taken root inside Sylven specifically (different growth site,
  same underlying force — and likely a different Type, since Withering is native here).
- Purity Orbs and similar items (`gloom_effect` in `data/items.py`) are the existing
  treatment mechanic — most effective on Touched-State afflictions.

This framework is reusable for future towns/remnants — new States, Types, or Marks can be
added later without needing to retcon anything here.

**Connection to Oakhaven Outpost (Town 1):** Oakhaven already planted hints of this without
naming it — Galen's unspoken suspicion that the Rotting Pits and the Weeping Chasm "share a
Gloom source — same breach, different surface points" (`docs/design/oakhaven_outpost/oakhaven_outpost-done.md`)
is the same underlying phenomenon, just not yet given a framework. Whisperwood Grove —
specifically the Weeping Root — is where the player first gets the *vocabulary* (State / Type
/ Mark) to understand what Oakhaven was hinting at. Nothing in Oakhaven needs to change; this
is presented as the payoff of an earlier breadcrumb, not a retcon.

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
above) she's tied directly to Sylven and the Weeping Root. Side story material.

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
  Elowen's material at the Weeping Root).

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
- Whether/how the Weeping Root (see below) ties into this quest as the location where the
  Heart of Decay's source is actually confronted.

---

## Side Story Beat (OPEN / TBD)

Identified threads, not yet written into a structured beat:
- The Luna/Mira dynamic (day/night halves of the same inn, complementary knowledge).
- Fae Whisper's role — she's been to the Weeping Root before, alone, and has crossed paths
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
line is meant to pay off later in the Weeping Root — the player goes from "huh, ash circle" up
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

- ~~Evolution levels for Cinderkit→Ashveil and Smolderoot→Pyrethorn~~ — RESOLVED
  (groundwork pass): Cinderkit→Ashveil at 16 (matches other Common→Uncommon lines),
  Smolderoot→Pyrethorn at 30 (matches Uncommon→Rare lines).
- ~~`ember_charm` exact effect/value~~ — RESOLVED (groundwork pass): consumable,
  restores 15 player energy (`restore_energy` effect, same family as Sun-Kissed
  Berries/Trail Morsels). Matches the "small warmth charm" flavor without adding a
  new mechanical hook.
- ~~Exact zone key naming and First Ring structure~~ — RESOLVED (groundwork pass):
  zone key is `ashenVerge`. The First Ring was folded into The Ash Circle's
  encounter table as rare/very-rare sightings (Pyrethorn day, Cindermaw/Pyrehart
  night) rather than its own dropdown entry — revisit if it needs a distinct
  location later (e.g. for the lore choice events).

---

## The Weeping Root (quest-gated remnant)

**Status:** Quest-gated remnant — unlocked partway through `whisperwoods_plea`. Not visible
in travel options until the gate fires (see Connection/Flow below). Once unlocked, stays
accessible afterward (Elowen is a recurring merchant, Corvin is a recurring lore stop, and
Anora's resolved state remains visitable).

**Visuals:** A pitch-black subterranean abyss beneath the oldest roots of Sylven the Treant.
Air thick with a sweet, sickening smell of decay, illuminated entirely by intense,
bruised-purple bioluminescent sap oozing from giant, pulsating root veins.

**Connection / Flow:** While `whisperwoods_plea` is active, a quest-only Choice Event in the
Whispering Thicket fires (mirrors the Ferryn's-Fetch pattern from Mirefields — quest-gated
explore event, but the payoff is a location unlock instead of an item). Fae Whisper steps out
from between two roots that "weren't there a moment ago" — *"I've been down there. I don't go
anymore. But you need to."* — and opens the path down into The Weeping Root. She knows the way
because she's been here before, alone.

### Gloom Sickness — this is the source

See "Gloom Sickness — Framework: State / Type / Mark" earlier in this doc for the full
framework and its existing-code anchors. **The Weeping Root is the growth site** for the
**Withering** Type — not the original Chasm breach (that's a separate, older lore thread
already in `data/remnants.py`), but where Withering specifically originates. All three NPCs
here represent different points in the framework:

- **Elowen** — State: Touched, Type: Withering, Mark: corrupted bark arm
- **Anora** — State: Shorn, Type: Withering, Mark: root-fusion + weeping sap eyes
- **Corvin** — State: Touched, Type: Calcifying, Mark: petrified/calcified body

### Lore Spine (locked)

**The wound that couldn't be burned out.** Ashen Verge was a fragment of Whisperwood's
corruption that broke off long ago and got sealed with fire — a scar on the surface,
contained. The Weeping Root is the *source* fire could never reach, because it isn't a
separate thing sitting on the land — it's grown directly into **Sylven's own root system**.
You can't burn it out without burning Sylven himself.

**The sap has turned.** Sylven's sap — his lifeblood — runs bruised-purple and bioluminescent
down here, "weeping" out of the root walls like an infected wound seeping. Prolonged exposure
to it doesn't kill outright — it sets off the Gloom Sickness progression (see "Gloom Sickness
— Working Theory of Stages" above), slowly replacing what a living thing was with something
that serves the wound, while leaving fragments of the original self behind (memory,
personality, mannerisms bleeding through). The Weeping Root is where this *originates* — the
source spring of Gloom Sickness, not just another infected site. (Note: State names —
Touched/Shorn/Hollow, etc. — are the *current* in-world understanding, not locked endpoints —
see the Gloom Sickness section for the full seven-state framework.)

**Three case studies, told through three NPCs — each at a different point in the
State/Type/Mark framework:**

- **Corvin, the Root-Eaten Scribe** (long ago, pre-Guild) — found the wound first. His
  exposure predates Withering — instead his Gloom Type is **Calcifying**, which spread
  stone-like patches across parts of his body and then stalled at "Touched," decades ago.
  Fully mobile and lucid — "Petrified" describes the patches, not the person — a living
  record of the "before."
- **Anora** (decades ago, Guild scout) — Type: **Withering**, State: **Shorn**. The process
  has run further than Elowen's or Corvin's, fusing her into the root wall — but "Shorn," not
  "Hollow," because there's still an Anora *there*: someone whose tragedy and whose chance at
  recovery still mean something. She is the current active threat/quest climax.
- **Elowen** (present day) — Type: **Withering**, State: **Touched** (a corrupted bark arm).
  She sought out the Weeping Root deliberately — Corvin and Anora are her two case studies, and
  her forbidden magic is self-directed research into whether the process can be deliberately
  *stopped/frozen* (like Corvin) before it runs its course (like Anora). Her "evolution item"
  trade (Glamorose → Malicea → Aberraflora line; naming fix Glamourise → **Glamorose** applies
  here) is part of that research, not just commerce.

**Verdanthorn's Reflection** is the wound's "immune response" — a corrupted echo of
Verdanthorn (Sylven's living guardian presence above) grown from the same toxic root-matter,
patrolling the deep veins. It's a preview of what Verdanthorn — and all of Sylven — becomes
if the wound wins. Ties directly to Corvin's line: *"It showed me what Sylven could become."*

**Anora's choice (purify vs. defeat) pays off the structure:**

- **Purify** — draw the toxic sap out of her without destroying the host. Slow, risky, but
  she may survive in a recovering form; her alcove's sap clears from bruised-purple toward
  something healthier.
- **Defeat** — remove the corrupted mass outright. Faster, decisive, but Anora doesn't
  survive in any recognizable form; her alcove becomes an empty, scarred cavity.

Either way, severing this "active terminal" stops the spread and stabilizes the region —
mirroring the "the line is moving" thread from Ashen Verge (the shrinking boundary stops once
this is dealt with). Full healing of Sylven himself stays a longer-term/future-arc thread.
Exact mechanical/dialogue differences between the two outcomes: **TBD, later pass.**

### NPC 1 — Anora, the Hollowed Weaver (quest climax / boss encounter)

The visible symptom of the Heart of Decay, not the source itself. Lean: a **Guild scout who
went looking for the source of the corruption decades ago and didn't come back the same** —
gives players a gut-punch if they ever cross-reference old Guild records (future hook).

- Visual: physically fused into the central root wall of the abyss, eyes weeping glowing,
  toxic sap into the earth.
- Mechanics: main narrative milestone/boss of Town 2. Defeating or purifying her
  vine-manifestations stabilizes the region (and may unlock further progression).
- Player choice (purify vs. defeat) — see Lore Spine above. Outcome details TBD.

### NPC 2 — Corvin, the Root-Eaten Scribe (hidden historian / lore)

A pre-Guild scholar trapped in a deep cavern pocket decades ago, surrounded by calcified,
petrified journals. Gives the player the "before" picture while Anora is the "after" — could
literally be the journal/remains of whoever was with Anora when it happened.

- Lore-seeds **Verdanthorn's Reflection** here: *"It showed me what Sylven could become, and
  I haven't been able to stop seeing it."* Don't fully build the encounter yet — keeps the
  door open for "the other connected location" in a future main-quest pairing.

### NPC 3 — Elowen

Forbidden magic + a literal corrupted limb (left arm transforming into dark wooden bark).
Conducts forbidden magic right outside the town's jurisdiction. Currently
**State: Touched, Type: Withering, Mark: corrupted bark arm** — see Lore Spine and Gloom
Sickness section above.

- **Personality:** all three of "pragmatic," "desperate," and "resigned" at once — not in
  conflict, but layered. She treats her own affliction like a research problem (pragmatic),
  because she's racing her own timeline (desperate), while having already accepted that
  "cured" probably isn't a realistic outcome — "frozen" or "gone" are the likely endpoints,
  and she's trying to land on the better of those two (resigned). Not bitter or cruel —
  matter-of-fact, even gentle, about things most people would find horrifying.
- Mechanics: plant/pet merchant — sells seeds, spores, and evolution items (ties to the
  Glamorose → Malicea → Aberraflora line; naming fix Glamourise → **Glamorose** applies here).
  Offers dangerous, high-risk bounties.
- Narrative: she'd recognize what Anora's becoming because she's a few steps behind on the
  same path — a "warning of what could happen to YOU" beat for the player too. Her research
  uses Corvin (frozen/Petrified, Touched) and Anora (Shorn, furthest along) as her two reference points —
  she didn't stumble into the Weeping Root, she sought it out *because* they're here.

**Pet — TBD name, species TBD, State: Touched / Type: Withering** (same Mark framework as
Elowen herself — see Pets section below for the proposed Glamorose-based design). Her
"control subject" — a small creature she's been monitoring/treating alongside her own
affliction, its condition mirroring (and informing) her own progression. Not framed as a warm
companion in the usual sense, but not cold either — she's quietly trying to keep it from
progressing further than she has, even while accepting she may not be able to do the same for
herself.

- **Side story seed (future expansion):** at some point along her arc, she may have to "let
  go" of this pet — release it, or lose her ability to treat it — as part of a larger
  "searching for answers to treat Gloom Sickness" thread. Not structured yet; flagged here so
  it isn't lost. Could tie into future towns/NPCs working on the same problem from other
  angles.

### Verdanthorn's Reflection (lore-seeded, mechanically deferred)

A towering knight of jagged black thorns patrolling the pulsing veins of the deep earth. Not
literally the same creature as Verdanthorn (the standalone Ancient pet in the main
Whisperwood roster) — a corrupted mirror/doppelganger of it, born from the same toxic
root-matter as the rest of the Weeping Root. Treated like Veilmother/Chasmbane — lore-seeded
now (via Corvin's line above), not a designed boss fight yet. Seed for "the other connected
location" in a future main-quest pairing alongside the Weeping Root.

### Locations (5, proposed)

Mirrors the Ashen Verge structure (NPC locations + main explore zone + lore zone). Rough flow
order, following the path Fae Whisper opens:

1. **Elowen's Camp** — just outside the town's jurisdiction, positioned as the
   threshold/last stop before the descent. Merchant beat before the dive.
2. **Corvin's Hollow** — the petrified-journal cavern pocket. Lore-heavy "before" picture.
3. **The Weeping Root** — main explore zone (encounter table, explore events).
4. **The Deep Vein** — lore zone, Verdanthorn's Reflection (Hollowthorn) seeded here. "May
   still change" flag, same as The First Ring in Ashen Verge.
5. **Anora's Hollow** — the central root wall. Quest climax/boss encounter.

### Pets (template for State/Type/Mark going forward)

Only **one new species** for this remnant — Stillroot. Hollowthorn (Verdanthorn's Reflection)
remains lore-seeded/mechanically deferred (Veilmother/Chasmbane pattern), so it isn't counted
as "added" yet. Everything else reuses existing species with a Gloom Mark applied.

| Pet | Type | Rarity | State / Type / Mark | Role |
|---|---|---|---|---|
| Stillroot (NEW) | Rock/Grass | Common (standalone) | Touched / Calcifying / stone-plated patches | Corvin's companion; rare wild encounter |
| Veinglow (NEW) | Poison/Grass | Uncommon (standalone) | Not Gloom-Marked — adapted/immune | Ambient — The Weeping Root, sap-veins |
| Glamorose (Withering variant) | Grass/Poison | Common | Touched / Withering / one wilted petal | Elowen's pet |
| Mossling (Withering variant) | (existing type) | Common | Touched / Withering | Ambient — Weeping Root |
| Serpentine (Withering variant) | (existing type) | Uncommon | Shorn / Withering | Ambient — Weeping Root |
| Hollowthorn (Verdanthorn's Reflection) | Grass/Ghost | Elder (standalone, deferred) | Wrought / Withering (extreme) | Lore-seeded only — The Deep Vein |

### Pet Appearances & Passives (rough — locked as foundation, numbers TBD)

**Stillroot** (Common, Rock/Grass, standalone — Touched/Calcifying)
- Appearance: a small root-and-moss creature with patches of genuine stone-like growth
  spreading across its body — like lichen-covered rock fused onto living moss. Fully mobile,
  alert, and able to fight/communicate normally; the calcified patches haven't progressed in
  a long time and likely never will.
- Passive: *Stonecrust* — bonus passive Defense from the calcified plating, **no Speed
  penalty** — armored, not slow. Rewards patience without making it feel inert or "stuck in
  place."
- Found among Corvin's petrified journals (his companion); also a rare wild encounter in The
  Weeping Root proper — signals to the player that Corvin's "Calcifying" case isn't unique,
  just rare.

**Veinglow** (NEW — Uncommon, Poison/Grass, standalone)
- Appearance: a small, eel-like or larval creature that lives directly within the sap-veins,
  bioluminescent in the same bruised-purple as its surroundings. The glow brightens briefly
  when it first notices something approaching, then gradually fades/dims as it settles back
  into stillness — a natural "hint, then fade" signal rather than a constant light.
- Lore: explicitly **not** Gloom-Marked (`is_gloom_touched: False`, same precedent as
  Siltborn in Mirefields) — its body chemistry has *adapted* to neutralize the toxic sap
  rather than being afflicted by it. The first hint of something that isn't sick down here.
  Elowen would be very interested in one (side-story seed for the "searching for a Gloom
  Sickness treatment" thread — not a cure, just a clue).
- Passive (rough): *Neutralize* — small chance to resist or shrug off poison-type status
  effects against it, reflecting its natural resistance to the sap's toxicity.

**Glamorose (Withering Mark)** — Elowen's pet
- Appearance: identical to standard Glamorose (soft, floating, delicate petals) except for
  **one petal** that's wilted, discolored, and faintly leaking the same bruised-purple
  bioluminescence as the Weeping Root's sap veins — small, easy to miss unless you're looking
  for it.
- Passive: same as base Glamorose for now (no mechanical change at Touched State) — the Mark
  is presented as primarily *visual/narrative* at this stage. Reinforces that Touched is
  "manageable" — barely different from an unafflicted pet.

**Mossling (Withering Mark)** — ambient, ~Touched
- Appearance: standard Mossling, but its moss has gone a duller, ashier green, with faint
  purple-ish veining visible just under the surface in patches.
- Passive: as base Mossling — same "barely different" framing as Elowen's Glamorose.

**Serpentine (Withering Mark)** — ambient, ~Shorn
- Appearance: a more visibly disturbing step up — the vine-body looks like it's *unraveling*
  in places, with the bruised-purple sap visibly seeping from the unraveled ends. Less
  "indistinguishable from a vine" (its normal trait) and more "a vine that's coming apart
  from the inside."
- Passive: existing Serpentine kit, possibly with a minor downside/quirk reflecting
  instability (exact mechanic TBD) — first taste of "Shorn doesn't just look different,
  it behaves differently."

**Hollowthorn (Verdanthorn's Reflection)** — lore-seeded, deferred
- No appearance/passive lock yet beyond what's already written ("a towering knight of jagged
  black thorns patrolling the pulsing veins of the deep earth"). Full design deferred to a
  future pass, same as Veilmother/Chasmbane.

### Encounter Table — The Weeping Root (main explore zone)

| Tier | Pet (Mark) |
|---|---|
| Common | Mossling (Withering Mark, Touched) |
| Uncommon | Serpentine (Withering Mark, Shorn), Glamorose (Withering Mark, Touched), Veinglow (unmarked, adapted) |
| Rare | Stillroot (Calcifying Mark, Touched) |
| Lore zone (The Deep Vein) only | Hollowthorn (very rare sighting) |

This table is the "tour" structure: common encounters show **Withering at Touched**, rarer
ones show **Withering progressing toward Shorn**, a special rare shows the **other Type
(Calcifying)** existing alongside it, and the lore zone teases the framework's far end via
Hollowthorn, sitting at **Wrought**.

### Items (The Weeping Root)

| Item ID | Name | Type | Source | Notes |
|---|---|---|---|---|
| `weeping_sap` | Weeping Sap | Crafting material | Withering-Marked pet drops, Loot Bonus events | Bruised-purple, faintly warm, doesn't behave like sap should. Future crafting use — keep flexible (parallel to `ash_ember`). |
| `stoneplate_shard` | Stoneplate Shard | Crafting material | Stillroot drop, Loot Bonus events | A piece of calcified bark/stone. Cool, smooth, doesn't regrow. |
| `veinglow_essence` | Veinglow Essence | Quest/research item | Rare Veinglow drop | Tastes neutral against the tongue — somehow, against everything else down here. Elowen would want this (side-story seed for the Gloom Sickness research thread). Not a cure; a clue. |

### Explore Events — The Weeping Root

Zone key: TBD (e.g. `weepingRoot`). Tone: dark, oppressive, dripping, sickly-sweet — the
inverse of the Thicket's "managed" Ashen Verge quiet. Bioluminescent bruised-purple glow is
the only light source.

**Flavor**
```
- Bruised-purple veins pulse along the cavern walls, slow and steady, like a heartbeat
  that isn't yours.

- The air is thick and sweet, almost cloying — like fruit left far too long in the
  sun.

- Your footsteps echo down here, but a half-second late, like something nearby is
  copying them.

- Drops of sap fall from somewhere above, hissing faintly where they land.
```

**Pet Sighting**
```
- A Mossling shuffles past — its moss has gone duller, ashier, with faint purple
  veining just beneath the surface.

- Something with too many root-like limbs unravels and reforms in the dark, just out
  of clear sight, before you can get a good look.

- A faint purple glow brightens nearby, then slowly dims again as whatever it belongs
  to settles back into stillness.
```

**Hazard**
```
- You step into a shallow pool of sap before you notice it. It's warmer than it
  should be, and it takes a moment to wash off.
  outcome: { hp: -6 }

- One of the root-veins pulses harder than the others, and for a moment the whole
  cavern seems to shudder. Loose stone rattles down from somewhere above.
  outcome: { energy: -1 }
```

**Loot Bonus**
```
- Something glints faintly beneath a film of dried sap.
  outcome: { item: weeping_sap or stoneplate_shard, qty: 1 }
```

**Choice Events**
```
1. A faint purple glow brightens as you pass, then dims again — slower than the others
   you've seen. This one didn't flee.
   - "Approach slowly": it's a Veinglow, unbothered by the sap around it. Doesn't seem
     sick at all. (lore_fragment, seeds Elowen's research thread / veinglow_essence
     chance)
   - "Leave it be": nothing

2. The path splits — one way deeper into the main cavern, the other toward a narrow
   vein where the purple glow is brightest, almost too bright to look at directly.
   Something large moves at the very edge of it, then is gone.
   - "Follow the brightest vein": glimpse toward The Deep Vein — ties to Hollowthorn
     (Verdanthorn's Reflection), not a full encounter yet. (lore_fragment, unsettling)
   - "Stay on the main path": nothing
```

### A note on terminology ("pets")

Open idea, not acted on yet: is there an in-world term the people of Aethelgard use instead
of "pets" (companions, partners, etc.)? Flagged here so it isn't lost — for now, "pets"
stays the working term throughout this doc and in code.

Still TBD: exact dropdown structure/zone keys, encounter tables for the other 4 locations
(if any need their own beyond the main zone), full dialogue trees, Anora's purify/defeat
mechanics and dialogue branches (including whether her "vine-manifestations" boss mechanic
uses Withering/Shorn-Marked creatures as the fight's building blocks).

### Implementation status — Pass A (groundwork) complete

Mirrors the Ashen Verge groundwork-first approach, but more conservative given how much of
this remnant is still TBD (NPC dialogue, Anora's purify/defeat mechanic, the
`whisperwoods_plea` quest-gating mechanism). Pass A covers only the data/zone shell, **left
disconnected by design**:

- **2 new pets** (`data/pets.py`): Stillroot (Common, Rock/Grass, standalone — `Stonecrust`
  passive, `is_gloom_touched: True`, Touched/Calcifying) and Veinglow (Uncommon, Poison/Grass,
  standalone — `Neutralize` passive, `is_gloom_touched: False`, same "adapted, not afflicted"
  precedent as Siltborn). The Withering-Marked Mossling/Serpentine/Glamorose variants from the
  pets table were **not** given separate species entries or an `is_gloom_touched` flag —
  doing so would mark *all* Mossling/Serpentine/Glamorose everywhere as Gloom-touched, which
  is wrong (only the Weeping Root's population is Marked). Per the doc's own framing
  ("primarily visual/narrative at this stage" for Touched), the Withering Mark for these three
  is represented as flavor text only (on_enter text, `EXPLORE_EVENTS["weepingRoot"]`,
  `ENCOUNTER_TABLES["weepingRoot"]` comment) — no mechanical change, no new data entries. This
  sidesteps the deferred "Gloom Mark code representation" question entirely for Pass A.
- **`ENCOUNTER_TABLES["weepingRoot"]`** (`data/pets.py`): Mossling/Serpentine/Glamorose
  (Withering, flavor-only) + Veinglow (unmarked) + rare Stillroot (Calcifying), single table
  reused for day/night since the zone is permanently underground.
- **3 new items** (`data/items.py`): `weeping_sap`, `stoneplate_shard` (Crafting Materials,
  parallel to `ash_ember`), `veinglow_essence` (Quest Items, research-thread seed for Elowen).
- **`EXPLORE_EVENTS["weepingRoot"]`** (`data/explore_events.py`, 13 events) +
  `ZONE_LOOT_TABLES["weepingRoot"]`: flavor/pet_sighting/hazard/loot_bonus/choice events per
  the doc's sketches, including the Veinglow "approach slowly" choice
  (→ `veinglow_essence`) and the Deep Vein "brightest vein" choice (Hollowthorn glimpse,
  → `lore_fragment`, kept unsettling per the classification framework's note on Elder
  sightings).
- **`data/remnants.py`**: new `weepingRoot` remnant entry, 5 locations (Elowen's Camp,
  Corvin's Hollow, The Weeping Root, The Deep Vein, Anora's Hollow) with on_enter flavor text
  for each. `the_weeping_root` location has `services.explore_zone: "weepingRoot"`.
  - **Elowen** (Elowen's Camp) and **Corvin** (Corvin's Hollow) are added as NPC stubs —
    `name`/`role`/`availability`/`pet` only, no `dialogue` key (mirrors the pre-dialogue
    Ashen Verge pattern). Their pets follow the doc's pets table directly: Corvin →
    Stillroot (Touched/Calcifying — matches Corvin's own Mark exactly), Elowen → Glamorose
    with the Withering Mark (one wilted petal — her "control subject"). Both pet
    `nickname`s are `None`/TBD pending Pass B. The Talk button works but just returns "..."
    until dialogue trees are added.
  - **Anora's Hollow** stays `npcs: {}` — she's the quest climax, not a stub-able NPC; her
    full presence, dialogue, and purify/defeat mechanic are Pass B/C together.
  - The Deep Vein also stays `npcs: {}` (lore zone, Hollowthorn lore-seeded only).
- **Quest gate (placeholder, not wired)**: `weepingRoot` has
  `connection_requirements: {"whisperwoodGrove": "whisperwoods_plea_weeping_root_unlocked"}`,
  and `data/towns.py`'s `whisperwoodGrove` entry adds the reverse connection gated by the same
  flag. **No quest step sets this flag yet** — per `whisperwoods_plea_quest.md`, the Fae
  Whisper Choice Event that's supposed to set it (Beat 3) is a separate wiring pass. Until
  then, this remnant is correctly hidden from both directions' travel dropdowns — confirmed
  via the same `connection_requirements` check `weeping_chasm`/`mirefields` already use.

**Deferred to Pass B/C** (per `whisperwoods_plea_quest.md`): Elowen/Corvin/Anora NPCs, pets,
and dialogue trees; the Fae Whisper quest-gate wiring; Anora's purify/defeat mechanic;
Hollowthorn/Verdanthorn's Reflection (lore-seeded only, same as Veilmother/Chasmbane).

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
9. Remnants (Ashen Verge, Weeping Root) — rough sketches only; need full design pass
   (NPC dialogue trees, encounter tables, items, explore events) before implementation.
   Two open questions flagged inline above.

---

## Implementation Status (tracking)

**Done (this implementation pass):**
- Pet renames + new evolution lines (Glimmerva→Luminara→Solarmoth, Serpentine→Serpumbra,
  Glamorose→Malicea→Aberraflora, Verdanthorn) + encounter tables.
- Full NPC pet roster (Vexia/Fen, Linden/Frond, Slithers/Glim, Mira/Petal, Luna/Lunarblossom).
- Luna added (Moonpetal Inn, night shift); Mira split to day-only.
- on_enter embed redesign (`build_on_enter_embed` in `cogs/views/towns.py`) — personalizable
  speaker/icon/color/footer, used for new on_enter entries across 5 Grove locations.
- Explore events + loot tables for `whisperwoodGrove` (Whispering Thicket) and
  `whisperwoodWilds`.

**Flagged for Pass 5+ (OPEN — needs design pass before implementation):**
- `whisperwoods_plea` quest structure — see "whisperwoods_plea — Quest Structure (OPEN/TBD)"
  above. Blockers: how the player finds the Heart of Decay, what "kindness and
  understanding" means mechanically, whether the Weeping Root is the confrontation site.
- Side Story Beat (Luna/Mira dynamic, Fae Whisper ↔ Weeping Root connection,
  Arboreal/Sylven thread) — see "Side Story Beat (OPEN/TBD)" above.
- `DIALOGUES` entries for Vexia, Linden, Slithers, Mira, Luna — `dialogue` dicts exist in
  `data/towns.py` but `_get_dialogue_node` finds nothing in `data/dialogues.py`, so "Talk to
  X" currently falls back to "They have nothing to say to you right now." Intentionally left
  unwired until quest/side-story flags exist to give these NPCs something conditional to say.

**The Ashen Verge — groundwork + NPC pass done:**
- New pets added to `data/pets.py`: Cinderkit→Ashveil, Tindertail (standalone),
  Smolderoot→Pyrethorn, Cindermaw (Ancient standalone), Pyrehart (Ancient standalone).
- New items added to `data/items.py`: `ash_ember` (crafting material), `ember_charm`
  (consumable, restores 15 energy).
- New `ashenVerge` remnant added to `data/remnants.py` — side branch off Whisperwood
  Grove (connection added both ways, cost 10), with 3 locations: Kaelen's Shack,
  Bram & Pip's Caravan, The Ash Circle (`explore_zone: "ashenVerge"`).
- `ENCOUNTER_TABLES["ashenVerge"]` added (day/night, First Ring sightings folded in).
- NPCs added (using the `dialogue: {default: [...]}` inline pattern, same as Vexia/
  Linden/Bea — random-line flavor, no flag/quest branching yet, consistent with how
  those Whisperwood NPCs currently work):
  - **Kaelen** (Kaelen's Shack) — pet "Soot" (Cinderkit). Dialogue covers the lore
    spine (first ring, "fire was the only thing the roots couldn't pretend to be"),
    a hint at The First Ring's buried occupants, and the Serpentine-culling bounty
    flavor line.
  - **Bram & Pip** (Bram & Pip's Caravan) — shared pet Tindertail, nicknamed "Match"
    by Bram and "Wisp" by Pip (unresolved, per design — both nicknames present via
    each NPC's own `pet` entry). Pip's lines hint at "the line is moving" without
    confirming it.
- `on_enter` entries added for all 3 locations (first-visit ambient text, same
  `condition: first_visit` / `flag` / `once` pattern as other zones).
- `EXPLORE_EVENTS["ashenVerge"]` added — 12 events (4 flavor, 2 pet sighting,
  2 hazard, 2 loot bonus, 2 choice) covering the doc's flavor/hazard/loot/choice
  beats, including the "recently relit fire-ring" and "First Ring burial" choice
  events. `ZONE_LOOT_TABLES["ashenVerge"]` added (`ash_ember`, `ember_charm`,
  `trail_morsels`).
- `QUESTS["ashenVerge"]["kaelens_bounty"]` added — repeatable bounty, "Defeat 3
  Serpentine", rewards 80 coins + 1 Ember Charm. Written in the fully-structured
  objective format (`type`/`target`/`required_count`) so `check_quest_progress`
  can track it, unlike `forest_cleanup`'s plain-string objectives.
- **Dialogue-tree wiring fixed**: `RemnantView` now checks `data/dialogues.py`
  first — if an NPC has a `dialogue_tree` there, `_make_talk_callback` routes
  through a new `create_talk_callback`/`_get_dialogue_node` pair (mirroring
  `TownView`'s, added to `RemnantView` in `cogs/views/towns.py`), so
  `grant_quest`/`complete_quest` actions and flag/quest-conditional lines work.
  NPCs without a `dialogue_tree` (Bram, Pip) keep using the simple inline
  `dialogue: {default: [...]}` lookup. Added `kaelen` to `DIALOGUES`: grants
  `kaelens_bounty` on first talk, shows the "bounty active" line while it's
  active, and a rotating thank-you once `quest_kaelens_bounty_completed` is set.
  Kaelen's old inline `dialogue` dict was removed (now redundant).
- **Still pending** (separate pass, lower priority): the "the choosing" side story
  (Tindertail picks who to follow during a hazard), the slow reveal of "the line is
  moving" at higher rank, and re-grant flow for repeatable bounties in general —
  `add_quest` is `ON CONFLICT DO NOTHING`, so once `kaelens_bounty` is completed it
  can't currently be picked up again (same pre-existing limitation as
  `forest_cleanup`; not specific to this remnant).

**The Weeping Root — Pass A (groundwork) done:** see "Implementation status — Pass A
(groundwork) complete" under "The Weeping Root (quest-gated remnant)" above for the full
breakdown (2 new pets, 3 new items, encounter table, 13 explore events + loot table, 5-location
remnant shell with Elowen/Corvin NPC stubs + pets, gated-but-unwired travel connection).
Remnant is correctly unreachable in-game until Pass B/C.

**Remaining, separate design passes (not started, not blocking the above):**
- The Weeping Root — Pass B/C: Elowen/Corvin/Anora dialogue trees, Anora's purify/defeat
  mechanic, the `whisperwoods_plea` Fae Whisper quest-gate wiring, Hollowthorn/Verdanthorn's
  Reflection. Depends on `whisperwoods_plea_quest.md` (still WIP) being finalized.
- Gloom Sickness — State/Type/Mark framework (see section above) — marked NOT FINAL,
  Town 2 era; needs its own design pass before any code (status/mark application, gloom_tick
  wiring in `cogs/adventure.py`, etc.).
