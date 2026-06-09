# PolyPilot

AI-аналитика для рынков прогнозов (Polymarket). Рускоязычная платформа: события, перевес PP, штаб агентов.

> Этап прототипа завершён. Дальше — боевой формат: один репозиторий, отдельные модули.

## Структура mono-repo

```text
PolyPilot/
├── platform/          ← веб-приложение (HTML/CSS/JS)
├── backend/           ← API, агенты, Polymarket, LLM
├── PolyPilot-Штаб/    ← документация Obsidian (vault)
└── README.md          ← вы здесь
```

| Папка | Назначение |
|-------|------------|
| **platform/** | Сайт: лента событий, карточки, тарифы, демо-режимы |
| **backend/** | Priority Agent, harvest, sync live-данных на сайт |
| **PolyPilot-Штаб/** | Стратегия, архитектура, дорожная карта (Obsidian) |

## Быстрый старт

### Сайт (локально)

Откройте в браузере:

```text
platform/app/events.html
```

Или поднимите статический сервер из корня `platform/`.

### Backend

```powershell
cd backend
copy .env.example .env   # заполнить POLZA_API_KEY
.\run.ps1
```

Проверка: http://127.0.0.1:8787/health

### Обновить live-события на сайте

```powershell
cd backend
.\.runtime\python.exe scripts\harvest_test_events.py
```

Скан Polymarket → Priority Agent → анализ → `platform/data/events-live.js`

## Документация

Obsidian vault: **`PolyPilot-Штаб/`** → заметка [[ДОМ_ШТАБ]]

Ключевые файлы:

- `PolyPilot-Штаб/07_Архитектура/СТАТУС_ЛАБОРАТОРИИ.md`
- `PolyPilot-Штаб/07_Архитектура/ПРИОРИТЕТ_АГЕНТ.md`

## GitHub

Репозиторий: **https://github.com/AndreySavinWB/polypilot-platform**
