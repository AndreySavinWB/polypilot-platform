"""Daily CEO publish brief — готовый текст TG-поста + напоминание в личку.

Usage:
  python scripts/daily_publish.py              # сегодня (print)
  python scripts/daily_publish.py --send       # отправить CEO в Telegram
  python scripts/daily_publish.py --day 3      # конкретный день спринта
  python scripts/daily_publish.py --list       # все 7 дней

Env (backend/.env):
  DAILY_PUBLISH_START_DATE=2026-06-14   # день 1 спринта
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CEO_CHAT_ID=...              # твой chat id (см. CEO_DAILY_PUBLISH.md)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from server import load_env
from src.bot import config, telegram_api

SCHEDULE_PATH = os.path.join(ROOT, "data", "daily_publish.json")


def load_schedule():
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
    delta = (today - start).days + 1
    return max(1, delta)


def get_day_entry(schedule: dict, day_index: int) -> dict:
    days = schedule.get("days") or []
    if not days:
        raise ValueError("daily_publish.json has no days")
    if day_index <= len(days):
        return days[day_index - 1]
    # После 7 дней — цикл с пометкой repeat
    idx = (day_index - 1) % len(days)
    entry = dict(days[idx])
    entry["label"] = entry.get("label", "") + " (repeat week)"
    return entry


def build_brief(schedule: dict, day_index: int) -> str:
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


def send_to_ceo(text: str) -> None:
    token = config.bot_token()
    chat_id = os.getenv("TELEGRAM_CEO_CHAT_ID", "").strip()
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in backend/.env")
    if not chat_id:
        raise SystemExit("Set TELEGRAM_CEO_CHAT_ID in backend/.env (см. CEO_DAILY_PUBLISH.md)")
    telegram_api.send_message(token, chat_id, text, parse_mode=None)
    print(f"Sent to CEO chat_id={chat_id}")


def main():
    load_env()
    parser = argparse.ArgumentParser(description="Daily TG publish brief for CEO")
    parser.add_argument("--send", action="store_true", help="Send brief to TELEGRAM_CEO_CHAT_ID")
    parser.add_argument("--day", type=int, help="Force sprint day number (1-based)")
    parser.add_argument("--list", action="store_true", help="List all sprint days")
    parser.add_argument("--start", help="Override DAILY_PUBLISH_START_DATE (YYYY-MM-DD)")
    args = parser.parse_args()

    schedule = load_schedule()
    start = parse_start_date(args.start or os.getenv("DAILY_PUBLISH_START_DATE"))

    if args.list:
        for entry in schedule.get("days") or []:
            print(f"Day {entry.get('day')}: {entry.get('label')}")
        return

    day_index = args.day if args.day else sprint_day_index(start)
    brief = build_brief(schedule, day_index)

    if args.send:
        send_to_ceo(brief)
    else:
        print(brief)


if __name__ == "__main__":
    main()
