# Простой backend PolyPilot

> Цель: быстро проверить реальную внутреннюю механику PP без тяжёлой инфраструктуры.

---

## Решение

Папка:

```text
PolyPilot-Backend/
```

Технология первого этапа:

```text
Python standard library
```

Причина: на текущей машине не найден `npm`, поэтому не тратим время на Node-setup.

---

## Что уже заложено

```text
PolyPilot-Backend/
├── server.py
├── .env.example
├── README.md
└── src/
    ├── agents/pipeline.py
    └── services/
        ├── polymarket.py
        └── llm.py
```

---

## API

### Health

```text
GET /health
```

### 10 реальных событий Polymarket

```text
GET /api/polymarket/events?limit=10
```

Данные берутся из публичного Polymarket Gamma API. API key не нужен.

### Анализ события

```text
POST /api/agents/analyze
```

Тело:

```json
{
  "event": {
    "id": "...",
    "title": "...",
    "markets": []
  }
}
```

Ответ:
- priority
- newsScout
- riskOfficer
- verdict
- ui

---

## Ключи

Polymarket market data:

```text
ключ не нужен
```

LLM:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

Ключ хранится только в `.env`, не в чате и не в git.

---

## Ограничения

Этот backend:
- не торгует;
- не ставит ордера;
- не подключает кошелёк;
- не является trading bot.

Он только собирает данные и готовит аналитический JSON.

---

## Следующие шаги

1. Запустить `python server.py`.
2. Проверить `/api/polymarket/events?limit=10`.
3. Выбрать 10 событий для тестового набора.
4. Подключить LLM key через `.env`.
5. Прогнать 4 базовых агента по scorecard.

---

Связанные:
- [[ЛАБОРАТОРИЯ_АГЕНТОВ]]
- [[АРХИТЕКТУРА_АГЕНТОВ]]
