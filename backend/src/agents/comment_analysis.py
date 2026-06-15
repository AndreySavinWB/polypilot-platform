"""Comment Analysis — blocks 5.5A / 5.5B / 5.5C (Crowd Pulse).

Separates Polymarket event comments from external social discussion.
Auxiliary signal only: max ~10% weight on PP probability.
"""
from __future__ import annotations

from typing import Any

MAX_CROWD_WEIGHT_PCT = 10
MAX_MARKET_COMMENTS_WEIGHT_PCT = 7
MAX_SOCIAL_WEIGHT_PCT = 5

LEAN_VALUES = ("yes", "no", "split", "unclear")
QUALITY_VALUES = ("high", "medium", "low")
NOISE_VALUES = ("low", "medium", "high")
IMPACT_VALUES = (
    "positive",
    "negative",
    "neutral",
    "weak_positive",
    "weak_negative",
)


def empty_crowd_pulse(status: str = "insufficient") -> dict[str, Any]:
    return {
        "status": status,
        "maxWeightPct": MAX_CROWD_WEIGHT_PCT,
        "marketComments": None,
        "socialDiscussion": None,
        "synthesis": None,
        "scoringMode": "stub_v0",
    }


def tesla_robotaxi_mock() -> dict[str, Any]:
    """Mock Crowd Pulse for live-79061 (MVP / UI preview). API stubs until collectors ship."""
    market = {
        "commentCount": 47,
        "lean": "no",
        "argumentsYes": [
            "Tesla уже тестирует FSD — запуск возможен до июня.",
            "В Калифорнии есть разрешения на robotaxi-пилоты.",
        ],
        "argumentsNo": [
            "Спорят, будет ли запуск считаться полноценным по правилам рынка.",
            "Нужен публичный сервис без водителя — демо не засчитают.",
        ],
        "resolutionDispute": True,
        "hasSourceLinks": True,
        "noiseSignals": ["resolve_rules_debate", "speculation"],
        "quality": "medium",
        "noiseLevel": "high",
        "summaryRu": (
            "Участники рынка осторожны: много споров о том, что именно засчитается "
            "запуском по правилам Polymarket."
        ),
        "weightPct": 4,
        "dataSource": "polymarket_comments_stub",
    }
    social = {
        "sources": [
            {"platform": "x", "found": True, "activityTrend": "rising"},
            {"platform": "reddit", "found": True, "activityTrend": "stable"},
            {"platform": "youtube", "found": True, "activityTrend": "rising"},
            {"platform": "telegram", "found": False, "activityTrend": "unknown"},
            {"platform": "news", "found": True, "activityTrend": "stable"},
        ],
        "lean": "yes",
        "arguments": [
            "Соцсети обсуждают заявления Tesla о robotaxi в Калифорнии.",
            "Есть хайп вокруг демо и тестовых поездок.",
        ],
        "freshFacts": False,
        "viralHype": True,
        "expertSources": False,
        "quality": "medium",
        "noiseLevel": "medium",
        "summaryRu": (
            "Внешняя аудитория склоняется к YES: верят в запуск и цитируют "
            "новости Tesla, но без новых официальных фактов."
        ),
        "weightPct": 3,
        "dataSource": "social_stub",
    }
    synthesis = {
        "alignment": "divergent",
        "contradiction": (
            "Участники рынка осторожнее из-за правил резолва; соцсети оптимистичнее."
        ),
        "repeatedArgument": "Запуск robotaxi в Калифорнии до 30 июня",
        "mainRiskFromDiscussion": "Спор по формулировке «полноценного» публичного сервиса",
        "forecastImpact": "weak_positive",
        "probabilityAdjustPct": 2,
        "summaryRu": (
            "Обсуждения расходятся. Соцсети оптимистичны, но участники рынка "
            "осторожнее из-за правил события."
        ),
        "totalWeightPct": 5,
        "passToRiskOfficer": ["resolutionDispute", "high_noise_market_comments"],
    }
    return {
        "status": "ready",
        "maxWeightPct": MAX_CROWD_WEIGHT_PCT,
        "marketComments": market,
        "socialDiscussion": social,
        "synthesis": synthesis,
        "scoringMode": "mock_v1",
    }


def run_comment_analysis(event_id: str | None = None) -> dict[str, Any]:
    """Entry point for pipeline step 5.5. MVP: mock for Tesla, empty elsewhere."""
    if str(event_id) == "79061":
        return tesla_robotaxi_mock()
    return empty_crowd_pulse()
