// Méthodes et helpers pour les charts (pré-traitement de données)

export function buildWeightSeries(animalInfos) {
  const labels = (animalInfos || []).map(i => `S${i.semaine_production}`);
  const series = (animalInfos || []).map(i => i.poids_moyen || null);
  return { labels, series };
}

export function buildConsumptionSeries(consommations) {
  const labels = (consommations || []).map(c => c.date);
  const series = (consommations || []).map(c => c.kg || 0);
  return { labels, series };
}

export function buildGainsSeries(gainsData) {
  const labels = (gainsData || []).map(g => g.date || g.jour || '');
  const actual = (gainsData || []).map(g => g.actual || g.valeur || 0);
  const reference = (gainsData || []).map(g => g.reference || 0);
  return { labels, actual, reference };
}
