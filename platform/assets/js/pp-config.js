/**
 * Конфиг окружения PolyPilot platform.
 *
 * Локально (консоль браузера):
 *   window.PP_CONFIG = { apiBase: 'http://127.0.0.1:8787', usePieApi: true };
 *
 * Production: Railway Public URL → PP_PROD_API_BASE ниже
 * (Railway → backend service → Settings → Networking → Generate Domain).
 */
(function (global) {
  'use strict';

  /** Public URL backend на Railway. Обновить после первого деплоя backend/. */
  var PP_PROD_API_BASE = 'https://polypilot-platform-production.up.railway.app';

  function isProdHost() {
    if (typeof location === 'undefined') return false;
    var h = location.hostname;
    if (!h || h === 'localhost' || h === '127.0.0.1') return false;
    return /\.vercel\.app$/i.test(h) || /^polypilot\.pro$/i.test(h) || /\.polypilot\.pro$/i.test(h);
  }

  var prod = isProdHost();
  var prodApi = (PP_PROD_API_BASE || '').replace(/\/$/, '');

  var defaults = {
    apiBase: prod && prodApi ? prodApi : '',
    useLiveApi: prod && !!prodApi,
    usePieApi: prod && !!prodApi,
    pieApiTimeoutMs: 15000,
    pieDebug: !prod,
    funnel: {
      telegramChannel: 'https://t.me/polypilot_pro',
      telegramBot: 'https://t.me/polypilot_pro_bot',
      telegramBotStart: 'https://t.me/polypilot_pro_bot?start=',
      supportTelegram: 'https://t.me/polypilot_support',
      starterBotStart: 'https://t.me/polypilot_pro_bot?start=starter',
      polymarketReferralUrl: '',
    },
  };

  global.PP_CONFIG = Object.assign(defaults, global.PP_CONFIG || {});

  global.PP_FUNNEL = {
    botLink(payload) {
      var base = (global.PP_CONFIG.funnel || {}).telegramBotStart || 'https://t.me/polypilot_pro_bot?start=';
      return payload ? base + encodeURIComponent(payload) : (global.PP_CONFIG.funnel || {}).starterBotStart;
    },
    guestEventUrl(eventId, source) {
      var q = new URLSearchParams({ id: eventId || '' });
      if (source) q.set('utm_source', source);
      q.set('utm_campaign', 'funnel_1_0');
      return 'guest-event.html?' + q.toString();
    },
    starterUrl(source) {
      var q = source ? '?utm_source=' + encodeURIComponent(source) + '&utm_campaign=starter_cohort_1' : '';
      return 'learn.html' + q + '#starter';
    },
    polymarketEventUrl(ev) {
      var ref = (global.PP_CONFIG.funnel || {}).polymarketReferralUrl;
      var base = ev && ev.marketUrl ? ev.marketUrl : 'https://polymarket.com';
      return ref || base;
    },
  };
})(typeof window !== 'undefined' ? window : {});
