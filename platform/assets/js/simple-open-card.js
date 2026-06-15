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

  const CHECK_ITEMS = [
    { label: "формулировка события", test: (ev) => !!ev.title },
    { label: "дата закрытия", test: (ev) => !!ev.resolveDate },
    { label: "текущая вероятность рынка", test: (ev) => ev.marketOdds != null },
    { label: "источники данных", test: (ev) => (ev.warRoom?.agents || []).length > 1 },
    { label: "похожие события", test: () => false },
    { label: "противоречия", test: (ev) => Math.abs((ev.aiOdds || 0) - (ev.marketOdds || 0)) >= 8 },
    { label: "риски", test: (ev) => !!(ev.riskTags?.length || ev.riskLevel) },
  ];

  const SOURCE_LIST =
    "новости · официальные источники · X / Reddit · Google Trends · YouTube / медиа · " +
    "похожие события · история Polymarket · внешние аналитические сервисы";

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

  function renderReasonsSection(ev) {
    const reasons = buildReasons(ev);
    return `
      <section class="so-section">
        <h2 class="so-section-title">Почему PolyPilot так думает</h2>
        <ol class="so-list num">
          ${reasons.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}
        </ol>
      </section>`;
  }

  function renderRisksSection(ev) {
    const risks = buildRisks(ev);
    return `
      <section class="so-section">
        <h2 class="so-section-title">Что может пойти не так</h2>
        <ul class="so-list dash">
          ${risks.map((r) => `<li>${escapeHtml(r)}</li>`).join("")}
        </ul>
      </section>`;
  }

  function renderCheckedSection(ev) {
    const checks = CHECK_ITEMS.map((item) => ({
      label: item.label,
      done: item.test(ev),
    }));
    return `
      <section class="so-section">
        <h2 class="so-section-title">Что мы проверили</h2>
        <div class="so-check-grid">
          ${checks
            .map(
              (c) => `
            <div class="so-check-item ${c.done ? "done" : ""}">
              <span class="so-check-mark">${c.done ? "✓" : "·"}</span>
              ${escapeHtml(c.label)}
            </div>`
            )
            .join("")}
        </div>
        <div class="so-sources">
          <strong>Источники</strong>
          ${escapeHtml(SOURCE_LIST)}
        </div>
      </section>`;
  }

  function renderActionsSection(ev, opts) {
    opts = opts || {};
    const marketUrl = ev.marketUrl || opts.marketUrl || "https://polymarket.com";

    return `
      <section class="so-section">
        <h2 class="so-section-title">Что делать</h2>
        <div class="so-actions">
          <a class="so-btn so-btn-ghost" href="${escapeHtml(marketUrl)}" target="_blank" rel="noopener">Открыть на Polymarket</a>
        </div>
        <p class="so-disclaimer">Не финансовый совет. PolyPilot показывает расхождение с рынком — решение за вами.</p>
      </section>`;
  }

  function renderTopBar(ev, opts) {
    opts = opts || {};
    const shareUrl = opts.guestShareLink || `guest-event.html?id=${encodeURIComponent(ev.id)}`;
    const followHref = opts.proBotLink || "#";

    return `
      <div class="so-topbar">
        <a href="events.html" class="so-back">← Назад к событиям</a>
        <div class="so-topbar-actions">
          <a class="so-btn so-btn-primary so-btn-sm" href="${escapeHtml(followHref)}" target="_blank" rel="noopener">Следить</a>
          <a class="so-btn so-btn-outline so-btn-sm" href="${escapeHtml(shareUrl)}">Поделиться</a>
        </div>
      </div>`;
  }

  function getCategoryCounts(allEvents) {
    const map = {};
    (allEvents || []).forEach((item) => {
      const key = item.categoryTag || item.simpleCategory || "other";
      const label = CARD.getCategoryLabel ? CARD.getCategoryLabel(item) : item.category || "Другое";
      if (!map[key]) map[key] = { key, label, count: 0 };
      map[key].count += 1;
    });
    return Object.values(map).sort((a, b) => b.count - a.count);
  }

  function renderMiniEventLink(item, currentId) {
    if (!item || item.id === currentId) return "";
    const market = clampPct(item.marketOdds ?? 50);
    const pp = clampPct(item.aiOdds ?? item.confidence ?? 50);
    const title = item.title || "—";
    const short = title.length > 52 ? `${title.slice(0, 49)}…` : title;
    return `
      <a class="so-mini-ev" href="event.html?id=${encodeURIComponent(item.id)}">
        <span class="so-mini-title">${escapeHtml(short)}</span>
        <span class="so-mini-vs">${market}% · PP ${pp}%</span>
      </a>`;
  }

  function renderLeftRail(ev, allEvents) {
    const siblings = (allEvents || [])
      .filter((item) => item.id !== ev.id)
      .sort((a, b) => (b.edgeScore || 0) - (a.edgeScore || 0))
      .slice(0, 4);
    const cats = getCategoryCounts(allEvents);

    return `
      <div class="so-widget">
        <div class="so-widget-title">Ещё события</div>
        <div class="so-mini-list">
          ${siblings.length ? siblings.map((item) => renderMiniEventLink(item, ev.id)).join("") : '<div class="so-empty-note">Других live-событий пока нет</div>'}
        </div>
      </div>
      <div class="so-widget">
        <div class="so-widget-title">Категории</div>
        <div class="so-cat-links">
          <a class="so-cat-link" href="events.html">Все <span>${(allEvents || []).length}</span></a>
          ${cats
            .map(
              (c) =>
                `<a class="so-cat-link" href="events.html">${escapeHtml(c.label)} <span>${c.count}</span></a>`
            )
            .join("")}
        </div>
      </div>
      <div class="so-widget so-widget-legend">
        <div class="so-widget-title">Как читать прогнозы</div>
        <ul class="so-legend">
          <li><strong>Рынок</strong> — текущая цена на Polymarket</li>
          <li><strong>PolyPilot</strong> — наша оценка по данным</li>
          <li><strong>Занижен / завышен</strong> — расхождение ≥ 8 п.п.</li>
        </ul>
      </div>`;
  }

  function renderSparkline(ev) {
    const open = clampPct(ev.proofTrack?.marketOddsAtOpen ?? ev.marketOdds ?? 50);
    const now = clampPct(ev.marketOdds ?? open);
    const points = [];
    for (let i = 0; i < 8; i += 1) {
      points.push(Math.round(open + ((now - open) * i) / 7));
    }
    const max = Math.max(...points, 1);
    return points
      .map((p) => `<i style="height:${Math.max(12, Math.round((p / max) * 100))}%"></i>`)
      .join("");
  }

  function renderChangesWidget(ev) {
    const items = buildChanges(ev);
    const body = items.length
      ? `<ul class="so-rail-list">${items.map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ul>`
      : `<div class="so-changes-empty">Пока существенных изменений нет</div>`;

    return `
      <div class="so-widget">
        <div class="so-widget-title">Изменения</div>
        <div class="so-sparkline" aria-hidden="true">${renderSparkline(ev)}</div>
        <div class="so-changes-sub">PolyPilot следит за событием</div>
        ${body}
      </div>`;
  }

  function renderTrackRecordWidget(ev) {
    const cat = CARD.getCategoryLabel ? CARD.getCategoryLabel(ev) : ev.category || "категории";
    return `
      <div class="so-widget">
        <div class="so-widget-head">
          <span class="so-widget-title">Точность PolyPilot</span>
          <span class="so-badge-soon">скоро</span>
        </div>
        <div class="so-track-row">
          <div class="so-donut" style="--pct:67" aria-hidden="true"><span>67%</span></div>
          <p class="so-track-note">Демо-метрика по ${escapeHtml(cat.toLowerCase())}. Реальная история точности появится после первых закрытых событий.</p>
        </div>
      </div>`;
  }

  function renderSimilarWidget(ev, allEvents) {
    const similar = (allEvents || [])
      .filter((item) => item.id !== ev.id && (item.categoryTag === ev.categoryTag || item.simpleCategory === ev.simpleCategory))
      .slice(0, 3);

    const demo = [
      { title: "Ecuador dollarizes by 2026?", market: 45, pp: 38, status: "пример" },
      { title: "El Salvador BTC reserve by end 2025?", market: 12, pp: 8, status: "пример" },
    ];

    const liveHtml = similar
      .map(
        (item) => `
        <a class="so-similar" href="event.html?id=${encodeURIComponent(item.id)}">
          <span class="so-similar-title">${escapeHtml(item.title)}</span>
          <span class="so-similar-meta">${clampPct(item.marketOdds)}% · PP ${clampPct(item.aiOdds ?? item.confidence)}% · открыто</span>
        </a>`
      )
      .join("");

    const demoHtml = demo
      .map(
        (item) => `
        <div class="so-similar so-similar--demo">
          <span class="so-similar-title">${escapeHtml(item.title)}</span>
          <span class="so-similar-meta">${item.market}% · PP ${item.pp}% · ${item.status}</span>
        </div>`
      )
      .join("");

    return `
      <div class="so-widget">
        <div class="so-widget-title">Похожие события</div>
        <div class="so-similar-list">${liveHtml}${demoHtml}</div>
      </div>`;
  }

  function renderRightRail(ev, allEvents) {
    return `${renderChangesWidget(ev)}${renderTrackRecordWidget(ev)}${renderSimilarWidget(ev, allEvents)}`;
  }

  function renderMainColumn(ev, opts) {
    return `
      ${renderVerdictSection(ev)}
      <div class="so-duo">
        ${renderReasonsSection(ev)}
        ${renderRisksSection(ev)}
      </div>
      ${renderCheckedSection(ev)}
      ${renderActionsSection(ev, opts)}
      ${renderAdvancedSection(opts.advancedHtml || "")}
      <div class="so-footer">
        <span>ID: ${escapeHtml(ev.id)}</span>
        <span>·</span>
        <span>Данные: Polymarket, новости, соцсети</span>
      </div>`;
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
    const allEvents = opts.allEvents || [];

    return `
      <div class="so-page">
        ${renderTopBar(ev, opts)}
        ${sourceBanner}
        <div class="so-layout">
          <aside class="so-rail so-rail--left">${renderLeftRail(ev, allEvents)}</aside>
          <div class="so-main">${renderMainColumn(ev, opts)}</div>
          <aside class="so-rail so-rail--right">${renderRightRail(ev, allEvents)}</aside>
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
    renderLeftRail,
    renderRightRail,
    buildReasons,
    buildRisks,
    buildChanges,
  };
})(window);
