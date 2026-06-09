/**
 * Единое хранилище событий: LIVE (Polymarket) + DEMO (примеры MVP)
 */
window.PP_EVENTS_STORE = (function () {
  function normalizeDemo(events) {
    return (events || []).map(function (ev) {
      return Object.assign({}, ev, {
        isLive: false,
        isDemo: true,
        source: ev.source || 'demo',
      });
    });
  }

  function normalizeLive(events) {
    return (events || []).map(function (ev) {
      return Object.assign({}, ev, {
        isLive: true,
        isDemo: false,
        source: ev.source || 'polymarket',
      });
    });
  }

  function getLiveEvents() {
    return normalizeLive((window.EVENTS_LIVE || {}).events);
  }

  function getDemoEvents() {
    const fromJson = window.__PP_EVENTS_JSON__;
    if (fromJson && fromJson.events) {
      return normalizeDemo(fromJson.events);
    }
    return normalizeDemo((window.EVENTS_DATA || {}).events);
  }

  function getAllEvents() {
    return getLiveEvents().concat(getDemoEvents());
  }

  function getEventById(id) {
    return getAllEvents().find(function (ev) { return ev.id === id; }) || null;
  }

  return {
    getLiveEvents: getLiveEvents,
    getDemoEvents: getDemoEvents,
    getAllEvents: getAllEvents,
    getEventById: getEventById,
  };
})();
