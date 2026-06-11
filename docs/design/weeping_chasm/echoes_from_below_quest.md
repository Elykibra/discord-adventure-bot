# echoes_from_below — Quest Line (Story Pass)

**Status:** LOCKED (brainstorm session, no code changes yet)

Same approach as `whisperwoods_plea_quest.md`: **story first, mechanics/wiring later.**
This is Weeping Chasm's main story — the "first stop after Oakhaven." It also exists to
make Aethelgard feel connected: see `aethelgard_world_connections.md` for the cross-remnant
threads this sets up ("The Threnody Correspondence," "The Long Memory").

---

## What Exists in Code Today

- `data/towns.py` — Oakhaven's `connections` include `weeping_chasm`, gated by
  `connection_requirements: { "weeping_chasm": "quest_a_guildsmans_first_steps_completed" }`.
  Comment in code confirms the intended route: **Oakhaven → Weeping Chasm → Mirefields →
  Whisperwood.**
- `data/quests.py` — `a_guildsmans_first_steps` (main quest, Oakhaven) auto-grants
  `head_to_whisperwood` (assignment: "Travel to Whisperwood Grove") on completion. Both are
  fully implemented.
- `weeping_chasm_v2.md` — `echoes_from_below` exists only as a rough stub: "Giver: Elder
  Vexia (Oakhaven Outpost)... reward TBD... forward hook to Obsidian Monoliths/Sunstone
  Oasis." Written before Whisperwood Grove existed — Vexia is actually in Whisperwood, not
  Oakhaven, so this stub needs reframing (see below).
- `weeping_chasm_v2.md` — Kael already has a `required_quest` gate wired in code (data
  not yet written). Orin, Kael, Gretta all have base dialogue implemented.
- `docs/design/oakhaven_outpost/oakhaven_outpost-done.md` — Galen's Vigil: Galen suspects "the Rotting Pits
  and the Weeping Chasm share a Gloom source — same breach, different surface points," but
  doesn't file reports. Lore-only, no quest wrapper currently.

---

## Reframe — Giver & The Oakhaven Handoff

**Old plan:** Vexia (Oakhaven) gives the quest, sends player to Weeping Chasm, player
returns to Vexia. Doesn't work — Vexia's in Whisperwood, and it creates an awkward
backtrack right at the moment the player is supposed to be heading *forward*.

**New plan:**
- **`echoes_from_below` is given on-site by Lore-Keeper Kael**, at the Scholar's Camp,
  Weeping Chasm — the first NPC with anything substantial to say once the player leaves
  Oakhaven. No round trip needed. The quest resolves entirely within Weeping Chasm
  (return to Kael, not to anyone in Oakhaven).
- **The Oakhaven Handoff** is a single added dialogue line, not a new objective — flavor
  only, attached to the completion of `a_guildsmans_first_steps` (or `head_to_whisperwood`'s
  flavor text). Spoken by **Grit Galen**, since he's the one with the Gloom-source theory:

  > *"The road to Whisperwood runs through the Weeping Chasm first. Guild keeps a scholar
  > out there — Kael. Good man, bit obsessive. He's been cataloguing things out there for
  > years. If the Pits and the Chasm really do share a source like I think... he's the one
  > who'd want to know what you've seen here."*

  This does three things at once: hands the player forward naturally, gives Galen's
  unfiled theory somewhere to *go* (without Galen ever leaving Oakhaven), and gives Kael a
  reason to be receptive to the player immediately — he's expecting someone, in a sense,
  even if not literally.

- **Net result:** Oakhaven stays "done" — no new objectives added there, no quest reopened.
  Just one new line of dialogue on an already-completed quest's tail end.

---

## Lore Update — The Chasm as a Wider Question

`Kael's `lore_gloom_origin` (his theory: "the Chasm" as a singular Gloom breach point,
rooted in collective grief) sits in tension with Whisperwood's **Unified Origin** (one
organism, two surface points, grown from Sylven's roots — see `whisperwoods_plea_quest.md`).
Both can't be the *whole* picture, and `echoes_from_below` doesn't need to resolve that —
in fact it shouldn't, yet.

**Framing:** a player who's finished `whisperwoods_plea` already feels like they understand
the shape of "the problem." `echoes_from_below` is where that shape gets **wider, not
clearer**. Maybe Kael's "single breach" theory isn't wrong — maybe the Chasm is older and
deeper than the Whisperwood situation, and what happened at Whisperwood is something that
*grew out of* a connection the Chasm still has. This lines up with
`aethelgard_classification.md`'s note that the Chasm is "a strong candidate for a future
Primordial/Eternal-tier entity" — bigger than any single Elder pair.

Same spirit as the Unified Origin: **nobody to blame, no solution yet, just a wider view.**
This sets up future arcs (Mirefields' Deep Mire, eventual Primordial/Eternal reveals)
without committing to any of them now.

**Order independence note:** Some players may reach Weeping Chasm having *not yet* done
Whisperwood's plea (it's earlier on the route). That's fine — `echoes_from_below` stands on
its own without referencing Whisperwood by name. The "widening" framing only *lands harder*
in retrospect for players who do both, in either order. Nothing here should require
`whisperwoods_plea` as a prerequisite.

---

## Story Spine (Beats)

- **Beat 1 — Arrival at the Chasm's Edge.** Player arrives via the Oakhaven→Chasm route
  (Galen's handoff line already primed them for Kael). First atmosphere beat: the cold,
  the slow exhale-rhythm from below, Warden Orin's quiet vigilance at the Edge.

- **Beat 1.5 — The Tally Marks (stretch).** The cracked Guild marker post with 37 scratched
  tally marks (already an existing flavor event). Small optional beat: ask Orin about it —
  he doesn't know either. Plants "nobody's been counting on purpose, but somebody's been
  counting" without explanation.

- **Beat 2 — Kael, Scholar's Camp.** Quest given here (reframed giver). Kael explains the
  samples task, but also — almost as an aside — his `lore_hollowed_vs_corrupted`
  distinction. Sets vocabulary the way Elowen/Corvin did for Whisperwood, but from a
  scholar's remove rather than personal grief.

- **Beat 2.5 — Threnody (stretch).** A quiet character beat: Kael's Duskspinner,
  "Threnody." If asked, Kael explains the name (a funeral song, referencing the Gloom's
  origin in collective sorrow) — existing dialogue hook. Establishes Kael as someone who's
  been quietly carrying this question for a long time, before anything's gone wrong yet.

- **Beat 3 — The East Wall / Collecting Samples.** Chasm's Edge explore proper — hazard
  events, the Veilmother webbing sighting (existing Pet Sighting event). Orin's
  `lore_east_wall` line lands here ("something large made that overnight, I don't go near
  it").

- **Beat 3.5 — Gretta's Hollow (stretch).** Visit Gretta's camp. The Threshling is *seen*,
  not explained — Gretta's philosophy ("It isn't [named]"). A quiet, unsettling character
  beat before the climax. (This is also the seed for "The Long Memory" — see
  `aethelgard_world_connections.md`.)

- **Beat 4 — The Breathing (Climax).** Samples collected, but the Chasm reacts — the
  **Chasmbane scare encounter** (per the rank-gated design in `weeping_chasm_v2.md`):
  Gloom Meter spike, forced retreat, no battle UI. Not a fight to win — a moment to survive
  and walk away from, recontextualizing every hint since Beat 1.

- **Beat 4.5 — The Quiet After (stretch).** Back at Scholar's Camp, shaken. Kael doesn't
  have words either — possibly the first time the player sees him *not* immediately reach
  for a theory. Mirrors Whisperwood's "Quiet After" beats.

- **Beat 5 — Return to Kael, the Theory Widens.** Samples delivered. `lore_gloom_origin`
  delivered properly here, with the "widening" framing from the Lore Update above.

- **Beat 5.5 — Forward Hook (stretch).** Kael's forward hook to Obsidian Monoliths/Sunstone
  Oasis (per existing stub) — kept light, a "there's more out there" beat rather than a
  hard quest chain commitment.

- **Beat 6 — Coda.** Quest closes at Weeping Chasm itself — no Oakhaven or Whisperwood
  return trip required. Player continues forward toward Mirefields/Whisperwood at their
  own pace, quest fully resolved.

This is 6 numbered beats + 4 stretch beats — slightly leaner than Whisperwood's 11, which
fits: this is a tutorial-adjacent "first taste of the open world," not a town's full plea
quest.

---

## Objective Mapping Notes (for future mechanics pass)

Following `a_guildsmans_first_steps` / `head_to_whisperwood` conventions, each beat above
should map to a quest-tab objective using existing types:

| Beat | Likely objective type(s) |
|---|---|
| 1 | `talk_npc` → Orin (arrival flavor, optional) |
| 1.5 | optional, may not need an objective — pure flavor/Choice Event |
| 2 | `talk_npc` → Kael (quest start) |
| 2.5 | optional flavor, no objective needed |
| 3 | `item_pickup` → `gloom_mist_sample` x3, `zone: weeping_chasm` (Chasm's Edge) |
| 3.5 | optional, `talk_npc` → Gretta (flavor, not required) |
| 4 | scare encounter — likely needs a new objective type or a flag-based trigger;
    flag for implementation review (same as the rank-gating tag already in
    `weeping_chasm_v2.md`) |
| 4.5 | optional flavor |
| 5 | `talk_npc` → Kael (turn in samples) |
| 5.5 | dialogue-only, no objective |
| 6 | none — quest completes on Beat 5's turn-in |

This keeps the "don't get lost" guarantee — every required step has a visible objective —
while letting the stretch beats stay purely textual, same balance as Whisperwood's.

---

## Branches — Side Quests & Side Stories (rough sketches)

All of the below are **purely optional** — none gate `echoes_from_below`'s completion or
the player's onward journey toward Mirefields/Whisperwood. They exist for players who
linger, the way Whisperwood's branches did. Same Before/During/After stretch structure
where it fits.

### Branch 1 — "The Sealed Journal" (feeds The Threnody Correspondence)

- **Before:** During Beat 3 (Chasm's Edge explore), the existing Choice Event — a sealed
  Guild journal wedged near the Tainted Ledge — fires. "Pry it open" gives `lore_fragment`
  (minor Gloom-meter risk, per existing design). Player may or may not take it.
- **During:** If the player has `lore_fragment` and talks to Kael (any time after Beat 2),
  new dialogue: Kael recognizes the handwriting immediately — it's his own, from years ago.
  It's a copy of a letter he sent to "an archivist in Whisperwood" (Linden, unnamed at this
  point) asking whether anyone had records of Guild scouts who went missing near
  Gloom-sources and were later "accounted for, but changed." He never got a real answer.
- **After:** Kael asks the player, almost offhand, to mention it if they ever pass through
  Whisperwood and meet "whoever keeps the records there now." No quest flag forced — just
  a planted thread. **This is the direct seed for "The Threnody Correspondence"** in
  `aethelgard_world_connections.md`: if the player later reaches Linden's capstone reveal in
  `whisperwoods_plea_quest.md`, Linden's old reply-that-was-never-followed-up takes on extra
  weight, and the player has *both halves* of a conversation two NPCs never finished.
- **Reward:** `lore_fragment` (existing item). No mechanical reward beyond that — this is an
  information/connection branch.

### Branch 2 — "What Spun That" (Veilmother thread)

- **Before:** During Beat 3, Orin's `lore_east_wall` line ("the east wall is webbed over
  some mornings... I don't go near it") plants the hook.
- **During:** Optional return visit to the Chasm's Edge after Beat 3 — a new flavor/Choice
  Event variant: the webbing is closer to the path than it was. Something small is caught
  in it — too far away and too high to identify clearly. "Look closer" vs. "Leave it."
  Looking closer doesn't resolve anything (no item, no battle) — just a slightly-too-long
  description of *almost* making out a shape, before the player's pet pulls them back.
- **After:** If the player mentions this to Orin, his only reaction: *"Then you've seen as
  much as I have. Don't go back for a better look."* No new lore unlocked — the dread is
  the content. This deliberately stays unresolved; Veilmother remains a Wanderer-rank
  scare/Legend-rank theoretical capture per `weeping_chasm_v2.md`'s existing rank-gating.
- **Reward:** None — pure atmosphere/foreshadowing branch.

### Branch 3 — "Held at the Threshold" (Gretta's Threshling, feeds The Long Memory)

- **Before:** Beat 3.5 (Gretta's Hollow) — the Threshling is seen for the first time,
  unexplained.
- **During:** Optional follow-up conversation with Gretta (`subdue_path_intro` dialogue
  already exists per code state) — she explains her philosophy of the Subdue capture path
  using the Threshling as the example: *"Didn't purify it. Made it clear who's in charge.
  That's all Subdue ever is — an agreement about who yields first."* This doubles as a
  natural-language introduction to the Subdue mechanic for players who haven't encountered
  it yet.
- **After:** A small, quiet detail — if the player lingers, the Threshling's clear eye
  tracks them, briefly, before going still again. Gretta, without looking up: *"It does
  that. Don't read into it."* Plants unease without explanation.
- **Connection payoff (later, elsewhere):** This is the direct seed for **"The Long
  Memory"** in `aethelgard_world_connections.md` — when/if Corvin's affinity story (Weeping
  Root) deepens, his offhand recognition of "something held at a threshold, out east" lands
  for any player who's been here. No forced ordering; works whichever remnant comes first.
- **Reward:** None mechanically — characterization + Subdue-mechanic teaching moment +
  cross-remnant seed.

### Branch 4 — Orin's Posting (affinity-based)

- Light, affinity-unlocked personal background for Warden Orin, gradually revealed over
  repeated conversations (same unlock pattern as Whisperwood's affinity-based NPC stories).
- **The shape of it:** Orin started out as a Guild recruit at Oakhaven, much like the
  player — and at some point, instead of moving on toward Whisperwood (or wherever his
  "head to ___" assignment pointed), he stayed at the Chasm. Not because of a dramatic
  event — he just... didn't leave. His Barkback (evolved from a Pineling issued early in
  his posting) is the only thing that's changed since.
- **Why it matters:** offers a quiet "road not taken" mirror for the player, who *is*
  currently mid-journey on that same road. Doesn't need a tragic reason — "I got used to
  the cold air. Didn't anymore. Stayed." is enough. Could gently echo Corvin's "stayed near
  the wound for decades" framing from Weeping Root, without copying it — Orin stayed near
  *nothing happening*, which is its own kind of staying.
- **Reward:** None — pure characterization.

---

## NPC Personal Side Stories — Mapping

Unlike Whisperwood (large cast, dedicated section needed), Weeping Chasm has only three
NPCs — and each is already covered by a Branch above. No separate content needed; this is
just a pointer for consistency with `whisperwoods_plea_quest.md`'s structure:

| NPC | Personal side story |
|---|---|
| Warden Orin | Branch 4 — "Orin's Posting" |
| Lore-Keeper Kael | Branch 1 — "The Sealed Journal" |
| "Grim" Gretta | Branch 3 — "Held at the Threshold" |

---

## Open Questions

1. Reward for `echoes_from_below` — original stub said "TBD." Suggest: XP + a lore item
   (mirrors `lore_fragment` already planned) rather than a pet/equipment reward, to keep
   tone consistent (this quest is about *information*, not loot).
2. Beat 4's scare encounter as a quest objective — needs an implementation-feasibility
   check (carried over from `weeping_chasm_v2.md`'s existing TAG FOR IMPLEMENTATION REVIEW).
3. Branches/side quests and NPC personal side stories for Weeping Chasm — not started yet;
   next pass, same structure as Whisperwood (Branches → NPC Personal Side Stories).
4. Should Galen's handoff line be conditional on anything, or always shown? Leaning: always
   shown, since it's flavor-only and doesn't gate progress.

---

## Cross-References

- `weeping_chasm_v2.md` — full Weeping Chasm design (NPCs, pets, Apex Ancients, explore
  events, original `echoes_from_below` stub).
- `whisperwoods_plea_quest.md` — Unified Origin lore, story-spine precedent, NPC Personal
  Side Stories structure to follow for Weeping Chasm's next pass.
- `aethelgard_classification.md` — Classification Tier framework; Primordial/Eternal note.
- `aethelgard_world_connections.md` — "The Threnody Correspondence" (Kael ↔ Linden), "The
  Long Memory" (Gretta's Threshling ↔ Corvin).
- `docs/design/oakhaven_outpost/oakhaven_outpost-done.md` — Galen's Vigil (source of the handoff line),
  `a_guildsmans_first_steps` / `head_to_whisperwood`.
