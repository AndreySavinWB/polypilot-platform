"""Smoke test PIE v1.0g - normalizedEvent + MI + marketStructure + evidence + probability + strategy.

Run:
    .runtime\\python.exe scripts\\test_pie.py

Reads data/test_events.json (no internet / API needed).
Prints summary table + full JSON of first accepted event.
Exits with code 1 if any contract field is missing or has a wrong scale.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.agents.pie import run_pie

# ---------------------------------------------------------------------------
# Contract definition
# ---------------------------------------------------------------------------

REQUIRED_NORMALIZED = {
    "titleRu", "resolutionCriteria", "horizonDays",
    "decisionMaker", "normalizationStatus", "marketSnapshot",
}
REQUIRED_SNAPSHOT = {"marketProb", "volume", "liquidity"}
REQUIRED_CLASSIFICATION = {
    "eventType", "subType", "classifierConfidence", "analysisProfile",
}
REQUIRED_MI = {
    "moneyDirection", "volumeSignal", "volumeAnomaly",
    "whaleSignal", "confidence", "anomalies", "scoringMode",
}
VALID_MONEY_DIR  = {"yes", "no", "neutral", "unknown"}
VALID_VOL_SIGNAL = {"rising", "falling", "flat", "unknown"}
VALID_VOL_ANOM   = {"none", "moderate", "high"}
VALID_WHALE      = {"accumulation_yes", "accumulation_no", "none", "unknown"}

REQUIRED_MARKET_STRUCTURE = {
    "marketHealthScore", "liquidityTier", "spreadRisk", "walletConcentration",
    "whaleDominance", "manipulationRisk", "crowdParticipation", "priceReliability",
    "marketReliability", "structureSummary", "flags", "sourcesUsed", "scoringMode",
}
VALID_LIQ_TIER = {"low", "medium", "high", "unknown"}
VALID_SPREAD_RISK = {"low", "medium", "high", "unknown"}
VALID_MANIP_RISK = {"low", "medium", "high"}
VALID_CROWD = {"low", "moderate", "high"}
VALID_PRICE_REL = {"low", "moderate", "high"}

REQUIRED_EVIDENCE = {"items", "counts", "collectionStatus", "scoringMode"}
REQUIRED_EV_ITEM  = {
    "type", "title", "summary", "source", "url",
    "publishedAt", "freshnessHours", "supportsOutcome", "confidence",
}
REQUIRED_EV_COUNTS = {"total", "official", "news", "social", "trends", "market"}
VALID_EV_TYPE      = {"news", "official", "social", "trends", "market"}
VALID_EV_SUPPORTS  = {"yes", "no", "neutral", "unknown"}
VALID_EV_STATUS    = {"empty", "partial", "ok"}

REQUIRED_STRATEGY = {
    "version", "primaryStrategy", "strategyFits", "queues",
    "verdictMode", "userWhySelected", "scoringMode",
}
REQUIRED_STRATEGY_FIT = {
    "strategy", "fitScore", "status", "reason", "requiredChecks", "invalidation",
}
VALID_STRATEGIES = {"whale_copy", "news_lag", "education"}
VALID_STRATEGY_STATUS = {"candidate", "watchlist", "not_a_fit"}

REQUIRED_PROBABILITY = {
    "marketProb", "ppProb", "edgePp", "confidence",
    "components", "status", "scoringMode",
}
VALID_PROB_STATUS = {"ok", "preliminary", "insufficient_data"}

REQUIRED_STRATEGY_VERDICT = {
    "primaryStrategy", "mode", "summary", "marketProbText", "ppProbText",
    "edgeText", "confidence", "riskLevel", "requiredChecks", "invalidation",
    "disclaimer", "scoringMode",
}


def _check_contract(package: dict) -> list[str]:
    errors: list[str] = []
    status = package.get("pipelineStatus", "")

    if status == "stopped_priority":
        return []  # rejected events: nothing to validate

    # normalizedEvent
    ne = package.get("normalizedEvent")
    if not ne:
        errors.append("MISSING: normalizedEvent")
        return errors
    for f in REQUIRED_NORMALIZED:
        if f not in ne:
            errors.append(f"MISSING in normalizedEvent: {f}")

    snap = ne.get("marketSnapshot") or {}
    for f in REQUIRED_SNAPSHOT:
        if f not in snap:
            errors.append(f"MISSING in marketSnapshot: {f}")
    prob = snap.get("marketProb")
    if prob is not None and not (0.0 <= prob <= 1.0):
        errors.append(f"SCALE ERROR: marketProb={prob} must be 0.0-1.0")

    # eventClassification
    ec = package.get("eventClassification")
    if not ec:
        errors.append("MISSING: eventClassification")
    else:
        for f in REQUIRED_CLASSIFICATION:
            if f not in ec:
                errors.append(f"MISSING in eventClassification: {f}")

    # marketIntelligence
    mi = package.get("marketIntelligence")
    if mi is None:
        errors.append("MISSING: marketIntelligence")
    else:
        for f in REQUIRED_MI:
            if f not in mi:
                errors.append(f"MISSING in marketIntelligence: {f}")
        if mi.get("moneyDirection") not in VALID_MONEY_DIR:
            errors.append(f"INVALID moneyDirection: {mi.get('moneyDirection')}")
        if mi.get("volumeSignal") not in VALID_VOL_SIGNAL:
            errors.append(f"INVALID volumeSignal: {mi.get('volumeSignal')}")
        if mi.get("volumeAnomaly") not in VALID_VOL_ANOM:
            errors.append(f"INVALID volumeAnomaly: {mi.get('volumeAnomaly')}")
        if mi.get("whaleSignal") not in VALID_WHALE:
            errors.append(f"INVALID whaleSignal: {mi.get('whaleSignal')}")
        conf = mi.get("confidence")
        if conf is not None and not (0.0 <= conf <= 1.0):
            errors.append(f"SCALE ERROR: MI confidence={conf} must be 0.0-1.0")

    # evidence
    ev = package.get("evidence")
    if ev is None:
        errors.append("MISSING: evidence")
    else:
        for f in REQUIRED_EVIDENCE:
            if f not in ev:
                errors.append(f"MISSING in evidence: {f}")
        if ev.get("collectionStatus") not in VALID_EV_STATUS:
            errors.append(f"INVALID collectionStatus: {ev.get('collectionStatus')}")
        counts = ev.get("counts") or {}
        for f in REQUIRED_EV_COUNTS:
            if f not in counts:
                errors.append(f"MISSING in evidence.counts: {f}")
        items = ev.get("items")
        if not isinstance(items, list):
            errors.append("evidence.items must be a list")
        else:
            if counts.get("total") != len(items):
                errors.append(
                    f"COUNT MISMATCH: counts.total={counts.get('total')} != len(items)={len(items)}"
                )
            for idx, it in enumerate(items):
                for f in REQUIRED_EV_ITEM:
                    if f not in it:
                        errors.append(f"MISSING in evidence.items[{idx}]: {f}")
                if it.get("type") not in VALID_EV_TYPE:
                    errors.append(f"INVALID evidence.items[{idx}].type: {it.get('type')}")
                if it.get("supportsOutcome") not in VALID_EV_SUPPORTS:
                    errors.append(
                        f"INVALID evidence.items[{idx}].supportsOutcome: {it.get('supportsOutcome')}"
                    )
                ic = it.get("confidence")
                if ic is not None and not (0.0 <= ic <= 1.0):
                    errors.append(f"SCALE ERROR: evidence.items[{idx}].confidence={ic} must be 0.0-1.0")

    # marketStructure
    ms = package.get("marketStructure")
    if ms is None:
        errors.append("MISSING: marketStructure")
    else:
        for f in REQUIRED_MARKET_STRUCTURE:
            if f not in ms:
                errors.append(f"MISSING in marketStructure: {f}")
        health = ms.get("marketHealthScore")
        if health is not None and not (0 <= health <= 100):
            errors.append(f"SCALE ERROR: marketHealthScore={health} must be 0-100")
        rel = ms.get("marketReliability")
        if rel is not None and not (0.0 <= rel <= 1.0):
            errors.append(f"SCALE ERROR: marketReliability={rel} must be 0.0-1.0")
        if ms.get("liquidityTier") not in VALID_LIQ_TIER:
            errors.append(f"INVALID liquidityTier: {ms.get('liquidityTier')}")
        if ms.get("spreadRisk") not in VALID_SPREAD_RISK:
            errors.append(f"INVALID spreadRisk: {ms.get('spreadRisk')}")
        if ms.get("manipulationRisk") not in VALID_MANIP_RISK:
            errors.append(f"INVALID manipulationRisk: {ms.get('manipulationRisk')}")
        if ms.get("crowdParticipation") not in VALID_CROWD:
            errors.append(f"INVALID crowdParticipation: {ms.get('crowdParticipation')}")
        if ms.get("priceReliability") not in VALID_PRICE_REL:
            errors.append(f"INVALID priceReliability: {ms.get('priceReliability')}")
        if not isinstance(ms.get("flags"), list):
            errors.append("marketStructure.flags must be a list")
        if not isinstance(ms.get("sourcesUsed"), list):
            errors.append("marketStructure.sourcesUsed must be a list")

    # pipelineStatus
    if "pipelineStatus" not in package:
        errors.append("MISSING: pipelineStatus")

    # strategyIntelligence
    si = package.get("strategyIntelligence")
    if si is None:
        errors.append("MISSING: strategyIntelligence")
    else:
        for f in REQUIRED_STRATEGY:
            if f not in si:
                errors.append(f"MISSING in strategyIntelligence: {f}")
        primary = si.get("primaryStrategy")
        if primary is not None and primary not in VALID_STRATEGIES:
            errors.append(f"INVALID primaryStrategy: {primary}")
        if si.get("scoringMode") != "rules_v0":
            errors.append(f"INVALID strategy scoringMode: {si.get('scoringMode')}")
        if not isinstance(si.get("queues"), list):
            errors.append("strategyIntelligence.queues must be a list")
        fits = si.get("strategyFits")
        if not isinstance(fits, list) or not fits:
            errors.append("strategyIntelligence.strategyFits must be a non-empty list")
        else:
            for idx, fit in enumerate(fits):
                for f in REQUIRED_STRATEGY_FIT:
                    if f not in fit:
                        errors.append(f"MISSING in strategyFits[{idx}]: {f}")
                if fit.get("strategy") not in VALID_STRATEGIES:
                    errors.append(f"INVALID strategyFits[{idx}].strategy: {fit.get('strategy')}")
                if fit.get("status") not in VALID_STRATEGY_STATUS:
                    errors.append(f"INVALID strategyFits[{idx}].status: {fit.get('status')}")
                fs = fit.get("fitScore")
                if fs is not None and not (0 <= fs <= 100):
                    errors.append(f"SCALE ERROR: strategyFits[{idx}].fitScore={fs} must be 0-100")

    # probability
    prob = package.get("probability")
    if prob is None:
        errors.append("MISSING: probability")
    else:
        for f in REQUIRED_PROBABILITY:
            if f not in prob:
                errors.append(f"MISSING in probability: {f}")
        if prob.get("status") not in VALID_PROB_STATUS:
            errors.append(f"INVALID probability.status: {prob.get('status')}")
        if prob.get("scoringMode") != "rules_v0":
            errors.append(f"INVALID probability.scoringMode: {prob.get('scoringMode')}")
        for f in ("marketProb", "ppProb", "confidence"):
            value = prob.get(f)
            if value is not None and not (0.0 <= value <= 1.0):
                errors.append(f"SCALE ERROR: probability.{f}={value} must be 0.0-1.0")
        edge = prob.get("edgePp")
        if edge is not None and not (-100 <= edge <= 100):
            errors.append(f"SCALE ERROR: probability.edgePp={edge} must be -100..100")
        if not isinstance(prob.get("components"), dict):
            errors.append("probability.components must be an object")

    # strategyVerdict
    sv = package.get("strategyVerdict")
    if sv is None:
        errors.append("MISSING: strategyVerdict")
    else:
        for f in REQUIRED_STRATEGY_VERDICT:
            if f not in sv:
                errors.append(f"MISSING in strategyVerdict: {f}")
        if sv.get("primaryStrategy") is not None and sv.get("primaryStrategy") not in VALID_STRATEGIES:
            errors.append(f"INVALID strategyVerdict.primaryStrategy: {sv.get('primaryStrategy')}")
        if sv.get("scoringMode") != "rules_v0":
            errors.append(f"INVALID strategyVerdict.scoringMode: {sv.get('scoringMode')}")
        if not isinstance(sv.get("requiredChecks"), list):
            errors.append("strategyVerdict.requiredChecks must be a list")
        if not isinstance(sv.get("invalidation"), list):
            errors.append("strategyVerdict.invalidation must be a list")

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    sample_path = os.path.join(ROOT, "data", "test_events.json")
    if not os.path.exists(sample_path):
        print("ERROR: data/test_events.json not found — run harvest first.")
        sys.exit(1)

    with open(sample_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    items = data.get("items") or []
    if not items:
        print("ERROR: test_events.json has no items.")
        sys.exit(1)

    all_errors: list[str] = []
    rows = []

    for item in items:
        event = item.get("event") or item
        priority = (item.get("analysis") or {}).get("priority")
        package = run_pie(event, priority_result=priority)
        errors = _check_contract(package)
        all_errors.extend(errors)

        ne   = package.get("normalizedEvent") or {}
        ec   = package.get("eventClassification") or {}
        mi   = package.get("marketIntelligence") or {}
        ms   = package.get("marketStructure") or {}
        ev   = package.get("evidence") or {}
        si   = package.get("strategyIntelligence") or {}
        pr   = package.get("probability") or {}
        snap = ne.get("marketSnapshot") or {}

        rows.append({
            "no":        item.get("testNo", "?"),
            "status":    package.get("pipelineStatus", "?"),
            "title":     (ne.get("titleRu") or event.get("title") or "")[:42],
            "normSt":    ne.get("normalizationStatus", "?"),
            "evType":    ec.get("eventType", "?"),
            "dir":       mi.get("moneyDirection", "?"),
            "volSig":    mi.get("volumeSignal", "?"),
            "anom":      mi.get("volumeAnomaly", "?"),
            "whale":     mi.get("whaleSignal", "?"),
            "miConf":    mi.get("confidence", "?"),
            "health":    ms.get("marketHealthScore", "?"),
            "priceRel":  ms.get("priceReliability", "?"),
            "evTotal":   (ev.get("counts") or {}).get("total", "?"),
            "evStatus":  ev.get("collectionStatus", "?"),
            "strategy":  si.get("primaryStrategy", "?"),
            "edge":      pr.get("edgePp", "?"),
            "pp":        pr.get("ppProb", "?"),
            "queues":    ",".join(si.get("queues") or []),
        })

    # --- Table ---
    W = 140
    print("=" * W)
    print(
        f"{'#':<3} {'normSt':<8} {'evType':<12} {'dir':<8} "
        f"{'volSig':<9} {'anom':<10} {'whale':<17} {'miConf':<7} "
        f"{'health':<6} {'rel':<8} {'edge':<7} {'pp':<6} "
        f"{'evN':<4} {'evStatus':<8} {'strategy':<12} {'queues':<24}"
    )
    print("-" * W)
    for r in rows:
        print(
            f"{r['no']:<3} {r['normSt']:<8} {r['evType']:<12} {r['dir']:<8} "
            f"{r['volSig']:<9} {r['anom']:<10} {r['whale']:<17} "
            f"{str(r['miConf']):<7} {str(r['health']):<6} {r['priceRel']:<8} "
            f"{str(r['edge']):<7} {str(r['pp']):<6} "
            f"{str(r['evTotal']):<4} {r['evStatus']:<8} "
            f"{str(r['strategy']):<12} {str(r['queues']):<24}"
        )
        print(f"    {r['title']}")
    print("=" * W)

    # --- Full JSON of first non-rejected event ---
    first = next(
        (it for it in items
         if (it.get("analysis") or {}).get("priority", {}).get("decision") != "rejected"),
        items[0],
    )
    pkg0 = run_pie(first.get("event") or first,
                   priority_result=(first.get("analysis") or {}).get("priority"))
    output = {
        "eventId":              pkg0.get("eventId"),
        "pieVersion":           pkg0.get("pieVersion"),
        "pipelineStatus":       pkg0.get("pipelineStatus"),
        "normalizedEvent":      pkg0.get("normalizedEvent"),
        "eventClassification":  pkg0.get("eventClassification"),
        "marketIntelligence":   pkg0.get("marketIntelligence"),
        "marketStructure":      pkg0.get("marketStructure"),
        "evidence":             pkg0.get("evidence"),
        "risk":                 pkg0.get("risk"),
        "probability":          pkg0.get("probability"),
        "strategyIntelligence": pkg0.get("strategyIntelligence"),
        "strategyVerdict":      pkg0.get("strategyVerdict"),
    }
    print("\n=== Full JSON (first accepted event) ===\n")
    print(json.dumps(output, ensure_ascii=False, indent=2))

    # --- Result ---
    if all_errors:
        print(f"\nFAIL: {len(all_errors)} contract violation(s):")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"\nOK: Contract passed -- {len(rows)} events checked.")


if __name__ == "__main__":
    main()
