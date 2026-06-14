"""Market Structure Analyzer — PIE v1.0f.

Rules-only market health layer. It answers whether the market price is a
reasonably reliable signal before Strategy Router / Probability use it.

No wallet concentration is invented in v0. Wallet-specific fields stay
"unknown" until a real wallet/trades source is connected.
"""

from __future__ import annotations


def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def _liquidity_tier(liquidity: float | None) -> str:
    if liquidity is None:
        return "unknown"
    if liquidity >= 250_000:
        return "high"
    if liquidity >= 25_000:
        return "medium"
    return "low"


def _spread_risk(spread: float | None) -> str:
    if spread is None:
        return "unknown"
    if spread >= 0.05:
        return "high"
    if spread >= 0.02:
        return "medium"
    return "low"


def _crowd_participation(volume: float, volume_24h: float | None, liquidity: float | None) -> str:
    if volume >= 1_000_000 and (liquidity or 0) >= 100_000:
        return "high"
    if volume >= 100_000 and (liquidity or 0) >= 25_000:
        return "moderate"
    if volume_24h is not None and volume_24h >= 25_000 and (liquidity or 0) >= 10_000:
        return "moderate"
    return "low"


def _price_reliability(score: int, flags: list[str]) -> str:
    if score >= 75 and "manipulation_suspect" not in flags and "price_unreliable" not in flags:
        return "high"
    if score >= 45:
        return "moderate"
    return "low"


def _manipulation_risk(flags: list[str], volume_anomaly: str, whale_signal: str) -> str:
    if "price_unreliable" in flags:
        return "high"
    if "thin_market_whale_combo" in flags:
        return "high"
    if whale_signal in ("accumulation_yes", "accumulation_no") and volume_anomaly == "high":
        return "medium"
    if volume_anomaly == "high":
        return "medium"
    return "low"


def _summary(score: int, price_reliability: str, manipulation_risk: str, flags: list[str]) -> str:
    if price_reliability == "high":
        return "Рынок выглядит достаточно здоровым: ликвидность и объём позволяют использовать цену как рабочий сигнал."
    if price_reliability == "moderate":
        return "Рынок умеренно надёжен: цену можно учитывать, но нужны проверки структуры и риска."
    if manipulation_risk == "high":
        return "Рынок структурно опасен: цена может быть ненадёжной из-за тонкой ликвидности или аномального движения."
    if flags:
        return "Рынок слабый: есть структурные флаги, поэтому цену нельзя считать сильным consensus-сигналом."
    return "Надёжность рыночной цены низкая по доступным метаданным."


def analyze_market_structure(
    normalized_event: dict,
    market_intelligence: dict | None = None,
    event_classification: dict | None = None,
) -> dict:
    """PIE step: derive market health/reliability from current structured data."""
    snap = (normalized_event or {}).get("marketSnapshot") or {}
    mi = market_intelligence or {}

    volume = _to_float(snap.get("volume")) or 0.0
    volume_24h = _to_float(snap.get("volume24h"))
    liquidity = _to_float(snap.get("liquidity"))
    spread = _to_float(snap.get("spread"))
    market_prob = _to_float(snap.get("marketProb"))

    volume_anomaly = mi.get("volumeAnomaly") or "none"
    whale_signal = mi.get("whaleSignal") or "none"

    flags: list[str] = []
    score = 70.0

    liq_tier = _liquidity_tier(liquidity)
    if liq_tier == "high":
        score += 12
    elif liq_tier == "medium":
        score += 3
    elif liq_tier == "low":
        score -= 28
        flags.append("thin_market")

    if volume >= 1_000_000:
        score += 8
    elif volume >= 100_000:
        score += 2
    else:
        score -= 15
        if "thin_market" not in flags:
            flags.append("thin_market")

    spread_level = _spread_risk(spread)
    if spread_level == "high":
        score -= 18
        flags.append("wide_spread")
    elif spread_level == "medium":
        score -= 8

    if volume_anomaly == "high":
        score -= 8
        flags.append("volume_spike")
    elif volume_anomaly == "moderate":
        score -= 3

    if whale_signal in ("accumulation_yes", "accumulation_no"):
        flags.append("whale_proxy_flow")
        if liq_tier == "low":
            score -= 18
            flags.append("thin_market_whale_combo")
        else:
            score -= 5

    if market_prob is not None and (market_prob <= 0.03 or market_prob >= 0.97):
        score -= 10
        flags.append("dead_price")

    health = _clamp(score)
    if health < 45 and "price_unreliable" not in flags:
        flags.append("price_unreliable")

    manipulation = _manipulation_risk(flags, volume_anomaly, whale_signal)
    crowd = _crowd_participation(volume, volume_24h, liquidity)
    reliability = _price_reliability(health, flags)

    return {
        "marketStructure": {
            "marketHealthScore": health,
            "liquidityTier": liq_tier,
            "spreadRisk": spread_level,
            "walletConcentration": "unknown",
            "whaleDominance": None,
            "manipulationRisk": manipulation,
            "crowdParticipation": crowd,
            "priceReliability": reliability,
            "marketReliability": round(health / 100, 2),
            "structureSummary": _summary(health, reliability, manipulation, flags),
            "flags": flags,
            "sourcesUsed": ["polymarket_gamma", "market_intelligence_rules"],
            "scoringMode": "rules_v0",
        }
    }
