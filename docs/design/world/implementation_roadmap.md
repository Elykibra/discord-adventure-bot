# Aethelgard — Implementation Roadmap (Design → Code Layering)

Status: WIP reference. This is a suggested *order*, not a gate — design docs
remain the source of truth, this just sequences "what to wire next" so batches
build on top of each other instead of crossing wires.

---

## Layer 0 — Already Done

- `oakhaven_outpost/oakhaven_outpost-done.md` — tutorial hub, fully wired.
  `a_guildsmans_first_steps` → `head_to_whisperwood` assignment.

---

## Layer 1 — Per-Remnant Main Stories (geography order)

Each is mostly self-contained — wires one remnant's quest line using NPCs/
locations already described in that remnant's core doc. Suggested order
follows the travel route (`Oakhaven → Weeping Chasm → Mirefields →
Whisperwood`), since that's the order a new player encounters them, even
though none of these are hard-gated.

1. **Weeping Chasm — `echoes_from_below`**
   (`weeping_chasm/echoes_from_below_quest.md` + `weeping_chasm/weeping_chasm_v2.md`)
   - Small prerequisite touch: add Galen's one new handoff line in Oakhaven
     (quoted in the quest doc) — doesn't change Oakhaven's `-done` quest
     structure, just adds a dialogue line.
   - New quest: Kael as giver/resolver, 6 beats + 4 stretch beats →
     objectives (talk_npc/travel/item_pickup/combat per the beat list).
   - Reward: lore-only per current draft (open question in doc).

2. **Mirefields — "Readings from the Edge"**
   (`mirefields/mirefields_main_quest.md` + `mirefields/mirefields.md`)
   - Folds existing "Ferryn's Fetch" stub + Old Crossroads ledger Choice
     Event into one optional `side`-type quest.
   - Sable/Ferryn dialogue already exists in `mirefields.md` — mostly
     quest-wrapper + a couple of new lines (Beat 4.5 conditional dialogue).

3. **Whisperwood Grove — `whisperwoods_plea`**
   (`whisperwood_grove/whisperwoods_plea_quest.md` + `whisperwood_grove/whisperwood_grove.md`)
   - Largest of the three — bigger cast, has the one *real* hard gate
     (`whisperwoods_plea_weeping_root_unlocked` for `weepingRoot` connection
     in `data/towns.py`, currently unwired).
   - Natural last in Layer 1 since it's the heaviest lift and the gate only
     matters once this is live.

---

## Layer 2 — Branches / Side Quests (per remnant, optional)

These ride on top of Layer 1's NPCs and locations — easiest to wire
immediately after (or alongside) each remnant's main story while that
remnant's context is fresh, but nothing breaks if they slip to a later pass.

- **Weeping Chasm**: Branch 1 "The Sealed Journal" (Kael), Branch 2 "What
  Spun That" (Veilmother/Orin), Branch 3 "Held at the Threshold" (Gretta),
  Branch 4 "Orin's Posting" (affinity).
- **Mirefields**: Branch 1 "The One Who Stayed" (Sable), Branch 2 "Probably"
  (Ferryn, seasonal), Branch 3 "The Crossroads Trade" (one dialogue line,
  no quest wrapper).
- **Whisperwood**: per `whisperwoods_plea_quest.md` NPC mapping (larger set,
  not detailed here).

---

## Layer 3 — Cross-Remnant Connections

(`world/aethelgard_world_connections.md`)

Each connection thread touches dialogue/lore in **two** remnants — wire these
*after* both endpoints' Layer 1 (and ideally Layer 2, where the thread lives
in a branch) are done, so the "answering" side has something to answer.

Suggested order, by readiness once Layer 1/2 land in the order above:

1. **"The Sealed Journal" → "The Threnody Correspondence"** (Weeping Chasm
   Branch 1 ↔ Whisperwood's Linden capstone) — both sides depend on
   Whisperwood being live, so this is naturally last among the three Weeping
   Chasm/Whisperwood threads.
2. **"The Long Memory"** (Weeping Chasm Branch 3 / Gretta ↔ Weeping Root's
   Corvin) — same dependency (Weeping Root content).
3. **"Probably"** (Mirefields Branch 2 / Ferryn ↔ Weeping Chasm's
   `lore_gloom_origin`) — both sides ready once Layers 1 for Weeping Chasm
   and Mirefields are done; doesn't need Whisperwood. Could move earlier.
4. **"What the Ledger Knew"** (Mirefields' `waystation_ledger` ↔ Whisperwood)
   — needs Whisperwood live.
5. **"The Crossroads Trade"** (Ashen Verge's Bram & Pip ↔ Mirefields' Sable)
   — both already-implemented remnants; could be done any time, low
   priority/low effort (dialogue-only on both sides).
6. **"The Mid-Sentence Motif"** — not a quest, just a stylistic consistency
   note (how "the record stops" reads across Kael/Mirefields' ledger);
   apply opportunistically while writing the above, not its own batch.

---

## Layer 4 — World Reference Data (flavor/lore, no urgency)

- `world/aethelgard_classification.md` — already partially in
  `data/classifications.py` as reference data (not wired into game logic).
- `world/aethelgard_gloom_frames.md` — philosophy/frames brainstorm. Not a
  quest-implementation target; pull from this *as* Layers 1-3 are written
  (e.g. "does this NPC's reaction match a Frame we've defined?"), and treat
  gaps (Seeker/Liberationist/Fatalist frames) as seeds for *future* remnants,
  not retrofits.

---

## Quick-Reference Table

| Layer | What | Depends on | Player-facing gate? |
|---|---|---|---|
| 0 | Oakhaven Outpost | — | Yes (only hard gate before Weeping Chasm) |
| 1a | Weeping Chasm main (`echoes_from_below`) | Layer 0 (1-line dialogue add) | No |
| 1b | Mirefields main (`Readings from the Edge`) | Layer 1a not required | No |
| 1c | Whisperwood main (`whisperwoods_plea`) | Layer 1a/1b not required | Partial (`weepingRoot` gate) |
| 2 | Branches/side quests per remnant | That remnant's Layer 1 | No |
| 3 | Cross-remnant connections | Both endpoints' Layer 1 (+2 where thread lives in a branch) | No |
| 4 | World reference docs (classification, frames) | Ongoing reference, not a build target | No |

---

## Cross-References

- `weeping_chasm/echoes_from_below_quest.md`
- `mirefields/mirefields_main_quest.md`
- `whisperwood_grove/whisperwoods_plea_quest.md`
- `world/aethelgard_world_connections.md`
- `world/aethelgard_gloom_frames.md`
- `world/aethelgard_classification.md`
