# Aethelgard — Next World Segment (Notes, Pre-Brainstorm)

Status: NOTES — captured findings, brainstorm not yet started. Picks up after the
Weeping Chasm / Mirefields / Whisperwood pass + `implementation_roadmap.md`.

---

## What Exists in Code Today

- **Town 3 = Sunstone Oasis** (`data/towns.py`, key `sunstoneOasis`, rank
  "Journeyman", desert flavor — morning/noon/evening/night descriptions written,
  but `locations: {}` and `connections: {'whisperwoodGrove': 'Whisperwood Grove'}`
  only). Equivalent stage to a blank `whisperwood_grove.md` before that pass —
  no NPCs, shop, or lore yet.

- **Between Whisperwood Grove and Sunstone Oasis = "The Glade of Whispers"**
  (`data/remnants.py`, key `glade_of_whispers`, `between: ['whisperwoodGrove',
  'sunstoneOasis']`). More fleshed than other stub remnants (12 keys vs 8 —
  already has a `connections` field). Description sets up a deliberate tonal
  contrast vs. everything else in Aethelgard so far:

  > "A small, perfectly circular glade where sunlight filters through a natural
  > opening in the canopy. The air hums faintly — not with danger, but with
  > something older and calmer. Flowers here bloom year-r[ound]..."

- **Larger map skeleton already sketched** (all placeholder `between` pairs,
  generic names, `availability: all`/`day`, minimal fields — basically an
  overworld graph waiting to be filled in, not relevant yet but good to know
  it exists):
  - `obsidian_monoliths` — between `sunstoneOasis` & `ironforge`
  - `shifting_dunes` — between `sunstoneOasis` & `aethelgardsRest`
  - `lost_guild_hall` — between `frostfallPeak` & `blackwaterMarsh`
  - `sunken_ship_graveyard` — between `aethelgardsRest` & `skylightSpire`
  - `wyrmwood_forest` — between `blackwaterMarsh` & `ironforge` ("The Gloom runs
    deep here")
  - `cloudspire_outpost` — between `skylightSpire` & `silvermoonGlade`
  - `scholars_retreat` — between `silvermoonGlade` & `sunkenCity` (library,
    "collection inside spans centuries of Aethelgard's history")
  - `chasm_of_whispers` — between `ironforge` & `skylightSpire`
  - `forgotten_grove` — between `blackwaterMarsh` & `ironforge` (inside
    Wyrmwood Forest, "miraculously resisted the Gloom")
  - `serpents_coil` — between `sunkenCity` & `dragonsTooth`

  None of these future towns (`ironforge`, `aethelgardsRest`, `blackwaterMarsh`,
  `frostfallPeak`, `skylightSpire`, `silvermoonGlade`, `sunkenCity`,
  `dragonsTooth`) exist in `TOWNS` yet.

---

## Other Loose Threads That Touch This Segment

- **`data/towns.py` comment says "TOWN 3 — Sunstone Oasis (stub, unlocked after
  Verdant Crest)"**. "Verdant Crest" doesn't match any current town name
  (Whisperwood Grove is the actual predecessor). Likely a leftover/older name
  from before the remnant naming settled — flag and resolve (or just update the
  comment) when this segment starts.

- **`data/wandering_npcs.py`** already has a placeholder road entry:
  `"whisperwoodGrove__sunstoneOasis"`, commented "stub — fill in when Town 3 is
  built." Wandering NPCs for this road are part of the Town 3 batch.

- **`utils/constants.py`** — "The Ember Crest" achievement is already written
  and tied to Sunstone Oasis: *"Earned in Sunstone Oasis, it symbolizes an
  Adventurer's ability to master powerful Fire-type companions and endure the
  scorching heat of the desert."* This pins Sunstone Oasis as a **Fire-type
  hub** — useful constraint when designing its pets/NPCs/shop.

- **Forward hooks already planted from Weeping Chasm** point straight at this
  segment — continuity is already half-built:
  - `weeping_chasm/echoes_from_below_quest.md`, Beat 5.5 ("Forward Hook,
    stretch") — Kael's hook points toward "Obsidian Monoliths/Sunstone Oasis."
  - `weeping_chasm/weeping_chasm_v2.md` — reward note: "forward hook to
    Obsidian Monoliths / Sunstone Oasis."
  - `weeping_chasm/archive/weeping_chasm.md` (superseded, but for reference) —
    "Kael disappears from the Chasm. Thread dangles toward Sunstone Oasis."

  When this segment starts, check whether Kael's forward hook (Layer 1a) should
  resolve *into* the Glade of Whispers / Sunstone Oasis story, or stay a
  separate dangling thread for later (Obsidian Monoliths is one stop further,
  between Sunstone Oasis and the not-yet-built `ironforge`).

---

## Suggested Next Step (when we pick this up)

Mirrors the Oakhaven → Whisperwood pattern: **the remnant *between* the current
frontier town and the next town gets a main story first.**

1. **The Glade of Whispers — main story pass** (same story-first approach as
   Weeping Chasm/Mirefields). Bridges Whisperwood Grove → Sunstone Oasis.
2. **Sunstone Oasis — Town 3 core design** (NPCs, shop, locations, lore) — the
   bigger "Whisperwood Grove-sized" pass, after or alongside #1.

### Why Glade of Whispers is an interesting seed

- Its "calm, no danger" framing is a natural place to finally use one of the
  still-unused Gloom Frames from `aethelgard_gloom_frames.md` (Seeker,
  Liberationist, Fatalist) — or even introduce something **not** Gloom-touched
  at all, a real tonal break after every other remnant has been Gloom-inflected.
- Could be a resting point for the "Probably" / Anora thread (Weeping Chasm) —
  a quiet, ambiguous place fits an unresolved "what happened to her" beat.

---

## Cross-References

- `world/implementation_roadmap.md` — current build-order for Layers 1-4
  (Weeping Chasm/Mirefields/Whisperwood). This segment comes *after* that.
- `world/aethelgard_gloom_frames.md` — Seeker/Liberationist/Fatalist frames,
  flagged there as "future remnant" seeds.
- `world/aethelgard_world_connections.md` — "Probably" / Anora thread.
