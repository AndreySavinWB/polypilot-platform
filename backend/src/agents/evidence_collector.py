"""Evidence Collector — PIE v1.0d.

Builds a minimal evidence layer from data already available on the event.
No external APIs. No invented news. Honest empty/partial status.

Only internal sources are used in v0:
  - market    : derived from marketSnapshot + marketIntelligence
  - official  : derived from sourceUrl + decisionMaker + resolutionCriteria

Real external sources (news / social / trends) stay empty until their phase.
collectionStatus reflects this honestly:
  "empty"   — no items at all
  "partial" — only internal items (no real external sources)
  "ok"      — at least one real external source (unreachable in v0)
"""

from __future__ import annotations

ITEM_TYPES = ("news", "official", "social", "trends", "market")

EXTERNAL_TYPES = {"news", "social", "trends"}


def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _market_item(event: dict, market_snapshot: dict, market_intelligence: dict) -> dict:
    """Internal evidence: the market itself as a signal."""
    prob = _to_float(market_snapshot.get("marketProb"))
    vol_signal = market_intelligence.get("volumeSignal", "unknown")
    anomaly = market_intelligence.get("volumeAnomaly", "none")
    direction = market_intelligence.get("moneyDirection", "unknown")
    mi_conf = _to_float(market_intelligence.get("confidence"))

    if prob is not None:
        prob_txt = f"{prob * 100:.0f}%"
    else:
        prob_txt = "неизвестна"

    summary = (
        f"Рынок оценивает вероятность в {prob_txt}, "
        f"сигнал объёма: {vol_signal}, аномалия: {anomaly}"
    )

    # supportsOutcome follows the money direction
    if direction in ("yes", "no", "neutral"):
        supports = direction
    else:
        supports = "unknown"

    # confidence inherits MI confidence, but if prob is missing → drop
    if prob is None:
        confidence = 0.1
    elif mi_conf is not None:
        confidence = round(mi_conf, 2)
    else:
        confidence = 0.2

    return {
        "type": "market",
        "title": "Рыночный сигнал Polymarket",
        "summary": summary,
        "source": "Polymarket",
        "url": event.get("sourceUrl"),
        "publishedAt": None,
        "freshnessHours": None,
        "supportsOutcome": supports,
        "confidence": confidence,
    }


def _official_item(event: dict, normalized_event: dict) -> dict | None:
    """Internal evidence: resolution source (decisionMaker + criteria)."""
    source_url = event.get("sourceUrl")
    if not source_url:
        return None

    decision_maker = normalized_event.get("decisionMaker") or "Polymarket / UMA"
    criteria = (normalized_event.get("resolutionCriteria") or "").strip()
    if criteria:
        summary = criteria[:200]
    else:
        summary = f"Резолв события определяет: {decision_maker}"

    return {
        "type": "official",
        "title": f"Источник резолва: {decision_maker}",
        "summary": summary,
        "source": decision_maker,
        "url": source_url,
        "publishedAt": None,
        "freshnessHours": None,
        "supportsOutcome": "unknown",
        "confidence": 0.3,
    }


def _build_counts(items: list[dict]) -> dict:
    counts = {"total": len(items)}
    for t in ITEM_TYPES:
        counts[t] = sum(1 for it in items if it.get("type") == t)
    return counts


def _collection_status(items: list[dict]) -> str:
    if not items:
        return "empty"
    has_external = any(it.get("type") in EXTERNAL_TYPES for it in items)
    return "ok" if has_external else "partial"


def collect_evidence(
    event: dict,
    normalized_event: dict,
    event_classification: dict | None = None,
    market_intelligence: dict | None = None,
) -> dict:
    """
    PIE step 4: collect minimal internal evidence items.

    Returns {"evidence": {...}} per output contract.
    """
    normalized_event = normalized_event or {}
    market_intelligence = market_intelligence or {}
    market_snapshot = normalized_event.get("marketSnapshot") or {}

    items: list[dict] = []

    # Internal item 1 — market signal (created whenever a snapshot exists)
    if market_snapshot:
        items.append(_market_item(event, market_snapshot, market_intelligence))

    # Internal item 2 — official resolution source (only if sourceUrl exists)
    official = _official_item(event, normalized_event)
    if official:
        items.append(official)

    return {
        "evidence": {
            "items": items,
            "counts": _build_counts(items),
            "collectionStatus": _collection_status(items),
            "scoringMode": "rules_v0",
        }
    }
