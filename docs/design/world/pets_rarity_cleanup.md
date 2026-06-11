# Pets — Rarity Field Cleanup (Story Pass → Code Pass Handoff)

Status: LOCKED on intent (per Kyle), implementation not started.

---

## The Model (clarified)

There used to be one "rarity" stat. `aethelgard_classification.md` split it into two
axes: **Classification Tier** (what a creature *is*) and **Encounter Rarity** (how often
it's *seen*, in context).

What actually happened during the recent `classification_tier`/`encounter_rarity`
migration: `classification_tier` was added to every `PET_DATABASE` entry, and
`ENCOUNTER_TABLES` were migrated to per-location `encounter_rarity`. **But the old
per-species `rarity` field (`Starter` / `Common` / `Uncommon` / `Rare` / `Ancient` /
`"Very Rare"`) was left in place alongside it** — so right now every pet carries both an
old-style `rarity` and a new `classification_tier`, and several places in the code still
read the old field. That's the miscommunication this doc is closing:

> **`classification_tier` IS the rarity, for a species.** The old `rarity` field on
> `PET_DATABASE` is to be discarded. "Rarity" as a word now belongs to
> `encounter_rarity` only (per-location sighting frequency, Section 2 of
> `aethelgard_classification.md`).

---

## Confirmed: `rarity` ↔ `classification_tier` Mapping (for reference during removal)

| old `rarity` | `classification_tier` | Count | Notes |
|---|---|---|---|
| Common | Ordinary | 8 | |
| Uncommon | Prime | 16 | |
| Rare | Apex | 11 | |
| Ancient | Elder | 6 | Veilmother, Aberraflora, Verdanthorn, Cindermaw, Pyrehart, Threshbound |
| Starter | Ordinary / Prime / Apex (per evolution stage) | 9 | Pyrelisk/Dewdrop/Terran lines |
| **"Very Rare"** | Elder | 1 | **Mirewarden** — confirmed stale, "Very Rare" isn't used anymore. Once `rarity` is removed this is moot, but if anything reads it before then, treat as `Ancient`. |
| Common | **Apex** | 1 | **Stillroot** — the one real outlier (see below). |

### Stillroot — needs a decision

Stillroot's `classification_tier` was deliberately bumped to `Apex` (so its unique
Stonecrust passive isn't overridden by the shared type-passive pool — see inline comment
in `data/pets.py`), but its old `rarity` stayed `Common`. Once `rarity` is gone, Stillroot
is just `Apex` tier like any other Apex creature — **is that correct**, or was the
"Common-but-mechanically-special" framing meant to persist some other way (e.g. a
specific `encounter_rarity` entry for Stillroot in the `weepingRoot` table — which already
exists and is separately tagged "Rare" per the classification doc's own example)?
Likely fine to just let Stillroot be `Apex` + whatever `encounter_rarity` its table entry
already has — flagging so it's a conscious choice, not a silent side effect.

---

## What Reads the Old `rarity` Field Today

| File | Usage | What replaces it |
|---|---|---|
| `cogs/game.py:17` | `STARTER_PETS_LIST = [pet for pet in PET_DATABASE.values() if pet.get('rarity') == 'Starter']` | **Needs a new mechanism** — `rarity` is the *only* place "this is a starter line" is recorded. Suggest a small `STARTER_SPECIES` list (the 3 species keys: Pyrelisk/Dewdrop/Terran) or an `is_starter: True` flag on those 3 top-level entries only (not their evolutions). |
| `cogs/adventure.py:254` | Legacy fallback: `wild_pet_base['rarity'] in ["Common", "Uncommon"]` for shared-passive-pool decision, only used `if classification_tier is None` | **Dead code** — every pet now has `classification_tier`. Safe to delete the fallback branch (and the `else`). |
| `cogs/adventure.py:279` | Copies `rarity` into the wild pet instance dict | Drop, or copy `classification_tier` instead if instances need it downstream. |
| `cogs/admin.py:136` | Copies `rarity` into a pet instance dict (admin pet-grant tool) | Same as above. |
| `cogs/search.py:62-64,177-178` | `RARITY_EMOJIS` dict (`Starter/Common/Uncommon/Rare/Epic/Legendary`) keyed by `data.get("rarity", "Common")` | Rebuild keyed by `classification_tier` (`Ordinary/Prime/Apex/Elder/Ancient/Primordial/Eternal`). Note `Epic`/`Legendary` were never actual values — drop them. |
| `cogs/views/character.py:374-377` | `rarity_colors` dict (`Starter/Common/Uncommon/Rare/Legendary`) keyed by `pet.rarity` | Same — rebuild keyed by `classification_tier`. This is also where the **Ancient-tier display gap** gets fixed (Veilmother/Verdanthorn/etc. currently fall back to plain grey). |

### Already-dead, unrelated but found during this pass

- `utils/constants.py` — `PET_EVOLUTIONS` (references nonexistent species `"Verdant
  Golem"`) and `XP_REWARD_BY_RARITY` (`Common/Uncommon/Rare/Legendary`) are both fully
  unreferenced anywhere in `cogs/`/`utils/`. Safe to delete as part of the same pass
  (or separately — they're unrelated to the `rarity` field itself, just dead weight in the
  same file family).

---

## Suggested Cleanup Order (for a code session)

1. Add a starter-line marker that doesn't depend on `rarity` (e.g. `STARTER_SPECIES =
   ["Pyrelisk", "Dewdrop", "Terran"]` somewhere central, or `is_starter: True` on those 3
   entries). Update `cogs/game.py:17`.
2. Rebuild `RARITY_EMOJIS` (`cogs/search.py`) and `rarity_colors`
   (`cogs/views/character.py`) keyed on `classification_tier`, covering all 7 tiers
   (Ordinary/Prime/Apex/Elder/Ancient/Primordial/Eternal — even if Primordial/Eternal have
   no pets yet, define a fallback so future additions don't silently render wrong).
3. Remove `rarity` from every `PET_DATABASE` entry (base + evolutions).
4. Remove the dead legacy-fallback branch in `cogs/adventure.py` (`use_shared_passive`
   `else` arm) and the `rarity` copies in `cogs/adventure.py`/`cogs/admin.py` instance
   dicts.
5. Delete `PET_EVOLUTIONS` and `XP_REWARD_BY_RARITY` from `utils/constants.py`.
6. Resolve Stillroot per the decision above (likely: no special-case needed, just confirm).

---

## Cross-References

- `world/aethelgard_classification.md` — Section 1 (Classification Tier) and Section 2
  (Encounter Rarity, updated alongside this doc to reflect the actual implemented
  `Normal/Odd/Rare/Peculiar/Strange/Uncanny/Unknown` scale).
- `data/classifications.py` — `CLASSIFICATION_TIERS`, `ENCOUNTER_RARITIES`,
  `ENCOUNTER_RARITY_WEIGHTS`.
- `data/pets.py` — `PET_DATABASE`, `ENCOUNTER_TABLES`.
