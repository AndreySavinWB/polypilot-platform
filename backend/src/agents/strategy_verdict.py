"""Strategy Verdict — PIE v1.0g.

Human-readable but rules-only summary for the selected Strategy Layer setup.
No trading advice, no buy/sell instructions.
"""

from __future__ import annotations


def _fmt_pct(value) -> str:
    if value is None:
        return "unknown"
    return f"{float(value) * 100:.0f}%"


def _fmt_edge(value) -> str:
    if value is None:
        return "unknown"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}pp"


def _top_fit(strategy: dict, primary: str | None) -> dict:
    for fit in strategy.get("strategyFits") or []:
        if fit.get("strategy") == primary:
            return fit
    return {}


def _summary(primary: str | None, fit: dict, probability: dict, market_structure: dict) -> str:
    edge = _fmt_edge(probability.get("edgePp"))
    reliability = market_structure.get("priceReliability") or "unknown"

    if primary == "whale_copy":
        return (
            f"Setup похож на Whale Copy candidate: {fit.get('reason')}. "
            f"Надёжность цены: {reliability}, edge PP: {edge}."
        )
    if primary == "news_lag":
        return (
            f"Setup похож на News Lag watchlist: {fit.get('reason')}. "
            f"Нужно подтвердить внешний catalyst; edge PP: {edge}."
        )
    if primary == "education":
        return (
            f"Событие подходит как учебный кейс: {fit.get('reason')}. "
            f"Можно объяснить рынок, резолв и ограничения данных."
        )
    return "Сильный торговый setup не найден; событие требует ручной проверки."


def build_strategy_verdict(package: dict) -> dict:
    strategy = package.get("strategyIntelligence") or {}
    probability = package.get("probability") or {}
    market_structure = package.get("marketStructure") or {}
    risk = package.get("risk") or {}

    primary = strategy.get("primaryStrategy")
    fit = _top_fit(strategy, primary)
    required_checks = fit.get("requiredChecks") or []
    invalidation = fit.get("invalidation") or []

    return {
        "strategyVerdict": {
            "primaryStrategy": primary,
            "mode": strategy.get("verdictMode") or "research",
            "summary": _summary(primary, fit, probability, market_structure),
            "marketProbText": _fmt_pct(probability.get("marketProb")),
            "ppProbText": _fmt_pct(probability.get("ppProb")),
            "edgeText": _fmt_edge(probability.get("edgePp")),
            "confidence": probability.get("confidence"),
            "riskLevel": risk.get("riskLevel"),
            "requiredChecks": required_checks,
            "invalidation": invalidation,
            "disclaimer": "Аналитика PolyPilot не является финансовым советом и не обещает прибыль.",
            "scoringMode": "rules_v0",
        }
    }
