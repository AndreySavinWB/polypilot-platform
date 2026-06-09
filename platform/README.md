# PolyPilot — Platform (веб-приложение)

Интерактивный сайт PolyPilot: события, карточки, War Room, тарифы.

## Локальный запуск

Откройте `app/events.html` в браузере или поднимите статический сервер из этой папки.

## Данные

| Файл | Источник |
|------|----------|
| `data/events-live.js` | Polymarket (auto: `backend/scripts/harvest_test_events.py`) |
| `data/events-data.js` | Демо-примеры интерфейса |

## Онлайн

| Хостинг | URL |
|---------|-----|
| GitHub Pages | https://andreysavinwb.github.io/polypilot-platform/app/events.html |
| Vercel (цель) | `polypilot.pro` — см. `../vercel.json`, [[ЦЕЛЕВАЯ_ИНФРАСТРУКТУРА]] |

Конфиг API (для Railway): `assets/js/pp-config.js`
