# Polymarket Analytics Check — v1 (PIE 5.6)

> [[INTELLIGENCE_DATA_FLOW]] · [[СХЕМА_ДАННЫХ_СОБЫТИЯ]] · [[СХЕМА_МЯСОРУБКИ]] · [[PROBABILITY_INTELLIGENCE_ENGINE]]

> **Версия:** `external_market_check_v1` · **Статус:** MVP mock + UI · **Дата:** 14 июня 2026

---

## Зачем

Проверить, **найдено ли событие на polymarketanalytics.com**, и понять, что полезного можно взять из внешней аналитики рынка.

**Важно:** Polymarket Analytics **не** главный источник истины.  
Главный источник — **Polymarket / наш scanner**. PMA — вспомогательный слой проверки рыночного поведения.

---

## Место в pipeline

```text
5.  Сбор доказательств
5.5 Comment Analysis (A/B/C)
5.6 Polymarket Analytics Check     → externalMarketCheck
6.  Карта противоречий
```

**Код MVP:** `backend/src/agents/external_market_check.py`

---

## Контракт `externalMarketCheck`

```json
{
  "lookupStatus": "found|not_found|similar_found|error",
  "eventUrl": "https://polymarket.com/event/...",
  "pmAnalyticsUrl": "https://polymarketanalytics.com/events/...",
  "features": {
    "priceChartAvailable": true,
    "orderBookAvailable": true,
    "similarMarketsAvailable": false,
    "traderWhaleDataAvailable": false
  },
  "metrics": {
    "liquidityLevel": "low|medium|high|unknown",
    "spreadLevel": "low|medium|high|unknown",
    "priceReliability": "reliable|distorted|unknown",
    "sharpPriceMove": false,
    "orderBookSkew": "balanced|yes_heavy|no_heavy|unknown",
    "anomalies": ["thin_liquidity", "low_volume_24h"]
  },
  "marketCharacter": "alive|thin|weird|insufficient_data",
  "observationsRu": ["…", "…", "…"],
  "summaryRu": "Короткий вывод на русском",
  "marketOddsTrust": "low|medium|high",
  "forecastImpact": "weak_negative|neutral|…",
  "probabilityAdjustPct": 0,
  "dataSource": "polymarket_analytics_stub",
  "scoringMode": "mock_v1|stub_v0"
}
```

### lookupStatus

| Значение | Смысл |
|----------|--------|
| `found` | Событие найдено на PMA |
| `not_found` | Не найдено |
| `similar_found` | Найдено похожее, не точное совпадение |
| `error` | Ошибка запроса / парсинга |

### marketCharacter (вывод)

| Значение | UX |
|----------|-----|
| `alive` | рынок живой |
| `thin` | рынок тонкий |
| `weird` | рынок странный |
| `insufficient_data` | данных мало |

---

## UI (Simple open card)

Блок **«Данные с Polymarket Analytics»**:

- статус: найдено / не найдено;
- 3 коротких наблюдения;
- итоговый вывод;
- влияние на прогноз.

Без технических терминов в лице пользователя: spread / order book → «ликвидность низкая», «цена может искажаться».

Если `not_found`: **«Событие не найдено на Polymarket Analytics»**.

Рендер: `platform/assets/js/simple-open-card.js` → `renderExternalMarketCheckSection()`.

---

## MVP / заглушки

| Компонент | Статус |
|-----------|--------|
| PMA search API / scraper | ❌ stub |
| Tesla `live-79061` mock | ✅ |
| UI open card | ✅ |
| Probability Engine weight | ❌ не подключено |
| checkedReview «внешние сервисы» | ✅ только при real dataSource |

---

## Связь с другими полями

- **`marketStructure`** — внутренний анализ PP; не заменяет PMA check.
- **`marketIntelligence`** — flow денег; PMA может дополнять, но не дублировать как источник истины.
- **`checkedReview.externalAnalytics`** — галочка только если PMA `found` и не stub.
