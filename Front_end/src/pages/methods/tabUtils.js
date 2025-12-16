// Fonctions utilitaires pour la gestion des tabs et autres méthodes transverses

export function getTrendClass(trendValue) {
  if (typeof trendValue !== 'number') return 'neutral';
  if (trendValue > 0) return 'positive';
  if (trendValue < 0) return 'negative';
  return 'neutral';
}

// Ajoutez ici d'autres fonctions utilitaires

export function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return '0';
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(decimals) : '0';
}

export function formatCurrencyFCFA(value, decimals = 0) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '0 FCFA';
  return `${num.toFixed(decimals)} FCFA`;
}

export function formatWeekRange(startDate, week) {
  if (!startDate) return '—';
  const start = new Date(startDate);
  start.setDate(start.getDate() + (week - 1) * 7);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  return `${start.toLocaleDateString('fr-FR')} - ${end.toLocaleDateString('fr-FR')}`;
}

export function formatPercent(val) {
  const num = Number(val);
  if (!Number.isFinite(num)) return '0%';
  return `${num.toFixed(0)}%`;
}

export function parseDate(str) {
  if (!str) return null;
  const parts = str.split('/');
  if (parts.length === 3) {
    const [day, month, year] = parts;
    const d = new Date(parseInt(year, 10), parseInt(month, 10) - 1, parseInt(day, 10));
    return Number.isNaN(d.getTime()) ? null : d;
  }
  const d = new Date(str);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function isSameDay(a, b) {
  return a && b && a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

export function getFilledWeeksMapFrom(consommations) {
  const map = new Map();
  (consommations || []).forEach(c => { if (c.semaine_production) map.set(c.semaine_production, true); });
  return map;
}

export function scrollToConsumptionForm() { const el = document.querySelector('.consumption-form'); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
