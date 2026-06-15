"""Probability Intelligence Engine — orchestrator.

PIE v1.0g: Priority → Event Normalizer → Event Type Classifier → Market Intelligence
           → Market Structure → Evidence Collector → Risk (draft) → Probability
           → Strategy Router → Strategy Verdict.
Output contract: POLYPILOT_STATE.md §Следующий шаг.

Blocks not in v1.0g scope (null):
  contradictionMap, analogs, generic verdict.
Risk block remains draft — not part of accepted scope per CEO.
"""

from __future__ import annotations

from src.agents.classifier import classify_event
from src.agents.evidence_collector import collect_evidence
from src.agents.market_intelligence import assess_market_intelligence
from src.agents.market_structure import analyze_market_structure
from src.agents.normalizer import normalize_event_pie
from src.agents.probability import calculate_probability
from src.agents.event_ranking import score_event
from src.agents.risk import assess_risk_v1_0a
from src.agents.strategy import route_strategy
from src.agents.strategy_verdict import build_strategy_verdict
from src.services.llm import has_llm_key

PIE_VERSION = "pie_v1_0g"


def _slim_priority(priority: dict) -> dict | None:
    if not priority:
        return None
    slim = {
        "agent": priority.get("agent", "Priority Agent"),
        "score": priority.get("score"),
        "decision": priority.get("decision"),
        "reason": priority.get("reason"),
        "gates": priority.get("hardGates") or {},
        "scoringMode": priority.get("scoringMode"),
        "rank": priority.get("rank"),
    }
    if priority.get("simpleCategory"):
        slim["simpleCategory"] = priority.get("simpleCategory")
        slim["categoryTier"] = priority.get("categoryTier")
        slim["categoryLabel"] = priority.get("categoryLabel")
    return slim


def _future_blocks() -> dict:
    return {
        "contradictionMap": [],
        "analogs": [],
        "probability": None,
        "marketStructure": None,
        "strategyIntelligence": None,
        "strategyVerdict": None,
        "verdict": None,
        "publishedAt": None,
    }


def run_pie(event: dict, priority_result: dict | None = None) -> dict:
    """Run PIE pipeline v1.0g. Returns pipelinePackage per output contract."""
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
        package["marketStructure"] = None
        package["evidence"] = None
        package["probability"] = None
        package["strategyVerdict"] = None
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

    # Step 4 — Market Structure Analyzer
    ms = analyze_market_structure(
        normalized_event,
        package["marketIntelligence"],
        package["eventClassification"],
    )
    package["marketStructure"] = ms["marketStructure"]

    # Step 5 — Evidence Collector
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

    # Step 6 — Probability Engine
    probability = calculate_probability(package)
    package["probability"] = probability["probability"]

    # Step 7 — Strategy Intelligence Layer
    strategy = route_strategy(package)
    package["strategyIntelligence"] = strategy["strategyIntelligence"]

    # Step 8 — Strategy Verdict
    strategy_verdict = build_strategy_verdict(package)
    package["strategyVerdict"] = strategy_verdict["strategyVerdict"]

    flags = normalized_event.get("flags") or []
    if "resolution_unclear" in flags:
        package["pipelineStatus"] = "branch_resolution_unclear"
    else:
        package["pipelineStatus"] = "v1_0g_complete"

    return package
