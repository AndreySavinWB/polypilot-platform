# Анализ комментариев (Comment Analysis) — v1

> [[INTELLIGENCE_DATA_FLOW]] · [[СХЕМА_ДАННЫХ_СОБЫТИЯ]] · [[СХЕМА_МЯСОРУБКИ]] · [[PROBABILITY_INTELLIGENCE_ENGINE]]

> **Версия:** `comment_analysis_v1` · **Статус:** MVP mock + UI · **Дата:** 14 июня 2026

---

## Зачем отдельный модуль

Два разных типа обсуждений **нельзя смешивать**:

| Блок | Что это | Кто говорит |
|------|---------|-------------|
| **5.5A** | Комментарии внутри события | Участники конкретного рынка Polymarket |
| **5.5B** | Обсуждение в сети | X, Reddit, YouTube, Telegram, медиа, форумы |
| **5.5C** | Сводный вывод | PolyPilot сравнивает A и B |

Комментарии — **вспомогательный сигнал**, не главный источник прогноза.

**Веса (ориентир):**

- комментарии внутри события: **0–7%**
- соцсети: **0–5%**
- **Crowd Pulse суммарно: ≤ 10%**

При спорном резолве, новом официальном источнике или сильном риске — флаги в **Risk Officer**.

---

## Место в pipeline (Simple Events / PIE)

```text
0.  Политика простоты
1.  Сканер событий
2.  Фильтр простоты
3.  Нормализатор события
4.  Категорийный аналитик
5.  Сбор доказательств
5.5A Комментарии внутри события      → crowdPulse.marketComments
5.5B Обсуждение в сети                → crowdPulse.socialDiscussion
5.5C Сводный вывод                   → crowdPulse.synthesis
6.  Карта противоречий
7.  Расчёт вероятности PP
8.  Риск-офицер
9.  Итоговый вывод
9.5 Редакторский слой
10. Андрей одобряет
11. Публикация / контент-пак
12. Отслеживание результата
13. Track record / кейс-лента
```

**Код MVP:** `backend/src/agents/comment_analysis.py` · mock для `79061` (Tesla robotaxi).

---

## Контракт `crowdPulse`

Публикуется в `pipelinePackage.crowdPulse` и на live-карточке как `ev.crowdPulse`.

```json
{
  "status": "ready|insufficient|noisy",
  "maxWeightPct": 10,
  "marketComments": { "...": "5.5A" },
  "socialDiscussion": { "...": "5.5B" },
  "synthesis": { "...": "5.5C" },
  "scoringMode": "mock_v1|stub_v0"
}
```

### 5.5A — `marketComments`

| Поле | Тип | Описание |
|------|-----|----------|
| `commentCount` | number | Сколько комментариев найдено |
| `lean` | yes/no/split/unclear | Склонение участников рынка |
| `argumentsYes` | string[] | Аргументы за YES |
| `argumentsNo` | string[] | Аргументы за NO |
| `resolutionDispute` | boolean | Спор по правилам резолва |
| `hasSourceLinks` | boolean | Есть ссылки на источники |
| `noiseSignals` | string[] | troll, pump, manipulation… |
| `quality` | high/medium/low | Качество обсуждения |
| `noiseLevel` | low/medium/high | Уровень шума |
| `summaryRu` | string | Короткая выжимка |
| `weightPct` | 0–7 | Вес для PP |
| `dataSource` | string | `polymarket_comments_stub` в MVP |

### 5.5B — `socialDiscussion`

| Поле | Тип | Описание |
|------|-----|----------|
| `sources` | array | platform, found, activityTrend |
| `lean` | yes/no/split/unclear | Склонение внешней аудитории |
| `arguments` | string[] | Главные аргументы |
| `freshFacts` | boolean | Есть свежие факты |
| `viralHype` | boolean | Вирусный хайп |
| `expertSources` | boolean | Экспертные/официальные источники |
| `quality` | high/medium/low | |
| `noiseLevel` | low/medium/high | |
| `summaryRu` | string | |
| `weightPct` | 0–5 | |
| `dataSource` | string | `social_stub` в MVP |

### 5.5C — `synthesis`

| Поле | Тип | Описание |
|------|-----|----------|
| `alignment` | aligned/divergent/partial | Совпадают ли A и B |
| `contradiction` | string | Где противоречие |
| `repeatedArgument` | string | Повторяющийся аргумент |
| `mainRiskFromDiscussion` | string | Главный риск из обсуждений |
| `forecastImpact` | positive/negative/neutral/weak_* | Влияние на прогноз |
| `probabilityAdjustPct` | number | Сдвиг PP (малый) |
| `summaryRu` | string | Общий вывод для UI |
| `totalWeightPct` | ≤10 | |
| `passToRiskOfficer` | string[] | Флаги для шага 8 |

---

## UI (Simple open card)

Блок **«Анализ комментариев»** — три части:

1. **Внутри события** — lean, главная мысль, шум  
2. **В сети** — lean, главная мысль, шум  
3. **Общий вывод**

Рендер: `platform/assets/js/simple-open-card.js` → `renderCrowdPulseSection()`.

**Правила UX:**

- Не писать «толпа считает» без уточнения, какая именно.
- Если данных нет: «Недостаточно комментариев для вывода».
- Если шум высокий: «Обсуждение шумное, влияние на прогноз слабое».
- Закрытую карточку не трогаем.

---

## MVP / заглушки

| Компонент | Статус |
|-----------|--------|
| Polymarket Comments API | ❌ stub |
| X / Reddit / YouTube / Telegram collectors | ❌ stub |
| LLM summarization RU | ❌ ручной mock |
| Tesla `live-79061` mock | ✅ |
| UI open card | ✅ |
| Probability Engine weight | ❌ не подключено |
| Risk Officer auto-flags | ❌ не подключено |

---

## Связь с другими полями

- **`evidence.social[]`** — сырые соцсигналы на шаге 5; **не заменяет** `crowdPulse`.
- **`marketStructure.crowdParticipation`** — объём торгов, **не sentiment комментариев**.
