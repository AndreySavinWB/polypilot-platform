"""Checked Review — «Мы проверили» block for Simple open card.

Marks only what PIE agents actually processed. Stubs and empty collectors stay unchecked.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

CHECK_CATALOG: list[tuple[str, str]] = [
    ("eventRules", "Формулировка и правила резолва"),
    ("news", "Новости"),
    ("official", "Официальные источники"),
    ("social", "X / Reddit / соцсети"),
    ("trends", "Google Trends / поисковый интерес"),
    ("youtubeMedia", "YouTube / медиа"),
    ("marketComments", "Комментарии участников рынка"),
    ("comparableEvents", "Похожие события"),
    ("polymarketHistory", "Исторические данные Polymarket"),
    ("externalAnalytics", "Внешние аналитические сервисы"),
    ("contradictions", "Противоречия между источниками"),
    ("risks", "Риски и неизвестные"),
]

STUB_MARKERS = ("stub", "mock")


def _is_real_source(data_source: str | None) -> bool:
    if not data_source:
        return True
    lower = data_source.lower()
    return not any(marker in lower for marker in STUB_MARKERS)


def _count_type(evidence: dict, item_type: str) -> int:
    counts = evidence.get("counts") or {}
    if item_type in counts:
        return int(counts.get(item_type) or 0)
    items = evidence.get("items") or []
    return sum(1 for it in items if it.get("type") == item_type)


def _social_platforms_found(crowd_pulse: dict, platforms: set[str]) -> bool:
    social = crowd_pulse.get("socialDiscussion") or {}
    if not _is_real_source(social.get("dataSource")):
        return False
    for src in social.get("sources") or []:
        if src.get("found") and src.get("platform") in platforms:
            return True
    return False


def _market_comments_checked(crowd_pulse: dict) -> bool:
    market = crowd_pulse.get("marketComments") or {}
    if not market or not _is_real_source(market.get("dataSource")):
        return False
    return int(market.get("commentCount") or 0) > 0


def _pma_analytics_checked(pma: dict) -> bool:
    if pma.get("lookupStatus") not in ("found", "similar_found"):
        return False
    return _is_real_source(pma.get("dataSource"))


def _hashdive_whale_checked(whale: dict) -> bool:
    if whale.get("lookupStatus") not in ("found", "similar_found"):
        return False
    if whale.get("status") != "ready":
        return False
    return _is_real_source(whale.get("dataSource"))


def _resolve_last_checked(
    package: dict,
    analysis: dict | None,
    generated_at: str | None = None,
) -> str:
    for key in ("publishedAt", "analyzedAt", "updatedAt"):
        value = package.get(key)
        if value:
            return str(value)[:10]

    news_scout = (analysis or {}).get("newsScout") or {}
    if news_scout.get("generatedAt"):
        return str(news_scout["generatedAt"])[:10]

    return (generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%d"))[:10]


def build_checked_review(
    package: dict,
    analysis: dict | None = None,
    event: dict | None = None,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build checkedReview for live card from pipelinePackage + analysis."""
    package = package or {}
    analysis = analysis or {}
    event = event or {}

    normalized = package.get("normalizedEvent") or {}
    evidence = package.get("evidence") or {}
    crowd_pulse = package.get("crowdPulse") or {}
    mi = package.get("marketIntelligence") or {}
    market_snapshot = normalized.get("marketSnapshot") or {}
    probability = package.get("probability") or {}

    news_scout = analysis.get("newsScout") or {}
    risk = package.get("risk") or analysis.get("riskOfficer") or {}
    analogs = package.get("analogs") or []
    contradictions = package.get("contradictionMap") or []

    market_prob = market_snapshot.get("marketProb")
    pp_prob = probability.get("ppProb")
    if market_prob is not None and pp_prob is not None:
        try:
            edge_pp = abs(float(pp_prob) - float(market_prob)) * 100
        except (TypeError, ValueError):
            edge_pp = 0.0
    else:
        edge_pp = 0.0

    flags: dict[str, bool] = {
        "eventRules": bool(
            normalized.get("titleRu")
            and (normalized.get("resolutionCriteria") or event.get("description"))
        ),
        "news": bool(_count_type(evidence, "news") > 0 or news_scout),
        "official": bool(_count_type(evidence, "official") > 0),
        "social": bool(
            _count_type(evidence, "social") > 0
            or _social_platforms_found(crowd_pulse, {"x", "reddit", "telegram"})
        ),
        "trends": bool(_count_type(evidence, "trends") > 0),
        "youtubeMedia": bool(
            _social_platforms_found(crowd_pulse, {"youtube", "news"})
            or any(it.get("type") in {"media", "video"} for it in (evidence.get("items") or []))
        ),
        "marketComments": _market_comments_checked(crowd_pulse),
        "comparableEvents": bool(len(analogs) > 0),
        "polymarketHistory": bool(
            _count_type(evidence, "market") > 0
            or market_snapshot.get("marketProb") is not None
            or event.get("volume") is not None
        ),
        "externalAnalytics": bool(
            _pma_analytics_checked(package.get("externalMarketCheck") or {})
            or _hashdive_whale_checked(package.get("whaleCheck") or {})
            or (
                mi.get("whaleSignal") not in (None, "unknown", "none")
                and bool(mi.get("whaleSignal"))
            )
            or bool((mi.get("sourcesUsed") or []))
        ),
        "contradictions": bool(len(contradictions) > 0 or edge_pp >= 8),
        "risks": bool(risk.get("flags") or risk.get("riskLevel") or risk.get("factors")),
    }

    checks = [{"id": cid, "label": label, "done": flags.get(cid, False)} for cid, label in CHECK_CATALOG]

    return {
        "lastCheckedAt": _resolve_last_checked(package, analysis, generated_at),
        "checks": checks,
        "scoringMode": "rules_v1",
    }
