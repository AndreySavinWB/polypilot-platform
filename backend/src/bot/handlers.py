import json
import os
import re

from src.bot import config, store, telegram_api
from src.bot.ceo_brief import build_morning_brief, build_publish_full, is_ceo_chat

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DISCLAIMER = (
    "PolyPilot — аналитический и образовательный инструмент. "
    "Не финансовый совет. Мы не обещаем прибыль."
)


def _load_featured_event(event_id=None):
    path = os.path.join(ROOT, "data", "events-live.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    events = data.get("events") or []
    if event_id:
        for ev in events:
            if str(ev.get("id")) == str(event_id):
                return ev
    for ev in events:
        if ev.get("hot"):
            return ev
    return events[0] if events else None


def _guest_url(event_id, source="bot"):
    return f"{config.site_base()}/guest-event.html?id={event_id}&utm_source={source}&utm_campaign=funnel_1_0"


def _learn_starter_url(source="bot"):
    return f"{config.site_base()}/learn.html?utm_source={source}&utm_campaign=starter_cohort_1#starter"


def _keyboard(rows):
    return {"inline_keyboard": rows}


def _starter_keyboard():
    return _keyboard([
        [{"text": "Записаться в cohort", "callback_data": "starter_apply"}],
        [{"text": "Страница cohort на сайте", "url": _learn_starter_url()}],
        [{"text": "Канал PolyPilot", "url": config.channel_url()}],
    ])


def _welcome_keyboard(event_id):
    return _keyboard([
        [{"text": "Открыть разбор", "url": _guest_url(event_id)}],
        [{"text": "PolyPilot Starter", "callback_data": "starter_intro"}],
        [{"text": "Обучение на сайте", "url": f"{config.site_base()}/learn.html"}],
        [{"text": "Канал", "url": config.channel_url()}],
    ])


def _parse_start_payload(text):
    if not text:
        return ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return ""
    return parts[1].strip()


def _starter_intro_text():
    return (
        "<b>PolyPilot Starter</b> — первый cohort\n\n"
        "Что входит:\n"
        "• mini-course: Polymarket с нуля\n"
        "• 3 live разбора актуальных событий\n"
        "• 7 дней research feed\n\n"
        "Не сигналы. Не «гарантированная прибыль».\n"
        "Early price: <b>4 990 ₽</b> (первые 10 мест)\n\n"
        f"{DISCLAIMER}\n\n"
        "Нажми «Записаться» и отправь одним сообщением:\n"
        "1) @username или email\n"
        "2) Интерес: Polymarket с нуля / разбор событий / метод PolyPilot"
    )


def _starter_apply_prompt():
    return (
        "Отлично. Ответь одним сообщением:\n\n"
        "1) @username или email\n"
        "2) Что интереснее: Polymarket с нуля / разбор событий / метод PolyPilot\n\n"
        "Пришлём реквизиты для manual payment.\n\n"
        f"<i>{DISCLAIMER}</i>"
    )


def _default_welcome_text(event):
    title = event.get("title") or "актуальное событие"
    event_id = event.get("id") or ""
    odds = event.get("marketOdds")
    odds_line = f"Рынок сейчас: <b>{odds}%</b>\n\n" if odds is not None else ""
    return (
        "Привет. Это <b>PolyPilot</b> — аналитика prediction markets.\n\n"
        f"{DISCLAIMER}\n\n"
        f"Открыт разбор события:\n<b>{title}</b>\n\n"
        f"{odds_line}"
        "Открой карточку (60–90 сек) — завтра пришлём ещё события, которые стоит понять."
    )


def _event_welcome_text(event):
    title = event.get("title") or "Событие"
    summary = event.get("summary") or event.get("verdictText") or ""
    if len(summary) > 280:
        summary = summary[:277] + "..."
    odds = event.get("marketOdds")
    odds_line = f"Рынок: <b>{odds}%</b>\n" if odds is not None else ""
    body = f"{summary}\n\n" if summary else ""
    return (
        f"<b>{title}</b>\n\n"
        f"{odds_line}"
        f"{body}"
        f"{DISCLAIMER}\n\n"
        "Полный разбор — по кнопке ниже."
    )


def _application_received_text():
    return (
        "Заявка принята. Спасибо.\n\n"
        "Мы свяжемся в Telegram с деталями оплаты и доступом в cohort.\n\n"
        f"<i>{DISCLAIMER}</i>"
    )


def _signal_guard_reply():
    return (
        "PolyPilot не даёт торговые сигналы и не обещает прибыль.\n\n"
        "Можем помочь разобраться в событии и методологии:\n"
        f"• {_learn_starter_url()}\n"
        f"• {config.channel_url()}"
    )


def send_starter_intro(chat_id, token):
    telegram_api.send_message(
        token,
        chat_id,
        _starter_intro_text(),
        reply_markup=_starter_keyboard(),
    )


def _ceo_only_reply(chat_id, token, text):
    if is_ceo_chat(chat_id):
        telegram_api.send_message(token, chat_id, text, parse_mode="HTML")
        return True
    telegram_api.send_message(
        token,
        chat_id,
        "Эта команда только для CEO. Для разбора события: /start",
    )
    return False


def handle_ceo_today(chat_id, token):
    from src.bot.ceo_brief import build_morning_brief_plain
    telegram_api.send_plain(token, chat_id, build_morning_brief_plain())


def handle_ceo_publish(chat_id, token):
    telegram_api.send_message(
        token,
        chat_id,
        build_publish_full(),
        parse_mode=None,
    )


def send_default_welcome(chat_id, token, payload=""):
    event_id = None
    if payload.startswith("event_"):
        event_id = payload[len("event_"):]
    event = _load_featured_event(event_id)
    if not event:
        telegram_api.send_message(
            token,
            chat_id,
            (
                "Привет. Это <b>PolyPilot</b>.\n\n"
                f"{DISCLAIMER}\n\n"
                "Сейчас нет live-события для разбора — загляни на сайт или в канал."
            ),
            reply_markup=_keyboard([
                [{"text": "PolyPilot Starter", "callback_data": "starter_intro"}],
                [{"text": "Сайт", "url": config.site_base() + "/events.html"}],
                [{"text": "Канал", "url": config.channel_url()}],
            ]),
        )
        return

    eid = event.get("id")
    telegram_api.send_message(
        token,
        chat_id,
        _default_welcome_text(event),
        reply_markup=_welcome_keyboard(eid),
    )


def handle_start(chat_id, token, payload=""):
    store.set_user(chat_id, {"state": None, "startPayload": payload or "direct"})
    if payload == "starter" or payload.startswith("starter_"):
        send_starter_intro(chat_id, token)
        return
    if payload.startswith("event_"):
        event_id = payload[len("event_"):]
        event = _load_featured_event(event_id)
        if event:
            telegram_api.send_message(
                token,
                chat_id,
                _event_welcome_text(event),
                reply_markup=_welcome_keyboard(event.get("id")),
            )
            return
    send_default_welcome(chat_id, token, payload)


def handle_callback(callback, token):
    chat_id = callback["message"]["chat"]["id"]
    data = callback.get("data") or ""
    callback_id = callback["id"]

    if data == "starter_intro":
        telegram_api.answer_callback(token, callback_id)
        send_starter_intro(chat_id, token)
        return

    if data == "starter_apply":
        store.set_user(chat_id, {"state": "awaiting_starter_application"})
        telegram_api.answer_callback(token, callback_id, "Напиши заявку одним сообщением")
        telegram_api.send_message(token, chat_id, _starter_apply_prompt())
        return

    telegram_api.answer_callback(token, callback_id)


def handle_message(message, token):
    chat = message["chat"]
    chat_id = chat["id"]
    text = (message.get("text") or "").strip()
    username = message.get("from", {}).get("username")

    if text.startswith("/start"):
        payload = _parse_start_payload(text)
        handle_start(chat_id, token, payload)
        return

    if text.startswith("/starter"):
        handle_start(chat_id, token, "starter")
        return

    if text.startswith("/today") or text.startswith("/brief"):
        if is_ceo_chat(chat_id):
            handle_ceo_today(chat_id, token)
        else:
            _ceo_only_reply(chat_id, token, "")
        return

    if text.startswith("/publish"):
        if is_ceo_chat(chat_id):
            handle_ceo_publish(chat_id, token)
        else:
            _ceo_only_reply(chat_id, token, "")
        return

    if text.startswith("/help"):
        if is_ceo_chat(chat_id):
            telegram_api.send_message(
                token,
                chat_id,
                (
                    "<b>PolyPilot CEO</b>\n\n"
                    "/today — задачи на день + план контента\n"
                    "/publish — полный текст поста в канал\n"
                    "/start — как у обычного пользователя\n\n"
                    "Автобудильник: 9:00 Europe/Moscow (GitHub Actions)"
                ),
                parse_mode="HTML",
            )
            return
        telegram_api.send_message(
            token,
            chat_id,
            (
                "<b>PolyPilot bot</b>\n\n"
                "/start — разбор события и ссылки\n"
                "/starter — заявка в PolyPilot Starter\n\n"
                f"{DISCLAIMER}"
            ),
            reply_markup=_keyboard([
                [{"text": "PolyPilot Starter", "callback_data": "starter_intro"}],
                [{"text": "Канал", "url": config.channel_url()}],
            ]),
        )
        return

    lowered = text.lower()
    if re.search(r"\b(сигнал|ставк|bet|signal)\b", lowered):
        telegram_api.send_message(token, chat_id, _signal_guard_reply())
        return

    user = store.get_user(chat_id) or {}
    if user.get("state") == "awaiting_starter_application" and text:
        store.save_starter_application(chat_id, username, text)
        store.set_user(chat_id, {"state": None, "starterApplied": True})
        telegram_api.send_message(token, chat_id, _application_received_text())
        return

    telegram_api.send_message(
        token,
        chat_id,
        (
            "Не понял запрос.\n\n"
            "/start — разбор события\n"
            "/starter — cohort PolyPilot Starter"
        ),
        reply_markup=_keyboard([
            [{"text": "Starter", "callback_data": "starter_intro"}],
        ]),
    )


def handle_update(update, token=None):
    token = token or config.bot_token()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    if "message" in update:
        handle_message(update["message"], token)
        return {"ok": True}

    if "callback_query" in update:
        handle_callback(update["callback_query"], token)
        return {"ok": True}

    return {"ok": True, "skipped": True}
