# Mirefields — Main Story (Story Pass)

**Status:** LOCKED (brainstorm session, no code changes yet)

Same approach as `echoes_from_below_quest.md` and `whisperwoods_plea_quest.md`: **story
first, mechanics/wiring later.** This is Mirefields' main story — the second stop on the
Oakhaven → Weeping Chasm → Mirefields → Whisperwood road.

---

## What Exists in Code/Docs Today

- `mirefields.md` — full design doc. Sable (NPC, shop, dialogue) and Ferryn (seasonal NPC)
  both fully written. Old Crossroads = environmental lore + standalone Choice Event
  (`waystation_ledger`). "Ferryn's Fetch" quest stubbed (retrieve `ferryn_equipment` near
  the crossroads boundary, return to Ferryn) — currently a simple two-step fetch, not yet
  connected to the Old Crossroads beat.
- `data/towns.py` / `mirefields.md` "UI Layout" — **no travel gate either direction.**
  Back to Weeping Chasm always open; forward to Whisperwood Grove is "open road" with no
  requirement. This is intentional and should stay that way — see Framing below.
- Currently *not* connected: Ferryn's Fetch and the Old Crossroads ledger are two separate
  pieces of content that happen to be near each other geographically but don't reference
  each other.

---

## Framing — "The Place That Let Go"

Mirefields is explicitly the odd one out so far: `gloom_level: 8`, "the danger here is
physical, not supernatural," Siltborn/Mirewarden are **not** Gloom-touched — "the mire's
wrongness is ancient and organic." Whisperwood and Weeping Chasm are both, in different
ways, stories about *escalating* wrongness and a search for understanding. Mirefields
isn't that, and shouldn't try to be.

**The story here is smaller and more human-scale on purpose:** a place that used to matter,
and the two people who stayed after everyone else left — for opposite reasons (Sable wants
it to stay forgotten; Ferryn wants to understand why it's changing). The "main story" is
really about **the player walking into that disagreement**, briefly, without needing to
resolve it.

This also means:
- **No travel gate.** Unlike `echoes_from_below` (which required a quest-flag to unlock
  Weeping Chasm's connection), Mirefields' road stays open in both directions regardless of
  whether the player engages with any of this. "The mire won, but the road's still here if
  you want to use it" — apt for a place defined by indifference, not danger.
- **The Deep Mire / Mirewarden / "Probably" threads (per `mirefields.md`'s "Lore Thread —
  The Deep Mire" and `aethelgard_world_connections.md`'s "Probably") stay exactly as
  ambiguous as they currently are.** This story pass should *touch* that ambiguity (the
  player gets close enough to feel the Mirewarden's territory, per the existing "tense, not
  dangerous" design) without resolving anything. Same "no solution yet" discipline as the
  other two remnants, just with lower stakes.

---

## Quest Structure Note

Given no travel gate, the main story here is best framed as an **optional `side`-type
quest** (per `data/quests.py`'s type vocabulary: "Optional NPC quest, completable anytime")
rather than an `assignment` or `main` quest. It still gets full objectives in the quest tab
for players who pick it up — it just never blocks anything if ignored.

**Proposed unification:** fold the existing "Ferryn's Fetch" stub and the standalone Old
Crossroads ledger Choice Event into **one quest arc** — they're a few minutes' walk from
each other and thematically the same beat (both involve getting close to the Mirewarden's
territory). Working title: **"Readings from the Edge"** (placeholder, easy to rename).

---

## Story Spine (Beats)

- **Beat 1 — Sable's Camp.** Arrival. Existing `default`/`night` dialogue and shop. First
  impression of Mirefields: economical, indifferent, *fine*. Nothing needs fixing here —
  that's the point.

- **Beat 1.5 — The Trail Markers (stretch).** Existing flavor event: Sable's knotted-reed
  trail markers are the only reliable guide through the mire. A small, wordless
  characterization beat — she maintains this for travelers she's not particularly
  interested in meeting. Nobody asked her to. She just does.

- **Beat 2 — The Reed Hollow / Ferryn.** Meet Ferryn (if in season). Her enthusiasm,
  `lore_expansion`, `about_sable` — the tension between the two of them surfaces naturally,
  without the player needing to take a side.

- **Beat 2.5 — Silt's Unease (stretch).** Small observational beat, drawn from existing
  Ferryn lore: Silt (her Pallefin) reacts to certain water near the expanding sections —
  refuses to enter, gets agitated near the crossroads area. Ferryn's noted it, hasn't
  concluded anything. Plant, don't explain.

- **Beat 3 — Ferryn's Request (existing "Ferryn's Fetch").** Retrieve `ferryn_equipment`
  near the crossroads boundary — "tense, not dangerous," per existing design. First brush
  with Mirewarden territory: the player feels it without seeing it.

- **Beat 3.5 — The Readings (stretch).** Return the gauge. Ferryn's `quest_complete`
  reaction — the readings near that area are "unlike anything else in the mire." She files
  it and moves on, same restraint Kael showed post-Chasmbane in `echoes_from_below`. Small
  but deliberate echo between the two remnants' scholars.

- **Beat 4 — The Old Crossroads (Climax, such as it is).** The existing Choice Event:
  overgrown foundations, the illegible signpost, fresh territorial signs, the sealed
  ledger. "Take the ledger" / "Step back" — exactly as currently designed. This is the
  closest the player gets to the Mirewarden, and the design intent (unease, not combat)
  stays unchanged.

- **Beat 4.5 — Showing Sable (stretch, conditional on taking the ledger).** New small
  beat: bring the `waystation_ledger` to Sable. She doesn't need to read it — she already
  knows what it'll say. `lore_crossroads`-adjacent reaction: *"Figured something like that
  was still down there. Didn't go looking."* Not dismissive — just confirms she's known
  about that section longer than the player has, and chose not to engage with it, same as
  she's chosen not to engage with Ferryn's research. Reinforces her character without new
  plot.

- **Beat 5 — The Road Continues.** No formal "coda" turn-in needed beyond Beat 3.5/4.5 —
  the quest can simply complete on returning the gauge (Beat 3.5), with the Old Crossroads
  beat (4/4.5) as connected-but-optional bonus content for players who want to go further.
  Either way, the player continues toward Whisperwood at their own pace. Open road, as
  designed.

---

## Objective Mapping Notes (for future mechanics pass)

| Beat | Likely objective type(s) |
|---|---|
| 1 | `talk_npc` → Sable (optional, flavor) |
| 1.5 | none — pure flavor event |
| 2 | `talk_npc` → Ferryn (quest start, if in season) |
| 2.5 | none — pure flavor/dialogue |
| 3 | `item_pickup` → `ferryn_equipment`, `zone: mirefields` (quest-only Choice Event, existing) |
| 3.5 | `talk_npc` → Ferryn (turn in gauge) — **quest may complete here** |
| 4 | optional — Old Crossroads Choice Event, `item_pickup` → `waystation_ledger` if taken (not currently quest-gated; could remain free-standing OR become an optional bonus objective) |
| 4.5 | optional — `talk_npc` → Sable, only if `waystation_ledger` in inventory |
| 5 | none — no turn-in, just onward travel |

**Key design question carried into Open Questions:** should Beat 4 (the ledger) be part of
this quest's objectives at all, or stay a fully free-standing Choice Event that *happens*
to sit near Beat 3's location? Leaning toward: **keep it free-standing**, but add Beat 4.5
(Sable reaction) as a small bonus dialogue branch that fires *if* the player has the ledger,
regardless of quest state. Keeps the "open, optional, low-pressure" feel intact.

---

## Branches — Side Stories (rough sketches)

Same as `echoes_from_below_quest.md`: **purely optional**, none gate the (already
gate-free) road. With only two NPCs, this is short — and that's fine.

### Branch 1 — "The One Who Stayed" (Sable, affinity-based)

- Affinity-unlocked, gradual, same pattern as Whisperwood/Weeping Chasm's affinity NPCs.
- **The shape of it:** deepens what's already in `mirefields.md` — growing up on the edge
  of the mire when the crossroads was active, learning it "the way you learn a language
  when you're a child," and the quiet realization after the waystation collapsed that the
  emptied-out version of this place was the one she'd actually wanted all along.
- **Tone:** no tragedy, no reveal. Just Sable, in her economical way, confirming what the
  player has probably already pieced together by Beat 1.5 (the trail markers) — she didn't
  stay out of stubbornness or grief. She stayed because everyone else leaving solved a
  problem she'd had her whole life.
- **Possible late beat:** if the player has built enough affinity *and* brought her the
  `waystation_ledger` (Beat 4.5), one additional line becomes available — she recognizes a
  name or route in the ledger from her childhood. Doesn't react visibly. Just: *"Huh."*
  Doesn't elaborate. (Optional connection to "What the Ledger Knew" — see below.)
- **Reward:** none — pure characterization.

### Branch 2 — "Probably" (Ferryn, seasonal arc)

- Uses the seasonal mechanic already designed in `mirefields.md` — no new system needed.
- **In-season (Before):** Beats 2/2.5/3/3.5 as written in the main spine — Ferryn's
  optimism, Silt's unease, the gauge retrieval, her restrained-but-intrigued reaction to
  the readings.
- **Off-season / "she's gone" (During → After):** per existing design, the Reed Hollow is
  empty when the player returns at higher rank, except for her field notes left on the
  post. This branch's addition: the notes' final entry — the one that "reads like she got
  closer to the crossroads than she told Sable she would" — should specifically reference
  **the readings from Beat 3.5** as the reason she went back. Not a cliffhanger sequence,
  just one consistent thread: the gauge readings near the crossroads were "unlike anything
  else in the mire," and that's exactly the kind of thing Ferryn wouldn't be able to leave
  alone.
- **This is the direct payoff of "Probably"** in `aethelgard_world_connections.md` — the
  structural echo to Anora (researcher gets close to something Gloom-adjacent-or-not, goes
  further than told, doesn't come back, fate left ambiguous). For a player who's done
  `whisperwoods_plea` first, finding Ferryn's notes should land with quiet recognition —
  *I've seen this shape before.* For a player who hasn't, it's just an unresolved local
  mystery, which is fine — same order-independence approach as `echoes_from_below`.
- **Reward:** none — this is the emotional/connective payoff, not a mechanical one.

### Branch 3 — "The Crossroads Trade" (connection only, Ashen Verge)

- Not a Mirefields NPC story — this is the Mirefields-side half of "The Crossroads Trade"
  from `aethelgard_world_connections.md` (Bram & Pip, Ashen Verge).
- **Implementation:** a small addition to Sable's existing `lore_crossroads` dialogue —
  when describing the crossroads' busy days, she can mention the kind of traders who came
  through: *"Salvagers, mostly, this end. People who picked through old ruins further out
  and brought it here to sell on."* Doesn't name Bram & Pip — just establishes that the
  *kind* of trade Bram & Pip do today is the same kind that used to flow through here.
- **Payoff sits on the Ashen Verge side** (Bram/Pip's affinity line about the crossroads
  drying up, per the connections doc) — this branch is just the matching half-sentence on
  the Mirefields end, so neither side needs the other to make sense, but together they
  quietly confirm the same economic history from two unconnected NPCs.
- **Reward:** none — pure world-texture.

---

## NPC Personal Side Stories — Mapping

| NPC | Personal side story |
|---|---|
| Sable | Branch 1 — "The One Who Stayed" |
| Ferryn | Branch 2 — "Probably" |

(Branch 3 is a connection-only addition to Sable's existing dialogue, not a separate
personal story.)

---

## Open Questions

1. Quest type/name — "Readings from the Edge" is a placeholder. Could also just keep
   "Ferryn's Fetch" as the formal quest and treat Beats 4/4.5 as unrelated bonus content
   (per the leaning above) — in which case this doc is really "Ferryn's Fetch, expanded
   with surrounding flavor beats" rather than a brand-new quest.
2. Reward for the gauge-retrieval — original stub said TBD + "Ferryn's expansion lore
   dialogue unlocks fully." Suggest keeping it lore-only, consistent with
   `echoes_from_below`'s "this is about information, not loot" precedent.
3. Branches/side stories (Sable's deeper history, the Sable/Ferryn dynamic over time,
   "The Crossroads Trade" connection to Ashen Verge, "Probably"/Ferryn's departure) —
   not started yet. Next pass.
4. Should there be any small connective nod *from* Weeping Chasm (Kael or Gretta
   mentioning the mire ahead) the way Galen's line seeds `echoes_from_below`? Leaning:
   not necessary — Mirefields doesn't need a "tutorial exit" moment the way Oakhaven did,
   and the open-road design already signals "just pass through if you want."

---

## Cross-References

- `mirefields.md` — full design doc (NPCs, pets, items, explore events, Old Crossroads,
  Lore Thread — The Deep Mire).
- `echoes_from_below_quest.md` — structural precedent (story spine + stretch beats +
  objective mapping), Kael's restraint as a model for Ferryn's `quest_complete` beat.
- `aethelgard_world_connections.md` — "Probably" (Ferryn ↔ Anora structural echo), "What
  the Ledger Knew" (Whisperwood ↔ Mirefields, `waystation_ledger`), "The Crossroads Trade"
  (Ashen Verge ↔ Mirefields, Bram & Pip).
- `aethelgard_classification.md` — relevant by *contrast*: Siltborn/Mirewarden are
  explicitly outside this framework (not Gloom-touched).
