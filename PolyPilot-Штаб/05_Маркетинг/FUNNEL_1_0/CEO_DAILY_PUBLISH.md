# CEO Daily Publish — напоминания + готовые тексты

> **Задача:** ты публикуешь в @polypilot_pro **руками**, но **не придумываешь** текст каждый день и **не забываешь** про пост.

---

## Как это работает

| Кто | Что делает |
|-----|------------|
| **Система** | Каждое утро шлёт тебе в **личку Telegram** готовый текст поста на сегодня |
| **Ты** | Копируешь → вставляешь в канал @polypilot_pro → Publish (~2 мин) |

Тексты на **7 дней** лежат в `backend/data/daily_publish.json` (Pack #1 Fed 2026).  
После 7-го дня цикл повторяется с пометкой `(repeat week)` — пока не добавим Pack #2.

---

## Настройка (один раз, ~10 мин)

### Шаг 1 — Узнай свой Telegram chat id

1. Напиши боту [@userinfobot](https://t.me/userinfobot) — он пришлёт `Id: 123456789`.
2. Или напиши **своему** `@polypilot_pro_bot` любое сообщение (после деплоя webhook).

Это число → `TELEGRAM_CEO_CHAT_ID`.

### Шаг 2 — Локально (backend/.env)

```env
TELEGRAM_BOT_TOKEN=...          # уже есть
TELEGRAM_CEO_CHAT_ID=123456789  # твой id
DAILY_PUBLISH_START_DATE=2026-06-14   # день 1 = Post 1 из Pack #1
```

### Шаг 3 — Проверка без GitHub

```powershell
cd d:\Andrey\PolyPilot\backend
.\.runtime\python.exe scripts\daily_publish.py
.\.runtime\python.exe scripts\daily_publish.py --send
```

В Telegram должно прийти сообщение с полным текстом поста.

### Шаг 4 — GitHub Actions (авто каждое утро 10:00 MSK)

Repo → **Settings → Secrets and variables → Actions** → добавь:

| Secret | Значение |
|--------|----------|
| `TELEGRAM_BOT_TOKEN` | токен бота |
| `TELEGRAM_CEO_CHAT_ID` | твой chat id |
| `DAILY_PUBLISH_START_DATE` | `2026-06-14` (или дата старта спринта) |

Workflow: `.github/workflows/daily-ceo-reminder.yml`  
Можно запустить вручную: **Actions → Daily CEO publish reminder → Run workflow**.

### Шаг 5 (опционально) — Railway cron

Если не хочешь GitHub: добавь на Railway cron job  
`python scripts/daily_publish.py --send` в 07:00 UTC.

---

## Команды

```powershell
# Текст на сегодня (в консоль)
python scripts/daily_publish.py

# День 3 спринта
python scripts/daily_publish.py --day 3

# Список всех 7 дней
python scripts/daily_publish.py --list

# Отправить себе в Telegram
python scripts/daily_publish.py --send
```

---

## Расписание 7 дней

| День | Тема |
|------|------|
| 1 | Post 1 · Hook (Fed 80% / 13 markets) |
| 2 | Education · resolution criteria |
| 3 | Post 2 · mini-breakdown |
| 4 | Structure · $33M volume |
| 5 | Trust · method |
| 6 | Post 3 · Starter CTA |
| 7 | Recap · last cohort call |

Полные тексты — в `backend/data/daily_publish.json`.  
Источник смысла: [PACK_001_FED_RATE_CUTS_2026.md](packs/PACK_001_FED_RATE_CUTS_2026.md).

---

## Кто пишет тексты дальше

| Сейчас | Потом |
|--------|-------|
| 7 постов в JSON (ручная верстка из Pack #1) | Pack #2 → новый `daily_publish.json` или неделя 2 |
| CRO / CEO правит JSON перед спринтом | LLM-черновик из PIE + Pack template (04 Backend) |
| Cursor-агент по запросу «день 4» | Автоген из `events-live.js` + guardrails |

**Правило:** перед публикацией сверь цифры на `event.html?id=live-51456` (market ~80%, preliminary).

---

## KPI (отмечай вручную)

Google Sheet / Notion — одна строка в день:

- дата · опубликовал да/нет · просмотры TG · клики guest-event · bot starts · заметки

---

← [FUNNEL_1_0 README](README.md) · [PACK_001](packs/PACK_001_FED_RATE_CUTS_2026.md)
