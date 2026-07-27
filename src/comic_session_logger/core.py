from __future__ import annotations

import json
import os
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


def empty_log() -> dict[str, Any]:
    return {"version": 1, "sessions": []}


def load_log(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_log()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("log must be a version 1 object")
    sessions = data.get("sessions")
    if not isinstance(sessions, list):
        raise TypeError("sessions must be a list")
    seen: set[str] = set()
    for item in sessions:
        validate_session(item, seen)
        seen.add(item["id"])
    return data


def validate_session(item: Any, existing_ids: set[str] | None = None) -> None:
    if not isinstance(item, dict):
        raise TypeError("session must be an object")
    required_strings = ("id", "date", "series", "issue_start", "issue_end")
    if any(not isinstance(item.get(key), str) or not item[key].strip() for key in required_strings):
        raise ValueError("session requires id, date, series, issue_start, and issue_end")
    if existing_ids and item["id"] in existing_ids:
        raise ValueError(f"duplicate session id: {item['id']}")
    try:
        date.fromisoformat(item["date"])
    except ValueError as exc:
        raise ValueError("session date must use YYYY-MM-DD") from exc
    minutes = item.get("minutes")
    interruptions = item.get("interruptions", 0)
    if not isinstance(minutes, int) or minutes <= 0:
        raise ValueError("minutes must be a positive integer")
    if not isinstance(interruptions, int) or interruptions < 0:
        raise ValueError("interruptions must be a non-negative integer")


def add_session(data: dict[str, Any], session: dict[str, Any]) -> None:
    ids = {item["id"] for item in data["sessions"]}
    validate_session(session, ids)
    data["sessions"].append(session)
    data["sessions"].sort(key=lambda item: (item["date"], item["id"]))


def save_log(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def summary(data: dict[str, Any]) -> dict[str, Any]:
    sessions = data["sessions"]
    per_series = Counter(item["series"] for item in sessions)
    return {
        "sessions": len(sessions),
        "minutes": sum(item["minutes"] for item in sessions),
        "interruptions": sum(item.get("interruptions", 0) for item in sessions),
        "series": dict(sorted(per_series.items())),
    }


def render_markdown(data: dict[str, Any]) -> str:
    totals = summary(data)
    lines = [
        "# Comic Reading Sessions",
        "",
        f"Sessions: **{totals['sessions']}** · Minutes: **{totals['minutes']}** · Interruptions: **{totals['interruptions']}**",
        "",
    ]
    for item in reversed(data["sessions"]):
        lines.append(
            f"- **{item['date']} — {item['series']} {item['issue_start']}–{item['issue_end']}**: "
            f"{item['minutes']} minutes, {item.get('interruptions', 0)} interruptions"
        )
        if item.get("notes"):
            lines.append(f"  - {item['notes']}")
    return "\n".join(lines).rstrip() + "\n"
