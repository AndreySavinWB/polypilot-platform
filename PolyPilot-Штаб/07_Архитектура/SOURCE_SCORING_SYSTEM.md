# Source Scoring System — система оценки источников

> [[PROBABILITY_INTELLIGENCE_ENGINE]] · [[PROBABILITY_FORMULA_V1_1]]

> **Версия:** `pie_v1.3`  
> **Статус:** 📐 зафиксирован на бумаге  
> **Дата:** 9 июня 2026

---

## Зачем этот блок

Evidence Collector собирает факты: новости, тренды, соцсети.

Но не все факты одинаковы.

> Официальный документ суда ≠ твит анонима.  
> Статья Reuters ≠ перепечатка на третьем сайте без ссылок.  
> Новость 6 часов назад ≠ новость 4 дня назад.

Без оценки источников Probability Engine суммирует несравнимые вещи.

**Source Scoring System решает:**
- Какой вес дать каждому доказательству
- Обнаружить дублирование: одна история в 15 перепечатках — это не 15 фактов
- Посчитать итоговый **Evidence Quality Score** — входной сигнал для Probability Engine

---

## Место в pipeline

```
Evidence Collector
      ↓
[Source Scoring System]   ← этот блок
      ↓
Contradiction Engine
```

---

## Вход и выход

### Вход

| Поле | Откуда | Описание |
|------|--------|----------|
| `evidence.news[]` | Evidence Collector | Список новостей с URL, датой, источником |
| `evidence.trends[]` | Evidence Collector | Google Trends данные |
| `evidence.social[]` | Evidence Collector | X-посты, сигналы |
| `eventType` | Event Type Classifier | Тип события (влияет на приоритеты источников) |

### Выход

```json
{
  "scoredEvidence": {
    "news": [
      {
        "url": "https://reuters.com/...",
        "source": "Reuters",
        "sourceTrust": 95,
        "sourceFreshness": 98,
        "sourceUniqueness": 1.0,
        "duplicateCount": 0,
        "evidenceScore": 97,
        "tier": "A"
      },
      {
        "url": "https://blog-xyz.com/...",
        "source": "Unknown Blog",
        "sourceTrust": 25,
        "sourceFreshness": 72,
        "sourceUniqueness": 0.3,
        "duplicateCount": 4,
        "evidenceScore": 22,
        "tier": "C"
      }
    ],
    "social": [...],
    "qualitySummary": {
      "evidenceQualityScore": 68,
      "tierACount": 3,
      "tierBCount": 5,
      "tierCCount": 12,
      "uniqueClaimsCount": 4,
      "totalDuplicatesRemoved": 9,
      "freshnessPenaltyApplied": true,
      "dominantSourceTier": "B"
    }
  }
}
```

---

## Оценка доверия к источнику (sourceTrust)

### Шкала доверия

| Тип источника | Балл | Tier | Примеры |
|---------------|------|------|---------|
| Официальный документ (суд, SEC, ЦБ) | 100 | A | SEC filing, судебное решение, ЦБ пресс-релиз |
| Правительственный источник | 95 | A | WhiteHouse.gov, Fed.gov, официальные заявления |
| Мировые агентства | 90–95 | A | Reuters, AP, Bloomberg, AFP |
| Ведущие деловые СМИ | 80–90 | A | FT, WSJ, NYT (business), CNBC, The Economist |
| Крупные аналитические центры | 75–85 | A/B | Brookings, RAND, Goldman Sachs Research |
| Проверенные отраслевые эксперты | 60–75 | B | Известный аналитик с track record, Polymarket community |
| Региональные / нишевые СМИ | 45–60 | B | Надёжные, но ограниченный охват |
| Крупные социальные аккаунты | 35–50 | B/C | Верифицированные аккаунты X (>100K), LinkedIn |
| Массовые соцсети | 20–35 | C | Обычные X-посты, Reddit |
| Анонимные / неверифицированные | 10–20 | C | Анонимные блоги, неизвестные сайты |
| Не проверяется | 5 | C | Нет URL, нет автора |

---

## Оценка свежести (sourceFreshness)

Информация устаревает. Штрафы за давность:

| Возраст материала | sourceFreshness |
|-------------------|-----------------|
| < 6 часов | 100 |
| 6–24 часа | 90 |
| 1–3 дня | 75 |
| 3–7 дней | 55 |
| 7–30 дней | 35 |
| > 30 дней | 15 |

**Исключение:** для событий типа `legal` и `elections` исторические документы могут иметь высокий Trust даже при низкой Freshness.

---

## Оценка уникальности (sourceUniqueness)

Детектирует перепечатки и дублирование.

**Как работает v1:**
1. Группируем статьи по первоисточнику (домен + дата публикации)
2. Если 5 сайтов перепечатали Reuters — это 1 уникальный факт, не 5
3. `sourceUniqueness = 1.0` — оригинал
4. `sourceUniqueness = 0.0` — чистая перепечатка без добавленной ценности
5. Промежуточные значения — частичное добавление контекста

**Влияние на Evidence Quality Score:**
- Только уникальные факты (sourceUniqueness > 0.5) полностью засчитываются
- Перепечатки снижают вес, но не удаляются полностью

---

## Evidence Quality Score (итоговый балл)

Считается для каждого источника:

```
evidenceScore(i) = sourceTrust(i) × sourceFreshness(i)/100 × sourceUniqueness(i)
```

Итоговый **Evidence Quality Score** для всего пакета:

```
EQS = weighted_average(evidenceScore[tier_A]) × 0.60
    + weighted_average(evidenceScore[tier_B]) × 0.30
    + weighted_average(evidenceScore[tier_C]) × 0.10
```

Если нет источников tier A: используется только B и C с пересчётом весов.

| EQS | Интерпретация |
|-----|---------------|
| 80–100 | Сильная доказательная база |
| 55–79 | Умеренная база, есть надёжные источники |
| 30–54 | Слабая — в основном социальные сети или устаревшее |
| < 30 | Недостаточно — Probability Engine downweight `news_signal` |

---

## Удаление дублей и группировка

| Действие | Описание |
|----------|----------|
| **Дедупликация** | URL + первые 100 символов → если совпадают, оставляем один |
| **Группировка перепечаток** | Определяем первоисточник по домену и дате |
| **Счётчик дублей** | `duplicateCount` — сколько копий было до удаления |
| **Уникальных утверждений** | `uniqueClaimsCount` — реальное количество независимых фактов |

---

## Влияние на Probability Engine

EQS является множителем для компонентов `news_signal`, `social_signal`, `trends_signal`:

| EQS | Множитель news_signal |
|-----|----------------------|
| ≥ 80 | ×1.0 |
| 55–79 | ×0.8 |
| 30–54 | ×0.55 |
| < 30 | ×0.3 (+ флаг `weak_evidence`) |

**Если `uniqueClaimsCount = 0`:** `news_signal = 0.5` (нейтраль), флаг `no_verified_facts`.

---

## Влияние на Risk Officer

| Ситуация | Флаг |
|----------|------|
| EQS < 30 | `insufficient_evidence` |
| `uniqueClaimsCount` = 0 | `no_verified_facts` |
| Все источники tier C | `low_quality_sources_only` |
| Freshness > 72ч для time-sensitive события | `stale_evidence` |
| dominantSourceTier = C | предупреждение в verdict |

---

## Что НЕ делает этот блок

- ❌ Не собирает источники (это Evidence Collector)
- ❌ Не проверяет факты на правдивость (это Contradiction Engine)
- ❌ Не выдаёт вердикт
- ❌ Не хранит whitelist навсегда (whitelist обновляется вручную)

---

## MVP v1 — что включаем

| Функция | v1 | Позже |
|---------|----|-------|
| Статический whitelist источников с Trust-баллами | ✅ | |
| Freshness scoring | ✅ | |
| URL-дедупликация | ✅ | |
| Перепечатка-детектор (домен + дата) | ✅ | |
| EQS расчёт | ✅ | |
| ML-детектор уникальности контента (NLP) | ❌ | v2 |
| Автоматическое обновление Trust (из track record) | ❌ | v1.1 из Memory |
| API верификации источника (MediaBias, AllSides) | ❌ | v1.1 |

---

## Definition of Done

- [ ] Основатель прочитал — шкала доверия к источникам понятна
- [ ] Понятно, что 15 перепечаток Reuters = 1 факт, не 15
- [ ] Место в pipeline зафиксировано: после Evidence Collector, до Contradiction Engine

---

← [[EVENT_TYPE_CLASSIFIER]] · [[MARKET_STRUCTURE_ANALYZER]] · [[PROBABILITY_FORMULA_V1_1]]
