# PIE v1.2 — Финальная архитектура PolyPilot

> ⚠️ **Архив** (`99_Архив/`). Redirect: [[PIE_V1_2_ФИНАЛЬНАЯ_АРХИТЕКТУРА]]. Актуально: [[PROBABILITY_INTELLIGENCE_ENGINE]] v1.3.

> **Версия:** `pie_v1.2`  
> **Статус:** 🛑 архив — заменён v1.3  
> **Дата:** 9 июня 2026

---

## 1. Что такое PIE

**PIE (Probability Intelligence Engine)** — мозг PolyPilot.

Это мясорубка, через которую проходит каждое событие с Polymarket, прежде чем попасть на сайт.

Мясорубка отвечает на один вопрос:

> **Где рынок ошибается — и насколько мы в этом уверены?**

Мясорубка не пишет новости. Не делает советы. Не угадывает. Она собирает факты, смотрит на деньги, ищет противоречия — и считает вероятность по формуле с компонентами.

**Что есть сейчас в коде:**  
Priority Agent + один большой LLM-промпт. Это не мясорубка. Это заготовка.

**Что строим:**  
Полную цепочку из 11 модулей, разделённых на 5 уровней.

---

## 2. Пять уровней системы

```
Уровень 1 · СОБЫТИЕ      ← что торгуем и как резолвится?
     ↓
Уровень 2 · ДЕНЬГИ       ← что делают участники рынка?
     ↓
Уровень 3 · ИНФОРМАЦИЯ   ← что говорит мир снаружи?
     ↓
Уровень 4 · МЫШЛЕНИЕ     ← где edge и какой риск?
     ↓
Уровень 5 · ПАМЯТЬ        ← что мы предсказывали и где ошиблись?
```

Между уровнями 3 и 4 всегда работает **сквозной слой качества**: проверка источников, дедупликация, свежесть данных.

---

## 3. Агенты внутри каждого уровня

### Уровень 1 · Событие

| Агент | Зачем |
|-------|-------|
| **Market Scanner** | Берёт события из Polymarket, отдаёт список кандидатов |
| **Priority Gate** | Отсекает мусор по жёстким правилам — до любого LLM |
| **Event Normalizer** | Делает событие понятным: переводит на RU, находит условие резолва, считает горизонт |

Без `accepted` от Priority Gate событие не идёт дальше.

---

### Уровень 2 · Деньги

| Агент | Зачем |
|-------|-------|
| **Market Intelligence Agent** | Смотрит, что делают деньги на рынке: киты, аномалии, flow |

Это отдельный уровень, не часть новостей. Нейтральные новости и массовая покупка YES китами — разные сигналы.

---

### Уровень 3 · Информация

| Агент | Зачем |
|-------|-------|
| **Evidence Collector** | Собирает верифицируемые факты: новости, Google Trends, X |

---

### Уровень 4 · Мышление

| Агент | Зачем |
|-------|-------|
| **Contradiction Engine** | Находит расхождения: рынок vs факты vs flow |
| **Comparable Events** | Ищет похожие прошлые события и их исходы |
| **Probability Engine** | Считает PP Probability по формуле с 7 компонентами |
| **Risk Officer** | Оценивает риск ошибиться и риск данных |
| **Verdict Agent** | Пишет человекочитаемый итог на русском |

Порядок внутри уровня важен: сначала Contradiction и Comparable, потом Probability, потом Risk, потом Verdict.

---

### Уровень 5 · Память

| Агент | Зачем |
|-------|-------|
| **Publishing** | Проверяет gates и публикует карточку на сайт |
| **Memory** | Хранит прогноз и результат, считает Brier score после резолва |
| **Autopsy** | Подмодуль Memory: разбирает ошибки, пишет теги |

Память — единственное, что делает систему обучающейся. Без неё веса Probability Engine никогда не улучшатся.

---

## 4. Источники данных

### Уровень 2 · Деньги (Market Intelligence)

| Источник | Что даёт | v1 |
|----------|----------|----|
| **Polymarket Analytics** | История цены, объёмы, движение вероятности | ✅ включаем |
| **Unusual Whales** | Крупные сделки, аномалии | ✅ включаем |
| Polymarket Whales tracker | Топ-кошельки, PnL | → v1.1 |
| Dune Analytics | Дашборды on-chain | → v1.1 |
| Arkham | Движение денег on-chain | → v2 |
| Nansen | Smart Money, фонды | → v2 (дорого) |

### Уровень 3 · Информация (Evidence Collector)

| Источник | Что даёт | v1 |
|----------|----------|----|
| **News API / RSS** | Новости tier A/B с URL | ✅ включаем |
| **Google Trends** | Поисковый интерес, delta | ✅ включаем |
| **X Search API v2** | Narrative, тренды | ✅ включаем |
| Reddit | Обсуждения | → v1.1 |
| YouTube | Транскрипты | → v2 |
| Официальные источники gov | Пресс-релизы, суды | → v1.1 для geo |

### Память (Memory)

| Хранилище | v1 |
|-----------|-----|
| **PostgreSQL** | ✅ — track record, версии, autopsy |
| pgvector / embeddings | ❌ — не в v1 |

---

## 5. Входы и выходы каждого блока

### Market Scanner

- **Вход:** Polymarket Gamma API
- **Выход:** список `rawEvent` — сырые события из пула

---

### Priority Gate

- **Вход:** `rawEvent`
- **Выход:** `priority` — decision: `accepted` / `watchlist` / `rejected`, score 0–100
- **Если `rejected`:** pipeline останавливается

Hard gates (без LLM):

| Критерий | Порог |
|----------|-------|
| Ликвидность | ≥ $5K |
| Объём total | ≥ $25K |
| Объём 24ч | ≥ $500 |
| Горизонт | 1–540 дней |
| Цена | не <2% и не >98% |
| Описание | ≥ 80 символов |

---

### Event Normalizer

- **Вход:** `rawEvent` + `priority`
- **Выход:** блоки `normalized` + `marketSnapshot`

`normalized` содержит:
- `titleRu` — название на русском
- `resolutionCriteria` — что должно произойти для YES
- `decisionMaker` — кто решает (UMA, official source)
- `horizonDays` — сколько дней до резолва
- `flags` — `resolution_unclear`, `missing_end_date`

`marketSnapshot` содержит:
- `marketProb` — текущая вероятность в %
- `volume24h`, `liquidity`, `spread`, `priceChange24h`

**Если `resolution_unclear`:** статус `research_required`, дальше не идёт.

---

### Market Intelligence Agent

- **Вход:** `normalized` + `marketSnapshot` + MI APIs
- **Выход:** блок `marketIntelligence`

Содержит:
- `whaleSignal` — `neutral` / `accumulation_yes` / `accumulation_no` / `mixed` / `unknown`
- `confidence` — 0–100
- `smartMoneyBias` — `yes` / `no` / `none`
- `anomalies[]` — тип, описание, severity
- `sourcesUsed[]` — какие API дали данные

Если API недоступны: `whaleSignal = unknown`, компонент в Probability Engine обнуляется.

---

### Evidence Collector

- **Вход:** `normalized` (titleRu → поисковые запросы)
- **Выход:** блок `evidence`

Содержит:
- `news[]` — источник, дата, утверждение, tier (A/B/C), URL
- `trends[]` — запрос, индекс, delta за 7 дней
- `social[]` — платформа X, сигнал, sentiment
- `quality` — sourcesCount, freshnessHours

Правила качества (сквозной слой):
- Источник без URL → не принимается
- Новость старше 72ч → downweight
- Дублирующиеся утверждения → merge

---

### Comment Analysis (5.5A / 5.5B / 5.5C)

- **Вход:** `normalized` + контекст `evidence`
- **Выход:** блок `crowdPulse` (см. [[COMMENT_ANALYSIS_V1]])

Содержит три **отдельных** блока:
- `marketComments` (5.5A) — комментарии под событием Polymarket
- `socialDiscussion` (5.5B) — X, Reddit, YouTube, Telegram, медиа
- `synthesis` (5.5C) — сравнение A и B, max weight 10% на probability

MVP: mock для event `79061`; API collectors — заглушки.

---

### Contradiction Engine

- **Вход:** `marketSnapshot` + `marketIntelligence` + `evidence`
- **Выход:** `contradictionMap[]`

Каждое противоречие содержит: тип, что говорит рынок, что говорит другой сигнал, severity.

Примеры правил v1:

| Ситуация | Тип |
|----------|-----|
| Whale YES + нейтральные новости | `flow_without_news` |
| Вероятность растёт + Trends flat | `market_vs_trends` |
| Цена стоит + накопление YES | `price_vs_mi` |
| Нет новостей >72ч при высоком объёме | `stale_evidence` |

---

### Comparable Events

- **Вход:** `normalized` + `evidence` + данные из Memory
- **Выход:** `analogs[]` — до 5 штук

Каждый аналог содержит: ID, название, исход, оценку схожести, base rate.

Поиск аналогов в v1: по категории + ключевым словам + bucket горизонта.

---

### Probability Engine

- **Вход:** все блоки выше
- **Выход:** блок `probability`

Содержит:
- `ppProb` — PP вероятность 0–100
- `marketProb` — цена рынка
- `edgePp` — разница ppProb − marketProb
- `components{}` — разбивка по всем 7 источникам

**Формула:**

```
ppProb = clamp(
  0.30 × market_base
  0.15 × whale_signal
  0.22 × news_signal
  0.08 × social_signal
  0.12 × trends_signal
  0.08 × historical_base_rate
  0.05 × contradiction_adjustment
, 2%, 98%)
```

Если компонент не получил данные → вес = 0, флаг `component_missing`.

Edge показывается, только если:
- ≥ 5 pp разницы
- И есть хотя бы 1 verified fact ИЛИ `whaleSignal` с confidence ≥ 70

---

### Risk Officer

- **Вход:** весь `pipelinePackage`
- **Выход:** блок `risk` — `riskLevel`, `riskScore`, `flags[]`

Уровни: `low` (0–33) / `medium` (34–66) / `high` (67+)

Факторы риска:

| Фактор | Что проверяем |
|--------|---------------|
| Ликвидность | < $5K = high risk |
| Резолв | `resolution_unclear` flag |
| Качество данных | stale news, мало источников |
| Flow без новостей | whale YES + neutral news |
| Тонкий рынок + кит | liquidity < $10K + whale > 20% vol |
| Разброс компонентов | большие отклонения в Probability |

LLM в Risk Officer v1: только формулирует `flags[]` на русском из уже посчитанных факторов. Не придумывает риски сам.

---

### Verdict Agent

- **Вход:** `probability` + `risk` + краткое summary `contradictionMap`
- **Выход:** блок `verdict` — 2–4 предложения на русском + `status` + `confidence`

Статусы: `ready` / `research_required` / `rejected`

Verdict Agent не пересчитывает вероятность. Он только объясняет, что посчитал Probability Engine.

---

### Publishing

- **Вход:** весь `pipelinePackage`
- **Выход:** карточка на сайт (`events-live.js`, API)

**Событие НЕ публикуется, если:**
- `riskLevel = high` и `confidence < 60`
- `status = research_required` и нет 2 verified news
- edge выдуман без evidence
- `|ppProb − marketProb| < 3pp` и нет contradiction и `whaleSignal = neutral`

---

### Memory

- **Вход после публикации:** `liveCard` → запись в БД
- **Вход после резолва:** outcome от Polymarket → расчёт Brier score
- **Выход:** исторические данные для Comparable + Autopsy + калибровка весов

**Autopsy v1:** теги ошибок — `missed_whale_signal`, `overconfident`, `stale_news`, `bad_resolution`. Без LLM-эссе.

---

## 6. MVP-версия каждого блока

| Блок | v1 включает | v1 НЕ включает |
|------|-------------|----------------|
| Market Scanner | Gamma API, rubric_v1 | Kalshi, Metaculus |
| Event Normalizer | titleRu, резолв, горизонт, decisionMaker | сложные мульти-outcome рынки |
| Market Intelligence | Polymarket Analytics, Unusual Whales | Nansen, Arkham, Dune |
| Evidence Collector | News API, Google Trends, X Search | Reddit, YouTube, gov scrapers |
| Contradiction Engine | 4–5 rule-based правил | ML-модель, граф противоречий |
| Comparable Events | PostgreSQL + keyword + category | pgvector, RAG, embeddings |
| Probability Engine | формула с 7 компонентами, components в JSON | авто-калибровка без track record |
| Risk Officer | rules + LLM только для формулировки RU | отдельная ML-модель |
| Verdict Agent | LLM summary из structured inputs | свободный narrative |
| Publishing | pre-publish gate + events-live.js | tier API blur |
| Memory | PostgreSQL: predictions + resolutions | pgvector, embeddings |

---

## 7. Что НЕ делаем в v1

Это не список «забыли». Это сознательные решения.

**Данные:**
- ❌ Nansen, Arkham — дорого и избыточно для старта
- ❌ Dune Analytics — полезно, но не критично для v1
- ❌ Reddit, YouTube — шум, сложная фильтрация
- ❌ Официальные gov-источники — нужны отдельные scrapers, риск нестабильности
- ❌ Kalshi, Metaculus — PM достаточно для v1

**Технологии:**
- ❌ pgvector / embeddings — оверкилл без 1000+ прогнозов в базе
- ❌ RAG — нужна качественная история, которой пока нет
- ❌ Redis / Kafka — один harvest worker справляется
- ❌ Отдельные микросервисы — монолит проще на старте
- ❌ Bayesian full model для вероятности — формула с весами достаточно

**Процессы:**
- ❌ Авто-калибровка весов без track record — нечего калибровать
- ❌ Autopsy LLM-эссе — теги ошибок достаточно для v1
- ❌ Квартальный review весов до первых 50 прогнозов

---

## 8. DoD — когда архитектура готова к backend

Начинаем писать первый код только после того, как выполнены все пункты:

- [ ] Основатель прочитал этот документ целиком — нет вопросов по цепочке
- [ ] Понятно, что делает каждый блок и что он **не** делает
- [ ] Понятны STOP-условия: когда событие не идёт дальше
- [ ] Согласована MVP-таблица (раздел 6) — нет блоков «добавим потом, не записывая»
- [ ] Первый кодовый блок: **Event Normalizer** (не Market Intelligence, не Memory)
- [ ] Порядок реализации принят: Normalizer → MI → Evidence → Contradiction → Probability → Memory → Comparable → Autopsy

**После ОК:** открываем `backend/src/agents/` и пишем `normalizer.py`.

---

## Порядок реализации

```
1 · Event Normalizer            ← первый
2 · Market Intelligence v0
3 · Evidence Collector v0
4 · Contradiction Engine v0
5 · Probability Engine v0
6 · Memory (PostgreSQL)
7 · Comparable Events v0
8 · Autopsy tags
```

Risk Officer и Verdict Agent улучшаются параллельно с каждой фазой (сейчас ⚠️ LLM — постепенно заменяем на rules + structured).

---

← [[ДОМ_ШТАБ]] · [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[INTELLIGENCE_ENGINE_MVP]] · [[INTELLIGENCE_DATA_FLOW]]
