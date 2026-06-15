"""Hashdive / Whale Check — PIE step 5.7.

Tracks what large players (whales) are doing — NOT general market structure.
Market structure = Polymarket Analytics (5.6). Whales = Hashdive (5.7).

Source MVP: Hashdive (migrated to Unusual Whales Predictions) — stub until API key.
Auxiliary signal: max ~10% weight on PP probability.
"""
from __future__ import annotations

from typing import Any

LOOKUP_STATUSES = ("found", "not_found", "similar_found", "error", "not_supported")
WHALE_LEAN = ("yes", "no", "neutral", "mixed")
MAIN_VERDICTS = (
    "yes_leaning",
    "no_leaning",
    "neutral",
    "against_market",
    "no_data",
)
SKEW_STRENGTH = ("weak", "medium", "strong")
IMPACT_VALUES = (
    "neutral",
    "weak_positive",
    "weak_negative",
    "moderate_positive",
    "moderate_negative",
)

MAX_WHALE_WEIGHT_PCT = 10
HASHDIVE_BASE = "https://hashdive.com"


def empty_whale_check(
    lookup_status: str = "not_found",
    *,
    summary_ru: str | None = None,
) -> dict[str, Any]:
    text = summary_ru or (
        "Данных по крупным игрокам нет. "
        "Hashdive не нашёл это событие или не даёт по нему полезной информации."
    )
    return {
        "lookupStatus": lookup_status,
        "sourceName": "Hashdive / Unusual Whales Predictions",
        "eventUrl": None,
        "hashdiveUrl": None,
        "status": "no_data",
        "whaleLean": None,
        "mainVerdict": "no_data",
        "headlineRu": "Данных по крупным игрокам нет",
        "yesWhaleVolumeUsd": None,
        "noWhaleVolumeUsd": None,
        "netWhalePressureUsd": None,
        "skewStrength": None,
        "againstMarket": False,
        "againstCrowd": False,
        "explanationRu": text,
        "summaryRu": text,
        "forecastImpact": "neutral",
        "weightPct": 0,
        "maxWeightPct": MAX_WHALE_WEIGHT_PCT,
        "passToRiskOfficer": [],
        "contradictionHints": [],
        "dataSource": "stub_v0",
        "scoringMode": "stub_v0",
    }


def tesla_robotaxi_mock() -> dict[str, Any]:
    """Mock whale check for live-79061 — whales lean YES vs thin market at ~3%."""
    slug = "will-tesla-launch-robotaxis-in-california-by-june-30"
    return {
        "lookupStatus": "found",
        "sourceName": "Hashdive / Unusual Whales Predictions",
        "eventUrl": f"https://polymarket.com/event/{slug}",
        "hashdiveUrl": f"{HASHDIVE_BASE}/market/{slug}",
        "status": "ready",
        "whaleLean": "yes",
        "mainVerdict": "against_market",
        "headlineRu": "Киты идут против рынка",
        "yesWhaleVolumeUsd": 84000,
        "noWhaleVolumeUsd": 11000,
        "netWhalePressureUsd": 73000,
        "skewStrength": "medium",
        "againstMarket": True,
        "againstCrowd": False,
        "explanationRu": (
            "За последние 24 часа крупные игроки вложили заметно больше денег в YES, "
            "чем в NO — при том что рынок оценивает YES около 3%."
        ),
        "summaryRu": (
            "Киты идут против рынка. Это важный сигнал, но требует дополнительной проверки: "
            "ликвидность низкая, крупная сделка может искажать цену."
        ),
        "forecastImpact": "moderate_positive",
        "weightPct": 5,
        "maxWeightPct": MAX_WHALE_WEIGHT_PCT,
        "passToRiskOfficer": ["thin_market_whale_entry", "whales_vs_market"],
        "contradictionHints": ["whales_vs_market"],
        "dataSource": "hashdive_stub",
        "scoringMode": "mock_v1",
    }


def build_whale_check(
    event: dict,
    normalized_event: dict | None = None,
    market_intelligence: dict | None = None,
    *,
    market_odds_pct: float | None = None,
    crowd_pulse: dict | None = None,
) -> dict[str, Any]:
    """Build whaleCheck from pipeline context. MVP: no Hashdive API yet."""
    event_id = str(event.get("id") or "")
    if event_id == "79061":
        return tesla_robotaxi_mock()
    return empty_whale_check()


def run_whale_check(
    event_id: str | None = None,
    *,
    event: dict | None = None,
    normalized_event: dict | None = None,
    market_intelligence: dict | None = None,
    market_odds_pct: float | None = None,
    crowd_pulse: dict | None = None,
) -> dict[str, Any]:
    """Pipeline entry point for step 5.7."""
    if event:
        return build_whale_check(
            event,
            normalized_event,
            market_intelligence,
            market_odds_pct=market_odds_pct,
            crowd_pulse=crowd_pulse,
        )
    if str(event_id) == "79061":
        return tesla_robotaxi_mock()
    return empty_whale_check()
