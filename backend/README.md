# PolyPilot — Backend

API и агенты: Priority Agent (рубрика v1), Polymarket, LLM (OpenRouter).

## Локально

```powershell
copy .env.example .env   # OPENROUTER_API_KEY
.\run.ps1
# http://127.0.0.1:8787/health
```

## Railway

Root Directory: **`backend`**. См. `railway.toml`, `Procfile`.

Переменные: `OPENROUTER_API_KEY`, `LLM_PROVIDER=openrouter`, `LLM_MODEL=openai/gpt-4o-mini`, `PP_SCAN_LIMIT`, `PP_TOP_N`.

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

## API

- `GET /health`
- `GET /api/live/events` — live-карточки (JSON)
- `GET /api/polymarket/events?limit=10`
- `GET /api/priority/scan?scan=300&top=10`
- `POST /api/agents/analyze`

Деплой и домен: `PolyPilot-Штаб/07_Архитектура/ЦЕЛЕВАЯ_ИНФРАСТРУКТУРА.md`
