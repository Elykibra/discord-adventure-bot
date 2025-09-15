# apps/api/server/main.py

from __future__ import annotations
import os, sys
from pathlib import Path
from typing import Optional, List
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncpg

# ---- import your shared engine/data ----
# main.py lives in apps/api/server → parents: [server, api, apps, <repo_root>]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

from core.repository import SqlRepository, MemoryRepository
from core.narrative import Narrative
from data.section_0.story import STORY as STORY_SECTION_0

app = FastAPI(title="Aethelgard API")
origins_env = os.getenv("CORS_ORIGINS", "")
ALLOW_ORIGINS = [o.strip() for o in origins_env.split(",") if o.strip()]

# sensible dev defaults if none provided
if not ALLOW_ORIGINS:
    ALLOW_ORIGINS = [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
    ]

allow_origin_regex = r"^https?://(localhost|127\.0\.0\.1|192\.168\.1\.8)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,     # keep explicit ones
    allow_origin_regex=allow_origin_regex,  # plus regex for any port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    # Send people to the interactive docs
    return RedirectResponse(url="/docs")

@app.on_event("startup")
async def startup():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        pool = await asyncpg.create_pool(dsn=db_url, min_size=1, max_size=5)
        app.state.repo = SqlRepository(pool)
        print("API repo: SqlRepository")
    else:
        app.state.repo = MemoryRepository()
        print("API repo: MemoryRepository (DATABASE_URL not set)")
    app.state.narr = Narrative(STORY_SECTION_0, app.state.repo)

@app.on_event("shutdown")
async def shutdown():
    repo = app.state.repo
    if isinstance(repo, SqlRepository):
        await repo.pool.close()

def get_repo():
    return app.state.repo

def get_narr() -> Narrative:
    return app.state.narr

# ------------ models ------------
class Option(BaseModel):
    id: str
    label: str

class StepState(BaseModel):
    section_id: str
    step_id: str
    kind: str
    text: Optional[str] = None
    prompt: Optional[str] = None
    options: List[Option] = Field(default_factory=list)
    can_continue: bool = False
    needs_input: bool = False

# ------------ helpers ------------
async def ensure_player(repo, narr: Narrative, user_id: int):
    p = await repo.get_player(user_id)
    if not p:
        await repo.create_player(user_id, {
            "name": f"Adventurer {user_id}",
            "section_id": "section_0",
            "story_step_id": narr.first_step_id(),
            "energy": 10, "max_energy": 10
        })

def render_text(t: Optional[str], player_name: str, fallback: str = "") -> str:
    if not t:
        return fallback
    return t.replace("{player_name}", player_name or "Adventurer")

async def serialize_step(repo, narr: Narrative, user_id: int) -> StepState:
    player = await repo.get_player(user_id)
    state = await repo.get_story_state(user_id)
    step = narr.get_step(state["story_step_id"])
    stype = step.get("type")

    if stype == "narration":
        return StepState(
            section_id=state.get("section_id", "section_0"),
            step_id=step["id"],
            kind="narration",
            text=render_text(step.get("text"), player.get("name")),
            can_continue=bool(step.get("next")),
        )

    if stype == "modal":
        return StepState(
            section_id=state.get("section_id", "section_0"),
            step_id=step["id"],
            kind="modal",
            prompt=step.get("modal_title", "Enter value"),
            needs_input=True,
        )

    if stype == "choice":
        opts = [Option(id=o["id"], label=o["label"]) for o in step.get("options", [])]
        return StepState(
            section_id=state.get("section_id", "section_0"),
            step_id=step["id"],
            kind="choice",
            prompt=step.get("prompt", "Choose:"),
            options=opts,
        )

    if stype == "dyn_choice":
        player = await repo.get_player(user_id)
        flags = player.get("flags", set())
        if not isinstance(flags, set):
            flags = set(flags or [])
        starter = next((f.split(":",1)[1] for f in flags
                        if isinstance(f, str) and f.startswith("starter_pet:")), None)
        from data.abilities import STARTER_TALENTS
        opts = [Option(id=t["mechanic_name"], label=t["name"]) for t in STARTER_TALENTS.get(starter, [])]
        return StepState(
            section_id=state.get("section_id", "section_0"),
            step_id=step["id"],
            kind="dyn_choice",
            prompt=step.get("prompt", "Choose:"),
            options=opts,
        )

    return StepState(
        section_id=state.get("section_id", "section_0"),
        step_id=step["id"],
        kind=stype or "unknown",
        text="🚧 This branch isn’t written yet. Thanks for testing!",
        can_continue=False,
    )

# ------------ endpoints ------------
@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/session/start", response_model=StepState)
async def session_start(user_id: int, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await ensure_player(repo, narr, user_id)
    return await serialize_step(repo, narr, user_id)

@app.post("/story/continue", response_model=StepState)
async def story_continue(user_id: int, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await ensure_player(repo, narr, user_id)
    state = await repo.get_story_state(user_id)
    step = narr.get_step(state["story_step_id"])
    if step.get("type") != "narration" or not step.get("next"):
        raise HTTPException(status_code=400, detail="Cannot continue from this step.")
    await narr.apply_effects(user_id, step.get("effects"))
    await repo.set_story_state(user_id, "section_0", step["next"])
    return await serialize_step(repo, narr, user_id)

class SubmitBody(BaseModel):
    user_id: int
    value: str
    step_id: str | None = None

@app.post("/story/submit", response_model=StepState)
async def story_submit(body: SubmitBody, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await ensure_player(repo, narr, body.user_id)
    state = await repo.get_story_state(body.user_id)
    step = narr.get_step(state["story_step_id"])

    # If the client sent the step_id and it doesn’t match, just return the real current step
    if body.step_id and body.step_id != step["id"]:
        return await serialize_step(repo, narr, body.user_id)

    if step.get("type") != "modal":
        # Be forgiving: return current step instead of error
        return await serialize_step(repo, narr, body.user_id)

    await narr.apply_effects(body.user_id, step.get("effects"), modal_value=body.value)
    next_id = step.get("next")
    if next_id:
        await repo.set_story_state(body.user_id, "section_0", next_id)
    return await serialize_step(repo, narr, body.user_id)

class ChooseBody(BaseModel):
    user_id: int
    option_id: str
    step_id: str | None = None

@app.post("/story/choose", response_model=StepState)
async def story_choose(body: ChooseBody, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await ensure_player(repo, narr, body.user_id)
    state = await repo.get_story_state(body.user_id)
    step = narr.get_step(state["story_step_id"])

    # If client’s idea of the step doesn’t match, just return the real current step
    if body.step_id and body.step_id != step["id"]:
        return await serialize_step(repo, narr, body.user_id)

    st = step.get("type")
    if st not in ("choice", "dyn_choice"):
        # Be forgiving: return current step instead of error
        return await serialize_step(repo, narr, body.user_id)

    if st == "choice":
        choice = next((o for o in step.get("options", []) if o["id"] == body.option_id), None)
        if not choice:
            # If the option isn’t valid anymore, also just return current step
            return await serialize_step(repo, narr, body.user_id)
        await narr.apply_effects(body.user_id, choice.get("effects"))
        next_id = choice.get("next") or step.get("next") or step["id"]
    else:
        # dyn_choice: flag the selected talent
        await narr.apply_effects(body.user_id, [{"op": "set_flag", "flag": f"starter_talent:{body.option_id}"}])
        next_id = step.get("next") or step["id"]

    await repo.set_story_state(body.user_id, "section_0", next_id)
    return await serialize_step(repo, narr, body.user_id)

class PlayerState(BaseModel):
    name: str
    energy: int
    max_energy: int
    main_pet_species: str | None = None
    flags: list[str] = []

# --- helper to get flags as list ---
async def get_player_state(repo, user_id: int) -> PlayerState:
    p = await repo.get_player(user_id)
    flags = p.get("flags", set())
    if not isinstance(flags, set):
        flags = set(flags or [])
    return PlayerState(
        name=p.get("name") or "Adventurer",
        energy=int(p.get("energy", 0)),
        max_energy=int(p.get("max_energy", 0)),
        main_pet_species=p.get("main_pet_species"),
        flags=sorted(list(flags)),
    )

# --- endpoints ---
@app.get("/player/state", response_model=PlayerState)
async def player_state(user_id: int, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await ensure_player(repo, narr, user_id)
    return await get_player_state(repo, user_id)

@app.post("/session/reset")
async def session_reset(user_id: int, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    first = narr.first_step_id()
    if hasattr(repo, "pool"):  # SqlRepository path
        async with repo.pool.acquire() as con:
            # detect the players PK column just like the repo does
            rows = await con.fetch(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'players' AND column_name = ANY($1::text[])",
                ['id', 'player_id', 'user_id']
            )
            cols = {r['column_name'] for r in rows}
            if 'id' in cols:        pk = 'id'
            elif 'player_id' in cols: pk = 'player_id'
            elif 'user_id' in cols: pk = 'user_id'
            else:
                raise HTTPException(status_code=500, detail="players table missing PK column")

            async with con.transaction():
                await con.execute("DELETE FROM pets WHERE player_id=$1", user_id)
                await con.execute(
                    "DELETE FROM player_flags WHERE player_id=$1 "
                    "AND (flag LIKE 'starter_pet:%' OR flag LIKE 'starter_talent:%')",
                    user_id
                )
                await con.execute(
                    f"UPDATE players SET story_step_id=$1, section_id='section_0', main_pet_species=NULL "
                    f"WHERE {pk}=$2",
                    first, user_id
                )
    else:
        p = await repo.get_player(user_id)
        if p:
            p["story_step_id"] = first
            p["section_id"] = "section_0"
            p["main_pet_species"] = None
            if isinstance(p.get("flags"), set):
                p["flags"] = {f for f in p["flags"]
                              if not (isinstance(f, str) and (f.startswith("starter_pet:") or f.startswith("starter_talent:")))}
            else:
                p["flags"] = [f for f in (p.get("flags") or [])
                              if not (isinstance(f, str) and (f.startswith("starter_pet:") or f.startswith("starter_talent:")))]
            await repo.save_player(user_id, p)

    await repo.set_story_state(user_id, "section_0", first)
    return await serialize_step(repo, narr, user_id)
