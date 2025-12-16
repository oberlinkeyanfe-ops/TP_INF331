// Fonctions utilitaires pour la gestion des tabs et autres méthodes transverses

export function getTrendClass(trendValue) {
  if (typeof trendValue !== 'number') return 'neutral';
  if (trendValue > 0) return 'positive';
  if (trendValue < 0) return 'negative';
  return 'neutral';
}

// Ajoutez ici d'autres fonctions utilitaires
