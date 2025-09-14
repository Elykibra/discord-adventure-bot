# core/validator.py
from __future__ import annotations
from typing import Dict, Any, List, Set

ALLOWED_TYPES: Set[str] = {"narration", "choice", "modal", "dyn_choice"}

def _is_str(x) -> bool:
    return isinstance(x, str) and len(x) > 0

def validate_story(story: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(story, dict):
        return ["story must be a dict"]

    if not _is_str(story.get("id")):
        errors.append("story missing or invalid 'id'")

    steps = story.get("steps", [])
    if not isinstance(steps, list) or not steps:
        errors.append("story 'steps' must be a non-empty list")
        return errors

    seen_ids: Set[str] = set()
    target_ids: List[str] = []

    for s in steps:
        sid = s.get("id")
        if not _is_str(sid):
            errors.append("step missing 'id'")
            continue
        if sid in seen_ids:
            errors.append(f"duplicate step id: {sid}")
        seen_ids.add(sid)

        stype = s.get("type")
        if stype not in ALLOWED_TYPES:
            errors.append(f"step {sid} has invalid type: {stype}")
            continue

        # Common: validate 'next' if present
        nxt = s.get("next")
        if nxt is not None and not _is_str(nxt):
            errors.append(f"step {sid} has non-string 'next'")
        if _is_str(nxt):
            target_ids.append(nxt)

        if stype == "narration":
            if not _is_str(s.get("text")):
                errors.append(f"step {sid} (narration) missing 'text'")

        elif stype == "choice":
            options = s.get("options")
            if not isinstance(options, list) or not options:
                errors.append(f"choice step {sid} missing non-empty 'options'")
            else:
                for i, opt in enumerate(options):
                    if not _is_str(opt.get("id")):
                        errors.append(f"choice step {sid} option {i} missing 'id'")
                    if not _is_str(opt.get("label")):
                        errors.append(f"choice step {sid} option {i} missing 'label'")
                    opt_next = opt.get("next")
                    if opt_next is not None and not _is_str(opt_next):
                        errors.append(f"choice step {sid} option {i} has non-string 'next'")
                    if _is_str(opt_next):
                        target_ids.append(opt_next)

        elif stype == "modal":
            # minimal requirements for name modal
            if not _is_str(s.get("modal_title")):
                errors.append(f"modal step {sid} missing 'modal_title'")
            if not _is_str(s.get("modal_label")):
                errors.append(f"modal step {sid} missing 'modal_label'")
            # next is recommended (where to go after submit)
            if not _is_str(s.get("next")):
                errors.append(f"modal step {sid} should define a 'next'")

        elif stype == "dyn_choice":
            if not _is_str(s.get("prompt")):
                errors.append(f"dyn_choice step {sid} missing 'prompt'")
            if not _is_str(s.get("dynamic_source")):
                errors.append(f"dyn_choice step {sid} missing 'dynamic_source'")
            # usually should define next
            if not _is_str(s.get("next")):
                errors.append(f"dyn_choice step {sid} should define a 'next'")

    # cross-reference: every referenced 'next' must exist
    missing_targets = [t for t in target_ids if t not in seen_ids]
    for t in missing_targets:
        errors.append(f"'next' references missing step id: {t}")

    return errors


def validate_all() -> None:
    # Import here to avoid circulars
    from data.section_0.story import STORY
    problems = validate_story(STORY)
    if problems:
        raise ValueError("Data validation failed:\n- " + "\n- ".join(problems))
