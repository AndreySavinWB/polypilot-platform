# Starter Assets — Funnel 1.0

> 20 стартовых hooks и 5 Event Content Packs для первого теста acquisition-воронки.

---

## 20 Hooks (Ready To Test)

### Education (P1 — Новички)

| # | Hook | Segment | Format |
|---|------|---------|--------|
| 1 | «70% на Polymarket ≠ 70% что событие точно случится» | Novice | Reels 20s |
| 2 | «Polymarket за 60 секунд: что это и чем не казино» | Novice | Reels 45s |
| 3 | «5 ошибок новичка на prediction markets» | Novice | Carousel |
| 4 | «Resolution criteria — почему люди теряют деньги, не читая правила» | Novice | TG post |
| 5 | «YES/NO — это не «угадал / не угадал». Вот как работает payout» | Novice | Reels 30s |

### Anomaly (P2 — Semi-active)

| # | Hook | Segment | Format |
|---|------|---------|--------|
| 6 | «Рынок +12pp за сутки. Evidence пока слабый — вот что проверить» | Semi-active | Visual card |
| 7 | «3 события сегодня, где цена двигается быстрее фактов» | Semi-active | TG digest |
| 8 | «Volume spike без news — что это может значить (и что не значит)» | Semi-active | Reels 25s |
| 9 | «Одна вероятность — это не анализ. Вот что ещё смотреть» | Semi-active | Thread |
| 10 | «Событие дня: рынок может ошибаться — 3 причины» | Semi-active | TG post |

### Newsjacking (P3 — Macro/News)

| # | Hook | Segment | Format |
|---|------|---------|--------|
| 11 | «Что рынок думает о решении ФРС прямо сейчас» | Macro | Reels 30s |
| 12 | «Выборы: рынок ставит X% — не на hype, а на resolution» | Politics | Thread |
| 13 | «ETF approval odds: что уже заложено в цену» | Crypto/macro | Short |
| 14 | «Regulatory event: почему resolution criteria важнее headline» | Regulatory | TG post |
| 15 | «Геопolitics на Polymarket: цена ≠ прогноз CNN» | News | Reels 25s |

### Method / Trust

| # | Hook | Segment | Format |
|---|------|---------|--------|
| 16 | «Как PolyPilot раскладывает вероятность — не магия, а компоненты» | Data/AI | Thread |
| 17 | «Рынок vs evidence vs risk — три слоя, которые большинство смешивает» | Semi-active | Reels 30s |
| 18 | «Почему мы не обещаем прибыль — и почему это feature, не bug» | All | TG post |

### Risk-Controlled (Crypto-adjacent, Phase 1.5)

| # | Hook | Segment | Format |
|---|------|---------|--------|
| 19 | «Рынок X%, но 3 риска, которые большинство пропускает» | Crypto | Reels 20s |
| 20 | «Prediction markets ≠ crypto futures. Где ломается интуиция» | Adjacent | Reels 30s |

---

## 5 Event Content Packs (Test Batch)

> Заполнить `event_id` и `market_prob` из live Polymarket перед публикацией.  
> Если PIE data partial — маркировать «preliminary / rules_v0».

---

### Pack 1 — Fed Rate Decision (Macro / P3)

**Meta**

- category: regulatory / fed_rate
- priority: P0
- segments: P3 macro, P2 semi-active

**One-liner:** Рынок оценивает вероятность решения ФРС по ставке — но resolution зависит от конкретного wording.

**Market angle:** Следить за движением prob за 7 дней до meeting; сравнить с consensus economists.

**Risk angle:** Resolution criteria (basis points vs «cut/hike/pause»); thin market near event; news lag.

**Education angle:** Macro events — resolution criteria важнее headline.

**Scripts:**

- A (News): «Что рынок думает о ФРС → 3 фактора → TG»
- B (Risk): «Resolution criteria на Fed events — почему 70% ≠ outcome»
- C (Anomaly): «Prob двинулась на Xpp — evidence или repositioning?»

**CTA:** guest-event → bot → Starter (day 3+)

---

### Pack 2 — US Election / Primary (Politics / P3)

**One-liner:** Prediction market на политическое событие — цена отражает collective belief, не опрос.

**Market angle:** Compare market prob vs polling averages; volume as participation signal.

**Risk angle:** Resolution source (AP/Reuters/etc); long horizon = narrative drift; low liquidity early.

**Education angle:** Politics markets punish ambiguous resolution.

**Scripts:**

- A: «Рынок ставит X% на исход — что заложено»
- B: «3 things market prices that polls miss»
- C: «Resolution criteria на election markets»

**CTA:** TG breakdown → learn module

---

### Pack 3 — Bitcoin ETF / Crypto Milestone (Crypto / P1+P2)

**One-liner:** Crypto milestone markets — high attention, high misread of probability.

**Market angle:** Approval/rejection prob; volume spikes on news.

**Risk angle:** Binary resolution timing; regulatory wording; hype without evidence.

**Education angle:** 70% on approval ≠ «buy crypto».

**Scripts:**

- A: «ETF odds: что рынок думает»
- B: «3 risks people skip on crypto milestone markets»
- C: «Probability ≠ price target»

**CTA:** guest-event (use risk disclaimer heavily)

---

### Pack 4 — «Polymarket 101» Evergreen (Education / P1)

**One-liner:** Обучающий pack без привязки к hot event — для постоянного трафика.

**Market angle:** N/A — use generic example event.

**Risk angle:** 5 beginner mistakes checklist.

**Education angle:** Full «how to read one event card» walkthrough.

**Scripts:**

- A: «Polymarket за 60 секунд»
- B: «70% ≠ 100%»
- C: «5 ошибок новичка»

**CTA:** Telegram bot → learn.html → Starter (day 5)

**Note:** Best performer for Shorts evergreen — remix weekly.

---

### Pack 5 — Volume Anomaly Generic (Semi-active / P2)

**One-liner:** Шаблон для любого события с volume spike из PIE marketIntelligence.

**Market angle:** Pull from PIE: volumeSignal, volumeAnomaly, moneyDirection.

**Risk angle:** Volume without verified news; whale heuristic (rules_v0); confidence capped 0.50.

**Education angle:** «Price moved — what evidence supports it?»

**Scripts:**

- A: «Volume spike on [EVENT] — 3 checks»
- B: «Market +Xpp, evidence weak — what now?»
- C: «How PolyPilot flags anomalies (rules_v0)»

**CTA:** guest-event with partial data disclaimer

**Data rule:**

```text
If collectionStatus = partial → say "preliminary analysis, rules_v0"
If whaleSignal = heuristic → do not say "whales confirmed"
```

---

## Test Plan (7 Days)

| Day | Action | Metric |
|-----|--------|--------|
| D1 | Publish hooks #1, #11 + Pack 4 Shorts | views, TG joins |
| D2 | Pack 1 TG + X thread | bot starts |
| D3 | hooks #6, #7 + Pack 5 | guest-event clicks |
| D4 | Pack 2 + Remix best Short | engagement rate |
| D5 | Bot reaches T+48h — Starter intro | applications |
| D6 | Pack 3 (crypto, careful) | negative feedback ratio |
| D7 | Recap + scale top 3 hooks | Starter pre-orders target: 5 |

---

## Winner Criteria

Promote hook/pack to «scale» if:

- view-through > channel median;
- TG join rate > 2% of views (Shorts);
- bot start rate > 30% of TG joins;
- negative comments < 5%;
- at least 1 Starter application attributed.

---

← [EVENT_CONTENT_PACK_TEMPLATE.md](EVENT_CONTENT_PACK_TEMPLATE.md) · [CONTENT_MATRIX.md](CONTENT_MATRIX.md)
