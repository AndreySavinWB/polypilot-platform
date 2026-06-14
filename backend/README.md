# PolyPilot — Backend

API и агенты: Priority Agent (рубрика v1), Polymarket, LLM (Polza).

## Локально

```powershell
copy .env.example .env   # POLZA_API_KEY
.\run.ps1
# http://127.0.0.1:8787/health
```

## Railway

Root Directory: **`backend`**. См. `railway.toml`, `Procfile`.

Переменные: `POLZA_API_KEY`, `LLM_PROVIDER=polza`, `PP_SCAN_LIMIT`, `PP_TOP_N`.

Cron (harvest):

```bash
python scripts/harvest_test_events.py
```

## Harvest + sync

```powershell
.\.runtime\python.exe scripts\harvest_test_events.py
```

Пишет:

- `data/test_events.json` — полный анализ
- `data/events-live.json` — для API
- `../platform/data/events-live.js` — для статического сайта (если есть)

## PIE V1.0a

Модули: `src/agents/normalizer.py`, `risk.py`, `pie.py`.

```powershell
python scripts/test_pie.py
```

Harvest пишет `pipelinePackage` рядом с legacy `analysis`.

## Telegram bot (Funnel 1.0)

Код: `src/bot/` · тексты по [[../PolyPilot-Штаб/05_Маркетинг/FUNNEL_1_0/BOT_SEQUENCE_72H.md]]

1. BotFather → токен для `@polypilot`
2. `backend/.env`: `TELEGRAM_BOT_TOKEN=...`
3. **Локально (быстрый старт):** сбросить старый webhook и polling:

```powershell
cd backend
python scripts/run_telegram_polling.py
```

4. **Production (Railway):** `PUBLIC_BACKEND_URL=https://…` → `python scripts/setup_telegram_webhook.py`

Заявки Starter сохраняются в `data/bot_starter_applications.json` (local, в gitignore).

## API

- `GET /health`
- `GET /api/telegram/health` — bot configured?
- `POST /api/telegram/webhook` — Telegram updates (production)
- `GET /api/live/events` — live-карточки (JSON)
- `GET /api/polymarket/events?limit=10`
- `GET /api/priority/scan?scan=300&top=10`
- `POST /api/agents/analyze` — legacy MVP pipeline
- `POST /api/pie/process` — PIE V1.0a (`{ "event": {...}, "priority": optional }`)

Деплой и домен: `PolyPilot-Штаб/07_Архитектура/ЦЕЛЕВАЯ_ИНФРАСТРУКТУРА.md`
