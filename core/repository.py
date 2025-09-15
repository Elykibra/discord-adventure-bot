# core/repository.py
from __future__ import annotations
from typing import Protocol, Dict, Any, List, Optional, Set
import asyncio

# ---------- Protocol (engine uses only this) ----------
class Repository(Protocol):
    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]: ...
    async def create_player(self, user_id: int, defaults: Dict[str, Any]) -> Dict[str, Any]: ...
    async def save_player(self, user_id: int, data: Dict[str, Any]) -> None: ...
    async def add_item(self, user_id: int, item_id: str, qty: int = 1) -> None: ...
    async def add_pet(self, user_id: int, pet_id: str) -> None: ...
    async def set_flag(self, user_id: int, flag: str) -> None: ...
    async def get_story_state(self, user_id: int) -> Dict[str, Any]: ...
    async def set_story_state(self, user_id: int, section_id: str, step_id: str) -> None: ...

# ---------- In-memory (dev / tests) ----------
class MemoryRepository:
    def __init__(self):
        self.players: Dict[int, Dict[str, Any]] = {}
    async def update_player_name(self, user_id: int, name: str) -> None:
        p = self.players[user_id]
        p["name"] = name

    async def set_main_pet_by_species(self, user_id: int, pet_species: str) -> None:
        p = self.players[user_id]
        for pet in p["pets"]:
            if pet.get("pet_id") == pet_species:
                p["main_pet_id"] = pet_species
                return
    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.players.get(user_id)

    async def create_player(self, user_id: int, defaults: Dict[str, Any]) -> Dict[str, Any]:
        self.players[user_id] = {
            "id": user_id,
            "name": defaults.get("name", f"Adventurer {user_id}"),
            "section_id": defaults.get("section_id", "section_0"),
            "story_step_id": defaults.get("story_step_id", "intro_1"),
            "flags": set(defaults.get("flags", [])),
            "inventory": [],
            "pets": [],
            "energy": defaults.get("energy", 10),
            "warp_unlocks": set(),
        }
        return self.players[user_id]

    async def save_player(self, user_id: int, data: Dict[str, Any]) -> None:
        if user_id not in self.players:
            await self.create_player(user_id, data)
        else:
            self.players[user_id].update(data)

    async def add_item(self, user_id: int, item_id: str, qty: int = 1) -> None:
        p = self.players[user_id]
        inv = p["inventory"]
        for it in inv:
            if it["item_id"] == item_id:
                it["qty"] += qty
                break
        else:
            inv.append({"item_id": item_id, "qty": qty})

    async def add_pet(self, user_id: int, pet_id: str) -> None:
        p = self.players[user_id]
        p["pets"].append({"pet_id": pet_id, "nickname": None})

    async def set_flag(self, user_id: int, flag: str) -> None:
        self.players[user_id]["flags"].add(flag)

    async def get_story_state(self, user_id: int) -> Dict[str, Any]:
        p = self.players[user_id]
        return {"section_id": p["section_id"], "story_step_id": p["story_step_id"]}

    async def set_story_state(self, user_id: int, section_id: str, step_id: str) -> None:
        p = self.players[user_id]
        p["section_id"] = section_id
        p["story_step_id"] = step_id

    async def get_session_message_id(self, user_id: int) -> int | None:
        return self.players[user_id].get("session_message_id")

    async def set_session_message_id(self, user_id: int, message_id: int) -> None:
        self.players[user_id]["session_message_id"] = int(message_id)

    async def restore_energy_full(self, user_id: int) -> None:
        p = await self.get_player(user_id)
        if p:
            p["energy"] = int(p.get("max_energy", p.get("energy", 0)))
            await self.save_player(user_id, p)

    async def add_energy(self, user_id: int, amount: int) -> None:
        p = await self.get_player(user_id)
        if p:
            cur = int(p.get("energy", 0))
            mx = int(p.get("max_energy", cur))
            p["energy"] = min(cur + int(amount), mx)
            await self.save_player(user_id, p)

    async def spend_energy(self, user_id: int, amount: int) -> bool:
        p = await self.get_player(user_id)
        if not p:
            return False
        need = int(amount)
        cur = int(p.get("energy", 0))
        if cur < need:
            return False
        p["energy"] = cur - need
        await self.save_player(user_id, p)
        return True

# ---------- Your real DB repo (skeleton) ----------
class SqlRepository:
    def __init__(self, pool):
        self.pool = pool
        self._player_pk = None

    async def update_player_name(self, user_id: int, name: str) -> None:
        async with self.pool.acquire() as con:
            await con.execute(
                "UPDATE players SET username=$2 WHERE user_id=$1",
                user_id, name
            )

    async def set_main_pet_by_species(self, user_id: int, species: str):
        async with self.pool.acquire() as con:
            await con.execute(
                "UPDATE players SET main_pet_species=$2 WHERE user_id=$1",
                user_id, species
            )

    async def get_player(self, user_id: int):
        async with self.pool.acquire() as con:
            row = await con.fetchrow(
                """SELECT user_id, username, section_id, story_step_id,
                          current_energy, max_energy, main_pet_id
                   FROM players WHERE user_id=$1""",
                user_id,
            )
            if not row:
                return None
            flags = {r["flag"] for r in await con.fetch(
                "SELECT flag FROM player_flags WHERE player_id=$1", user_id
            )}
            return {
                "id": row["user_id"],
                "name": row["username"],
                "section_id": row["section_id"],
                "story_step_id": row["story_step_id"],
                "energy": row["current_energy"],
                "max_energy": row["max_energy"],
                "main_pet_id": row["main_pet_id"],
                "flags": flags,
            }

    async def create_player(self, user_id: int, defaults: dict):
        async with self.pool.acquire() as con:
            await con.execute(
                """INSERT INTO players (user_id, username, section_id, story_step_id, current_energy, max_energy)
                   VALUES ($1, $2, $3, $4, $5, $6)
                   ON CONFLICT (user_id) DO NOTHING""",
                user_id,
                defaults.get("name", f"Adventurer {user_id}"),
                defaults.get("section_id", "section_0"),
                defaults.get("story_step_id", "intro_1"),
                defaults.get("energy", 10),
                defaults.get("max_energy", 10),
            )
        return await self.get_player(user_id)

    async def save_player(self, user_id: int, data: dict):
        async with self.pool.acquire() as con:
            await con.execute(
                "UPDATE players SET name=$2, section_id=$3, story_step_id=$4, energy=$5 WHERE id=$1",
                user_id, data.get("name"), data.get("section_id"), data.get("story_step_id"), data.get("energy", 10)
            )

    async def add_item(self, user_id: int, item_id: str, qty: int = 1):
        async with self.pool.acquire() as con:
            await con.execute(
                """INSERT INTO inventory (player_id, item_id, qty)
                   VALUES ($1, $2, $3)
                   ON CONFLICT (player_id, item_id) DO UPDATE SET qty = inventory.qty + EXCLUDED.qty""",
                user_id, item_id, qty
            )

    async def add_pet(self, player_id: int, species: str):
        async with self.pool.acquire() as con:
            await con.execute(
                "INSERT INTO pets (player_id, species) VALUES ($1, $2)",
                player_id, species
            )

    async def set_flag(self, user_id: int, flag: str):
        async with self.pool.acquire() as con:
            await con.execute(
                "INSERT INTO player_flags (player_id, flag) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                user_id, flag
            )

    async def get_story_state(self, user_id: int):
        async with self.pool.acquire() as con:
            row = await con.fetchrow(
                "SELECT section_id, story_step_id FROM players WHERE user_id = $1",
                user_id,
            )
            return dict(row) if row else {"section_id": "section_0", "story_step_id": "intro_1"}

    async def set_story_state(self, user_id: int, section_id: str, step_id: str):
        async with self.pool.acquire() as con:
            await con.execute(
                "UPDATE players SET section_id = $2, story_step_id = $3 WHERE user_id = $1",
                user_id, section_id, step_id
            )

    async def get_session_message_id(self, user_id: int) -> int | None:
        async with self.pool.acquire() as con:
            return await con.fetchval(
                "SELECT session_message_id FROM players WHERE user_id=$1", user_id
            )

    async def set_session_message_id(self, user_id: int, message_id: int) -> None:
        async with self.pool.acquire() as con:
            await con.execute(
                "UPDATE players SET session_message_id=$2 WHERE user_id=$1",
                user_id, int(message_id)
            )

    async def _get_player_pk(self, con) -> str:
        if self._player_pk:
            return self._player_pk
        rows = await con.fetch(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'players' AND column_name = ANY($1::text[])",
            ['id', 'player_id', 'user_id']
        )
        cols = {r['column_name'] for r in rows}
        if 'id' in cols:        self._player_pk = 'id'
        elif 'player_id' in cols: self._player_pk = 'player_id'
        elif 'user_id' in cols: self._player_pk = 'user_id'
        else:
            raise RuntimeError("players table has no id/player_id/user_id column")
        return self._player_pk

    # --- energy helpers ---

    async def restore_energy_full(self, user_id: int) -> None:
        async with self.pool.acquire() as con:
            pk = await self._get_player_pk(con)
            await con.execute(f"UPDATE players SET energy = max_energy WHERE {pk} = $1", user_id)

    async def add_energy(self, user_id: int, amount: int) -> None:
        async with self.pool.acquire() as con:
            pk = await self._get_player_pk(con)
            await con.execute(
                f"UPDATE players SET energy = LEAST(energy + $2, max_energy) WHERE {pk} = $1",
                user_id, amount,
            )

    async def spend_energy(self, user_id: int, amount: int) -> bool:
        async with self.pool.acquire() as con:
            pk = await self._get_player_pk(con)
            row = await con.fetchrow(
                f"UPDATE players SET energy = energy - $2 "
                f"WHERE {pk} = $1 AND energy >= $2 RETURNING energy",
                user_id, amount,
            )
            return row is not None