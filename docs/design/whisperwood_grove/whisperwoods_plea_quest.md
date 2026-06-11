# whisperwoods_plea — Quest Line (Story Pass)

**Status:** LOCKED (brainstorm session, no code changes yet)

This doc picks up the `whisperwoods_plea` quest design, split out from the (now parked)
`whisperwood_grove.md`. It assumes everything locked in that doc — the Lore Lock (Sylven
Heartwood = the Heart of Decay), the Gloom Sickness State/Type/Mark framework, the Weeping
Root remnant (Elowen, Corvin, Anora, Hollowthorn), and the new
`aethelgard_classification.md` (Classification Tier vs. Encounter Rarity).

Approach: **story first, mechanics/wiring later.** This doc is the story spine. Quest
flags, triggers, and step-by-step implementation get their own pass once the spine is solid.

---

## What Exists in Code Today

From Vexia's dialogue (`data/towns.py`):
- `quest_whisperwoods_plea_active`: "The Thicket grows darker by the day. Find the source
  of the corruption — the Heart of Decay. The forest is counting on you."
- `quest_whisperwoods_plea_complete`: "You've shown kindness and understanding. Now, let us
  see the strength of your bond. Face my companion — and prove yourself worthy."
- `crest_earned`: "The Verdant Crest rests with a worthy guardian."

Implied shape: find the Heart of Decay → return to Vexia → crest battle vs. Ferngale →
earn the Verdant Crest.

---

## Lore Update — Unified Origin (supersedes "wound that couldn't be burned out" framing)

This refines the Weeping Root's Lore Spine from `whisperwood_grove.md`, connecting it
directly to the Ashen Verge's lore spine (also in that doc):

**One organism, two surface points, no one to blame.** Generations ago, the same organism
first broke the surface at what is now the Ashen Verge. Pyrehart fought it back — at great
cost, leaving Pyrehart permanently wounded and dormant — and fire sealed off the part that
had breached the surface, becoming Cindermaw: a severed, contained fragment, a scar on the
land. But fire only ever reached the *surface*. The rest of the organism survived
underground, untouched, and over generations its root system kept growing — slowly,
unnoticed — until it reached and grew directly into **Sylven's own root system**. The
Weeping Root is where that growth ended up. You can't burn it out without burning Sylven
himself.

Nobody caused this — everyone in this story has only ever *responded* to something already
in motion: Pyrehart fought it, Kaelen's ancestors maintain the old containment ring out of
inherited duty, Corvin found the deep growth decades ago, Anora went looking for its source
and didn't come back, Elowen researches it now. Whether this organism is itself connected to
the single Gloom breach site ("the Chasm," per the Mirefields/Chasm lore and Oakhaven's
hints) is a much bigger question — deliberately left open for a later arc.

**Elder pairs.** Per `aethelgard_classification.md`, Pyrehart/Cindermaw and
Verdanthorn/Hollowthorn read as the same *kind* of phenomenon at two different sites and ages:
an Elder that embodies a territory's vitality, paired with an Elder that embodies the same
organism's wound at that site. Pyrehart/Cindermaw are the old, wounded, mostly-dormant pair;
Verdanthorn/Hollowthorn are the current, active pair. Worth a brief cross-reference note in
`aethelgard_classification.md`'s Elder tier entry.

**Sylven's role, reframed.** Sylven (Ancient tier) has been fighting this from the inside the
entire time — slowly, the way something enormous and old fights something it doesn't fully
understand. That's *why* the corruption spreads slowly instead of overrunning everything.
But Sylven can't finish the job: **Hollowthorn actively guards/feeds the core (Anora)**, and
as long as that anchor point is protected, Sylven's stabilization can't take hold there.
Removing Hollowthorn — by either branch of Beat 5 — doesn't fix anything by itself, but it
removes the thing that was *stopping* Sylven from eventually stabilizing on its own. That
becomes the long-term/future-arc payoff: Sylven can heal, slowly, once the active guard is
gone. Neither branch is "the cure" — both just let Sylven try.

---

## Story Spine (Beats)

### Beat 1 — The Quest Starts (Vexia)

Existing dialogue, unchanged. Vexia sends the player to find "the Heart of Decay" in the
Whispering Thicket / Whisperwood Wilds. At this point, the player has no reason to think
the Heart of Decay is Sylven itself — it reads as "find the source of a corruption problem
in the forest."

### Beat 2 — Signs Point Inward, Not Outward

While exploring the Thicket/Wilds, the player runs into the Withering-Marked wildlife
already seeded in the encounter tables/explore events (Mossling, Serpentine, Glamorose).
Per `aethelgard_classification.md`, these are **Ordinary-tier creatures with an
Uncommon/Rare sighting** — i.e., normal animals that look *wrong*. This is the player's
first contact with Gloom Sickness, framed as "the wildlife is getting sick," before any
named NPC explains what's actually happening.

Optional: a line or two from Arboreal or Linden registering quiet concern, without naming
the cause — they've noticed the same thing, but don't have the vocabulary yet (that comes
later, in the Weeping Root).

### Beat 2.5 — A Small Mercy (or Not)

A quiet, flavor-only Choice Event during exploration: the player finds a single
Withering-Marked creature in clear distress — not a fight, a moment. The "options" don't
have a clearly correct answer (help it / leave it alone / not sure helping even means
anything here) and carry no mechanical consequence. This is the player's first time sitting
with "I don't know what's right here" — a quiet rehearsal for Beat 5's Sever/Defeat choice.
Could reuse/extend one of the existing Pet Sighting explore events already written for the
Thicket/Wilds. Exact creature/wording: TBD.

### Beat 3 — Fae Whisper Opens the Path

Quest-only Choice Event in the Whispering Thicket. Fae Whisper steps out from between two
roots that "weren't there a moment ago" — *"I've been down there. I don't go anymore. But
you need to."* She opens the path down into **The Weeping Root**.

This is the pivot: the "source" isn't out in the wilds, it's *underneath*, inside Sylven's
own roots.

### Beat 3.5 — The Descent

A short transition beat following Fae Whisper down into the dark — tone shift from canopy
to abyss. Mostly atmosphere/flavor text (can lean on the Weeping Root's existing Flavor
explore events for tone). Room for one personal line from Fae Whisper about *why* she
stopped coming back here — not plot-critical, but recontextualizes her later (ties into the
Side Story Beat / Luna connection from `whisperwood_grove.md`). Exact line: TBD.

### Beat 4 — The Weeping Root: Gathering Understanding

The player meets **Elowen** (merchant, sees Gloom Sickness up close via her own Touched
Mark and her research) and **Corvin** (lore — Verdanthorn's Reflection, the history of the
wound, the first written account of "Petrified"/Calcifying). This is where the player gets
the actual *vocabulary* — State / Type / Mark — for what they've been seeing since Beat 2.

This beat is explicitly about understanding *before* confrontation. By the time the player
reaches Anora, they should know:
- What Gloom Sickness actually is (not just "corruption").
- That it has degrees (Touched/Hollowing) and that those degrees aren't necessarily final.
- That someone (Elowen) is actively trying to find a way to stop/reverse it.
- That someone else (Corvin) saw it happen to a person before, decades ago.

That's what makes Anora land as a *person*, not a monster, when the player gets there.

**Also part of this beat: the unified-origin connection.** Corvin is the natural
mouthpiece — he's old enough to remember (or to have records of) the Ashen Verge incident,
and he's the one who found this deep growth in the first place. A line from him connecting
"what fire sealed off up there" to "what you're standing in now" is the moment the player
realizes Ashen Verge and the Weeping Root are the same wound. Exact dialogue: TBD, but this
should land *before* Anora's Hollow, not after — it's part of the "understanding" the
climax depends on.

### Beat 4.5 — Before the Hollow

A quiet beat after meeting Elowen and Corvin, before pressing on toward Anora's Hollow.
Elowen, knowing where the player's headed, says something that isn't instructions — an
acknowledgment, or a small request ("if you find anything that... isn't her anymore, don't
tell me what it looked like"). Gives the climax emotional stakes from a third party who
isn't Anora herself, and reinforces Elowen's research stake in what's about to happen.
Exact dialogue: TBD.

### Beat 5 — Anora's Hollow (Climax)

The confrontation. Per the locked framing:
- **Anora** is the host/core — fused into the root wall, State: Hollowing, Type: Withering.
  She doesn't fight. She's the tragedy: a Guild scout who went looking for this decades ago
  and didn't come back the same.
- **Hollowthorn** — an **Elder**-tier being (per `aethelgard_classification.md`), Whisperwood's
  "balance-break" mirror of Verdanthorn — has gravitated to Anora as the strongest
  concentration of the wound, the way a guardian gravitates to a territory's heart.
  **Hollowthorn is the actual fight.**
- The player's choice — **Sever vs. Defeat** — is the mechanical expression of
  "kindness and understanding" from `quest_whisperwoods_plea_complete`. Critically, **neither
  option is a cure** — there isn't one yet (see Lore Update above). The fight against
  Hollowthorn plays out the same either way; the choice is what happens *after* Hollowthorn
  is beaten down:
  - **Sever**: cut Hollowthorn's connection to the core without destroying the root-mass
    Anora is fused into. This doesn't heal her — it **arrests her progression where it is**,
    the same way Corvin's Calcifying stalled decades ago. She'd be left suspended,
    Touched/Hollowing-frozen — still fused, still not herself, but no longer actively
    worsening. Pays off Elowen's research question directly: the player just generated her
    first real data point on whether the process *can* be stopped before it runs its course.
  - **Defeat**: destroy Hollowthorn outright, taking the corrupted mass — and Anora — with
    it. Faster, decisive, no ambiguity. Her alcove becomes an empty, scarred cavity.
  - Both outcomes are bittersweet by design — "is being frozen mid-Hollowing better than
    being released from it?" is left genuinely unclear. This fits "Town 2, no answers yet."
- Either outcome removes Hollowthorn as the active guard on the core — stabilizing the
  region (mirrors "the line is moving" thread from Ashen Verge, which should stop shrinking
  once this resolves) and clearing the way for Sylven's own slow self-stabilization (see
  Lore Update above). Full healing of Sylven himself remains a longer-term/future-arc thread.

**Foreshadowing note:** the Deep Vein Choice Event (already sketched in `whisperwood_grove.md`)
gives the player a glimpse of "something large" in the brightest vein before this point —
that's Hollowthorn. Per the classification framework, an Elder being *sighted at all* in a
quest-gated remnant is itself a signal that something is deeply wrong — Elders aren't
casually encountered. Worth making sure that teaser reads as unsettling rather than just
"strong wild pet ahead."

### Beat 5.5 — The Quiet After

A short beat immediately following the Sever/Defeat choice, before the player leaves the
Hollow — alone with the result. Different flavor text depending on which choice was made
(Sever: the suspended, frozen stillness of an arrested wound; Defeat: the empty, scarred
cavity). This is where the "did I do the right thing?" ambiguity gets room to land, instead
of being immediately overtaken by "now go fight Ferngale." Exact text: TBD.

### Beat 6 — Return to Vexia, Crest Battle, Verdant Crest

Existing locked dialogue (`quest_whisperwoods_plea_complete`, `crest_earned`). Crest battle
vs. Vexia's companion Ferngale. Optional/light-touch idea: Ferngale's battle dialogue or
demeanor could subtly reflect the player's Anora choice — not a hard branch, just flavor
text variance. Not committed.

### Beat 6.5 — Coda

After the crest battle, back in the Thicket, something subtly different — e.g., the
Withering-Marked creature from Beat 2.5 is gone, changed, or unchanged, depending on the
Sever/Defeat outcome. A small, optional "did it matter" payoff that closes the loop opened
in Beat 2.5 without requiring a hard branch elsewhere. Exact details: TBD.

---

## Branches — Side Quests & Side Stories (rough sketches)

These are **not required** for `whisperwoods_plea`, but connect to it — mostly as payoffs
that only make sense *after* the main spine resolves, or as texture that deepens it without
gating it. Pulled from the "Side Story Beat (OPEN/TBD)" list and the Ashen Verge lore spine
in `whisperwood_grove.md`, now reframed against the Unified Origin and Beat 5's Sever/Defeat
outcome.

### Branch 1 — "The Line is Moving" (Ashen Verge payoff)

Bram & Pip have been quietly tracking the Ashen Verge boundary slowly shrinking (Pip marks
it with stones), without Pyrehart at full strength to hold it. This is the *other* surface
point of the same organism (per Unified Origin) — so **Beat 5's resolution should be visible
here too**.

- **Before (seed):** an early, pre-quest visit to Ashen Verge where Pip mentions the stones
  casually — no weight yet, just color (this may already exist as part of the Ashen Verge
  side-story sketch in `whisperwood_grove.md` — confirm/reuse rather than duplicate).
- **During:** during Beat 3.5 (The Descent) or 4.5 (Before the Hollow), a small, optional
  line where the player notices something down here that *echoes* what Pip described up
  top — the player connects the two locations before Pip does. Flavor-only.
- **After (payoff, two-step):** first return visit post-Beat 5 — Pip notices something's
  different but isn't sure yet ("the stone... I don't think I need to move it today"). A
  later visit confirms it — he's sure now, the line has held.
- **Open question:** does Sever vs. Defeat produce any *visible* difference at Ashen Verge,
  or is "the line stopped" identical either way? Leaning toward **identical** — the
  stabilization is about Hollowthorn no longer guarding the shared root system, which is
  the same regardless of Anora's specific outcome. Keeps this branch simple and avoids
  needing two versions of Ashen Verge content.

### Branch 2 — Elowen's Research / "Letting Go"

Already seeded in `whisperwood_grove.md`: Elowen's Glamorose (Touched/Withering) is her
"control subject," and there's a flagged future side-story about her eventually having to
let it go. Beat 5's **Sever** outcome (if chosen) hands her real data for the first time —
this branch is what she *does* with that. Naturally suited to stretching since it's already
multi-visit by design.

- **Stage 1 (first visit, pre-existing):** establishes Elowen, her Touched Mark, her
  Glamorose, and the research framing — already covered in her NPC writeup.
- **Stage 2 (Beat 4.5, "Before the Hollow"):** her quiet request not to be told *what it
  looked like* — already written into Beat 4.5.
- **Stage 3 (immediately post-Beat 5):** her reaction to what the player tells her — about
  *meaning*, not description, per Stage 2's framing.
  - **If Sever:** she has real data for the first time. Reaction should feel like a
    held-breath moment — not relief exactly, more "this is the first time the question
    isn't purely theoretical."
  - **If Defeat:** no new data, but not "nothing" — grief without data is still something.
    Her reaction here should carry its own weight (TBD tone), not read as the empty branch.
- **Stage 4 (settling visits, plural):** over a few subsequent visits, her stance on her own
  Glamorose shifts gradually rather than all at once — small dialogue variations per visit
  rather than one big change. Direction (more hopeful vs. more resigned): TBD, depends on
  overall tone for her arc.
- **Stage 5 (eventual "letting go" beat):** still flagged for a future pass, possibly beyond
  Town 2's scope entirely (could be a Town 3+ thread if Elowen remains recurring).

### Branch 3 — Luna/Mira & Fae Whisper (Moonpetal Inn thread)

The day/night Moonpetal Inn split (Mira/Luna) and Fae Whisper's history both involve "things
that happen at night that don't get repeated to day-people." Naturally suited to stretching
since it requires multiple visits/timing already.

- **Before (seed):** an early, pre-quest visit to Luna (night) where she has one odd,
  unexplained line — something that only makes sense later. No context given at the time.
- **During (Beat 3.5):** Fae Whisper's personal line (already part of Beat 3.5) is the
  other half of what Luna said — neither repeats what the other said (mirrors the Bram/Pip
  "Match"/"Wisp" naming bit — a recurring texture pattern of "two people who know the same
  thing and don't compare notes").
- **After (payoff):** a later visit to Luna, post-Beat 3.5 — if the player brings up Fae
  Whisper (or just based on quest progress), Luna reacts subtly, confirming the connection
  without spelling it out. Attentive players connect the dots themselves.
- **Payoff framing:** mostly characterization/world-texture — confirms Fae Whisper isn't
  just "quest NPC who opens a door," she has a life/history in the town that predates the
  quest. No mechanical reward needed; this is "the world feels lived-in" texture.

### Branch 4 — Arboreal & Sylven

Arboreal's healing draws from Sylven's roots (Lore Lock). Question flagged in
`whisperwood_grove.md`: does he *know* what's happening to Sylven?

- **Before (seed):** early in the quest (around Beat 2, alongside the optional
  Arboreal/Linden "quiet concern" lines), Arboreal has a small unprompted line about the
  roots feeling "off" — *"the roots have felt... tired, lately. I didn't know what to make
  of it."* Plants the seed long before the player has the vocabulary to understand why.
- **During:** no additional touchpoint needed — Arboreal doesn't have State/Type/Mark
  vocabulary (per Beat 4), so he stays quiet through the middle beats. His not-knowing is
  itself part of the texture.
- **After (payoff, tied to Beat 5):** post-quest, Arboreal has a small reaction — something
  changed in how the roots feel, even if he still can't explain it. Quiet confirmation that
  Sylven's slow self-stabilization (per the Lore Update) has begun, told through the NPC
  most directly connected to Sylven day-to-day, without Sylven ever appearing directly. The
  "before" seed makes this read as *recognition* ("it's different now") rather than a new
  reveal.
- **Open question:** should this reaction differ between Sever/Defeat? Leaning **no**,
  same reasoning as Branch 1 — keeps it simple, and the "did it matter" question is already
  being asked more pointedly in Beat 6.5.

---

## NPC Personal Side Stories (rough sketches)

Background-story content for individual NPCs, separate from the main spine and Branches
1-4 — but several connect to each other and to the main quest. Two unlock patterns are
used, matched to what kind of reveal it is:
- **Quest-flag-based** — only makes sense after specific story knowledge exists.
- **Affinity-based** — unlocked by repeated conversations/visits, independent of quest state.

### The Guild Scout Thread (Vexia, Linden, Fae Whisper, Anora) — major connected web

This is the big one — four NPCs' personal stories interlock around a single thread: what
actually happened to Anora, decades ago.

- **Vexia** *(quest-flag, post-Beat 5)*: Vexia knew Anora — personally, or at least knew of
  her disappearance and was involved in the decision to stop searching. Post-Beat 5,
  returning to Vexia for Beat 6 carries a second layer: "Face my companion, prove yourself
  worthy" now lands differently, knowing Vexia already suspected, on some level, what was
  down there. Possible "before" seed: an odd, unexplained reaction from Vexia to something
  forest-related, pre-quest — recontextualized later.
- **Linden** *(quest-flag, post-Beat 5, OR affinity — whichever reads better)*: Linden is
  the Guild's records-keeper. This is the mechanism for the "cross-reference old Guild
  records" gut-punch flagged back when Anora was first established. Post-quest, the player
  can ask Linden about old expeditions — he digs up Anora's record. This is the payoff of
  that early hook, and it's the piece that makes the thread *concrete* (a name, a date, a
  case file) rather than just implied.
- **Fae Whisper** *(quest-flag, tied to Beat 3.5/her personal line)*: reframe her "why I
  stopped going back" line (Beat 3.5) — she didn't just *hear about* the wound, she's the
  one who, on her solo trip, actually found Anora already fused into the root wall. That's
  what she saw. That's why she doesn't go back, and why she sends the player instead of
  going herself. This single reframe makes Beat 3.5 retroactively much heavier on a second
  playthrough/reflection, without changing a word of what's said *at the time*.
- **Anora**: doesn't get her own repeat-visit content — her "personal side story" *is* this
  thread, told through the other three. (If Sever was chosen, there may be room for very
  minimal, non-verbal acknowledgment from her in a future pass — not committed.)

**Suggested unlock order:** Beat 5 resolves → Fae Whisper reframe becomes available
(she's already met) → Vexia reveal at Beat 6 → Linden's records become askable afterward,
as the "proof"/concrete capstone. All four pieces should be discoverable without a strict
forced order beyond "after Beat 5," but this is the natural reading order.

### Town Core (remaining NPCs)

- **Arboreal** *(affinity-based)*: deepen Branch 4 — how did he come to tend the Lodge?
  Possible angle: he was healed by Sylven himself once, long ago, and has devoted himself
  to the Lodge ever since. Affinity-based reveal, independent of quest state; Branch 4's
  post-Beat-5 "roots feel different" reaction stays quest-flag-based as already designed.
- **Mira / Luna** *(affinity-based)*: why twins run day/night shifts — light personal
  history, could carry a faint Gloom-adjacent thread (without being heavy) that
  complements Branch 3's Luna/Fae Whisper connection rather than duplicating it.
- **Slithers** *(affinity-based, light)*: the shop's stock includes salvage — connects
  loosely to Bram & Pip's "stripping old ruins" economy (Ashen Verge). Mostly flavor;
  gives Slithers *some* personality beyond "shop," and gives Bram & Pip's scavenging a
  destination/purpose in the wider economy.

### Ashen Verge

- **Kaelen** *(side-quest-flag, "What's Beneath the Ash")*: once the side quest reveals
  what the containment ritual was actually *for*, Kaelen has personal doubt — he's spent
  his life tending something he now understands for the first time, and isn't sure how he
  feels about that. Direct 1:1 payoff of the side quest.
- **Bram & Pip** *(affinity-based)*: lighter personal history — why they live out here.
  Connects to Slithers above (where their salvage ends up). Complements existing "the
  choosing" and "the line is moving" side stories without replacing them.

### Weeping Root

- **Elowen**: covered by Branch 2 (Research / "Letting Go") — no separate entry needed.
- **Corvin** *(affinity-based)*: why has he *stayed* near the wound for decades, fully
  mobile and able to leave? His own reason — guilt, duty, an inability to look away —
  separate from his lore-dump role. Unlocks gradually over repeated conversations, giving
  players a reason to revisit him after the main quest ends.
- **Anora**: see Guild Scout Thread above — no separate repeat-visit content.

---

## Open Questions (carried forward)

1. ~~Should the player be able to attempt/complete `whisperwoods_plea` without ever finding
   the Weeping Root?~~ — **RESOLVED: hard requirement.** It's the main story for a reason —
   it follows through. No skipping the Weeping Root.
2. ~~Do Beats 2-4 need their own smaller choices?~~ — **RESOLVED:** yes, but flavor-only,
   no mechanical branching. Added as Beats 2.5 (A Small Mercy), 3.5 (The Descent), and 4.5
   (Before the Hollow) — each rehearses or sets up the emotional weight of Beat 5 without
   forking the quest state. Beat 5.5 (The Quiet After) and 6.5 (Coda) round out the back
   half with the same approach.
3. Beat 6 Ferngale flavor-variance based on Anora's outcome — yes/no, low priority. Still
   open, not blocking.
4. Step-by-step quest flag/trigger wiring — separate pass, after this spine is approved.
   Now includes wiring for Beats 2.5/3.5/4.5/5.5/6.5 in addition to the original six.

---

## Cross-References

- `whisperwood_grove.md` — town core, NPCs, Gloom Sickness framework, Weeping Root remnant
  (Elowen/Corvin/Anora/Hollowthorn full write-ups).
- `aethelgard_classification.md` — Classification Tier (Elder/Ancient/etc.) and Encounter
  Rarity framework referenced throughout this doc.
