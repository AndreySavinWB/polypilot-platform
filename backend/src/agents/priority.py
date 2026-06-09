"""Priority Agent — жёсткая рубрика отбора событий Polymarket.

Сканирует широкий пул рынков, отсекает мусор, ранжирует по воспроизводимому score.
Цель: события с быстрым потенциалом, понятным резолвом и торгуемой ликвидностью.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone

from src.services.llm import ask_llm, has_llm_key

# --- Рубрика (сумма весов = 100) ---
RUBRIC_WEIGHTS = {
    "volume": 25,           # объём торгов (деньги в рынке)
    "liquidity": 20,        # можно войти/выйти без искажения цены
    "news_driver": 25,      # новостной катализатор → быстрое движение
    "resolution_clarity": 15,  # понятно, что считается «Да»
    "time_to_money": 10,    # короткий горизонт → быстрее результат
    "price_quality": 5,     # цена не «мёртвая» (не 0% / 100%)
}

# Пороги решений
THRESHOLD_ACCEPTED = 70
THRESHOLD_WATCHLIST = 55

# Жёсткие отсечки (мусор)
HARD_GATES = {
    "min_liquidity": 5_000,
    "min_volume_total": 25_000,
    "min_volume_24h": 500,
    "min_description_len": 80,
    "max_horizon_days": 540,
    "min_horizon_days": 1,
    "dead_price_low": 0.02,
    "dead_price_high": 0.98,
}

NEWS_KEYWORDS = (
    "election", "выбор", "trump", "biden", "fed", "rate", "ставк", "war", "войн",
    "bitcoin", "btc", "eth", "crypto", "ipo", "nato", "нато", "ukraine", "украин",
    "ceasefire", "перемири", "tariff", "тариф", "inflation", "инфляц", "gdp",
    "macron", "starmer", "congress", "senate", "shutdown", "default", "sanction",
    "merger", "acquisition", "launch", "announce", "resign", "impeach", "referendum",
)

PRIORITY_LLM_PROMPT = """Ты — Priority Agent PolyPilot. Оцени событие прогнозного рынка по двум качественным критериям.
Верни ТОЛЬКО JSON:
{
  "newsDriverScore": 0-100,
  "resolutionClarityScore": 0-100,
  "reason": "1-2 предложения на русском: почему событие прибыльно/неприбыльно для PP"
}

newsDriverScore (новостной драйвер):
- 80-100: явный ближайший катализатор (выборы, заседание ЦБ, суд, дедлайн, IPO)
- 50-79: тема живёт в новостях, но дата размыта
- 0-49: нет драйвера, рынок «спит»

resolutionClarityScore (понятность резолва):
- 80-100: чёткие критерии «Да/Нет», официальный источник, дата
- 50-79: в целом понятно, есть нюансы
- 0-49: спорный/размытый резолв, мусор

Не давай советов купить/продать. Только оценка пригодности для аналитики PP."""


def _to_number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0


def _parse_prices(raw):
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
        return float(raw[0])
    except (TypeError, ValueError, IndexError):
        return None


def _days_to_end(event):
    end = event.get("endDate")
    if not end:
        return None
    try:
        end_dt = datetime.fromisoformat(str(end).replace("Z", "+00:00"))
        return (end_dt - datetime.now(timezone.utc)).days
    except ValueError:
        return None


def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def _scale_log(value, low, high):
    """Map value to 0-100 on log scale between low and high anchors."""
    if value <= 0:
        return 0
    if value >= high:
        return 100
    if value <= low:
        return _clamp((value / low) * 40)
    log_pos = math.log10(value) - math.log10(low)
    log_span = math.log10(high) - math.log10(low)
    return _clamp(40 + (log_pos / log_span) * 60)


def check_hard_gates(event):
    """Жёсткие фильтры — мусор отсекается до рубрики."""
    failed = []
    liquidity = _to_number(event.get("liquidity"))
    volume_total = _to_number(event.get("volume"))
    volume_24h = _to_number(event.get("volume24hr"))
    description = (event.get("description") or "").strip()
    days = _days_to_end(event)
    price = _parse_prices((event.get("markets") or [{}])[0].get("outcomePrices"))

    if liquidity < HARD_GATES["min_liquidity"]:
        failed.append(f"ликвидность ${liquidity:,.0f} < ${HARD_GATES['min_liquidity']:,.0f}")
    if volume_total < HARD_GATES["min_volume_total"]:
        failed.append(f"общий объём ${volume_total:,.0f} < ${HARD_GATES['min_volume_total']:,.0f}")
    if volume_24h < HARD_GATES["min_volume_24h"]:
        failed.append(f"объём 24ч ${volume_24h:,.0f} < ${HARD_GATES['min_volume_24h']:,.0f}")
    if len(description) < HARD_GATES["min_description_len"]:
        failed.append("слишком короткое или пустое описание резолва")
    if days is None:
        failed.append("нет даты окончания рынка")
    elif days < HARD_GATES["min_horizon_days"]:
        failed.append("рынок уже закрывается / просрочен")
    elif days > HARD_GATES["max_horizon_days"]:
        failed.append(f"горизонт {days} дн. — слишком долго до денег")
    if price is not None and (price <= HARD_GATES["dead_price_low"] or price >= HARD_GATES["dead_price_high"]):
        failed.append(f"цена {price * 100:.0f}% — рынок фактически решён")

    return {"passed": not failed, "failed": failed}


def score_volume(event):
    volume_total = _to_number(event.get("volume"))
    volume_24h = _to_number(event.get("volume24hr"))
    total_score = _scale_log(volume_total, 25_000, 5_000_000)
    day_score = _scale_log(volume_24h, 500, 250_000)
    score = _clamp(total_score * 0.55 + day_score * 0.45)
    note = f"объём всего ${volume_total:,.0f}, за 24ч ${volume_24h:,.0f}"
    return score, note


def score_liquidity(event):
    liquidity = _to_number(event.get("liquidity"))
    score = _scale_log(liquidity, 5_000, 500_000)
    note = f"ликвидность ${liquidity:,.0f}"
    return score, note


def score_news_driver_heuristic(event):
    text = f"{event.get('title') or ''} {event.get('description') or ''}".lower()
    hits = sum(1 for kw in NEWS_KEYWORDS if kw in text)
    volume_24h = _to_number(event.get("volume24hr"))
    volume_total = max(_to_number(event.get("volume")), 1)
    activity_ratio = volume_24h / volume_total
    keyword_score = _clamp(hits * 18)
    activity_score = _clamp(activity_ratio * 400)
    score = _clamp(keyword_score * 0.65 + activity_score * 0.35)
    note = f"ключевых тем: {hits}, активность 24ч/всего: {activity_ratio:.2%}"
    return score, note


def score_resolution_clarity_heuristic(event):
    description = (event.get("description") or "").lower()
    score = 35
    checks = []
    if len(description) >= 200:
        score += 20
        checks.append("развёрнутое описание")
    if re.search(r"resolve|resolution|will resolve|резолв", description):
        score += 15
        checks.append("есть правила резолва")
    if re.search(r"yes|no|\"да\"|\"нет\"", description):
        score += 10
        checks.append("бинарный исход")
    if event.get("endDate"):
        score += 10
        checks.append("есть дедлайн")
    markets_count = int(event.get("marketsCount") or 0)
    if markets_count > 4:
        score -= 15
        checks.append("много подрынков — сложнее")
    score = _clamp(score)
    note = ", ".join(checks) if checks else "базовая проверка"
    return score, note


def score_time_to_money(event):
    days = _days_to_end(event)
    if days is None:
        return 0, "нет даты"
    if days <= 14:
        score = 95
    elif days <= 45:
        score = 85
    elif days <= 90:
        score = 75
    elif days <= 180:
        score = 55
    elif days <= 365:
        score = 35
    else:
        score = 15
    note = f"до резолва ~{days} дн."
    return score, note


def score_price_quality(event):
    markets = event.get("markets") or []
    prices = [_parse_prices(m.get("outcomePrices")) for m in markets[:3]]
    prices = [p for p in prices if p is not None]
    if not prices:
        return 50, "цена недоступна"
    best = max(prices, key=lambda p: min(p, 1 - p))
    uncertainty = min(best, 1 - best)
    if uncertainty >= 0.25:
        score = 100
    elif uncertainty >= 0.10:
        score = 75
    elif uncertainty >= 0.05:
        score = 40
    else:
        score = 10
    note = f"лидирующая вероятность ~{best * 100:.0f}%"
    return score, note


def _llm_qualitative_scores(event):
    if not has_llm_key():
        return None
    try:
        return ask_llm(
            PRIORITY_LLM_PROMPT,
            {
                "title": event.get("title"),
                "description": (event.get("description") or "")[:1500],
                "volume24hr": event.get("volume24hr"),
                "liquidity": event.get("liquidity"),
                "endDate": event.get("endDate"),
                "marketsCount": event.get("marketsCount"),
            },
        )
    except Exception:
        return None


def score_event(event, use_llm=False):
    """Полный расчёт Priority для одного события."""
    gates = check_hard_gates(event)
    if not gates["passed"]:
        return {
            "agent": "Priority Agent",
            "score": 0,
            "decision": "rejected",
            "reason": "Отклонено: " + "; ".join(gates["failed"]),
            "rubric": {},
            "hardGates": gates,
            "scoringMode": "rubric_v1",
        }

    components = {}
    total = 0.0

    for key, scorer in (
        ("volume", score_volume),
        ("liquidity", score_liquidity),
        ("news_driver", score_news_driver_heuristic),
        ("resolution_clarity", score_resolution_clarity_heuristic),
        ("time_to_money", score_time_to_money),
        ("price_quality", score_price_quality),
    ):
        raw, note = scorer(event)
        weight = RUBRIC_WEIGHTS[key]
        weighted = raw * weight / 100
        components[key] = {
            "score": round(raw, 1),
            "weight": weight,
            "weighted": round(weighted, 2),
            "note": note,
        }
        total += weighted

    llm_reason = None
    if use_llm:
        llm = _llm_qualitative_scores(event)
        if llm:
            news_llm = _clamp(float(llm.get("newsDriverScore") or 0))
            res_llm = _clamp(float(llm.get("resolutionClarityScore") or 0))
            llm_reason = llm.get("reason")

            # LLM заменяет эвристику на 70%, сохраняя 30% эвристики для стабильности
            for key, llm_score in (("news_driver", news_llm), ("resolution_clarity", res_llm)):
                old = components[key]
                blended = old["score"] * 0.3 + llm_score * 0.7
                weight = RUBRIC_WEIGHTS[key]
                total -= old["weighted"]
                components[key] = {
                    "score": round(blended, 1),
                    "weight": weight,
                    "weighted": round(blended * weight / 100, 2),
                    "note": old["note"] + " + LLM",
                    "llmScore": llm_score,
                }
                total += blended * weight / 100

    final_score = round(_clamp(total), 1)
    if final_score >= THRESHOLD_ACCEPTED:
        decision = "accepted"
    elif final_score >= THRESHOLD_WATCHLIST:
        decision = "watchlist"
    else:
        decision = "rejected"

    reason = llm_reason or _build_reason_ru(components, decision, final_score)

    return {
        "agent": "Priority Agent",
        "score": final_score,
        "decision": decision,
        "reason": reason,
        "rubric": components,
        "hardGates": gates,
        "scoringMode": "rubric_v1_llm" if use_llm and llm_reason else "rubric_v1",
        "thresholds": {
            "accepted": THRESHOLD_ACCEPTED,
            "watchlist": THRESHOLD_WATCHLIST,
        },
    }


def _build_reason_ru(components, decision, final_score):
    top = sorted(components.items(), key=lambda x: x[1]["weighted"], reverse=True)[:2]
    top_txt = ", ".join(f"{k} ({v['score']})" for k, v in top)
    labels = {
        "accepted": "Принято в топ PP",
        "watchlist": "На наблюдении",
        "rejected": "Отклонено",
    }
    return f"{labels.get(decision, decision)} · score {final_score}. Сильные стороны: {top_txt}."


def scan_and_rank(events, top_n=10, min_decision="watchlist", use_llm_top_k=15):
    """Оценить пул событий и вернуть лучшие."""
    scored = []
    for event in events:
        priority = score_event(event, use_llm=False)
        scored.append({"event": event, "priority": priority})

    scored.sort(key=lambda row: row["priority"]["score"], reverse=True)

    if use_llm_top_k and has_llm_key():
        for row in scored[:use_llm_top_k]:
            if row["priority"]["decision"] == "rejected" and row["priority"]["score"] < THRESHOLD_WATCHLIST:
                continue
            row["priority"] = score_event(row["event"], use_llm=True)

        scored.sort(key=lambda row: row["priority"]["score"], reverse=True)

    allowed = {"accepted", "watchlist"} if min_decision == "watchlist" else {"accepted"}
    filtered = [row for row in scored if row["priority"]["decision"] in allowed]

    for index, row in enumerate(filtered, start=1):
        row["priority"]["rank"] = index
        row["priority"]["scannedTotal"] = len(events)

    return {
        "scannedTotal": len(events),
        "passedGates": sum(1 for r in scored if r["priority"]["hardGates"]["passed"]),
        "accepted": sum(1 for r in scored if r["priority"]["decision"] == "accepted"),
        "watchlist": sum(1 for r in scored if r["priority"]["decision"] == "watchlist"),
        "rejected": sum(1 for r in scored if r["priority"]["decision"] == "rejected"),
        "top": filtered[:top_n],
        "rubricVersion": "v1",
        "weights": RUBRIC_WEIGHTS,
    }
