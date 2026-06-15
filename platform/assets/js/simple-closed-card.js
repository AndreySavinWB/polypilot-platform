/** Simple Events v1 — closed card renderer (shared). */
(function (global) {
  const EDGE_PP = 8;
  const SEGMENTS = 20;

  const MONTHS_RU = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
  ];

  const CATEGORY_LABELS = {
    sports: "Спорт",
    entertainment: "Кино",
    crypto_simple: "Крипто",
    tech_oneshot: "Tech",
    games: "Игры",
  };

  const ICON_GLOBE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>`;
  const ICON_TREND = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="4,16 9,11 13,15 20,6"/><polyline points="15,6 20,6 20,11"/></svg>`;
  const ICON_SIGNAL = `<svg viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="10" width="3" height="5" rx="0.5" opacity="0.45"/><rect x="6" y="7" width="3" height="8" rx="0.5" opacity="0.7"/><rect x="11" y="4" width="3" height="11" rx="0.5"/></svg>`;

  function clampPct(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return 0;
    return Math.max(0, Math.min(100, Math.round(n)));
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function computeSimpleVerdict(market, pp, threshold) {
    const edge = threshold == null ? EDGE_PP : threshold;
    const m = clampPct(market);
    const p = clampPct(pp);
    const delta = p - m;
    if (delta >= edge) return { label: "Рынок занижен", tone: "under", delta };
    if (delta <= -edge) return { label: "Рынок завышен", tone: "over", delta };
    return { label: "Совпадаем с рынком", tone: "match", delta };
  }

  function formatHorizonLong(ev) {
    const resolveDate = ev.resolveDate || "";
    const parts = resolveDate.split("-");
    const daysMatch = String(ev.horizon || "").match(/(\d+)/);
    const days = daysMatch ? daysMatch[1] : null;
    if (parts.length === 3) {
      const day = parseInt(parts[2], 10);
      const month = MONTHS_RU[parseInt(parts[1], 10) - 1] || parts[1];
      const year = parts[0];
      const base = `Закрытие ${day} ${month} ${year}`;
      return days ? `${base} • ${days} дней` : base;
    }
    return ev.horizon || "—";
  }

  function formatHorizonShort(ev) {
    if (ev.horizonShort) return ev.horizonShort;
    const long = formatHorizonLong(ev);
    const m = long.match(/Закрытие (\d+\.\d+)/);
    if (m) return `Закрытие ${m[1]}`;
    const parts = (ev.resolveDate || "").split("-");
    const daysMatch = String(ev.horizon || "").match(/(\d+)/);
    const days = daysMatch ? daysMatch[1] : null;
    if (parts.length === 3) {
      return days ? `Закрытие ${parts[2]}.${parts[1]} · ${days} дн.` : `Закрытие ${parts[2]}.${parts[1]}`;
    }
    return ev.horizon || "—";
  }

  function getCategoryLabel(ev) {
    if (ev.category) return ev.category;
    if (ev.simpleCategoryLabel) return ev.simpleCategoryLabel;
    if (ev.simpleCategory && CATEGORY_LABELS[ev.simpleCategory]) {
      return CATEGORY_LABELS[ev.simpleCategory];
    }
    return "Событие";
  }

  function getVerdictHeadline(verdict) {
    const d = Math.abs(verdict.delta || 0);
    if (verdict.tone === "under") {
      return d >= 25 ? "Рынок сильно занижен" : "Рынок занижен";
    }
    if (verdict.tone === "over") {
      return d >= 25 ? "Рынок сильно завышен" : "Рынок завышен";
    }
    return "Совпадаем с рынком";
  }

  function pickReason(ev, verdict) {
    if (ev.simpleVerdictLine) return ev.simpleVerdictLine;
    const text = ev.verdictText || "";
    if (text.length > 40 && text.length <= 160) return text;
    if (text.length > 160) return `${text.slice(0, 157)}…`;

    const templates = {
      under: "Рынок почти не закладывает исход — PolyPilot видит сильное расхождение.",
      over: "Рынок переоценивает вероятность — PolyPilot видит завышение.",
      match: "Оценки близки — детали и аргументы в полном разборе.",
    };
    return templates[verdict.tone] || templates.match;
  }

  function getConfidenceLabel(ev) {
    const risk = ev.riskLevel || "medium";
    const map = { low: "низкая", medium: "средняя", high: "высокая" };
    if (map[risk]) return map[risk];
    const conf = clampPct(ev.confidence ?? ev.aiOdds ?? 50);
    if (conf >= 72) return "высокая";
    if (conf >= 48) return "средняя";
    return "низкая";
  }

  function renderSegments(pct, variant) {
    const filled = Math.round((clampPct(pct) / 100) * SEGMENTS);
    let html = `<div class="sc-segments sc-segments--${variant}">`;
    for (let i = 0; i < SEGMENTS; i += 1) {
      html += `<i class="${i < filled ? "on" : ""}"></i>`;
    }
    html += "</div>";
    return html;
  }

  function renderSimpleClosedCard(ev, opts) {
    opts = opts || {};
    const market = clampPct(ev.marketOdds ?? 50);
    const pp = clampPct(ev.aiOdds ?? ev.confidence ?? 50);
    const verdict = ev.simpleVerdict
      ? {
          label: ev.simpleVerdict,
          tone: ev.simpleVerdictTone || "match",
          delta: pp - market,
        }
      : computeSimpleVerdict(market, pp);
    const headline = getVerdictHeadline(verdict);
    const reason = pickReason(ev, verdict);
    const href = opts.href || `event.html?id=${encodeURIComponent(ev.id)}`;
    const watchers = ev.watchers || "—";
    const confidence = getConfidenceLabel(ev);

    return `
      <div class="event-card simple-v1" onclick="location.href='${href}'" role="link" tabindex="0">
        <div class="sc-head">
          <div class="sc-head-left">
            <span class="sc-cat-icon">${ICON_GLOBE}</span>
            <span class="sc-cat-label">${escapeHtml(getCategoryLabel(ev))}</span>
          </div>
          <div class="sc-head-date">${escapeHtml(formatHorizonLong(ev))}</div>
          <div class="sc-head-views">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
            ${escapeHtml(watchers)}
          </div>
        </div>

        <div class="sc-hero">
          <div class="sc-title">${escapeHtml(ev.title || "—")}</div>
          <div class="sc-sub">Что думает рынок и что видит PolyPilot</div>
        </div>

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
        </div>

        <div class="sc-insight sc-insight--${verdict.tone}">
          <div class="sc-insight-ico">${ICON_TREND}</div>
          <div class="sc-insight-body">
            <strong>${escapeHtml(headline)}</strong>
            <p>${escapeHtml(reason)}</p>
          </div>
          <div class="sc-insight-badge">
            ${ICON_SIGNAL}
            <span>Уверенность: ${escapeHtml(confidence)}</span>
          </div>
        </div>
      </div>`;
  }

  global.PP_SIMPLE_CARD = {
    render: renderSimpleClosedCard,
    computeSimpleVerdict,
    formatHorizonShort,
    formatHorizonLong,
    getCategoryLabel,
  };
})(window);
