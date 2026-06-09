"""Russian localization for Polymarket events shown in PolyPilot MVP."""

import json
import re

from src.services.llm import ask_llm, has_llm_key


TITLE_RU = {
    "16183": "Kraken проведёт IPO до…?",
    "16263": "Макрон уйдёт с поста до…?",
    "16423": "В Великобритании объявят выборы до…?",
    "17526": "Военный конфликт Китай — Индия до…?",
    "17549": "Войска НАТО/ЕС будут сражаться на Украине до…?",
    "17725": "Стармер уйдёт с поста до…?",
    "17858": "Украина признает суверенитет России над своей территорией до…?",
    "18558": "На Украине объявят выборы до…?",
    "18571": "Какая-либо страна выйдет из НАТО до…?",
    "18576": "На Украине пройдут выборы до…?",
}

AGENT_NAMES_RU = {
    "Priority Agent": "Агент приоритета",
    "News Scout": "Разведчик новостей",
    "Risk Officer": "Офицер рисков",
    "Verdict Agent": "Агент вердикта",
}

DECISION_RU = {
    "accepted": "ПРИНЯТО",
    "watchlist": "НАБЛЮДЕНИЕ",
    "rejected": "ОТКЛОНЕНО",
}

RISK_LEVEL_RU = {
    "low": "НИЗКИЙ",
    "medium": "СРЕДНИЙ",
    "high": "ВЫСОКИЙ",
}

VERDICT_STATUS_RU = {
    "yes": "ДА",
    "no": "НЕТ",
    "pending": "ОЖИДАНИЕ",
    "watchlist": "НАБЛЮДЕНИЕ",
    "research_required": "НУЖЕН АНАЛИЗ",
    "watch": "НАБЛЮДЕНИЕ",
}


def _has_cyrillic(text):
    return bool(text and re.search(r"[а-яА-ЯёЁ]", str(text)))


def _needs_translation(text):
    if not text or not str(text).strip():
        return False
    return not _has_cyrillic(str(text))


def translate_title(event_id, title_en):
    return TITLE_RU.get(str(event_id)) or title_en


def translate_verdict_token(token):
    if not token:
        return token
    key = str(token).strip().lower()
    return VERDICT_STATUS_RU.get(key, str(token).upper() if len(str(token)) <= 12 else token)


def localize_analysis_texts(analysis):
    """Translate analysis fields to Russian via LLM when needed."""
    priority = analysis.get("priority") or {}
    news = analysis.get("newsScout") or {}
    risk = analysis.get("riskOfficer") or {}
    verdict = analysis.get("verdict") or {}

    payload = {
        "priorityReason": priority.get("reason") or "",
        "newsSummary": news.get("summary") or "",
        "newsFacts": news.get("facts") or [],
        "newsMissing": news.get("missing") or [],
        "riskFlags": risk.get("flags") or [],
        "ppVerdict": verdict.get("ppVerdict") or "",
    }

    if not has_llm_key() or not any(_needs_translation(v) for v in [
        payload["priorityReason"],
        payload["newsSummary"],
        *payload["newsFacts"],
        *payload["newsMissing"],
        *payload["riskFlags"],
        payload["ppVerdict"],
    ]):
        return payload

    try:
        result = ask_llm(
            """Ты переводчик для рускоязычной платформы прогнозных рынков PolyPilot.
Переведи ВСЕ текстовые поля на русский язык. Сохраняй имена собственные (Macron, Starmer, NATO, Kraken, Ukraine).
Верни ТОЛЬКО JSON с теми же ключами: priorityReason, newsSummary, newsFacts, newsMissing, riskFlags, ppVerdict.
Короткие токены вроде Yes/No/pending/watchlist переводи смыслом: Да/Нет/ожидание/наблюдение.""",
            payload,
        )
        for key in payload:
            if result.get(key):
                payload[key] = result[key]
    except Exception:
        pass

    return payload


def localize_description(description, title_ru):
    if not description:
        return ""
    if _has_cyrillic(description):
        return description[:400]
    if not has_llm_key():
        return f"Рынок прогнозов на Полимаркете: {title_ru}"

    try:
        result = ask_llm(
            """Переведи описание рынка прогнозов на русский для обычного пользователя.
Верни JSON: {"summary": "краткое описание 2-3 предложения на русском"}""",
            {"title": title_ru, "description": description[:1200]},
        )
        return (result.get("summary") or description)[:400]
    except Exception:
        return f"Рынок прогнозов на Полимаркете: {title_ru}"
