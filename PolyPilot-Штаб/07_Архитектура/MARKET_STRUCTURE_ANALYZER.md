# Market Structure Analyzer — анализатор структуры рынка

> [[PIE_V1_2_ФИНАЛЬНАЯ_АРХИТЕКТУРА]] · [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[EVENT_TYPE_CLASSIFIER]] · [[SOURCE_SCORING_SYSTEM]]

> **Версия:** `pie_v1.3`  
> **Статус:** ✅ v0 реализован rules-only в `backend/src/agents/market_structure.py`  
> **Дата:** 9 июня 2026

---

## Зачем этот блок

Market Intelligence смотрит на движение денег: что делают киты, есть ли накопление, аномалии.

Но движение денег само по себе ничего не говорит о качестве рыночного сигнала.

> Один кит с 80% объёма — это не «рынок сказал».  
> Это один человек сказал.

**Market Structure Analyzer отвечает на вопрос:**

> Насколько можно доверять цене рынка как агрегатному мнению?

Если рынок управляется одним игроком — его вероятность не равна «консенсусу толпы».  
Если рынок здоровый и широкий — цена несёт настоящий информационный сигнал.

---

## Место в pipeline

```
Market Intelligence
      ↓
[Market Structure Analyzer]   ← этот блок
      ↓
Evidence Collector
```

---

## Вход и выход

### Вход

| Поле | Откуда | Описание |
|------|--------|----------|
| `marketSnapshot` | Normalizer | Объём, ликвидность, спред, prob |
| `marketIntelligence` | Market Intelligence Agent | whaleSignal, anomalies, sourcesUsed |
| `eventType` | Event Type Classifier | Тип события (влияет на норму концентрации) |

### Выход

```json
{
  "marketStructure": {
    "marketHealthScore": 74,
    "walletConcentration": "medium",
    "whaleDominance": 38,
    "manipulationRisk": "low",
    "crowdParticipation": "moderate",
    "priceReliability": "moderate",
    "structureSummary": "Рынок умеренно здоровый: доминирование китов 38%, признаков манипуляции нет.",
    "flags": ["thin_market", "single_whale_above_30pct"],
    "sourcesUsed": ["polymarket_analytics", "unusual_whales"]
  }
}
```

---

## Основные показатели

### marketHealthScore (0–100)

Итоговый балл здоровья рынка. Считается из всех показателей ниже.

| Диапазон | Интерпретация |
|----------|---------------|
| 80–100 | Здоровый — большой, диверсифицированный, без аномалий |
| 55–79 | Умеренный — некоторая концентрация, но приемлемо |
| 30–54 | Слабый — высокая концентрация или признаки манипуляции |
| 0–29 | Нездоровый — один игрок, thin market, высокий риск |

---

### walletConcentration

Насколько объём сосредоточен у нескольких кошельков.

| Значение | Описание |
|----------|----------|
| `low` | Топ-5 кошельков < 30% объёма |
| `medium` | Топ-5 кошельков 30–60% объёма |
| `high` | Топ-5 кошельков > 60% объёма |

---

### whaleDominance (0–100%)

Доля объёма, приходящаяся на крупнейший одиночный кошелёк или группу.

- `> 50%` — один игрок доминирует → `manipulationRisk = high`
- `30–50%` — значимая концентрация → flag
- `< 30%` — нормально

---

### manipulationRisk

| Значение | Условие |
|----------|---------|
| `high` | whaleDominance > 50% ИЛИ координированный pump (много мелких + 1 кит) |
| `medium` | whaleDominance 30–50% ИЛИ аномальный spike без новостей |
| `low` | Нет явных признаков |

---

### crowdParticipation

Насколько рынок широкий — есть ли реальная «толпа» или только несколько игроков.

| Значение | Описание |
|----------|----------|
| `high` | Много участников, диверсифицированный объём |
| `moderate` | Средняя активность |
| `low` | Мало уникальных участников, thin market |

---

### priceReliability

Можно ли доверять рыночной вероятности как сигналу.

| Значение | Условие |
|----------|---------|
| `high` | marketHealthScore ≥ 75 и нет manipulation flags |
| `moderate` | Score 45–74, есть концентрация но не критичная |
| `low` | Score < 45, thin market, или manipulation_suspect |

---

## Флаги

| Флаг | Значение |
|------|----------|
| `thin_market` | Ликвидность < $10K или объём total < $50K |
| `single_whale_above_30pct` | Один кошелёк > 30% объёма |
| `single_whale_above_50pct` | Один кошелёк > 50% объёма |
| `coordinated_pump` | Много мелких + один кит в одном направлении |
| `manipulation_suspect` | Из Market Intelligence (уже проставлен MI) |
| `no_crowd` | crowdParticipation = low при высокой цене |
| `price_unreliable` | priceReliability = low |

---

## Влияние на Probability Engine

Market Structure Score напрямую влияет на вес компонента `market_base` в формуле:

| priceReliability | Множитель market_base |
|------------------|-----------------------|
| `high` | ×1.0 (полный вес 0.30) |
| `moderate` | ×0.7 (эффективный вес ~0.21) |
| `low` | ×0.4 (эффективный вес ~0.12) |

**Логика:** если рынком управляет один кит, цена этого рынка — менее надёжный prior. Вес переносится на `news_signal` и `whale_signal` (но whale_signal при манипуляции также downweight).

---

## Влияние на Risk Officer

Передаёт прямые флаги в Risk Officer:

- `manipulationRisk = high` → `riskLevel` повышается до `high`
- `thin_market` + `whale_dominance > 30%` → флаг `thin_market_whale_combo`
- `price_unreliable` → предупреждение в `verdict`

---

## Что НЕ делает этот блок

- ❌ Не ищет новости и не анализирует факты
- ❌ Не считает итоговую вероятность
- ❌ Не выдаёт торговые рекомендации
- ❌ Не хранит историю структуры рынков

---

## MVP v1 — что включаем

| Показатель | v1 | Позже |
|------------|-----|-------|
| whaleDominance | ✅ из Unusual Whales + Analytics | |
| walletConcentration | ✅ rule-based из топ сделок | |
| manipulationRisk | ✅ из MI флагов + правила | |
| crowdParticipation | ✅ оценка по числу уникальных сделок | |
| marketHealthScore | ✅ взвешенная сумма | |
| On-chain wallet tracking (Arkham) | ❌ | v2 |
| Graph-анализ связанных кошельков | ❌ | v2 |
| Исторический baseline концентрации | ❌ | v1.1 (из Memory) |

### Реализованный v0 (июнь 2026)

До подключения wallet/trades API блок не выдумывает концентрацию кошельков.

**Использует:**

- `marketSnapshot.volume`
- `marketSnapshot.volume24h`
- `marketSnapshot.liquidity`
- `marketSnapshot.spread`
- `marketSnapshot.marketProb`
- `marketIntelligence.volumeAnomaly`
- `marketIntelligence.whaleSignal` как proxy, а не настоящий wallet signal

**Выход v0:**

```json
{
  "marketHealthScore": 0,
  "liquidityTier": "low|medium|high|unknown",
  "spreadRisk": "low|medium|high|unknown",
  "walletConcentration": "unknown",
  "whaleDominance": null,
  "manipulationRisk": "low|medium|high",
  "crowdParticipation": "low|moderate|high",
  "priceReliability": "low|moderate|high",
  "marketReliability": 0.0,
  "flags": [],
  "scoringMode": "rules_v0"
}
```

---

## Definition of Done

- [x] Основатель прочитал — показатели и интерпретации понятны
- [x] Понятно, как marketHealthScore влияет на Probability Engine
- [x] Место в pipeline зафиксировано: после Market Intelligence, до Evidence Collector
- [x] v0 подключён в `pie_v1_0f`

---

← [[EVENT_TYPE_CLASSIFIER]] · [[SOURCE_SCORING_SYSTEM]] · [[PROBABILITY_FORMULA_V1_1]]
