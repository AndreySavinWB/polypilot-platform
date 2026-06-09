/**
 * sidebar.js — рендер бокового меню
 * Подключается после state.js в app/*.html
 */

(function () {

  // SVG иконки (Lucide-style, stroke-based, viewBox 0 0 24 24)
  const ICONS = {
    home: `<polyline points="3 9 12 2 21 9"/><path d="M9 22V12h6v10"/>`,
    calendar: `<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>`,
    zap: `<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>`,
    compass: `<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>`,
    book: `<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>`,
    headphones: `<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>`,
    creditcard: `<rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/>`,
    settings: `<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>`,
  };

  const NAV = [
    { id: 'home',          label: 'Главная',            file: 'index.html',        icon: ICONS.home },
    { id: 'events',        label: 'События',            file: 'events.html',       icon: ICONS.calendar },
    { id: 'how-it-works',  label: 'Как это работает',   file: 'how-it-works.html', icon: ICONS.compass },
    { id: 'learn',         label: 'Обучение',           file: 'learn.html',        icon: ICONS.book },
    { id: 'support',       label: 'Поддержка',          file: 'support.html',      icon: ICONS.headphones },
    { id: 'pricing',       label: 'Тарифы',             file: 'pricing.html',      icon: ICONS.creditcard },
    { id: 'settings',      label: 'Настройки',          file: 'settings.html',     icon: ICONS.settings },
  ];

  function getActiveFile() {
    const path = window.location.pathname;
    return path.split('/').pop() || 'index.html';
  }

  function getHomeHref() {
    const file = getActiveFile();
    return file === 'index.html' ? '#' : 'index.html';
  }

  function renderSidebar() {
    const el = document.getElementById('sidebar');
    if (!el) return;

    const activeFile = getActiveFile();
    const tier       = window.PP ? PP.getTier() : 'guest';
    const tierMeta   = window.PP ? PP.getMeta(tier) : { label: 'Гость', badgeClass: 'tier-guest' };
    const trialDays  = window.PP ? PP.getTrialDaysLeft() : null;

    const navHTML = NAV.map(item => {
      const isActive = activeFile === item.file;
      return `
        <a href="${item.file}" class="nav-item${isActive ? ' active' : ''}">
          <svg class="nav-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">${item.icon}</svg>
          <span>${item.label}</span>
        </a>`;
    }).join('');

    // Trial countdown banner
    const trialBanner = (tier === 'trial' && trialDays !== null)
      ? `<div class="trial-banner">⏱ PRO Trial — ещё ${trialDays} дн.</div>`
      : '';

    el.innerHTML = `
      <div class="sidebar-inner">
        <a href="${getHomeHref()}" class="sidebar-logo">
          <img src="../assets/img/logo-icon.png" alt="PP" class="logo-icon">
          <span class="logo-text">
            <span class="logo-poly">Poly</span><span class="logo-pilot">Pilot</span>
          </span>
        </a>

        ${trialBanner}

        <nav class="sidebar-nav">${navHTML}</nav>

        <div class="sidebar-footer">
          <span class="sidebar-footer-label">Аккаунт</span>
          <span class="tier-badge ${tierMeta.badgeClass}">${tierMeta.label}</span>
        </div>
      </div>`;
  }

  // Перерисовать при смене tier
  window.addEventListener('pp:tierChange', renderSidebar);

  renderSidebar();

})();
