"""Event Type Classifier — PIE v1.0b.

Rule-based keyword classifier per EVENT_TYPE_CLASSIFIER.md.
Метод v1: keyword matching по titleRu + rawQuestion.
Если confidence < 0.25 → eventType = "other".
LLM-классификация — v2 (после Memory).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------
# Структура: { eventType: { "keywords": [...], "subtypes": {name: [kw,...]}, "analysisProfile": str } }
# keywords — триггеры для определения типа
# subtypes — триггеры для subType внутри типа (первый совпавший wins)

TAXONOMY: dict[str, dict] = {
    "regulatory": {
        "keywords": [
            "fed", "fomc", "federal reserve", "rate cut", "rate hike", "interest rate",
            "basis point", "monetary policy", "quantitative", "ecb", "european central bank",
            "bank of england", "boe", "boj", "pboc", "central bank", "sec ruling",
            "cftc", "фрс", "ставка", "снижение ставки", "повышение ставки", "цб рф",
        ],
        "subtypes": {
            "fed_rate": ["fed", "fomc", "federal reserve", "rate cut", "rate hike", "basis point", "фрс"],
            "sec_ruling": ["sec ruling", "securities and exchange commission"],
            "ecb": ["ecb", "european central bank"],
            "other_central_bank": ["bank of england", "boe", "boj", "pboc", "central bank"],
        },
        "analysisProfile": "macro_regulatory",
    },
    "elections": {
        "keywords": [
            "election", "vote", "ballot", "primary", "senate", "presidential", "congress",
            "runoff", "incumbent", "candidate", "electoral", "polling", "midterm",
            "выборы", "голосование", "кандидат", "президент", "сенат", "парламент",
            "macron", "starmer", "trump", "biden", "harris",
        ],
        "subtypes": {
            "us_presidential": [
                "president", "presidential", "white house", "trump", "biden", "harris",
                "oval office",
            ],
            "us_senate": ["senate", "congress", "representative", "house of representatives"],
            "eu_national": ["macron", "starmer", "uk election", "european", "british election"],
        },
        "analysisProfile": "election_political",
    },
    "crypto": {
        "keywords": [
            "bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "defi",
            "etf", "halving", "liquidation", "binance", "coinbase", "altcoin",
            "solana", "sol", "xrp", "stablecoin", "nft", "крипто", "биткоин",
            "эфириум", "блокчейн", "криптовалюта",
        ],
        "subtypes": {
            "etf_approval": ["etf", "spot etf", "etf approval", "etf rejection"],
            "exchange_event": ["binance", "coinbase", "exchange", "listing", "delisting"],
            "protocol_upgrade": ["upgrade", "merge", "fork", "halving", "hard fork"],
            "regulation": ["crypto regulation", "crypto ban", "sec crypto", "crackdown"],
        },
        "analysisProfile": "crypto_market",
    },
    "economics": {
        "keywords": [
            "inflation", "gdp", "employment", "nfp", "jobs report", "unemployment",
            "cpi", "pce", "trade deficit", "recession", "economic growth", "gdp growth",
            "инфляция", "ввп", "безработица", "рецессия", "экономика",
            "non-farm payroll", "payroll", "consumer price",
        ],
        "subtypes": {
            "inflation": ["inflation", "cpi", "pce", "consumer price", "инфляция"],
            "gdp": ["gdp", "economic growth", "growth rate", "ввп"],
            "employment": [
                "jobs", "nfp", "non-farm", "unemployment", "employment", "payroll",
                "безработица",
            ],
            "trade": ["trade", "deficit", "tariff", "import", "export", "тариф"],
            "recession": ["recession", "рецессия", "contraction"],
        },
        "analysisProfile": "macro_economic",
    },
    "geopolitics": {
        "keywords": [
            "ukraine", "war", "ceasefire", "nato", "sanctions", "russia", "conflict",
            "diplomacy", "treaty", "troops", "military", "invasion", "missile",
            "украина", "война", "перемирие", "нато", "санкции", "россия",
            "геополитика", "конфликт", "переговоры",
        ],
        "subtypes": {
            "conflict": ["war", "conflict", "troops", "military", "invasion", "войн", "конфликт"],
            "diplomacy": ["diplomacy", "treaty", "deal", "talks", "переговор", "summit"],
            "sanctions": ["sanctions", "санкции", "embargo"],
        },
        "analysisProfile": "geopolitical",
    },
    "legal": {
        "keywords": [
            "court", "supreme court", "ruling", "lawsuit", "judge", "verdict",
            "criminal", "civil", "federal court", "indictment", "trial", "appeal",
            "суд", "иск", "приговор", "верховный суд", "уголовное",
        ],
        "subtypes": {
            "supreme_court": ["supreme court", "верховный суд"],
            "federal_court": ["federal court", "district court", "circuit court"],
            "criminal": ["criminal", "indictment", "prosecution", "уголовное"],
            "civil": ["civil", "lawsuit", "settlement", "иск"],
        },
        "analysisProfile": "legal_judicial",
    },
    "sports": {
        "keywords": [
            "championship", "nba", "nfl", "nhl", "mlb", "soccer", "football",
            "world cup", "super bowl", "playoffs", "tournament", "match", "game",
            "чемпионат", "кубок", "матч", "финал",
        ],
        "subtypes": {
            "championship": [
                "championship", "super bowl", "world cup", "чемпионат", "title",
            ],
            "match": ["match", "game", " vs ", "play", "матч"],
            "tournament": ["tournament", "playoffs", "series", "bracket"],
        },
        "analysisProfile": "sports_statistics",
    },
    "corporate": {
        "keywords": [
            "earnings", "ipo", "merger", "acquisition", "product launch", "ceo",
            "revenue", "guidance", "quarterly", "profit", "buyout", "spin-off",
            "kraken", "apple", "microsoft", "google", "meta", "amazon", "tesla",
            "прибыль", "слияние", "поглощение", "ipo",
        ],
        "subtypes": {
            "earnings": ["earnings", "revenue", "quarterly", "profit", "guidance", "прибыль"],
            "merger": ["merger", "acquisition", "buyout", "слияние", "поглощение"],
            "product_launch": ["launch", "release", "announce", "debut"],
            "leadership": ["ceo", "resign", "appoint", "leadership", "fired"],
        },
        "analysisProfile": "corporate_fundamental",
    },
}

_OTHER_RESULT = {
    "eventType": "other",
    "subType": "other",
    "classifierConfidence": 0.0,
    "analysisProfile": "general",
}

CONFIDENCE_THRESHOLD = 0.25


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _score_type(event_type: str, text: str) -> int:
    """Count keyword hits for a given event type."""
    keywords = TAXONOMY[event_type]["keywords"]
    return sum(1 for kw in keywords if kw in text)


def _find_subtype(event_type: str, text: str) -> str:
    """Return the first matching subtype, or 'other'."""
    for subtype, triggers in TAXONOMY[event_type]["subtypes"].items():
        if any(t in text for t in triggers):
            return subtype
    return "other"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_event(normalized_event: dict, raw_question: str = "") -> dict:
    """Classify event type from normalizedEvent + rawQuestion.

    Returns eventClassification dict per output contract.
    """
    title_ru = normalized_event.get("titleRu") or ""
    resolution = normalized_event.get("resolutionCriteria") or ""
    text = f"{title_ru} {raw_question} {resolution}".lower()

    scores: dict[str, int] = {et: _score_type(et, text) for et in TAXONOMY}

    total_hits = sum(scores.values())
    if total_hits == 0:
        return dict(_OTHER_RESULT)

    winner = max(scores, key=lambda t: scores[t])
    winner_hits = scores[winner]

    # Confidence = winner's share of all keyword hits across all types.
    # High confidence when one type dominates; low when scattered.
    confidence = round(winner_hits / total_hits, 2)

    if confidence < CONFIDENCE_THRESHOLD:
        return dict(_OTHER_RESULT)

    return {
        "eventType": winner,
        "subType": _find_subtype(winner, text),
        "classifierConfidence": confidence,
        "analysisProfile": TAXONOMY[winner]["analysisProfile"],
    }
