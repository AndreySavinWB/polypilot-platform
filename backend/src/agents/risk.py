"""Risk Officer — PIE V1.0a (structured rules).

Uses priority + normalized + marketSnapshot. LLM enrichment comes in later phases.
"""

from __future__ import annotations

from src.agents.priority import _to_number

RISK_FACTORS = {
    "low_liquidity": 22,
    "thin_market": 18,
    "resolution_unclear": 28,
    "missing_end_date": 20,
    "multi_market_complex": 14,
    "dead_price": 16,
    "long_horizon": 10,
    "short_horizon": 12,
    "weak_description": 12,
    "priority_watchlist": 8,
}

FLAG_MESSAGES_RU = {
    "low_liquidity": "Низкая ликвидность — цена и исполнение могут искажаться.",
    "thin_market": "Тонкий рынок: мало объёма за 24ч относительно ликвидности.",
    "resolution_unclear": "Правила резолва размыты — нужна ручная проверка.",
    "missing_end_date": "Нет даты окончания рынка.",
    "multi_market_complex": "Много подрынков — сложнее интерпретировать исход.",
    "dead_price": "Цена близка к 0% или 100% — рынок почти решён.",
    "long_horizon": "Длинный горизонт — больше неопределённости до резолва.",
    "short_horizon": "Короткий горизонт — мало времени на подтверждение тезиса.",
    "weak_description": "Слабое описание резолва в метаданных Polymarket.",
    "priority_watchlist": "Событие на наблюдении, не в топе приоритета PP.",
}


def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def _risk_level(score):
    if score <= 33:
        return "low"
    if score <= 66:
        return "medium"
    return "high"


def assess_risk_v1_0a(event, normalized, market_snapshot, priority):
    """Compute structured risk from V1.0a pipeline inputs."""
    triggered = []
    score = 0.0

    liquidity = _to_number((market_snapshot or {}).get("liquidity") or event.get("liquidity"))
    volume_24h = _to_number((market_snapshot or {}).get("volume24h") or event.get("volume24hr"))
    market_prob = (market_snapshot or {}).get("marketProb")
    flags = list((normalized or {}).get("flags") or [])
    horizon = (normalized or {}).get("horizonDays")
    description = (event.get("description") or "").strip()

    if liquidity and liquidity < 10_000:
        triggered.append("low_liquidity")
    if liquidity and volume_24h and volume_24h < liquidity * 0.02 and volume_24h < 2_000:
        triggered.append("thin_market")
    if "resolution_unclear" in flags:
        triggered.append("resolution_unclear")
    if "missing_end_date" in flags:
        triggered.append("missing_end_date")
    if "multi_market_complex" in flags:
        triggered.append("multi_market_complex")
    if market_prob is not None and (market_prob <= 0.02 or market_prob >= 0.98):
        triggered.append("dead_price")
    if horizon is not None and horizon > 365:
        triggered.append("long_horizon")
    if horizon is not None and 0 <= horizon < 7:
        triggered.append("short_horizon")
    if len(description) < 120:
        triggered.append("weak_description")
    if (priority or {}).get("decision") == "watchlist":
        triggered.append("priority_watchlist")

    for key in triggered:
        score += RISK_FACTORS.get(key, 0)

    risk_score = round(_clamp(score), 1)
    risk_level = _risk_level(risk_score)
    risk_flags = [FLAG_MESSAGES_RU[key] for key in triggered if key in FLAG_MESSAGES_RU]
    if not risk_flags:
        risk_flags.append("Критических структурных рисков в доступных метаданных не найдено.")

    return {
        "riskScore": risk_score,
        "riskLevel": risk_level,
        "flags": risk_flags,
        "factors": triggered,
        "scoringMode": "rules_v1_0a",
    }
