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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # << DEV ONLY. Replace with explicit origins later.
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

@app.post("/story/submit", response_model=StepState)
async def story_submit(body: SubmitBody, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await ensure_player(repo, narr, body.user_id)
    state = await repo.get_story_state(body.user_id)
    step = narr.get_step(state["story_step_id"])
    if step.get("type") != "modal":
        raise HTTPException(status_code=400, detail="Not a modal step.")
    await narr.apply_effects(body.user_id, step.get("effects"), modal_value=body.value)
    next_id = step.get("next")
    if next_id:
        await repo.set_story_state(body.user_id, "section_0", next_id)
    return await serialize_step(repo, narr, body.user_id)

class ChooseBody(BaseModel):
    user_id: int
    option_id: str

@app.post("/story/choose", response_model=StepState)
async def story_choose(body: ChooseBody, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await ensure_player(repo, narr, body.user_id)
    state = await repo.get_story_state(body.user_id)
    step = narr.get_step(state["story_step_id"])
    st = step.get("type")
    if st not in ("choice", "dyn_choice"):
        raise HTTPException(status_code=400, detail="Not a choice step.")

    if st == "choice":
        choice = next((o for o in step.get("options", []) if o["id"] == body.option_id), None)
        if not choice:
            raise HTTPException(status_code=404, detail="Option not found.")
        await narr.apply_effects(body.user_id, choice.get("effects"))
        next_id = choice.get("next") or step.get( "next") or step["id"]
    else:
        await narr.apply_effects(body.user_id, [{"op": "set_flag", "flag": f"starter_talent:{body.option_id}"}])
        next_id = step.get("next") or step["id"]

    await repo.set_story_state(body.user_id, "section_0", next_id)
    return await serialize_step(repo, narr, body.user_id)

@app.post("/session/reset")
async def session_reset(user_id: int, repo=Depends(get_repo), narr: Narrative = Depends(get_narr)):
    await repo.set_story_state(user_id, "section_0", narr.first_step_id())
    return await serialize_step(repo, narr, user_id)
