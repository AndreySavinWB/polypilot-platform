# CURRENT_UI_STATUS — Аудит UI PolyPilot

> **Обновлено:** 14 июня 2026 · baseline **OPEN CARD v2** (`bc48e47`)  
> Спецификация карточки: [[OPEN_CARD_V2_SIMPLE]]  
> Предыдущий аудит (9 июня, legacy layout): см. историю git

---

## Метаданные релиза

| Параметр | Значение |
|----------|---------|
| **SHA коммита** | `bc48e47` |
| **Ветка** | `main` |
| **Дата аудита** | 14 июня 2026 |
| **Baseline** | Simple Open Card v2 — 9 секций, единый `renderPage()` |
| **Репозиторий** | https://github.com/AndreySavinWB/polypilot-platform |
| **Prod URL** | https://polypilot-platform.vercel.app || **Backup URL** | https://andreysavinwb.github.io/polypilot-platform/app/events.html |

---

## Часть 1. Скриншоты

Скриншоты сохранены в папку: `PolyPilot-Штаб/03_MVP_Сайт/UI_AUDIT/`

| Файл | Страница |
|------|---------|
| `01_landing_top.png` | Главная — Hero секция |
| `04_events.png` | Страница событий |
| `05_event_detail.png` | Событие без ID (ошибка) |
| `05_event_card_open.png` | Открытая карточка события (demo ID) |
| `06_how_it_works.png` | Как это работает |
| `07_pricing.png` | Тарифы |
| `08_support.png` | Поддержка |

---

## Часть 2. Карта страниц

| Роут | Файл | Существует | Готовность |
|------|------|-----------|-----------|
| `/` | `platform/index.html` | ✅ | **95%** — Лендинг |
| `/app/events.html` | `app/events.html` | ✅ | **85%** — Лента событий |
| `/app/event.html?id=X` | `app/event.html` | ✅ | **85%** — OPEN CARD v2 (Simple Open Card) |
| `/app/how-it-works.html` | `app/how-it-works.html` | ✅ | **90%** — Объяснения |
| `/app/pricing.html` | `app/pricing.html` | ✅ | **90%** — Тарифы |
| `/app/support.html` | `app/support.html` | ✅ | **80%** — Поддержка |
| `/app/check.html` | `app/check.html` | ✅ | **60%** — PP Check (отдельная) |
| `/app/compare.html` | `app/compare.html` | ✅ | **40%** — Сравнение событий |
| `/app/proof-track.html` | `app/proof-track.html` | ✅ | **50%** — Трек-рекорд |
| `/app/learn.html` | `app/learn.html` | ✅ | **30%** — Обучение |
| `/app/settings.html` | `app/settings.html` | ✅ | **40%** — Настройки |
| `/app/guest-event.html` | `app/guest-event.html` | ✅ | **50%** — Guest-режим |
| `/app/index.html` | `app/index.html` | ✅ | **60%** — Dashboard |

**Итого: 13 страниц, все существуют.**

---

## Часть 3. Навигация

**Лендинг (`index.html`) — верхнее меню:**
- События → `app/events.html`
- Как это работает → `app/how-it-works.html`
- Тарифы → `app/pricing.html`

**Sidebar приложения (`layout.css` + `sidebar.js`):**
- Главная, События, Как это работает, Обучение, Поддержка, Тарифы, Настройки
- Внизу: «АККАУНТ» + кнопка ГОСТЬ

---

## Часть 4. Реальные блоки страниц

### Главная (`index.html`)

#### Есть
- ✅ NAV — логотип, меню, CTA-кнопки (Войти через Telegram)
- ✅ Hero — заголовок «AI видит, где рынок ошибается», демо-карточка с 38% vs 54% + edge +16%
- ✅ Stats strip — 4 цифры: 5 PP AI, 71% точность, +8.3%, 100% открытый
- ✅ «Как это работает» — 3 шага с иконками и стрелками
- ✅ Advantages — PP vs Polymarket сравнение (2 колонки)
- ✅ Hot events — 3 мини-карточки из EVENTS_DATA (JS-рендер)
- ✅ Proof section — 3 карточки прошлых прогнозов + статистика справа
- ✅ Pricing section — 3 тарифа: Guest/Pulse/PRO
- ✅ Final CTA banner — градиент, «Войти через Telegram»
- ✅ Footer — лого, копирайт, ссылки

#### Частично есть
- ⚠️ Hot events рендер — если EVENTS_DATA не загрузился, строка пустая
- ⚠️ «Войти через Telegram» — кнопка есть, но Telegram Auth не реализован (ведёт на `events.html`)
- ⚠️ Цифры в Stats strip — захардкожены (71%, 47, +8.3%), не из реальных данных

#### Нет
- ❌ Реального трек-рекорда в Proof section (3 примера = mock)
- ❌ Мобильная адаптация не проверена
- ❌ Meta-теги для SEO (только базовый title)

---

### События (`events.html`)

#### Есть
- ✅ Sidebar навигация
- ✅ «Реальные события на Полимаркете» — grid 4 карточки из `events-live.js` (ОНЛАЙН)
- ✅ «Лента событий» — список с thumbnail, метриками, Потенциал/Риск/Горизонт
- ✅ Фильтры по категориям (8 категорий)
- ✅ Сортировка (5 вариантов)
- ✅ Поиск в реальном времени
- ✅ Разделение ОНЛАЙН / ДЕМО событий
- ✅ PP Check секция — ввод ссылки/тезиса, имитация загрузки, результаты (mock)
- ✅ «Штаб PP AI» — 5 агентов в PP Check
- ✅ Риск-матрица в PP Check
- ✅ Закрытые события (Autopsy) — карточки с разбором полётов
- ✅ Upsell banner

#### Частично есть
- ⚠️ PP Check — работает на моке (два сценария: default и btc), реального LLM-запроса нет
- ⚠️ Закрытые события — берутся из `EVENTS_DATA.closedEvents` (статичные данные)
- ⚠️ Paywall для Pulse-тира — показывает уведомление, но блокировки нет реально
- ⚠️ Счётчик следящих (watchers) — отображается, но логика не реализована

#### Нет
- ❌ Реальный PP Check через API
- ❌ Реальная авторизация (Гость/Pulse/PRO различаются в коде, но auth нет)
- ❌ Закладки (🔖) — иконка есть, но функционал не реализован
- ❌ Уведомления о новых событиях
- ❌ Infinite scroll или пагинация

---

### Карточка события (`event.html`) — OPEN CARD v2 ✅

**Рендер:** `PP_SIMPLE_OPEN.renderPage(ev, opts)` · `simple-open-card.js`

#### Есть (все demo + live)
- ✅ Единый порядок **9 секций** на каждой открытой карточке
- ✅ «Вывод за 10 секунд» — VS: Рынок | EDGE + горизонт | PolyPilot
- ✅ «Почему PolyPilot так думает» + риски (duo-блок)
- ✅ «Анализ комментариев» — всегда на экране (placeholder если нет данных)
- ✅ «Данные с Polymarket Analytics» — always-on + empty-state
- ✅ «Крупные игроки» — always-on + empty-state
- ✅ «Мы проверили» — чипы проверок (эвристика / `checkedReview`)
- ✅ «Итоговый вывод» — уверенность из `confidence`, риск, горизонт
- ✅ «Что делать» — CTA Polymarket / бот / guest-share
- ✅ «Изменения по событию»
- ✅ Баннер ДЕМО / ОНЛАЙН

#### Частично есть
- ⚠️ Pipeline-секции (3–5) с **реальным контентом** только у `live-79061` (stub)
- ⚠️ «Мы проверили» — эвристика; явный `checkedReview` из pipeline пока нет
- ⚠️ Legacy CSS/JS в `event.html` не удалён (не рендерится)

#### Убрано (14.06.2026)
- ❌ War Room-аккордеон, AI Timeline, калькулятор, «Подробная аналитика», PIE-панель на странице

#### Следующий шаг (подкапотка)
- Pipeline → `crowdPulse`, `externalMarketCheck`, `whaleCheck`, `checkedReview` для всех live
- См. [[OPEN_CARD_V2_SIMPLE]] · [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]] этап 4c
---

### Как это работает (`how-it-works.html`)

#### Есть
- ✅ Hero с заголовком и подзаголовком
- ✅ 3 шага процесса с детальным описанием
- ✅ Визуальные mock-примеры (Event Scanner, Analysis, Result)
- ✅ FAQ-секция
- ✅ CTA-секция внизу

#### Нет
- ❌ Актуальные данные о работе PIE v1.3
- ❌ Схема «мясорубки» для пользователя

---

### Тарифы (`pricing.html`)

#### Есть
- ✅ 3 колонки: Guest (0₽), Pulse (990₽/мес), PRO (2 990₽/мес)
- ✅ Feature lists с checkmarks
- ✅ «7 дней бесплатно» для Pulse
- ✅ Сравнительная таблица ниже
- ✅ FAQ секция
- ✅ CTA-баннер

#### Нет
- ❌ Реальная оплата (Stripe/ЮKassa не подключены)
- ❌ Реальный Telegram Login
- ❌ Переключатель месяц/год

---

### Поддержка (`support.html`)

#### Есть
- ✅ 3 способа связи: FAQ, Telegram, форма обратной связи
- ✅ Статус системы (hardcoded «Онлайн»)
- ✅ Базовый FAQ

#### Нет
- ❌ Реальная форма (не отправляет)
- ❌ Telegram ссылка (placeholder)
- ❌ Реальный статус системы (Railway health check)

---

## Часть 5. Карточка события — детальный анализ

### Закрытая карточка (в ленте событий)

Отображается в `events.html` в формате списка (list row):
- Thumbnail с иконкой категории (цветной градиент)
- Категорийный бейдж (цвет по типу), «🔥 Горячее», ОНЛАЙН/ДЕМО
- Заголовок события (2 строки max)
- Субстрока: объём total, объём 24ч, интерес (▲/▼)
- Метрики справа: Потенциал / Риск / Горизонт
- Стрелка-CTA при hover

**В grid-карточке (hot section) добавлено:**
- 6 stat-блоков (2 ряда)
- Счётчик следящих
- Bookmark-иконка

### Открытая карточка (`event.html?id=...`) — v2

**9 секций (фиксированный порядок):**
1. Вывод за 10 секунд (VS + EDGE)
2. Почему PolyPilot так думает + риски
3. Анализ комментариев
4. Данные с Polymarket Analytics
5. Крупные игроки
6. Мы проверили
7. Итоговый вывод
8. Что делать
9. Изменения по событию

**Единая логика:** demo и live используют один `renderPage()`. Секции 3–5 с placeholder при отсутствии pipeline-полей.

**Данные:** полный pipeline только `live-79061`; остальные 12 open-событий — empty-state в секциях 3–5.
---

## Часть 6. Сравнение с Master Reference (AI_ARCHITECTURE_V1)

| Блок из архитектуры | Утверждён в arch | Реализован в UI |
|--------------------|-----------------|-----------------|
| Рыночная вероятность (marketProb) | ✅ | ✅ Отображается |
| PP Probability (ppProb) | ✅ | ⚠️ Mock-значения |
| Edge (edgePp) | ✅ | ⚠️ Mock / не из PIE |
| Whale Signal / MI | ✅ (v1.3) | ❌ Не отображается |
| Market Structure Score | ✅ (v1.3) | ❌ Не отображается |
| Evidence / факты с источниками | ✅ | ❌ Нет |
| Source Quality Score (EQS) | ✅ (v1.3) | ❌ Нет |
| Contradiction Engine | ✅ | ❌ Нет |
| Comparable Events | ✅ | ❌ Нет |
| Risk Officer (structured) | ✅ | ⚠️ Mock в PP Check |
| Verdict Agent | ✅ | ⚠️ Mock в War Room |
| Event Type | ✅ (v1.3) | ❌ Нет поля eventType |
| Memory / Track Record | ✅ | ⚠️ Mock Autopsy |
| Autopsy | ✅ | ⚠️ Mock данные |
| Tier-based visibility | ✅ | ⚠️ Логика есть, auth нет |
| Pre-publish gate | ✅ | ❌ Не применяется |

**Расхождения:**
- Самое критичное: **live-карточки не получают PP Probability** — событие проходит через harvest, но не через PIE → на сайте `??%`
- **Whale Signal** полностью отсутствует в UI, хотя в архитектуре это ключевой блок
- **Evidence** (факты с ссылками) не отображаются, хотя это центральная ценность системы

---

## Часть 7. Готовность UI под PIE v1.3

| Блок PIE | Готовность UI | Объяснение |
|----------|--------------|-----------|
| **Event Type Classifier** | 🔴 Не готов | Поля `eventType` и `subType` нет в карточке. Нужны badges и фильтр. |
| **Market Intelligence** | 🔴 Не готов | Whale Signal, smart money bias — не отображаются. Поля зарезервированы в архитектуре, но нет UI-блока. |
| **Market Structure Analyzer** | 🔴 Не готов | `marketHealthScore`, `manipulationRisk` — не отображаются нигде. |
| **Evidence Collector** | 🔴 Не готов | Блок с источниками (URL, tier A/B/C, дата) отсутствует в event.html. |
| **Source Scoring System** | 🔴 Не готов | EQS, дедупликация — нет UI. |
| **Contradiction Engine** | 🔴 Не готов | Contradiction map — нет блока в карточке. |
| **Comparable Events** | 🔴 Не готов | Аналоги с base rate — нет блока. |
| **Probability Engine** | 🟡 Частично | Место для ppProb и edge есть, но `components{}` не отображаются. |
| **Risk Officer** | 🟡 Частично | Risk level отображается в ленте. В карточке — mock-данные. |
| **Memory / Track Record** | 🟡 Частично | Autopsy-секция в events.html есть (mock). Track record — mock. |

---

## Часть 8. UX-анализ

### 1. Какие блоки уже сильные?

- **Hero на лендинге** — отличный первый экран, демо-карточка объясняет суть за 5 секунд
- **Лента событий** — live-данные с Polymarket показываются, фильтры работают, поиск работает
- **Тарифная страница** — чистая, понятная, pricing psychology на месте (Pulse highlighted)
- **Sidebar навигация** — стабильная, активный элемент подсвечен
- **PP Check mock** — хорошо имитирует финальный функционал: loading states, War Room, риск-матрица

### 2. Где пользователь может запутаться?

- **«??%»** в open-карточке — пользователь видит сломанный UI, не понимает, есть ли анализ
- **«undefined следят»** — читается как баг, роняет доверие
- **Нет объяснения «Потенциал»** в ленте — пользователь не знает что это значит без тултипа
- **ДЕМО / ОНЛАЙН разделение** — разделение есть, но новый пользователь не сразу понимает разницу
- **«Войти через Telegram»** ведёт на events.html — пользователь ожидает реальный вход

### 3. Где не хватает доверия?

- **Цифры 71% точности, 47 событий** — захардкожены, не из реальных данных → можно проверить
- **Трек-рекорд на лендинге** — 3 примера с ФРС 2019/2024 — выглядят как выдуманные истории
- **PP Check** — даёт красивый ответ, но пользователь-эксперт увидит, что это mock
- **«Все системы работают нормально» в Support** — захардкожен, не реальный статус

### 4. Какие блоки нужны для отображения PIE?

Для PIE v1.3 нужно добавить в `event.html`:

| Новый блок | Данные из PIE | Приоритет |
|------------|--------------|-----------|
| Event Type badge (тип события) | `eventType`, `subType` | P1 |
| Probability components (разбивка) | `components{}` из Probability Engine | P1 |
| Market Structure блок | `marketHealthScore`, `whaleDominance`, `manipulationRisk` | P1 |
| Evidence секция | `scoredEvidence.news[]` с URL и tier | P1 |
| Contradiction map | `contradictionMap[]` | P2 |
| Comparable Events | `analogs[]` | P2 |
| Source Quality badge | `evidenceQualityScore` | P2 |
| Whale Signal indicator | `whaleSignal`, `confidence` | P1 |

### 5. Что можно удалить без потери смысла?

- Статичные mock-числа в Proof section лендинга → заменить на «данные обновляются»
- Дублирующий PP Check на events.html + отдельный `check.html` → оставить один
- `learn.html` (30% готовности) → убрать из навигации до содержимого
- «undefined следят» → убрать до реализации watchers

---

## Часть 9. Итог

### Готовность сайта под MVP: **72%**

MVP = сайт отображает живые данные Polymarket, пользователь видит события, понимает концепцию.

**Почему не 100%:**
- Live-карточки показывают `??%` вместо PP Probability
- Auth (Telegram Login) не реализован
- Трек-рекорд — mock данные

### Готовность сайта под PIE v1.3: **25%**

PIE v1.3 = все 15 блоков pipeline видны в UI с реальными данными.

**Почему 25%, а не 0%:**
- Место для ppProb и edge уже есть в event.html
- Risk section зарезервирован
- War Room / агенты — UI готов, нужны реальные данные

---

### Критичные доработки (блокируют MVP)

1. **Исправить `??%` в event.html** — live-события должны получать ppProb из pipeline
2. **Исправить `undefined` поля** — watcher, horizon → дата
3. **Реальные цифры в PP Check** — подключить к backend API (или явно пометить как демо)
4. **Telegram Login** — без auth весь paywall — имитация

### Желательные доработки (для PIE v1.3)

1. Добавить блок **Market Intelligence** в event.html (whale signal, healthScore)
2. Добавить **Evidence секцию** — факты с источниками, tier, URL
3. Добавить **Probability Components** — разбивка формулы v1.1
4. Добавить **Contradiction map** — расхождения рынок vs факты
5. Добавить **Event Type badge** с профилем анализа

### Что можно оставить на V2

- Comparable Events визуализация (аналоги)
- Source Scoring в UI (EQS badge)
- Market Structure full dashboard
- Mobile adaptation
- Notifications система
- Bookmark функционал
- Пагинация / infinite scroll

---

## Сводная таблица страниц

| Страница | Визуально | Данные | Баги | Итог |
|---------|-----------|--------|------|------|
| Landing `index.html` | ⭐⭐⭐⭐⭐ | Mock | Minor | **95%** |
| Events `events.html` | ⭐⭐⭐⭐ | Live + Mock | Medium | **85%** |
| Event `event.html` | ⭐⭐⭐⭐ | Live + Demo | Minor (pipeline data) | **85%** |
| How it works | ⭐⭐⭐⭐ | Mock | None | **90%** |
| Pricing | ⭐⭐⭐⭐⭐ | Mock | Minor | **90%** |
| Support | ⭐⭐⭐⭐ | Mock | None | **80%** |
| Check | ⭐⭐⭐ | Mock | None | **60%** |
| Compare | ⭐⭐ | — | — | **40%** |
| Proof-track | ⭐⭐ | Mock | — | **50%** |
| Learn | ⭐ | — | — | **30%** |

---

← [[ДОМ_ШТАБ]] · [[OPEN_CARD_V2_SIMPLE]] · [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]]
