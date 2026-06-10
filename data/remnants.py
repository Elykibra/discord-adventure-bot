# data/remnants.py
# Remnants — Points of Interest found between towns.
#
# Remnants are optional locations discovered while traveling between towns.
# They are not full towns — no inn, no shops — but they can have:
#   - NPCs (quest givers, lore, merchants)
#   - Explore zones (unique encounters)
#   - Quest hooks
#   - Unique items or drops
#
# "between" defines which two towns flank this remnant on the road.
# "availability" can restrict when the remnant is accessible (day/night/all).
# "gloom_level" — if set, all battles here start with this Gloom % preloaded.

REMNANTS = {

    # =========================================================================
    # ROAD: Oakhaven Outpost ↔ Whisperwood Grove
    # =========================================================================

    "weeping_chasm": {
        "id": "weeping_chasm",
        "name": "The Weeping Chasm",
        "emoji": "🕳️",
        "between": ["oakhavenOutpost", "whisperwoodGrove"],
        "connections": {
            "oakhavenOutpost": "Oakhaven Outpost",
            "mirefields": "Mirefields",
        },
        "connection_costs": {
            "oakhavenOutpost": 8,
            "mirefields": 14,
        },
        "connection_requirements": {
            "mirefields": "quest_a_guildsmans_first_steps_completed",
        },
        "availability": "all",
        "gloom_level": 25,
        "description_day": (
            "A jagged tear in the earth stretches across the road, as if the land itself "
            "was ripped open long ago. A faint, cold mist rises from below, carrying with it "
            "the distant sound of something — breathing. Guild records mark this as the site "
            "where The Gloom first breached the surface world."
        ),
        "description_night": (
            "At night, the Chasm seems to exhale — a rhythmic pulse of cold air that makes "
            "the trees lean away. The mist thickens into something almost visible, and the "
            "darkness below feels aware of you."
        ),
        # -----------------------------------------------------------------
        # Locations — same pattern as towns.py
        # Availability: 'all' | 'day' | 'night'
        # required_flag: greyed out until player has this flag
        # required_quest: greyed out until this quest is active
        # -----------------------------------------------------------------
        "locations": {
            "chasms_edge": {
                "name": "The Chasm's Edge",
                "emoji": "🕳️",
                "menu_description": "The lip of the Chasm. Cold. The source of the Gloom.",
                "availability": "all",
                "description_day": (
                    "A narrow ledge of cracked stone along the chasm's rim. The Guild has "
                    "bolted warning markers into the rock, but most have tilted with the "
                    "settling ground. The air here smells of cold metal and something older."
                ),
                "description_night": (
                    "The mist curls upward around your ankles. The darkness below is total. "
                    "Nothing attacks. Something is just checking."
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_chasms_edge",
                        "text": (
                            "The cold hits before you reach the rim. Your pet stops a full "
                            "step behind you and won't come closer. From below — not wind, "
                            "not echo — something like breathing."
                        ),
                    },
                    {
                        "condition": "time:night",
                        "once": False,
                        "text": (
                            "*The mist curls upward around your ankles. "
                            "Nothing attacks. Something is just checking.*"
                        ),
                    },
                ],
                "services": {
                    "explore_zone": "weeping_chasm",
                    "gloom_level": 25,
                },
                "npcs": {},
            },

            "wardens_post": {
                "name": "The Warden's Post",
                "emoji": "🛡️",
                "menu_description": "Warden Orin's watch station. Manned during daylight hours.",
                "availability": "day",
                "description_day": (
                    "A solid Guild-issue post: a small fire, a folding chair, a logbook "
                    "worn thin from use. Warden Orin keeps his eyes on the Chasm with the "
                    "patience of someone who has been doing this a long time."
                ),
                "description_night": (
                    "A folded note is pinned to the post with a Guild insignia pin.\n\n"
                    "*\"Gone at dark. You should be too. — O.\"*"
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_wardens_post",
                        "text": (
                            "Orin glances up from his logbook. *\"Road's passable. "
                            "Mostly. Don't linger at the edge — the creatures here "
                            "are drawn to the source and they don't watch where they're going.\"*"
                        ),
                    },
                    {
                        "condition": "flag:quest_a_guildsmans_first_steps_completed",
                        "once": True,
                        "flag": "orin_recruit_acknowledged",
                        "text": (
                            "Orin looks up, recognizes the Guild insignia. "
                            "*\"Recruit. Good — you made it this far.\"* "
                            "A pause. *\"That's not nothing.\"*"
                        ),
                    },
                ],
                "services": {},
                "npcs": {
                    "warden_orin": {
                        "name": "Warden Orin",
                        "role": "Guild Warden",
                        "emoji": "🛡️",
                        "availability": "day",
                        "pet": {
                            "species": "Frostbile",
                            "nickname": None,
                            "nickname_visible_flag": None,
                            "description": (
                                "A Frostbile moves along the chasm wall a few feet behind Orin, "
                                "unhurried. It followed him for weeks before he stopped chasing "
                                "it off. He does not consider that a bonding experience."
                            ),
                            "player_species_reactions": {},
                        },
                        "dialogue": {
                            "default": (
                                "This is as close as most people get. The Chasm draws "
                                "Gloom-Touched creatures — they're drawn to the source. "
                                "I keep watch so travelers can pass safely. Mostly."
                            ),
                            "lore_prompt": (
                                "The records say The Gloom first surfaced here. I believe it. "
                                "Some nights I can feel it thinking."
                            ),
                            "returning_recruit": (
                                "Ah — a Guild recruit. Good. The road east gets worse before "
                                "it gets better. Keep your pet fed and your energy up."
                            ),
                            "lore_east_wall": (
                                "*\"The east section of the wall is webbed over some mornings. "
                                "Something large made that overnight.\"* "
                                "He doesn't elaborate. *\"I don't go near it.\"*"
                            ),
                            "lore_breathing": (
                                "*\"Some mornings the mist is different. Heavier. "
                                "Like something exhaled the whole of it at once.\"* "
                                "He says it the way you'd report weather."
                            ),
                        },
                    },
                },
            },

            "scholars_camp": {
                "name": "The Scholar's Camp",
                "emoji": "📜",
                "menu_description": "A field researcher's camp. Appears occupied — sometimes.",
                "availability": "all",
                "required_quest": "echoes_from_below",   # greyed until quest is active
                "description_day": (
                    "A small camp pressed against the rock face away from the wind. "
                    "Notebooks, vials, and equipment cases are stacked with the organised "
                    "chaos of someone who knows exactly where everything is. "
                    "A lamp burns low on a flat stone."
                ),
                "description_night": (
                    "The lamp is still burning. The notebooks are still open. "
                    "Kael doesn't sleep much when he's onto something."
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_scholars_camp",
                        "text": (
                            "Kael looks up immediately, already talking. "
                            "*\"You're here — good. I've been waiting for someone "
                            "Vexia would actually trust with this. "
                            "The origin point is right here and nobody studies it properly.\"*"
                        ),
                    },
                ],
                "services": {},
                "npcs": {
                    "lore_keeper_kael": {
                        "name": "Lore-Keeper Kael",
                        "role": "Guild Scholar",
                        "emoji": "🔬",
                        "availability": "all",
                        "pet": {
                            "species": "Duskspinner",
                            "nickname": "threnody",
                            "nickname_visible_flag": None,  # Kael tells everyone immediately
                            "description": (
                                "A Duskspinner perches on the edge of Kael's equipment case, "
                                "perfectly still. He named it Threnody — a funeral song — "
                                "after the Gloom's origin in collective sorrow. "
                                "He will explain the etymology if asked. You didn't ask."
                            ),
                            "player_species_reactions": {
                                "Grimweave": (
                                    "*\"Oh, a Grimweave. Threnody's base form — "
                                    "interesting choice for a traveler. "
                                    "Give it time and the right conditions.\"*"
                                ),
                            },
                        },
                        "dialogue": {
                            "default": (
                                "You found me. Good — I wasn't sure Vexia would send anyone "
                                "capable. The origin point is right here and nobody bothers "
                                "to study it properly. I need samples. Three vials of "
                                "gloom-mist from the Edge. Can you do that?"
                            ),
                            "samples_collected": (
                                "These are clean samples — remarkable. The density here is "
                                "unlike anything recorded further out. When you reach the "
                                "Oasis, find the Obsidian Monoliths. I'll be there. "
                                "There's something I need to show you."
                            ),
                            "lore_gloom_origin": (
                                "The Gloom didn't spread from a single point by accident. "
                                "Every record points here — the Chasm — as the breach site. "
                                "My theory: collective grief. A catastrophic loss, enough "
                                "souls in enough pain at once to tear something open. "
                                "The Guild doesn't like that theory. Too difficult to quantify."
                            ),
                            "lore_hollowed_vs_corrupted": (
                                "Corrupted pets can still be reached — the Gloom has touched "
                                "them but hasn't consumed them. There's still something there "
                                "to work with. Hollowed is different. When a creature Hollows, "
                                "there's nothing left that remembers being a creature. "
                                "That distinction matters. Remember it."
                            ),
                            "lore_east_wall": (
                                "He shows you a single research note. "
                                "*'Specimen of unusual scale observed on east face. "
                                "Preliminary classification impossible.'* "
                                "One entry. The next page is blank."
                            ),
                        },
                    },
                },
            },

            "lookout_hollow": {
                "name": "The Lookout Hollow",
                "emoji": "🗡️",
                "menu_description": "A weathered hollow. Someone has been here a long time.",
                "availability": "all",
                "description_day": (
                    "A natural depression in the rock, sheltered from the wind and set back "
                    "from the Chasm. It's been lived in — a fire ring, a bedroll, a row of "
                    "marked stones that might be a personal tallying system. "
                    "Gretta is here, as she always is."
                ),
                "description_night": (
                    "The fire is low but steady. Gretta is awake. "
                    "She's always awake at night — she learned not to sleep deeply here "
                    "a long time ago."
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_lookout_hollow",
                        "text": (
                            "Gretta looks up from the fire. Takes you in once, top to bottom. "
                            "*\"Guild sends another one.\"* She looks back at the fire. "
                            "*\"They always look the same.\"*"
                        ),
                    },
                    {
                        "condition": "has_pet_species:Threshling",
                        "once": True,
                        "flag": "gretta_threshling_reaction_seen",
                        "text": (
                            "Gretta's eyes go to your pet. Stay there longer than usual. "
                            "*\"You caught one of those.\"* Not a question. "
                            "She looks back at the half-solid shape near her fire. "
                            "Doesn't say anything else."
                        ),
                    },
                ],
                "services": {
                    "rest": {
                        "type": "rough_camp",
                        "cost": 0,
                        "energy_restore": 20,
                        "health_restore_percent": 0,
                        "flavor": (
                            "Gretta gestures at a flat rock near the fire without looking up. "
                            "*\"Sit. Don't talk.\"* "
                            "You rest in silence. It's enough."
                        ),
                    },
                },
                "npcs": {
                    "grim_gretta": {
                        "name": "\"Grim\" Gretta",
                        "role": "Chasm Watcher",
                        "emoji": "🗡️",
                        "availability": "all",
                        "pet": {
                            "species": "Threshling",
                            "nickname": None,
                            "nickname_visible_flag": None,
                            "description": (
                                "Something half-solid crouches near Gretta's fire. "
                                "Parts of it solid, parts mist. One eye clear, one eye dark. "
                                "She didn't purify it. She made it clear who was in charge. "
                                "It stays because she makes it stay."
                            ),
                            "player_species_reactions": {},
                        },
                        "dialogue": {
                            "default": (
                                "Guild sends another one. They always look the same — "
                                "hopeful. The Chasm fixes that eventually. "
                                "What do you want?"
                            ),
                            "player_has_pet": (
                                "That creature following you — you trust it? "
                                "The Gloom finds the ones you're attached to first. "
                                "Keep it strong. Soft bonds don't survive this road."
                            ),
                            "subdue_path_intro": (
                                "You want to know what I know? Fine. "
                                "The Guild tells you to heal corrupted creatures. "
                                "I've watched that fail more times than you've been alive. "
                                "Control is not cruelty. It's honesty. "
                                "There's another way — if you're willing to hear it."
                            ),
                            "lore_deep_chasm": (
                                "*\"Nothing worth finding out there.\"*"
                            ),
                            "lore_deep_chasm_pressed": (
                                "She looks at you for a long moment. "
                                "*\"The breathing. You've heard it. "
                                "Don't go looking for what makes it.\"*"
                            ),
                            "returning_high_rank": (
                                "She looks you over once. Looks back at the fire. "
                                "*\"Still here.\"* That's all she gives you. "
                                "From Gretta, it means something."
                            ),
                        },
                    },
                },
            },
        },
    },

    "mirefields": {
        "id": "mirefields",
        "name": "The Mirefields",
        "emoji": "🌫️",
        "between": ["oakhavenOutpost", "whisperwoodGrove"],
        "connections": {
            "weeping_chasm": "Weeping Chasm",
            "whisperwoodGrove": "Whisperwood Grove",
        },
        "connection_costs": {
            "weeping_chasm": 12,
            "whisperwoodGrove": 14,
        },
        "availability": "all",
        "gloom_level": 8,
        "description_day": (
            "A stretch of dense, boggy terrain where the road becomes little more than a "
            "muddy suggestion. Twisted undergrowth crowds the path and the air smells of "
            "damp earth and rot. The creatures here are territorial and aggressive — not "
            "Gloom-touched, just mean. The ruins of an old crossroads camp can be spotted "
            "through the fog, long since reclaimed by the mire."
        ),
        "description_night": (
            "The fog thickens after dark, swallowing what little visibility remained. "
            "Sounds carry strangely through the mire — snapping branches, low growls, "
            "the occasional splash of something moving through the water. "
            "Not the place to stop and rest."
        ),
        "locations": {
            "bogside_trail": {
                "name": "The Bogside Trail",
                "emoji": "🌫️",
                "menu_description": "The main stretch through the mire. Creatures lurk nearby.",
                "availability": "all",
                "description_day": (
                    "The road narrows to a muddy track hemmed in by twisted undergrowth. "
                    "The ground shifts unpredictably underfoot. Territorial creatures "
                    "watch from the fog — not Gloom-touched, just mean and hungry."
                ),
                "description_night": (
                    "The trail is nearly invisible in the dark. Every sound is amplified. "
                    "Moving through here at night requires patience and a steady pet."
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_bogside_trail",
                        "text": (
                            "The path disappears under two inches of brown water. "
                            "You can't tell if it continues forward or if you've already stepped off it. "
                            "Somewhere to your left, something shifts in the reeds."
                        ),
                    },
                    {
                        "condition": "time:night",
                        "once": False,
                        "text": (
                            "*The fog is worse at night. You knew that before you came out here.*"
                        ),
                    },
                ],
                "services": {
                    "explore_zone": "mirefields",
                    "gloom_level": 8,
                },
                "npcs": {},
            },

            "sables_post": {
                "name": "Sable's Post",
                "emoji": "🪤",
                "menu_description": "A trapper's camp off the main trail. Supplies available.",
                "availability": "all",
                "description_day": (
                    "A compact camp built from salvaged wood and waterproofed canvas. "
                    "Traps and pelts hang from a line. Sable runs a lean operation — "
                    "everything here has a purpose. A large armored creature rests on "
                    "a flat rock near the water's edge, motionless."
                ),
                "description_night": (
                    "The camp lantern is on. Sable keeps late hours. "
                    "The armored creature on the flat rock hasn't moved. "
                    "You're not sure it's sleeping."
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_sables_post",
                        "text": (
                            "Sable glances up from her work. *\"You lost? Most people "
                            "don't come through here by choice. I've got supplies — "
                            "nothing fancy, but it'll keep you alive.\"*"
                        ),
                    },
                    {
                        "condition": "has_pet_species:Murkback",
                        "once": True,
                        "flag": "sable_murkback_reaction_seen",
                        "text": (
                            "Sable's eyes drop to your pet for a moment. "
                            "*\"Caught one of those, did you. Give it time.\"* "
                            "She doesn't elaborate."
                        ),
                    },
                    {
                        "condition": "time:night",
                        "once": False,
                        "text": (
                            "*\"You're braver than most, traveling through here at night. "
                            "Or dumber. Hard to tell.\"*"
                        ),
                    },
                ],
                "services": {
                    "shop": True,
                    "shop_items": ["mire_balm", "trail_morsels", "tether_orb", "bog_reed_bundle", "murk_fragment"],
                    "shop_items_night": ["trail_morsels", "tether_orb", "bog_reed_bundle", "murk_fragment"],  # mire_balm out of stock at night
                    "rest": {
                        "type": "rough_camp",
                        "cost": 0,
                        "energy_restore": 20,
                        "health_restore_percent": 0,
                        "flavor": (
                            "Sable tosses you a strip of dried bark to chew on and points "
                            "to a dry log. You sit in silence while the fog drifts past. "
                            "*\"Don't get comfortable.\"*"
                        ),
                    },
                },
                "npcs": {
                    "sable": {
                        "name": "Sable",
                        "role": "Bog Trapper",
                        "emoji": "🪤",
                        "availability": "all",
                        "pet": {
                            "species": "murkwall",
                            "nickname": "ledge",
                            "nickname_visible_flag": "sable_ledge_name_revealed",
                            "description": (
                                "A large armored creature rests on a flat rock near the "
                                "water's edge. It doesn't patrol. It just exists there. "
                                "Everything else in the mire has done the math."
                            ),
                            "player_species_reactions": {
                                "Murkback": (
                                    "*\"Caught one of those, did you. Give it time.\"* "
                                    "She doesn't elaborate."
                                ),
                            },
                        },
                        "dialogue": {
                            "default": (
                                "You lost? Most people don't come through here by choice. "
                                "I've got supplies if you need them — nothing fancy, "
                                "but it'll keep you alive."
                            ),
                            "night": (
                                "You're braver than most, traveling through here at night. "
                                "Or dumber. Hard to tell. Watch your step — the mire shifts after dark."
                            ),
                            "sell": "Take what you need and move on. I don't do small talk.",
                            "lore_crossroads": (
                                "Used to be busy. Road ran right through — traders, couriers, "
                                "a waystation that served maybe thirty people a day. Then one wet "
                                "season the mire came up and didn't stop. "
                                "*\"Not everything's meant to last.\"*"
                            ),
                            "lore_ferryn": (
                                "*\"She's going to measure every reed in this bog and go home "
                                "with a headache.\"* No malice in it. She just knows how this ends."
                            ),
                            "lore_deep_mire": (
                                "*\"Nothing worth finding out there.\"*"
                            ),
                            "returning_player": (
                                "She recognizes you. Doesn't say anything about it. "
                                "Just sets out the usual without being asked."
                            ),
                        },
                    },
                },
            },

            "reed_hollow": {
                "name": "The Reed Hollow",
                "emoji": "🌿",
                "menu_description": "A naturalist's camp in the reeds. Someone is studying the mire.",
                "availability": "all",
                # TODO: seasonal logic — Ferryn is gone at higher rank/story flag.
                # When absent: show her field notes instead of NPC. Wire when quest line is ready.
                "description_day": (
                    "A tidy research camp tucked into a bend in the reeds. Charts and "
                    "specimen jars line a folding table. A small creature is perched on "
                    "the edge of a water sample jar, watching it intently."
                ),
                "description_night": (
                    "A lantern burns low over the research table. Notes are spread across "
                    "it, weighted down against the breeze. She works late."
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_reed_hollow",
                        "text": (
                            "A young woman looks up from her instruments with immediate "
                            "curiosity. *\"Oh — a traveler. Perfect timing, actually. "
                            "Have you noticed anything unusual on the Bogside Trail? "
                            "Unusual even for here, I mean.\"*"
                        ),
                    },
                    {
                        "condition": "has_pet_species:Pallefin",
                        "once": True,
                        "flag": "ferryn_pallefin_reaction_seen",
                        "text": (
                            "Ferryn's eyes go wide. *\"Is that — that's a Pallefin. "
                            "Where did you find it? I've only seen Silt behave like that "
                            "near the crossroads boundary — does yours do that too?\"* "
                            "She's already reaching for her notes."
                        ),
                    },
                ],
                "npcs": {
                    "ferryn": {
                        "name": "Ferryn",
                        "role": "Field Naturalist",
                        "emoji": "🌿",
                        "availability": "all",
                        "pet": {
                            "species": "pallefin",
                            "nickname": "silt",
                            "nickname_visible_flag": None,  # Ferryn tells everyone immediately
                            "description": (
                                "A small, almost translucent creature perches on the rim "
                                "of a water sample jar, watching the surface intently. "
                                "Ferryn named it on the first day. She will tell you this "
                                "story whether you ask or not."
                            ),
                            "player_species_reactions": {
                                "Pallefin": (
                                    "*\"You have one too! I named mine Silt — it was in "
                                    "the silt, it seemed right. What's yours called?\"*"
                                ),
                            },
                        },
                        "dialogue": {
                            "default": (
                                "Oh — yes, hello. I'm cataloguing the bog expansion. "
                                "The mire is growing faster than natural rates should allow. "
                                "Something is accelerating it. I don't know what yet, "
                                "but the instruments point toward the Old Crossroads."
                            ),
                            "about_sable": (
                                "*\"She knows this place better than anyone. She just "
                                "doesn't seem curious about why it is the way it is.\"* "
                                "A pause. *\"She told me not to go near the crossroads. "
                                "I'm... taking that under advisement.\"*"
                            ),
                            "lore_expansion": (
                                "The growth rate is wrong. Bog expansion is measurable — "
                                "predictable, even. This isn't that. Something here is "
                                "feeding it. My instruments read differently near the "
                                "Old Crossroads than anywhere else in the mire."
                            ),
                            "lore_crossroads": (
                                "*\"I want to document it properly. Get close, take "
                                "readings. Sable says not to. She didn't explain why — "
                                "just 'not to.' I've noted it as a local superstition "
                                "for now, but...\"* She trails off, glancing toward the fog."
                            ),
                        },
                    },
                },
            },

            "old_crossroads": {
                "name": "The Old Crossroads",
                "emoji": "🪨",
                "menu_description": "Ruins of a waystation, half-swallowed by the mire.",
                "availability": "all",
                "description_day": (
                    "The stone foundations of the old waystation are still visible — "
                    "half-submerged, overgrown with dark reeds. The signpost still stands. "
                    "Three arrows, all pointing different directions. No legible names. "
                    "Something has been dragging through here. Recently. "
                    "There is an unnatural stillness to this part of the mire."
                ),
                "description_night": (
                    "The ruins are barely visible in the fog. The signpost casts a long "
                    "shadow in the lantern light. You have the distinct sense that "
                    "something here is aware of you. Not hostile. Just aware."
                ),
                "on_enter": [
                    {
                        "condition": "first_visit",
                        "flag": "visited_old_crossroads",
                        "text": (
                            "The air here is different. Heavier. Your pet moves closer "
                            "to you without being told."
                        ),
                    },
                    {
                        "condition": "time:night",
                        "once": False,
                        "text": (
                            "*You came here at night. That was your choice.*"
                        ),
                    },
                ],
                # TODO: Choice event (take the ledger) — wire when quest lines are ready.
                # The Mirewarden territory interaction is lore only for now.
                "services": {},
                "npcs": {},
            },
        },
    },

    # =========================================================================
    # ROAD: Whisperwood Grove ↔ Sunstone Oasis
    # =========================================================================

    "glade_of_whispers": {
        "id": "glade_of_whispers",
        "name": "The Glade of Whispers",
        "emoji": "✨",
        "between": ["whisperwoodGrove", "sunstoneOasis"],
        "connections": {
            "whisperwoodGrove": "Whisperwood Grove",
            "sunstoneOasis": "Sunstone Oasis",
        },
        "availability": "all",
        "gloom_level": 0,
        "description_day": (
            "A small, perfectly circular glade where sunlight filters through a natural "
            "opening in the canopy. The air hums faintly — not with danger, but with something "
            "older and calmer. Flowers here bloom year-round, and the grass is always soft. "
            "Adventurers often stop to rest."
        ),
        "description_night": (
            "At night the glade is lit by the soft glow of Moonpetal flowers that only "
            "bloom here after dark. The humming grows quieter but doesn't stop. "
            "It feels like the forest is holding its breath — in a good way."
        ),
        "lore": (
            "One of the few places in Aethelgard where the Gloom has never taken hold. "
            "Scholars believe a Great Spirit once rested here, leaving a lasting impression "
            "on the land. Pets recover faster in this glade."
        ),
        "npcs": {},
        "services": {
            "rest": {
                "type": "glade",
                "cost": 0,
                "energy_restore_percent": 25,
                "health_restore_percent": 50,  # Natural healing, free
            }
        },
    },

    # =========================================================================
    # STUBS — Further roads (fill in when those towns are built)
    # =========================================================================

    "obsidian_monoliths": {
        "id": "obsidian_monoliths",
        "name": "The Obsidian Monoliths",
        "emoji": "🗿",
        "between": ["sunstoneOasis", "ironforge"],
        "availability": "all",
        "description_day": "Strange formations of jet-black stone rise from the desert floor, humming with a faint magnetic energy. Compasses are useless here.",
        "npcs": {},
        "services": {},
    },

    "shifting_dunes": {
        "id": "shifting_dunes",
        "name": "The Shifting Dunes",
        "emoji": "🏜️",
        "between": ["sunstoneOasis", "aethelgardsRest"],
        "availability": "all",
        "description_day": "A treacherous desert region where the sands move on their own, erasing paths overnight. More than one caravan has been lost here.",
        "npcs": {},
        "services": {},
    },

    "lost_guild_hall": {
        "id": "lost_guild_hall",
        "name": "The Lost Guild Hall",
        "emoji": "🏚️",
        "between": ["frostfallPeak", "blackwaterMarsh"],
        "availability": "all",
        "description_day": "An ancient, overgrown ruin of what was once a proud Guild Hall. Ivy has reclaimed the walls, and the records inside — if any survived — could be invaluable.",
        "npcs": {},
        "services": {},
    },

    "sunken_ship_graveyard": {
        "id": "sunken_ship_graveyard",
        "name": "The Sunken Ship Graveyard",
        "emoji": "⚓",
        "between": ["aethelgardsRest", "skylightSpire"],
        "availability": "all",
        "description_day": "A treacherous stretch of reef and rusted shipwrecks, half-submerged and groaning in the current. Salvagers come here, but not all of them leave.",
        "npcs": {},
        "services": {},
    },

    "wyrmwood_forest": {
        "id": "wyrmwood_forest",
        "name": "The Wyrmwood Forest",
        "emoji": "🌑",
        "between": ["blackwaterMarsh", "ironforge"],
        "availability": "all",
        "description_day": "A dark, twisted forest where the trees grow in unnatural spirals and the canopy blocks all sunlight. The Gloom runs deep here.",
        "npcs": {},
        "services": {},
    },

    "cloudspire_outpost": {
        "id": "cloudspire_outpost",
        "name": "The Cloudspire Outpost",
        "emoji": "☁️",
        "between": ["skylightSpire", "silvermoonGlade"],
        "availability": "all",
        "description_day": "A small floating platform suspended between two peaks by ancient chain-work. The view is breathtaking. The wind is brutal.",
        "npcs": {},
        "services": {},
    },

    "scholars_retreat": {
        "id": "scholars_retreat",
        "name": "The Scholar's Retreat",
        "emoji": "📚",
        "between": ["silvermoonGlade", "sunkenCity"],
        "availability": "day",
        "description_day": "A secluded library hidden between two cliff faces, accessible only by a narrow rope bridge. The collection inside spans centuries of Aethelgard's history.",
        "npcs": {},
        "services": {},
    },

    "chasm_of_whispers": {
        "id": "chasm_of_whispers",
        "name": "The Chasm of Whispers",
        "emoji": "🌀",
        "between": ["ironforge", "skylightSpire"],
        "availability": "all",
        "description_day": "A deep, winding canyon whose walls amplify sound in strange ways. Voices echo here that have no source. Travelers move through quickly.",
        "npcs": {},
        "services": {},
    },

    "forgotten_grove": {
        "id": "forgotten_grove",
        "name": "The Forgotten Grove",
        "emoji": "🌸",
        "between": ["blackwaterMarsh", "ironforge"],  # hidden within Wyrmwood
        "availability": "all",
        "description_day": "A beautiful grove hidden within the Wyrmwood Forest that has miraculously resisted the Gloom. The contrast with the surrounding darkness is striking.",
        "npcs": {},
        "services": {},
    },

    "serpents_coil": {
        "id": "serpents_coil",
        "name": "The Serpent's Coil",
        "emoji": "🐍",
        "between": ["sunkenCity", "dragonsTooth"],
        "availability": "all",
        "description_day": "A treacherous winding path through ancient ruins that corkscrews down into a valley. The stonework is unlike anything built by current civilization.",
        "npcs": {},
        "services": {},
    },

}
