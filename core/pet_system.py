# core/pet_system.py
# Contains the core game logic for an individual pet.

import math
from data.pets import PET_DATABASE
from data.skills import PET_SKILLS


class Pet:
    """Represents a single instance of a pet, handling all its mechanics."""

    def __init__(self, pet_data: dict):
        """
        Initializes a Pet object from a dictionary of data,
        typically loaded from the database.
        """
        if not isinstance(pet_data, dict):
            raise TypeError("pet_data must be a dictionary.")

        # --- Core Identifiers ---
        self.pet_id = pet_data.get('pet_id')
        self.owner_id = pet_data.get('owner_id')
        self.name = pet_data.get('name', 'Unnamed')
        self.species = pet_data.get('species')
        self.rarity = pet_data.get('rarity')
        self.pet_type = pet_data.get('pet_type')
        self.personality = pet_data.get('personality', 'Unknown')

        # --- Core Stats ---
        self.level = pet_data.get('level', 1)
        self.xp = pet_data.get('xp', 0)
        self.current_hp = pet_data.get('current_hp', 1)
        self.max_hp = pet_data.get('max_hp', 1)
        self.attack = pet_data.get('attack', 1)
        self.defense = pet_data.get('defense', 1)
        self.special_attack = pet_data.get('special_attack', 1)
        self.special_defense = pet_data.get('special_defense', 1)
        self.speed = pet_data.get('speed', 1)

        # --- Base Stats (for recalculation on level up) ---
        self.base_hp = pet_data.get('base_hp', 1)
        self.base_attack = pet_data.get('base_attack', 1)
        self.base_defense = pet_data.get('base_defense', 1)
        self.base_special_attack = pet_data.get('base_special_attack', 1)
        self.base_special_defense = pet_data.get('base_special_defense', 1)
        self.base_speed = pet_data.get('base_speed', 1)

        # --- Other Attributes ---
        self.skills = pet_data.get('skills', [])
        self.passive_ability = pet_data.get('passive_ability')

    def __repr__(self):
        return f"Pet(id={self.pet_id}, name='{self.name}', level={self.level})"

    def add_xp(self, amount: int) -> bool:
        """
        Adds XP to the pet, handles leveling up, and recalculates stats.
        Returns True if the pet leveled up, False otherwise.
        """
        if amount <= 0:
            return False

        self.xp += amount
        xp_for_next_level = self.level * 100
        leveled_up = False

        while self.xp >= xp_for_next_level:
            leveled_up = True
            self.level += 1
            self.xp -= xp_for_next_level

            self._recalculate_stats()
            self.current_hp = self.max_hp  # Fully heal on level up

            # Check for new skills to learn at this level (optional, can add later)

            xp_for_next_level = self.level * 100

        return leveled_up

    def _recalculate_stats(self):
        """Internal method to update stats based on level, base stats, and growth rates."""
        pet_base_data = PET_DATABASE.get(self.species)
        if not pet_base_data:
            print(f"Warning: Could not find base data for species '{self.species}' to recalculate stats.")
            return

        growth_rates = pet_base_data["growth_rates"]

        self.max_hp = math.floor(self.base_hp + (self.level - 1) * growth_rates['hp'])
        self.attack = math.floor(self.base_attack + (self.level - 1) * growth_rates['attack'])
        self.defense = math.floor(self.base_defense + (self.level - 1) * growth_rates['defense'])
        self.special_attack = math.floor(self.base_special_attack + (self.level - 1) * growth_rates['special_attack'])
        self.special_defense = math.floor(
            self.base_special_defense + (self.level - 1) * growth_rates['special_defense'])
        self.speed = math.floor(self.base_speed + (self.level - 1) * growth_rates['speed'])

    def take_damage(self, amount: int):
        """Reduces the pet's current HP."""
        self.current_hp = max(0, self.current_hp - amount)

    def heal(self, amount: int):
        """Increases the pet's current HP."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def to_dict_for_saving(self) -> dict:
        """Converts the pet's current state into a dictionary for database updates."""
        return {
            "level": self.level,
            "xp": self.xp,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "special_attack": self.special_attack,
            "special_defense": self.special_defense,
            "speed": self.speed,
            "skills": self.skills
            # Add any other attributes that can change and need to be saved
        }