# Probability Intelligence Engine — архитектура PolyPilot

> [[ДОМ_ШТАБ]] · [[INTELLIGENCE_ENGINE_MVP]] · [[INTELLIGENCE_DATA_FLOW]] · [[AI_ARCHITECTURE_V1]] · [[STRATEGY_INTELLIGENCE_LAYER]] · [[СХЕМА_МЯСОРУБКИ]]

> **Статус:** ✅ **зафиксирован** — DoD закрыт, основатель ОК 9 июня 2026  
> **Версия:** `pie_v1.3` · **Дата:** 9 июня 2026  
> **Изменено:** добавлены 4 новых блока (Event Type Classifier, Market Structure Analyzer, Source Scoring System, Probability Formula v1.1)

---

## Зачем этот документ

**AI Architecture V1** зафиксировал контракт (веса, gates, 4 уровня).  
**Probability Intelligence Engine (PIE)** — это **единая мясорубка**: порядок модулей, границы ответственности, что куда передаётся.

> Самый дорогой риск сейчас — построить **не ту** мясорубку.  
> Railway, Vercel, harvest уже есть. Нужно спроектировать **мозг**, не писать куски.

---

## Одна цепочка (master pipeline v1.3)

```text
Market Scanner              ← пул Polymarket, raw events
        ↓
   Priority Gate             ← rubric_v1 (не LLM) · embedded в Scanner-этап
        ↓
Event Normalizer             ← резолв, RU, горизонт, decision maker
        ↓
Event Type Classifier        ← тип события, профиль анализа, источники
        ↓
Market Intelligence          ← поведение денег (киты, flow, аномалии)
        ↓
Market Structure Analyzer    ← концентрация, здоровье рынка, манипуляция
        ↓
Evidence Collector           ← факты снаружи (news, social, trends)
        ↓
Comment Analysis (5.5A/B/C)  ← crowdPulse: рынок vs сеть vs сводка (max 10%)
        ↓
Source Scoring System        ← Trust, Freshness, Uniqueness, EQS
        ↓
Contradiction Engine         ← рынок vs факты vs flow
        ↓
Comparable Events            ← аналоги, base rates
        ↓
Probability Engine           ← PP Probability v1.1, edge, компоненты
        ↓
Risk Officer                 ← riskLevel, flags, gates
        ↓
Strategy Router              ← primary setup, strategy fits, why selected
        ↓
Verdict Agent                ← итог для UX
        ↓
Publishing                   ← events-live.js / API  (продукт)
        ↓
Memory                       ← track record, версии, autopsy feed
        ↺ (обратная связь в Priority weights, Probability weights)
```

**Сквозной слой:** Quality & Monitoring — verify, dedupe, freshness на каждом шаге.

**Strategy Intelligence Layer:** не заменяет PIE. Он работает после базового evidence package и отвечает на вопрос: под какую торговую стратегию событие подходит и почему оно вообще выбрано. См. [[STRATEGY_INTELLIGENCE_LAYER]].

---

## Пять уровней разведки (v1.3)

| Уровень | Модули PIE | Вопрос |
|---------|------------|--------|
| **1 · Событие** | Scanner, Priority, Normalizer, **Event Type Classifier** | *Что торгуем, как резолвится, какого типа?* |
| **2 · Деньги** | Market Intelligence, **Market Structure Analyzer** | *Что делают деньги? Можно ли доверять рынку?* |
| **3 · Информация** | Evidence Collector, **Comment Analysis (5.5A/B/C)**, **Source Scoring System** | *Что говорит мир снаружи и что говорят люди (отдельно)?* |
| **4 · Мышление** | Contradiction, Comparable, **Probability Engine v1.1**, Risk, **Strategy Router**, Verdict | *Где PP видит edge, риск и trading setup?* |
| **5 · Память** | Memory (+ Autopsy) | *Что мы предсказывали и где ошиблись?* |

**Новые блоки v1.3:**
- **Event Type Classifier** → профиль анализа под тип события
- **Market Structure Analyzer** → насколько можно доверять рыночной цене
- **Source Scoring System** → EQS, дедупликация, Trust/Freshness
- **Probability Formula v1.1** → market_reliability_mult + EQS_mult в расчёте

---

## Модули — роль, вход, выход

### 0. Market Scanner (+ Priority Gate)

| | |
|---|---|
| **Роль** | Найти кандидатов в пуле PM; отсечь мусор до intelligence |
| **Вход** | Polymarket Gamma API |
| **Выход** | `rawEvent` + `priorityDecision` (accepted / watchlist / rejected) |
| **Не делает** | резолв RU, новости, киты, вероятность |
| **Статус код** | ✅ `polymarket.py`, `priority.py` |

Hard gates: [[ПРИОРИТЕТ_АГЕНТ]]. Без `accepted` событие **не входит** в PIE pipeline (кроме watchlist research).

---

### 1. Event Normalizer

| | |
|---|---|
| **Роль** | Сделать событие **понятным** для агентов и пользователя RU |
| **Вход** | `rawEvent` |
| **Выход** | `normalizedEvent` — titleRu, resolutionCriteria, horizonDays, decisionMaker, marketSnapshot |
| **Не делает** | новости, киты, PP prob |
| **Fail** | `resolution_unclear` → reject или research_required |
| **Статус код** | ⬜ первый кодовый блок **после** P1–P3 docs |

---

### 2. Market Intelligence (MI Layer)

| | |
|---|---|
| **Роль** | Поведение **участников рынка**, не narrative |
| **Вход** | `normalizedEvent` + MI APIs |
| **Выход** | `marketIntelligence` — whaleSignal, confidence, anomalies, smartMoneyBias |
| **Потребитель** | Contradiction Engine, **Probability Engine** (`whale_signal`), Risk Officer |
| **Не показываем** | сырые адреса кошельков на сайте (только агрегат PRO) |
| **Статус код** | ⬜ |

Вопросы агента: что делают киты? smart money? аномалии 6h/24h? скрытое накопление?

---

### 3. Evidence Collector

| | |
|---|---|
| **Роль** | Верифицируемые **факты** и контекст снаружи |
| **Вход** | `normalizedEvent` |
| **Выход** | `evidence` — news[], social[], trends[], official[] |
| **Не делает** | on-chain flow (это MI), финальный вердикт |
| **Статус код** | ⚠️ LLM mock в `pipeline.py` |

---

### 3b. Comment Analysis (5.5A / 5.5B / 5.5C)

| | |
|---|---|
| **Роль** | Отдельно: комментарии Polymarket vs обсуждение в сети → сводка |
| **Вход** | `normalized` + контекст `evidence` |
| **Выход** | `crowdPulse` — marketComments, socialDiscussion, synthesis |
| **Вес на PP** | max **10%** (рынок 0–7%, сеть 0–5%) |
| **Risk Officer** | спорный резолв, сильный риск → `passToRiskOfficer[]` |
| **Спека** | [[COMMENT_ANALYSIS_V1]] |
| **Статус код** | ⚠️ mock `comment_analysis.py` · UI ✅ |

**Не смешивать** с `evidence.social[]` — там сырые сигналы, здесь структурированный crowd sentiment.

---

### 4. Contradiction Engine

| | |
|---|---|
| **Роль** | Карта расхождений: рынок vs факты vs flow vs trends |
| **Вход** | marketSnapshot + marketIntelligence + evidence |
| **Выход** | `contradictionMap` — claims, sides, severity |
| **Пример** | PM 45%, news neutral, whales → YES = contradiction «flow без news» |
| **Статус код** | ⬜ |

---

### 5. Comparable Events Engine

| | |
|---|---|
| **Роль** | Исторические аналоги, base rates |
| **Вход** | normalized + evidence + **Memory** (прошлые PP прогнозы) |
| **Выход** | `analogs[]` — analogId, outcome, similarity, baseRate |
| **Статус код** | ⬜ |

---

### 6. Probability Engine

| | |
|---|---|
| **Роль** | Единственный источник **PP Probability** и **edge** |
| **Вход** | market_base, whale_signal, news, social, trends, historical, contradiction_adj |
| **Выход** | `probability` — ppProb, marketProb, edgePp, components{} |
| **Формула** | [[AI_ARCHITECTURE_V1]] §4.2 (whale_signal w=0.15) |
| **Не делает** | UX-текст, risk flags |
| **Статус код** | ⬜ (сейчас ≈ LLM confidence) |

> Именование: **Probability Engine** = **Probability Model** в AI_ARCHITECTURE_V1.

---

### 7. Risk Officer

| | |
|---|---|
| **Роль** | Оценка риска **ошибиться** и риска **данных** |
| **Вход** | всё выше + quality scores |
| **Выход** | `risk` — riskLevel, riskScore, flags[] |
| **Gates** | high risk + low confidence → не публикуем edge |
| **Статус код** | ⚠️ LLM-only |

---

### 8. Verdict Agent

| | |
|---|---|
| **Роль** | Человекочитаемый итог для карточки / War Room |
| **Вход** | probability + risk + contradiction summary |
| **Выход** | `verdict` — ppVerdict RU, confidence, status |
| **Не делает** | не пересчитывает ppProb |
| **Статус код** | ⚠️ LLM-only |

---

### 9. Publishing

| | |
|---|---|
| **Роль** | Pre-publish gate + sync продукт |
| **Вход** | полный pipeline package |
| **Выход** | `events-live.js`, API, карточка сайта |
| **Gates** | [[AI_ARCHITECTURE_V1]] §3.4–3.5 |
| **Статус код** | ✅ harvest sync |

---

### 10. Memory

| | |
|---|---|
| **Роль** | Track record, версии прогнозов, feed для Comparable и Autopsy |
| **Вход** | published card + later resolution |
| **Выход** | `memoryRecord`, autopsy input, weight calibration data |
| **Статус код** | ⬜ mock UI |

**Autopsy** — подмодуль Memory: после резолва → lesson, Brier, errorTags → обновление весов (раз в квартал, не ad hoc).

---

## Что нельзя забыть (чеклист основателя)

| Риск «забыли» | Где в PIE |
|---------------|-----------|
| Киты / flow | Market Intelligence → Probability Engine |
| Аналоги | Comparable Events → Probability Engine |
| История прогнозов | Memory → Comparable + Autopsy |
| Risk Officer | **После** Probability, **до** Verdict |
| Contradiction | **До** Probability Engine |
| Priority до intelligence | Scanner gate |

---

## Связь документов

| Документ | Содержание |
|----------|------------|
| **PROBABILITY_INTELLIGENCE_ENGINE.md** | ← этот файл · **архитектура модулей v1.3** |
| [[EVENT_TYPE_CLASSIFIER]] | классификатор типа события, профили анализа |
| [[MARKET_STRUCTURE_ANALYZER]] | здоровье рынка, концентрация, manipulationRisk |
| [[SOURCE_SCORING_SYSTEM]] | Trust/Freshness/Uniqueness, EQS |
| [[PROBABILITY_FORMULA_V1_1]] | официальная формула PIE v1.1 с модификаторами |
| [[INTELLIGENCE_ENGINE_MVP]] | **v0 каждого блока** — что включаем, что откладываем |
| [[INTELLIGENCE_DATA_FLOW]] | **поток данных** · JSON на каждом шаге |
| [[AI_ARCHITECTURE_V1]] | веса, gates, site vs internal, DoD weights |
| [[СХЕМА_МЯСОРУБКИ]] | визуальная карта |

---

## Definition of Done — PIE на бумаге ✅

**Закрыто:** 9 июня 2026 — основатель дал ОК.

- [x] Основатель прочитал этот документ — цепочка модулей без дыр
- [x] [[INTELLIGENCE_ENGINE_MVP]] — v0 каждого блока согласован
- [x] [[INTELLIGENCE_DATA_FLOW]] — JSON-поток от PM до Memory согласован
- [x] Нет противоречий с [[AI_ARCHITECTURE_V1]] §4–§7

**Следующий шаг:** код **Event Normalizer** ([[INTELLIGENCE_ENGINE_MVP]] · порядок реализации).

---

## Журнал

| Версия | Дата | Изменение |
|--------|------|-----------|
| `pie_v1` | 2026-06-09 | Master pipeline PIE · блокер перед кодом |
| `pie_v1` **approved** | 2026-06-09 | DoD закрыт · старт V1.0a Normalizer |
| `pie_v1.3` | 2026-06-09 | +4 блока: EventTypeClassifier, MarketStructureAnalyzer, SourceScoring, FormulaV1.1 |

---

← [[ДОМ_ШТАБ]] · [[INTELLIGENCE_ENGINE_MVP]] · [[INTELLIGENCE_DATA_FLOW]]
