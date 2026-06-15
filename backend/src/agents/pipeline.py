from src.agents.event_ranking import score_event
from src.services.llm import ask_llm, has_llm_key


def analyze_event(event, priority_result=None):
    """Run the first PP agent pipeline for one event.

    MVP pipeline:
    1. Priority Agent
    2. News Scout
    3. Risk Officer
    4. Verdict Agent
    """
    priority = priority_result or score_event(event, use_llm=has_llm_key())
    if has_llm_key():
        return _analyze_with_llm(event, priority)
    return _mock_analysis(event, priority)


def _analyze_with_llm(event, priority):
    system_prompt = """
You are the PolyPilot analyst pipeline for prediction markets.
Priority Agent has ALREADY scored this event — do NOT change priority scores.
Return ONLY valid JSON with EXACTLY this structure:

{
  "eventId": "string",
  "source": "polymarket_gamma",
  "newsScout": {
    "agent": "News Scout",
    "summary": "string",
    "facts": ["string"],
    "missing": ["string"]
  },
  "riskOfficer": {
    "agent": "Risk Officer",
    "riskLevel": "low|medium|high",
    "flags": ["string"]
  },
  "verdict": {
    "agent": "Verdict Agent",
    "ppVerdict": "string",
    "confidence": 0-100,
    "edgeScore": null,
    "status": "research_required|ready|rejected"
  },
  "ui": {
    "closedCardBadge": "Accepted|Watchlist|Rejected",
    "warRoomAgents": ["Priority Agent", "News Scout", "Risk Officer", "Verdict Agent"],
    "disclaimer": "Analysis only. Not financial advice."
  }
}

Rules:
- No buy/sell advice.
- Separate facts from assumptions.
- If external news is unavailable, list gaps in newsScout.missing.
- edgeScore must be null unless you have strong mispricing evidence.
- ALL user-facing text (reason, summary, facts, missing, flags, ppVerdict) MUST be in Russian.
- ppVerdict must be a full sentence in Russian, not a single word like Yes/No.
"""
    result = ask_llm(system_prompt, {"event": event, "priority": priority})
    result.setdefault("eventId", event.get("id"))
    result.setdefault("source", event.get("source") or "polymarket_gamma")
    result["priority"] = priority
    return result


def _mock_analysis(event, priority):
    title = event.get("title") or "Unknown market"
    volume = _to_number(event.get("volume") or event.get("volume24hr"))
    liquidity = _to_number(event.get("liquidity"))
    markets_count = event.get("marketsCount") or len(event.get("markets") or [])

    risk_level = "medium"
    risk_flags = []
    if liquidity and liquidity < 10000:
        risk_level = "high"
        risk_flags.append("Low liquidity can distort probability and execution quality.")
    if not event.get("endDate"):
        risk_flags.append("Missing end date or resolution timing.")
    if not event.get("description"):
        risk_flags.append("Weak public description; resolution rules need manual review.")
    if not risk_flags:
        risk_flags.append("No critical structural red flags in the available metadata.")

    return {
        "eventId": event.get("id"),
        "source": event.get("source"),
        "priority": priority,
        "newsScout": {
            "agent": "News Scout",
            "summary": "Real news collection is not connected yet; this stage uses Polymarket metadata only.",
            "facts": [
                f"Market/event: {title}",
                f"Markets inside event: {markets_count}",
                f"Source URL: {event.get('sourceUrl')}",
            ],
            "missing": ["External news sources", "social narrative", "latest probability change"],
        },
        "riskOfficer": {
            "agent": "Risk Officer",
            "riskLevel": risk_level,
            "flags": risk_flags,
        },
        "verdict": {
            "agent": "Verdict Agent",
            "ppVerdict": "Track this event, but do not show a strong Edge Score until external sources and price history are connected.",
            "confidence": 42,
            "edgeScore": None,
            "status": "research_required",
        },
        "ui": {
            "closedCardBadge": priority.get("decision", "watchlist").title(),
            "warRoomAgents": ["Priority Agent", "News Scout", "Risk Officer", "Verdict Agent"],
            "disclaimer": "Prototype analysis. Not financial advice.",
        },
    }


def _to_number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0
