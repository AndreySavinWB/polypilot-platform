import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GAMMA_URL = os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com")


def _get_json(path, params=None):
    query = f"?{urlencode(params or {})}" if params else ""
    request = Request(
        f"{GAMMA_URL}{path}{query}",
        headers={
            "Accept": "application/json",
            "User-Agent": "PolyPilot-Platform/1.0",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def list_active_events(limit=10):
    return scan_active_events(max_events=int(limit))


def scan_active_events(max_events=300, page_size=100):
    """Сканировать активные события Polymarket с пагинацией."""
    max_events = int(max_events)
    page_size = min(int(page_size), 100)
    collected = []
    offset = 0

    while len(collected) < max_events:
        batch = _get_json(
            "/events",
            {
                "active": "true",
                "closed": "false",
                "limit": page_size,
                "offset": offset,
                "order": "volume_24hr",
                "ascending": "false",
            },
        )
        if not batch:
            break
        for raw in batch:
            collected.append(normalize_event(raw))
            if len(collected) >= max_events:
                break
        if len(batch) < page_size:
            break
        offset += page_size

    return collected


def normalize_event(event):
    markets = event.get("markets") or []
    first_market = markets[0] if markets else {}
    return {
        "id": str(event.get("id") or ""),
        "slug": event.get("slug"),
        "title": event.get("title") or event.get("ticker") or first_market.get("question"),
        "description": event.get("description") or first_market.get("description"),
        "category": event.get("category") or event.get("series", [{}])[0].get("title") if event.get("series") else None,
        "volume": event.get("volume") or first_market.get("volume"),
        "volume24hr": event.get("volume24hr") or event.get("volume_24hr"),
        "liquidity": event.get("liquidity") or first_market.get("liquidity"),
        "startDate": event.get("startDate"),
        "endDate": event.get("endDate") or first_market.get("endDate"),
        "marketsCount": len(markets),
        "markets": [
            {
                "id": str(market.get("id") or ""),
                "question": market.get("question"),
                "conditionId": market.get("conditionId"),
                "clobTokenIds": market.get("clobTokenIds"),
                "outcomes": market.get("outcomes"),
                "outcomePrices": market.get("outcomePrices"),
                "volume": market.get("volume"),
                "liquidity": market.get("liquidity"),
            }
            for market in markets[:3]
        ],
        "source": "polymarket_gamma",
        "sourceUrl": f"https://polymarket.com/event/{event.get('slug')}" if event.get("slug") else None,
    }
