"""Расписание TG-постов CEO (Pack sprint)."""

from __future__ import annotations

import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEDULE_PATH = os.path.join(ROOT, "data", "daily_publish.json")


def load_schedule() -> dict:
    with open(SCHEDULE_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_start_date(raw: str | None) -> date:
    if raw:
        return date.fromisoformat(raw.strip()[:10])
    schedule = load_schedule()
    hint = schedule.get("startDateHint")
    if hint:
        return date.fromisoformat(hint)
    return date.today()


def sprint_day_index(start: date, today: date | None = None) -> int:
    today = today or date.today()
    return max(1, (today - start).days + 1)


def get_day_entry(schedule: dict, day_index: int) -> dict:
    days = schedule.get("days") or []
    if not days:
        raise ValueError("daily_publish.json has no days")
    if day_index <= len(days):
        return days[day_index - 1]
    idx = (day_index - 1) % len(days)
    entry = dict(days[idx])
    entry["label"] = entry.get("label", "") + " (repeat week)"
    return entry


def build_publish_brief(schedule: dict, day_index: int) -> str:
    entry = get_day_entry(schedule, day_index)
    total = len(schedule.get("days") or [])
    optional = entry.get("alsoOptional") or []
    opt_lines = "\n".join(f"• {x}" for x in optional) if optional else "• —"

    return (
        f"📅 PolyPilot · День {day_index}/{total}\n"
        f"📌 {entry.get('label', 'TG post')}\n"
        f"📣 Канал: @polypilot_pro\n\n"
        f"Скопируй текст ниже и опубликуй в канале:\n"
        f"{'—' * 28}\n\n"
        f"{entry.get('text', '').strip()}\n\n"
        f"{'—' * 28}\n\n"
        f"Опционально сегодня:\n{opt_lines}\n\n"
        f"Pack: {schedule.get('packId')} · event {schedule.get('eventId')}"
    )
