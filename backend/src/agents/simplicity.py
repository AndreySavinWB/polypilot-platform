"""Simplicity Filter — отбор простых событий для PolyPilot Simple Events v1.

Rule-based rubric per SIMPLE_EVENTS_POLICY.md. Без LLM.
"""

from __future__ import annotations

import json
import re

from src.agents.priority import _clamp, _days_to_end, _to_number

THRESHOLD_ACCEPTED = 70
THRESHOLD_WATCHLIST = 60
MAX_HORIZON_DAYS = 90
MAX_MARKETS = 2

# Hard reject: macro / politics / geo (Hold categories)
HOLD_KEYWORDS = (
    "fed", "fomc", "federal reserve", "rate cut", "rate hike", "interest rate",
    "basis point", "inflation", "gdp", "recession", "cpi", "pce", "macro",
    "midterm", "election", "presidential", "congress", "senate", "house of representatives",
    "balance of power", "which party", "trump", "biden", "harris", "putin", "zelensky",
    "ukraine", "russia", "war", "ceasefire", "nato", "sanction", "geopolit",
    "tariff", "shutdown", "default", "impeach", "referendum", "primary",
    "nobel peace", "regime fall", "regime change",
    "фрс", "ставк", "инфляц", "выбор", "сенат", "конгресс", "войн", "украин", "нато",
)

WEATHER_KEYWORDS = (
    "hurricane", "temperature", "weather", "rainfall", "snowfall", "celsius", "fahrenheit",
    "погод", "ураган", "осадк",
)

AMBIGUOUS_RESOLUTION = (
    "uma discretion", "subjective", "community consensus", "good faith",
    "reasonable person", "at its sole discretion", "interpretation",
)

# P0 — sports + entertainment
SPORTS_KEYWORDS = (
    "championship", "nba", "nfl", "nhl", "mlb", "mls", "soccer", "football",
    "world cup", "super bowl", "playoff", "playoffs", "tournament", "final",
    "mvp", "uefa", "champions league", "premier league", "match", " vs ",
    "win the", "winner", "cup", "serie a", "la liga", "f1", "formula 1",
    "tennis", "wimbledon", "olympic",
)

ENTERTAINMENT_KEYWORDS = (
    "oscar", "academy award", "best picture", "best actor", "best director",
    "emmy", "grammy", "golden globe", "box office", "opening weekend",
    "billboard", "spotify", "netflix", "survivor", "bachelor", "reality tv",
    "award", "nominee", "nomination",
)

# P1 — simple crypto + tech one-shot
SIMPLE_CRYPTO_KEYWORDS = (
    "bitcoin", "btc", "ethereum", "eth", "solana", "sol", "xrp",
)
SIMPLE_CRYPTO_PATTERNS = (
    r"above \$", r"below \$", r"reach \$", r"hit \$", r"price of",
    r"above \d", r"before .*\?",
)

TECH_ONESHOT_KEYWORDS = (
    "wwdc", "apple announce", "google i/o", "product launch", "release date",
    "iphone", "keynote",
)

GAMES_KEYWORDS = (
    "steam", "esports", "counter-strike", "dota", "league of legends",
    "valorant", "game of the year",
)

OFFICIAL_SOURCE_PATTERNS = (
    r"espn", r"official", r"academy", r"oscar\.org", r"fifa", r"uefa",
    r"nba\.com", r"nfl\.com", r"coinbase", r"coingecko", r"coinmarketcap",
    r"apple\.com", r"sec filing", r"associated press", r"reuters", r"ap news",
)


def _event_text(event) -> str:
    title = event.get("title") or ""
    description = event.get("description") or ""
    category = event.get("category") or ""
    return f"{title} {description} {category}".lower()


def _keyword_hits(text: str, keywords: tuple[str, ...]) -> int:
    return sum(1 for kw in keywords if kw in text)


def detect_simple_category(event) -> dict:
    """Return simpleCategory, categoryTier, and hold flags."""
    text = _event_text(event)

    if _keyword_hits(text, HOLD_KEYWORDS):
        return {
            "simpleCategory": "hold_politics_macro",
            "categoryTier": "hold",
            "categoryLabel": "Политика / macro",
        }
    if _keyword_hits(text, WEATHER_KEYWORDS):
        return {
            "simpleCategory": "hold_weather",
            "categoryTier": "hold",
            "categoryLabel": "Погода",
        }

    sports_hits = _keyword_hits(text, SPORTS_KEYWORDS)
    entertainment_hits = _keyword_hits(text, ENTERTAINMENT_KEYWORDS)
    crypto_hits = _keyword_hits(text, SIMPLE_CRYPTO_KEYWORDS)
    tech_hits = _keyword_hits(text, TECH_ONESHOT_KEYWORDS)
    games_hits = _keyword_hits(text, GAMES_KEYWORDS)

    crypto_simple = crypto_hits and any(re.search(p, text) for p in SIMPLE_CRYPTO_PATTERNS)

    candidates = [
        ("sports", "P0", "Спорт", sports_hits),
        ("entertainment", "P0", "Шоу / кино", entertainment_hits),
        ("crypto_simple", "P1", "Простое крипто", 2 if crypto_simple else crypto_hits),
        ("tech_oneshot", "P1", "Tech one-shot", tech_hits),
        ("games", "P2", "Игры", games_hits),
    ]
    candidates.sort(key=lambda row: row[3], reverse=True)
    best = candidates[0]
    if best[3] <= 0:
        return {
            "simpleCategory": "other",
            "categoryTier": "hold",
            "categoryLabel": "Вне whitelist",
        }

    return {
        "simpleCategory": best[0],
        "categoryTier": best[1],
        "categoryLabel": best[2],
    }


def check_hard_rejects(event) -> dict:
    """Hard reject before rubric scoring."""
    failed = []
    text = _event_text(event)
    markets_count = int(event.get("marketsCount") or 0)
    days = _days_to_end(event)
    category = detect_simple_category(event)

    if category["categoryTier"] == "hold":
        failed.append(f"категория hold: {category['categoryLabel']}")

    if markets_count > MAX_MARKETS:
        failed.append(f"multi-market: {markets_count} подрынков > {MAX_MARKETS}")

    if days is None:
        failed.append("нет даты resolution")
    elif days < 1:
        failed.append("рынок закрывается / просрочен")
    elif days > MAX_HORIZON_DAYS:
        failed.append(f"горизонт {days} дн. > {MAX_HORIZON_DAYS}")

    if any(phrase in text for phrase in AMBIGUOUS_RESOLUTION):
        failed.append("серая зона resolution / UMA discretion")

    description = (event.get("description") or "").strip()
    if len(description) < 40:
        failed.append("слишком короткое описание — непонятный резолв")

    return {"passed": not failed, "failed": failed, "category": category}


def score_clear_outcome(event) -> tuple[float, str]:
    markets_count = int(event.get("marketsCount") or 0)
    markets = event.get("markets") or []

    if markets_count > MAX_MARKETS:
        return 0, f"{markets_count} подрынков — сложный исход"

    if markets_count <= 1:
        return 20, "бинарный рынок (1 market)"

    outcomes = []
    for market in markets[:MAX_MARKETS]:
        raw = market.get("outcomes")
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                raw = []
        if isinstance(raw, list):
            outcomes.append(len(raw))

    if outcomes and max(outcomes) <= 2 and len(outcomes) <= MAX_MARKETS:
        return 18, f"≤{MAX_MARKETS} бинарных подрынка"

    if markets_count <= 5:
        return 10, f"{markets_count} исхода — умеренная сложность"

    return 0, "слишком много исходов"


def score_title_clarity(event) -> tuple[float, str]:
    title = (event.get("title") or "").strip()
    text = title.lower()
    score = 10
    notes = []

    if not title:
        return 0, "нет title"

    if len(title) <= 100:
        score += 3
        notes.append("короткий title")
    elif len(title) > 160:
        score -= 5
        notes.append("длинный title")

    if _keyword_hits(text, HOLD_KEYWORDS):
        return 0, "title содержит macro/politics"

    if "?" in title or title.lower().startswith("will "):
        score += 2
        notes.append("явный вопрос")

    return _clamp(score, 0, 15), ", ".join(notes) or "базовая проверка"


def score_horizon(event) -> tuple[float, str]:
    days = _days_to_end(event)
    if days is None:
        return 0, "нет даты"
    if days <= 30:
        return 15, f"~{days} дн. (≤30)"
    if days <= MAX_HORIZON_DAYS:
        return 10, f"~{days} дн. (≤90)"
    return 0, f"~{days} дн. (>90)"


def score_truth_source(event) -> tuple[float, str]:
    text = _event_text(event)
    category = detect_simple_category(event)
    hits = sum(1 for pattern in OFFICIAL_SOURCE_PATTERNS if re.search(pattern, text))

    if hits >= 2:
        return 20, f"официальные источники в описании ({hits})"
    if hits == 1:
        return 16, "есть публичный источник"

    tier = category.get("categoryTier")
    kind = category.get("simpleCategory")
    if tier == "P0":
        return 14, f"категория {kind} — проверяемый исход по умолчанию"
    if tier == "P1" and kind == "crypto_simple":
        return 12, "крипто — price feed как источник"
    if "community" in text or "social media" in text:
        return 0, "источник — мнение сообщества"

    return 6, "источник не указан явно"


def score_liquidity_rubric(event) -> tuple[float, str]:
    liquidity = _to_number(event.get("liquidity"))
    if liquidity >= 100_000:
        return 10, f"${liquidity:,.0f} (≥$100K)"
    if liquidity >= 50_000:
        return 7, f"${liquidity:,.0f} (≥$50K)"
    if liquidity >= 20_000:
        return 4, f"${liquidity:,.0f} (≥$20K)"
    return 0, f"${liquidity:,.0f} (<$20K)"


def score_category_whitelist(event) -> tuple[float, str]:
    category = detect_simple_category(event)
    tier = category["categoryTier"]
    if tier == "P0":
        return 10, f"P0 · {category['categoryLabel']}"
    if tier == "P1":
        return 10, f"P1 · {category['categoryLabel']}"
    if tier == "P2":
        return 6, f"P2 · {category['categoryLabel']} (выборочно)"
    return 0, category["categoryLabel"]


def score_resolution_clarity(event) -> tuple[float, str]:
    description = (event.get("description") or "").lower()
    score = 4
    notes = []

    if re.search(r"resolve|resolution|will resolve|резолв", description):
        score += 3
        notes.append("есть правила резолва")
    if re.search(r"\byes\b|\bno\b|\"yes\"|\"no\"", description):
        score += 2
        notes.append("бинарный исход в правилах")
    if event.get("endDate"):
        score += 1
        notes.append("есть дедлайн")

    if any(phrase in description for phrase in AMBIGUOUS_RESOLUTION):
        return 0, "серая зона resolution"

    return _clamp(score, 0, 10), ", ".join(notes) or "базовая проверка"


RUBRIC_COMPONENTS = (
    ("clear_outcome", score_clear_outcome),
    ("title_clarity", score_title_clarity),
    ("horizon", score_horizon),
    ("truth_source", score_truth_source),
    ("liquidity", score_liquidity_rubric),
    ("category_whitelist", score_category_whitelist),
    ("resolution_clarity", score_resolution_clarity),
)


def score_event(event) -> dict:
    """Simplicity Score for one event — compatible with Priority Agent shape."""
    hard = check_hard_rejects(event)
    category = hard["category"]

    if not hard["passed"]:
        return {
            "agent": "Simplicity Filter",
            "score": 0,
            "decision": "rejected",
            "reason": "Hard reject: " + "; ".join(hard["failed"]),
            "rubric": {},
            "hardGates": hard,
            "scoringMode": "simplicity_v1",
            "simpleCategory": category.get("simpleCategory"),
            "categoryTier": category.get("categoryTier"),
            "categoryLabel": category.get("categoryLabel"),
            "thresholds": {
                "accepted": THRESHOLD_ACCEPTED,
                "watchlist": THRESHOLD_WATCHLIST,
            },
        }

    components = {}
    total = 0.0
    for key, scorer in RUBRIC_COMPONENTS:
        raw, note = scorer(event)
        components[key] = {"score": round(raw, 1), "note": note}
        total += raw

    final_score = round(_clamp(total, 0, 100), 1)
    if final_score >= THRESHOLD_ACCEPTED:
        decision = "accepted"
    elif final_score >= THRESHOLD_WATCHLIST:
        decision = "watchlist"
    else:
        decision = "rejected"

    labels = {
        "accepted": "Simple accept · кандидат на публикацию",
        "watchlist": "Simple watchlist · копим, не публикуем",
        "rejected": "Simple reject",
    }
    top = sorted(components.items(), key=lambda x: x[1]["score"], reverse=True)[:2]
    top_txt = ", ".join(f"{k} ({v['score']})" for k, v in top)
    reason = f"{labels[decision]} · score {final_score}. {category['categoryLabel']}. Сильные: {top_txt}."

    return {
        "agent": "Simplicity Filter",
        "score": final_score,
        "decision": decision,
        "reason": reason,
        "rubric": components,
        "hardGates": hard,
        "scoringMode": "simplicity_v1",
        "simpleCategory": category.get("simpleCategory"),
        "categoryTier": category.get("categoryTier"),
        "categoryLabel": category.get("categoryLabel"),
        "thresholds": {
            "accepted": THRESHOLD_ACCEPTED,
            "watchlist": THRESHOLD_WATCHLIST,
        },
    }


def scan_and_rank(events, top_n=10, min_decision="accepted", use_llm_top_k=0):
    """Rank events by Simplicity Score. LLM not used (use_llm_top_k ignored)."""
    del use_llm_top_k  # simplicity is rule-based only

    scored = []
    for event in events:
        priority = score_event(event)
        scored.append({"event": event, "priority": priority})

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
        "rubricVersion": "simplicity_v1",
        "rankMode": "simple",
        "weights": {key: "see SIMPLE_EVENTS_POLICY" for key, _ in RUBRIC_COMPONENTS},
    }
