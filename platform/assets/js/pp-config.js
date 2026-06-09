/**
 * Конфиг окружения. На Vercel — через Environment Variables (префикс не нужен, подставляется при сборке статики вручную).
 * Локально можно переопределить в консоли: window.PP_CONFIG = { apiBase: 'http://127.0.0.1:8787' }
 */
window.PP_CONFIG = window.PP_CONFIG || {
  /** Пусто = только статика events-live.js. Пример: https://api.polypilot.pro */
  apiBase: "",
  /** Когда apiBase задан — подгружать live-события с GET /api/live/events */
  useLiveApi: false,
};
