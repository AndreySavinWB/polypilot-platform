# Event Content Pack #1 — Fed Rate Cuts 2026

> **Pack ID:** PACK_001 · **Priority:** P0 · **Status:** ready to publish  
> **Owner:** `05_CRO` · **Date:** 2026-06-14  
> **Track:** A (Starter primary) · **Referral CTA:** нет (до $10k gate)

---

## Meta

| Field | Value |
|-------|-------|
| event_id | `live-51456` |
| polymarket_id | `51456` |
| title_en | How many Fed rate cuts in 2026? |
| title_ru | Сколько снижений ставки ФРС будет в 2026? |
| category / eventType | Макро · `regulatory` / `fed_rate` |
| markets_count | 13 подрынков |
| volume_total | ~$33.5M |
| volume_24h | ~$159K |
| liquidity | ~$2.0M |
| horizon | до 2026-12-31 (~203 дня) |
| pack_owner | 05_CRO |
| priority | **P0** |

**Links**

| Destination | URL |
|-------------|-----|
| Guest funnel | `guest-event.html?id=live-51456&utm_source={channel}&utm_campaign=funnel_1_0` |
| Full PP card | `event.html?id=live-51456` |
| Polymarket | https://polymarket.com/event/how-many-fed-rate-cuts-in-2026 |
| TG channel | https://t.me/polypilot_pro |
| TG bot (event) | https://t.me/polypilot_pro_bot?start=event_live-51456 |
| TG bot (Starter) | https://t.me/polypilot_pro_bot?start=starter |
| Starter offer | `learn.html#starter` |

---

## 1. One-liner

На Polymarket открыт **мульти-рынок по снижениям ставки ФРС в 2026**: 13 подрынков, один официальный источник резолва (FOMC) — и большинство читает только одну цифру, не resolution criteria.

---

## 2. Market angle

**Что думает рынок (snapshot Polymarket, 2026-06-14):**

| Подрынок | Implied prob (YES) | Комментарий |
|----------|-------------------|-------------|
| **0 снижений в 2026** | **~80%** | доминирующий narrative |
| 1 снижение | ~12.5% | |
| 2 снижения | ~3% | хвост распределения |

- **Key signal:** рынок массово ставит на сценарий «ставку не снижают в 2026» (0 cuts).
- **volume_24h:** ~$159K при total ~$33.5M — интерес сохраняется, не «мёртвый» рынок.
- **movement:** activity rising (Polymarket feed).

**Важно для контента:** это не один YES/NO, а **распределение по числу cuts**. Hook «80%» всегда сопровождать: «80% на подрынке *0 cuts*, не на всё событие целиком».

---

## 3. Risk angle (что большинство не учитывает)

1. **Multi-market resolution:** 13 подрынков; резолв по **количеству снижений на 25 bps**, включая emergency cuts; ранний резолв в «No», если исход уже невозможен.
2. **Partial evidence (PIE):** `collectionStatus = partial` — нет полноценного news/social/trends feed; только market + official resolution source.
3. **multi_market_complex:** сложнее интерпретировать «одну вероятность» без чтения criteria; ошибка новичка = торговать не тот подрынок.

---

## 4. Education angle

**Принцип:** *Resolution criteria важнее headline probability.*

На этом событии можно за 60 секунд показать:

- чем multi-market Polymarket отличается от «одной монеты»;
- почему 80% на «0 cuts» ≠ «ФРС точно не снизит ставку» без чтения правил;
- зачем смотреть official source (FOMC calendar + fed funds target);
- почему PolyPilot относит такие кейсы к **Education setup**, а не к «сигналу».

---

## 5. PP angle — PIE v1.0g reference snapshot

> **Disclaimer обязателен в каждом asset:**  
> `Preliminary analysis · rules_v0 · не финансовый совет · не обещаем прибыль`

Данные ниже — **reference snapshot** для контента (согласовано с `test_events.json` + `events-live.js` + логика PIE v1.0g). При публикации сверить с live `event.html?id=live-51456` если `usePieApi` активен.

| Block | Value |
|-------|-------|
| pipelineStatus | `v1_0g_complete` (expected) |
| eventType / subType | `regulatory` / `fed_rate` |
| classifierConfidence | ~0.87 (rule-based) |
| collectionStatus | `partial` |
| scoringMode | `rules_v0` |

**Market snapshot**

| Metric | Value |
|--------|-------|
| marketProb (card) | ~80% |
| ppProb (card) | ~75% |
| edgePp | ~0 pp (card) / small negative vs top strike |
| probability.status | `preliminary` |

**Market structure (rules_v0)**

| Metric | Expected |
|--------|----------|
| marketHealthScore | high band (volume ~$33M, liquidity ~$2M) |
| liquidityTier | `high` |
| priceReliability | `moderate`–`high` |
| manipulationRisk | `low`–`medium` |
| crowdParticipation | `high` |

**Strategy Intelligence (expected primary: `education`)**

```text
primaryStrategy: education
userWhySelected: PP выбрал событие как учебный кейс: на нём можно объяснить механику Polymarket и анализа PP.
verdictMode: education_case
queues: education_queue, news_queue (watchlist possible)
```

**Strategy verdict (template copy from PIE logic)**

```text
summary: Событие подходит как учебный кейс: clear event category regulatory; official/resolution evidence exists; multi-market structure worth explaining.
requiredChecks:
  - simple_resolution — прочитать criteria FOMC / 25bp / emergency cuts
  - clear_title — понять, какой подрынок смотришь (0 vs 1 vs 2 cuts)
  - teachable_contradiction — почему одна цифра 80% не равна «всё понятно»
invalidation:
  - too_complex — если аудитория не готова к multi-market
  - unclear_resolution — если criteria не прочитаны
  - no_context — если нет связи с macro calendar
```

**Risk**

```text
riskLevel: medium
factors: multi_market_complex, partial_evidence
```

---

## 6. Visual pack (brief for designer / CEO)

### A. Probability card

```text
[Заголовок] Fed rate cuts 2026 — что думает рынок
[Bar 1] 0 cuts: ~80%
[Bar 2] 1 cut: ~12%
[Bar 3] 2 cuts: ~3%
[Footnote] 13 подрынков · preliminary · rules_v0
[Logo] PolyPilot
```

### B. Risk checklist card

```text
Перед решением проверь:
☐ Какой подрынок ты смотришь (0 / 1 / 2 cuts)?
☐ Resolution criteria: 25 bps, emergency cuts, FOMC source
☐ Evidence partial — нет полного news feed
☐ Multi-market ≠ одна монета
[Disclaimer] Не финансовый совет
```

### C. Education card

```text
80% ≠ «точно не будет cuts»
= рынок так оценивает подрынок «0 cuts»
PolyPilot · teachable case
```

### D. CTA card

```text
Полный разбор → guest-event / event.html
PolyPilot Starter — научиться читать такие события
@polypilot_pro · @polypilot_pro_bot
```

---

## 7. Short scripts (15–25 сек)

### Script A — Education

**0–2s hook:**  
«80% на Polymarket — но 80% *чего*?»

**2–10s body:**  
«Это не одна монета. 13 подрынков: сколько раз ФРС снизит ставку в 2026. Сейчас рынок ~80% на сценарий *ноль* снижений. Без resolution criteria легко прочитать не то.»

**10–15s payoff:**  
«PolyPilot разбирает criteria, структуру рынка и риски — не сигнал.»

**CTA:**  
«Разбор в bio → Telegram @polypilot_pro»

**Disclaimer (on-screen text):**  
«Preliminary · rules_v0 · не финсовет»

**Link:** `guest-event.html?id=live-51456&utm_source=shorts`

---

### Script B — Anomaly / Structure

**0–2s hook:**  
«$33M объёма — и большинство смотрит только одну цифру.»

**2–10s body:**  
«Fed cuts 2026: top strike ~80% на 0 cuts, но хвосты на 1–2 cuts всё ещё живы. Multi-market + partial evidence = нужен чеклист, не hype.»

**10–15s payoff:**  
«PP помечает это как education case: учимся читать рынок.»

**CTA:**  
«Полный разбор → ссылка в Telegram»

**Link:** `guest-event.html?id=live-51456&utm_source=shorts_anomaly`

---

### Script C — Newsjacking (macro)

**0–2s hook:**  
«Что prediction market думает о ФРС в 2026?»

**2–10s body:**  
«Не опрос CNN — цена на Polymarket. Сейчас доминирует сценарий без cuts в 2026. Но это цена *конкретного* подрынка, не магический прогноз.»

**10–15s payoff:**  
«Разбор criteria + структура — в PolyPilot.»

**CTA:**  
«@polypilot_pro — разбор дня»

**Link:** `guest-event.html?id=live-51456&utm_source=shorts_macro`

---

## 8. Telegram posts

### Post 1 — Hook (T+0, без продажи)

```text
📊 Событие дня: Fed rate cuts 2026

На Polymarket — не одна монета, а 13 подрынков: сколько раз ФРС снизит ставку на 25 bps в 2026.

Сейчас top strike «0 cuts» ≈ 80%.
Но большинство не читает resolution criteria: emergency cuts, FOMC source, early resolve rules.

PolyPilot разобрал структуру и риски (preliminary · rules_v0).

→ Полный разбор: [guest-event link]
→ Карточка PP: event.html?id=live-51456

PolyPilot — аналитика и образование. Не финансовый совет. Не обещаем прибыль.
```

**Button:** `Открыть разбор` → guest-event

---

### Post 2 — Mini-breakdown (T+24h)

```text
🔍 Fed 2026 — что важно кроме «80%»

1️⃣ Multi-market: отдельные цены на 0 / 1 / 2 cuts
2️⃣ Resolution: только официальные FOMC statements + fed funds target
3️⃣ PP Strategy Layer: education case — учим читать рынок, не «сигнал»
4️⃣ Evidence partial: market + official, без полного news feed

PP probability snapshot: market ~80% · PP ~75% · edge ~0pp
(rules_v0 · preliminary — сверь на карточке)

→ Разбор: [guest-event]
→ Бот пришлёт ещё 2 события: @polypilot_pro_bot?start=event_live-51456

Не финансовый совет.
```

---

### Post 3 — Soft CTA Starter (T+48h)

```text
🎓 Хотите понимать такие события системно?

PolyPilot Starter — первый cohort:
• mini-course Polymarket с нуля
• 3 live разбора (Fed 2026 — одно из них)
• 7 дней research feed

Не сигналы. Не «гарантированная прибыль».
Early price: 4 990 ₽ · ~10 мест

→ Запись: @polypilot_pro_bot?start=starter
→ Что входит: learn.html#starter

Уже смотрели разбор Fed? Напишите в бот «Хочу Starter».
```

---

## 9. X thread (6 tweets)

**Tweet 1 (hook):**  
Polymarket: «How many Fed rate cuts in 2026?»  
~$33M volume. Not one market — 13 sub-markets.  
Thread: what the price actually means 🧵  
(not financial advice)

**Tweet 2:**  
Top strike right now: ~80% implied on **0 cuts** in 2026.  
That is NOT «80% Fed will never cut.»  
It is the price of one specific sub-market.

**Tweet 3:**  
Resolution criteria matter:  
• 25 bps cuts count  
• emergency cuts count  
• resolves on official FOMC / fed funds target  
• can resolve early if outcome impossible

**Tweet 4:**  
Distribution snapshot:  
0 cuts ~80% · 1 cut ~12.5% · 2 cuts ~3%  
Tail outcomes still exist — multi-market structure is the story.

**Tweet 5:**  
@PolyPilot (RU) marks this as an **education case** in Strategy Layer — teach resolution + market structure, not tips.  
Preliminary · rules_v0 · partial evidence

**Tweet 6 (disclaimer + CTA):**  
Analytics only. No profit promises.  
Full breakdown (RU): [guest-event link]  
TG: @polypilot_pro · Starter cohort open → bot /starter

---

## 10. CTA block

| Priority | CTA | When |
|----------|-----|------|
| Primary T+0–24h | guest-event / event card | Posts 1–2, all Shorts |
| Secondary T+0 | TG bot `event_live-51456` | Post 2, guest-event button |
| Tertiary T+48h | Starter `learn.html#starter` + bot `/starter` | Post 3 only |
| Forbidden | PRO trial, «ставь YES», Polymarket referral | — |

**Deep links**

```text
guest-event: guest-event.html?id=live-51456&utm_source={channel}&utm_campaign=funnel_1_0
bot event:   https://t.me/polypilot_pro_bot?start=event_live-51456
bot starter: https://t.me/polypilot_pro_bot?start=starter
starter:     learn.html#starter?utm_source=tg&utm_campaign=starter_cohort_1
```

---

## 11. Compliance check

- [x] no profit promise
- [x] no «signal» / «ставь YES» language
- [x] disclaimer in every asset
- [x] preliminary / rules_v0 marked
- [x] CTA → breakdown / education / Starter (not bet)
- [x] no Polymarket referral CTA
- [x] no PRO subscription CTA
- [x] multi-market nuance explained (80% context)

---

## 12. Publish schedule (72h)

| Time | Asset | Channel | Owner | KPI |
|------|-------|---------|-------|-----|
| **T+0** | Post 1 | @polypilot_pro | CEO | views, guest clicks |
| **T+0** | Script A video | Shorts/Reels | CEO | bio → TG joins |
| **T+2h** | X thread | X | CEO | link clicks |
| **T+4h** | Bot trigger* | @polypilot_pro_bot | CEO/auto | bot starts |
| **T+24h** | Post 2 | @polypilot_pro | CEO | guest clicks |
| **T+24h** | Script B | Shorts | CEO | remix test |
| **T+48h** | Post 3 + Starter CTA | @polypilot_pro | CEO | /starter applications |
| **T+48h** | Script C | Reels | CEO | — |
| **T+72h** | Recap + last cohort call | TG | CEO | applications count |

\*Bot sequence: см. [BOT_SEQUENCE_72H.md](../BOT_SEQUENCE_72H.md) — payload `event_live-51456`.

---

## 13. CEO manual vs automate later

| Сейчас вручную (CEO / Marketing) | Автоматизировать позже |
|----------------------------------|-------------------------|
| Публикация TG posts 1–3 | Scheduler (Buffer / native TG) |
| Запись Shorts/Reels | Remotion template from Event Pack |
| X thread | Typefully / scheduled posts |
| Visual cards (4 шт.) | Figma template → auto-fill from PIE JSON |
| Ответы на заявки Starter в боте | Bot flow + CRM sheet |
| Сверка PIE numbers перед постом | `usePieApi` + pack auto-fill script |
| Метрики в Google Sheet | UTM + bot tags → dashboard |

---

## 14. KPI недели (Pack #1)

| Metric | Target |
|--------|--------|
| Pack published | TG + ≥1 Short |
| guest-event clicks from TG | ≥3 |
| bot starts (`event_live-51456`) | baseline |
| `/starter` applications | ≥1 |
| Starter payments / pre-orders | 1 или 5 commitments (cohort) |
| Negative feedback | <5% «scam/signal» |

---

## 15. Remix if winner

If Script A or Post 1 beats median CTR:

- republish with hook «13 подрынков, одна ошибка новичка»;
- add carousel «0 vs 1 vs 2 cuts»;
- feed winning asset into bot day 1 message.

---

← [EVENT_CONTENT_PACK_TEMPLATE.md](../EVENT_CONTENT_PACK_TEMPLATE.md) · [LAUNCH.md](../LAUNCH.md) · [STARTER_OFFER.md](../../../06_Монетизация/STARTER_OFFER.md)
