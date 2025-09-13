# core/narrative.py
from __future__ import annotations
from typing import Dict, Any, List, Optional
from .repository import Repository

class Narrative:
    def __init__(self, story: Dict[str, Any], repo: Repository):
        self.story = story
        self.repo = repo
        self._steps = {s["id"]: s for s in story.get("steps", [])}

    def first_step_id(self) -> str:
        return self.story.get("steps", [])[0]["id"]

    def get_step(self, step_id: str) -> Dict[str, Any]:
        step = self._steps.get(step_id)
        if not step:
            # Graceful fallback for missing content
            return {"id": "missing", "type": "narration",
                    "text": "⚠️ This part of the story is under construction."}
        return step

    async def apply_effects(self, user_id: int, effects: Optional[List[Dict[str, Any]]], *, modal_value: str | None = None):
        for eff in effects or []:
            op = eff.get("op")

            if op == "grant_pet":
                await self.repo.add_pet(user_id, eff["pet_id"])

            elif op == "grant_item":
                await self.repo.add_item(user_id, eff["item_id"], eff.get("qty", 1))

            elif op == "set_flag":
                await self.repo.set_flag(user_id, eff["flag"])

            elif op == "set_name_from_modal":
                # pull the text the user typed in the modal
                if modal_value:
                    await self.repo.update_player_name(user_id, modal_value)

            elif op == "set_main_pet_by_species":
                # optional op: set player's main pet to the first pet matching species
                await self.repo.set_main_pet_by_species(user_id, eff["pet_id"])
            # Add more ops over time; engine stays the same.

    async def choose(self, user_id: int, current_step_id: str, choice_id: str) -> str:
        step = self.get_step(current_step_id)
        if step.get("type") != "choice":
            return current_step_id  # no-op

        # find selected option
        chosen = next((o for o in step.get("options", []) if o["id"] == choice_id), None)
        if not chosen:
            return current_step_id

        await self.apply_effects(user_id, chosen.get("effects"))

        # next step resolution: prefer option.next, else step.next, else stay
        next_id = chosen.get("next") or step.get("next") or current_step_id
        await self.repo.set_story_state(user_id, self.story["id"], next_id)
        return next_id