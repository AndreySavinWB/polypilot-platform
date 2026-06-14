# Telegram Bot — 72h Sequence (PolyPilot Starter)

> Переписанная sequence под текущий CEO-фокус: **PolyPilot Starter**, не PRO trial.

**Старый flow (deprecated):** Pulse + PRO Trial 7 дней → оплата PRO.  
**Новый flow:** разбор → nurture → Starter offer → manual payment / pre-order.

---

## Entry Points

| Source | start payload | First message |
|--------|---------------|---------------|
| TG Channel CTA | `start=channel` | Welcome + today's event |
| Short/Reels bio | `start=shorts` | Welcome + featured event |
| Guest-event | `start=event_{id}` | Event-specific breakdown |
| X thread | `start=x_{id}` | Same as event |
| Direct | `start=starter` | Skip to offer intro |

---

## Sequence Overview

```text
T+0    → Welcome + open breakdown (guest-event deep link)
T+4h   → Probability moved / context update
T+24h  → 3 events worth watching + education moment
T+48h  → PolyPilot Starter intro + social proof frame
T+72h  → Last call Starter + waitlist fallback
```

---

## Messages

### T+0 — Welcome + Breakdown

**Trigger:** user starts bot (any payload)

**Text:**

```text
Привет. Это PolyPilot — аналитика prediction markets.

Не финансовый совет. Не обещаем прибыль.

Сейчас открыт разбор события:
[EVENT_TITLE]

→ Открыть разбор (60–90 сек): [guest-event deep link]

Посмотри карточку — завтра пришлю ещё 3 события, которые стоит понять.
```

**Buttons:**

- `Открыть разбор` → guest-event.html?id=
- `Как читать Polymarket` → learn.html
- `Подписаться на канал` → TG channel link

---

### T+4h — Movement / Context

**Trigger:** +4 hours after start (if user opened breakdown OR clicked any button)

**Text:**

```text
Обновление по [EVENT_TITLE]:

Рыночная вероятность: [X]% → [Y]% ([delta]pp за последние часы)

Что это может значить — и что большинство не проверяет:
• resolution criteria
• качество evidence
• риск данных

Полный контекст в карточке события:
[guest-event link]
```

**Buttons:**

- `Открыть карточку`
- `3 события на завтра` (info — придёт в T+24h)

**Skip if:** no event data available — send education fallback:

```text
Пока нет свежего движения по событию. Вот принцип:
70% на Polymarket ≠ 70% «точно случится».
Разбор механики → learn.html
```

---

### T+24h — 3 Events + Education

**Trigger:** +24 hours after start

**Text:**

```text
3 события, которые сегодня стоит понять:

1. [EVENT_1] — рынок [X]%, [angle: anomaly/education/news]
2. [EVENT_2] — рынок [X]%, [angle]
3. [EVENT_3] — рынок [X]%, [angle]

PolyPilot смотрит не только на цену, но на evidence, риски и resolution.

Открой любое → guest-event links

Хочешь научиться читать такие события системно?
```

**Buttons:**

- `Событие 1` / `Событие 2` / `Событие 3`
- `Как PolyPilot разбирает событие` → learn.html

---

### T+48h — PolyPilot Starter Intro

**Trigger:** +48 hours after start

**Text:**

```text
PolyPilot Starter — для тех, кто хочет разобраться в Polymarket системно.

Что входит:
• mini-course: Polymarket + как читать события
• 3 live разбора актуальных событий
• 7 дней research feed / закрытый чат

Не сигналы. Не «гарантированная прибыль».
Структура анализа, риски, resolution, evidence.

Стартовая цена: 4 990–9 990 ₽
Первый cohort — ограниченное число мест.

Хочешь попасть в список?
```

**Buttons:**

- `Хочу в Starter` → collect contact / pre-order form
- `Сначала бесплатный разбор` → guest-event
- `Не сейчас` → waitlist only

**On «Хочу в Starter»:**

```text
Отлично. Ответь:
1) Твой @username или email
2) Что интереснее: Polymarket с нуля / разбор событий / метод PolyPilot

Мы свяжемся с деталями оплаты (manual payment на старте).
```

---

### T+72h — Last Call + Waitlist

**Trigger:** +72 hours after start

**Text:**

```text
Последний день, когда можно попасть в первый cohort PolyPilot Starter по стартовой цене.

Если не готов — останешься в бесплатном канале:
• daily разборы
• guest-event links
• education

Starter закрывается через 24ч → [deadline date]

Или оставь заявку в waitlist — напишем, когда откроем следующий cohort.
```

**Buttons:**

- `Записаться в Starter`
- `Waitlist`
- `Бесплатный канал` → TG channel

---

## Triggers (In-Bot Actions)

| Trigger | Action |
|---------|--------|
| 2-й открытый guest-event | Send Starter soft mention |
| Click «Как читать Polymarket» | Tag: education_intent |
| Click «Хочу в Starter» | Tag: high_intent → notify sales |
| «Не сnowas» | Tag: nurture_only → weekly digest |
| Reply «сигнал» / «ставка» | Auto-reply: disclaimer + education redirect |

---

## Tags For Analytics

| Tag | Meaning |
|-----|---------|
| `source_shorts` | from Reels/Shorts |
| `source_channel` | from TG channel |
| `source_event_{id}` | from specific event |
| `education_intent` | clicked learn |
| `high_intent` | Starter application |
| `nurture_only` | declined offer |

---

## Compliance

Every message block must include or reference:

```text
PolyPilot — аналитический инструмент. Не финансовый совет.
```

Do not mention:

- PRO trial
- PRO 2 990 ₽ as primary CTA
- guaranteed profit
- «signals»

---

## Migration From Old Sequence

| Old (ВОРОНКА_И_ТГ) | New |
|---------------------|-----|
| Pulse + PRO Trial 7 дней | Free channel + guest-event |
| +48h Proof Track + Trial | +48h PolyPilot Starter intro |
| +72h End Trial → оплата PRO | +72h Last call Starter |
| Триггеры PRO (blur Edge, Day 5 Trial) | Triggers: 2nd event, Starter click |

---

← [README.md](README.md) · [[ВОРОНКА_И_ТГ]]
