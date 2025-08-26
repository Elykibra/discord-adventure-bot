# cogs/utils/views.py

# Import all view classes from the individual files
from .views_modals import RenamePetModal
from .views_character import PetView, SetMainPetView, ProfileView
# --- FIX: Removed outdated OutpostView and added the new WildsView ---
from .views_towns import TownView, WildsView, TravelView, QuestAcceptView, ShopLocationView
from .views_combat import CombatView, SwitchPetView

# You can also add a comment here to make it clear that this file
# is a central hub for all views.
# All views can be imported from this file.