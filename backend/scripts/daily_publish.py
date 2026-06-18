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
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from server import load_env
from src.bot import config, telegram_api
from src.bot.publish_schedule import build_publish_brief, load_schedule, parse_start_date, sprint_day_index


def send_to_ceo(text: str, parse_mode=None) -> None:
    token = config.bot_token()
    chat_id = os.getenv("TELEGRAM_CEO_CHAT_ID", "").strip()
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in backend/.env")
    if not chat_id:
        raise SystemExit("Set TELEGRAM_CEO_CHAT_ID in backend/.env (см. CEO_DAILY_PUBLISH.md)")
    telegram_api.send_message(token, chat_id, text, parse_mode=parse_mode)
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
    brief = build_publish_brief(schedule, day_index)

    if args.send:
        send_to_ceo(brief, parse_mode=None)
    else:
        print(brief)


if __name__ == "__main__":
    main()
