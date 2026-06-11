# Aethelgard — Creature Classification & Encounter Rarity

**Status:** LOCKED (brainstorm session, no code changes yet)

This is a world-level framework, not specific to any one town/remnant. It was born out of
the Whisperwood Grove design pass (see `whisperwood_grove.md`), specifically while figuring
out where Sylven Heartwood, Verdanthorn, and Hollowthorn sit relative to each other — but it's
meant to apply everywhere in Aethelgard, going forward.

It introduces **two separate axes** that were previously conflated into one "rarity" stat:

1. **Classification Tier** — what a creature fundamentally *is* (its place in the world's
   power/significance hierarchy).
2. **Encounter Rarity** — how often a creature is actually *seen/caught*, independent of its
   classification.

A creature's classification tier is mostly fixed (a species is what it is). Its encounter
rarity can vary by context, region, or individual — and that variance is itself a storytelling
tool.

---

## 1. Classification Tier

Ordinary → Prime → Apex → **Elder** → **Ancient** → Primordial → Eternal

| Tier | What it represents | Example(s) |
|---|---|---|
| Ordinary | Everyday wildlife. The baseline of the world. | Mossling, Sunmoth, most starter-line species |
| Prime | A step above ordinary — more capable, still common enough to encounter regularly. | Mid-evolution-line species |
| Apex | The "top of the food chain" for a given habitat — strong, but still part of the normal ecosystem. | Late-evolution-line species, strong standalones |
| **Elder** | A creature that *embodies* a quality of its territory — not just strong, but a living expression of something about the place. Neutral term: an Elder can embody growth, decay, memory, etc. — good or ill is not implied by the tier itself. | Verdanthorn (Whisperwood's living guardian presence), Hollowthorn (Whisperwood's corrupted mirror/"balance-break" entity) |
| **Ancient** | A being a territory is *built around* — foundational to that region's identity, history, and balance. Effectively one-per-major-territory. | Sylven Heartwood (Whisperwood) |
| Primordial | Reserved / unused so far. A being whose significance extends beyond a single territory — possibly tied to Aethelgard-wide forces (the Gloom's origin point, etc.). No confirmed example yet. | — |
| Eternal | Reserved / unused so far. The theoretical ceiling — something that predates or transcends current territorial structures entirely. No confirmed example yet. | — |

**Notes:**
- Elder tier is explicitly **dual-natured by design** — Verdanthorn and Hollowthorn are both
  Elders of Whisperwood, one expressing the territory's health and the other its wound. Future
  territories may or may not have both halves of an Elder pair; that's a per-region story
  choice, not a rule.
- **Observed Elder pairs:** Whisperwood actually has *two* such pairs, at different sites and
  ages of the same underlying wound (see `whisperwoods_plea_quest.md` "Lore Update — Unified
  Origin"): **Pyrehart/Cindermaw** (Ashen Verge — old, wounded, mostly dormant) and
  **Verdanthorn/Hollowthorn** (Weeping Root — current, active). Same kind of phenomenon,
  different stages — a useful template for how Elder pairs can recur across a single
  territory's history, not just once per territory.
- Primordial/Eternal are intentionally left open. Given Oakhaven Outpost's hints that the
  Rotting Pits and Weeping Chasm "share a Gloom source — same breach, different surface
  points," the Chasm itself (or whatever lives at its source) is a strong candidate for a
  future Primordial/Eternal-tier entity — but this is *not* committed to anything yet.

---

## 2. Encounter Rarity

Common → Uncommon → Rare → (further tiers TBD as needed)

This is the **familiar rarity language**, but it now describes *sighting frequency*, not
power level. It's the term Guilds, NPCs, and players would actually use day-to-day —
"there's a rare sighting of an ordinary pet out near the Thicket" is a complete, useful
sentence that doesn't require the listener to know anything about Classification Tiers.

**Why this split matters:**
- A creature's Classification Tier rarely changes. Its Encounter Rarity can shift based on
  context — and *that shift is itself information* the world can react to.
- Concrete example (already built, retroactively explained by this framework): a
  Withering-Marked Mossling is still **Ordinary** tier — it's a Mossling. But seeing one in
  that state is a **Rare** sighting, and an attentive Guild member would flag it as such.
  The Mark changed how often it's *seen looking like that*, not what it fundamentally *is*.
- This also explains things like Stillroot being listed as a "Rare" encounter in the Weeping
  Root despite being a relatively Ordinary/Apex-level creature conceptually — the Calcifying
  Mark is what makes it a rare sighting, not its baseline classification.

---

## Open / Future Work

- No code changes yet — this is conceptual scaffolding for future design passes.
- Primordial/Eternal tiers remain unassigned. Don't force an example into existence just to
  fill the table.
- Future town/remnant docs should reference this file rather than re-deriving rarity
  language locally.
- Possible future pass: formalize how Encounter Rarity interacts with capture mechanics
  (does a "Rare sighting" of an Ordinary pet have different catch-rate odds than a baseline
  Ordinary encounter? Not decided.)
