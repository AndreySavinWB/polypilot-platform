# POLYPILOT STATE

> Главный оперативный статус проекта и единый источник правды для всех команд: `01_CEO`, `02_Product Manager`, `03_UX/UI Designer`, `04_Backend Dev`, `05_CRO / Monetization Manager`.

---

## Последний коммит

**SHA:** `8060053` (Strategy liquidity fix) · checkpoint hero+CRO+liquidity — pending push  
**Дата:** 2026-06-14

---

## Текущий этап

**Текущая фаза:** dual-track monetization; Funnel 1.0 + PolyPilot Starter (primary).  
**Текущий владелец:** `05_CRO` (публикация Pack #1) · `03_UX/UI` (hero/PIE sync) · `01_CEO` (контроль)

**Prod stack live:** Vercel frontend + Railway backend (`polypilot-platform-production.up.railway.app`). PIE v1.0g + Strategy Layer на `event.html?id=live-51456` — **проверено на prod** (Обучение / Кандидат). Hero `??%` для guest — tier lock + PRO banner (не баг API).

---

## Что готово

- Архитектура PIE v1.3 зафиксирована.
- Strategy Intelligence Layer v1.0 зафиксирован:
  - `PolyPilot-Штаб/07_Архитектура/STRATEGY_INTELLIGENCE_LAYER.md`
  - принцип: PIE = общий мозг, Strategy Layer = торговые линзы
  - первые стратегии: Whale Copy, News Lag, Mispricing, Market Structure Warning, Education
- Документы по новым PIE-блокам созданы:
  - Event Type Classifier
  - Market Structure Analyzer
  - Source Scoring System
  - Probability Formula v1.1
- Полный UI-аудит платформы выполнен.
- UI-каркас PIE v1.3 в `platform/app/event.html` принят.
- Backend-срез PIE v1.0b реализован:
  - Event Normalizer v0
  - Event Type Classifier v0
  - контракт `normalizedEvent + eventClassification + pipelineStatus`
  - smoke-test на 10 событиях проходит
- Backend-срез PIE v1.0c реализован:
  - Market Intelligence v0
  - `moneyDirection`
  - `volumeSignal`
  - `volumeAnomaly`
  - `whaleSignal` как эвристический placeholder
  - `confidence` capped at 0.50
  - `anomalies[]`
  - smoke-test на 10 событиях проходит
- Backend-срез PIE v1.0d реализован:
  - Evidence Collector v0
  - `evidence.items[]` из внутренних данных: `market` + `official`
  - `counts` по типам источников
  - `collectionStatus`
  - `scoringMode = rules_v0`
  - smoke-test на 10 событиях проходит
- Backend-срез PIE v1.0e реализован:
  - Strategy Router v0
  - `strategyIntelligence.primaryStrategy`
  - `strategyFits[]` для `whale_copy`, `news_lag`, `education`
  - `queues[]`
  - `userWhySelected`
  - `verdictMode`
  - smoke-test на 10 событиях проходит
- Backend-срез PIE v1.0f реализован:
  - Market Structure Analyzer v0
  - `marketHealthScore`
  - `liquidityTier`
  - `spreadRisk`
  - `manipulationRisk`
  - `priceReliability`
  - `marketReliability`
  - Strategy Router использует `marketStructure` для ограничения Whale Copy / News Lag
  - smoke-test на 10 событиях проходит
- Backend-срез PIE v1.0g реализован:
  - Probability Engine v0
  - `probability.marketProb`
  - `probability.ppProb`
  - `probability.edgePp`
  - `probability.components`
  - Strategy Verdict v0
  - `strategyVerdict.summary`
  - `strategyVerdict.requiredChecks`
  - `strategyVerdict.invalidation`
  - smoke-test на 10 событиях проходит
- Командная структура чатов зафиксирована:
  - `01_CEO`
  - `02_Product Manager`
  - `03_UX/UI Designer`
  - `04_Backend Dev`
  - `05_CRO / Monetization Manager`
- Создана операционная система управления проектом:
  - `POLYPILOT_STATE.md`
  - `CEO_OPERATING_SYSTEM.md`
- Создана рабочая зона монетизации:
  - `PolyPilot-Штаб/06_Монетизация/README.md`
  - `PolyPilot-Штаб/06_Монетизация/CRO_SYSTEM_PROMPT.md`
  - `PolyPilot-Штаб/06_Монетизация/MONETIZATION_STATE.md`
  - `PolyPilot-Штаб/06_Монетизация/FIRST_MONETIZATION_AUDIT.md`
  - `PolyPilot-Штаб/06_Монетизация/POLYMARKET_REFERRAL_ANALYSIS.md`
- Funnel 1.0 зафиксирован:
  - `PolyPilot-Штаб/05_Маркетинг/FUNNEL_1_0/` (сегменты, guardrails, content matrix, bot 72h, starter assets)
  - `PolyPilot-Штаб/05_Маркетинг/ВОРОНКА_И_ТГ.md` обновлён под Funnel 1.0
- Дорожная карта и навигация штаба синхронизированы (2026-06-14):
  - `PolyPilot-Штаб/07_Архитектура/ДОРОЖНАЯ_КАРТА_ОНЛАЙН.md`
  - `PolyPilot-Штаб/00_Старт/ДОМ_ШТАБ.md`
  - `PolyPilot-Штаб/01_Стратегия/КОНТЕКСТ_ПРОЕКТА_2.0.md`

---

## Что в работе

- **Track A — Funnel 1.0 (активен):** Event Content Pack #1 готов → CEO публикует 72h sprint.
  - Pack: `PolyPilot-Штаб/05_Маркетинг/FUNNEL_1_0/packs/PACK_001_FED_RATE_CUTS_2026.md`
  - Событие P0: `live-51456` · Fed rate cuts 2026 · guest-event + bot `event_live-51456`
  - Цепочка: Shorts/Reels/X → @polypilot_pro → guest-event → bot /starter
- Minimal paid proof: `PolyPilot Starter: Polymarket + 3 live разбора событий` (цель: 5–10 оплат).
- Product architecture: Strategy Intelligence Layer превращает ленту “интересных событий” в события, выбранные под конкретные trading setups.
- Integration prod (2026-06-14):
  - Railway backend Online · `/health` 200 · `PP_PROD_API_BASE` в `pp-config.js`
  - Strategy fix: `estimateLiquidity()` в `pie-api.js` — Priority Gate проходит без `liquidity` в карточке
  - Hero sync: `applyPieToHero()` — рынок из PIE/карточки; PP AI/Edge по tier
  - CRO strip на `event.html`: PRO banner → Telegram bot / pricing / guest-event
  - `sync_live_to_mvp.py`: поля `liquidity`, `liquidityFormatted`, `marketsCount` в events-live
- План набора **$10k lifetime volume** на Polymarket для unlock referral link.
- Финализация affiliate disclosure copy для Polymarket CTA (принцип утверждён CEO).
- Offer page / copy для PolyPilot Starter.

---

## Блокеры

- **Prod PIE:** ✅ Railway URL в `PP_PROD_API_BASE`; live PIE на Vercel prod-хостах.
- Hero `??%` для guest — **by design** (tier lock); разблокировка через PRO Trial / Telegram bot.
- `titleRu` в smoke-test остаётся на английском без LLM-ключа.
- Event Type Classifier v0 даёт rule-based misfire на edge cases: 2 из 10 тестовых событий.
- Market Intelligence работает только на данных Polymarket, без whale API.
- `marketIntelligence.confidence` ограничен 0.50 из-за отсутствия внешних MI-источников.
- `whaleSignal` является эвристикой по объёму и направлению, а не реальными кошельками.
- Evidence Collector v0 не подключает внешние источники, только `market` + `official`.
- `collectionStatus = partial` у всех тестовых событий, потому что нет реальных News API / RSS / Trends.
- Source Scoring, Contradiction Engine и Comparable Events пока не реализованы.
- Probability Engine v0 реализован rules-only; external evidence / historical / contradiction компоненты помечаются как missing.
- Market Structure Analyzer v0 реализован rules-only, без реальной wallet concentration.
- Strategy Router v0 пока rules-only и использует whale proxy по объёму, без реальных кошельков.
- Нет проверенного willingness-to-pay: нужны 5–10 оплат или pre-order commitments по Starter.
- Подписка PolyPilot 1.0 остаётся рабочей гипотезой, не первым CTA.
- Referral link недоступен до **$10k lifetime volume** на Polymarket.
- Не упакован offer page / copy для `PolyPilot Starter`.
- Не финализирован точный текст affiliate disclosure (принцип утверждён).

---

## Следующий шаг

**CEO — Track A T+0 (сейчас):** публикация Pack #1 · `packs/PACK_001_FED_RATE_CUTS_2026.md` ✅ в git

```text
T+0:  TG Post 1 + Short A → guest-event live-51456
T+2h: X thread (6 tweets)
T+24h: Post 2 + Short B
T+48h: Post 3 + Starter CTA + Short C
KPI: ≥3 guest clicks · ≥1 /starter · 1 оплата или 5 pre-orders
```

Prod links:
- guest: https://polypilot-platform.vercel.app/app/guest-event.html?id=live-51456&utm_source=tg&utm_campaign=funnel_1_0
- full:  https://polypilot-platform.vercel.app/app/event.html?id=live-51456
- bot:   https://t.me/polypilot_pro_bot?start=event_live-51456

Последний принятый backend-output:

```json
{
  "normalizedEvent": {
    "titleRu": "...",
    "resolutionCriteria": "...",
    "horizonDays": 42,
    "decisionMaker": "...",
    "marketSnapshot": {
      "marketProb": 0.56,
      "volume": 1200000,
      "liquidity": 240000
    },
    "normalizationStatus": "ok",
    "marketSnapshot": {
      "marketProb": 0.44,
      "volume": 33387971,
      "liquidity": 1961217
    }
  },
  "eventClassification": {
    "eventType": "regulatory",
    "subType": "fed_rate",
    "classifierConfidence": 0.87,
    "analysisProfile": "macro_regulatory"
  },
  "marketIntelligence": {
    "moneyDirection": "yes",
    "volumeSignal": "rising",
    "volumeAnomaly": "moderate",
    "whaleSignal": "none",
    "confidence": 0.5,
    "anomalies": [
      {
        "type": "volume_spike",
        "description": "24h volume is 1.8x average daily volume",
        "severity": "medium"
      }
    ],
    "scoringMode": "rules_v0"
  },
  "evidence": {
    "items": [
      {
        "type": "market",
        "title": "Рыночный сигнал Polymarket",
        "source": "Polymarket",
        "supportsOutcome": "yes",
        "confidence": 0.5
      },
      {
        "type": "official",
        "title": "Источник резолва",
        "supportsOutcome": "unknown",
        "confidence": 0.3
      }
    ],
    "counts": {
      "total": 2,
      "official": 1,
      "news": 0,
      "social": 0,
      "trends": 0,
      "market": 1
    },
    "collectionStatus": "partial",
    "scoringMode": "rules_v0"
  },
  "pipelineStatus": "v1_0d_complete"
}
```

---

## Последнее решение CEO

**Dual-track monetization утверждён (2026-06-14).**

1. **Track A primary:** PolyPilot Starter через Funnel 1.0.
2. **Track B secondary:** Polymarket referral после unlock $10k lifetime volume; CTA только после разбора, не в Shorts hooks.
3. **Контент-машина:** строить сейчас, **не** как referral-first funnel.
4. **Referral:** accelerator, not core business; PRO и PIE roadmap не меняем.
5. **Disclosure:** обязателен affiliate disclosure рядом с Polymarket CTA; точный текст — задача CRO/Product.

Checkpoint-коммит опубликован на GitHub/Vercel: UI-каркас PIE v1.3 + Project Operating System + Backend PIE v1.0b–v1.0d.

Первый CRO-аудит принят: не строим billing/auth сейчас. Первый путь к деньгам — `education + premium reports + early access`.

Backend-срез PIE v1.0d принят: Event Normalizer v0 + Event Type Classifier v0 + Market Intelligence v0 + Evidence Collector v0.

До paid proof Starter не начинаем:

- billing/auth;
- aggressive referral funnel / referral-first контент;
- Track Record как marketing claim без истории;
- B2B/API;
- Compare Terminal;
- новых агентов PIE вне текущего roadmap.

---

## Последнее изменение архитектуры

PIE v1.3 утверждён как основа дальнейшей разработки.

Ключевые блоки v1.3:

- Event Type Classifier
- Market Structure Analyzer
- Source Scoring System
- Probability Formula v1.1

Архитектуру сейчас не расширяем.

---

## Последнее изменение UI

`03_UX/UI Designer` + `04_Backend Dev` — PIE v1.0g + Strategy Layer в `event.html`:

- `platform/assets/js/pie-api.js` — `loadPiePackage`, `mapStoreEventToPieInput`, `renderPieFromPackage`
- `platform/assets/js/pp-config.js` — prod auto-config (`usePieApi`, `PP_PROD_API_BASE`)
- Strategy badge, Strategy verdict, Market Structure, Probability — real data или mock fallback
- Globals: `window.__PP_PIE_PACKAGE__`, `__PP_PIE_META__`, `__PP_PIE_STRATEGY__`, `__PP_PIE_VERDICT__`

---

## Последнее изменение Backend

Backend-срез PIE v1.0d реализован.

Реализовано:

- Event Normalizer v0
- Event Type Classifier v0
- Market Intelligence v0
- Evidence Collector v0
- `backend/src/agents/normalizer.py`
- `backend/src/agents/classifier.py`
- `backend/src/agents/market_intelligence.py`
- `backend/src/agents/evidence_collector.py`
- `backend/src/agents/pie.py`
- `backend/scripts/test_pie.py`
- endpoint `/api/pie/process`

Проверка:

- smoke-test проходит на 10 событиях;
- контракт `normalizedEvent + eventClassification + marketIntelligence + evidence + pipelineStatus` соблюдён;
- classifier имеет 2/10 misfire на edge cases, это не блокер для v0.

---

## Последнее изменение Product

Продуктовый фокус зафиксирован:

- не строить весь PIE сразу;
- двигаться вертикальными срезами;
- сначала получить реальные PIE-данные;
- затем подключать эти данные в уже подготовленный UI;
- сложную оплату и расширенные продуктовые фичи отложить до проверки ценности;
- monetization-гипотезу теперь прорабатывает `05_CRO` до разработки billing/auth.

---

## Последнее изменение Monetization

CEO утвердил **dual-track monetization** по анализу `POLYMARKET_REFERRAL_ANALYSIS.md`.

```text
Track A (primary):  Funnel 1.0 → PolyPilot Starter
Track B (secondary): referral после $10k volume gate + CTA после разбора
Track C (later):     real PIE-output → Early Access → PRO
```

Ключевые правила:

- контент-машина стартует сейчас, не вокруг referral как core;
- referral = accelerator, not core business;
- Telegram = бесплатный hub, деньги через Starter на старте;
- PRO 2 990 ₽/мес — гипотеза, не первый CTA;
- affiliate disclosure обязателен у Polymarket CTA.

Первый paid offer:

```text
PolyPilot Starter: Polymarket + 3 live разбора событий · 4 990–9 990 ₽
```

KPI 60 дней: 5–10 Starter payments · unlock $10k volume · baseline referral metrics.

Документы:

- `PolyPilot-Штаб/06_Монетизация/POLYMARKET_REFERRAL_ANALYSIS.md`
- `PolyPilot-Штаб/05_Маркетинг/FUNNEL_1_0/README.md`
- `PolyPilot-Штаб/06_Монетизация/MONETIZATION_STATE.md`

Event Content Pack #1:

```text
Файл: PolyPilot-Штаб/05_Маркетинг/FUNNEL_1_0/packs/PACK_001_FED_RATE_CUTS_2026.md
Статус: ready to publish · PIE reference snapshot (rules_v0 · preliminary)
CTA: guest-event → bot event → Starter (T+48h)
```

Funnel 1.0 KPI недели (baseline до публикации):

| Метрика | Цель | Факт |
|---------|------|------|
| Pack опубликован (TG + ≥1 Short) | 1 | — |
| guest-event clicks from TG | ≥3 | — |
| bot `/starter` заявки | ≥1 | — |
| Starter оплата / pre-order | 1 или 5 | — |

Следующий monetization-фокус:

```text
CEO: публикация Pack #1 (72h) · метрики в Sheet · Pack #2 после baseline
```

---

## Правило Обновления

Любая завершённая задача считается незавершённой, пока не обновлён `POLYPILOT_STATE.md`.

Это правило обязательно для всех команд:

- `02_Product Manager`
- `03_UX/UI Designer`
- `04_Backend Dev`
- `05_CRO / Monetization Manager`

После завершения задачи команда должна вернуть в `01_CEO`:

```text
Что сделано
Какие файлы изменены
Что изменилось в статусе проекта
Как нужно обновить POLYPILOT_STATE.md
```

---

## Ответственный За Актуальность

Главный ответственный: `01_CEO`.

Правило ответственности:

- команда выполняет задачу и сообщает, что изменилось;
- `01_CEO` принимает результат;
- `01_CEO` обновляет `POLYPILOT_STATE.md` или явно поручает это команде;
- без обновления state задача не считается закрытой.
