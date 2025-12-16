// Fonctions liées au dashboard de la bande

export function calculateWeightTrend(band) {
  if (!band?.poids_moyen_initial) return 0;
  return band.poids_moyen_initial > 2.5 ? 2.5 : -1.0;
}

export function calculateCostTrend(totalCost) {
  return totalCost < 500 ? -1.2 : 3.5;
}

export function calculateMortalityTrend(band) {
  if (!band?.nombre_initial || band.nombre_initial === 0) return 0;
  const mortalityRate = ((band.nombre_morts_totaux || 0) / band.nombre_initial) * 100;
  return mortalityRate < 5 ? 0.5 : 2.5;
}

export function calculateICTrend(totalCost, currentAnimals) {
  if (currentAnimals === 0 || totalCost === 0) return 0;
  const ic = totalCost / currentAnimals;
  return ic < 2 ? -0.8 : 1.5;
}

// Autres méthodes dashboard à ajouter ici
