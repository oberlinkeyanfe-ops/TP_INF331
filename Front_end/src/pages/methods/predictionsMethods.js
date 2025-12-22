// Fonctions liées à l'onglet Prédictions

export function calculateWeightIncrease(day, model) {
  switch(model) {
    case 'exponentiel': return 0.04;
    case 'saisonnier': return 0.03;
    default: return 0.035;
  }
}

export function getMarginClass(margin) {
  return margin > 0 ? 'positive' : margin < 0 ? 'negative' : 'neutral';
}

export function getProfitClass(profit) {
  return profit > 0 ? 'positive' : profit < 0 ? 'negative' : 'neutral';
}

export function getROIClass(roi) {
  return roi > 15 ? 'good' : roi > 5 ? 'medium' : 'low';
}

// Ajoutez ici d'autres méthodes spécifiques aux prédictions

export function calculateAverageConsumptionFrom(vm) {
  // Return average consumption PER BIRD PER DAY
  // Consommation records may use different keys depending on source: prefer 'aliment_kg' or 'kg'
  if (!vm.consommations || vm.consommations.length === 0) return 0;
  const totalKg = vm.consommations.reduce((sum, c) => {
    const kg = Number(c.aliment_kg ?? c.kg ?? c.alimentKg ?? 0) || 0;
    return sum + kg;
  }, 0);
  const periods = Math.max(1, vm.consommations.length);
  const birds = Number(vm.band?.nombre_initial || vm.currentAnimals || 1);
  // assume each period is one week (7 days)
  const avgPerBirdPerDay = birds > 0 ? (totalKg / periods) / birds / 7 : 0;
  return avgPerBirdPerDay;
}

export function getAverageCostPerKgFrom(vm) {
  if (!vm.consommations || vm.consommations.length === 0) return 1.8;
  const totalCost = vm.consommations.reduce((sum, c) => sum + (Number(c.cout_aliment ?? c.cout ?? c.coutAliment ?? 0) || 0), 0);
  const totalKg = vm.consommations.reduce((sum, c) => sum + (Number(c.aliment_kg ?? c.kg ?? c.alimentKg ?? 0) || 0), 0);
  return totalKg > 0 ? totalCost / totalKg : 1.8;
}

export function getPricePerKgFrom(vm) {
  return vm.band?.race === 'Poulet de chair' ? 3.5 : 4.0;
}

export function findOptimalSellingDateFrom(predictions) {
  if (!predictions || predictions.length === 0) return '';
  const max = predictions.reduce((max, p) => p.marge > max.marge ? p : max, predictions[0]);
  return max.date;
}

export function generatePredictions(vm) {
  // Reset any previous error
  vm.predictionErrorMsg = '';

  // Determine horizon requested by user (7/14/30) and current band duration
  const desiredDays = parseInt(vm.predictionDays) || 7;
  const durationDays = Number(vm.band?.duree_jours || 0);
  const currentWeek = Number(vm.currentProductionWeek || vm.animalAgeWeeks || 0);

  // If band has a duration defined, compute remaining days; otherwise allow desiredDays
  let remainingDays = durationDays > 0 ? Math.max(0, durationDays - (currentWeek * 7)) : null;

  // If band is finished (remainingDays === 0) block predictions and mark terminee
  if (remainingDays === 0) {
    vm.predictions = [];
    vm.totalPredictedProfit = 0;
    vm.predictionErrorMsg = "La bande a atteint sa durée : aucune prédiction possible.";
    if (vm.band && vm.band.statut !== 'terminee') {
      vm.band.statut = 'terminee';
      try {
        fetch(`http://localhost:5000/bandes/${vm.band.id}`, {
          method: 'PUT',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ statut: 'terminee' })
        }).then(res => res.ok ? null : console.warn('Failed set status terminee for band', res.status));
      } catch (e) { console.warn('Failed to persist statut terminee:', e); }
    }
    return;
  }

  // Decide how many days to predict: either desiredDays or capped by remainingDays when duration exists
  let daysToPredict = desiredDays;
  if (remainingDays !== null) {
    daysToPredict = Math.min(desiredDays, remainingDays);
  }

  if (!daysToPredict || daysToPredict <= 0) {
    vm.predictions = [];
    vm.totalPredictedProfit = 0;
    vm.predictionErrorMsg = "Aucune période restante pour prédire jusqu'à la fin.";
    return;
  }

  // Notice: if the requested horizon is longer than remaining days, inform the user
  if (remainingDays !== null && daysToPredict < desiredDays) {
    vm.predictionNotice = `Horizon réduit à ${daysToPredict} jour(s) (fin de bande plus proche).`;
  } else {
    vm.predictionNotice = '';
  }

  const days = daysToPredict;

  vm.predictions = [];
  vm.totalPredictedProfit = 0;
  let runningPredCost = 0;
  const currentWeight = Number(vm.getObservedWeightForPredictions?.() ?? vm.band?.poids_moyen_initial ?? 2.0);
  const currentAnimals = Number(vm.currentAnimals || 0);
  const initialAnimals = Number(vm.band?.nombre_initial || currentAnimals || 0);
  const totalCostToDate = vm.totalCostsAll || 0;
  const totalDeaths = vm.totalAnimalDeaths || (vm.band?.nombre_morts_totaux || 0);
  const weeksObserved = vm.animalAgeWeeks || vm.durationWeeks || 1;
  const avgDeathsPerDay = totalDeaths > 0 ? totalDeaths / Math.max(1, weeksObserved * 7) : 0.15;
  const today = new Date();

  for (let i = 1; i <= days; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() + i);
    const dateStr = date.toISOString().slice(0, 10);
    const weightIncrease = calculateWeightIncrease(i, vm.predictionModel);
    // iterative weight: each day builds on previous day's weight
    const prevWeight = i === 1 ? Number(currentWeight) : Number(vm.predictions[i - 2]?.poids || currentWeight);
    const predictedWeight = Number(prevWeight) * (1 + Number(weightIncrease || 0));

    // consumption scales with weight ratio relative to observed weight
    // calculateAverageConsumptionFrom now returns per-bird consumption (per period)
    const avgConsumptionPerBird = Number(calculateAverageConsumptionFrom(vm) || 0);
    const weightRatio = Number(currentWeight) > 0 ? (predictedWeight / Number(currentWeight)) : 1;
    // predicted consumption PER BIRD for the period
    const predictedConsumptionPerBird = Number(avgConsumptionPerBird * weightRatio || 0);
    // estimate survivors earlier (used for total cost/value)
    const expectedDeaths = avgDeathsPerDay * i;
    const survivors = Math.max(0, currentAnimals - expectedDeaths);
    // predicted cost must be TOTAL cost for surviving birds (per-bird * survivors * cost/kg)
    const avgCostPerKg = Number(getAverageCostPerKgFrom(vm) || 0);
    const predictedCostTotal = Number(predictedConsumptionPerBird * (survivors || 0) * avgCostPerKg || 0);
    runningPredCost += predictedCostTotal;
    // Use fixed market price when provided (gainPricePerKg), otherwise fallback to model price
    const prixKg = Number(vm.gainPricePerKg ?? getPricePerKgFrom(vm) ?? 0);
    const predictedValue = Number(predictedWeight * prixKg * survivors || 0);
    // Marge quotidienne calculée comme valeur attendue moins le coût prédit (totaux)
    const predictedMargin = Number(predictedValue - predictedCostTotal || 0);
    const tauxSurvie = initialAnimals > 0 ? (survivors / initialAnimals) * 100 : (initialAnimals === 0 && currentAnimals > 0 ? (survivors / currentAnimals) * 100 : 100);
      vm.predictions.push({
      jour: i,
      date: dateStr,
      poids: Number.isFinite(predictedWeight) ? Number(predictedWeight) : 0,
      // store consumption as PER-BIRD (same unit as poids denominator)
      consommation: Number.isFinite(predictedConsumptionPerBird) ? Number(predictedConsumptionPerBird) : 0,
      // store cost as TOTAL for the flock at that day
      cout: Number.isFinite(predictedCostTotal) ? Number(predictedCostTotal) : 0,
      valeur: Number.isFinite(predictedValue) ? Number(predictedValue) : 0,
      marge: Number.isFinite(predictedMargin) ? Number(predictedMargin) : 0,
      survivants: Number.isFinite(survivors) ? Math.round(survivors) : 0,
      taux_survie: Number.isFinite(tauxSurvie) ? Number(tauxSurvie) : 0
    });
  }

  // total predicted profit = margin at the optimal selling day (max margin)
  if (vm.predictions.length) {
    const best = vm.predictions.reduce((b, p) => (p.marge > (b.marge ?? -Infinity) ? p : b), vm.predictions[0]);
    vm.optimalPrediction = best;
    vm.totalPredictedProfit = Number(best.marge || 0);
    vm.optimalSellingDate = best.date || findOptimalSellingDateFrom(vm.predictions);
    vm.roi = ((vm.totalPredictedProfit || 0) / (totalCostToDate || 1)) * 100 || 0;
  } else {
    vm.totalPredictedProfit = 0;
    vm.optimalPrediction = null;
    vm.optimalSellingDate = '';
    vm.roi = 0;
  }
}

export function getObservedWeightForPredictions(vm) {
  const last = vm.animalLastWeight;
  if (last && last.value) return Number(last.value) || 0;
  return vm.band?.poids_moyen_initial || 2.0;
}
