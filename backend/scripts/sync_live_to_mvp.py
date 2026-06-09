"""Convert test_events.json → platform/data/events-live.js"""

import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SRC = os.path.join(ROOT, "data", "test_events.json")
OUT = os.path.join(ROOT, "..", "platform", "data", "events-live.js")

from src.services.localize import (
    AGENT_NAMES_RU,
    DECISION_RU,
    RISK_LEVEL_RU,
    localize_analysis_texts,
    localize_description,
    translate_title,
    translate_verdict_token,
)


def load_env():
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


def fmt_money(value):
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return "—"
    if number >= 1_000_000_000:
        return f"${number / 1_000_000_000:.1f}B".replace(".0B", "B")
    if number >= 1_000_000:
        return f"${number / 1_000_000:.1f}M".replace(".0M", "M")
    if number >= 1_000:
        return f"${number / 1_000:.0f}K"
    return f"${number:.0f}"


def parse_prices(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if not raw:
        return None
    try:
        return int(round(float(raw[0]) * 100))
    except (TypeError, ValueError, IndexError):
        return None


def guess_category(title, tags, title_en=None):
    text = f"{title or ''} {title_en or ''}".lower()
    if any(word in text for word in ("ipo", "kraken", "bitcoin", "crypto", "крипто")):
        return "Крипто", "crypto"
    if any(word in text for word in ("election", "macron", "starmer", "nato", "ukraine", "uk ", "troops", "макрон", "стармер", "выбор", "нато", "украин")):
        return "Политика", "politics"
    if any(word in text for word in ("china", "india", "military", "clash", "китай", "инди", "конфликт")):
        return "Геополитика", "politics"
    if "news_driven" in tags:
        return "Политика", "politics"
    return "Макро", "macro"


def horizon_days(end_date):
    if not end_date:
        return "—"
    try:
        end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        delta = (end - datetime.now(timezone.utc)).days
        if delta < 0:
            return "скоро"
        return f"{delta} дней"
    except ValueError:
        return "—"


def build_agents(analysis, localized):
    priority = analysis.get("priority") or {}
    news = analysis.get("newsScout") or {}
    risk = analysis.get("riskOfficer") or {}
    verdict = analysis.get("verdict") or {}

    flags = localized.get("riskFlags") or risk.get("flags") or ["Нет критических флагов"]
    facts = localized.get("newsFacts") or news.get("facts") or []
    decision = priority.get("decision", "watchlist")
    risk_level = risk.get("riskLevel") or "medium"
    pp_verdict = localized.get("ppVerdict") or verdict.get("ppVerdict") or ""
    if len(str(pp_verdict)) < 25 or str(pp_verdict).strip().lower() in {"yes", "no", "да", "нет", "pending", "watchlist", "research_required"}:
        pp_verdict = localized.get("newsSummary") or news.get("summary") or pp_verdict

    return [
        {
            "name": AGENT_NAMES_RU["Priority Agent"],
            "role": "Приоритет PP",
            "avatar": "🎯",
            "message": localized.get("priorityReason") or priority.get("reason") or "Событие отобрано для анализа PP.",
            "verdict": DECISION_RU.get(decision, decision.upper()),
            "verdictColor": "green" if decision == "accepted" else "orange",
            "confidence": priority.get("score") or 50,
        },
        {
            "name": AGENT_NAMES_RU["News Scout"],
            "role": "Сбор фактов",
            "avatar": "📡",
            "message": localized.get("newsSummary") or news.get("summary") or (facts[0] if facts else "Сбор новостей в процессе."),
            "verdict": "ФАКТЫ",
            "verdictColor": "green",
            "confidence": 60,
        },
        {
            "name": AGENT_NAMES_RU["Risk Officer"],
            "role": "Контроль риска",
            "avatar": "🛡️",
            "message": flags[0],
            "verdict": RISK_LEVEL_RU.get(risk_level, risk_level.upper()),
            "verdictColor": {"low": "green", "medium": "orange", "high": "red"}.get(risk_level, "orange"),
            "confidence": 55,
        },
        {
            "name": AGENT_NAMES_RU["Verdict Agent"],
            "role": "Итог PP",
            "avatar": "⚡",
            "message": pp_verdict or "Требуется дополнительный анализ.",
            "verdict": "ВЕРДИКТ",
            "verdictColor": "purple",
            "confidence": verdict.get("confidence") or 50,
        },
    ]


def convert_item(item):
    event = item["event"]
    analysis = item["analysis"]
    tags = item.get("tags") or []
    markets = event.get("markets") or []
    first_market = markets[0] if markets else {}
    event_id = str(event.get("id"))
    title_ru = translate_title(event_id, event.get("title"))
    localized = localize_analysis_texts(analysis)
    category, category_tag = guess_category(title_ru, tags, event.get("title"))

    market_odds = parse_prices(first_market.get("outcomePrices"))
    confidence = (analysis.get("verdict") or {}).get("confidence") or 50
    risk_level = (analysis.get("riskOfficer") or {}).get("riskLevel") or "medium"
    priority_decision = (analysis.get("priority") or {}).get("decision")
    volume24 = float(event.get("volume24hr") or 0)
    volume_total = float(event.get("volume") or 0)

    short_verdicts = {"yes", "no", "да", "нет", "pending", "watchlist", "research_required", "ожидание", "наблюдение"}
    verdict_text = localized.get("ppVerdict") or (analysis.get("verdict") or {}).get("ppVerdict") or ""
    if len(str(verdict_text)) < 25 or str(verdict_text).strip().lower() in short_verdicts:
        verdict_text = localized.get("newsSummary") or (analysis.get("newsScout") or {}).get("summary") or "PP AI проанализировал событие. Полный разбор доступен в карточке."

    edge = None
    if market_odds is not None:
        edge = max(0, confidence - market_odds)

    summary_ru = localize_description(event.get("description"), title_ru)
    risk_tags_ru = localized.get("riskFlags") or (analysis.get("riskOfficer") or {}).get("flags") or []
    facts_ru = localized.get("newsFacts") or (analysis.get("newsScout") or {}).get("facts") or []

    return {
        "id": f"live-{event.get('id')}",
        "polymarketId": event.get("id"),
        "title": title_ru,
        "titleEn": event.get("title"),
        "category": category,
        "categoryTag": category_tag,
        "status": "open",
        "isLive": True,
        "isDemo": False,
        "source": "polymarket",
        "hot": priority_decision == "accepted" or "hot" in tags,
        "resolveDate": (event.get("endDate") or "")[:10],
        "potential": f"+{max(5, min(40, (analysis.get('priority') or {}).get('score', 50) // 3))}%",
        "horizon": horizon_days(event.get("endDate")),
        "volumeTotal": fmt_money(volume_total),
        "volume24h": fmt_money(volume24) if volume24 else "—",
        "volume24hPositive": volume24 >= 0,
        "interest": "Интерес растёт" if volume24 > 1000 else "Стабильно",
        "interestPositive": volume24 > 1000,
        "watchers": fmt_money(volume_total).replace("$", "").strip(),
        "market": "Полимаркет",
        "marketUrl": event.get("sourceUrl") or "https://polymarket.com",
        "marketOdds": market_odds if market_odds is not None else 50,
        "aiOdds": confidence,
        "edgeScore": edge if edge is not None else 0,
        "edgeDirection": "ДА",
        "riskLevel": risk_level,
        "riskTags": risk_tags_ru,
        "confidence": confidence,
        "verdict": "НАБЛЮДЕНИЕ",
        "verdictText": verdict_text,
        "summary": summary_ru,
        "warRoom": {"duration": 6, "agents": build_agents(analysis, localized)},
        "arguments": {
            "yes": facts_ru,
            "no": risk_tags_ru,
        },
        "news": [],
        "changes": [],
        "proofTrack": {
            "opened": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "ppOdds": confidence,
            "marketOddsAtOpen": market_odds or 50,
        },
    }


def main():
    load_env()
    with open(SRC, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    events = [convert_item(item) for item in payload.get("items", [])]
    js = "/** Auto-generated from backend/data/test_events.json */\n"
    js += "window.EVENTS_LIVE = "
    js += json.dumps({"events": events, "generatedAt": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False, indent=2)
    js += ";\n"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(js)

    print(f"Synced {len(events)} live events to {OUT}")


if __name__ == "__main__":
    main()
