# Plan: $10k Lifetime Volume — Unlock Referral

> **Цель:** получить доступ к referral-ссылке Polymarket (Lifetime Trading Volume > $10 000)  
> **Track B** активируется после unlock

---

## Зачем

Без $10k lifetime volume referral link недоступен → Track B revenue = 0.

---

## Фазы

### Phase 1 — Подготовка (неделя 1)

- [ ] Аккаунт Polymarket верифицирован
- [ ] Понимание fee structure и eligible markets
- [ ] Capital allocation plan (сколько готовы держать в позициях)
- [ ] Journal: date, market, volume, notes

### Phase 2 — Накопление volume (недели 2–6)

**Принципы:**

- volume для unlock, **не** для «заработка на unlock»;
- предпочитать ликвидные macro/politics markets;
- не chase illiquid markets ради volume;
- document every trade for internal review.

**Ориентиры:**

| Неделя | Cumulative volume target |
|--------|--------------------------|
| 2 | $2 000 |
| 3 | $4 000 |
| 4 | $6 000 |
| 5 | $8 000 |
| 6 | **$10 000+** |

### Phase 3 — Unlock + Track B Launch

- [ ] Получить referral link в Polymarket
- [ ] Добавить `referralUrl` в `pp-config.js`
- [ ] Включить CTA на event.html + guest-event с [AFFILIATE_DISCLOSURE.md](AFFILIATE_DISCLOSURE.md)
- [ ] Baseline: clicks, signups, volume from referrals (30/60/90 days)

---

## Риски

| Риск | Mitigation |
|------|------------|
| Потери на trades while building volume | Малые позиции, ликвидные рынки, не «unlock at any cost» |
| Время отвлекает от product | Cap: X hours/week on volume building |
| Referral program terms change | Не строить business plan только на referral |

---

## KPI Track B (после unlock)

| KPI | 30d | 60d |
|-----|-----|-----|
| Referral signups | baseline | — |
| Active traders (>$100 vol) | — | target |
| Referral revenue | — | compare vs Starter ARPU |
| Revenue per 1000 guest-event views | — | — |

---

← [POLYMARKET_REFERRAL_ANALYSIS.md](POLYMARKET_REFERRAL_ANALYSIS.md) · [LAUNCH.md](../05_Маркетинг/FUNNEL_1_0/LAUNCH.md)
