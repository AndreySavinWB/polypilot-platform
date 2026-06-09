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

## API

- `GET /health`
- `GET /api/live/events` — live-карточки (JSON)
- `GET /api/polymarket/events?limit=10`
- `GET /api/priority/scan?scan=300&top=10`
- `POST /api/agents/analyze`

Деплой и домен: `PolyPilot-Штаб/07_Архитектура/ЦЕЛЕВАЯ_ИНФРАСТРУКТУРА.md`
