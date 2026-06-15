"""External Market Check — PIE step 5.6 (Polymarket Analytics).

Verifies whether the event exists on polymarketanalytics.com and what useful
market-behavior signals can be taken from external analytics.

Polymarket Analytics is NOT the source of truth — Polymarket / our scanner is.
This block is an auxiliary check on market behavior.
"""
from __future__ import annotations

from typing import Any

LOOKUP_STATUSES = ("found", "not_found", "similar_found", "error")
MARKET_CHARACTER = ("alive", "thin", "weird", "insufficient_data")
LIQUIDITY_LEVELS = ("low", "medium", "high", "unknown")
PRICE_RELIABILITY = ("reliable", "distorted", "unknown")
TRUST_LEVELS = ("low", "medium", "high")
IMPACT_VALUES = (
    "positive",
    "negative",
    "neutral",
    "weak_positive",
    "weak_negative",
)

PMA_BASE = "https://polymarketanalytics.com"


def empty_external_market_check(
    lookup_status: str = "not_found",
    *,
    summary_ru: str | None = None,
) -> dict[str, Any]:
    return {
        "lookupStatus": lookup_status,
        "eventUrl": None,
        "pmAnalyticsUrl": None,
        "features": None,
        "metrics": None,
        "marketCharacter": None,
        "observationsRu": [],
        "summaryRu": summary_ru or "Событие не найдено на Polymarket Analytics.",
        "marketOddsTrust": None,
        "forecastImpact": "neutral",
        "probabilityAdjustPct": 0,
        "dataSource": "stub_v0",
        "scoringMode": "stub_v0",
    }


def tesla_robotaxi_mock() -> dict[str, Any]:
    """Mock PMA check for live-79061 — thin market, price may distort."""
    slug = "will-tesla-launch-robotaxis-in-california-by-june-30"
    url = f"{PMA_BASE}/events/{slug}"
    return {
        "lookupStatus": "found",
        "eventUrl": f"https://polymarket.com/event/{slug}",
        "pmAnalyticsUrl": url,
        "features": {
            "priceChartAvailable": True,
            "orderBookAvailable": True,
            "similarMarketsAvailable": True,
            "traderWhaleDataAvailable": False,
        },
        "metrics": {
            "liquidityLevel": "low",
            "spreadLevel": "low",
            "priceReliability": "distorted",
            "sharpPriceMove": False,
            "orderBookSkew": "balanced",
            "anomalies": ["thin_liquidity", "low_volume_24h"],
        },
        "marketCharacter": "thin",
        "observationsRu": [
            "Ликвидность низкая — в стакане мало денег.",
            "Цена может искажаться из-за редких сделок.",
            "Резких скачков за последние дни не видно.",
        ],
        "summaryRu": (
            "Рынок тонкий: внешняя аналитика подтверждает низкую ликвидность. "
            "Рыночную цену лучше использовать осторожно."
        ),
        "marketOddsTrust": "low",
        "forecastImpact": "weak_negative",
        "probabilityAdjustPct": 0,
        "dataSource": "polymarket_analytics_stub",
        "scoringMode": "mock_v1",
    }


def _liquidity_level(liquidity: float | None) -> str:
    if liquidity is None:
        return "unknown"
    if liquidity >= 100_000:
        return "high"
    if liquidity >= 25_000:
        return "medium"
    return "low"


def _character_from_metrics(liquidity_level: str, reliability: str, anomalies: list) -> str:
    if liquidity_level == "unknown" and not anomalies:
        return "insufficient_data"
    if "manipulation_suspect" in anomalies or reliability == "distorted":
        return "weird"
    if liquidity_level == "low":
        return "thin"
    return "alive"


def build_external_market_check(
    event: dict,
    normalized_event: dict | None = None,
    market_intelligence: dict | None = None,
    market_structure: dict | None = None,
) -> dict[str, Any]:
    """Build externalMarketCheck from pipeline context. MVP: no PMA API yet."""
    event_id = str(event.get("id") or "")
    if event_id == "79061":
        return tesla_robotaxi_mock()

    normalized_event = normalized_event or {}
    market_structure = market_structure or {}
    snapshot = normalized_event.get("marketSnapshot") or {}

    # Without PMA API we cannot honestly claim "found".
    if not snapshot and not event.get("sourceUrl"):
        return empty_external_market_check()

    return empty_external_market_check(
        summary_ru="Событие не найдено на Polymarket Analytics.",
    )


def run_external_market_check(
    event_id: str | None = None,
    *,
    event: dict | None = None,
    normalized_event: dict | None = None,
    market_intelligence: dict | None = None,
    market_structure: dict | None = None,
) -> dict[str, Any]:
    """Pipeline entry point for step 5.6."""
    if event:
        return build_external_market_check(
            event,
            normalized_event,
            market_intelligence,
            market_structure,
        )
    if str(event_id) == "79061":
        return tesla_robotaxi_mock()
    return empty_external_market_check()
