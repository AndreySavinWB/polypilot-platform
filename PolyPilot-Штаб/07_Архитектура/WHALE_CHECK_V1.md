# Hashdive / Whale Check — v1 (PIE 5.7)

> [[INTELLIGENCE_DATA_FLOW]] · [[СХЕМА_ДАННЫХ_СОБЫТИЯ]] · [[EXTERNAL_MARKET_CHECK_V1]] · [[COMMENT_ANALYSIS_V1]]

> **Версия:** `whale_check_v1` · **Статус:** MVP mock + UI · **Дата:** 14 июня 2026

---

## Зачем отдельный блок

| Блок | Вопрос |
|------|--------|
| **5.6 Polymarket Analytics** | Рынок живой или тонкий? |
| **5.7 Hashdive / Whale Check** | Куда идут **крупные деньги**? |

Hashdive (переехал в **Unusual Whales Predictions**) — источник данных о крупных игроках.  
**Не** главное доказательство прогноза. Вспомогательный сигнал, max **~10%** веса на PP.

---

## Место в pipeline

```text
5.6 Polymarket Analytics Check   → externalMarketCheck
5.7 Hashdive Whale Check         → whaleCheck
6.  Карта противоречий
```

**Код MVP:** `backend/src/agents/whale_check.py`

---

## Контракт `whaleCheck`

```json
{
  "lookupStatus": "found|not_found|similar_found|error|not_supported",
  "sourceName": "Hashdive / Unusual Whales Predictions",
  "eventUrl": "https://polymarket.com/event/...",
  "hashdiveUrl": "https://hashdive.com/market/...",
  "status": "ready|no_data|insufficient",
  "whaleLean": "yes|no|neutral|mixed",
  "mainVerdict": "yes_leaning|no_leaning|neutral|against_market|no_data",
  "headlineRu": "Киты идут против рынка",
  "yesWhaleVolumeUsd": 84000,
  "noWhaleVolumeUsd": 11000,
  "netWhalePressureUsd": 73000,
  "skewStrength": "weak|medium|strong",
  "againstMarket": true,
  "againstCrowd": false,
  "explanationRu": "За последние 24 часа…",
  "summaryRu": "Короткий вывод",
  "forecastImpact": "moderate_positive|weak_negative|neutral|…",
  "weightPct": 5,
  "maxWeightPct": 10,
  "passToRiskOfficer": ["thin_market_whale_entry", "whales_vs_market"],
  "contradictionHints": ["whales_vs_market", "whales_vs_crowd", "whales_vs_pp"],
  "dataSource": "hashdive_stub",
  "scoringMode": "mock_v1|stub_v0"
}
```

### mainVerdict → UI headline

| mainVerdict | headlineRu |
|-------------|------------|
| `yes_leaning` | Киты скорее за YES |
| `no_leaning` | Киты скорее за NO |
| `neutral` | Без явного сигнала |
| `against_market` | Киты идут против рынка |
| `no_data` | Данных по крупным игрокам нет |

### Вес на прогноз (ориентир)

| Сигнал | weightPct |
|--------|-----------|
| слабый | 0–3% |
| средний | 3–7% |
| сильный | 7–10% |
| киты против рынка + низкая ликвидность | до 10%, только после Risk Officer |

---

## Связи с другими блоками

**+ Polymarket Analytics:** тонкий рынок + крупный вход китов → `passToRiskOfficer: thin_market_whale_entry`

**+ Crowd Pulse:** люди YES, киты NO → `contradictionHints: whales_vs_crowd`

**+ Contradiction Map:** `whales_vs_market`, `whales_vs_pp`, `whales_aligned`

---

## UI (Simple open card)

Блок **«Крупные игроки»** — подзаголовок «Проверяем, куда идут крупные деньги…»

Рендер: `renderWhaleCheckSection()` в `simple-open-card.js`.

**Правила UX:**

- Не писать «киты знают правду».
- Массовая ЦА: «Крупные игроки»; «киты» — в скобках при необходимости.
- `against_market` — подсветка как важное противоречие.

---

## MVP / заглушки

| Компонент | Статус |
|-----------|--------|
| Hashdive / UW Predictions API | ❌ stub |
| Tesla `live-79061` mock | ✅ |
| UI open card | ✅ |
| Contradiction Map auto-wire | ❌ |
| Risk Officer auto-flags | ❌ |
| Probability Engine weight | ❌ |

### Следующие шаги для live-подключения

1. API-ключ Unusual Whales Predictions / Hashdive → `.env`
2. HTTP-клиент: поиск события по slug / conditionId
3. Парсинг whale volumes, net pressure, lean
4. Rule engine: `mainVerdict`, `againstMarket`, `againstCrowd`
5. Убрать `hashdive_stub`, оставить контракт и UI
