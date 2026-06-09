/**
 * state.js — управление состоянием пользователя (tier)
 * Все данные в localStorage, без backend.
 *
 * Tiers: guest | pulse | trial | pro
 */

const PP = (function () {

  const TIERS = ['guest', 'pulse', 'trial', 'pro'];

  const TIER_META = {
    guest: {
      label: 'Гость',
      badgeClass: 'tier-guest',
      canSeeEdge: false,
      canSeeWarRoom: false,   // только 2 агента
      eventsPerDay: 0,
    },
    pulse: {
      label: 'Pulse',
      badgeClass: 'tier-pulse',
      canSeeEdge: false,
      canSeeWarRoom: true,
      eventsPerDay: 5,
    },
    trial: {
      label: 'PRO Trial',
      badgeClass: 'tier-trial',
      canSeeEdge: true,
      canSeeWarRoom: true,
      eventsPerDay: Infinity,
    },
    pro: {
      label: 'PRO',
      badgeClass: 'tier-pro',
      canSeeEdge: true,
      canSeeWarRoom: true,
      eventsPerDay: Infinity,
    },
  };

  // ---- Getters / Setters ----

  function getTier() {
    const t = localStorage.getItem('pp_tier');
    return TIERS.includes(t) ? t : 'guest';
  }

  function setTier(tier) {
    if (!TIERS.includes(tier)) return;
    localStorage.setItem('pp_tier', tier);
    localStorage.setItem('pp_tier_set', Date.now().toString());
    window.dispatchEvent(new CustomEvent('pp:tierChange', { detail: { tier } }));
  }

  function getMeta(tier) {
    return TIER_META[tier || getTier()];
  }

  // Trial: дата начала и кол-во дней осталось
  function getTrialDaysLeft() {
    if (getTier() !== 'trial') return null;
    const set = parseInt(localStorage.getItem('pp_tier_set') || '0', 10);
    if (!set) return 7;
    const elapsed = (Date.now() - set) / (1000 * 60 * 60 * 24);
    return Math.max(0, Math.ceil(7 - elapsed));
  }

  // Симулировать вход через Telegram (для воронки)
  function simulateTelegramLogin() {
    setTier('trial');
    localStorage.setItem('pp_tier_set', Date.now().toString());
  }

  // Симулировать оплату PRO
  function simulateProUpgrade() {
    setTier('pro');
  }

  return {
    getTier,
    setTier,
    getMeta,
    getTrialDaysLeft,
    simulateTelegramLogin,
    simulateProUpgrade,
    TIERS,
    TIER_META,
  };

})();

// Экспорт для совместимости
window.PP = PP;
