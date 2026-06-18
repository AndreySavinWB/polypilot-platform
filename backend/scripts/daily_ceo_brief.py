"""Утренний будильник CEO: задачи на день + ссылка на пост канала.

Usage:
  python scripts/daily_ceo_brief.py           # preview
  python scripts/daily_ceo_brief.py --send    # Telegram push в 9:00 MSK (настрой cron)

Env:
  TELEGRAM_BOT_TOKEN, TELEGRAM_CEO_CHAT_ID
  DAILY_PUBLISH_START_DATE — день спринта для /publish
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from server import load_env
from src.bot import config, telegram_api
from src.bot.ceo_brief import build_morning_brief, build_publish_full, ceo_chat_id


def send_to_ceo(text: str, parse_mode: str | None = None) -> None:
    token = config.bot_token()
    chat_id = ceo_chat_id()
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in backend/.env")
    if not chat_id:
        raise SystemExit("Set TELEGRAM_CEO_CHAT_ID in backend/.env")
    if parse_mode is None:
        telegram_api.send_plain(token, chat_id, text)
    else:
        telegram_api.send_message(token, chat_id, text, parse_mode=parse_mode)
    print(f"Sent to CEO chat_id={chat_id}")


def main():
    load_env()
    parser = argparse.ArgumentParser(description="Morning CEO brief (wake + tasks)")
    parser.add_argument("--send", action="store_true", help="Send to TELEGRAM_CEO_CHAT_ID")
    parser.add_argument(
        "--with-publish",
        action="store_true",
        help="Also send full channel post text (2nd message)",
    )
    args = parser.parse_args()

    brief = build_morning_brief()

    if args.send:
        from src.bot.ceo_brief import build_morning_brief_plain, send_morning_brief_to_ceo
        try:
            send_morning_brief_to_ceo()
            print("Sent.")
        except Exception as err:
            raise SystemExit(f"Send failed: {err}") from err
        if args.with_publish:
            send_to_ceo(build_publish_full(), parse_mode=None)
    else:
        print(brief.replace("<b>", "").replace("</b>", ""))
        if args.with_publish:
            print("\n--- publish ---\n")
            print(build_publish_full())


if __name__ == "__main__":
    main()
