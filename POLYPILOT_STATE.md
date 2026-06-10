# POLYPILOT STATE

> Главный оперативный статус проекта и единый источник правды для всех команд: `01_CEO`, `02_Product Manager`, `03_UX/UI Designer`, `04_Backend Dev`.

---

## Последний коммит

**SHA:** `ce144611ca071d9a97c9ca40afff5f77d850ec2b`  
**Дата:** 2026-06-10 17:33:45 +03:00

---

## Текущий этап

**Текущая фаза:** checkpoint PIE v1.0d опубликован на GitHub, Vercel деплоит UI-каркас.  
**Текущий владелец:** `01_CEO`

Главное узкое место сейчас: UI пока на mock-данных — нужен следующий backend-срез или подключение PIE-output к `event.html`.

---

## Что готово

- Архитектура PIE v1.3 зафиксирована.
- Документы по новым PIE-блокам созданы:
  - Event Type Classifier
  - Market Structure Analyzer
  - Source Scoring System
  - Probability Formula v1.1
- Полный UI-аудит платформы выполнен.
- UI-каркас PIE v1.3 в `platform/app/event.html` принят.
- Backend-срез PIE v1.0b реализован:
  - Event Normalizer v0
  - Event Type Classifier v0
  - контракт `normalizedEvent + eventClassification + pipelineStatus`
  - smoke-test на 10 событиях проходит
- Backend-срез PIE v1.0c реализован:
  - Market Intelligence v0
  - `moneyDirection`
  - `volumeSignal`
  - `volumeAnomaly`
  - `whaleSignal` как эвристический placeholder
  - `confidence` capped at 0.50
  - `anomalies[]`
  - smoke-test на 10 событиях проходит
- Backend-срез PIE v1.0d реализован:
  - Evidence Collector v0
  - `evidence.items[]` из внутренних данных: `market` + `official`
  - `counts` по типам источников
  - `collectionStatus`
  - `scoringMode = rules_v0`
  - smoke-test на 10 событиях проходит
- Командная структура чатов зафиксирована:
  - `01_CEO`
  - `02_Product Manager`
  - `03_UX/UI Designer`
  - `04_Backend Dev`
- Создана операционная система управления проектом:
  - `POLYPILOT_STATE.md`
  - `CEO_OPERATING_SYSTEM.md`

---

## Что в работе

- Ожидание деплоя Vercel после checkpoint-коммита.
- Решение CEO: следующий backend-срез (Market Structure Analyzer v0) или wiring UI ↔ backend.
- Формирование привычки команды: перед началом работы читать `POLYPILOT_STATE.md`.

---

## Блокеры

- UI пока не подключён к реальному backend-output PIE.
- `titleRu` в smoke-test остаётся на английском без LLM-ключа.
- Event Type Classifier v0 даёт rule-based misfire на edge cases: 2 из 10 тестовых событий.
- Market Intelligence работает только на данных Polymarket, без whale API.
- `marketIntelligence.confidence` ограничен 0.50 из-за отсутствия внешних MI-источников.
- `whaleSignal` является эвристикой по объёму и направлению, а не реальными кошельками.
- Evidence Collector v0 не подключает внешние источники, только `market` + `official`.
- `collectionStatus = partial` у всех тестовых событий, потому что нет реальных News API / RSS / Trends.
- Market Structure, Source Scoring и Probability Engine пока не реализованы.

---

## Следующий шаг

Checkpoint-коммит выполнен и опубликован (`ce14461`).

Следующий шаг CEO:

```text
Выбрать один из двух путей:
A) Backend: Market Structure Analyzer v0
B) Integration: подключить PIE v1.0d output к UI-каркасу event.html
```

Последний принятый backend-output:

```json
{
  "normalizedEvent": {
    "titleRu": "...",
    "resolutionCriteria": "...",
    "horizonDays": 42,
    "decisionMaker": "...",
    "marketSnapshot": {
      "marketProb": 0.56,
      "volume": 1200000,
      "liquidity": 240000
    },
    "normalizationStatus": "ok",
    "marketSnapshot": {
      "marketProb": 0.44,
      "volume": 33387971,
      "liquidity": 1961217
    }
  },
  "eventClassification": {
    "eventType": "regulatory",
    "subType": "fed_rate",
    "classifierConfidence": 0.87,
    "analysisProfile": "macro_regulatory"
  },
  "marketIntelligence": {
    "moneyDirection": "yes",
    "volumeSignal": "rising",
    "volumeAnomaly": "moderate",
    "whaleSignal": "none",
    "confidence": 0.5,
    "anomalies": [
      {
        "type": "volume_spike",
        "description": "24h volume is 1.8x average daily volume",
        "severity": "medium"
      }
    ],
    "scoringMode": "rules_v0"
  },
  "evidence": {
    "items": [
      {
        "type": "market",
        "title": "Рыночный сигнал Polymarket",
        "source": "Polymarket",
        "supportsOutcome": "yes",
        "confidence": 0.5
      },
      {
        "type": "official",
        "title": "Источник резолва",
        "supportsOutcome": "unknown",
        "confidence": 0.3
      }
    ],
    "counts": {
      "total": 2,
      "official": 1,
      "news": 0,
      "social": 0,
      "trends": 0,
      "market": 1
    },
    "collectionStatus": "partial",
    "scoringMode": "rules_v0"
  },
  "pipelineStatus": "v1_0d_complete"
}
```

---

## Последнее решение CEO

Checkpoint-коммит опубликован на GitHub/Vercel: UI-каркас PIE v1.3 + Project Operating System + Backend PIE v1.0b–v1.0d.

Backend-срез PIE v1.0d принят: Event Normalizer v0 + Event Type Classifier v0 + Market Intelligence v0 + Evidence Collector v0.

До решения CEO по следующему backend-фокусу не начинаем:

- новые UI-задачи;
- новые страницы;
- оплату;
- auth;
- Track Record;
- Autopsy;
- Compare Terminal;
- новых агентов.

---

## Последнее изменение архитектуры

PIE v1.3 утверждён как основа дальнейшей разработки.

Ключевые блоки v1.3:

- Event Type Classifier
- Market Structure Analyzer
- Source Scoring System
- Probability Formula v1.1

Архитектуру сейчас не расширяем.

---

## Последнее изменение UI

`03_UX/UI Designer` добавил и доработал UI-каркас PIE v1.3 в открытой карточке события `platform/app/event.html`.

Приняты 8 блоков:

1. Разбивка вероятности PP AI
2. Тип события
3. Разведка рынка
4. Структура рынка
5. Качество источников
6. Карта противоречий
7. Исторические аналоги
8. История точности PP

Статус: принято CEO.

---

## Последнее изменение Backend

Backend-срез PIE v1.0d реализован.

Реализовано:

- Event Normalizer v0
- Event Type Classifier v0
- Market Intelligence v0
- Evidence Collector v0
- `backend/src/agents/normalizer.py`
- `backend/src/agents/classifier.py`
- `backend/src/agents/market_intelligence.py`
- `backend/src/agents/evidence_collector.py`
- `backend/src/agents/pie.py`
- `backend/scripts/test_pie.py`
- endpoint `/api/pie/process`

Проверка:

- smoke-test проходит на 10 событиях;
- контракт `normalizedEvent + eventClassification + marketIntelligence + evidence + pipelineStatus` соблюдён;
- classifier имеет 2/10 misfire на edge cases, это не блокер для v0.

---

## Последнее изменение Product

Продуктовый фокус зафиксирован:

- не строить весь PIE сразу;
- двигаться вертикальными срезами;
- сначала получить реальные PIE-данные;
- затем подключать эти данные в уже подготовленный UI;
- монетизацию и расширенные продуктовые фичи отложить до проверки ценности.

---

## Правило Обновления

Любая завершённая задача считается незавершённой, пока не обновлён `POLYPILOT_STATE.md`.

Это правило обязательно для всех команд:

- `02_Product Manager`
- `03_UX/UI Designer`
- `04_Backend Dev`

После завершения задачи команда должна вернуть в `01_CEO`:

```text
Что сделано
Какие файлы изменены
Что изменилось в статусе проекта
Как нужно обновить POLYPILOT_STATE.md
```

---

## Ответственный За Актуальность

Главный ответственный: `01_CEO`.

Правило ответственности:

- команда выполняет задачу и сообщает, что изменилось;
- `01_CEO` принимает результат;
- `01_CEO` обновляет `POLYPILOT_STATE.md` или явно поручает это команде;
- без обновления state задача не считается закрытой.
