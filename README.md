# PolyPilot

AI-аналитика для рынков прогнозов (Polymarket). Рускоязычная платформа: события, перевес PP, штаб агентов.

> Этап прототипа завершён. Дальше — боевой формат: один репозиторий, отдельные модули.

## Структура mono-repo

```text
PolyPilot/
├── platform/          ← веб-приложение (HTML/CSS/JS)
├── backend/           ← API, агенты, Polymarket, LLM
├── PolyPilot-Штаб/    ← документация Obsidian (vault)
├── vercel.json        ← деплой platform/ на Vercel
└── README.md          ← вы здесь
```

## Сайт онлайн

| Куда | URL |
|------|-----|
| **Сейчас (Pages)** | https://andreysavinwb.github.io/polypilot-platform/app/events.html |
| **Цель (Vercel)** | https://polypilot.pro/app/events.html |

## Инфраструктура (целевая)

| Слой | Хостинг | Папка |
|------|---------|-------|
| Frontend | **Vercel** (или Netlify) | `platform/` |
| Backend | **Railway** → позже VPS | `backend/` |
| Код + CI | **GitHub** | весь репо |

Пошаговая настройка: `PolyPilot-Штаб/07_Архитектура/ЦЕЛЕВАЯ_ИНФРАСТРУКТУРА.md`  
Дорожная карта: `PolyPilot-Штаб/07_Архитектура/ДОРОЖНАЯ_КАРТА_ОНЛАЙН.md`

### Vercel (5 мин)

1. Import repo на [vercel.com](https://vercel.com)
2. Root Directory: `platform` *(или корень — см. `vercel.json`)*
3. Deploy → привязать домен `polypilot.pro`

### Railway (10 мин)

1. New Project → GitHub → Root Directory: `backend`
2. Variables: `POLZA_API_KEY`, `LLM_PROVIDER=polza`
3. Cron: `python scripts/harvest_test_events.py` каждые 6 ч

## Быстрый старт (локально)

### Сайт

```text
platform/app/events.html
```

### Backend

```powershell
cd backend
copy .env.example .env
.\run.ps1
```

http://127.0.0.1:8787/health

### Harvest

```powershell
cd backend
.\.runtime\python.exe scripts\harvest_test_events.py
```

## GitHub

https://github.com/AndreySavinWB/polypilot-platform
