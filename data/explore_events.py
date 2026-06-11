# data/explore_events.py
#
# Flavor events that can fire during /explore, themed per zone.
# Each event is a dict with:
#   "type"        : "flavor" | "choice" | "loot_bonus" | "hazard" | "pet_sighting"
#   "weight"      : int  — relative chance (higher = more common)
#   "text"        : str  — narrative description shown to the player
#   "outcome"     : dict — optional stat/item consequence
#       "energy"  : int  (positive = restore, negative = drain)
#       "hp"      : int  (positive = restore, negative = drain, as % of max_hp)
#       "item"    : {"item_id": str, "qty": int}
#   "choices"     : list of choice dicts (only for "choice" type)
#       Each choice: {"label": str, "emoji": str, "outcome": dict, "text": str}
#
# For "pet_sighting" events, the player sees a wild pet but no battle starts —
# just lore and atmosphere. These are purely flavor.

EXPLORE_EVENTS = {

    # ─────────────────────────────────────────────
    # Oakhaven Outpost — The Rotting Pits
    # ─────────────────────────────────────────────
    "oakhavenOutpost_rottingPits": [

        # --- Flavor Events (no consequence) ---
        {
            "type": "flavor",
            "weight": 10,
            "text": "A thick, sulphurous bubble rises from the nearest pit and pops with a wet *schloop*. Whatever is living down there, it isn't in a hurry.",
        },
        {
            "type": "flavor",
            "weight": 10,
            "text": "You spot a rusted boot half-sunken into the tar at the pit's edge. It has been there a long time. You decide not to think about where the other boot went.",
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": "A faint luminescence pulses beneath the surface of the nearest pit — slow, rhythmic, like a heartbeat. The Gloom is alive here.",
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": "Grit Galen's scratched warning marker — a stick with a strip of red cloth — stands at the pit's edge. Someone keeps moving it further back. The pits are growing.",
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": "The air tastes of iron and rot. Your pet presses close to your leg, eyes fixed on the bubbling centre of the largest pit. Something is watching from below.",
        },

        # --- Pet Sightings (atmosphere, no battle) ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": "A Corroder skitters across the far rim of the pit — all jagged shell and twitching antennae. It stops, fixes you with compound eyes, then sinks silently back into the tar. It already knows where you are.",
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": "Something large and dark shifts beneath the surface of the largest pit. For a moment you see the outline of limbs — too many limbs — before the Gloom closes over it.",
        },

        # --- Loot Bonus Events ---
        {
            "type": "loot_bonus",
            "weight": 7,
            "text": "You notice a weathered pack wedged beneath a cracked tar-stone at the pit's edge. Inside: a few battered supplies, still usable.",
            "outcome": {"item": {"item_id": "moss_balm", "qty": 1}},
        },
        {
            "type": "loot_bonus",
            "weight": 5,
            "text": "A cluster of Spiritshard Moss clings to the underside of a tar-crusted rock — rare here, but the Gloom seems to nourish it.",
            "outcome": {"item": {"item_id": "sun_kissed_berries", "qty": 2}},
        },

        # --- Hazard Events (minor negative) ---
        {
            "type": "hazard",
            "weight": 7,
            "text": "You step too close to a bubbling vent. A geyser of scalding sludge erupts without warning, spattering you and your pet.",
            "outcome": {"hp": -8},
        },
        {
            "type": "hazard",
            "weight": 5,
            "text": "The ground shifts underfoot — a sinkhole, barely a metre across, opens just behind you. Your heart hammers as you scramble clear. That was too close.",
            "outcome": {"energy": -1},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 6,
            "text": "A blackened Tether Orb bobs near the surface of the shallower pit — Gloom-stained, but possibly still functional. Do you reach in?",
            "choices": [
                {
                    "label": "Reach in",
                    "emoji": "🤿",
                    "text": "You plunge your arm into the tar and grab the orb. It's intact — and now your sleeve is ruined.",
                    "outcome": {"item": {"item_id": "tether_orb", "qty": 1}, "hp": -5},
                },
                {
                    "label": "Leave it",
                    "emoji": "🚶",
                    "text": "Not worth a faceful of Gloom-tar. You walk on.",
                    "outcome": {},
                },
            ],
        },
        {
            "type": "choice",
            "weight": 5,
            "text": "A low groan echoes from a collapsed section of pit-wall. Something small is trapped in the rubble — you can't tell what. You could try to free it, or the noise might attract something larger.",
            "choices": [
                {
                    "label": "Investigate",
                    "emoji": "🔍",
                    "text": "You clear the rubble and find a startled Bristlecone, unhurt. It bolts the moment it is free. Small victories.",
                    "outcome": {"energy": 1},
                },
                {
                    "label": "Back away",
                    "emoji": "🚶",
                    "text": "You slip away quietly. Whatever it was, it can sort itself out.",
                    "outcome": {},
                },
            ],
        },
    ],

    # ─────────────────────────────────────────────
    # Outpost Wilds
    # ─────────────────────────────────────────────
    "outpostWilds": [

        # --- Flavor ---
        {
            "type": "flavor",
            "weight": 10,
            "text": "A shaft of early light breaks through the canopy, catching motes of dust and spores in a slow golden column. Your pet basks in it for a moment.",
        },
        {
            "type": "flavor",
            "weight": 10,
            "text": "A Bristlecone watches you from a low branch, perfectly still. The moment you look directly at it, it vanishes into the underbrush without a sound.",
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": "A trail of small, three-toed prints cuts across the muddy path ahead. Fresh — made within the last hour. Something was moving quickly.",
        },
        {
            "type": "flavor",
            "weight": 7,
            "text": "The underbrush rattles violently to your left. Then silence. Then, from your right, the same rattling. Something is circling you, but nothing ever appears.",
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": "You find an old Guild marker — the wood warped and moss-covered, the blazed symbol barely legible. This path was regularly patrolled once. It is not now.",
        },

        # --- Pet Sightings ---
        {
            "type": "pet_sighting",
            "weight": 9,
            "text": "A Dewdrop clings to a broad leaf overhead, its translucent body refracting the light into tiny rainbows on the forest floor. It hasn't noticed you.",
        },
        {
            "type": "pet_sighting",
            "weight": 7,
            "text": "Two Bristlecones chase each other through the canopy at reckless speed, crashing through branches and raining bark down around you. Neither one acknowledges your presence.",
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 8,
            "text": "You spot a cluster of ripe Sun-Kissed Berries on a low bush just off the path — more than usual, and perfectly ripe.",
            "outcome": {"item": {"item_id": "sun_kissed_berries", "qty": 2}},
        },
        {
            "type": "loot_bonus",
            "weight": 5,
            "text": "A small hollow in the base of an old oak hides a tattered satchel — forgotten by some past traveller. Inside: trail rations, still sealed.",
            "outcome": {"item": {"item_id": "trail_morsels", "qty": 2}},
        },

        # --- Restorative ---
        {
            "type": "loot_bonus",
            "weight": 6,
            "text": "A natural spring bubbles up through a mossy outcrop nearby. The water is cold and clear. You and your pet rest here for a few minutes.",
            "outcome": {"energy": 1},
        },

        # --- Hazard ---
        {
            "type": "hazard",
            "weight": 6,
            "text": "You misjudge a jump across a muddy streambed and go in up to the knee. Cold, wet, and annoyed, you haul yourself out. Your pet finds this hilarious.",
            "outcome": {"energy": -1},
        },

        # --- Choice ---
        {
            "type": "choice",
            "weight": 6,
            "text": "You come across a large, unusual mushroom ring — perfect circle, no mushrooms broken. Local lore says eating one gives strength. Local lore also says it causes vivid nightmares.",
            "choices": [
                {
                    "label": "Eat one",
                    "emoji": "🍄",
                    "text": "Earthy, bitter, and oddly warm going down. You feel a strange surge of energy... and resolve to sleep with the lantern on tonight.",
                    "outcome": {"energy": 2, "hp": -5},
                },
                {
                    "label": "Leave it alone",
                    "emoji": "🚶",
                    "text": "Some lore is lore for a reason. You step around the ring and continue on your way.",
                    "outcome": {},
                },
            ],
        },
        {
            "type": "choice",
            "weight": 5,
            "text": "A wounded Mossling sits in the middle of the path, favouring its front leg. It growls weakly as you approach — scared, not aggressive. You have a Moss Balm in your pack.",
            "choices": [
                {
                    "label": "Treat its wound",
                    "emoji": "💚",
                    "text": "You kneel slowly, let it sniff your hand, and apply the balm. After a long moment, it licks your wrist and limps off into the undergrowth. That felt good.",
                    "outcome": {"item": {"item_id": "moss_balm", "qty": -1}},  # costs 1 balm
                },
                {
                    "label": "Walk around it",
                    "emoji": "🚶",
                    "text": "You give it a wide berth. It watches you go, growling softly. Sometimes that is all you can do.",
                    "outcome": {},
                },
            ],
        },
    ],

    # ─────────────────────────────────────────────
    # Weeping Chasm — The Chasm's Edge
    # ─────────────────────────────────────────────
    "weeping_chasm": [

        # --- Flavor Events ---
        {
            "type": "flavor",
            "weight": 10,
            "text": (
                "The chasm exhales cold air in a slow, rhythmic pulse. "
                "Your pet refuses to approach the edge. "
                "It doesn't move until the pulse stops."
            ),
        },
        {
            "type": "flavor",
            "weight": 9,
            "text": (
                "A Guild marker post — cracked, the rune barely holding. "
                "Someone scratched a tally into the wood. Thirty-seven marks. "
                "You don't know what they were counting."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "A sound rises from below. Not a creature — more like a voice, "
                "too deep and too slow to understand. "
                "It stops the moment you move."
            ),
        },
        {
            "type": "flavor",
            "weight": 7,
            "text": (
                "Near the Whispering Stones — a cluster of rounded rocks at the "
                "sealed section — the air hums faintly. Guild records say this is "
                "where the first ward was placed. Whatever it was holding, it's still holding."
            ),
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": (
                "The mist curls upward around your ankles. "
                "Nothing attacks. Something is just checking.",
            ),
            "time": "night",
        },
        {
            "type": "flavor",
            "weight": 5,
            "text": (
                "The breathing from below changes rhythm. Slower. Deeper. "
                "Your pet goes completely still and won't move until it resumes."
            ),
            "time": "night",
        },

        # --- Pet Sightings ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": (
                "A Corroder sits at the chasm's lip, staring down into the dark "
                "instead of at you. It doesn't react to your presence. "
                "It seems drawn to the source."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": (
                "Something pale drifts upward from the chasm on the cold thermal — "
                "translucent, barely there, gone before you can focus on it."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 5,
            "text": (
                "The east wall of the Chasm is covered in thick, dark silk from rim "
                "to rock face. Something enormous spun this overnight. "
                "The webbing is still faintly warm."
            ),
        },

        # --- Hazard Events ---
        {
            "type": "hazard",
            "weight": 7,
            "text": (
                "A cold updraft hits without warning — disorienting, wrong. "
                "Not wind. An exhale from below. Your pet stumbles. You catch it."
            ),
            "outcome": {"hp": -8},
        },
        {
            "type": "hazard",
            "weight": 6,
            "text": (
                "The ground near the Tainted Ledge shifts. A crack opens, "
                "runs three feet, stops. You step back slowly. "
                "The crack doesn't close."
            ),
            "outcome": {"energy": -1},
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 5,
            "text": (
                "A Guild emergency cache bolted to a post near the sealed section. "
                "Still stocked. Someone kept resupplying this long after the post was abandoned."
            ),
            "outcome": {"item": {"item_id": "zone_loot", "qty": 1}},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 6,
            "text": (
                "A sealed Guild journal is wedged in a crack near the Tainted Ledge. "
                "It's been here a while — the wax seal is intact but the cover is "
                "warped from cold. You could pry it open."
            ),
            "choices": [
                {
                    "label": "Pry it open",
                    "emoji": "📖",
                    "text": (
                        "The seal breaks. Inside: field notes, precise until the last few pages "
                        "where the handwriting changes. You take the fragment. "
                        "The Gloom around you feels slightly heavier."
                    ),
                    "outcome": {"item": {"item_id": "lore_fragment", "qty": 1}, "gloom_tick": 5},
                },
                {
                    "label": "Leave it",
                    "emoji": "🚶",
                    "text": "Some things stay sealed for a reason. You walk away.",
                    "outcome": {},
                },
            ],
        },

        # --- Apex Lore Events (Chasmbane + Veilmother) ---
        # These are atmosphere/scare events — no battle, no capture.
        # Full rank-gated encounter logic tagged for later.
        {
            "type": "hazard",
            "weight": 3,
            "text": (
                "The mist stops. All of it — in an instant. The chasm goes completely "
                "silent. Something at the rim of your vision, near the base of the wall, "
                "is large enough that your mind refuses to measure it. "
                "It isn't looking at you. Then it is. "
                "The Gloom floods your senses before you consciously decide to back away."
            ),
            "outcome": {"gloom_tick": 15},
        },
        {
            "type": "pet_sighting",
            "weight": 2,
            "time": "night",
            "text": (
                "The east wall moves. Not shifts — moves, deliberately, slowly. "
                "A section of what you thought was webbing detaches from the rock face "
                "and redistributes itself further up. The scale of it doesn't make sense "
                "until you find a marker post for reference. "
                "You stop using the marker post for reference."
            ),
        },
    ],

    # ─────────────────────────────────────────────
    # Mirefields — The Mire Path
    # ─────────────────────────────────────────────
    "mirefields": [

        # --- Flavor Events ---
        {
            "type": "flavor",
            "weight": 10,
            "text": (
                "The path disappears under two inches of brown water. You can't tell if it "
                "continues forward or if you've already stepped off it."
            ),
        },
        {
            "type": "flavor",
            "weight": 9,
            "text": (
                "A territorial bog creature bursts from the reeds, takes one look at you "
                "and your pet, and retreats. You're bigger than its usual targets. Barely."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "The ruins of a signpost poke out of the muck — three arrows pointing "
                "different directions. None of the place names are legible. Someone has "
                "tried to scratch new ones in. You can't read those either."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "Sable's trail markers — knotted reed bundles tied to stakes — are the "
                "only reliable guide here. You spot one and orient yourself. Without "
                "these, you'd be walking in circles."
            ),
        },
        {
            "type": "flavor",
            "weight": 5,
            "text": (
                "The fog sits low and still. Sound travels oddly — a splash from somewhere "
                "to your left sounds close, then far, then close again. Nothing surfaces."
            ),
            "time": "night",
        },

        # --- Pet Sightings ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": (
                "A Murkback watches you from a half-submerged log, perfectly still. "
                "It's not interested in fighting. It's waiting for you to leave its territory."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": (
                "Something moves under the surface in the deeper section of the mire. "
                "Not small. It tracks alongside you for about a minute, then veers off "
                "without surfacing."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 5,
            "text": (
                "A Pallefin skims the surface of a still pool just off the path — barely "
                "disturbing the water. It's gone before you can focus on it."
            ),
            "time": "day",
        },
        {
            "type": "pet_sighting",
            "weight": 5,
            "text": (
                "Something low and slow moves through the reeds. You can't see it clearly. "
                "Just the reeds parting and settling. It doesn't come closer."
            ),
            "time": "night",
        },

        # --- Hazard Events ---
        {
            "type": "hazard",
            "weight": 7,
            "text": (
                "You sink into a soft patch up to your knee. Extracting yourself takes "
                "time and costs you. Your pet watches from dry ground with no sympathy."
            ),
            "outcome": {"energy": -1},
        },
        {
            "type": "hazard",
            "weight": 6,
            "text": (
                "A bog creature you didn't see charges from the shallow water — a glancing "
                "hit. It was more startled than aggressive, but that doesn't help your ribs much."
            ),
            "outcome": {"hp": -10},
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 6,
            "text": (
                "You spot a waterlogged pack half-buried in the reed bed — old, probably "
                "from the waystation days. Still has something inside worth keeping."
            ),
            "outcome": {"item": {"item_id": "zone_loot", "qty": 1}},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 7,
            "text": (
                "A section of the old crossroads road is visible just beneath the water — "
                "stone paving, still intact. You could follow it deeper into the mire, "
                "or stick to Sable's markers."
            ),
            "choices": [
                {
                    "label": "Follow the old road",
                    "emoji": "🗺️",
                    "text": (
                        "The paving holds for a while. Then it doesn't. You backtrack "
                        "before it gets worse — but not before finding something."
                    ),
                    "outcome": {"item": {"item_id": "zone_loot", "qty": 1}, "energy": -1},
                },
                {
                    "label": "Stick to the markers",
                    "emoji": "🌿",
                    "text": "Smart. You follow Sable's reeds and stay dry. Nothing happens.",
                    "outcome": {},
                },
            ],
        },
    ],

    # ─────────────────────────────────────────────
    # Whisperwood Grove — The Whispering Thicket
    # gloom_level 15. Tone: ancient, beautiful, something is wrong underneath.
    # ─────────────────────────────────────────────
    "whisperwoodGrove": [

        # --- Flavor Events ---
        {
            "type": "flavor",
            "weight": 10,
            "text": (
                "The canopy is so dense overhead that noon looks like dusk. "
                "The light that filters through is green and old."
            ),
        },
        {
            "type": "flavor",
            "weight": 9,
            "text": (
                "Something has woven vines across the path overnight — not blocking it, "
                "just crossing it. Like a boundary marker that wasn't there yesterday."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "The bark of the nearest tree has a shallow indent — like a handprint. "
                "Far too large to be human."
            ),
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": (
                "A cluster of Glamorose drifts past at eye level, trailing a faint sweet "
                "scent. You hold your breath without quite deciding to. It continues "
                "without slowing."
            ),
            "time": "night",
        },

        # --- Pet Sighting Events ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": (
                "Verdanthorn stands motionless between two massive oaks, watching. "
                "When you move, it doesn't. When you stop, it already isn't there."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": (
                "Something large moves through the undergrowth — slow, deliberate. "
                "The ground doesn't crack under it. It is part of the ground."
            ),
        },

        # --- Hazard Events ---
        {
            "type": "hazard",
            "weight": 7,
            "text": (
                "Hollowed petals lie scattered across the path. You don't notice them "
                "until you've already walked through. Your pet pulls back from the residue."
            ),
            "outcome": {"hp": -6},
        },
        {
            "type": "hazard",
            "weight": 5,
            "text": (
                "A branch shifts above you — there's no wind. Something heavy was resting "
                "there a moment ago."
            ),
            "outcome": {"energy": -1},
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 6,
            "text": (
                "A Guild researcher's cache, half-buried in moss at the base of an old "
                "trunk. Old, but still sealed."
            ),
            "outcome": {"item": {"item_id": "moss_balm", "qty": 1}},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 6,
            "text": (
                "The oldest tree in the Thicket has something carved into its bark. "
                "Not words — more like a map, or a warning. You could take a rubbing."
            ),
            "choices": [
                {
                    "label": "Take a rubbing",
                    "emoji": "📜",
                    "text": (
                        "You press a scrap of cloth against the bark and rub gently. "
                        "The pattern transfers cleanly. Somewhere in the canopy above, "
                        "something shifts — and goes still again."
                    ),
                    "outcome": {"item": {"item_id": "lore_fragment", "qty": 1}},
                },
                {
                    "label": "Leave it",
                    "emoji": "🚶",
                    "text": "Some markings aren't meant to be copied. You walk on.",
                    "outcome": {},
                },
            ],
        },
        {
            "type": "choice",
            "weight": 4,
            "time": "night",
            "text": (
                "A cluster of Glamorose has surrounded a Mossling in the middle of the "
                "path, its struggling slowing by the second as the sweet fragrance settles "
                "over it. You could pull it free."
            ),
            "choices": [
                {
                    "label": "Pull it free",
                    "emoji": "💚",
                    "text": (
                        "You wade in, breath held, and haul the Mossling clear. The "
                        "fragrance clings to your skin and clothes long after the bloom "
                        "loses interest. The Mossling bolts without a sound."
                    ),
                    "outcome": {"hp": -5, "energy": 1},
                },
                {
                    "label": "Walk past",
                    "emoji": "🚶",
                    "text": (
                        "You walk past. The Mossling stops struggling before you're out "
                        "of sight. You feel the fragrance for a while after, even though "
                        "you never got close."
                    ),
                    "outcome": {},
                },
            ],
        },
    ],

    # ─────────────────────────────────────────────
    # Whisperwood Wilds
    # Tone: untamed, primordial, not corrupted — just old and unmanaged.
    # ─────────────────────────────────────────────
    "whisperwoodWilds": [

        # --- Flavor Events ---
        {
            "type": "flavor",
            "weight": 10,
            "text": (
                "The path here isn't really a path. It's a gap that was cleared once and "
                "hasn't been cleared since. The forest is taking it back, slowly."
            ),
        },
        {
            "type": "flavor",
            "weight": 9,
            "text": (
                "A split oak, struck by lightning long ago, has grown back around the "
                "scar. Something lives in the hollow where the wood rejoined."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "Tracks cut through the mud ahead — three toes, deep. Something heavy "
                "passed this way recently."
            ),
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": (
                "The further you go, the quieter it gets. Not peaceful quiet. "
                "Waiting quiet."
            ),
        },

        # --- Pet Sighting Events ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": (
                "A Serpentine hangs perfectly still from an overhead branch, "
                "indistinguishable from a vine — until it turns one eye toward you."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 6,
            "text": (
                "Two Mosslings chase each other through the undergrowth at the edge of "
                "your vision, then vanish into the moss without a sound."
            ),
        },

        # --- Hazard Events ---
        {
            "type": "hazard",
            "weight": 7,
            "text": (
                "You step onto what looks like solid ground. A root hollow collapses "
                "beneath you, and you scramble back onto the path, muddy and annoyed."
            ),
            "outcome": {"energy": -1},
        },
        {
            "type": "hazard",
            "weight": 5,
            "text": (
                "Something drops from the canopy — not a branch. It's gone before you "
                "can get a look at it, but the impact still caught you."
            ),
            "outcome": {"hp": -5},
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 6,
            "text": (
                "A traveller's pack, wedged in a root hollow. Whoever left it isn't "
                "coming back for it."
            ),
            "outcome": {"item": {"item_id": "trail_morsels", "qty": 1}},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 6,
            "text": (
                "A Serpentine is coiled around the base of a tree, pinning a sealed tin "
                "beneath it. It hasn't moved since you spotted it."
            ),
            "choices": [
                {
                    "label": "Try to retrieve it",
                    "emoji": "🤿",
                    "text": (
                        "You ease the tin out from under the coils. The Serpentine's eye "
                        "tracks you the entire time, but it doesn't strike — until the "
                        "very last moment, and even then it's barely a warning bite."
                    ),
                    "outcome": {"item": {"item_id": "tether_orb", "qty": 1}, "hp": -8},
                },
                {
                    "label": "Leave it",
                    "emoji": "🚶",
                    "text": (
                        "The Serpentine doesn't even look at you as you pass. Whatever's "
                        "in that tin can stay there."
                    ),
                    "outcome": {},
                },
            ],
        },
        {
            "type": "choice",
            "weight": 5,
            "text": (
                "You come across a perfectly circular clearing — no trees within it, old "
                "ash marks scorched into the ground. Something happened here, and not "
                "recently."
            ),
            "choices": [
                {
                    "label": "Examine the marks",
                    "emoji": "🔍",
                    "text": (
                        "The ash is old, but the pattern is deliberate — too even to be "
                        "natural. You note the shape before moving on. It stays with you "
                        "longer than you'd like."
                    ),
                    "outcome": {"item": {"item_id": "lore_fragment", "qty": 1}},
                },
                {
                    "label": "Keep moving",
                    "emoji": "🚶",
                    "text": "You look at it for a long moment before you do.",
                    "outcome": {},
                },
            ],
        },
    ],

    # ─────────────────────────────────────────────
    # The Ashen Verge — The Ash Circle
    # Tone: quiet, smoky, cold, *managed* — not hostile. The First Ring's rare
    # sightings (Pyrethorn/Cindermaw/Pyrehart) are folded into this zone's
    # encounter table rather than given a separate explore pool.
    # ─────────────────────────────────────────────
    "ashenVerge": [

        # --- Flavor Events ---
        {
            "type": "flavor",
            "weight": 10,
            "text": (
                "The grass ends in a perfectly straight line. On one side, green. "
                "On the other, gray ash that doesn't shift in the wind."
            ),
        },
        {
            "type": "flavor",
            "weight": 9,
            "text": (
                "Old fire-rings, dozens of them, sit in concentric circles fading "
                "outward. Most look decades old."
            ),
        },
        {
            "type": "flavor",
            "weight": 8,
            "text": (
                "Your footprints are the only mark on the ash. It hasn't rained "
                "here in a long time — or the ash doesn't let it show."
            ),
        },
        {
            "type": "flavor",
            "weight": 6,
            "text": (
                "A faint smell of smoke that never quite fades, even this far "
                "from any fire."
            ),
        },

        # --- Pet Sighting Events ---
        {
            "type": "pet_sighting",
            "weight": 8,
            "text": (
                "A Cinderkit sits at the edge of a cold fire-ring, warming itself "
                "against embers that aren't there."
            ),
        },
        {
            "type": "pet_sighting",
            "weight": 5,
            "text": (
                "Something with smoking footprints crossed here recently. The "
                "tracks lead toward the deeper ash and don't come back."
            ),
        },

        # --- Hazard Events ---
        {
            "type": "hazard",
            "weight": 7,
            "text": (
                "A patch of ash gives way to a bed of still-hot coals "
                "underneath."
            ),
            "outcome": {"hp": -6},
        },
        {
            "type": "hazard",
            "weight": 5,
            "text": (
                "The wind shifts and a wall of ash dust rolls over you. Hard to "
                "see, harder to breathe for a moment."
            ),
            "outcome": {"energy": -1},
        },

        # --- Loot Bonus ---
        {
            "type": "loot_bonus",
            "weight": 6,
            "text": (
                "Half-buried near an old ring: something someone left as an "
                "offering, a long time ago."
            ),
            "outcome": {"item": {"item_id": "ash_ember", "qty": 1}},
        },
        {
            "type": "loot_bonus",
            "weight": 4,
            "text": (
                "Tucked into a crack in the hardened ash, wrapped in cloth gone "
                "stiff with age: a small charm, still warm to the touch."
            ),
            "outcome": {"item": {"item_id": "ember_charm", "qty": 1}},
        },

        # --- Choice Events ---
        {
            "type": "choice",
            "weight": 6,
            "text": (
                "One of the fire-rings looks recently relit — ash disturbed, "
                "faint warmth still rising from it. Kaelen didn't mention doing "
                "this."
            ),
            "choices": [
                {
                    "label": "Investigate",
                    "emoji": "🔍",
                    "text": (
                        "The ash here was disturbed on purpose, and recently — by "
                        "something, or someone, that wasn't Kaelen. You can't "
                        "shake the feeling as you walk away."
                    ),
                    "outcome": {"item": {"item_id": "lore_fragment", "qty": 1}},
                },
                {
                    "label": "Leave it",
                    "emoji": "🚶",
                    "text": "You leave the ring as you found it and move on.",
                    "outcome": {},
                },
            ],
        },
        {
            "type": "choice",
            "weight": 4,
            "text": (
                "The ash here is older — packed dense, almost glassy in places. "
                "At the center, something is half-buried: scorched, root-shaped, "
                "too large to be a tree stump. Nearby, barely visible under the "
                "ash, the shape of something else — curled, still, also "
                "half-buried."
            ),
            "choices": [
                {
                    "label": "Brush away the ash",
                    "emoji": "🪶",
                    "text": (
                        "You recognize enough of both shapes to know they're not "
                        "natural formations. Neither moves, but you feel watched "
                        "anyway. You back away slowly and don't look behind you "
                        "again."
                    ),
                    "outcome": {"item": {"item_id": "lore_fragment", "qty": 1}},
                },
                {
                    "label": "Leave it buried",
                    "emoji": "🚶",
                    "text": "Whatever it is, it can stay buried. You move on.",
                    "outcome": {},
                },
            ],
        },
    ],
}


def get_zone_events(zone_id: str) -> list:
    """Returns the event list for a given explore zone, or empty list if none defined."""
    return EXPLORE_EVENTS.get(zone_id, [])


# ─────────────────────────────────────────────
# Zone Loot Tables
# Each entry: (item_id, weight)
# ─────────────────────────────────────────────
ZONE_LOOT_TABLES = {
    "oakhavenOutpost_rottingPits": [
        ("trail_morsels",    3),
        ("moss_balm",        2),
        ("tether_orb",       1),
    ],
    "outpostWilds": [
        ("sun_kissed_berries", 4),
        ("trail_morsels",      2),
        ("moss_balm",          1),
    ],
    "weeping_chasm": [
        ("moss_balm",     3),
        ("tether_orb",    3),
        ("trail_morsels", 2),
    ],
    "mirefields": [
        ("trail_morsels",    4),
        ("mire_balm",        3),
        ("bog_reed_bundle",  3),
        ("tether_orb",       1),
    ],
    "whisperwoodGrove": [
        ("moss_balm",          3),
        ("sun_kissed_berries", 3),
        ("trail_morsels",      2),
        ("tether_orb",         1),
    ],
    "whisperwoodWilds": [
        ("trail_morsels",      3),
        ("moss_balm",          2),
        ("tether_orb",         2),
        ("sun_kissed_berries", 2),
    ],
    "ashenVerge": [
        ("ash_ember",   4),
        ("ember_charm", 1),
        ("trail_morsels", 2),
    ],
    # Whisperwood remnants and beyond added here when towns are built
}

_DEFAULT_LOOT_TABLE = [("sun_kissed_berries", 1)]


def get_zone_loot(zone_id: str) -> tuple[str, int]:
    """Picks a random item from the zone's loot table. Returns (item_id, qty=1)."""
    import random
    table = ZONE_LOOT_TABLES.get(zone_id, _DEFAULT_LOOT_TABLE)
    items = [entry[0] for entry in table]
    weights = [entry[1] for entry in table]
    return random.choices(items, weights=weights, k=1)[0], 1
