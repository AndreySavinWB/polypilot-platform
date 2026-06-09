# PolyPilot — Backend

API и агенты: Priority Agent (рубрика v1), Polymarket, LLM (Polza).

## Запуск

```powershell
.\run.ps1
# http://127.0.0.1:8787/health
```

## Harvest + sync на platform

```powershell
.\.runtime\python.exe scripts\harvest_test_events.py
```

Переменные: `PP_SCAN_LIMIT=300`, `PP_TOP_N=10` в `.env`

## API

- `GET /health`
- `GET /api/polymarket/events?limit=10`
- `GET /api/priority/scan?scan=300&top=10`
- `POST /api/agents/analyze`

См. `PolyPilot-Штаб/07_Архитектура/`
