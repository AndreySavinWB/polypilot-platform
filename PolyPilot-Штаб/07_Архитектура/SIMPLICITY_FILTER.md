# Simplicity Filter — v1

> **Статус:** ✅ в коде · 15 июня 2026  
> **Политика:** [[SIMPLE_EVENTS_POLICY]] · **Legacy:** [[ПРИОРИТЕТ_АГЕНТ]]

Rule-based фильтр простых событий. Заменяет Priority Agent на harvest по умолчанию.

---

## Переключение

```env
PP_RANK_MODE=simple    # default — Simplicity Filter
PP_RANK_MODE=priority  # legacy macro rubric
```

---

## Код

| Файл | Роль |
|------|------|
| `backend/src/agents/simplicity.py` | Rubric + hard reject |
| `backend/src/agents/event_ranking.py` | Facade (simple / priority) |
| `backend/scripts/harvest_test_events.py` | Harvest использует facade |
| `backend/scripts/test_simplicity_scan.py` | Быстрый scan без LLM |
| `backend/tests/test_simplicity.py` | Unit tests |

---

## Пороги

| Score | Decision |
|-------|----------|
| ≥ 70 | accepted — идёт в harvest top-N |
| 60–69 | watchlist |
| < 60 | rejected |

Hard reject: politics/macro, multi-market (>2), horizon > 90d, ambiguous resolution.

---

## API

`GET /api/priority/scan` — отдаёт ranking в активном режиме (`rankMode` в ответе).

---

## Changelog

| Дата | Изменение |
|------|-----------|
| 2026-06-15 | v1 — Simplicity Filter в backend, default `PP_RANK_MODE=simple` |
