"""Strategy Intelligence Layer — PIE v1.0e.

Rules-only Strategy Router v0. It does not invent signals and does not give
trading advice. It maps the existing PIE package into strategy fits:

  - whale_copy: money-flow / volume-anomaly candidate
  - news_lag: event looks catalyst-driven, but external news is still partial
  - education: useful for explaining Polymarket / PolyPilot methodology

Output contract follows STRATEGY_INTELLIGENCE_LAYER.md.
"""

from __future__ import annotations


STRATEGY_VERSION = "strategy_intelligence_v1_0"

STATUS_CANDIDATE = "candidate"
STATUS_WATCHLIST = "watchlist"
STATUS_NOT_A_FIT = "not_a_fit"


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def _status(score: int, candidate_at: int = 65, watchlist_at: int = 40) -> str:
    if score >= candidate_at:
        return STATUS_CANDIDATE
    if score >= watchlist_at:
        return STATUS_WATCHLIST
    return STATUS_NOT_A_FIT


def _snapshot(package: dict) -> dict:
    return ((package.get("normalizedEvent") or {}).get("marketSnapshot") or {})


def _risk_factors(package: dict) -> set[str]:
    return set((package.get("risk") or {}).get("factors") or [])


def _risk_level(package: dict) -> str:
    return (package.get("risk") or {}).get("riskLevel") or "unknown"


def _market_structure(package: dict) -> dict:
    return package.get("marketStructure") or {}


def _has_resolution_issue(package: dict) -> bool:
    flags = set((package.get("normalizedEvent") or {}).get("flags") or [])
    return "resolution_unclear" in flags


def _liquidity_tier(liquidity: float | None) -> str:
    if liquidity is None:
        return "unknown"
    if liquidity >= 250_000:
        return "high"
    if liquidity >= 25_000:
        return "medium"
    return "low"


def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _status_rank(status: str) -> int:
    return {
        STATUS_CANDIDATE: 2,
        STATUS_WATCHLIST: 1,
        STATUS_NOT_A_FIT: 0,
    }.get(status, 0)


def _fit(
    strategy: str,
    score: int,
    status: str,
    reason: str,
    required_checks: list[str] | None = None,
    invalidation: list[str] | None = None,
) -> dict:
    return {
        "strategy": strategy,
        "fitScore": _clamp(score),
        "status": status,
        "reason": reason,
        "requiredChecks": required_checks or [],
        "invalidation": invalidation or [],
    }


def _whale_copy_fit(package: dict) -> dict:
    mi = package.get("marketIntelligence") or {}
    snap = _snapshot(package)
    risk = _risk_factors(package)
    structure = _market_structure(package)

    liquidity = _to_float(snap.get("liquidity"))
    liq_tier = _liquidity_tier(liquidity)
    price_reliability = structure.get("priceReliability") or "unknown"
    manipulation_risk = structure.get("manipulationRisk") or "unknown"
    structure_flags = set(structure.get("flags") or [])
    anomaly = mi.get("volumeAnomaly") or "none"
    whale = mi.get("whaleSignal") or "unknown"
    direction = mi.get("moneyDirection") or "unknown"
    confidence = _to_float(mi.get("confidence")) or 0.0

    score = 0
    reasons: list[str] = []
    checks = ["liquidity", "spread", "entry_timing", "wallet_quality"]
    invalidation = ["late_move", "thin_market", "unclear_resolution", "hedge_flow"]

    if whale in ("accumulation_yes", "accumulation_no"):
        score += 34
        reasons.append(f"whale proxy signal: {whale}")
    elif anomaly == "high" and direction in ("yes", "no"):
        score += 24
        reasons.append("high volume anomaly with directional market bias")
    elif anomaly == "moderate" and direction in ("yes", "no"):
        score += 14
        reasons.append("moderate volume anomaly with directional market bias")

    if anomaly == "high":
        score += 18
    elif anomaly == "moderate":
        score += 10

    if liq_tier == "high":
        score += 18
    elif liq_tier == "medium":
        score += 12
    elif liq_tier == "low":
        score -= 18
        reasons.append("liquidity is low")

    if direction in ("yes", "no"):
        score += 10
    if confidence:
        score += confidence * 20

    if _has_resolution_issue(package):
        score -= 25
        score = min(score, 39)
    if _risk_level(package) == "high":
        score -= 20
    if "low_liquidity" in risk or "thin_market" in risk:
        score -= 15
    if price_reliability == "low":
        score -= 22
        reasons.append("market price reliability is low")
    elif price_reliability == "moderate":
        score -= 6
    elif price_reliability == "high":
        score += 6
    if manipulation_risk == "high":
        score -= 25
        reasons.append("market structure manipulation risk is high")
    elif manipulation_risk == "medium":
        score -= 8
    if "thin_market_whale_combo" in structure_flags:
        score = min(score, 34)
        reasons.append("thin market + whale proxy flow")

    score = _clamp(score)
    if not reasons:
        reasons.append("no directional whale/volume setup in available data")

    return _fit(
        "whale_copy",
        score,
        _status(score),
        "; ".join(reasons),
        checks,
        invalidation,
    )


def _news_lag_fit(package: dict) -> dict:
    ec = package.get("eventClassification") or {}
    ev = package.get("evidence") or {}
    mi = package.get("marketIntelligence") or {}
    priority = package.get("priority") or {}
    structure = _market_structure(package)

    event_type = ec.get("eventType") or "other"
    classifier_conf = _to_float(ec.get("classifierConfidence")) or 0.0
    external_count = sum((ev.get("counts") or {}).get(t, 0) for t in ("news", "social", "trends"))
    official_count = (ev.get("counts") or {}).get("official", 0)

    catalyst_types = {
        "regulatory", "elections", "economics", "geopolitics",
        "legal", "corporate", "crypto",
    }

    score = 0
    reasons: list[str] = []
    checks = ["source_quality", "freshness", "market_reaction", "resolution_link"]
    invalidation = ["stale_news", "weak_source", "already_priced_in", "unclear_resolution"]

    if event_type in catalyst_types:
        score += 24
        reasons.append(f"catalyst-driven event type: {event_type}")
    if classifier_conf >= 0.7:
        score += 10
    elif classifier_conf >= 0.35:
        score += 6

    if external_count:
        score += 25
        reasons.append("external evidence exists")
    elif official_count:
        score += 10
        reasons.append("official/resolution evidence exists, but no external news feed yet")

    if mi.get("volumeSignal") == "rising":
        score += 10
        reasons.append("market activity is rising")

    if structure.get("priceReliability") == "low":
        score -= 8
        reasons.append("market price reliability is low")

    if (priority.get("score") or 0) >= 70:
        score += 8
    if _has_resolution_issue(package):
        score -= 20
        score = min(score, 34)

    # v0 has no real News API yet. Keep this strategy conservative until external evidence exists.
    if not external_count:
        score = min(score, 58)

    score = _clamp(score)
    if not reasons:
        reasons.append("no fresh external catalyst in available data")

    return _fit(
        "news_lag",
        score,
        _status(score, candidate_at=65, watchlist_at=35),
        "; ".join(reasons),
        checks,
        invalidation,
    )


def _education_fit(package: dict) -> dict:
    ec = package.get("eventClassification") or {}
    ev = package.get("evidence") or {}
    norm = package.get("normalizedEvent") or {}
    risk_level = _risk_level(package)
    structure = _market_structure(package)

    event_type = ec.get("eventType") or "other"
    title = norm.get("titleRu") or ""
    counts = ev.get("counts") or {}

    score = 18
    reasons: list[str] = []
    checks = ["simple_resolution", "clear_title", "teachable_contradiction"]
    invalidation = ["too_complex", "unclear_resolution", "no_context"]

    if event_type != "other":
        score += 20
        reasons.append(f"clear event category: {event_type}")
    if title:
        score += 10
    if counts.get("market", 0):
        score += 10
    if counts.get("official", 0):
        score += 10
    has_resolution_issue = _has_resolution_issue(package)
    if not has_resolution_issue:
        score += 15
    else:
        score = min(score, 45)
    if risk_level == "high":
        score -= 12
    if structure.get("priceReliability") == "low":
        score -= 8
    if "multi_market_complex" in set(norm.get("flags") or []):
        score -= 10

    score = _clamp(score)
    if not reasons:
        reasons.append("basic event package can support education content")

    return _fit(
        "education",
        score,
        _status(score, candidate_at=55, watchlist_at=35),
        "; ".join(reasons),
        checks,
        invalidation,
    )


def _queue_for_fit(fit: dict) -> str | None:
    if fit.get("status") == STATUS_NOT_A_FIT:
        return None
    strategy = fit.get("strategy")
    return {
        "whale_copy": "whale_queue",
        "news_lag": "news_queue",
        "education": "education_queue",
    }.get(strategy)


def _verdict_mode(primary_strategy: str | None) -> str:
    return {
        "whale_copy": "copyability",
        "news_lag": "catalyst_lag",
        "education": "education_case",
    }.get(primary_strategy or "", "research")


def _why_selected(primary: dict | None) -> str:
    if not primary:
        return "PP не нашёл сильного торгового setup в доступных данных."
    strategy = primary.get("strategy")
    if strategy == "whale_copy":
        return "PP выбрал событие как candidate для Whale Copy из-за движения денег и структуры рынка."
    if strategy == "news_lag":
        return "PP выбрал событие как News Lag candidate: тема выглядит событийной, но реакцию рынка нужно проверить."
    if strategy == "education":
        return "PP выбрал событие как учебный кейс: на нём можно объяснить механику Polymarket и анализа PP."
    return "PP выбрал событие по стратегии с максимальным fitScore."


def route_strategy(package: dict) -> dict:
    """Add strategyIntelligence to an accepted PIE package."""
    fits = [
        _whale_copy_fit(package),
        _news_lag_fit(package),
        _education_fit(package),
    ]
    fits.sort(key=lambda f: (_status_rank(f["status"]), f["fitScore"]), reverse=True)

    primary = next((f for f in fits if f["status"] != STATUS_NOT_A_FIT), None)
    primary_strategy = primary["strategy"] if primary else None
    queues = [q for q in (_queue_for_fit(f) for f in fits) if q]

    return {
        "strategyIntelligence": {
            "version": STRATEGY_VERSION,
            "primaryStrategy": primary_strategy,
            "strategyFits": fits,
            "queues": queues,
            "verdictMode": _verdict_mode(primary_strategy),
            "userWhySelected": _why_selected(primary),
            "scoringMode": "rules_v0",
        }
    }
