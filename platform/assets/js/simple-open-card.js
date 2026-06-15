/** Simple Events — open event card (detail page). */
(function (global) {
  const CARD = global.PP_SIMPLE_CARD || {};

  const DEFAULT_REASONS = [
    "Рынок почти не учитывает этот исход",
    "Есть сигналы, которые указывают на изменение вероятности",
    "Похожие события раньше часто недооценивались рынком",
  ];

  const DEFAULT_RISKS = [
    "событие может развиваться непредсказуемо",
    "решение может не успеть пройти до даты закрытия",
    "рынок может быть прав, если официальных шагов не будет",
    "данные могут быть шумом, а не реальным сигналом",
  ];

  const CHECK_CATALOG = [
    { id: "eventRules", label: "Формулировка и правила резолва" },
    { id: "news", label: "Новости" },
    { id: "official", label: "Официальные источники" },
    { id: "social", label: "X / Reddit / соцсети" },
    { id: "trends", label: "Google Trends / поисковый интерес" },
    { id: "youtubeMedia", label: "YouTube / медиа" },
    { id: "marketComments", label: "Комментарии участников рынка" },
    { id: "comparableEvents", label: "Похожие события" },
    { id: "polymarketHistory", label: "Исторические данные Polymarket" },
    { id: "externalAnalytics", label: "Внешние аналитические сервисы" },
    { id: "contradictions", label: "Противоречия между источниками" },
    { id: "risks", label: "Риски и неизвестные" },
  ];

  const STUB_MARKERS = ["stub", "mock"];

  function isRealDataSource(dataSource) {
    if (!dataSource) return true;
    const lower = String(dataSource).toLowerCase();
    return !STUB_MARKERS.some((m) => lower.includes(m));
  }

  function hasWarRoomAgent(ev, roleHint) {
    return (ev.warRoom?.agents || []).some((a) => String(a.role || "").includes(roleHint));
  }

  function resolveCheckedReview(ev) {
    if (ev.checkedReview?.checks?.length) return ev.checkedReview;

    const crowd = ev.crowdPulse || {};
    const social = crowd.socialDiscussion || {};
    const marketComments = crowd.marketComments || {};
    const socialSources = social.sources || [];
    const socialFound = (platforms) =>
      isRealDataSource(social.dataSource) &&
      socialSources.some((s) => s.found && platforms.includes(s.platform));

    const checks = CHECK_CATALOG.map((item) => {
      let done = false;
      switch (item.id) {
        case "eventRules":
          done = !!(ev.title && (ev.summary || ev.resolveDate));
          break;
        case "news":
          done = !!(ev.news?.length || hasWarRoomAgent(ev, "Сбор фактов"));
          break;
        case "official":
          done = !!(ev.summary?.length > 40 || ev.marketUrl);
          break;
        case "social":
          done = socialFound(["x", "reddit", "telegram"]);
          break;
        case "trends":
          done = false;
          break;
        case "youtubeMedia":
          done = socialFound(["youtube", "news"]);
          break;
        case "marketComments":
          done =
            isRealDataSource(marketComments.dataSource) &&
            Number(marketComments.commentCount || 0) > 0;
          break;
        case "comparableEvents":
          done = false;
          break;
        case "polymarketHistory":
          done = ev.marketOdds != null;
          break;
        case "externalAnalytics":
          done = false;
          break;
        case "contradictions":
          done = Math.abs((ev.aiOdds || 0) - (ev.marketOdds || 0)) >= 8;
          break;
        case "risks":
          done = !!(ev.riskTags?.length || ev.riskLevel || hasWarRoomAgent(ev, "риска"));
          break;
        default:
          done = false;
      }
      return { ...item, done };
    });

    return {
      lastCheckedAt: ev.proofTrack?.opened || null,
      checks,
    };
  }

  function formatCheckedDate(value) {
    if (!value) return "—";
    const raw = String(value);
    const iso = raw.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (iso) {
      const d = new Date(Number(iso[1]), Number(iso[2]) - 1, Number(iso[3]));
      return d.toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });
    }
    const parsed = new Date(raw);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });
    }
    return raw;
  }

  const ICON_BRAIN = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a4 4 0 0 1 4 4c0 .8-.2 1.5-.6 2.1A4 4 0 0 1 16 17a4 4 0 0 1-8 0 4 4 0 0 1-.4-7.9A4 4 0 0 1 12 3z"/><path d="M8 10H6a2 2 0 0 0 0 4h2"/><path d="M16 10h2a2 2 0 0 1 0 4h-2"/></svg>`;
  const ICON_SHIELD = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z"/></svg>`;
  const ICON_TREND = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4,16 9,11 13,15 20,6"/><polyline points="15,6 20,6 20,11"/></svg>`;
  const ICON_BULB = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a6 6 0 0 0-4 10c.6.6 1 1.2 1 2h6c0-.8.4-1.4 1-2a6 6 0 0 0-4-10z"/></svg>`;
  const ICON_BELL = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>`;
  const ICON_MARKET = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`;
  const ICON_EXT = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3h7v7"/><path d="M10 14 21 3"/><path d="M21 14v7h-7"/><path d="M3 10V3h7"/><path d="M3 21l7-7"/></svg>`;
  const ICON_SHARE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5 15.4 17.5"/><path d="M15.4 6.5 8.6 10.5"/></svg>`;
  const ICON_CROWD = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`;
  const ICON_PMA = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-7"/></svg>`;
  const ICON_WHALE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12c2-4 6-7 10-7s8 3 10 7c-2 4-6 7-10 7S4 16 2 12z"/><circle cx="8" cy="11" r="1"/><path d="M16 10c1.5 1 2.5 2.5 2.5 2.5"/></svg>`;

  const PMA_STATUS_LABELS = {
    found: "Найдено",
    not_found: "Не найдено",
    similar_found: "Найдено похожее",
    error: "Ошибка проверки",
  };

  const PMA_IMPACT_LABELS = {
    positive: "Поддерживает прогноз",
    negative: "Снижает доверие к рыночной цене",
    neutral: "Почти не влияет на прогноз",
    weak_positive: "Слегка поддерживает прогноз",
    weak_negative: "Слегка снижает доверие к рыночной цене",
  };

  const WHALE_LOOKUP_LABELS = {
    found: "Найдено в Hashdive",
    not_found: "Не найдено",
    similar_found: "Найдено похожее",
    error: "Ошибка проверки",
    not_supported: "Источник недоступен",
  };

  const WHALE_IMPACT_LABELS = {
    neutral: "Нейтральное",
    weak_positive: "Слабое положительное",
    weak_negative: "Слабое отрицательное",
    moderate_positive: "Умеренное положительное",
    moderate_negative: "Умеренное отрицательное",
  };

  const WHALE_SKEW_LABELS = {
    weak: "слабый",
    medium: "средний",
    strong: "сильный",
  };

  const LEAN_LABELS = {
    yes: "скорее YES",
    no: "скорее NO",
    split: "мнения разделены",
    unclear: "непонятно",
  };
  const NOISE_LABELS = {
    low: "низкий",
    medium: "средний",
    high: "высокий",
  };

  function formatUsd(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "—";
    if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `$${Math.round(n / 1_000)}K`;
    return `$${Math.round(n)}`;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function clampPct(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return 0;
    return Math.max(0, Math.min(100, Math.round(n)));
  }

  function computeVerdict(ev) {
    if (CARD.computeSimpleVerdict) {
      return CARD.computeSimpleVerdict(ev.marketOdds, ev.aiOdds ?? ev.confidence);
    }
    const market = clampPct(ev.marketOdds ?? 50);
    const pp = clampPct(ev.aiOdds ?? ev.confidence ?? 50);
    const delta = pp - market;
    if (delta >= 8) return { tone: "under", delta };
    if (delta <= -8) return { tone: "over", delta };
    return { tone: "match", delta };
  }

  function getHeadline(ev, verdict) {
    const d = Math.abs(verdict.delta || 0);
    if (verdict.tone === "under") return d >= 25 ? "Рынок сильно занижен" : "Рынок занижен";
    if (verdict.tone === "over") return d >= 25 ? "Рынок сильно завышен" : "Рынок завышен";
    return "Совпадаем с рынком";
  }

  function getPlainText(ev, verdict) {
    if (ev.simpleVerdictLine) return ev.simpleVerdictLine;
    const text = ev.verdictText || "";
    if (text.length > 40 && text.length <= 200) return text;
    if (verdict.tone === "under") {
      return "Рынок почти не закладывает исход — PolyPilot видит сильное расхождение по данным.";
    }
    if (verdict.tone === "over") {
      return "Рынок переоценивает вероятность — PolyPilot видит завышение относительно сигналов.";
    }
    return "Оценки близки — детали и аргументы ниже.";
  }

  function getConfidenceLabel(ev) {
    const map = { low: "низкая", medium: "средняя", high: "высокая" };
    return map[ev.riskLevel] || "средняя";
  }

  function getRiskLabel(ev) {
    const map = { low: "низкий", medium: "средний", high: "высокий" };
    return map[ev.riskLevel] || "средний";
  }

  function getHorizonLabel(ev) {
    if (CARD.formatHorizonLong) return CARD.formatHorizonLong(ev);
    const m = String(ev.horizon || "").match(/(\d+)/);
    return m ? `${m[1]} дней` : ev.horizon || "—";
  }

  function getMetaLine(ev) {
    const cat = CARD.getCategoryLabel ? CARD.getCategoryLabel(ev) : ev.category || "Событие";
    const horizon = CARD.formatHorizonLong ? CARD.formatHorizonLong(ev) : getHorizonLabel(ev);
    return `${cat} · ${horizon}`;
  }

  function buildReasons(ev) {
    const out = [];
    const yes = ev.arguments?.yes || [];
    yes.forEach((item) => {
      const text = String(item).trim();
      if (text.length > 16 && out.length < 4) out.push(text);
    });

    (ev.warRoom?.agents || []).forEach((agent) => {
      const role = String(agent.role || "").toLowerCase();
      if (role.includes("риск") || role.includes("risk")) return;
      const msg = String(agent.message || "").trim();
      if (msg.length > 20 && out.length < 4 && !out.includes(msg)) out.push(msg);
    });

    DEFAULT_REASONS.forEach((line) => {
      if (out.length < 3) out.push(line);
    });

    if (out.length && ev.marketOdds != null && clampPct(ev.marketOdds) <= 10) {
      const market = clampPct(ev.marketOdds);
      if (String(out[0]).includes("Рынок почти не учитывает")) {
        out[0] = `Рынок почти не учитывает этот исход — текущая вероятность всего ${market}%.`;
      }
    }

    if ((ev.riskLevel === "high" || ev.riskLevel === "medium") && out.length < 4) {
      out.push("Но данных пока недостаточно для сильной уверенности");
    }

    return out.slice(0, 4);
  }

  function buildRisks(ev) {
    const tags = ev.riskTags || ev.arguments?.no || [];
    if (tags.length) {
      return tags.slice(0, 4).map((t) => String(t).replace(/^[-—•]\s*/, "").trim());
    }
    return DEFAULT_RISKS;
  }

  function buildChanges(ev) {
    const items = [];
    const changes = ev.changes || [];
    changes.slice(0, 4).forEach((c) => {
      if (c.title || c.text || c.summary) {
        items.push(String(c.title || c.text || c.summary));
      }
    });

    const pt = ev.proofTrack || {};
    if (pt.marketOddsAtOpen != null && ev.marketOdds != null && pt.marketOddsAtOpen !== ev.marketOdds) {
      items.push(`рынок был ${pt.marketOddsAtOpen}%, стал ${ev.marketOdds}%`);
    }

    if (ev.riskLevel === "high") {
      items.push("риск пока высокий");
    }

    return items;
  }

  function renderSegments(pct, variant) {
    const SEGMENTS = 20;
    const filled = Math.round((clampPct(pct) / 100) * SEGMENTS);
    let html = `<div class="sc-segments sc-segments--${variant}">`;
    for (let i = 0; i < SEGMENTS; i += 1) {
      html += `<i class="${i < filled ? "on" : ""}"></i>`;
    }
    html += "</div>";
    return html;
  }

  function renderVsBlock(ev) {
    const market = clampPct(ev.marketOdds ?? 50);
    const pp = clampPct(ev.aiOdds ?? ev.confidence ?? 50);
    return `
      <div class="sc-vs-wrap">
        <div class="sc-vs-side sc-vs-side--market">
          <div class="sc-vs-lbl">Рынок</div>
          <div class="sc-vs-val sc-vs-val--market">${market}%</div>
          ${renderSegments(market, "market")}
        </div>
        <div class="sc-vs-divider"><span>vs</span></div>
        <div class="sc-vs-side sc-vs-side--pp">
          <div class="sc-vs-lbl">PolyPilot</div>
          <div class="sc-vs-val sc-vs-val--pp">${pp}%</div>
          ${renderSegments(pp, "pp")}
        </div>
      </div>`;
  }

  function renderVerdictSection(ev) {
    const verdict = computeVerdict(ev);
    const headline = getHeadline(ev, verdict);
    const plain = getPlainText(ev, verdict);
    const toneClass = verdict.tone === "over" ? "is-over" : verdict.tone === "match" ? "is-match" : "";
    const riskClass = ev.riskLevel === "high" ? "risk-high" : ev.riskLevel === "low" ? "risk-low" : "";

    return `
      <section class="so-verdict">
        <div class="so-verdict-label">Вывод за 10 секунд</div>
        <h1 class="so-title">${escapeHtml(ev.title || "—")}</h1>
        <div class="so-meta">${escapeHtml(getMetaLine(ev))}</div>
        ${renderVsBlock(ev)}
        <div class="so-verdict-headline ${toneClass}">${escapeHtml(headline)}</div>
        <div class="so-plain">${escapeHtml(plain)}</div>
        <div class="so-pills">
          <span class="so-pill">Уверенность: <strong>${escapeHtml(getConfidenceLabel(ev))}</strong></span>
          <span class="so-pill ${riskClass}">Риск: <strong>${escapeHtml(getRiskLabel(ev))}</strong></span>
          <span class="so-pill">Горизонт: <strong>${escapeHtml(getHorizonLabel(ev))}</strong></span>
        </div>
      </section>`;
  }

  function renderAnalysisDuo(ev) {
    const reasons = buildReasons(ev);
    const risks = buildRisks(ev);

    return `
      <div class="so-duo">
        <div class="so-card so-card--reasons">
          <div class="so-card-head">
            <span class="so-card-icon so-card-icon--purple">${ICON_BRAIN}</span>
            <h2 class="so-card-title so-card-title--purple">Почему PolyPilot так думает</h2>
          </div>
          <ol class="so-card-list num">
            ${reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}
          </ol>
        </div>
        <div class="so-card so-card--risks">
          <div class="so-card-head">
            <span class="so-card-icon so-card-icon--orange">${ICON_SHIELD}</span>
            <h2 class="so-card-title">Что может пойти не так</h2>
          </div>
          <ul class="so-card-list dash">
            ${risks.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}
          </ul>
        </div>
      </div>`;
  }

  function renderCheckedSection(ev) {
    const review = resolveCheckedReview(ev);
    const checks = review.checks || [];
    const lastChecked = formatCheckedDate(review.lastCheckedAt);

    return `
      <section class="so-checked-card">
        <div class="so-checked-head">
          <div class="so-checked-head-main">
            <span class="so-checked-icon">${ICON_TREND}</span>
            <h2 class="so-checked-title">Мы проверили.</h2>
          </div>
          <div class="so-checked-date">Крайняя проверка: ${escapeHtml(lastChecked)}</div>
        </div>
        <div class="so-checked-chips">
          ${checks
            .map(
              (c) => `
            <span class="so-check-chip ${c.done ? "done" : ""}">
              <span class="so-check-chip-mark">${c.done ? "✓" : "·"}</span>
              ${escapeHtml(c.label)}
            </span>`
            )
            .join("")}
        </div>
      </section>`;
  }

  function formatLean(lean) {
    return LEAN_LABELS[lean] || LEAN_LABELS.unclear;
  }

  function formatNoise(level) {
    return NOISE_LABELS[level] || NOISE_LABELS.medium;
  }

  function renderCrowdPulseSection(ev) {
    const pulse = ev.crowdPulse;
    if (!pulse) return "";

    const status = pulse.status || "insufficient";
    const market = pulse.marketComments;
    const social = pulse.socialDiscussion;
    const synthesis = pulse.synthesis;

    if (status === "insufficient" || (!market && !social)) {
      return `
      <section class="so-crowd-card">
        <div class="so-crowd-head">
          <span class="so-crowd-icon">${ICON_CROWD}</span>
          <h2 class="so-crowd-title">Анализ комментариев</h2>
        </div>
        <p class="so-crowd-empty">Недостаточно комментариев для вывода.</p>
      </section>`;
    }

    const marketNoise = market?.noiseLevel || "medium";
    const socialNoise = social?.noiseLevel || "medium";
    const noisyNote =
      marketNoise === "high" || socialNoise === "high"
        ? `<p class="so-crowd-note">Обсуждение шумное, влияние на прогноз слабое.</p>`
        : "";

    const marketBlock = market
      ? `
        <div class="so-crowd-part so-crowd-part--market">
          <div class="so-crowd-part-label">Внутри события</div>
          <div class="so-crowd-row"><span>Склонение:</span> ${escapeHtml(formatLean(market.lean))}</div>
          <div class="so-crowd-row so-crowd-row--main"><span>Главная мысль:</span> ${escapeHtml(market.summaryRu || "—")}</div>
          <div class="so-crowd-row"><span>Шум:</span> ${escapeHtml(formatNoise(marketNoise))}</div>
        </div>`
      : "";

    const socialBlock = social
      ? `
        <div class="so-crowd-part so-crowd-part--social">
          <div class="so-crowd-part-label">В сети</div>
          <div class="so-crowd-row"><span>Склонение:</span> ${escapeHtml(formatLean(social.lean))}</div>
          <div class="so-crowd-row so-crowd-row--main"><span>Главная мысль:</span> ${escapeHtml(social.summaryRu || "—")}</div>
          <div class="so-crowd-row"><span>Шум:</span> ${escapeHtml(formatNoise(socialNoise))}</div>
        </div>`
      : "";

    const synthesisBlock = synthesis?.summaryRu
      ? `
        <div class="so-crowd-synthesis">
          <div class="so-crowd-part-label">Общий вывод</div>
          <p>${escapeHtml(synthesis.summaryRu)}</p>
        </div>`
      : "";

    return `
      <section class="so-crowd-card">
        <div class="so-crowd-head">
          <span class="so-crowd-icon">${ICON_CROWD}</span>
          <h2 class="so-crowd-title">Анализ комментариев</h2>
        </div>
        <div class="so-crowd-grid">${marketBlock}${socialBlock}</div>
        ${synthesisBlock}
        ${noisyNote}
      </section>`;
  }

  function renderExternalMarketCheckSection(ev) {
    const pma = ev.externalMarketCheck;
    if (!pma) return "";

    const status = pma.lookupStatus || "not_found";
    const statusLabel = PMA_STATUS_LABELS[status] || PMA_STATUS_LABELS.not_found;

    if (status === "not_found" || status === "error") {
      return `
      <section class="so-pma-card">
        <div class="so-pma-head">
          <span class="so-pma-icon">${ICON_PMA}</span>
          <h2 class="so-pma-title">Данные с Polymarket Analytics</h2>
        </div>
        <p class="so-pma-empty">${escapeHtml(
          pma.summaryRu || "Событие не найдено на Polymarket Analytics."
        )}</p>
      </section>`;
    }

    const observations = (pma.observationsRu || []).slice(0, 3);
    const obsHtml = observations.length
      ? `<ul class="so-pma-obs">${observations
          .map((o) => `<li>${escapeHtml(o)}</li>`)
          .join("")}</ul>`
      : "";

    const summary = pma.summaryRu
      ? `<div class="so-pma-summary"><span>Итог:</span> ${escapeHtml(pma.summaryRu)}</div>`
      : "";

    const impact = PMA_IMPACT_LABELS[pma.forecastImpact] || PMA_IMPACT_LABELS.neutral;

    return `
      <section class="so-pma-card">
        <div class="so-pma-head">
          <span class="so-pma-icon">${ICON_PMA}</span>
          <h2 class="so-pma-title">Данные с Polymarket Analytics</h2>
        </div>
        <div class="so-pma-status">Статус: <strong>${escapeHtml(statusLabel)}</strong></div>
        ${obsHtml}
        ${summary}
        <div class="so-pma-impact">Влияние на прогноз: ${escapeHtml(impact)}</div>
      </section>`;
  }

  function renderWhaleCheckSection(ev) {
    const whale = ev.whaleCheck;
    if (!whale) return "";

    const lookup = whale.lookupStatus || "not_found";
    const noData =
      lookup === "not_found" ||
      lookup === "error" ||
      lookup === "not_supported" ||
      whale.mainVerdict === "no_data" ||
      whale.status === "no_data";

    if (noData) {
      return `
      <section class="so-whale-card">
        <div class="so-whale-head">
          <span class="so-whale-icon">${ICON_WHALE}</span>
          <div>
            <h2 class="so-whale-title">Крупные игроки</h2>
            <p class="so-whale-sub">Проверяем, куда идут крупные деньги по этому событию.</p>
          </div>
        </div>
        <p class="so-whale-empty">${escapeHtml(
          whale.summaryRu || "Данных по крупным игрокам нет."
        )}</p>
      </section>`;
    }

    const statusLabel = WHALE_LOOKUP_LABELS[lookup] || WHALE_LOOKUP_LABELS.found;
    const headline = whale.headlineRu || "Без явного сигнала";
    const highlight = whale.againstMarket ? " so-whale-headline--alert" : "";
    const skew = WHALE_SKEW_LABELS[whale.skewStrength] || "—";
    const impact = WHALE_IMPACT_LABELS[whale.forecastImpact] || WHALE_IMPACT_LABELS.neutral;

    return `
      <section class="so-whale-card">
        <div class="so-whale-head">
          <span class="so-whale-icon">${ICON_WHALE}</span>
          <div>
            <h2 class="so-whale-title">Крупные игроки</h2>
            <p class="so-whale-sub">Проверяем, куда идут крупные деньги по этому событию.</p>
          </div>
        </div>
        <div class="so-whale-status">Статус: <strong>${escapeHtml(statusLabel)}</strong></div>
        <div class="so-whale-headline${highlight}">${escapeHtml(headline)}</div>
        <div class="so-whale-metrics">
          <div class="so-whale-metric">
            <span>Крупный объём YES</span>
            <strong>${escapeHtml(formatUsd(whale.yesWhaleVolumeUsd))}</strong>
          </div>
          <div class="so-whale-metric">
            <span>Крупный объём NO</span>
            <strong>${escapeHtml(formatUsd(whale.noWhaleVolumeUsd))}</strong>
          </div>
          <div class="so-whale-metric">
            <span>Перекос</span>
            <strong>${escapeHtml(skew)}</strong>
          </div>
        </div>
        ${
          whale.explanationRu
            ? `<p class="so-whale-explain">${escapeHtml(whale.explanationRu)}</p>`
            : ""
        }
        <div class="so-whale-impact">Влияние на прогноз: ${escapeHtml(impact)}</div>
      </section>`;
  }

  function renderActionsSection(ev, opts) {
    opts = opts || {};
    const marketUrl = ev.marketUrl || opts.marketUrl || "https://polymarket.com";
    const shareUrl = opts.guestShareLink || `guest-event.html?id=${encodeURIComponent(ev.id)}`;
    const followHref = opts.proBotLink || "#";

    return `
      <section class="so-cta-bar">
        <div class="so-cta-left">
          <span class="so-cta-icon">${ICON_BULB}</span>
          <div class="so-cta-copy">
            <h2 class="so-cta-title">Что делать</h2>
            <p class="so-cta-desc">Наблюдать за событием и возвращаться к разбору при новых данных.</p>
            <p class="so-cta-desc">Не считать это гарантированным исходом.</p>
          </div>
        </div>
        <div class="so-cta-actions">
          <a class="so-btn so-btn-primary so-btn-cta" href="${escapeHtml(followHref)}" target="_blank" rel="noopener">
            <span class="so-btn-ico">${ICON_BELL}</span>
            Следить за событием
          </a>
          <a class="so-btn so-btn-outline-light so-btn-cta" href="${escapeHtml(marketUrl)}" target="_blank" rel="noopener">
            <span class="so-btn-ico">${ICON_MARKET}</span>
            Открыть на Polymarket
            <span class="so-btn-ico so-btn-ico--end">${ICON_EXT}</span>
          </a>
          <a class="so-btn so-btn-outline-light so-btn-cta" href="${escapeHtml(shareUrl)}">
            <span class="so-btn-ico">${ICON_SHARE}</span>
            Поделиться
          </a>
        </div>
      </section>`;
  }

  function renderTopBar(ev, opts) {
    return `
      <div class="so-topbar">
        <a href="events.html" class="so-back">← Назад к событиям</a>
      </div>`;
  }

  function renderChangesSection(ev) {
    const items = buildChanges(ev);
    const body = items.length
      ? `<ul class="so-list dash">${items.map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ul>`
      : `<div class="so-changes-empty">Пока существенных изменений нет</div>`;

    return `
      <section class="so-section">
        <h2 class="so-section-title">Изменения по событию</h2>
        <div class="so-changes-box">
          <div class="so-changes-sub">PolyPilot следит за событием</div>
          ${body}
        </div>
      </section>`;
  }

  function renderAdvancedSection(advancedHtml) {
    if (!advancedHtml) return "";
    return `
      <div class="so-advanced-wrap">
        <button type="button" class="so-advanced-btn" id="so-advanced-btn" aria-expanded="false">
          <span>Подробная аналитика</span>
          <span id="so-advanced-chevron">раскрыть ↓</span>
        </button>
        <div class="so-advanced-body" id="so-advanced-body">
          <p class="so-advanced-note">Технический слой для PRO: агенты, PIE, формулы. Основной вывод — в блоках выше.</p>
          ${advancedHtml}
        </div>
      </div>`;
  }

  function renderPage(ev, opts) {
    opts = opts || {};
    const sourceBanner = opts.sourceBanner || "";

    return `
      <div class="so-page">
        ${renderTopBar(ev, opts)}
        ${sourceBanner}
        ${renderVerdictSection(ev)}
        ${renderAnalysisDuo(ev)}
        ${renderCrowdPulseSection(ev)}
        ${renderExternalMarketCheckSection(ev)}
        ${renderWhaleCheckSection(ev)}
        ${renderCheckedSection(ev)}
        ${renderActionsSection(ev, opts)}
        ${renderChangesSection(ev)}
        ${renderAdvancedSection(opts.advancedHtml || "")}
        <div class="so-footer">
          <span>ID: ${escapeHtml(ev.id)}</span>
          <span>·</span>
          <span>Данные: Polymarket, новости, соцсети</span>
        </div>
      </div>`;
  }

  function wireAdvancedToggle(root) {
    const btn = (root || document).querySelector("#so-advanced-btn");
    const body = (root || document).querySelector("#so-advanced-body");
    const chev = (root || document).querySelector("#so-advanced-chevron");
    if (!btn || !body) return;
    btn.addEventListener("click", () => {
      const open = body.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      if (chev) chev.textContent = open ? "свернуть ↑" : "раскрыть ↓";
    });
  }

  global.PP_SIMPLE_OPEN = {
    renderPage,
    wireAdvancedToggle,
    buildReasons,
    buildRisks,
    buildChanges,
  };
})(window);
