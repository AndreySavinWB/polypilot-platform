# Probability Formula v1.1 — официальная формула PIE

> [[PIE_V1_2_ФИНАЛЬНАЯ_АРХИТЕКТУРА]] · [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[SOURCE_SCORING_SYSTEM]] · [[MARKET_STRUCTURE_ANALYZER]]

> **Версия:** `pie_v1.3` · формула `prob_formula_v1.1`  
> **Статус:** 📐 целевая формула зафиксирована · ✅ v0 реализован rules-only в `backend/src/agents/probability.py`  
> **Дата:** 9 июня 2026

---

## Зачем этот документ

PIE должна объяснять каждый свой прогноз.

> «Почему PP Probability = 67%?»  
> «Потому что рынок — 58%, киты накапливают YES, но новости нейтральные, и один источник tier C.»

Формула v1.1 отличается от v1.0:
- Добавлен `marketStructureScore` как модификатор `market_base`
- Добавлен `evidenceQualityScore` как модификатор `news_signal` и `social_signal`
- Каждый компонент теперь имеет явные условия отключения

---

## Место в pipeline

```
Comparable Events
      ↓
[Probability Engine — Formula v1.1]
      ↓
Risk Officer
```

---

## Официальная формула PIE v1.1

```
ppProb = clamp(
    w1 × market_base × market_reliability_mult
  + w2 × whale_signal_norm × whale_quality_mult
  + w3 × news_signal_norm × EQS_mult
  + w4 × social_signal_norm × EQS_mult
  + w5 × trends_signal_norm × EQS_mult
  + w6 × historical_base_rate
  + w7 × contradiction_adjustment
, 2%, 98%)
```

---

## Компоненты и веса

### Веса базовые (сумма = 1.0)

| # | Компонент | Вес (w) | Источник данных |
|---|-----------|---------|-----------------|
| 1 | `market_base` | **0.28** | marketSnapshot.marketProb |
| 2 | `whale_signal` | **0.15** | marketIntelligence.whaleSignal |
| 3 | `news_signal` | **0.22** | scoredEvidence.news[] |
| 4 | `social_signal` | **0.08** | scoredEvidence.social[] |
| 5 | `trends_signal` | **0.12** | scoredEvidence.trends[] |
| 6 | `historical_base_rate` | **0.08** | analogs[].baseRate |
| 7 | `contradiction_adjustment` | **0.07** | contradictionMap[] |

**Итого: 1.00**

> Если компонент отключён (missing), его вес перераспределяется пропорционально на остальные активные компоненты.

---

## Компонент 1 · market_base

**Что это:** Нормализованная рыночная цена (0–1).

**Что усиливает влияние:**
- marketHealthScore ≥ 80 → `market_reliability_mult = 1.0`
- crowdParticipation = high
- priceReliability = high

**Что ослабляет:**
- marketHealthScore 45–79 → `market_reliability_mult = 0.75`
- thin_market flag → mult ×0.6
- priceReliability = low → mult ×0.4

**Когда отключается:**
- marketProb ≤ 2% или ≥ 98% (рынок слишком однозначный → не несёт информации)
- `price_unreliable` flag + manipulationRisk = high

**Нормализация:** `market_base = marketProb / 100`

---

## Компонент 2 · whale_signal

**Что это:** Направление и уверенность поведения крупных участников.

**Нормализация:**

| whaleSignal | whale_signal_norm |
|-------------|-------------------|
| `accumulation_yes` | 0.75 |
| `accumulation_no` | 0.25 |
| `mixed` | 0.50 |
| `neutral` | 0.50 |
| `unknown` | 0.50 (+ флаг) |

**Что усиливает:**
- confidence ≥ 70 → `whale_quality_mult = 1.0`
- anomalies[] не пустой → сигнал сильнее

**Что ослабляет:**
- confidence < 40 → `whale_quality_mult = 0.5`
- manipulationRisk = high → mult ×0.3 (кит может манипулировать сам)
- thin_market + single_whale_above_50pct → mult ×0.2

**Когда отключается:**
- `whaleSignal = unknown` и sourcesUsed пуст → вес переходит к news_signal
- manipulationRisk = high и single_whale_above_50pct → компонент = 0.50 (нейтраль), флаг `whale_discounted`

---

## Компонент 3 · news_signal

**Что это:** Вектор доказательств из верифицированных новостных источников.

**Нормализация:**
- Считается как взвешенное среднее позиций источников tier A/B по отношению к YES/NO
- При отсутствии явной позиции → 0.50 (нейтраль)

**Что усиливает:**
- EQS ≥ 80 → `EQS_mult = 1.0`
- uniqueClaimsCount ≥ 3 независимых факта
- dominantSourceTier = A

**Что ослабляет:**
- EQS 55–79 → `EQS_mult = 0.8`
- EQS 30–54 → `EQS_mult = 0.55`
- EQS < 30 → `EQS_mult = 0.3`

**Когда отключается:**
- `no_verified_facts` flag → news_signal_norm = 0.50, w3 → 0
- `stale_evidence` (все источники > 72ч) → EQS_mult ×0.5

---

## Компонент 4 · social_signal

**Что это:** Нарратив и настроение в социальных сетях (X).

**Нормализация:** sentiment → [-1, +1] → [0, 1]

**Что усиливает:**
- Высокое количество уникальных постов (не дубли)
- Верифицированные аккаунты с большой аудиторией

**Что ослабляет:**
- `low_quality_sources_only` → EQS_mult снижается
- Hype без tier A/B новостей → downweight (социальный шум)
- Частые дубли → EQS_mult ×0.5

**Когда отключается:**
- Нет данных X API → w4 = 0
- Только анонимные источники и 0 tier A/B → w4 = 0, флаг `social_only_no_facts`

---

## Компонент 5 · trends_signal

**Что это:** Поисковый интерес (Google Trends), delta за 7 дней.

**Нормализация:**
- delta > +50% → trends_signal_norm = 0.70 (рост интереса = рост ожиданий события)
- delta -50%..+50% → нормализуем линейно
- delta < -50% → trends_signal_norm = 0.30

**Что усиливает:**
- Совпадение с тематикой события

**Что ослабляет:**
- Поисковый запрос слишком общий → EQS_mult ×0.7
- Тренд не по теме (ложный пик) → флаг, EQS_mult ×0.5

**Когда отключается:**
- Trends API не вернул данные → w5 = 0
- eventType = `legal` или `regulatory` (trends ненадёжны для этих типов) → w5 ×0.5

---

## Компонент 6 · historical_base_rate

**Что это:** Базовая вероятность исхода YES из аналогичных событий в прошлом.

**Нормализация:** `historical_base_rate = mean(analogs[i].outcome == YES) / 100`

**Что усиливает:**
- Аналогов ≥ 5 → полный вес
- Высокая схожесть (similarity ≥ 0.7)

**Что ослабляет:**
- Аналогов < 3 → вес ×0.5
- similarity < 0.4 → вес ×0.3

**Когда отключается:**
- analogs[] пустой → w6 = 0, флаг `no_historical_data`
- Первое событие данного типа без аналогов → w6 = 0

---

## Компонент 7 · contradiction_adjustment

**Что это:** Корректировка на основе карты противоречий.

**Нормализация:**

| Ситуация | contradiction_adjustment |
|----------|--------------------------|
| Нет противоречий | +0 |
| Слабые противоречия (severity low) | -0.03 |
| Средние (severity medium) | -0.07 |
| Сильные (severity high) | -0.12 |
| Прямое противоречие: flow vs news высокой достоверности | -0.15 |

Adjustment всегда отрицательный или нулевой: противоречия снижают уверенность, но не увеличивают.

**Когда отключается:**
- contradictionMap[] пустой → w7 = 0 (без корректировки)

---

## Edge и условия публикации

```
edgePp = ppProb - marketProb
```

**Edge показывается на сайте только если:**
- `|edgePp| ≥ 5pp`
- И (`uniqueClaimsCount ≥ 1` ИЛИ `whaleSignal ∈ {accumulation_yes, accumulation_no}` с confidence ≥ 70)
- И `riskLevel ≠ high` с `confidence < 60`
- И `priceReliability ≠ low`

Если edge не публикуется → карточка всё равно выходит, но без PP Edge блока.

---

## Объяснение прогноза (explainability)

Каждый прогноз должен содержать `components{}` в JSON:

```json
{
  "ppProb": 67,
  "marketProb": 58,
  "edgePp": 9,
  "components": {
    "market_base":       { "raw": 0.58, "mult": 0.75, "weighted": 0.123, "w": 0.28 },
    "whale_signal":      { "raw": 0.75, "mult": 1.0,  "weighted": 0.113, "w": 0.15 },
    "news_signal":       { "raw": 0.60, "mult": 0.8,  "weighted": 0.106, "w": 0.22 },
    "social_signal":     { "raw": 0.52, "mult": 0.55, "weighted": 0.023, "w": 0.08 },
    "trends_signal":     { "raw": 0.65, "mult": 1.0,  "weighted": 0.078, "w": 0.12 },
    "historical_rate":   { "raw": 0.62, "mult": 0.5,  "weighted": 0.025, "w": 0.08 },
    "contradiction_adj": { "raw": -0.07,"mult": 1.0,  "weighted": -0.005,"w": 0.07 }
  },
  "flags": ["thin_market", "low_analog_count"],
  "missingComponents": []
}
```

---

## Что НЕ делает формула

- ❌ Не изобретает факты — каждый компонент из структурированных данных
- ❌ Не пересчитывается в Verdict Agent — Verdict только объясняет
- ❌ Не меняет веса автоматически (авто-калибровка → v1.1, нужен Memory)
- ❌ Не даёт торговые рекомендации

---

## Изменения v1.1 относительно v1.0

| Что изменилось | v1.0 | v1.1 |
|----------------|------|------|
| market_base вес | 0.30 | 0.28 (−0.02, перешёл в contradiction) |
| Модификатор market_base | нет | market_reliability_mult из Market Structure |
| Модификатор news/social | нет | EQS_mult из Source Scoring System |
| contradiction_adjustment вес | 0.05 | 0.07 (+0.02) |
| Новые флаги | — | `whale_discounted`, `weak_evidence`, `price_unreliable` |

---

## Definition of Done

- [ ] Основатель прочитал — логика каждого компонента понятна
- [ ] Понятно, как Market Structure и EQS влияют на итог
- [ ] Понятны условия отключения компонентов
- [ ] Условия публикации edge зафиксированы

---

← [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[MARKET_STRUCTURE_ANALYZER]] · [[SOURCE_SCORING_SYSTEM]]
