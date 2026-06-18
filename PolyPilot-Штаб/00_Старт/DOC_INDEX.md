# Doc Index — единый указатель документов

> **Правило:** одна тема = один master-файл. Перед новой заметкой — проверь эту таблицу.  
> Оперативный статус проекта: `POLYPILOT_STATE.md` (корень репо, вне vault).

---

## Как пользоваться

| Кто | Что читать первым |
|-----|-------------------|
| Человек (Obsidian) | [[ДОМ_ШТАБ]] → эта таблица |
| AI-чат (Cursor) | `POLYPILOT_STATE.md` → эта таблица |
| CRO / деньги | [[MONETIZATION_STATE]] |
| Backend / PIE | [[PROBABILITY_INTELLIGENCE_ENGINE]] → [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]] |

**Не создавай новый `.md`**, если тема уже есть в таблице ниже — обнови master-файл или верни вопрос в `01_CEO`.

---

## Master-файлы (active)

| Тема | Master-файл | Статус |
|------|-------------|--------|
| Навигация штаба | [[ДОМ_ШТАБ]] | active |
| Видение продукта | [[КОНТЕКСТ_ПРОЕКТА_2.0]] | active |
| Оперативный статус | `POLYPILOT_STATE.md` | active · корень репо |
| Правила CEO / команд | `CEO_OPERATING_SYSTEM.md` | active · корень репо |
| Дорожная карта (текущая) | [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]] | active |
| OPEN CARD v2 | [[OPEN_CARD_V2_SIMPLE]] | active · visual ✅ |
| UI статус | [[CURRENT_UI_STATUS]] | active · краткий |
| PIE архитектура | [[PROBABILITY_INTELLIGENCE_ENGINE]] | active · v1.3 |
| Strategy Layer | [[STRATEGY_INTELLIGENCE_LAYER]] | active |
| AI / агенты (контракт) | [[AI_ARCHITECTURE_V1]] | active · сверять с PIE v1.3 |
| Монетизация | [[MONETIZATION_STATE]] | active · 2026 dual-track |
| Funnel / GTM | [[FUNNEL_1_0/README]] | active |
| Starter offer | [[STARTER_OFFER]] · [[FIRST_MONETIZATION_AUDIT]] | active |
| Referral (secondary) | [[POLYMARKET_REFERRAL_ANALYSIS]] | active · после $10k volume |
| Инфраструктура | [[ЦЕЛЕВАЯ_ИНФРАСТРУКТУРА]] | active |
| Бэклог идей | [[БЭКЛОГ_ИДЕЙ]] | active · `08_Идеи/` |
| Как писать в штаб | [[КАК_ПОЛЬЗОВАТЬСЯ_ШТАБОМ]] | active |

---

## PIE — блоки (active, детализация)

| Блок | Файл | Статус кода |
|------|------|-------------|
| Event Type Classifier | [[EVENT_TYPE_CLASSIFIER]] | v0 ✅ |
| Market Structure Analyzer | [[MARKET_STRUCTURE_ANALYZER]] | v0 ✅ |
| Source Scoring | [[SOURCE_SCORING_SYSTEM]] | spec only |
| Probability Formula | [[PROBABILITY_FORMULA_V1_1]] | v0 rules ✅ |
| Data flow | [[INTELLIGENCE_DATA_FLOW]] | active |
| Схема pipeline | [[СХЕМА_МЯСОРУБКИ]] | active |

---

## Frozen / archive (не для новых решений)

| Тема | Файл | Замена |
|------|------|--------|
| HTML MVP roadmap | [[ДОРОЖНАЯ_КАРТА]] | [[ДОРОЖНАЯ_КАРТА_ОНЛАЙН]] |
| Контекст v1 | [[КОНТЕКСТ_ПРОЕКТА]] | [[КОНТЕКСТ_ПРОЕКТА_2.0]] |
| Монетизация Guest/Pulse/PRO | [[МОНЕТИЗАЦИЯ_v1_GUEST_PULSE_PRO]] | [[MONETIZATION_STATE]] |
| PIE v1.2 | [[PIE_V1_2_АРХИВ]] | [[PROBABILITY_INTELLIGENCE_ENGINE]] |
| Redirect stubs | [[МОНЕТИЗАЦИЯ]] · [[PIE_V1_2_ФИНАЛЬНАЯ_АРХИТЕКТУРА]] | → master / архив |
| UI audit (полный) | [[CURRENT_UI_STATUS_FULL]] | [[CURRENT_UI_STATUS]] |

Полный список: [[README_АРХИВ]] · папка `99_Архив/`

---

## Папки штаба

| Папка | Назначение |
|-------|------------|
| `00_Старт` | Навигация, DOC_INDEX, миграция |
| `01_Стратегия` | Видение, контекст |
| `02_Продукт` | Карточка, политики, kill-фичи |
| `03_MVP_Сайт` | MVP specs, OPEN CARD, UI audit |
| `04_Интерфейс` | Экраны, стиль |
| `05_Маркетинг` | Воронка, Funnel 1.0 |
| `06_Монетизация` | CRO, offers, referral |
| `08_Идеи` | Бэклог без срочности |
| `07_Архитектура` | PIE, backend, инфра |
| `99_Архив` | Устаревшее |

---

## Правила архивации

1. Устаревший master → перенос в `99_Архив/`.
2. На старом пути — **stub** (5–15 строк) со ссылкой на архив и на новый master.
3. Обновить эту таблицу и [[README_АРХИВ]].
4. Сообщить `01_CEO` для обновления `POLYPILOT_STATE.md`.

---

← [[ДОМ_ШТАБ]] · [[КАК_ПОЛЬЗОВАТЬСЯ_ШТАБОМ]]
