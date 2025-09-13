# views/battle_actions.py
import discord
import asyncio
from data.pets import PET_DATABASE
from data.skills import PET_SKILLS
from utils.helpers import get_pet_image_url

class ForcedSwitchView(discord.ui.View):
    def __init__(self, player_roster):
        super().__init__(timeout=180) # Give them time to choose
        self.chosen_pet_id = None

        # Filter for only conscious pets
        conscious_pets = [p for p in player_roster if p.get('current_hp', 0) > 0]
        options = [
            discord.SelectOption(
                label=f"{pet['name']} (Lvl {pet['level']})",
                value=str(pet['pet_id']),
                description=f"HP: {pet['current_hp']}/{pet['max_hp']}"
            ) for pet in conscious_pets
        ]

        pet_select = discord.ui.Select(placeholder="Choose your next pet!", options=options)
        pet_select.callback = self.select_callback
        self.add_item(pet_select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.chosen_pet_id = int(interaction.data['values'][0])
        self.stop() # Stop the view, signaling a choice has been made


class EvolvingView(discord.ui.View):
    """
    A temporary view that displays the evolution animation.
    """

    def __init__(self, bot, battle_state, pet_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.battle_state = battle_state
        self.pet_id = pet_id
        self.message = None  # This will be set by the CombatView

        self.confirm_button = discord.ui.Button(label="Continue", style=discord.ButtonStyle.green, disabled=True)
        self.confirm_button.callback = self.confirm_callback
        self.add_item(self.confirm_button)

        asyncio.create_task(self.evolution_animation())

    async def evolution_animation(self):
        await asyncio.sleep(0.1)
        if not self.message:
            self.stop()
            return

        pet_data = self.battle_state.player_pet
        base_data = PET_DATABASE.get(pet_data['species'], {})
        evo_data = next(iter(base_data.get('evolutions', {}).values()), None)
        if not evo_data:
            self.stop()
            return

        new_species = evo_data['species']

        embed = discord.Embed(title=f"What?! {pet_data['name']} is evolving!", color=discord.Color.gold())
        embed.set_image(url=get_pet_image_url(pet_data['species']))
        await self.message.edit(content=None, embed=embed, view=self)
        await asyncio.sleep(2.5)

        embed.title = f"Congratulations! Your {pet_data['name']} evolved into a {new_species}!"
        embed.set_image(url=get_pet_image_url(new_species))
        self.confirm_button.disabled = False
        await self.message.edit(embed=embed, view=self)

    async def confirm_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

    async def on_timeout(self):
        self.stop()


class LearnSkillView(discord.ui.View):
    """
    A temporary view that prompts the player to replace a skill.
    """

    def __init__(self, pet_data, new_skill_id):
        super().__init__(timeout=180)
        self.chosen_skill_to_forget = None

        current_skills = pet_data.get('skills', [])
        options = [
            discord.SelectOption(label=PET_SKILLS[skill_id]['name'], value=skill_id)
            for skill_id in current_skills
        ]

        self.skill_select = discord.ui.Select(placeholder="Choose a skill to forget...", options=options)
        self.skill_select.callback = self.select_callback
        self.add_item(self.skill_select)

        self.cancel_button = discord.ui.Button(label="Don't Learn", style=discord.ButtonStyle.red)
        self.cancel_button.callback = self.cancel_callback
        self.add_item(self.cancel_button)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.chosen_skill_to_forget = self.skill_select.values[0]
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()

    async def on_timeout(self):
        self.stop()