/**
 * PIE API client — загрузка pipelinePackage с backend и рендер в event.html.
 *
 * Локально:
 *   window.PP_CONFIG = { apiBase: 'http://127.0.0.1:8787', usePieApi: true };
 */
(function (global) {
  'use strict';

  var EVENT_TYPE_RU = {
    regulatory: 'Регуляторика',
    elections: 'Выборы',
    crypto: 'Крипто',
    economics: 'Экономика',
    geopolitics: 'Геополитика',
    legal: 'Судебные',
    sports: 'Спорт',
    corporate: 'Корпоративные',
    other: 'Другое',
  };

  var WHALE_RU = {
    accumulation_yes: 'накопление YES',
    accumulation_no: 'накопление NO',
    none: 'нет сигнала',
    unknown: 'неизвестно',
  };

  var MONEY_DIR_RU = {
    yes: 'в сторону YES',
    no: 'в сторону NO',
    neutral: 'нейтрально',
    unknown: 'неизвестно',
  };

  function cfg() {
    return global.PP_CONFIG || {};
  }

  function apiBase() {
    var base = (cfg().apiBase || '').trim();
    return base.replace(/\/$/, '');
  }

  function shouldUseApi() {
    return !!apiBase() && cfg().usePieApi === true;
  }

  function parseMoneyString(raw) {
    if (raw == null || raw === '') return null;
    if (typeof raw === 'number' && !isNaN(raw)) return raw;
    var s = String(raw).trim().replace(/[$,\s]/g, '');
    if (!s) return null;
    var mult = 1;
    var last = s.slice(-1).toUpperCase();
    if (last === 'K') { mult = 1e3; s = s.slice(0, -1); }
    else if (last === 'M') { mult = 1e6; s = s.slice(0, -1); }
    else if (last === 'B') { mult = 1e9; s = s.slice(0, -1); }
    var n = parseFloat(s);
    return isNaN(n) ? null : Math.round(n * mult);
  }

  function toIsoEndDate(resolveDate) {
    if (!resolveDate) return null;
    var d = String(resolveDate).trim();
    if (!d) return null;
    if (d.indexOf('T') >= 0) return d;
    return d + 'T00:00:00Z';
  }

  function marketProbFromOdds(odds) {
    if (odds == null || odds === '') return null;
    var n = Number(odds);
    if (isNaN(n)) return null;
    if (n > 1) return Math.round(n) / 100;
    return n;
  }

  function polymarketId(storeEvent) {
    if (storeEvent.polymarketId) return String(storeEvent.polymarketId);
    var id = String(storeEvent.id || '');
    if (id.indexOf('live-') === 0) return id.slice(5);
    return id;
  }

  /** Оценка ликвидности для Priority Gate, если в карточке нет liquidity (events-live.js). */
  function estimateLiquidity(storeEvent, volume) {
    if (storeEvent && storeEvent.liquidity != null && storeEvent.liquidity !== '') {
      var direct = typeof storeEvent.liquidity === 'number'
        ? storeEvent.liquidity
        : parseMoneyString(storeEvent.liquidity);
      if (direct != null && direct > 0) return direct;
    }
    if (volume != null && volume > 0) {
      return Math.max(Math.round(volume * 0.06), 6000);
    }
    return null;
  }

  /** Собрать rawEvent для POST /api/pie/process из карточки events-store. */
  function mapStoreEventToPieInput(storeEvent) {
    if (!storeEvent) return null;

    var prob = marketProbFromOdds(storeEvent.marketOdds);
    var yes = prob != null ? prob.toFixed(4) : '0.50';
    var no = prob != null ? (1 - prob).toFixed(4) : '0.50';
    var title = storeEvent.titleEn || storeEvent.title || '';
    var volume = parseMoneyString(storeEvent.volumeTotal) || parseMoneyString(storeEvent.volume);
    var volume24 = parseMoneyString(storeEvent.volume24h) || parseMoneyString(storeEvent.volume24hr);
    var liquidity = estimateLiquidity(storeEvent, volume);
    var description = storeEvent.summary || storeEvent.verdictText || storeEvent.description || title;

    return {
      id: polymarketId(storeEvent),
      slug: storeEvent.slug || null,
      title: title,
      description: description,
      category: storeEvent.category || null,
      volume: volume,
      volume24hr: volume24,
      liquidity: liquidity,
      startDate: storeEvent.startDate || null,
      endDate: toIsoEndDate(storeEvent.resolveDate || storeEvent.endDate),
      marketsCount: 1,
      markets: [{
        question: title,
        outcomePrices: JSON.stringify([yes, no]),
        volume: volume,
        liquidity: liquidity,
      }],
      source: 'polymarket_gamma',
      sourceUrl: storeEvent.marketUrl || null,
    };
  }

  function buildMockPiePackage(storeEvent) {
    var marketProb = marketProbFromOdds(storeEvent.marketOdds);
    var ppProb = marketProbFromOdds(storeEvent.aiOdds) || marketProb;
    var edge = storeEvent.edgeScore != null
      ? Number(storeEvent.edgeScore)
      : (ppProb != null && marketProb != null ? Math.round((ppProb - marketProb) * 1000) / 10 : null);

    var strategyPrimary = 'education';
    if (storeEvent.categoryTag === 'macro' || storeEvent.categoryTag === 'crypto') {
      strategyPrimary = 'whale_copy';
    }

    return {
      eventId: polymarketId(storeEvent),
      pieVersion: 'mock_fallback',
      pipelineStatus: 'mock_fallback',
      source: 'mock',
      normalizedEvent: {
        titleRu: storeEvent.title || storeEvent.titleEn,
        resolutionCriteria: storeEvent.summary || '',
        horizonDays: null,
        decisionMaker: 'Polymarket / UMA',
        normalizationStatus: 'ok',
        marketSnapshot: {
          marketProb: marketProb,
          volume: parseMoneyString(storeEvent.volumeTotal),
          liquidity: null,
        },
      },
      eventClassification: {
        eventType: storeEvent.categoryTag || 'other',
        subType: 'other',
        classifierConfidence: 0.5,
        analysisProfile: 'general',
      },
      marketIntelligence: null,
      marketStructure: null,
      evidence: null,
      probability: marketProb != null ? {
        marketProb: marketProb,
        ppProb: ppProb,
        edgePp: edge,
        confidence: (storeEvent.confidence || 50) / 100,
        status: 'preliminary',
        scoringMode: 'mock',
        components: { missingComponents: ['external_evidence', 'historical_analogs'] },
      } : {
        status: 'insufficient_data',
        marketProb: null,
        ppProb: null,
        edgePp: null,
        confidence: 0,
        scoringMode: 'mock',
        components: { missingComponents: ['market_base'] },
      },
      strategyIntelligence: marketProb != null ? {
        version: 'strategy_intelligence_v1_0',
        primaryStrategy: strategyPrimary,
        strategyFits: [{
          strategy: strategyPrimary,
          fitScore: 45,
          status: 'watchlist',
          reason: 'Демонстрационный вывод на основе данных карточки события.',
          requiredChecks: ['liquidity', 'spread'],
          invalidation: ['thin_market', 'unclear_resolution'],
        }],
        queues: ['education_queue'],
        verdictMode: 'research',
        userWhySelected: 'Событие показано как учебный кейс (mock fallback без backend).',
        scoringMode: 'rules_v0',
      } : null,
      strategyVerdict: marketProb != null ? {
        primaryStrategy: strategyPrimary,
        mode: 'research',
        summary: 'Демонстрационный вывод: данные карточки без live PIE backend.',
        marketProbText: Math.round(marketProb * 100) + '%',
        ppProbText: ppProb != null ? Math.round(ppProb * 100) + '%' : 'unknown',
        edgeText: edge != null ? ((edge >= 0 ? '+' : '') + edge + 'pp') : 'unknown',
        confidence: (storeEvent.confidence || 50) / 100,
        riskLevel: storeEvent.riskLevel || 'medium',
        requiredChecks: ['liquidity', 'spread'],
        invalidation: ['thin_market'],
        disclaimer: 'Аналитика PolyPilot не является финансовым советом и не обещает прибыль.',
        scoringMode: 'rules_v0',
      } : null,
    };
  }

  function fetchWithTimeout(url, options, timeoutMs) {
    return new Promise(function (resolve, reject) {
      var timer = setTimeout(function () {
        reject(new Error('PIE API timeout'));
      }, timeoutMs);
      fetch(url, options)
        .then(function (res) {
          clearTimeout(timer);
          resolve(res);
        })
        .catch(function (err) {
          clearTimeout(timer);
          reject(err);
        });
    });
  }

  /**
   * POST /api/pie/process
   * @returns {{ ok, package, error, partial, source: 'api'|'mock' }}
   */
  async function loadPiePackage(storeEvent, options) {
    options = options || {};
    var timeoutMs = options.timeoutMs || cfg().pieApiTimeoutMs || 15000;

    if (!shouldUseApi()) {
      return {
        ok: true,
        package: buildMockPiePackage(storeEvent),
        error: null,
        partial: true,
        source: 'mock',
      };
    }

    var eventInput = mapStoreEventToPieInput(storeEvent);
    if (!eventInput || !eventInput.id) {
      return {
        ok: false,
        package: buildMockPiePackage(storeEvent),
        error: 'Invalid event input for PIE',
        partial: true,
        source: 'mock',
      };
    }

    try {
      var res = await fetchWithTimeout(
        apiBase() + '/api/pie/process',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ event: eventInput }),
        },
        timeoutMs
      );

      if (!res.ok) {
        var errText = await res.text();
        throw new Error('PIE API ' + res.status + ': ' + errText.slice(0, 200));
      }

      var pkg = await res.json();
      var partial = pkg.pipelineStatus === 'stopped_priority'
        || pkg.pipelineStatus === 'branch_resolution_unclear'
        || (pkg.evidence && pkg.evidence.collectionStatus === 'partial');

      if (cfg().pieDebug !== false && typeof console !== 'undefined') {
        console.info('[PIE]', pkg.pieVersion, pkg.pipelineStatus, pkg);
      }

      return { ok: true, package: pkg, error: null, partial: !!partial, source: 'api' };
    } catch (err) {
      if (typeof console !== 'undefined') {
        console.warn('[PIE] API fallback to mock:', err.message || err);
      }
      return {
        ok: false,
        package: buildMockPiePackage(storeEvent),
        error: err.message || String(err),
        partial: true,
        source: 'mock',
      };
    }
  }

  var STRATEGY_RU = {
    whale_copy: 'Копирование китов',
    news_lag: 'News Lag',
    education: 'Обучение',
  };

  var STRATEGY_STATUS_RU = {
    candidate: 'Кандидат',
    watchlist: 'Наблюдение',
    not_a_fit: 'Не подходит',
  };

  var CHECK_RU = {
    liquidity: 'Ликвидность',
    spread: 'Спред',
    entry_timing: 'Тайминг входа',
    wallet_quality: 'Качество кошелька',
    late_move: 'Позднее движение',
    thin_market: 'Тонкий рынок',
    unclear_resolution: 'Неясный резолв',
    hedge_flow: 'Хедж-поток',
    stale_news: 'Устаревшая новость',
    weak_source: 'Слабый источник',
    already_priced_in: 'Уже в цене',
    too_complex: 'Слишком сложно',
    no_context: 'Нет контекста',
    source_freshness: 'Свежесть источника',
    catalyst_link: 'Связь с исходом',
    simple_resolution: 'Понятный резолв',
    clear_title: 'Понятная формулировка',
    teachable_contradiction: 'Учебное противоречие',
    source_quality: 'Качество источника',
    freshness: 'Свежесть данных',
    market_reaction: 'Реакция рынка',
    resolution_link: 'Связь с резолвом',
  };

  var RISK_LEVEL_RU = {
    low: 'низкий',
    medium: 'средний',
    high: 'высокий',
    unknown: 'неизвестно',
  };

  var TIER_RU = {
    low: 'низкая',
    medium: 'средняя',
    high: 'высокая',
    unknown: 'неизвестно',
  };

  var RELIABILITY_RU = {
    low: 'низкая',
    moderate: 'умеренная',
    high: 'высокая',
    unknown: 'неизвестно',
  };

  var PROB_STATUS_RU = {
    ok: 'полные данные',
    preliminary: 'предварительно',
    insufficient_data: 'недостаточно данных',
  };

  var VOL_ANOM_RU = {
    none: 'нет',
    moderate: 'умеренная',
    high: 'высокая',
    unknown: 'неизвестно',
  };

  var VOL_SIGNAL_RU = {
    rising: 'растёт',
    falling: 'падает',
    flat: 'стабильно',
    unknown: 'неизвестно',
  };

  var EV_STATUS_RU = {
    empty: 'пусто',
    partial: 'частично',
    ok: 'полные',
  };

  function pct01(val) {
    if (val == null || val === '') return null;
    var n = Number(val);
    if (isNaN(n)) return null;
    return n <= 1 ? Math.round(n * 100) : Math.round(n);
  }

  function fmtPct01(val, fallback) {
    var p = pct01(val);
    return p != null ? p + '%' : (fallback || '—');
  }

  function fmtEdgePp(edge, locked) {
    if (locked) return 'PRO';
    if (edge == null || edge === '') return '—';
    var e = Number(edge);
    if (isNaN(e)) return '—';
    return (e >= 0 ? '+' : '−') + Math.abs(Math.round(e * 10) / 10) + ' пп';
  }

  function fmtPpProb(prob, locked) {
    if (locked) return 'PRO';
    if (!prob || prob.status === 'insufficient_data' || prob.ppProb == null) {
      return 'Недостаточно данных';
    }
    return pct01(prob.ppProb) + '%';
  }

  function riskClass(level) {
    if (!level || level === 'unknown') return 'pie-risk-unknown';
    if (level === 'low') return 'pie-risk-low';
    if (level === 'medium') return 'pie-risk-medium';
    if (level === 'high') return 'pie-risk-high';
    return 'pie-risk-unknown';
  }

  function labelRu(map, key, fallback) {
    if (key == null || key === '') return fallback || '—';
    return map[key] || String(key).replace(/_/g, ' ');
  }

  function setText(root, selector, text) {
    var el = root.querySelector(selector);
    if (el) el.textContent = text;
  }

  function setHtml(root, selector, html) {
    var el = root.querySelector(selector);
    if (el) el.innerHTML = html;
  }

  function kvRow(label, value, valueClass) {
    return '<div class="pie-kv"><span class="pie-kv-lbl">' + label + '</span>'
      + '<span class="pie-kv-val' + (valueClass ? ' ' + valueClass : '') + '">' + value + '</span></div>';
  }

  function applyLocked(root, selector, locked) {
    var wrap = root.querySelector(selector);
    if (wrap) wrap.classList.toggle('is-locked', !!locked);
  }

  function sourceSubLabel(meta, prob, pkg) {
    if (meta.source === 'mock') {
      return 'Демонстрационные данные (mock fallback)';
    }
    var partial = meta.partial || prob.status === 'preliminary'
      || (pkg.evidence && pkg.evidence.collectionStatus === 'partial');
    if (partial) {
      return '8 слоёв анализа · rules_v0 · предварительно';
    }
    return '8 слоёв анализа · live backend';
  }

  function topFit(si, primary) {
    var fits = si.strategyFits || [];
    for (var i = 0; i < fits.length; i++) {
      if (fits[i].strategy === primary) return fits[i];
    }
    return fits[0] || {};
  }

  function priorityBlockReason(pkg) {
    if (!pkg || pkg.pipelineStatus !== 'stopped_priority') return null;
    var pr = pkg.priority || {};
    if (pr.reason) return pr.reason;
    var failed = pr.gates && pr.gates.failed;
    if (failed && failed.length) return failed.join(' · ');
    return 'Событие не прошло Priority Gate — полный PIE не запущен.';
  }

  function renderStrategyBadge(root, si, pkg) {
    var blocked = priorityBlockReason(pkg);
    if (blocked) {
      setText(root, '#pie-strategy-name', 'Priority Gate: анализ не запущен');
      setText(root, '#pie-strategy-why', blocked);
      var blockedStatus = root.querySelector('#pie-strategy-status');
      if (blockedStatus) {
        blockedStatus.textContent = 'Отклонено';
        blockedStatus.className = 'pie-strategy-status not_a_fit';
      }
      return;
    }
    if (!si || !si.primaryStrategy) {
      setText(root, '#pie-strategy-name', 'Стратегия не определена');
      setText(root, '#pie-strategy-why', 'Данные Strategy Intelligence Layer пока недоступны.');
      setText(root, '#pie-strategy-status', '—');
      return;
    }
    var primary = si.primaryStrategy;
    var fit = topFit(si, primary);
    var status = fit.status || 'watchlist';

    setText(root, '#pie-strategy-name', labelRu(STRATEGY_RU, primary, primary));
    setText(root, '#pie-strategy-why', si.userWhySelected || fit.reason || '—');

    var statusEl = root.querySelector('#pie-strategy-status');
    if (statusEl) {
      statusEl.textContent = labelRu(STRATEGY_STATUS_RU, status, status);
      statusEl.className = 'pie-strategy-status ' + status;
    }
  }

  function renderStrategyVerdict(root, sv, canSeeEdge) {
    if (!sv) {
      setText(root, '#pie-verdict-summary', 'Вывод по стратегии появится после полного PIE-анализа.');
      setHtml(root, '#pie-verdict-metrics', '');
      setHtml(root, '#pie-verdict-checks', '<li>—</li>');
      setHtml(root, '#pie-verdict-invalidation', '<li>—</li>');
      setText(root, '#pie-verdict-disclaimer', '');
      return;
    }

    setText(root, '#pie-verdict-summary', sv.summary || '—');

    var metrics = [];
    if (sv.marketProbText) {
      metrics.push('<span class="pie-verdict-metric">Рынок: <strong>' + sv.marketProbText + '</strong></span>');
    }
    if (canSeeEdge) {
      if (sv.ppProbText) metrics.push('<span class="pie-verdict-metric">PP AI: <strong>' + sv.ppProbText + '</strong></span>');
      if (sv.edgeText && sv.edgeText !== 'unknown') {
        metrics.push('<span class="pie-verdict-metric">Edge: <strong>' + sv.edgeText + '</strong></span>');
      }
    } else {
      metrics.push('<span class="pie-verdict-metric">PP AI / Edge: <strong>PRO</strong></span>');
    }
    if (sv.riskLevel) {
      metrics.push('<span class="pie-verdict-metric">Риск: <strong>' + labelRu(RISK_LEVEL_RU, sv.riskLevel) + '</strong></span>');
    }
    setHtml(root, '#pie-verdict-metrics', metrics.join(''));

    var checks = sv.requiredChecks || [];
    setHtml(root, '#pie-verdict-checks', checks.length
      ? checks.map(function (c) { return '<li>' + labelRu(CHECK_RU, c, c) + '</li>'; }).join('')
      : '<li>Дополнительных проверок не требуется</li>');

    var invalid = sv.invalidation || [];
    setHtml(root, '#pie-verdict-invalidation', invalid.length
      ? invalid.map(function (c) { return '<li>' + labelRu(CHECK_RU, c, c) + '</li>'; }).join('')
      : '<li>Явных условий инвалидации нет</li>');

    setText(root, '#pie-verdict-disclaimer', sv.disclaimer || '');
  }

  function buildComponentsHtml(prob) {
    if (!prob || prob.status === 'insufficient_data') {
      return '<div class="ev-pie-no-flags">Недостаточно данных для разбивки вероятности</div>';
    }
    var comps = prob.components || {};
    var rows = [];
    var idx = 1;

    if (comps.marketBase) {
      var mb = comps.marketBase;
      rows.push({
        num: idx++, name: 'Рыночная база',
        desc: 'marketProb × structureMult ' + (mb.structureMult != null ? mb.structureMult : ''),
        weighted: Math.round((mb.centeredValue || 0) * 100),
        color: '#a78bfa',
      });
    }
    if (comps.whaleSignal && comps.whaleSignal.value != null) {
      rows.push({
        num: idx++, name: 'Сигнал китов',
        desc: labelRu(WHALE_RU, comps.whaleSignal.signal, comps.whaleSignal.signal || ''),
        weighted: Math.round((comps.whaleSignal.value || 0) * 100),
        color: '#22D3A6',
      });
    }
    if (comps.evidenceSignal && comps.evidenceSignal.value != null) {
      rows.push({
        num: idx++, name: 'Доказательства',
        desc: comps.evidenceSignal.status || comps.evidenceSignal.reason || '',
        weighted: Math.round((comps.evidenceSignal.value || 0) * 100),
        color: '#60a5fa',
      });
    }
    if (!rows.length) {
      return '<div class="ev-pie-no-flags">Компоненты формулы пока не детализированы (rules_v0)</div>';
    }

    var maxAbs = Math.max.apply(null, rows.map(function (r) { return Math.abs(r.weighted) || 1; }));
    return rows.map(function (c) {
      var isNeg = c.weighted < 0;
      var barPct = Math.max(4, Math.round(Math.abs(c.weighted / maxAbs) * 100));
      var valStr = (isNeg ? '−' : '+') + Math.abs(c.weighted) + ' пп';
      return ''
        + '<div class="ev-pie-row" title="' + c.desc + '">'
        + '<div class="ev-pie-row-num" style="background:' + c.color + '1A;color:' + c.color + '">' + c.num + '</div>'
        + '<div class="ev-pie-row-main"><div class="ev-pie-row-labels">'
        + '<span class="ev-pie-row-name">' + c.name + '</span></div>'
        + '<div class="ev-pie-row-bar-bg"><div class="ev-pie-row-bar-fill" style="width:' + barPct + '%;background:'
        + (isNeg ? '#f87171' : c.color) + ';opacity:0.72"></div></div></div>'
        + '<div class="ev-pie-row-val" style="color:' + (isNeg ? '#f87171' : c.color) + '">' + valStr + '</div>'
        + '</div>';
    }).join('');
  }

  function renderClassification(root, ec) {
    var body = root.querySelector('#pie-body-classification');
    if (!body) return;
    if (!ec || !ec.eventType) {
      body.innerHTML = kvRow('Тип события', '—');
      return;
    }
    body.innerHTML = [
      kvRow('Тип события', labelRu(EVENT_TYPE_RU, ec.eventType, ec.eventType), 'c-violet'),
      kvRow('Подтип', (ec.subType || '—').replace(/_/g, ' ')),
      kvRow('Профиль анализа', ec.analysisProfile || '—'),
      kvRow('Уверенность классификации', ec.classifierConfidence != null
        ? Math.round(ec.classifierConfidence * 100) + '%' : '—', 'c-green'),
    ].join('');
  }

  function renderMarketIntelligence(root, mi) {
    var body = root.querySelector('#pie-body-mi');
    var card = root.querySelector('#pie-card-mi');
    if (!body || !card) return;
    if (!mi) {
      card.style.display = 'none';
      return;
    }
    card.style.display = '';
    var anomaly = mi.volumeAnomaly && mi.volumeAnomaly !== 'none'
      ? labelRu(VOL_ANOM_RU, mi.volumeAnomaly, mi.volumeAnomaly)
      : 'нет';
    if (mi.anomalies && mi.anomalies.length) {
      anomaly = mi.anomalies.map(function (a) { return a.description || a.type; }).join(' · ');
    }
    body.innerHTML = [
      kvRow('Сигнал китов', labelRu(WHALE_RU, mi.whaleSignal, mi.whaleSignal || '—'), 'c-green'),
      kvRow('Направление денег', labelRu(MONEY_DIR_RU, mi.moneyDirection, mi.moneyDirection || '—')),
      kvRow('Динамика объёма', labelRu(VOL_SIGNAL_RU, mi.volumeSignal, mi.volumeSignal || '—')),
      kvRow('Аномалии', anomaly, anomaly !== 'нет' ? 'c-orange' : ''),
    ].join('');
  }

  function renderMarketStructure(root, ms) {
    var body = root.querySelector('#pie-body-structure');
    var card = root.querySelector('#pie-card-structure');
    if (!body || !card) return;
    if (!ms) {
      card.style.display = 'none';
      return;
    }
    card.style.display = '';
    var health = ms.marketHealthScore != null ? ms.marketHealthScore + ' / 100' : '—';
    var healthCls = ms.marketHealthScore >= 70 ? 'c-green' : (ms.marketHealthScore >= 45 ? 'c-orange' : 'c-red');
    body.innerHTML = [
      kvRow('Здоровье рынка', health, healthCls),
      kvRow('Ликвидность', labelRu(TIER_RU, ms.liquidityTier, ms.liquidityTier || '—'), riskClass(ms.liquidityTier === 'low' ? 'high' : ms.liquidityTier === 'high' ? 'low' : 'medium')),
      kvRow('Риск спреда', labelRu(RISK_LEVEL_RU, ms.spreadRisk, ms.spreadRisk || '—'), riskClass(ms.spreadRisk)),
      kvRow('Риск манипуляции', labelRu(RISK_LEVEL_RU, ms.manipulationRisk, ms.manipulationRisk || '—'), riskClass(ms.manipulationRisk)),
      kvRow('Надёжность цены', labelRu(RELIABILITY_RU, ms.priceReliability, ms.priceReliability || '—'), riskClass(ms.priceReliability === 'high' ? 'low' : ms.priceReliability === 'low' ? 'high' : 'medium')),
      kvRow('Надёжность рынка', ms.marketReliability != null ? '×' + ms.marketReliability : '—'),
      kvRow('Итог', ms.structureSummary || '—'),
    ].join('');
  }

  function renderEvidence(root, evd) {
    var body = root.querySelector('#pie-body-evidence');
    var card = root.querySelector('#pie-card-evidence');
    if (!body || !card) return;
    if (!evd) {
      card.style.display = 'none';
      return;
    }
    card.style.display = '';
    var counts = evd.counts || {};
    var items = evd.items || [];
    var freshest = null;
    items.forEach(function (it) {
      if (it.freshnessHours == null) return;
      if (freshest == null || it.freshnessHours < freshest) freshest = it.freshnessHours;
    });
    var freshStr = freshest != null
      ? (freshest < 1 ? 'менее часа' : freshest + ' ч назад')
      : '—';

    var html = [
      kvRow('Статус сбора', labelRu(EV_STATUS_RU, evd.collectionStatus, evd.collectionStatus || '—')),
      kvRow('Всего источников', String(counts.total || 0)),
      kvRow('Официальные / новости', (counts.official || 0) + ' / ' + (counts.news || 0)),
      kvRow('Свежесть данных', freshStr),
    ].join('');

    if (items.length) {
      html += '<div class="pie-evidence-items">';
      items.slice(0, 3).forEach(function (it) {
        html += '<div class="pie-evidence-item"><strong>' + (it.title || it.type) + '</strong>'
          + (it.summary ? ' — ' + it.summary : '')
          + (it.source ? ' · ' + it.source : '') + '</div>';
      });
      if (items.length > 3) {
        html += '<div class="pie-evidence-item">…и ещё ' + (items.length - 3) + '</div>';
      }
      html += '</div>';
    }
    body.innerHTML = html;
  }

  function renderContradiction(root, prob, si, canSeeEdge) {
    var locked = !canSeeEdge;
    setText(root, '#pie-contra-mkt', fmtPct01(prob && prob.marketProb, '—'));
    setText(root, '#pie-contra-pp', fmtPpProb(prob, locked));
    setText(root, '#pie-contra-gap', fmtEdgePp(prob && prob.edgePp, locked));
    applyLocked(root, '#pie-contra-pp-wrap', locked);

    var desc = '';
    if (prob && prob.status === 'insufficient_data') {
      desc = 'Недостаточно данных для карты противоречий.';
    } else if (si && si.userWhySelected) {
      desc = si.userWhySelected;
      if (prob && prob.edgePp != null && canSeeEdge) {
        var edge = Number(prob.edgePp);
        if (!isNaN(edge)) {
          desc += ' Разрыв рынок / PP AI: ' + fmtEdgePp(edge, false) + '.';
        }
      }
    } else {
      desc = 'Сравнение рыночной вероятности и оценки PP AI по текущему PIE-пакету.';
    }
    setText(root, '#pie-contra-desc', desc);
  }

  function renderProbability(root, prob, canSeeEdge) {
    var locked = !canSeeEdge;
    var ppText = fmtPpProb(prob, locked);
    var edgeText = fmtEdgePp(prob && prob.edgePp, locked);
    var mktText = fmtPct01(prob && prob.marketProb, '—');

    setText(root, '#pie-hdr-pp-val', ppText);
    setText(root, '#pie-hdr-edge-val', edgeText);
    setText(root, '#pie-sum-pp-val', ppText);
    setText(root, '#pie-sum-mkt-val', mktText);
    setText(root, '#pie-sum-edge-val', edgeText);

    applyLocked(root, '#pie-hdr-pp-wrap', locked);
    applyLocked(root, '#pie-hdr-edge-wrap', locked);
    applyLocked(root, '#pie-sum-pp-wrap', locked);

    var status = (prob && prob.status) || 'insufficient_data';
    var badge = root.querySelector('#pie-prob-status-badge');
    if (badge) {
      badge.textContent = labelRu(PROB_STATUS_RU, status, status);
      badge.className = 'pie-prob-badge ' + (status === 'ok' ? 'ok' : status === 'preliminary' ? 'preliminary' : 'insufficient');
    }

    var modeBadge = root.querySelector('#pie-prob-mode-badge');
    if (modeBadge) {
      modeBadge.textContent = (prob && prob.scoringMode) || 'rules_v0';
    }

    var compsEl = root.querySelector('#ev-pie-comps');
    if (compsEl) compsEl.innerHTML = buildComponentsHtml(prob);

    var flagsEl = root.querySelector('#ev-pie-flags');
    if (flagsEl) {
      var flags = (prob && prob.components && prob.components.missingComponents) || [];
      flagsEl.innerHTML = flags.length
        ? '<span class="ev-pie-flags-lbl">Неполные компоненты:</span>'
          + flags.map(function (f) { return '<span class="ev-pie-flag">' + f + '</span>'; }).join('')
        : '<span class="ev-pie-no-flags">Все доступные компоненты учтены</span>';
    }
  }

  /**
   * Рендер PIE + Strategy Intelligence Layer из pipelinePackage.
   * options.canSeeEdge — tier lock для ppProb / edge.
   */
  function renderPieFromPackage(pkg, meta, rootEl, options) {
    var root = rootEl || document.getElementById('pie-analysis');
    if (!root || !pkg) return;

    options = options || {};
    var canSeeEdge = options.canSeeEdge != null
      ? !!options.canSeeEdge
      : !!(global.PP && global.PP.getMeta && global.PP.getMeta().canSeeEdge);

    meta = meta || {};
    var prob = pkg.probability || {};
    var ec = pkg.eventClassification || {};
    var mi = pkg.marketIntelligence || {};
    var ms = pkg.marketStructure || {};
    var evd = pkg.evidence || {};
    var si = pkg.strategyIntelligence || null;
    var sv = pkg.strategyVerdict || null;

    var version = pkg.pieVersion || 'PIE';
    setText(root, '#pie-sec-badge', version);
    setText(root, '#pie-sec-sub', sourceSubLabel(meta, prob, pkg));

    renderStrategyBadge(root, si, pkg);
    renderStrategyVerdict(root, sv, canSeeEdge);
    renderProbability(root, prob, canSeeEdge);
    renderClassification(root, ec);
    renderMarketIntelligence(root, mi);
    renderMarketStructure(root, ms);
    renderEvidence(root, evd);
    renderContradiction(root, prob, si, canSeeEdge);

    global.__PP_PIE_PACKAGE__ = pkg;
    global.__PP_PIE_META__ = meta;
    global.__PP_PIE_STRATEGY__ = si;
    global.__PP_PIE_VERDICT__ = sv;
  }

  global.PP_PIE_API = {
    mapStoreEventToPieInput: mapStoreEventToPieInput,
    loadPiePackage: loadPiePackage,
    buildMockPiePackage: buildMockPiePackage,
    renderPieFromPackage: renderPieFromPackage,
  };
  global.renderPieFromPackage = renderPieFromPackage;

})(window);
