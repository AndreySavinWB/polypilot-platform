# Intelligence Engine — MVP v0 каждого блока

> [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[INTELLIGENCE_DATA_FLOW]] · [[AI_ARCHITECTURE_V1]]

> **Статус:** ✅ зафиксирован — ОК основателя 9 июня 2026  
> **Принцип:** v0 = минимум, который даёт **настоящую** intelligence, без «10 сервисов на старте»

---

## Зачем MVP v0

| Без MVP | С v0 |
|---------|------|
| Nansen + Arkham + RAG + векторы «на потом забыли» | Явно: **в v0** / **не в v0** |
| Переделка pipeline | Каждый блок расширяется, не ломается |

---

## Сводная таблица v0

| Блок | v0 включает | v0 **не** включает | Фаза кода |
|------|-------------|-------------------|-----------|
| Market Scanner | Gamma API, Priority `rubric_v1` | Kalshi, Metaculus | ✅ есть |
| Event Normalizer | резолв RU, horizon, decisionMaker, marketSnapshot | LLM-перевод сложных мульти-рынков | **1-й код** |
| Market Intelligence | Polymarket Analytics, Unusual Whales | Nansen, Arkham, Dune, LunarCrush | 2-й |
| Evidence Collector | News API, Google Trends, X Search | Reddit full, YouTube, Telegram | 3-й |
| Contradiction Engine | rule-based lite (3–5 правил) | ML, graph UI | 4-й |
| Comparable Events | PostgreSQL: прошлые PP + PM archive query | векторный поиск, RAG | 4-й |
| Probability Engine | формула v1.1, компоненты в JSON | auto-calibration без track record | 5-й |
| Risk Officer | rules + LLM flags RU | отдельная ML-модель | с Normalizer |
| Verdict Agent | LLM summary из structured inputs | свободный narrative | ✅ есть ⚠️ |
| Publishing | harvest → events-live.js | Railway prod | ✅ есть |
| Memory | PostgreSQL: track record, versions | pgvector, RAG, embeddings | 6-й |

---

## 1. Market Scanner v0 ✅

**Включает:**
- Polymarket Gamma API
- Priority Agent `rubric_v1` (hard gates + score)

**Не включает:**
- Polymarket Scan как отдельный продукт (логика scan → позже в MI)
- Kalshi / Metaculus

**Выход v0:** `rawEvent` + `priority`

---

## 2. Event Normalizer v0

**Включает:**
- `titleRu` — из title/question (LLM только если EN и нужен короткий RU, иначе rule)
- `resolutionCriteria` — из description + market question
- `horizonDays` — из endDate
- `decisionMaker` — эвристика (Polymarket UMA / explicit source в тексте)
- `marketSnapshot` — marketProb, volume24h, liquidity, spread
- flags: `resolution_unclear`, `missing_end_date`

**Не включает:**
- QA всех мульти-outcome рынков
- Автоматический перевод court docs

**Выход v0:** объект `normalized` (см. [[INTELLIGENCE_DATA_FLOW]])

---

## 3. Market Intelligence v0

**Включает только:**
| Сервис | Даёт |
|--------|------|
| **Polymarket Analytics** | объёмы, история цены, движение prob |
| **Unusual Whales** | крупные сделки, аномалии (где доступно для PM) |

**Не включает v0:**
- ❌ Nansen
- ❌ Arkham  
- ❌ Dune (→ v1)
- ❌ Polymarket Whales отдельный трекер (→ v0.1 если API простой)
- ❌ Polymarket Scan (→ v0.1)

**Выход v0:** `marketIntelligence` с полями:
- `whaleSignal`: neutral | accumulation_yes | accumulation_no | mixed | unknown
- `confidence`: 0–100
- `anomalies[]` (lite)
- `sourcesUsed[]`

**Whale Intelligence Agent v0:** rule + API aggregation, **не** LLM «угадай китов».

---

## 4. Evidence Collector v0

**Включает только:**
| Источник | v0 |
|----------|-----|
| **News API** | RSS / NewsAPI tier — tier A/B факты |
| **Google Trends** | query из titleRu, delta index |
| **X Search** | API v2 basic — narrative, не полный sentiment ML |

**Не включает v0:**
- Reddit API full crawl
- YouTube transcripts
- Official gov scrapers (→ v0.1 для geo/politics)
- LLM-generated facts без URL

**Выход v0:** `evidence` с `news[]`, `trends[]`, `social[]` (X only), `quality.sourcesCount`

---

## 4.5 Comment Analysis v0 (5.5A / 5.5B / 5.5C)

**Отдельно от Evidence Collector.** Не смешивать комментарии Polymarket и соцсети.

| Блок | v0 |
|------|-----|
| 5.5A Polymarket comments | stub / mock |
| 5.5B Social (X, Reddit, YouTube, Telegram, news) | stub / mock |
| 5.5C Synthesis | rule + mock RU summary |

**Выход:** `crowdPulse` — см. [[COMMENT_ANALYSIS_V1]]  
**Вес на PP:** max 10% (вспомогательный сигнал)  
**Код:** `backend/src/agents/comment_analysis.py` · UI mock `live-79061`

---

## 5. Contradiction Engine v0

**Rule-based lite (без LLM):**

| Правило | Пример |
|---------|--------|
| flow vs news | whale YES + neutral news → flag |
| market vs trends | prob ↑ + trends flat |
| market vs MI | price flat + accumulation_yes |
| stale evidence | нет news >72h при high vol |

**Выход v0:** `contradictionMap[]` — type, description, severity

**Не v0:** полный graph UI, LLM contradiction essay

---

## 6. Comparable Events v0

**Включает:**
- PostgreSQL таблица `pp_events` + `pp_predictions`
- Поиск аналогов: **category + keyword overlap + horizon bucket**
- Base rate из resolved PM markets (manual seed + API archive)

**Не включает v0:**
- ❌ pgvector / embeddings
- ❌ RAG
- ❌ автоматический crawl 10 лет истории

**Выход v0:** `analogs[]` max 5 штук, similarity score rule-based

---

## 7. Probability Engine v0

**Включает:**
- Формула [[AI_ARCHITECTURE_V1]] §4.2 (все 7 компонентов)
- `components{}` в JSON — воспроизводимость
- `edgePp` = ppProb − marketProb
- enforce: edge только при gates §3.4

**Не включает v0:**
- Авто-перекалибровка весов (нужен Memory + autopsy)
- Bayesian full model

**Компоненты без данных → weight 0, flag `component_missing`**

---

## 8. Risk Officer v0

**Structured rules (обязательно):**
- liquidity / volume (из Priority)
- resolution_unclear (из Normalizer)
- whale flow без news (из Contradiction)
- thin market + whale (MI + snapshot)
- component_missing в Probability

**LLM v0:** только формулировка flags[] на RU **из уже посчитанных факторов**, не invent risk

**Выход v0:** `riskLevel`, `riskScore`, `flags[]`

---

## 9. Verdict Agent v0

**Включает:**
- LLM: 2–4 предложения RU из **structured package** (ppProb, edge, top contradiction, risk)
- `status`: research_required | ready | rejected

**Не включает:**
- Свободный пересчёт вероятности
- Buy/sell language

---

## 10. Publishing v0 ✅

**Включает:**
- Pre-publish gate (rules из AI_ARCHITECTURE §3.4)
- `events-live.js` + optional Railway API

**Не v0:** tier-based field blur на API (UI уже есть mock)

---

## 11. Memory v0

**Storage:** **PostgreSQL only**

**Таблицы v0:**
```text
predictions     — recordId, eventId, publishedAt, marketProb, ppProb, verdict, riskLevel, edgePp, modelVersion
resolutions     — recordId, resolvedAt, outcome, brierScore, errorTags[]
agent_versions  — pipeline snapshot per publish
```

**Не включает v0:**
- ❌ pgvector
- ❌ RAG / embeddings
- ❌ Autopsy LLM essay (→ v0.1: one-line lesson)

**Autopsy v0:** rule tags only (`missed_whale_signal`, `overconfident`, …)

---

## Infrastructure v0 (под Memory)

| Компонент | v0 |
|-----------|-----|
| PostgreSQL | Railway Postgres **или** local Docker |
| Backend | Python API, один worker harvest |
| Secrets | POLZA_API_KEY, NEWS_API_KEY, DB_URL |

**Не v0:** Redis queue, Kafka, separate MI microservice

---

## Порядок реализации (после DoD документов)

```text
1 Event Normalizer
2 Market Intelligence v0 (Analytics + Unusual Whales)
3 Evidence Collector v0 (News + Trends + X)
4 Contradiction lite
5 Probability Engine v0
6 Memory PostgreSQL
7 Comparable lite
8 Autopsy tags
```

---

## Definition of Done — MVP doc ✅

**Закрыто:** 9 июня 2026.

- [x] MI v0 = Polymarket Analytics + Unusual Whales (не 10 сервисов)
- [x] Evidence v0 = News + Trends + X
- [x] Memory v0 = PostgreSQL без векторов / RAG
- [x] Порядок реализации принят

---

← [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[INTELLIGENCE_DATA_FLOW]]
