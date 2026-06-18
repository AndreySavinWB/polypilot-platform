"""Утренний CEO-бриф: будильник + задачи на день + контент канала."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone

from src.bot.publish_schedule import (
    build_publish_brief,
    get_day_entry,
    load_schedule,
    parse_start_date,
    sprint_day_index,
)

BRIEF_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "daily_ceo_brief.json",
)

_WEEKDAY_RU = {
    0: "понедельник",
    1: "вторник",
    2: "среда",
    3: "четверг",
    4: "пятница",
    5: "суббота",
    6: "воскресенье",
}


def _load_brief_config() -> dict:
    with open(BRIEF_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def ceo_chat_id() -> str:
    return os.getenv("TELEGRAM_CEO_CHAT_ID", "").strip()


def is_ceo_chat(chat_id) -> bool:
    expected = ceo_chat_id()
    if not expected:
        return False
    return str(chat_id) == str(expected)


_MSK = timezone(timedelta(hours=3))


def _tz_now(tz_name: str) -> datetime:
    # Fixed UTC+3 (Москва) — без пакета tzdata (Windows portable Python)
    if tz_name in ("Europe/Moscow", "MSK", "UTC+3"):
        return datetime.now(_MSK)
    return datetime.now(timezone.utc)


def _weekday_entry(brief: dict, dow: int) -> dict:
    for entry in brief.get("weekdays") or []:
        if entry.get("dow") == dow:
            return entry
    return {"label": _WEEKDAY_RU.get(dow, ""), "p0": [], "p1": []}


def _numbered(lines: list) -> str:
    if not lines:
        return "• —"
    return "\n".join(f"{i}. {line}" for i, line in enumerate(lines, 1))


def build_morning_brief(today: date | None = None, tz_name: str | None = None) -> str:
    brief_cfg = _load_brief_config()
    tz_name = tz_name or brief_cfg.get("timezone") or "Europe/Moscow"
    now = _tz_now(tz_name)
    today = today or now.date()
    dow = today.weekday()
    day_entry = _weekday_entry(brief_cfg, dow)

    schedule = load_schedule()
    start = parse_start_date(os.getenv("DAILY_PUBLISH_START_DATE"))
    day_index = sprint_day_index(start, today)
    publish_entry = get_day_entry(schedule, day_index)

    do_not = brief_cfg.get("doNotToday") or []
    do_not_lines = "\n".join(f"• {x}" for x in do_not)

    return (
        f"☀️ <b>Доброе утро!</b> {now.strftime('%H:%M')} · {tz_name}\n"
        f"📅 {today.isoformat()} · {_WEEKDAY_RU.get(dow, day_entry.get('label', ''))}\n"
        f"🎯 PolyPilot CEO · спринт день {day_index}\n\n"
        f"<b>Задачи на сегодня</b>\n\n"
        f"<b>P0 — обязательно</b>\n{_numbered(day_entry.get('p0') or [])}\n\n"
        f"<b>P1 — если останется время</b>\n{_numbered(day_entry.get('p1') or [])}\n\n"
        f"<b>Контент @polypilot_pro</b>\n"
        f"• {publish_entry.get('label', 'TG post')}\n"
        f"• Полный текст: /publish\n\n"
        f"<b>🚫 Не делать сегодня</b>\n{do_not_lines}\n\n"
        f"/today — повторить бриф · /publish — текст поста"
    )


def build_morning_brief_plain(today: date | None = None, tz_name: str | None = None) -> str:
    return (
        build_morning_brief(today=today, tz_name=tz_name)
        .replace("<b>", "")
        .replace("</b>", "")
    )


def send_morning_brief_to_ceo() -> dict:
    """Отправить бриф CEO. Возвращает {ok, chat_id} или бросает."""
    from src.bot import config, telegram_api

    token = config.bot_token()
    chat_id = ceo_chat_id()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CEO_CHAT_ID is not set")
    text = build_morning_brief_plain()
    result = telegram_api.send_plain(token, chat_id, text)
    return {"ok": True, "chat_id": chat_id, "messageId": (result or {}).get("message_id")}


def build_publish_full(today: date | None = None) -> str:
    schedule = load_schedule()
    start = parse_start_date(os.getenv("DAILY_PUBLISH_START_DATE"))
    today = today or date.today()
    day_index = sprint_day_index(start, today)
    return build_publish_brief(schedule, day_index)
