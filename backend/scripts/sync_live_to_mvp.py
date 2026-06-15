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


def guess_category(title, tags, title_en=None, simple_category=None):
    if simple_category == "sports":
        return "Спорт", "sport"
    if simple_category == "entertainment":
        return "Кино", "cinema"
    if simple_category == "crypto_simple":
        return "Крипто", "crypto"
    if simple_category == "tech_oneshot":
        return "Tech", "tech"
    if simple_category == "games":
        return "Игры", "sport"
    if "crypto_simple" in tags:
        return "Крипто", "crypto"
    if "sports" in tags or "sport" in tags:
        return "Спорт", "sport"
    if "entertainment" in tags:
        return "Кино", "cinema"
    text = f"{title or ''} {title_en or ''}".lower()
    if any(word in text for word in ("swift", "taylor", "pregnant", "marriage", "album", "oscar", "grammy")):
        return "Кино", "cinema"
    if any(word in text for word in ("tesla", "robotaxi", "iphone", "openai")):
        return "Tech", "tech"
    if any(word in text for word in ("ipo", "kraken", "bitcoin", "crypto", "крипто", "ai model", "deepseek")):
        return "Крипто", "crypto"
    if any(word in text for word in ("election", "macron", "starmer", "nato", "ukraine", "uk ", "troops", "макрон", "стармер", "выбор", "нато", "украин")):
        return "Политика", "politics"
    if any(word in text for word in ("china", "india", "military", "clash", "korea", "китай", "инди", "конфликт", "коре")):
        return "Геополитика", "politics"
    if "news_driven" in tags:
        return "Политика", "politics"
    return "Макро", "macro"


SIMPLE_CATEGORY_LABELS = {
    "sports": "Спорт",
    "entertainment": "Кино",
    "crypto_simple": "Простое · крипто",
    "tech_oneshot": "Tech",
    "games": "Игры",
}


def extract_simple_meta(item, tags):
    package_priority = (item.get("pipelinePackage") or {}).get("priority") or {}
    analysis_priority = (item.get("analysis") or {}).get("priority") or {}
    simple_cat = (
        package_priority.get("simpleCategory")
        or analysis_priority.get("simpleCategory")
        or next((tag for tag in tags if tag in SIMPLE_CATEGORY_LABELS), None)
    )
    label = (
        package_priority.get("categoryLabel")
        or analysis_priority.get("categoryLabel")
        or SIMPLE_CATEGORY_LABELS.get(simple_cat)
    )
    return simple_cat, label


def simple_verdict_fields(market_odds, confidence):
    market = 50 if market_odds is None else market_odds
    delta = confidence - market
    if delta >= 8:
        return "Рынок занижен", "under"
    if delta <= -8:
        return "Рынок завышен", "over"
    return "Совпадаем с рынком", "match"


def horizon_short(end_date):
    days_str = horizon_days(end_date)
    match = re.match(r"(\d+)", days_str)
    days = match.group(1) if match else None
    if end_date and len(end_date) >= 10:
        _, month, day = end_date[:10].split("-")
        if days:
            return f"Закрытие {day}.{month} · {days} дн."
        return f"Закрытие {day}.{month}"
    return days_str


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


def _risk_block(item):
    package = item.get("pipelinePackage") or {}
    pie_risk = package.get("risk") or {}
    if pie_risk:
        return pie_risk
    return (item.get("analysis") or {}).get("riskOfficer") or {}


def build_agents(analysis, localized, pie_risk=None):
    priority = analysis.get("priority") or {}
    news = analysis.get("newsScout") or {}
    risk = pie_risk or analysis.get("riskOfficer") or {}
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
    package = item.get("pipelinePackage") or {}
    normalized_event = package.get("normalizedEvent") or {}
    market_snapshot = normalized_event.get("marketSnapshot") or {}
    pie_risk = package.get("risk") or {}
    tags = item.get("tags") or []
    markets = event.get("markets") or []
    first_market = markets[0] if markets else {}
    event_id = str(event.get("id"))
    title_ru = normalized_event.get("titleRu") or translate_title(event_id, event.get("title"))
    localized = localize_analysis_texts(analysis)
    simple_category, simple_category_label = extract_simple_meta(item, tags)
    category, category_tag = guess_category(
        title_ru, tags, event.get("title"), simple_category=simple_category
    )

    # marketProb is 0.0–1.0 in PIE v1.0b; convert to integer % for display
    raw_prob = market_snapshot.get("marketProb")
    if raw_prob is not None:
        market_odds = int(round(raw_prob * 100))
    else:
        market_odds = parse_prices(first_market.get("outcomePrices"))
    confidence = (analysis.get("verdict") or {}).get("confidence") or 50
    risk_level = pie_risk.get("riskLevel") or (analysis.get("riskOfficer") or {}).get("riskLevel") or "medium"
    priority_decision = (analysis.get("priority") or {}).get("decision")
    volume24 = float(event.get("volume24hr") or 0)
    volume_total = float(event.get("volume") or 0)
    liquidity_raw = market_snapshot.get("liquidity")
    if liquidity_raw is None:
        liquidity_raw = event.get("liquidity")
    try:
        liquidity_num = float(liquidity_raw or 0)
    except (TypeError, ValueError):
        liquidity_num = 0.0

    short_verdicts = {"yes", "no", "да", "нет", "pending", "watchlist", "research_required", "ожидание", "наблюдение"}
    verdict_text = localized.get("ppVerdict") or (analysis.get("verdict") or {}).get("ppVerdict") or ""
    if len(str(verdict_text)) < 25 or str(verdict_text).strip().lower() in short_verdicts:
        verdict_text = localized.get("newsSummary") or (analysis.get("newsScout") or {}).get("summary") or "PP AI проанализировал событие. Полный разбор доступен в карточке."

    edge = None
    if market_odds is not None:
        edge = max(0, confidence - market_odds)

    simple_verdict, simple_verdict_tone = simple_verdict_fields(market_odds, confidence)
    horizon_label = horizon_short((event.get("endDate") or "")[:10])

    summary_ru = localize_description(event.get("description"), title_ru)
    risk_tags_ru = pie_risk.get("flags") or localized.get("riskFlags") or (analysis.get("riskOfficer") or {}).get("flags") or []
    facts_ru = localized.get("newsFacts") or (analysis.get("newsScout") or {}).get("facts") or []

    return {
        "id": f"live-{event.get('id')}",
        "polymarketId": event.get("id"),
        "title": title_ru,
        "titleEn": event.get("title"),
        "category": category,
        "categoryTag": category_tag,
        "simpleCategory": simple_category,
        "simpleCategoryLabel": simple_category_label or category,
        "simpleVerdict": simple_verdict,
        "simpleVerdictTone": simple_verdict_tone,
        "horizonShort": horizon_label,
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
        "liquidity": round(liquidity_num) if liquidity_num > 0 else None,
        "liquidityFormatted": fmt_money(liquidity_num) if liquidity_num > 0 else None,
        "marketsCount": int(event.get("marketsCount") or len(markets) or 1),
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
        "warRoom": {"duration": 6, "agents": build_agents(analysis, localized, pie_risk=pie_risk)},
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
        source = json.load(handle)

    events = [convert_item(item) for item in source.get("items", [])]
    payload = {"events": events, "generatedAt": datetime.now(timezone.utc).isoformat()}
    json_path = os.path.join(ROOT, "data", "events-live.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    print(f"Synced {len(events)} live events to {json_path}")

    if not os.path.isdir(os.path.dirname(OUT)):
        return

    js = "/** Auto-generated from backend/data/test_events.json */\n"
    js += "window.EVENTS_LIVE = "
    js += json.dumps(payload, ensure_ascii=False, indent=2)
    js += ";\n"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(js)

    print(f"Synced {len(events)} live events to {OUT}")


if __name__ == "__main__":
    main()
