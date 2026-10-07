"""Turn a meeting transcript into a validated Draft using an LLM via OpenRouter."""
import json
import os
import re

import httpx
from pydantic import ValidationError

from schemas import Draft

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MEETING_DATE = "2026-10-07"


class AIError(Exception):
    """The AI call failed or returned something that isn't JSON. Route returns 502."""


class DraftInvalid(Exception):
    """The AI returned JSON that doesn't fit the Draft shape. Route returns 422."""

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


SYSTEM_PROMPT = """You convert a company meeting transcript into projects and tasks.

Meeting date: {meeting_date}. All dates are in 2026. Output dates as YYYY-MM-DD.

Team directory (the ONLY people you may assign):
{directory}

Rules:
- Use only the FINAL agreed decisions. Later corrections replace earlier values
  (dates, hours, owners). The final recap is authoritative.
- Do not create tasks for features that were rejected or excluded.
- Each project's managerId must be a MANAGER id from the directory.
- Each task's assigneeId must be an AGENT id from the directory.
- Never invent people. Client contacts and end users are not employees.
- estimatedHours is developer effort in hours, not calendar days.
- Keep separate tasks separate, even if the same person owns them.
- Use the task and project names exactly as agreed in the meeting.
- If required information is missing, still return your best structure and
  leave the unknown field empty rather than guessing a person.

Return ONLY JSON in exactly this shape, no markdown, no explanation:
{{"projects":[{{"name":"","clientName":"","description":"","managerId":"",
"deadline":"YYYY-MM-DD","tasks":[{{"title":"","description":"","assigneeId":"",
"deadline":"YYYY-MM-DD","estimatedHours":0}}]}}]}}"""


def build_directory(users: list[dict]) -> str:
    # Only these fields reach the AI: never emails, passwords or hashes
    return "\n".join(
        f"{u['id']} | {u['name']} | {u['role']} | {u.get('specialization') or ''} | {', '.join(u.get('skills') or [])}"
        for u in users
    )


def _call_model(model: str, system: str, transcript: str) -> str:
    resp = httpx.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}"},
        json={
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": transcript},
            ],
        },
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    if not content:
        raise AIError("AI returned an empty response")
    return content


def _parse_json(text: str) -> dict:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Some models wrap JSON in prose; fall back to the outermost {...}
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def readable_errors(err: ValidationError, data: dict) -> list[str]:
    """Turn Pydantic errors into messages like 'UrbanCart Website / Demo cart UI: deadline is missing'."""
    messages = []
    for e in err.errors():
        loc = list(e["loc"])
        parts = []
        try:
            if len(loc) >= 2 and loc[0] == "projects":
                project = data["projects"][loc[1]]
                parts.append(project.get("name") or f"Project {loc[1] + 1}")
                if len(loc) >= 4 and loc[2] == "tasks":
                    task = project["tasks"][loc[3]]
                    parts.append(task.get("title") or f"Task {loc[3] + 1}")
                    loc = loc[4:]
                else:
                    loc = loc[2:]
        except (KeyError, IndexError, TypeError, AttributeError):
            pass
        field = ".".join(str(x) for x in loc) or "value"
        label = " / ".join(parts)
        messages.append(f"{label + ': ' if label else ''}{field} - {e['msg']}")
    return messages


def extract(transcript: str, directory: list[dict]) -> Draft:
    primary = os.environ.get("AI_MODEL")
    backup = os.environ.get("AI_BACKUP_MODEL")
    if not primary or not os.environ.get("OPENROUTER_API_KEY"):
        raise AIError("AI is not configured (set OPENROUTER_API_KEY and AI_MODEL)")

    system = SYSTEM_PROMPT.format(meeting_date=MEETING_DATE, directory=build_directory(directory))
    data, last_error = None, None
    for model in [m for m in (primary, backup) if m]:
        try:
            data = _parse_json(_call_model(model, system, transcript))
            break
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, AIError) as e:
            last_error = e
    if data is None:
        raise AIError(f"AI request failed: {last_error}")

    try:
        return Draft.model_validate(data)
    except ValidationError as e:
        raise DraftInvalid(readable_errors(e, data if isinstance(data, dict) else {}))


if __name__ == "__main__":
    # Standalone check against the supplied transcript: python ai_extract.py
    from pathlib import Path

    from db import connect
    from access import get_users

    sample = Path(__file__).resolve().parent.parent / "frontend" / "public" / "sample-transcript.txt"
    with connect() as conn:
        users = get_users(conn)
    draft = extract(sample.read_text(encoding="utf-8"), users)
    total = 0
    for p in draft.projects:
        print(f"\n{p.name} | {p.clientName} | {p.managerId} | {p.deadline}")
        for t in p.tasks:
            total += 1
            print(f"  - {t.title} | {t.assigneeId} | {t.deadline} | {t.estimatedHours}h")
    print(f"\n{len(draft.projects)} projects, {total} tasks")
