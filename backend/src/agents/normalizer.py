"""Event Normalizer — PIE v1.0b.

rawEvent → normalizedEvent (включает marketSnapshot внутри).
Контракт: INTELLIGENCE_DATA_FLOW §2 + POLYPILOT_STATE.md output contract.
"""

from __future__ import annotations

import json
import re

from src.agents.priority import _days_to_end, _parse_prices, _to_number
from src.services.llm import ask_llm, has_llm_key
from src.services.localize import translate_title

RESOLUTION_MARKERS = (
    "resolve", "resolution", "will resolve", "resolves", "резолв",
    "this market will", "outcome will be",
)

OFFICIAL_SOURCES = (
    (r"federalreserve\.gov|fomc", "ФРС США"),
    (r"uma\.xyz|uma\s+protocol", "UMA"),
    (r"congress\.gov|whitehouse\.gov", "Официальный источник США"),
    (r"gov\.uk|parliament\.uk", "Официальный источник Великобритании"),
    (r"sec\.gov", "SEC США"),
    (r"bls\.gov", "Bureau of Labor Statistics"),
)


def _has_cyrillic(text):
    return bool(text and re.search(r"[а-яА-ЯёЁ]", str(text)))


def _primary_market(event):
    markets = event.get("markets") or []
    return markets[0] if markets else {}


def _title_ru(event):
    event_id = str(event.get("id") or "")
    title = (event.get("title") or _primary_market(event).get("question") or "").strip()
    mapped = translate_title(event_id, title)
    if mapped != title or _has_cyrillic(mapped):
        return mapped
    if has_llm_key() and not _has_cyrillic(title) and title:
        try:
            result = ask_llm(
                """Переведи заголовок рынка прогнозов на короткий русский вопрос (до 80 символов).
Верни JSON: {"titleRu": "..."}
Сохраняй имена собственные. Формат: вопрос с «?» в конце.""",
                {"title": title[:200]},
            )
            translated = (result.get("titleRu") or "").strip()
            if translated:
                return translated
        except Exception:
            pass
    return title


def _resolution_criteria(event):
    description = (event.get("description") or "").strip()
    question = (_primary_market(event).get("question") or event.get("title") or "").strip()
    if description:
        text = description.replace("\n", " ").strip()
        for marker in ("This market will resolve", "This market resolves", "Resolves YES"):
            idx = text.find(marker)
            if idx >= 0:
                text = text[idx:]
                break
        criteria = text[:500].strip()
        if question and question.lower() not in criteria.lower():
            criteria = f"{question}. {criteria}"
        return criteria
    if question:
        return f"Рынок резолвится по исходу: {question}"
    return ""


def _decision_maker(event):
    text = f"{event.get('description') or ''} {event.get('title') or ''}".lower()
    for pattern, label in OFFICIAL_SOURCES:
        if re.search(pattern, text, re.IGNORECASE):
            return label
    if "uma" in text:
        return "UMA / Polymarket"
    return "Polymarket / UMA"


def _resolution_unclear(event, criteria):
    description = (event.get("description") or "").strip()
    markets_count = int(event.get("marketsCount") or len(event.get("markets") or []))
    if not description and not criteria:
        return True
    if len(description) < 80 and markets_count > 1:
        return True
    if markets_count > 6:
        return True
    text = description.lower()
    has_marker = any(m in text for m in RESOLUTION_MARKERS)
    has_binary = bool(re.search(r"\byes\b|\bno\b", text))
    if description and not has_marker and not has_binary and markets_count > 2:
        return True
    return False


def _build_flags(event, criteria):
    flags = []
    if not event.get("endDate"):
        flags.append("missing_end_date")
    if _resolution_unclear(event, criteria):
        flags.append("resolution_unclear")
    markets_count = int(event.get("marketsCount") or len(event.get("markets") or []))
    if markets_count > 4:
        flags.append("multi_market_complex")
    return flags


def _normalization_status(flags):
    if "resolution_unclear" in flags:
        return "rejected"
    if flags:
        return "flags"
    return "ok"


def _market_prob(event):
    """Returns probability as 0.0–1.0 float."""
    market = _primary_market(event)
    price = _parse_prices(market.get("outcomePrices"))
    if price is None:
        return None
    return round(float(price), 4)


def _spread_pct(event):
    market = _primary_market(event)
    raw = market.get("outcomePrices")
    if raw is None:
        return None
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if not raw or len(raw) < 2:
        return None
    try:
        yes = float(raw[0])
        no = float(raw[1])
        return round(abs(1.0 - yes - no), 4)
    except (TypeError, ValueError):
        return None


def _price_change_24h(event):
    for key in ("oneDayPriceChange", "priceChange24h", "price_change_24h"):
        value = event.get(key) or _primary_market(event).get(key)
        if value is not None:
            try:
                v = float(value)
                return round(v if abs(v) > 1 else v, 4)
            except (TypeError, ValueError):
                continue
    return None


def normalize_event_pie(event):
    """PIE step 1: rawEvent → {"normalizedEvent": {...}} per output contract."""
    criteria = _resolution_criteria(event)
    horizon = _days_to_end(event)
    flags = _build_flags(event, criteria)

    market_snapshot = {
        "marketProb": _market_prob(event),
        "volume": round(_to_number(event.get("volume")), 2),
        "volume24h": round(_to_number(event.get("volume24hr")), 2),
        "liquidity": round(_to_number(event.get("liquidity")), 2),
        "priceChange24h": _price_change_24h(event),
        "spread": _spread_pct(event),
    }

    normalized_event = {
        "titleRu": _title_ru(event),
        "resolutionCriteria": criteria,
        "horizonDays": horizon,
        "decisionMaker": _decision_maker(event),
        "flags": flags,
        "normalizationStatus": _normalization_status(flags),
        "marketSnapshot": market_snapshot,
    }

    return {"normalizedEvent": normalized_event}
