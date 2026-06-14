# Funnel 1.0 — Launch Playbook

> **Статус:** запуск · CEO утвердил dual-track 2026-06-14  
> **Track A:** Starter (primary) · **Track B:** referral после $10k gate

---

## Цель 7 Дней

| # | Цель | Метрика |
|---|------|---------|
| 1 | Запустить контент-машину | 7 Shorts + 7 TG posts |
| 2 | Набрать TG аудиторию | baseline joins |
| 3 | Прогнать bot 72h | bot starts, guest clicks |
| 4 | Получить заявки Starter | **5–10** |
| 5 | Зафиксировать winning hooks | top 3 по CTR |

---

## Порядок Запуска

### День 0 — Setup

- [ ] Создать Telegram канал **PolyPilot Radar** (placeholder в `pp-config.js`)
- [ ] Создать Telegram bot + 72h sequence ([BOT_SEQUENCE_72H.md](BOT_SEQUENCE_72H.md))
- [ ] Проверить landing: `platform/app/starter.html`
- [ ] Проверить guest-event: `platform/app/guest-event.html?id=live-32228`
- [ ] Таблица метрик (Google Sheet / Notion): views, joins, bot starts, applications, payments

### День 1–7 — Content

Использовать [STARTER_ASSETS.md](STARTER_ASSETS.md):

| День | Shorts | TG | X |
|------|--------|----|---|
| D1 | Hook #1 + Pack 4 | Event of day | Thread |
| D2 | Hook #11 Fed | Pack 1 | 3 tweets |
| D3 | Hook #6 anomaly | Pack 5 | — |
| D4 | Remix best | Digest | Thread |
| D5 | Hook #18 trust | Starter soft | — |
| D6 | Hook #3 errors | CTA Starter | — |
| D7 | Recap | Last cohort call | Recap |

---

## Ссылки (конфиг)

Все URL в `platform/assets/js/pp-config.js` → `funnel`:

```javascript
funnel: {
  telegramChannel: 'https://t.me/polypilot_pro',
  telegramBot: 'https://t.me/polypilot_bot?start=',
  starterPage: 'app/starter.html',
  supportTelegram: 'https://t.me/polypilot_support',
}
```

Заменить placeholder на реальные после создания каналов.

---

## UTM Schema

| Параметр | Пример |
|----------|--------|
| utm_source | shorts, tg, x, reels |
| utm_medium | social |
| utm_campaign | funnel_1_0 |
| utm_content | hook_01, pack_fed |

Guest-event:

```text
guest-event.html?id=live-32228&utm_source=tg&utm_campaign=funnel_1_0
```

Starter:

```text
starter.html?utm_source=bot&utm_campaign=starter_cohort_1
```

Bot deep link:

```text
t.me/polypilot_bot?start=event_live-32228
```

---

## Track A Flow (Primary)

```text
1. Short/Reels → bio → TG канал
2. TG post → guest-event (60–90 сек)
3. Кнопка «Telegram bot» → 72h sequence
4. Day 2–3 bot → starter.html
5. Заявка → manual payment → delivery
```

---

## Track B Flow (Secondary — после $10k)

```text
1. Разбор события на guest-event / event.html
2. CTA «Open on Polymarket» + affiliate disclosure
3. НЕ в Shorts hooks
```

См. [AFFILIATE_DISCLOSURE.md](../../06_Монетизация/AFFILIATE_DISCLOSURE.md)  
См. [VOLUME_10K_PLAN.md](../../06_Монетизация/VOLUME_10K_PLAN.md)

---

## Метрики (еженедельно)

| Метрика | Формула |
|---------|---------|
| TG join rate | joins / link clicks |
| Bot start rate | bot starts / channel joins |
| Guest CTR | guest opens / bot starts |
| Starter application rate | applications / bot starts |
| Payment rate | payments / applications |
| Negative feedback | scam/signal comments / total comments |
| Starter ARPU | revenue / payments |
| Referral rev (later) | $ / 1000 TG joins |

---

## Stop Rules

Остановить масштабирование, если:

- negative feedback > 5%;
- 0 Starter applications после 500+ TG joins;
- рост «signal/scam» комментариев;
- guest-event bounce > 80% без второго клика.

---

## Команды

| Команда | Задача |
|---------|--------|
| CRO/Marketing | контент, hooks, cohort, manual sales |
| Product | user stories Starter delivery |
| UI | guest-event, starter page, disclosure на event |
| Backend | real PIE in event.html (parallel track) |

---

← [README.md](README.md) · [STARTER_OFFER.md](../../06_Монетизация/STARTER_OFFER.md)
