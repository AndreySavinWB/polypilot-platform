/**
 * Конфиг окружения. На Vercel — через Environment Variables (префикс не нужен, подставляется при сборке статики вручную).
 * Локально можно переопределить в консоли: window.PP_CONFIG = { apiBase: 'http://127.0.0.1:8787' }
 */
window.PP_CONFIG = window.PP_CONFIG || {
  /** Пусто = только статика events-live.js. Пример: https://api.polypilot.pro */
  apiBase: "",
  /** Когда apiBase задан — подгружать live-события с GET /api/live/events */
  useLiveApi: false,

  /** Funnel 1.0 — заменить на реальные URL после создания каналов */
  funnel: {
    telegramChannel: "https://t.me/polypilot_pro",
    telegramBot: "https://t.me/polypilot_bot",
    telegramBotStart: "https://t.me/polypilot_bot?start=",
    supportTelegram: "https://t.me/polypilot_support",
    starterBotStart: "https://t.me/polypilot_bot?start=starter",
    /** Referral URL — заполнить после unlock $10k volume */
    polymarketReferralUrl: "",
  },
};

/** Helpers for funnel CTAs */
window.PP_FUNNEL = {
  botLink(payload) {
    const base = (window.PP_CONFIG.funnel || {}).telegramBotStart || "https://t.me/polypilot_bot?start=";
    return payload ? base + encodeURIComponent(payload) : (window.PP_CONFIG.funnel || {}).starterBotStart;
  },
  guestEventUrl(eventId, source) {
    const q = new URLSearchParams({ id: eventId || "" });
    if (source) q.set("utm_source", source);
    q.set("utm_campaign", "funnel_1_0");
    return "guest-event.html?" + q.toString();
  },
  starterUrl(source) {
    const q = source ? "?utm_source=" + encodeURIComponent(source) + "&utm_campaign=starter_cohort_1" : "";
    return "learn.html" + q + "#starter";
  },
  polymarketEventUrl(ev) {
    const ref = (window.PP_CONFIG.funnel || {}).polymarketReferralUrl;
    const base = ev && ev.marketUrl ? ev.marketUrl : "https://polymarket.com";
    return ref || base;
  },
};
