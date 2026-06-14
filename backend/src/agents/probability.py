"""Probability Engine — PIE v1.0g.

Minimal, reproducible PP probability. It intentionally uses only structured
signals already present in the package. Missing external components are flagged
instead of being hallucinated.
"""

from __future__ import annotations


def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float, low: float = 0.02, high: float = 0.98) -> float:
    return max(low, min(high, value))


def _snapshot(package: dict) -> dict:
    return ((package.get("normalizedEvent") or {}).get("marketSnapshot") or {})


def _whale_adjustment(mi: dict, ms: dict) -> tuple[float, dict]:
    signal = mi.get("whaleSignal") or "none"
    confidence = _to_float(mi.get("confidence")) or 0.0
    manipulation = ms.get("manipulationRisk") or "unknown"

    raw = 0.0
    if signal == "accumulation_yes":
        raw = 0.07
    elif signal == "accumulation_no":
        raw = -0.07

    quality_mult = min(1.0, max(0.35, confidence * 1.6))
    if manipulation == "medium":
        quality_mult *= 0.65
    elif manipulation == "high":
        quality_mult *= 0.25

    value = raw * quality_mult
    return value, {
        "signal": signal,
        "rawAdjustment": round(raw, 4),
        "qualityMult": round(quality_mult, 2),
        "value": round(value, 4),
    }


def _evidence_adjustment(evidence: dict) -> tuple[float, dict]:
    items = evidence.get("items") or []
    counts = evidence.get("counts") or {}
    if not items:
        return 0.0, {
            "value": 0.0,
            "status": "missing",
            "reason": "no evidence items",
        }

    total_weight = 0.0
    weighted = 0.0
    for item in items:
        side = item.get("supportsOutcome")
        confidence = _to_float(item.get("confidence")) or 0.0
        if side == "yes":
            signal = 1.0
        elif side == "no":
            signal = -1.0
        else:
            signal = 0.0
        weighted += signal * confidence
        total_weight += confidence

    directional = (weighted / total_weight) if total_weight else 0.0
    # Internal-only evidence should move probability only slightly.
    has_external = any((counts.get(t) or 0) > 0 for t in ("news", "social", "trends"))
    cap = 0.08 if has_external else 0.03
    value = directional * cap
    return value, {
        "value": round(value, 4),
        "directionalScore": round(directional, 3),
        "hasExternalEvidence": has_external,
        "items": len(items),
    }


def _structure_multiplier(ms: dict) -> float:
    reliability = ms.get("priceReliability") or "unknown"
    manipulation = ms.get("manipulationRisk") or "unknown"

    if reliability == "high":
        mult = 1.0
    elif reliability == "moderate":
        mult = 0.75
    else:
        mult = 0.45

    if manipulation == "medium":
        mult *= 0.85
    elif manipulation == "high":
        mult *= 0.55
    return round(mult, 2)


def _confidence(package: dict, components: dict) -> float:
    snap = _snapshot(package)
    mi = package.get("marketIntelligence") or {}
    ms = package.get("marketStructure") or {}
    ev = package.get("evidence") or {}
    risk = package.get("risk") or {}

    score = 0.0
    if snap.get("marketProb") is not None:
        score += 0.22
    if ms.get("priceReliability") == "high":
        score += 0.18
    elif ms.get("priceReliability") == "moderate":
        score += 0.10
    if mi.get("confidence") is not None:
        score += min(0.16, (_to_float(mi.get("confidence")) or 0.0) * 0.32)
    if (ev.get("counts") or {}).get("official", 0):
        score += 0.08
    if any((ev.get("counts") or {}).get(t, 0) for t in ("news", "social", "trends")):
        score += 0.18
    if risk.get("riskLevel") == "low":
        score += 0.12
    elif risk.get("riskLevel") == "medium":
        score += 0.06

    missing_penalty = 0.04 * len(components.get("missingComponents") or [])
    return round(max(0.0, min(0.85, score - missing_penalty)), 2)


def calculate_probability(package: dict) -> dict:
    """Calculate PP probability from the current PIE package."""
    snap = _snapshot(package)
    mi = package.get("marketIntelligence") or {}
    ms = package.get("marketStructure") or {}
    ev = package.get("evidence") or {}

    market_prob = _to_float(snap.get("marketProb"))
    missing: list[str] = []

    if market_prob is None:
        return {
            "probability": {
                "marketProb": None,
                "ppProb": None,
                "edgePp": None,
                "confidence": 0.0,
                "components": {"missingComponents": ["market_base"]},
                "status": "insufficient_data",
                "scoringMode": "rules_v0",
            }
        }

    structure_mult = _structure_multiplier(ms)
    whale_adj, whale_component = _whale_adjustment(mi, ms)
    evidence_adj, evidence_component = _evidence_adjustment(ev)

    if mi.get("whaleSignal") in (None, "unknown", "none"):
        missing.append("real_whale_wallets")
    counts = ev.get("counts") or {}
    if not any(counts.get(t, 0) for t in ("news", "social", "trends")):
        missing.append("external_evidence")
    missing.extend(["historical_analogs", "contradiction_map"])

    market_component = (market_prob - 0.5) * structure_mult
    # Work around 0.5 center: market remains anchor; adjustments move it.
    pp_prob = market_prob + whale_adj + evidence_adj
    pp_prob = round(_clamp(pp_prob), 4)

    components = {
        "marketBase": {
            "value": market_prob,
            "structureMult": structure_mult,
            "centeredValue": round(market_component, 4),
        },
        "whaleSignal": whale_component,
        "evidenceSignal": evidence_component,
        "missingComponents": missing,
    }

    confidence = _confidence(package, components)
    edge = round((pp_prob - market_prob) * 100, 1)

    return {
        "probability": {
            "marketProb": market_prob,
            "ppProb": pp_prob,
            "edgePp": edge,
            "confidence": confidence,
            "components": components,
            "status": "preliminary" if missing else "ok",
            "scoringMode": "rules_v0",
        }
    }
