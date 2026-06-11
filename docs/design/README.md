# Aethelgard — Design Docs

This folder is the working collection of world/story design for Aethelgard — brainstorm
output shared between brainstorm sessions, code sessions, and Kyle. It's notes and
scaffolding, not user-facing documentation. Whether/when any of this gets committed is a
separate call — these files exist to keep ideas consistent across sessions, first.

---

## Folder Structure

```
docs/design/
  README.md                  <- this file
  world/                      World-level frameworks — apply across all remnants/towns
    aethelgard_classification.md
    aethelgard_gloom_frames.md
    aethelgard_world_connections.md
  <remnant_name>/             One folder per town/remnant
    <remnant_name>.md          Core design doc (NPCs, pets, locations, lore, items)
    <quest_name>_quest.md      Main story / quest line for that remnant (story-first pass)
    archive/                    Superseded versions of docs in this folder
```

Currently:
- `world/` — classification & rarity system, the Seven Gloom States philosophy/frames,
  and cross-remnant connection threads.
- `oakhaven_outpost/` — tutorial hub. Tagged `-done` (see Conventions).
- `weeping_chasm/`, `mirefields/`, `whisperwood_grove/` — each has a core design doc +
  main quest doc, in active development.

---

## Conventions

- **Story first, mechanics/wiring later.** Quest docs are written as narrative spines
  (beats, branches, NPC side stories) before objective types/quest IDs/dialogue keys are
  finalized. "What Exists in Code Today" sections in each quest doc track the gap.
- **`-done` / `-implemented` suffix** — a filename tag (not a folder) meaning "this
  remnant's design is fully wired in code, no open implementation questions remain."
  Currently only `oakhaven_outpost-done.md`. Untagged = still has open questions/pending
  wiring per that doc's own "Open Questions"/"Implementation Notes" sections.
- **`archive/`** — superseded versions of a doc, kept for history/context. The current
  doc states what it supersedes (e.g. `weeping_chasm_v2.md` supersedes
  `archive/weeping_chasm.md`).
- **`LOCKED` status** (noted at the top of most docs) — the brainstorm/decisions in that
  doc are settled for now. Doesn't mean "never revisit," just "don't re-litigate without a
  reason — build on this."
- **Cross-references** — docs link to each other by filename (e.g.
  `` `whisperwoods_plea_quest.md` ``). These are informal pointers for readers, not
  resolved paths — use folder structure above + filename to locate.
- **Some docs are explicitly "don't edit further"** (e.g. `whisperwood_grove.md` is a
  checkpoint — new lore that touches it goes into newer docs instead, with a note
  cross-referencing back). If a doc says this, respect it; add a new doc or section
  elsewhere rather than editing in place.

---

## Reading Order (suggested, for getting oriented)

1. `world/aethelgard_classification.md` — Classification Tier / Encounter Rarity / Gloom
   States. The shared vocabulary everything else uses.
2. `world/aethelgard_gloom_frames.md` — philosophy/factions pass (work in progress).
3. Per-remnant core doc (e.g. `whisperwood_grove/whisperwood_grove.md`) for that
   remnant's NPCs/lore.
4. Per-remnant quest doc (e.g. `whisperwood_grove/whisperwoods_plea_quest.md`) for the
   story spine built on top of the core doc.
5. `world/aethelgard_world_connections.md` last — ties remnants together once you know
   what's in each.
