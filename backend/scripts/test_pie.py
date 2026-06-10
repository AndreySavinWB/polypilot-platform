"""Smoke test PIE v1.0d - normalizedEvent + eventClassification + marketIntelligence + evidence.

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

REQUIRED_EVIDENCE = {"items", "counts", "collectionStatus", "scoringMode"}
REQUIRED_EV_ITEM  = {
    "type", "title", "summary", "source", "url",
    "publishedAt", "freshnessHours", "supportsOutcome", "confidence",
}
REQUIRED_EV_COUNTS = {"total", "official", "news", "social", "trends", "market"}
VALID_EV_TYPE      = {"news", "official", "social", "trends", "market"}
VALID_EV_SUPPORTS  = {"yes", "no", "neutral", "unknown"}
VALID_EV_STATUS    = {"empty", "partial", "ok"}


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

    # pipelineStatus
    if "pipelineStatus" not in package:
        errors.append("MISSING: pipelineStatus")

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
        ev   = package.get("evidence") or {}
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
            "evTotal":   (ev.get("counts") or {}).get("total", "?"),
            "evStatus":  ev.get("collectionStatus", "?"),
        })

    # --- Table ---
    W = 140
    print("=" * W)
    print(
        f"{'#':<3} {'normSt':<8} {'evType':<12} {'dir':<8} "
        f"{'volSig':<9} {'anom':<10} {'whale':<17} {'miConf':<7} "
        f"{'evN':<4} {'evStatus':<8}"
    )
    print("-" * W)
    for r in rows:
        print(
            f"{r['no']:<3} {r['normSt']:<8} {r['evType']:<12} {r['dir']:<8} "
            f"{r['volSig']:<9} {r['anom']:<10} {r['whale']:<17} "
            f"{str(r['miConf']):<7} {str(r['evTotal']):<4} {r['evStatus']:<8}"
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
        "evidence":             pkg0.get("evidence"),
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
