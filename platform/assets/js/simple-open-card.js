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
        ${renderReasonsSection(ev)}
        ${renderRisksSection(ev)}
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
