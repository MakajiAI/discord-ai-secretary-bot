from __future__ import annotations

import json
import re


class TaskParseError(ValueError):
    """Raised when Gemini output cannot be parsed as the expected task JSON."""


def parse_tasks_json(raw_text: str) -> list[dict[str, str | None]]:
    try:
        payload = json.loads(_extract_json(raw_text))
    except json.JSONDecodeError as exc:
        raise TaskParseError("Invalid JSON returned by LLM") from exc

    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        raise TaskParseError("JSON must contain a tasks array")

    normalized: list[dict[str, str | None]] = []
    for item in tasks:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        normalized.append(
            {
                "title": title.strip(),
                "assignee": _optional_string(item.get("assignee")),
                "due_date": _optional_string(item.get("due_date")),
            }
        )
    return normalized


def _extract_json(raw_text: str) -> str:
    text = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def _optional_string(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
