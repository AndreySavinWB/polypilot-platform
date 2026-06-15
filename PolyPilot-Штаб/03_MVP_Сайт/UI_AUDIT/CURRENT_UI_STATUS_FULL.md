# CURRENT_UI_STATUS_FULL.md
## Полный аудит UI — PolyPilot Platform

> **⚠️ OPEN CARD v2 baseline (14.06.2026):** актуальный статус open-карточки — [[OPEN_CARD_V2_SIMPLE]] и [[CURRENT_UI_STATUS]].  
> Этот документ (9 июня) описывает **legacy layout** до редизайна; секция `event.html` ниже устарела.

---

## МЕТАДАННЫЕ

| Параметр      | Значение                                       |
|---------------|------------------------------------------------|
| SHA коммита   | `177c06c5d4b8bb70f3fd3f150f16635f962c0429`     |
| Ветка         | `main`                                         |
| Дата анализа  | 9 июня 2026                                    |
| Аналитик      | AI Agent (Cursor)                              |
| Цель          | Полный аудит UI перед реализацией PIE v1.3     |
| Базовый URL   | https://polypilot-platform.vercel.app           |

---

## ЧАСТЬ 1. КАРТА ВСЕХ СТРАНИЦ

### 1.1 Лендинг (публичная зона)

| Роут                      | Файл                              | Существует | Готовность |
|---------------------------|-----------------------------------|------------|------------|
| `/`                       | `platform/index.html`             | ✅         | 85%        |
| `/how-it-works`           | `platform/how-it-works.html`      | ✅         | 80%        |
| `/pricing`                | `platform/pricing.html`           | ✅         | 90%        |
| `/support`                | `platform/support.html`           | ✅         | 75%        |

### 1.2 Приложение (app-зона с sidebar)

| Роут                      | Файл                              | Существует | Готовность |
|---------------------------|-----------------------------------|------------|------------|
| `/app/` или `/app/index`  | `platform/app/index.html`         | ✅         | 70%        |
| `/app/events`             | `platform/app/events.html`        | ✅         | 80%        |
| `/app/event?id=X`         | `platform/app/event.html`         | ✅         | **65%**    |
| `/app/learn`              | `platform/app/learn.html`         | ✅         | 90%        |
| `/app/settings`           | `platform/app/settings.html`      | ✅         | 60%        |
| `/app/compare`            | `platform/app/compare.html`       | ⚠️ STUB   | 5%         |
| `/app/proof-track`        | `platform/app/proof-track.html`   | ⚠️ STUB   | 5%         |
| `/app/guest-event`        | `platform/app/guest-event.html`   | ⚠️ STUB   | 5%         |
| `/app/check`              | `platform/app/check.html`         | ↪️ redirect| —          |
| `/education`              | нет отдельного файла              | ❌         | 0%         |

**Итого страниц:** 13 (из них 3 заглушки, 1 редирект, 1 отсутствует)

---

## ЧАСТЬ 2. АНАЛИЗ КАЖДОЙ СТРАНИЦЫ

---

### 📄 СТРАНИЦА 1: Главная лендинг (`/`)
**Файл:** `platform/index.html`  
**Назначение:** Первая точка контакта. Знакомство с продуктом, объяснение ценности, CTA на регистрацию / переход в app.  
**Скриншот:** `01_landing_top.png`

#### ✅ Есть
- Hero-секция: заголовок, подзаголовок, CTA кнопки
- Анонс PP AI (агентов): OnChainBot, MacroScout, RiskGuard и др.
- Preview карточек событий (демо-данные)
- Тарифная секция (Pulse / PRO)
- Секция "Как это работает"
- Социальные доказательства / доверие
- Навигация: ссылки на `events`, `how-it-works`, `pricing`, `support`

#### ⚠️ Частично есть
- Демо-карточка события: показывает `ppProb`, `edgeScore`, `riskLevel`, но без детализации PIE
- Упоминание War Room / PP AI агентов — без их реального описания

#### ❌ Нет
- Блок Event Type (тип события, классификация)
- Блок Market Structure Score
- Блок Evidence Quality Score
- Блок Contradiction Engine
- Блок Track Record / историческая точность
- Реальная live-лента событий

#### 🔮 Нужно после PIE v1.3
- Демо-карточка с новыми полями: `eventType`, `marketHealthScore`, `EQS`, `contradictionScore`
- Секция "Что умеет PIE" → объяснение 5 уровней мясорубки
- Live-тикер с топ-3 событиями дня

---

### 📄 СТРАНИЦА 2: Как это работает (`/how-it-works`)
**Файл:** `platform/how-it-works.html`  
**Назначение:** Объяснение методологии PP AI. Снятие недоверия.  
**Скриншот:** `06_how_it_works.png`

#### ✅ Есть
- Пошаговая схема работы системы (Сбор → Анализ → Прогноз → Решение)
- Описание агентов War Room
- Объяснение Edge Score
- Инфографика с примерами

#### ⚠️ Частично есть
- Описание источников данных (без весов и EQS)
- Упоминание "риск-модели" (без детального Risk Officer)

#### ❌ Нет
- Описание Event Type Classifier
- Описание Market Structure Analyzer
- Описание Source Scoring System
- Описание Probability Formula v1.1
- Описание Contradiction Engine
- Описание Comparable Events Engine
- Описание Memory / Autopsy

#### 🔮 Нужно после PIE v1.3
- Обновить диаграмму: показать все 15 блоков мясорубки
- Добавить объяснение формулы ppProb
- Добавить раздел про Track Record и Autopsy

---

### 📄 СТРАНИЦА 3: Тарифы (`/pricing`)
**Файл:** `platform/pricing.html`  
**Назначение:** Конвертация в платную подписку. Сравнение тарифов.  
**Скриншот:** `07_pricing.png`

#### ✅ Есть
- 3 тарифа: Guest / Pulse / PRO
- Сравнительная таблица возможностей
- CTA кнопки
- Trial-период

#### ⚠️ Частично есть
- Описание PIE-возможностей привязано к тарифам (War Room, Edge Score)

#### ❌ Нет
- Упоминание новых PIE-блоков как premium-фичей (Market Structure, Source Scoring, Comparable Events)
- Конкретные примеры ROI с точностью Track Record

#### 🔮 Нужно после PIE v1.3
- Добавить новые PIE-функции в сравнительную таблицу
- Показать метрику Track Record (% точности PP AI)

---

### 📄 СТРАНИЦА 4: Поддержка (`/support`)
**Файл:** `platform/support.html`  
**Назначение:** FAQ, помощь пользователям, контакты.  
**Скриншот:** `08_support.png`

#### ✅ Есть
- FAQ блок
- Форма обратной связи
- Контактные ссылки (Telegram)

#### ❌ Нет
- FAQ по PIE (как читать ppProb, что такое EQS, что такое eventType)
- Объяснение новых PIE-метрик

#### 🔮 Нужно после PIE v1.3
- Добавить FAQ раздел "Как читать PIE v1.3 данные"

---

### 📄 СТРАНИЦА 5: Дашборд приложения (`/app/`)
**Файл:** `platform/app/index.html`  
**Назначение:** Главная страница приложения после входа. Обзор лучших событий, навигация.  
**Скриншот:** `11_app_dashboard.png`

#### ✅ Есть
- Sidebar с навигацией
- Hero-секция с топ-событием дня
- Grid карточек событий
- Tier-зависимое отображение (guest/pulse/pro)
- Tier-badge и CTA разблокировки

#### ⚠️ Частично есть
- Карточки событий с `ppProb`, `edgeScore`, `riskLevel` — данные без PIE-детализации

#### ❌ Нет
- Фильтрация по `eventType`
- Отображение `marketHealthScore` в карточке
- Отображение `EQS` в карточке
- Модуль Track Record / точность прогнозов

#### 🔮 Нужно после PIE v1.3
- Добавить badge `eventType` на карточки
- Добавить `marketHealthScore` индикатор в карточку
- Панель "Результаты прогнозов" (Proof Track lite)

---

### 📄 СТРАНИЦА 6: Список событий (`/app/events`)
**Файл:** `platform/app/events.html`  
**Назначение:** Полная лента событий с фильтрацией. Основная точка работы.  
**Скриншот:** `04_events.png`

#### ✅ Есть
- Фильтры по категориям (Все / Макро / Крипта / Политика / Спорт)
- Сортировка (по Edge / Volume / Дате)
- Карточка события в закрытом виде: ppProb, edgeScore, riskLevel, volume, horizon
- Hot badge ("Возможность дня")
- Live / Demo badge
- Количество наблюдателей (`watchers`)
- Tier-блокировка (blur edgeScore для Guest)
- Поиск по событиям (UI-элемент присутствует)

#### ⚠️ Частично есть
- Категория события отображается как текстовый тег ("Макро", "Крипта") — без `eventType` + `subType` из PIE
- Объём рынка (`volume`) без `marketHealthScore`

#### ❌ Нет
- Фильтрация по `eventType` / `subType` (PIE-классификация)
- Отображение `marketHealthScore` в карточке
- Отображение `EQS` (Evidence Quality Score)
- Отображение `contradictionScore`
- Whale Activity indicator (только один из агентов упоминает whale, нет UI-элемента)
- Comparable Events link
- Источники прогноза (Source Scoring)

#### 🔮 Нужно после PIE v1.3
- Badge `eventType` (Elections / Crypto / Macro / FED / Military…)
- Индикатор `marketHealthScore` (зелёный / жёлтый / красный)
- Иконка whale-активности
- `EQS` bar на карточке
- Фильтр по типу события

---

### 📄 СТРАНИЦА 7: Детальная страница события (`/app/event?id=X`) ⭐ ГЛАВНАЯ
**Файл:** `platform/app/event.html`  
**Назначение:** Полный анализ конкретного события. Главная рабочая страница пользователя.  
**Скриншоты:** `05_event_detail.png`, `05_event_card_open.png`

#### ✅ Есть
**Block 1 — HERO**
- Заголовок, summary, категория, watchers
- 6-stat панель: Потенциал, Вероятность (ppProb), Edge Score, Volume 24h, Риск (riskLevel), Горизонт (horizon)
- Category image с gradient fallback (macro / crypto / politics)
- Hot badge

**Block 2 — AI Timeline Panel**
- Рыночная вероятность (marketOdds) ← текущая
- PP AI вероятность (aiOdds) ← цель
- Edge ← разрыв
- Интерактивный timeline с драггабельным слайдером
- Тикеры дней

**Block 3 — Opportunity Tiles (5 штук)**
- Рост обсуждений (+340%)
- Просмотры материалов (128M+)
- Позитивный сентимент (82%)
- Деньги в событии растут (volume24h)
- Рынок не догнал реальность (edgeScore)

**Block 4 — War Room / PP AI Agents**
- OnChainBot, MacroScout, RiskGuard + другие агенты
- Для каждого агента: avatar, name, role, message, verdict, detail, evidence bullets, confidence bar, sources
- Tier-блокировка: Guest видит 2 агентов, Pulse/PRO — всех

**Block 5 — История изменений (Change Map)**
- Список значимых событий с датой, описанием и Impact (positive/negative/neutral)

**Block 6 — Калькулятор позиции**
- Инпуты: сумма, тип (YES/NO), вход
- Range slider для AI-вероятности
- Выходы: прибыль, ROI, годовой эквивалент

**Block 7 — Источники данных**
- 6 иконок: Рынки, Новости, Соцсети, Видео, Поиск, История

**Block 8 — Follow / CTA**
- Кнопка "Следить за событием"
- Дисклеймер с 3 блоками (not financial advice)
- Кнопка перехода на Polymarket

#### ⚠️ Частично есть
- `warRoom.agents` содержит evidence-пункты → это proto-Evidence Collector
- `riskLevel` отображается в stats → это proto-Risk Officer
- Sources-иконки (История, Рынки) → proto-Comparable Events, proto-Market Intelligence
- Opportunity tile "Деньги в событии растут" → proto-whale/market signal

#### ❌ Нет (критические пробелы для PIE v1.3)

| PIE-компонент | Что отсутствует в UI |
|---|---|
| **Event Type Classifier** | Нет badge `eventType`/`subType`, нет `classifierConfidence` |
| **Market Structure Analyzer** | Нет `marketHealthScore`, `walletConcentration`, `whaleDominance`, `manipulationRisk`, `crowdParticipation` |
| **Source Scoring System** | Sources — просто иконки без весов. Нет `sourceTrust`, `EQS`, `evidenceScore` |
| **Contradiction Engine** | Нет dedicated блока. Нет `contradictionScore`, нет списка противоречий |
| **Comparable Events Engine** | Нет блока похожих событий. Нет исторических аналогов |
| **Probability Formula v1.1** | Показывается финальное `ppProb`, но нет breakdown: market_base, whale_signal, news_signal и т.д. |
| **Memory / Track Record** | Нет ссылки на Track Record по этому типу событий |
| **Autopsy** | Нет |

#### 🔮 Нужно после PIE v1.3 (в порядке приоритета)

1. **Event Type badge** — небольшой тег рядом с категорией (Elections / FED / Crypto / Military)
2. **PIE Probability Breakdown** — раскрываемая панель с весами компонентов ppProb
3. **Market Structure Panel** — 4-5 метрик: Market Health Score, Whale Dominance, Manipulation Risk
4. **Source Scoring Panel** — список использованных источников с весами (A/B/C tier)
5. **Contradiction Engine Block** — список противоречий между агентами / источниками
6. **Comparable Events Block** — top-3 похожих событий из истории с исходами
7. **Evidence Quality Score** — общий EQS в stats-панели и детализация

---

### 📄 СТРАНИЦА 8: Обучение (`/app/learn`)
**Файл:** `platform/app/learn.html`  
**Назначение:** Образовательный центр. Онбординг пользователей, обучение работе с PP AI.  
**Скриншот:** `09_learn.png`

#### ✅ Есть
- Hero с 6 уроками
- Learning Path (прогресс по урокам, locked/unlocked)
- Featured Lesson: "Что такое Edge Score" (развёрнутый урок)
- Карточки всех 6 уроков
- Раздел "5 ошибок"
- Глоссарий терминов (Edge, Polymarket, War Room, USDC, Горизонт)
- Чеклист перед первым решением
- CTA к событиям

#### ⚠️ Частично есть
- Описание War Room (3 агента: OnChainBot, MacroScout, RiskGuard)
- Glossary есть, но не включает новые PIE-термины

#### ❌ Нет
- Объяснение PIE v1.3 новых блоков (Event Type, Market Structure, Source Scoring, Contradiction)
- Урок "Как читать Market Structure Score"
- Урок "Как читать Evidence Quality Score"
- Урок "Что такое Contradiction Engine"

#### 🔮 Нужно после PIE v1.3
- Добавить уроки/статьи по новым PIE-компонентам
- Обновить глоссарий (EQS, eventType, manipulationRisk, contradictionScore)

---

### 📄 СТРАНИЦА 9: Настройки (`/app/settings`)
**Файл:** `platform/app/settings.html`  
**Назначение:** Управление аккаунтом. Demo-switcher тиров.  
**Скриншот:** `10_settings.png`

#### ✅ Есть
- Demo-switcher: Guest / Pulse / PRO Trial / PRO
- Текущий тир с badge
- Аккаунт-блок (Telegram auth, язык)
- Trial days остаток

#### ❌ Нет
- Настройки уведомлений
- Управление watchlist событий
- API-ключ (для PRO)

---

### 📄 СТРАНИЦА 10: Compare Terminal (`/app/compare`) — STUB
**Статус:** Phase 5 — в разработке  
**Скриншот:** `12_compare.png`

Заглушка. Описание: "Side-by-side сравнение двух рынков: вероятности, edge, аргументы PP AI."
Связь с PIE: Comparable Events Engine будет питать эту страницу.

---

### 📄 СТРАНИЦА 11: Proof Track (`/app/proof-track`) — STUB
**Статус:** Phase 5 — в разработке  
**Скриншот:** `13_proof_track.png`

Заглушка. Описание: "Таблица всех прогнозов PP: дата открытия, PP%, рыночный %, итог, точность."
Связь с PIE: Memory + Autopsy будут питать эту страницу.

---

### 📄 СТРАНИЦА 12: Guest Event Landing (`/app/guest-event`) — STUB
**Статус:** Phase 4 — в разработке  
**Скриншот:** `14_guest_event.png`

Заглушка. Описание: "60–90 сек «вау»: открытое событие с блюром edge + CTA «Войти через Telegram»."

---

## ЧАСТЬ 3. ИТОГОВАЯ ТАБЛИЦА ГОТОВНОСТИ

| Страница              | Готовность % | Критичные пробелы                               | Связь с PIE              |
|-----------------------|--------------|-------------------------------------------------|--------------------------|
| `/` (лендинг)         | 85%          | Нет PIE-компонентов в демо                      | Витрина всего PIE        |
| `/how-it-works`       | 80%          | Схема не включает PIE v1.3 блоки                | Объяснение архитектуры   |
| `/pricing`            | 90%          | Нет новых PIE-фич в таблице тарифов             | PIE как платная ценность |
| `/support`            | 75%          | Нет FAQ по PIE-метрикам                         | —                        |
| `/app/`               | 70%          | Нет eventType, marketHealth в карточках         | Дашборд PIE              |
| `/app/events`         | 80%          | Нет eventType-фильтра, EQS, whale-индикатора    | Лента PIE-данных         |
| **`/app/event`**      | **65%**      | **Нет 7 из 15 PIE-блоков**                      | **Главный экран PIE**    |
| `/app/learn`          | 90%          | Нет уроков по новым PIE-блокам                  | Онбординг PIE            |
| `/app/settings`       | 60%          | Нет watchlist, уведомлений                      | —                        |
| `/app/compare`        | 5%           | Полная заглушка                                 | Comparable Events        |
| `/app/proof-track`    | 5%           | Полная заглушка                                 | Memory + Autopsy         |
| `/app/guest-event`    | 5%           | Полная заглушка                                 | Воронка Guest→Pulse      |

---

## ЧАСТЬ 4. ПРОВЕРКА PIE v1.3 КОМПОНЕНТОВ В UI

### 4.1 Probability Engine (ppProb)

**Статус: ⚠️ ЧАСТИЧНО ГОТОВ**

| Что есть | Что отсутствует |
|---|---|
| Финальный `ppProb` отображается в stats-баре | Нет breakdown по компонентам (market_base, whale_signal, news_signal, social_signal, trends_signal, historical_base_rate, contradiction_adjustment) |
| AI Timeline показывает marketOdds → aiOdds → edge | Нет отображения весов и модификаторов (market_reliability_mult, EQS_mult) |
| Edge Score виден в карточке | Нет explainability-блока "Почему именно X%" |

**Что нужно:** Раскрываемая панель "Из чего состоит вероятность" с вкладом каждого из 7 компонентов (визуализация bar chart).

---

### 4.2 Evidence Collector / отображение доказательств

**Статус: ⚠️ ЧАСТИЧНО ГОТОВ**

| Что есть | Что отсутствует |
|---|---|
| Каждый агент War Room имеет `evidence[]` — список пунктов-доказательств | Нет единого списка всех доказательств по событию |
| Sources-иконки (6 штук) | Нет отдельного Evidence Panel с группировкой по источникам |
| Opportunity Tiles частично показывают data-сигналы | Нет `sourceFreshness`, `sourceTrust`, `duplicateCount` |

**Что нужно:** Блок "Доказательная база" с grouped evidence items и метаданными источников.

---

### 4.3 Market Intelligence

**Статус: ✅ ДОСТАТОЧНО ДЛЯ MVP**

| Что есть | Что отсутствует |
|---|---|
| `marketOdds` (рыночная вероятность) | Детали ликвидности orderbook |
| `volume`, `volume24h` | |
| AI Timeline (market vs AI) | |
| Opportunity tile "Деньги в событии растут" | |

Данные рыночной вероятности и объёма присутствуют и хорошо отображаются.

---

### 4.4 Market Structure Analyzer

**Статус: ❌ НЕ ГОТОВ**

| Что есть | Что отсутствует |
|---|---|
| Один opportunity tile про рост денег в событии | `marketHealthScore` |
| Нет выделенного блока | `walletConcentration` |
| | `whaleDominance` |
| | `manipulationRisk` |
| | `crowdParticipation` |
| | Market Structure Score badge |

**Что нужно:** Отдельная панель "Структура рынка" в event.html с 4-5 метриками и traffic-light индикатором.

---

### 4.5 Contradiction Engine

**Статус: ❌ НЕ ГОТОВ**

В UI нет никакого отображения Contradiction Engine. Нет `contradictionScore`, нет списка противоречивых сигналов, нет UI-блока.

**Что нужно:** Секция "Противоречия" в event.html — список конфликтующих сигналов с весом каждого.

---

### 4.6 Track Record / Memory

**Статус: ❌ НЕ ГОТОВ**

`/app/proof-track` — полная заглушка Phase 5. На странице события нет ссылки на историческую точность по данному типу событий.

**Что нужно:**
- Минимальный Track Record widget в sidebar или event.html: "PP AI точность по этому типу: X%"
- Реализация Proof Track страницы (Phase 5)

---

### 4.7 Source Scoring System (EQS)

**Статус: ❌ НЕ ГОТОВ**

Источники данных есть как иконки (6 штук), но нет:
- Весов источников (tier A/B/C)
- `sourceTrust` per источник
- `evidenceScore` и суммарного `EQS`
- Флага дубликатов/перепечаток

**Что нужно:** В war room и opportunity tiles → добавить `trust` badge рядом с каждым источником; отдельный EQS индикатор в stats-панели.

---

### 4.8 Whale Signals

**Статус: ⚠️ ЧАСТИЧНО**

| Что есть | Что отсутствует |
|---|---|
| Opportunity tile "Деньги в событии растут" показывает приток | Нет whale-специфичного блока |
| Агент (MacroScout / OnChainBot) может упоминать whale | Нет `whaleDominance` метрики |
| | Нет whale wallet tracker |

---

### 4.9 Event Type Classifier

**Статус: ❌ НЕ ГОТОВ**

Текущий UI использует грубые категории: "Макро", "Крипта", "Политика". PIE-классификация предполагает:
- `eventType` (Elections, FED, Crypto-ETF, Military, Corporate…)
- `subType`
- `classifierConfidence`

Ни одного из этих полей не отображается. Категория — это статичный текст, а не PIE-output.

**Что нужно:** Badge `eventType` рядом с категорией в event.html и events.html; фильтр по `eventType` в ленте.

---

## ЧАСТЬ 5. UX-АНАЛИЗ

### 5.1 Сильные стороны текущего UI

1. **Карточка события** хорошо структурирована: 6-stat панель сразу даёт ключевые числа
2. **AI Timeline** с интерактивным слайдером — сильный визуальный элемент, нагляден
3. **War Room** с агентами — уникальный UX, объясняет "почему такой прогноз"
4. **Tier-gate система** реализована грамотно: blur + CTA не агрессивны
5. **Learn страница** — профессиональный образовательный центр, высокий уровень
6. **Settings demo-switcher** — удобен для разработки и демо

### 5.2 Где пользователь может запутаться

1. **"Вероятность PP AI" vs "Рыночная вероятность"** — без объяснения формулы пользователь не понимает, откуда берётся ppProb
2. **Opportunity Tiles** — разные источники данных без указания качества источника (почему именно этим источникам доверять?)
3. **War Room агенты** — у Pulse-пользователя видны только 2 из N агентов → ощущение "неполного анализа"
4. **Нет контекста похожих событий** → пользователь не может оценить "это нормально или нет?"
5. **Нет Track Record** → нет доверия к прогнозу ("PP AI когда-нибудь ошибался?")

### 5.3 Где не хватает доверия

1. **Нет Track Record виджета** — критически важно для conversion. Пользователь не знает точность PP AI
2. **Source Quality** неизвестна — "Рынки, Новости, Соцсети" без весов кажутся неточными
3. **Нет contradictionScore** — если сигналы противоречивы, пользователь должен это видеть
4. **Probability breakdown отсутствует** — "74%" без объяснения — это число из воздуха для скептика

### 5.4 Какие блоки нужны для PIE v1.3

| Блок | Новый/Доработка | Приоритет |
|---|---|---|
| Event Type badge | Доработка существующей категории | 🔴 Высокий |
| PIE Probability Breakdown panel | Новый блок | 🔴 Высокий |
| Market Structure Panel | Новый блок | 🔴 Высокий |
| Source Quality / EQS indicator | Доработка Sources-иконок | 🟡 Средний |
| Contradiction Engine block | Новый блок | 🟡 Средний |
| Comparable Events block | Новый блок | 🟡 Средний |
| Track Record widget | Новый (mini) | 🔴 Высокий |
| Whale Activity indicator | Доработка Opportunity Tiles | 🟡 Средний |

### 5.5 Что можно удалить без потери смысла

1. **Opportunity Tile "Просмотры материалов (128M+)"** — метрика неинформативна для prediction market
2. **Статичные источники-иконки** в footer карточки → заменить на Source Scoring Panel
3. **Двойное дублирование Edge** (в stats-баре и в AI Timeline) → можно объединить

---

## ЧАСТЬ 6. ИТОГОВЫЕ ВЫВОДЫ

### Готовность сайта под MVP: **72%**

Ключевые MVP-элементы (лента событий, карточка события, War Room, Edge Score, tier-gate) реализованы. Основной пользовательский путь работает.

### Готовность сайта под PIE v1.3: **35%**

Из 15 PIE-блоков отображаются полностью или частично только 5:
- ✅ Market Intelligence (отображение market odds, volume) — **готов**
- ⚠️ Probability Engine (только финальное ppProb) — **частично**
- ⚠️ Evidence Collector (bullets в агентах) — **частично**
- ⚠️ Risk Officer (riskLevel badge) — **частично**
- ⚠️ Market Scanner / Priority Gate (tier-gate, hot badge) — **частично**

Не отображаются совсем:
- ❌ Event Type Classifier
- ❌ Market Structure Analyzer
- ❌ Source Scoring System / EQS
- ❌ Contradiction Engine
- ❌ Comparable Events Engine
- ❌ Memory / Track Record
- ❌ Autopsy / Learning Loop

---

### Критичные доработки (до запуска PIE v1.3)

1. `event.html` — добавить Event Type badge (`eventType` + `subType`)
2. `event.html` — добавить PIE Probability Breakdown панель (7 компонентов + веса)
3. `event.html` — добавить Market Structure Panel (marketHealthScore, whaleDominance, manipulationRisk)
4. `event.html` — добавить Track Record mini-widget ("Точность PP AI по этому типу: X%")
5. `events.html` — добавить фильтр по `eventType`
6. `event.html` — добавить EQS индикатор в stats-панель

### Желательные доработки

7. `event.html` — блок Contradiction Engine (список противоречий)
8. `event.html` — блок Comparable Events (top-3 похожих событий)
9. `events.html` — whale-иконка на карточках
10. `learn.html` — уроки по новым PIE-компонентам
11. `/how-it-works` — обновить диаграмму под PIE v1.3

### Что оставить на V2

- `/app/compare` (Compare Terminal) — Phase 5, зависит от Comparable Events Engine
- `/app/proof-track` (Proof Track) — Phase 5, зависит от Memory + Autopsy
- `/app/guest-event` (Guest Landing) — Phase 4, маркетинговая страница
- Детальный Autopsy-экран (разбор завершённых прогнозов)
- Push-уведомления об изменениях в событии
- API-ключ и programmatic access (PRO+)

---

## СКРИНШОТЫ

| Файл | Страница |
|---|---|
| `01_landing_top.png` | Главная лендинг |
| `04_events.png` | Список событий |
| `05_event_detail.png` | Карточка события (hero) |
| `05_event_card_open.png` | Карточка события (War Room) |
| `06_how_it_works.png` | Как это работает |
| `07_pricing.png` | Тарифы |
| `08_support.png` | Поддержка |
| `09_learn.png` | Обучение |
| `10_settings.png` | Настройки |
| `11_app_dashboard.png` | Дашборд приложения |
| `12_compare.png` | Compare Terminal (stub) |
| `13_proof_track.png` | Proof Track (stub) |
| `14_guest_event.png` | Guest Event Landing (stub) |
