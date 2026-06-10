"""Probability Intelligence Engine — orchestrator.

PIE v1.0d: Priority → Event Normalizer → Event Type Classifier → Market Intelligence
           → Evidence Collector → Risk (draft).
Output contract: POLYPILOT_STATE.md §Следующий шаг.

Blocks not in v1.0d scope (null):
  contradictionMap, analogs, probability, verdict.
Risk block remains draft — not part of accepted scope per CEO.
"""

from __future__ import annotations

from src.agents.classifier import classify_event
from src.agents.evidence_collector import collect_evidence
from src.agents.market_intelligence import assess_market_intelligence
from src.agents.normalizer import normalize_event_pie
from src.agents.priority import score_event
from src.agents.risk import assess_risk_v1_0a
from src.services.llm import has_llm_key

PIE_VERSION = "pie_v1_0d"


def _slim_priority(priority: dict) -> dict | None:
    if not priority:
        return None
    return {
        "agent": priority.get("agent", "Priority Agent"),
        "score": priority.get("score"),
        "decision": priority.get("decision"),
        "reason": priority.get("reason"),
        "gates": priority.get("hardGates") or {},
        "scoringMode": priority.get("scoringMode"),
        "rank": priority.get("rank"),
    }


def _future_blocks() -> dict:
    return {
        "contradictionMap": [],
        "analogs": [],
        "probability": None,
        "verdict": None,
        "publishedAt": None,
    }


def run_pie(event: dict, priority_result: dict | None = None) -> dict:
    """Run PIE pipeline v1.0c. Returns pipelinePackage per output contract."""
    priority = priority_result or score_event(event, use_llm=has_llm_key())

    package: dict = {
        "eventId": str(event.get("id") or ""),
        "source": event.get("source") or "polymarket_gamma",
        "pieVersion": PIE_VERSION,
        "priority": _slim_priority(priority),
        **_future_blocks(),
    }

    if priority.get("decision") == "rejected":
        package["pipelineStatus"] = "stopped_priority"
        package["normalizedEvent"] = None
        package["eventClassification"] = None
        package["marketIntelligence"] = None
        package["evidence"] = None
        package["risk"] = assess_risk_v1_0a(event, None, None, priority)
        return package

    # Step 1 — Event Normalizer
    norm = normalize_event_pie(event)
    normalized_event: dict = norm["normalizedEvent"]
    package["normalizedEvent"] = normalized_event

    # Step 2 — Event Type Classifier
    raw_question = (
        (event.get("markets") or [{}])[0].get("question")
        or event.get("title")
        or ""
    )
    package["eventClassification"] = classify_event(normalized_event, raw_question)

    # Step 3 — Market Intelligence
    mi = assess_market_intelligence(event, normalized_event)
    package["marketIntelligence"] = mi["marketIntelligence"]

    # Step 4 — Evidence Collector
    ev = collect_evidence(
        event,
        normalized_event,
        package["eventClassification"],
        package["marketIntelligence"],
    )
    package["evidence"] = ev["evidence"]

    # Risk — draft, not in accepted v1.0d scope
    market_snapshot = normalized_event.get("marketSnapshot") or {}
    package["risk"] = assess_risk_v1_0a(event, normalized_event, market_snapshot, priority)

    flags = normalized_event.get("flags") or []
    if "resolution_unclear" in flags:
        package["pipelineStatus"] = "branch_resolution_unclear"
    else:
        package["pipelineStatus"] = "v1_0d_complete"

    return package
