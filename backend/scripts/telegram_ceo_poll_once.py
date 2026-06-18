"""One-shot Telegram long-poll for CEO commands (GitHub Actions fallback)."""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.bot import config, handlers, telegram_api
from src.bot.ceo_brief import build_morning_brief, build_publish_full, is_ceo_chat

OFFSET_PATH = os.path.join(ROOT, "data", ".telegram_ceo_poll_offset")


def _load_offset() -> int | None:
    if not os.path.exists(OFFSET_PATH):
        return None
    try:
        with open(OFFSET_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return int(data.get("offset", 0)) or None
    except (OSError, ValueError, TypeError):
        return None


def _save_offset(offset: int) -> None:
    os.makedirs(os.path.dirname(OFFSET_PATH), exist_ok=True)
    with open(OFFSET_PATH, "w", encoding="utf-8") as handle:
        json.dump({"offset": offset}, handle)


def _get_updates(token: str, offset: int | None):
    params = {"timeout": 0, "allowed_updates": json.dumps(["message"])}
    if offset is not None:
        params["offset"] = offset
    url = f"https://api.telegram.org/bot{token}/getUpdates?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(data)
    return data.get("result", [])


def main():
    token = config.bot_token()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN missing")
    offset = _load_offset()
    updates = _get_updates(token, offset)
    if not updates:
        print("no updates")
        return

    last_id = offset or 0
    for update in updates:
        last_id = max(last_id, int(update.get("update_id", 0)) + 1)
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = str(chat.get("id", ""))
        text = (message.get("text") or "").strip()
        if not chat_id or not text:
            continue
        if not is_ceo_chat(chat_id):
            if text.startswith("/start"):
                telegram_api.send_message(
                    token,
                    chat_id,
                    "Привет! Это PolyPilot bot. CEO-команды: /today /publish",
                )
            continue

        if text.startswith("/today") or text.startswith("/brief"):
            telegram_api.send_plain(token, chat_id, build_morning_brief().replace("<b>", "").replace("</b>", ""))
        elif text.startswith("/publish"):
            telegram_api.send_plain(token, chat_id, build_publish_full().replace("<b>", "").replace("</b>", ""))
        elif text.startswith("/start"):
            telegram_api.send_plain(
                token,
                chat_id,
                "PolyPilot CEO bot online.\n\n/today — утренний бриф\n/publish — пост в канал",
            )
        else:
            handlers.handle_update(update)

    _save_offset(last_id)
    print(f"processed {len(updates)} updates, offset={last_id}")


if __name__ == "__main__":
    main()
