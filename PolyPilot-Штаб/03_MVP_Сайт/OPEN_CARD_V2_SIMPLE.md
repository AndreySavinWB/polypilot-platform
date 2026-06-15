# OPEN CARD v2 — Simple Open Card (отправная точка)

> **Baseline:** `bc48e47` · 14 июня 2026  
> **Код:** `platform/assets/js/simple-open-card.js` · `platform/assets/css/simple-open-card.css`  
> **Страница:** `platform/app/event.html` → `PP_SIMPLE_OPEN.renderPage(ev, opts)`  
> **Следующий шаг:** подкапотка — pipeline → поля карточки для всех live-событий

← [[AI_КАРТОЧКА_СОБЫТИЯ]] · [[CURRENT_UI_STATUS]] · [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]]

---

## Принцип

Одна линейная карточка для **всех** открытых событий (demo + live).  
Нет War Room-аккордеона, PIE-панели, калькулятора и блока «Подробная аналитика» — только 9 секций + footer.

**Единая логика:** секции 3–5 **всегда** на экране; при отсутствии данных — placeholder, не скрытие блока.

---

## Порядок секций (фиксированный)

| # | Заголовок | Renderer | Обязательность |
|---|-----------|----------|----------------|
| 0 | Top bar | `renderTopBar` | всегда |
| — | Баннер ДЕМО/ОНЛАЙН | `opts.sourceBanner` | из `event.html` |
| 1 | **Вывод за 10 секунд** | `renderVerdictSection` | всегда |
| 2 | **Почему PolyPilot так думает** + риски | `renderAnalysisDuo` | всегда (fallback DEFAULT_REASONS / DEFAULT_RISKS) |
| 3 | **Анализ комментариев** | `renderCrowdPulseSection` | всегда |
| 4 | **Данные с Polymarket Analytics** | `renderExternalMarketCheckSection` | всегда |
| 5 | **Крупные игроки** | `renderWhaleCheckSection` | всегда |
| 6 | **Мы проверили** | `renderCheckedSection` | всегда (эвристика или `checkedReview`) |
| 7 | **Итоговый вывод** | `renderFinalConclusionSection` | всегда |
| 8 | **Что делать** | `renderActionsSection` | всегда |
| 9 | **Изменения по событию** | `renderChangesSection` | всегда |
| — | Footer | ID + источники | всегда |

---

## Блок 1 — Вывод за 10 секунд

**VS-трио:** Рынок | EDGE + горизонт (центр) | PolyPilot  
Стиль: фиолетовый/зелёный, бейдж EDGE, горизонт в центре.

| Поле | Назначение | Fallback |
|------|------------|----------|
| `title` | H1 | «—» |
| `category` / `simpleCategoryLabel` | мета-строка | через `PP_SIMPLE_CARD.getCategoryLabel` |
| `horizon` / `horizonShort` | мета + центр VS | «—» |
| `marketOdds` | колонка «Рынок» | 50% |
| `aiOdds` | колонка «PolyPilot» | `confidence` → 50% |
| `edgeScore` | бейдж EDGE | вычисляется из delta |
| `simpleVerdict` / `simpleVerdictTone` | live-тон | вычисляется из odds |

**Правило:** `aiOdds` = каноническая PP-вероятность; должна совпадать с `proofTrack.ppOdds`.

---

## Блок 2 — Почему / Риски

| Поле | Назначение |
|------|------------|
| `arguments.yes[]` | аргументы «за» |
| `warRoom.agents[]` (не risk) | доп. аргументы из агентов |
| `riskTags[]` / `arguments.no[]` | риски |
| `riskLevel` | только для pill «Риск» в блоке 7 |

---

## Блоки 3–5 — Pipeline-секции (empty-state)

### crowdPulse

| Статус | UI |
|--------|-----|
| нет объекта / `insufficient` | «Недостаточно комментариев для вывода.» |
| `ready` + данные | lean, summaryRu, noiseLevel, synthesis |

### externalMarketCheck

| Статус | UI |
|--------|-----|
| нет / not found | «Событие не найдено на Polymarket Analytics.» |
| `found` / `similar_found` | observationsRu, summaryRu, forecastImpact |

### whaleCheck

| Статус | UI |
|--------|-----|
| нет / `no_data` / `not_found` / `error` | «Данных по крупным игрокам нет.» |
| `ready` | headlineRu, объёмы YES/NO, skew, explanationRu |

**Завтра (backend):** `sync_live_to_mvp.py` → эти три блока для **всех** live-событий, не только `live-79061`.

---

## Блок 6 — Мы проверили

12 чипов каталога. Источники:

1. Явный `checkedReview.chips[]` (идеал, pipeline)
2. Эвристика: `title`, `summary`, `resolveDate`, `news[]`, `warRoom`, `crowdPulse`, `marketOdds`, `riskTags`, `proofTrack.opened`

**Важно:** stub-источники (`*_stub`, `*_mock` в `dataSource`) показывают контент в секциях 3–5, но **не** отмечают чип «проверено» (`isRealDataSource`).

---

## Блок 7 — Итоговый вывод

| Поле | Назначение |
|------|------------|
| `verdictText` | основной текст |
| `whaleCheck.explanationRu` | поддержка |
| `crowdPulse.synthesis.summaryRu` | поддержка |
| `confidence` (0–100) | pill «Уверенность» (≥70 высокая, ≥50 средняя) |
| `riskLevel` | pill «Риск» |

---

## Блоки 8–9 — CTA и изменения

**CTA:** Polymarket, PRO-бот, guest-share — из `opts` в `event.html`.

**Изменения:** `changes[]` или авто из `proofTrack.marketOddsAtOpen` vs `marketOdds`; иначе «Пока существенных изменений нет».

---

## Единый контракт данных (open events)

### Обязательный минимум (demo + live)

```text
id, title, category*, status, marketOdds, aiOdds, edgeScore, riskLevel,
confidence, verdictText, arguments?, riskTags?, warRoom?, proofTrack?
```

\* live: `simpleCategory`, `simpleCategoryLabel`, `horizonShort` — предпочтительно

### Pipeline-расширение (цель для всех live)

```text
crowdPulse, externalMarketCheck, whaleCheck, checkedReview
```

### Соглашения

| Правило | Demo | Live |
|---------|------|------|
| `aiOdds` = `proofTrack.ppOdds` | ✅ выровнено | ✅ |
| `edgeDirection` | `"YES"` | `"ДА"` (closed card нормализует) |
| `news[]` | часто заполнен | пока `[]` |
| `changes[]` | 2 события | пока `[]` |
| Pipeline-блоки | empty-state | только `live-79061` (stub) |

---

## Инвентарь событий (open)

### Demo — 8 (`events-data.js`)

| ID | Pipeline | War Room | changes |
|----|----------|----------|---------|
| fed-rate-july-2026 | empty | 5 агентов | 6 |
| btc-150k-2026 | empty | 5 агентов | 6 |
| trump-approval-q3-2026 | empty | 5 агентов | — |
| openai-gpt6-2026 | empty | пусто | — |
| mbapp-ballon-dor-2026 | empty | пусто | — |
| eu-recession-2026 | empty | пусто | — |
| horizons-film-2026 | empty | пусто | — |
| tesla-robotaxi-2026 | empty | пусто | — |

### Live — 5 (`events-live.js`)

| ID | Pipeline |
|----|----------|
| live-69702 | empty |
| live-73212 | empty |
| live-79050 | empty |
| **live-79061** | crowdPulse + PMA + whale (stub) |
| live-40270 | empty |

---

## Что убрано (legacy в `event.html`)

- Hero + AI Timeline slider
- «Почему мы видим возможность» (6 stat-блоков)
- War Room аккордеон на странице
- Калькулятор прибыли
- Блок «Подробная аналитика» (PIE, War Room PRO-слой)
- `pie-api.js` больше не подключается на `event.html`

CSS/JS legacy в файле остаётся — **не рендерится**; cleanup — отдельная задача.

---

## Завтра: подкапотка под этот визуал

| # | Задача | Владелец |
|---|--------|----------|
| 1 | Расширить `sync_live_to_mvp.py` — crowdPulse / PMA / whale для всех live | Backend |
| 2 | `checkedReview` из pipeline → чипы «Мы проверили» | Backend |
| 3 | `aiOdds` / `verdictText` / `arguments` из PIE Probability + Evidence | Backend |
| 4 | Удалить мёртвый CSS/JS из `event.html` | UX/UI |
| 5 | Скриншот `05_event_card_open.png` под v2 | UX/UI |

**Критерий готовности этапа:** любое live-событие открывается с тем же 9-блочным layout; секции 3–5 с реальными или осмысленными stub-данными, не только placeholder.

---

## Связанные файлы

| Файл | Роль |
|------|------|
| `simple-open-card.js` | единственный рендер open card |
| `simple-closed-card.js` | closed card (лента, hero) |
| `events-store.js` | merge live + demo, флаги `isLive` / `isDemo` |
| `events-live.js` | auto-generated из backend |
| `backend/scripts/sync_live_to_mvp.py` | sync pipeline → frontend |
