/** Simple Events v1 — closed card renderer (shared). */
(function (global) {
  const EDGE_PP = 8;

  const CATEGORY_LABELS = {
    sports: "Спорт",
    entertainment: "Кино",
    crypto_simple: "Простое · крипто",
    tech_oneshot: "Tech",
    games: "Игры",
  };

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
    if (delta >= edge) return { label: "Рынок занижен", tone: "under" };
    if (delta <= -edge) return { label: "Рынок завышен", tone: "over" };
    return { label: "Совпадаем с рынком", tone: "match" };
  }

  function formatHorizonShort(ev) {
    if (ev.horizonShort) return ev.horizonShort;
    const resolveDate = ev.resolveDate || "";
    const parts = resolveDate.split("-");
    const daysMatch = String(ev.horizon || "").match(/(\d+)/);
    const days = daysMatch ? daysMatch[1] : null;
    if (parts.length === 3) {
      const day = parts[2];
      const month = parts[1];
      return days ? `Закрытие ${day}.${month} · ${days} дн.` : `Закрытие ${day}.${month}`;
    }
    return ev.horizon || "—";
  }

  function getCategoryLabel(ev) {
    if (ev.simpleCategoryLabel) return ev.simpleCategoryLabel;
    if (ev.simpleCategory && CATEGORY_LABELS[ev.simpleCategory]) {
      return CATEGORY_LABELS[ev.simpleCategory];
    }
    return ev.category || "Событие";
  }

  function pickReason(ev, verdict) {
    if (ev.simpleVerdictLine) return ev.simpleVerdictLine;
    const text = ev.verdictText || "";
    if (text.length > 24) {
      return text.length > 140 ? `${text.slice(0, 137)}…` : text;
    }
    const templates = {
      under: "PolyPilot видит исход выше, чем заложено на рынке.",
      over: "PolyPilot видит исход ниже, чем заложено на рынке.",
      match: "Наша оценка близка к рынку — детали в разборе.",
    };
    return templates[verdict.tone] || templates.match;
  }

  function renderSimpleClosedCard(ev, opts) {
    opts = opts || {};
    const market = clampPct(ev.marketOdds ?? 50);
    const pp = clampPct(ev.aiOdds ?? ev.confidence ?? 50);
    const verdict = ev.simpleVerdict
      ? { label: ev.simpleVerdict, tone: ev.simpleVerdictTone || "match" }
      : computeSimpleVerdict(market, pp);
    const reason = pickReason(ev, verdict);
    const href = opts.href || `event.html?id=${encodeURIComponent(ev.id)}`;
    const hotClass = ev.hot ? " is-hot" : "";

    return `
      <div class="event-card simple-v1${hotClass}" onclick="location.href='${href}'">
        <div class="sc-meta">
          <span class="sc-cat">${escapeHtml(getCategoryLabel(ev))}</span>
          <span class="sc-date">${escapeHtml(formatHorizonShort(ev))}</span>
        </div>
        <div class="sc-title">${escapeHtml(ev.title || "—")}</div>
        <div class="sc-compare">
          <div class="sc-bar-block">
            <label><span>Рынок</span><span class="val">${market}%</span></label>
            <div class="sc-bar"><i style="width:${market}%"></i></div>
          </div>
          <div class="sc-bar-block">
            <label><span>PolyPilot</span><span class="val pp">${pp}%</span></label>
            <div class="sc-bar pp"><i style="width:${pp}%"></i></div>
          </div>
        </div>
        <div class="sc-verdict sc-verdict--${verdict.tone}">
          <strong>${escapeHtml(verdict.label)}</strong>
          <p>${escapeHtml(reason)}</p>
        </div>
        <div class="sc-cta">Разбор →</div>
      </div>`;
  }

  global.PP_SIMPLE_CARD = {
    render: renderSimpleClosedCard,
    computeSimpleVerdict,
    formatHorizonShort,
    getCategoryLabel,
  };
})(window);
