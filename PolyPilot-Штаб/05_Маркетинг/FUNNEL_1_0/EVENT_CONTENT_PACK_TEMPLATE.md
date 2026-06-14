# Event Content Pack Template — Funnel 1.0

> Единица производства контент-завода. Один Event Pack = один Polymarket event → весь контент на все каналы.

---

## Когда Создавать Pack

Создавать Event Content Pack, если событие проходит минимум 2 из 4:

- volume / interest выше среднего;
- есть newsjacking potential (macro, politics, crypto);
- есть teachable moment (resolution, risk, probability);
- есть anomaly или движение цены без сильного evidence.

---

## Шаблон Pack

```text
# Event Content Pack — [EVENT_ID]

## Meta
- event_id:
- title_ru:
- title_en:
- category / eventType:
- market_prob:
- volume_24h:
- horizon_days:
- pack_date:
- pack_owner:
- priority: P0 / P1 / P2

## 1. One-liner (что случилось)
[1 предложение — факт события, без hype]

## 2. Market angle (что думает рынок)
- market_prob:
- movement_24h:
- key_signal:

## 3. Risk angle (что большинство не учитывает)
- risk_1:
- risk_2:
- risk_3:

## 4. Education angle (какой принцип виден)
[resolution / probability / liquidity / evidence — один принцип]

## 5. PP angle (если есть real data)
- pipeline_status:
- confidence:
- collection_status:
- disclaimer: rules_v0 / partial — не продавать как final analysis

## 6. Visual pack
- [ ] probability card (market vs context)
- [ ] timeline / movement chart
- [ ] risk checklist card
- [ ] CTA card (Telegram / guest-event)

## 7. Short scripts (3×)
### Script A — Education (15–25 сек)
0–2s hook:
2–10s body:
10–15s payoff:
CTA:

### Script B — Anomaly (15–25 сек)
...

### Script C — Newsjacking (15–25 сек)
...

## 8. Telegram posts (3×)
### Post 1 — Hook
### Post 2 — Mini-breakdown
### Post 3 — CTA (guest-event / bot / Starter)

## 9. X thread (5–7 tweets)
Tweet 1 hook:
Tweet 2–5 breakdown:
Tweet 6 disclaimer:
Tweet 7 CTA:

## 10. CTA block
- primary: [Telegram bot / guest-event / Starter]
- deep_link: guest-event.html?id=
- bot_payload: event_[ID]
- offer_mention: yes/no (only after bot day 2+)

## 11. Compliance check
- [ ] no profit promise
- [ ] no «signal» language
- [ ] disclaimer included
- [ ] mock/demo marked if applicable
- [ ] CTA leads to breakdown/education, not «bet now»

## 12. Publish schedule
| Asset | Channel | Time |
|-------|---------|------|
| Script A | Shorts/Reels | T+0 |
| Post 1 | Telegram | T+0 |
| Thread | X | T+2h |
| Script B | Shorts | T+24h |
| Post 2 | Telegram | T+24h |
| Script C | Reels | T+48h |
| Post 3 + CTA | Telegram | T+48h |
```

---

## Automation Pipeline

```text
Event Pool (Polymarket / PIE priority gate)
  → Content Brief (auto-fill meta from PIE v1.0d where available)
  → Scripts + TG posts + X thread + Visuals
  → Scheduler (Buffer / native / n8n later)
  → Analytics (views, CTR, TG joins, bot starts)
  → Winning hooks → Remix & Scale
```

---

## Data Sources For Brief

| Field | Source now | Source later |
|-------|------------|--------------|
| title_ru | PIE normalizer | LLM + normalizer |
| market_prob | Polymarket API | PIE marketSnapshot |
| eventType | PIE classifier | PIE classifier |
| volume / anomalies | PIE marketIntelligence | full MI |
| evidence summary | PIE evidence (partial) | full evidence + EQS |
| pp_prob / edge | not yet | Probability Engine |

**Правило:** если `pipeline_status != complete` или `collectionStatus = partial` — в контенте явно: «preliminary analysis / rules_v0».

---

## Output Checklist Per Pack

- [ ] 3 short scripts
- [ ] 3 TG posts
- [ ] 1 X thread
- [ ] 4 visuals
- [ ] 1 CTA block
- [ ] compliance check passed
- [ ] publish schedule set

---

## Remix Rules

Если asset показал top 20% CTR:

- переделать hook в 2 новых варианта;
- опубликовать на другом канале;
- добавить в bot sequence as winning example;
- не менять factual claims — только hook/формат.

---

← [CONTENT_MATRIX.md](CONTENT_MATRIX.md) · [STARTER_ASSETS.md](STARTER_ASSETS.md)
