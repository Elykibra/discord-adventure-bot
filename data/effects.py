# data/effects.py

STATUS_EFFECTS = {
    "flinch": {
        "blocks_action": True,
        "duration": 1,
        "block_message": "› {pet_name} flinched and couldn't move!"
    },
    "paralyze": {
        "blocks_action": True,
        "block_chance": 0.25,
        "block_message": "› {pet_name} is paralyzed and couldn't move!"
    },
    "confused": {
        "blocks_action": True,
        "block_chance": 0.5,
        "block_message": "› {pet_name} hurt itself in its confusion!",
        "on_block": {"type": "self_damage", "formula": "attack/4"}
    },
    "sleep": {
        "blocks_action": True,
        "duration": 2,
        "block_message": "› {pet_name} is fast asleep..."
    },
    "frozen": {
        "blocks_action": True,
        "block_chance": 0.8,
        "block_message": "› {pet_name} is frozen solid!"
    },
    "stun": {
        "blocks_action": True,
        "duration": 1,
        "block_message": "› {pet_name} is stunned!"
    }
}