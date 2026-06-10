# AI Architecture V1 — Intelligence Pipeline PolyPilot

> [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[INTELLIGENCE_ENGINE_MVP]] · [[INTELLIGENCE_DATA_FLOW]] · [[ДОМ_ШТАБ]] · [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]] · [[СХЕМА_МЯСОРУБКИ]] · [[АРХИТЕКТУРА_АГЕНТОВ]] · [[СХЕМА_ДАННЫХ_СОБЫТИЯ]] · [[ПРИОРИТЕТ_АГЕНТ]]

> **Реализация:** master pipeline → [[PROBABILITY_INTELLIGENCE_ENGINE]] · веса/gates → этот документ

> **Версия:** `intelligence_v1.1`  
> **Статус:** ✅ **зафиксирован** — DoD §11 закрыт, владелец согласовал 9 июня 2026  
> **Дата:** 9 июня 2026

---

## Зачем этот документ

Сейчас у PolyPilot есть:

- ✅ **красивая оболочка** (Vercel, карточки, War Room UI);
- ✅ **первичный фильтр** (Priority Agent `rubric_v1`, harvest, Polza);
- ⚠️ **pipeline в коде не реализован** — следующий шаг V1.0a (Normalizer)

**AI Architecture V1** — единый контракт: какие данные, какие агенты, какие проверки, как считаются вероятность и риск, что видит пользователь, что остаётся внутри. **Зафиксирован** 9 июня 2026.

Это **не код**. Это фундамент, по которому потом пишем агентов и подключаем источники.

---

## Одним абзацем

PolyPilot берёт событие с prediction market → **нормализует** → **разведывает поведение денег** (киты, аномалии, smart money) → **собирает информационные доказательства** (новости, social, trends) → **ищет противоречия и аналоги** → **считает PP Probability** → **оценивает риск** → **выдаёт вердикт** → **публикует карточку** → **память + autopsy** → обучение системы.

---

## Четыре уровня PP (целевая модель)

Не 9 отдельных «коробок», а **4 слоя разведки**:

| Уровень | Суть | Источники / модули |
|---------|------|-------------------|
| **1. Событие** | Что торгуем, резолв, горизонт | Polymarket, Kalshi, Metaculus · Scanner · Normalizer |
| **2. Деньги** | Поведение участников рынка | Whale Intelligence · Polymarket Analytics · Dune · Arkham · … |
| **3. Информация** | Факты и narrative снаружи | News · X · Reddit · Google Trends · YouTube · Official |
| **4. Мышление** | Оценка, риск, вердикт | Contradiction · Comparable · Probability · Risk · Verdict |

```text
Уровень 1 ──► Уровень 2 ──► Уровень 3 ──► Уровень 4 ──► Карточка
 Событие        Деньги         Информация     Мышление
```

**Ключевой инсайт:** новости могут быть нейтральными, а **деньги уже движутся** — это отдельный сигнал, не факт.

---

## Схема pipeline (V1)

```text
┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 1 — СОБЫТИЕ                                             │
│  1. Polymarket Scanner      ← пул, объём, ликвидность           │
│  1b. Priority Agent         ← gates + rubric_v1                 │
│  2. Event Normalizer        ← резолв, RU, горизонт              │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 2 — ДЕНЬГИ (Market Intelligence Layer)                  │
│  3. Whale Intelligence Agent ← поведение участников рынка       │
│     · киты, smart money, аномалии, перекос ликвидности            │
│     · Polymarket Analytics · Unusual Whales · Dune · …           │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 3 — ИНФОРМАЦИЯ                                          │
│  4. Evidence Collector      ← news · social · trends · official │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 4 — МЫШЛЕНИЕ                                            │
│  5. Contradiction Engine                                        │
│  6. Comparable Events Engine                                    │
│  7. Probability Model       ← market + whale + info + history   │
│  8. Risk Officer                                                │
│  9. Verdict Agent                                               │
│  ═══ Quality & Monitoring (сквозной слой) ═══                   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
        Product (Card) → Memory → Autopsy → Feedback
```

**Цепочка (коротко):**

```text
Market Scanner → Event Normalizer → Whale Intelligence Agent
  → Evidence Collector → Contradiction Engine → Probability Model
  → Risk Officer → Verdict Agent → Event Card
```

**Цикл обучения (feedback):**

```text
прогноз → событие завершилось → факт → сравнение → ошибки → веса → лучше
```

---

## 1. Какие данные собираем

### 1.1 Классы источников (целевая модель V1)

| # | Класс | Примеры | Зачем PP | Уровень |
|---|-------|---------|----------|---------|
| 1 | **Prediction markets** | Polymarket (P0), Kalshi, Metaculus | Цена, объём, резолв | 1 · Событие |
| 2 | **Market intelligence (деньги)** | Polymarket Analytics, Unusual Whales, Dune, Arkham | Поведение китов, smart money, аномалии | 2 · Деньги |
| 3 | **News & media** | RSS, Reuters/Bloomberg, Google News | Факты, триггеры | 3 · Информация |
| 4 | **Social & communities** | X, Reddit, Telegram, YouTube | Narrative, sentiment | 3 · Информация |
| 5 | **Search interest** | **Google Trends** (приоритет ↑) | Интерес до новостей | 3 · Информация |
| 6 | **Official sources** | gov, пресс-релизы, court docs | Ground truth резолва | 3 · Информация |
| 7 | **Historical data** | архив PM, PP memory, autopsy | Аналоги, base rates | 3–4 |
| 8 | **On-chain / macro** | Nansen, LunarCrush (крипто), календари | Кросс-check для crypto-событий | 2–3 |

### 1.2 Что уже есть в коде (июнь 2026)

| Данные | Источник | Статус |
|--------|----------|--------|
| Список событий, markets, prices | Polymarket Gamma API | ✅ без ключа |
| volume, liquidity, endDate, description | Gamma API | ✅ |
| Whale / smart money / flow | — | ❌ |
| Polymarket Analytics, Dune, Unusual Whales | — | ❌ |
| Новости, social, trends (real APIs) | — | ❌ LLM или mock |
| Official docs | — | ❌ |
| Track record / autopsy store | — | ❌ UI mock |

### 1.3 Минимальный пакет данных на одно событие (V1 contract)

Каждое событие после Normalizer должно иметь **Evidence Package**:

```json
{
  "eventId": "string",
  "normalized": { "titleRu", "resolutionCriteria", "horizonDays", "decisionMaker" },
  "marketSnapshot": { "marketProb", "volume24h", "liquidity", "priceChange24h", "spread" },
  "marketIntelligence": {
    "whaleSignal": "neutral|accumulation_yes|accumulation_no|mixed",
    "confidence": 0-100,
    "topWallets": [{ "address", "side", "sizeUsd", "windowHours" }],
    "anomalies": [{ "type", "description", "severity" }],
    "smartMoneyBias": "yes|no|none",
    "sourcesUsed": ["polymarket_analytics", "unusual_whales", "dune"]
  },
  "evidence": {
    "news": [{ "source", "date", "claim", "reliability" }],
    "social": [{ "platform", "signal", "sentiment" }],
    "trends": [{ "query", "index", "delta" }],
    "official": [{ "url", "claim" }],
    "historical": [{ "analogId", "outcome", "similarity" }]
  },
  "quality": { "sourcesCount", "freshnessHours", "contradictionsFound" }
}
```

---

## 2. Какие агенты нужны

### 2.1 Карта агентов pipeline V1

| # | Модуль | Роль | Вход | Выход | P |
|---|--------|------|------|-------|---|
| 1 | **Polymarket Scanner** | Скан пула, кандидаты | Gamma API | список raw events | P0 ✅ |
| 1b | **Priority Agent** | Фильтр + score | raw event | accepted/watchlist/rejected | P0 ✅ `rubric_v1` |
| 2 | **Event Normalizer** | Понятный резолв RU | raw event | normalized event | P0 ⬜ |
| **3** | **Whale Intelligence Agent** | **Поведение денег на рынке** | normalized + MI APIs | `marketIntelligence` package | **P0 ⬜ PRO-core** |
| 4 | **Evidence Collector** | Сбор информации | normalized + news/social APIs | evidence (info layer) | P0 ⬜ |
| 5 | **Contradiction Engine** | Почему рынок wrong | MI + evidence + market | contradiction map | P1 ⬜ |
| 6 | **Comparable Events Engine** | Исторические аналоги | evidence + memory | analogs[] | P1 ⬜ |
| 7 | **Probability Model** | PP Probability | all above incl. **whale_signal** | ppProb, components | P0 ⬜ |
| 8 | **Risk Officer** | Риски | all above | riskLevel, flags[] | P0 ⚠️ LLM-only |
| 9 | **Verdict Agent** | Итог для UX | all above | verdict, confidence | P0 ⚠️ LLM-only |
| 10 | **Publishing Agent** | Sync на сайт | verdict pipeline | events-live.js / API | P0 ✅ sync |
| 11 | **Monitoring Agent** | Изменения после публикации | live markets + whale flow | alerts, diffs | P2 ⬜ |
| 12 | **Memory / Track Record** | Хранение прогнозов | published card | track record DB | P1 ⬜ |
| 13 | **Autopsy Agent** | Разбор после резолва | outcome + memory | lesson, score | P2 ⬜ |

**Легенда:** ✅ реализовано · ⚠️ упрощённо · ⬜ только в архитектуре

### 2.2 Связь с текущим кодом

| V1 модуль | Сейчас в backend |
|-----------|------------------|
| Scanner + Priority | `priority.py`, `polymarket.py` |
| News Scout (часть Evidence) | один LLM-вызов в `pipeline.py` |
| Risk Officer | один LLM-вызов |
| Verdict Agent | один LLM-вызов |
| Normalizer, Whale Intelligence, Contradiction, Comparable, Probability | **нет** |
| Memory / Autopsy | **нет** |

> **Честный вывод:** сейчас это **Priority + один monolithic LLM prompt**, а не pipeline из диаграммы. **Уровень 2 (деньги) отсутствует полностью.**

### 2.3 Whale Intelligence Agent — Market Intelligence Layer (блок №3.5)

**Место в pipeline:** сразу после Event Normalizer, **до** Evidence Collector.

```text
Market Scanner → Event Normalizer → Whale Intelligence Agent → Evidence Collector → …
```

**Не путать с информацией.** Этот слой смотрит не событие и не новости, а **поведение денег**:

| Сигнал | Примеры |
|--------|---------|
| Крупные кошельки | топ-N адресов по объёму на рынке |
| Киты (Whales) | сделки > порога, кластеры покупок |
| Smart money | прибыльные аккаунты, copy-traders |
| Аномалии | резкий вход, перекос ликвидности, orderbook shift |
| Скрытое накопление | медленный drift позиции без движения цены |

**Вопросы агента на каждое событие:**

1. Что делают киты? (buy / sell / hold / mixed)
2. Что делают лучшие трейдеры?
3. Есть ли аномалии за окно (6h / 24h / 7d)?
4. Растёт ли «уверенность рынка» (volume + flow + spread)?
5. Есть ли скрытое накопление позиции?

**Выход:** блок `marketIntelligence` в Evidence Package → **в Probability Model**, не напрямую пользователю как «факт».

**Пример (типовой кейс):**

| Источник | Что говорит |
|----------|-------------|
| Polymarket | вероятность = **45%** |
| Новости | **нейтральные** |
| Whale Intelligence | **5 крупнейших кошельков массово покупают YES** за последние 6 ч |

→ это **сигнал**, не доказательство. Часто двигает рынок **раньше** новостей. PP учитывает его в `whale_signal`, Risk Officer может поднять flag «flow без news».

#### Сервисы Market Intelligence (приоритет подключения)

| Сервис | Роль | P | Обязательность |
|--------|------|---|----------------|
| **Polymarket Analytics** | История рынка, объёмы, цены, графики вероятности | **P0** | база, обязательно |
| **Unusual Whales** | Киты, крупные сделки, аномальная активность | **P0** | обязательно |
| **Polymarket Whales** | Трекеры кошельков: кто покупает/продаёт, топ PnL | **P0** | обязательно |
| **Polymarket Scan** | Новые рынки, всплески объёма, быстрые сдвиги prob | **P0** | полезно для Scanner + MI |
| **Dune Analytics** | Дашборды: кошельки, PnL, активность рынков | **P1** | для PP почти обязательно |
| **Arkham** | On-chain: движение денег, крупные адреса | **P1** | если рынок связан с криптой |
| **Nansen** | Smart Money, фонды, крупные игроки | **P2** | дорого; позже |
| **LunarCrush** | Social + trends для crypto-событий | **P2** | крипто-ниши |
| **Google Trends** | Поисковый интерес | **P0↑** | уже в Evidence; **вес выше**, чем social |

> **PRO-уровень PP** = Event + **Money layer** + Information + Thinking. Без Whale Intelligence это «обёртка над новостями», не разведка.

---

## 3. Какие проверки проходит событие

### 3.1 Этап A — Gate (до intelligence)

**Priority Agent Hard Gates** — см. [[ПРИОРИТЕТ_АГЕНТ]]. Без LLM.

| Gate | Порог |
|------|-------|
| Ликвидность | ≥ $5K |
| Объём total | ≥ $25K |
| Объём 24ч | ≥ $500 |
| Описание | ≥ 80 символов |
| endDate | есть |
| Горизонт | 1–540 дней |
| Цена | не ≤2% и не ≥98% |

**Rubric score:** ≥70 accepted · 55–69 watchlist · <55 rejected.

### 3.2 Этап B — Normalization checks

| Проверка | Fail → |
|----------|--------|
| Резолв понятен человеку | `resolution_unclear` → reject или research_required |
| Есть бинарный исход (или явная мульти-структура) | flag |
| Известен decision maker / источник резолва | missing в evidence |
| Перевод на RU без искажения смысла | QA flag |

### 3.3 Этап C — Evidence quality (сквозной слой)

**Data Quality & Monitoring System** — работает на каждом шаге:

| Проверка | Действие |
|----------|----------|
| Верификация источника | whitelist / tier (A/B/C) |
| Дедупликация | merge одинаковых claim |
| Свежесть | stale > 72h → downweight |
| Противоречие фактов | → Contradiction Engine |
| Шум / hype | → downweight social |
| Нет внешних данных | `research_required`, не показывать edge |

### 3.4 Этап D — Pre-publish gate

Событие **не попадает в live-блок**, если:

- `riskLevel = high` **и** confidence < 60;
- `status = research_required` **и** нет минимум 2 verified news facts;
- `edgeScore` выдуман без evidence (запрет в промпте — нужен enforce в коде);
- Probability Model: `|ppProb - marketProb| < 3pp` **и** нет contradiction map **и** `whaleSignal = neutral` → не «горячее».

### 3.5 Этап E — Market Intelligence checks (Уровень 2)

Проходит **после** Normalizer, **до** Evidence Collector:

| Проверка | Действие |
|----------|----------|
| Есть данные flow за окно 6h/24h | иначе `whaleSignal = unknown`, downweight в модели |
| Согласованность китов (≥3 из топ-5 в одну сторону) | `accumulation_yes/no` |
| Аномалия без подтверждения ценой | flag → Risk Officer |
| Flow против market prob (>10pp delta) | → Contradiction Engine input |
| Координированный pump (много мелких + 1 кит) | `manipulation_suspect` → Risk high |
| MI sourcesUsed пуст | не показывать whale teaser на сайте |

**Правило:** whale-сигнал **никогда** не заменяет verified news — только сдвигает PP_prob и поднимает внимание Monitoring Agent.

---

## 4. Как считается вероятность

### 4.1 Два числа на карточке

| Метрика | Источник | Показываем |
|---------|----------|------------|
| **Market Probability** | Polymarket `outcomePrices` | ✅ всегда (Guest+) |
| **PP Probability** | Probability Model | ✅ Pulse+ / PRO (или скрыто Guest) |

### 4.2 Probability Model V1.1 (формула-рамка)

```text
PP_prob = clamp(
  w_m * market_base
+ w_w * whale_signal
+ w_n * news_signal
+ w_s * social_signal
+ w_t * trends_signal
+ w_h * historical_base_rate
+ w_c * contradiction_adjustment,
  0.02, 0.98
)
```

**`whale_signal`** — нормализованный bias из `marketIntelligence` (−1…+1 → mapped to prob space).  
Пример: `accumulation_yes` + confidence 80 → сдвиг +8…+15 pp к YES относительно market_base.

**Стартовые веса (гипотеза V1.1, калибровать по track record):**

| Компонент | w | Откуда |
|-----------|---|--------|
| market_base | 0.30 | текущая цена PM |
| **whale_signal** | **0.15** | **Whale Intelligence Agent** |
| news_signal | 0.22 | Evidence Collector |
| social_signal | 0.08 | sentiment aggregate |
| trends_signal | 0.12 | Google Trends delta (↑ приоритет) |
| historical_base_rate | 0.08 | Comparable Events |
| contradiction_adjustment | 0.05 | Contradiction Engine |

> Пока в коде: **PP Probability ≈ LLM confidence / narrative** — это **заменить** на модель с компонентами.

### 4.3 Edge (перевес)

```text
edge_pp = PP_prob - market_prob   // в процентных пунктах
```

Показываем edge только если:

- ≥ 5 pp **и**
- Risk ≠ high **или** confidence ≥ 70 **и**
- есть ≥ 1 verified fact **или** `whaleSignal` ∈ {accumulation_yes, accumulation_no} с confidence ≥ 70

---

## 5. Как считается риск

### 5.1 Risk Officer — входы

| Фактор | Пример |
|--------|--------|
| Качество данных | мало источников, stale news |
| Ликвидность / объём | уже частично в Priority |
| Надёжность резолва | спорные формулировки |
| Уверенность модели | разброс компонентов PP_prob |
| Manipulation / hype | social без news |
| **Whale flow без news** | accumulation + neutral news → medium risk |
| **Координированный flow** | manipulation_suspect из MI |
| **Тонкий рынок + кит** | liquidity < $10K + whale > 20% vol |
| Горизонт | слишком далеко / близко |

### 5.2 Risk score → уровень

```text
risk_score = sum(factor_i * weight_i)   // 0–100

0–33  → low
34–66 → medium
67+   → high
```

### 5.3 Связь с UX

| riskLevel | Closed card | War Room | Edge visible |
|-----------|-------------|----------|--------------|
| low | зелёный акcent | полный | ✅ |
| medium | нейтральный | полный + flags | ✅ Pulse+ |
| high | предупреждение | flags prominent | edge скрыт или disclaimer |

---

## 6. Как ведётся история ошибок

### 6.1 Memory Layer (V1)

**Track Record Entry** — при каждой публикации live-карточки:

```json
{
  "recordId": "uuid",
  "eventId": "live-51456",
  "publishedAt": "ISO",
  "marketProbAtPublish": 44,
  "ppProbAtPublish": 57,
  "verdict": "string",
  "riskLevel": "medium",
  "edgePp": 13,
  "whaleSignalAtPublish": "accumulation_yes",
  "modelVersion": "intelligence_v1.1",
  "agentsVersion": "pipeline_2026-06-09"
}
```

**Resolution Update** — когда Polymarket resolved:

```json
{
  "recordId": "uuid",
  "resolvedAt": "ISO",
  "outcome": "yes|no",
  "marketProbAtResolve": 91,
  "ppWasCorrect": true,
  "brierScore": 0.12,
  "errorTags": ["overconfident", "missed_news", "missed_whale_signal", "bad_resolution"]
}
```

### 6.2 Autopsy Agent (после резолва)

Выход:

- кто был прав — рынок или PP;
- где ошиблись агенты (какой модуль);
- урок одной строкой для memory;
- попадает в **Proof Track** / закрытые карточки на сайте.

### 6.3 Обновление системы

| Что учим | Как |
|----------|-----|
| Priority rubric | `rubric_v2` только с записью |
| Probability weights | раз в квартал по Brier score |
| Source tiers | autopsy: какие источники врали |
| Prompt versions | git tag + A/B |

**Правило:** без track record **не меняем** веса probability model.

---

## 7. Что попадает на сайт

### 7.1 Публично (events-live.js / API)

| Поле | Guest | Pulse | PRO |
|------|-------|-------|-----|
| title, category, horizon | ✅ | ✅ | ✅ |
| marketProb | ✅ | ✅ | ✅ |
| ppProb | ❌ blur | ✅ | ✅ |
| edgePp | ❌ | ✅ | ✅ |
| summary (1–2 предложения) | ✅ | ✅ | ✅ |
| verdict (короткий) | частично | ✅ | ✅ |
| riskLevel + top flags | ❌ | ✅ | ✅ |
| War Room (агенты) | teaser | ✅ | ✅ |
| contradiction map | ❌ | частично | ✅ |
| evidence list | ❌ | ❌ | ✅ |
| comparable events | ❌ | ❌ | ✅ |
| **whale summary** («киты → YES») | ❌ | teaser | ✅ |
| **marketIntelligence detail** | ❌ | ❌ | ✅ |
| model components | ❌ | ❌ | PRO debug |

### 7.2 Только внутри системы

- raw API dumps Polymarket;
- **полные адреса кошельков и сырые сделки MI** (на сайте — только агрегат);
- полный evidence package с URL и tiers;
- промежуточные scores каждого агента;
- failed gates log;
- LLM raw responses;
- contradiction graph (full);
- weight vectors probability model;
- autopsy drafts до публикации.

### 7.3 Блоки сайта vs pipeline

| UI блок | Источник в pipeline |
|---------|---------------------|
| ОНЛАЙН · Полимаркет | Publishing Agent ← accepted only |
| Closed card | Normalizer + Probability + Risk + Verdict |
| OPEN / War Room | Evidence + **Whale MI** + Contradiction + Comparable + agents |
| Proof Track | Memory / Track Record |
| Autopsy section | Autopsy Agent |

---

## 8. Quality & Monitoring (сквозной слой)

Работает **между** всеми модулями Core:

```text
verify source → dedupe → reliability tier → noise filter → monitor changes
```

| Метрика мониторинга | Алерт |
|---------------------|-------|
| Цена ±5pp за 24h | Monitoring Agent |
| **Whale flip** (accumulation_yes → accumulation_no) | пересчёт PP_prob |
| Новый tier-A fact | пересчёт PP_prob |
| Резолв изменился | Normalizer rerun |
| Harvest fail | ops alert |

---

## 9. Gap: сейчас vs V1

| Компонент диаграммы | Статус |
|---------------------|--------|
| Polymarket Scanner | ✅ |
| Priority / filter | ✅ rubric_v1 |
| Event Normalizer | ❌ |
| **Whale Intelligence Agent** | ❌ |
| **MI services** (Analytics, Unusual Whales, Dune…) | ❌ |
| Evidence Collector (real APIs) | ❌ |
| Contradiction Engine | ❌ |
| Comparable Events | ❌ |
| Probability Model (formula) | ❌ |
| Risk Officer (structured) | ⚠️ LLM |
| Verdict Agent | ⚠️ LLM |
| Publishing | ✅ |
| Memory / Track Record | ❌ mock UI |
| Autopsy | ❌ |
| Quality layer | ⚠️ только Priority gates |

---

## 10. Этапы реализации V1

> DoD §11 закрыт — реализация **только по фазам** ниже, без пропусков.

| Фаза | Модули | Результат |
|------|--------|-----------|
| **V1.0a** | Event Normalizer + structured Risk | JSON schema расширен |
| **V1.0b** | **Whale Intelligence Agent** + Polymarket Analytics (P0 MI) | `marketIntelligence` в pipeline |
| **V1.1** | Evidence Collector (news API P0) + Unusual Whales | facts + flow не из LLM |
| **V1.2** | Probability Model v1.1 + edge enforce | ppProb воспроизводим, whale_signal |
| **V1.3** | Contradiction + Comparable (lite) + Dune | War Room глубже |
| **V1.4** | Memory + Track Record persist | Proof Track real |
| **V1.5** | Autopsy + weight review | learning loop |

---

## 11. Definition of Done — Architecture V1 ✅

**Закрыто:** 9 июня 2026 — владелец дал ОК.

- [x] Владелец прочитал §1–§7 и нет «дыр» в логике
- [x] Согласованы веса Probability Model incl. **whale_signal** (§4.2)
- [x] Согласован **Market Intelligence Layer** и приоритет сервисов (§2.3)
- [x] Согласован pre-publish gate + MI checks (§3.4–3.5)
- [x] Согласована таблица «сайт vs внутреннее» (§7)
- [x] Gap-таблица (§9) принята — понимаем, что строим дальше
- [x] Фазы V1.0a–V1.5 добавлены в [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]]
- [x] [[АРХИТЕКТУРА_АГЕНТОВ]] ссылается на этот документ как master

**Дальше:** реализация по §10 — старт с **V1.0a** (Normalizer), параллельно можно поднимать Railway (этап 3).

---

## 12. Журнал версий

| Версия | Дата | Изменение |
|--------|------|-----------|
| `intelligence_v1` draft | 2026-06-09 | Первый документ по диаграмме pipeline |
| `intelligence_v1.1` draft | 2026-06-09 | **4 уровня PP** · Market Intelligence Layer · Whale Intelligence Agent · вес `whale_signal` |
| `intelligence_v1.1` **approved** | 2026-06-09 | DoD §11 закрыт · владелец ОК |

---

← [[ДОМ_ШТАБ]] · [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]] · [[СТАТУС_ЛАБОРАТОРИИ]]
