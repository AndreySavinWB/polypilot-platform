"""Market Intelligence — PIE v1.0c.

Rule-based signals derived purely from Polymarket data already in marketSnapshot.
No external APIs. No whale wallets. No invented signals.

Inputs used:
  marketSnapshot.marketProb  (0.0–1.0)
  marketSnapshot.volume      (total lifetime)
  marketSnapshot.volume24h
  marketSnapshot.liquidity
  marketSnapshot.priceChange24h  (often null)
  marketSnapshot.spread

If a field is absent or zero, we return "unknown"/"none" and lower confidence.
scoringMode is always "rules_v0".
"""

from __future__ import annotations

from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
MONEY_DIR_HIGH = 0.65   # marketProb above this → "yes"
MONEY_DIR_LOW  = 0.35   # marketProb below this → "no"

ACTIVITY_RISING = 1.5   # activity_ratio above → "rising"
ACTIVITY_FLAT   = 0.5   # activity_ratio below → "flat"

ANOMALY_HIGH     = 3.0  # activity_ratio above → "high" anomaly
ANOMALY_MODERATE = 1.5  # activity_ratio above → "moderate" anomaly

LIQUIDITY_THIN = 5_000  # below → thin_market anomaly


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
        return f if f >= 0 else None
    except (TypeError, ValueError):
        return None


def _elapsed_days(event: dict) -> int:
    """Days since market startDate, minimum 1."""
    start = event.get("startDate")
    if not start:
        return 1
    try:
        start_dt = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
        delta = (datetime.now(timezone.utc) - start_dt).days
        return max(1, delta)
    except (ValueError, OverflowError):
        return 1


def _money_direction(market_prob: float | None) -> str:
    if market_prob is None:
        return "neutral"
    if market_prob > MONEY_DIR_HIGH:
        return "yes"
    if market_prob < MONEY_DIR_LOW:
        return "no"
    return "neutral"


def _activity_ratio(volume_total: float, volume_24h: float, elapsed: int) -> float | None:
    """Ratio of today's volume to average daily volume."""
    if volume_total <= 0 or volume_24h is None:
        return None
    # cap volume24h at volume_total to handle data inconsistencies
    v24 = min(volume_24h, volume_total)
    daily_avg = volume_total / elapsed
    if daily_avg <= 0:
        return None
    return v24 / daily_avg


def _volume_signal(ratio: float | None, volume_24h: float | None) -> str:
    if volume_24h is None:
        return "unknown"
    if ratio is None:
        return "unknown"
    if ratio > ACTIVITY_RISING:
        return "rising"
    if ratio < ACTIVITY_FLAT:
        return "flat"
    return "flat"   # 0.5–1.5 is normal, no strong signal


def _volume_anomaly(ratio: float | None) -> str:
    if ratio is None:
        return "none"
    if ratio > ANOMALY_HIGH:
        return "high"
    if ratio > ANOMALY_MODERATE:
        return "moderate"
    return "none"


def _whale_signal(anomaly: str, direction: str) -> str:
    """
    Placeholder: inferred from price direction + volume anomaly.
    No real wallet data — kept conservative.
    Only fires on "high" anomaly to avoid false positives.
    """
    if anomaly != "high":
        return "none"
    if direction == "yes":
        return "accumulation_yes"
    if direction == "no":
        return "accumulation_no"
    return "none"   # neutral direction + high volume → no directional signal


def _build_anomalies(
    ratio: float | None,
    volume_24h: float | None,
    volume_total: float,
    liquidity: float | None,
) -> list[dict]:
    result = []

    # Volume spike
    if ratio is not None:
        if ratio > ANOMALY_HIGH:
            result.append({
                "type": "volume_spike",
                "description": f"24h volume is {ratio:.1f}x average daily volume",
                "severity": "high",
            })
        elif ratio > ANOMALY_MODERATE:
            result.append({
                "type": "volume_spike",
                "description": f"24h volume is {ratio:.1f}x average daily volume",
                "severity": "medium",
            })

    # Volume24h exceeds total (data inconsistency)
    if volume_24h is not None and volume_total > 0 and volume_24h > volume_total:
        result.append({
            "type": "data_inconsistency",
            "description": "volume24h exceeds total volume — possible data lag",
            "severity": "medium",
        })

    # Thin market
    if liquidity is not None and 0 < liquidity < LIQUIDITY_THIN:
        result.append({
            "type": "thin_market",
            "description": f"Liquidity ${liquidity:,.0f} is very low",
            "severity": "high",
        })

    return result


def _confidence(
    market_prob: float | None,
    volume_total: float,
    volume_24h: float | None,
    liquidity: float | None,
    price_change_24h: float | None,
    has_start_date: bool,
) -> float:
    """
    Data-quality-based confidence, capped at 0.50.
    Cap reflects absence of real MI APIs (whale wallets, order book).
    """
    score = 0.0
    if market_prob is not None:
        score += 0.15
    if volume_total > 0:
        score += 0.15
    if volume_24h is not None and volume_24h >= 0:
        score += 0.20
    if liquidity is not None and liquidity > 0:
        score += 0.10
    if has_start_date:
        score += 0.05
    if price_change_24h is not None:
        score += 0.05
    # Hard cap: no real whale/order-book data
    return round(min(score, 0.50), 2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def assess_market_intelligence(event: dict, normalized_event: dict) -> dict:
    """
    PIE step 3: derive market intelligence signals from Polymarket snapshot data.

    Returns {"marketIntelligence": {...}} per output contract.
    """
    snap = (normalized_event or {}).get("marketSnapshot") or {}

    market_prob   = _to_float(snap.get("marketProb"))
    volume_total  = _to_float(snap.get("volume")) or 0.0
    volume_24h    = _to_float(snap.get("volume24h"))
    liquidity     = _to_float(snap.get("liquidity"))
    price_chg_24h = _to_float(snap.get("priceChange24h"))

    elapsed = _elapsed_days(event)
    has_start = bool(event.get("startDate"))

    ratio = _activity_ratio(volume_total, volume_24h, elapsed)

    direction = _money_direction(market_prob)
    vol_signal = _volume_signal(ratio, volume_24h)
    anomaly    = _volume_anomaly(ratio)
    whale      = _whale_signal(anomaly, direction)
    anomalies  = _build_anomalies(ratio, volume_24h, volume_total, liquidity)
    conf       = _confidence(
        market_prob, volume_total, volume_24h, liquidity,
        price_chg_24h, has_start,
    )

    return {
        "marketIntelligence": {
            "moneyDirection":  direction,
            "volumeSignal":    vol_signal,
            "volumeAnomaly":   anomaly,
            "whaleSignal":     whale,
            "confidence":      conf,
            "anomalies":       anomalies,
            "scoringMode":     "rules_v0",
        }
    }
