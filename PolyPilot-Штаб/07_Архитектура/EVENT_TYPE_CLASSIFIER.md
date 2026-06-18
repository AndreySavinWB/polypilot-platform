# Event Type Classifier — классификатор типа события

> [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[MARKET_STRUCTURE_ANALYZER]]

> **Версия:** `pie_v1.3`  
> **Статус:** 📐 зафиксирован на бумаге  
> **Дата:** 9 июня 2026

---

## Зачем этот блок

Event Normalizer делает событие понятным: переводит, находит условие резолва, считает горизонт.

Но после Normalizer система ещё не знает **что именно** она анализирует.

> Выборы анализируются не так, как решение ФРС.  
> Криптособытие требует других источников, чем судебное дело.

**Event Type Classifier решает:**
- Какие источники искать в Evidence Collector
- Какие правила применять в Contradiction Engine
- Какие аналоги искать в Comparable Events
- Какие факторы риска учитывать в Risk Officer

---

## Место в pipeline

```
Event Normalizer
      ↓
[Event Type Classifier]   ← этот блок
      ↓
Market Intelligence
```

---

## Вход и выход

### Вход

| Поле | Откуда | Описание |
|------|--------|----------|
| `titleRu` | Normalizer | Название события на русском |
| `resolutionCriteria` | Normalizer | Условие завершения |
| `decisionMaker` | Normalizer | Кто решает (UMA, official source) |
| `horizonDays` | Normalizer | Горизонт в днях |
| `rawQuestion` | Scanner | Оригинальный вопрос с Polymarket |

### Выход

```json
{
  "eventType": "elections",
  "subType": "us_presidential",
  "classifierConfidence": 92,
  "analysisProfile": {
    "prioritySources": ["polls", "election_history", "prediction_markets"],
    "riskFactors": ["poll_variance", "turnout_uncertainty", "legal_challenges"],
    "comparableCategory": "elections_national",
    "contradictionRules": ["polls_vs_market", "early_vote_vs_narrative"]
  }
}
```

---

## Типы событий и профили анализа

### Политика / Выборы

| | |
|---|---|
| **eventType** | `elections` |
| **subType** | `us_presidential`, `us_senate`, `eu_national`, `other` |
| **Источники** | Опросы (538, RealClear), рейтинги, история выборов, явка |
| **Аналоги** | Прошлые выборы той же страны / уровня |
| **Риск-факторы** | Дисперсия опросов, подавление явки, юридические вызовы |
| **Противоречие** | Опросы показывают одно, рынок — другое |

---

### Решения регуляторов

| | |
|---|---|
| **eventType** | `regulatory` |
| **subType** | `fed_rate`, `sec_ruling`, `cftc`, `ecb`, `other_central_bank` |
| **Источники** | CME FedWatch, CPI/PCE, рынок труда (NFP), облигации |
| **Аналоги** | Прошлые заседания того же регулятора |
| **Риск-факторы** | Инфляционный сюрприз, нетипичная риторика |
| **Противоречие** | FedWatch говорит одно, рынок PM — другое |

---

### Крипта

| | |
|---|---|
| **eventType** | `crypto` |
| **subType** | `etf_approval`, `exchange_event`, `protocol_upgrade`, `liquidation_event`, `regulation` |
| **Источники** | On-chain (Unusual Whales, Analytics), ETF flows, биржевые объёмы, ликвидации |
| **Аналоги** | Прошлые ETF решения, аналогичные апгрейды сети |
| **Риск-факторы** | Манипуляция, тонкий рынок, регуляторный сюрприз |
| **Противоречие** | On-chain накопление + медвежьи новости |

---

### Экономика / Макро

| | |
|---|---|
| **eventType** | `economics` |
| **subType** | `inflation`, `gdp`, `employment`, `trade`, `recession` |
| **Источники** | BLS, BEA, Bloomberg, Reuters, облигации, expectations |
| **Аналоги** | Прошлые публикации того же индикатора |
| **Риск-факторы** | Ревизии данных, политическое давление |
| **Противоречие** | Опережающие индикаторы против consensus |

---

### Спорт

| | |
|---|---|
| **eventType** | `sports` |
| **subType** | `championship`, `match`, `tournament`, `individual` |
| **Источники** | Букмекеры, статистика команд, травмы, форма |
| **Аналоги** | Исторические встречи тех же команд |
| **Риск-факторы** | Неожиданные составы, погода, форс-мажор |
| **Противоречие** | Спортивная статистика против рыночной ставки |

---

### Технологии / Корпоративные

| | |
|---|---|
| **eventType** | `corporate` |
| **subType** | `earnings`, `merger`, `product_launch`, `legal`, `leadership` |
| **Источники** | SEC filings, Bloomberg, Reuters, отраслевые аналитики |
| **Аналоги** | Прошлые отчёты той же компании / аналогичные M&A |
| **Риск-факторы** | Утечки, инсайд, неожиданный guidance |
| **Противоречие** | Analyst consensus против рыночной цены |

---

### Геополитика / Военные события

| | |
|---|---|
| **eventType** | `geopolitics` |
| **subType** | `conflict`, `diplomacy`, `sanctions`, `treaty` |
| **Источники** | Reuters, AP, официальные заявления, разведывательные сводки (open) |
| **Аналоги** | Исторические прецеденты похожих конфликтов / переговоров |
| **Риск-факторы** | Информационная война, пропаганда, высокий stale risk |
| **Противоречие** | Официальные заявления против рыночной реакции |

---

### Судебные решения

| | |
|---|---|
| **eventType** | `legal` |
| **subType** | `supreme_court`, `federal_court`, `criminal`, `civil` |
| **Источники** | Официальные судебные документы, юридические аналитики, PACER |
| **Аналоги** | Аналогичные дела того же суда |
| **Риск-факторы** | Процессуальные задержки, апелляции, неожиданная позиция судьи |
| **Противоречие** | Юридический консенсус против рыночной оценки |

---

## Как классифицируем (MVP v1)

**Метод v1 — rule + keyword:**

```text
1. Keyword matching по titleRu + rawQuestion (список триггеров на каждый тип)
2. Проверка decisionMaker (UMA → широкий класс; official source → regulatory/legal)
3. Если confidence < 60 → eventType = "other", профиль общий
```

**Метод v2 (после Memory):**
- LLM classification с few-shot примерами
- Calibration из Autopsy (где классификатор ошибался)

---

## Что НЕ делает этот блок

- ❌ Не ищет новости
- ❌ Не считает вероятность
- ❌ Не оценивает риск
- ❌ Не меняет `titleRu` или `resolutionCriteria`

---

## Влияние на нижние блоки

| Блок | Как использует eventType |
|------|--------------------------|
| Market Intelligence | Выбирает нужные API (on-chain для crypto, FedWatch для regulatory) |
| Evidence Collector | Приоритизирует источники по `analysisProfile.prioritySources` |
| Comparable Events | Фильтрует аналоги по `comparableCategory` |
| Risk Officer | Добавляет event-specific risk flags из `riskFactors` |

---

## Definition of Done

- [ ] Основатель прочитал — профили типов не вызывают вопросов
- [ ] Понятно, что `classifierConfidence < 60` означает `eventType = "other"`
- [ ] Место в pipeline зафиксировано: после Normalizer, до Market Intelligence

---

← [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[MARKET_STRUCTURE_ANALYZER]] · [[SOURCE_SCORING_SYSTEM]]
