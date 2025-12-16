// Méthodes liées aux gains / recettes

export function computeTotalGains(vm) {
  return (vm.sales || []).reduce((s, it) => s + (Number(it.amount) || 0), 0);
}

export function computeAverageGainPerAnimal(vm) {
  const total = computeTotalGains(vm);
  const count = (vm.animals || []).length || 1;
  return total / count;
}

export function formatGainCurrency(vm, value) {
  if (value == null) return '0 FCFA';
  return new Intl.NumberFormat('fr-FR').format(Number(value)) + ' FCFA';
}

export function addGainRecord(vm, record) {
  const rec = { id: crypto.randomUUID(), ...record, amount: Number(record.amount) };
  vm.gains = [rec, ...(vm.gains || [])];
}

export function clearGains(vm) {
  vm.gains = [];
}

export function computeGainsComputed(vm) {
  const price = Number(vm.gainPricePerKg) || 0;
  const initial = vm.band?.nombre_initial || 0;

  const weeksWithWeight = [...(vm.animalInfos || [])
    .filter(i => i.semaine_production && i.poids_moyen !== null && i.poids_moyen !== undefined)
    .map(i => i.semaine_production)]
    .sort((a, b) => a - b)
    .filter((w, idx, arr) => arr.indexOf(w) === idx);

  if (!weeksWithWeight.length) {
    return { labels: [], actual: [], reference: [], cumActual: 0, cumRef: 0, delta: 0 };
  }

  const deathsByWeek = new Map();
  (vm.animalInfos || []).forEach(info => {
    if (info?.semaine_production) {
      deathsByWeek.set(info.semaine_production, Number(info.morts_semaine || 0));
    }
  });

  let cumulativeDeaths = 0;
  const labels = [];
  const actual = [];
  const reference = [];

  for (const w of weeksWithWeight) {
    cumulativeDeaths += deathsByWeek.get(w) || 0;
    const alive = Math.max(0, initial - cumulativeDeaths);

    const actualInfo = (vm.animalInfos || []).find(i => i.semaine_production === w);
    const weightActual = actualInfo?.poids_moyen ? Number(actualInfo.poids_moyen) : null;
    const refObj = (vm.weightReference || []).find(r => r.week === w);
    const weightRef = refObj ? ((refObj.low + refObj.high) / 2) : null;

    const gainAct = weightActual && price ? weightActual * alive * price : 0;
    // Use survivors at this week for reference revenue (reference weight * survivors_this_week * price)
    const gainRef = weightRef && price ? weightRef * alive * price : 0;

    labels.push(`S${w}`);
    actual.push(Math.round(gainAct));
    reference.push(Math.round(gainRef));
  }

  const cumActual = actual.reduce((a, b) => a + b, 0);
  const cumRef = reference.reduce((a, b) => a + b, 0);

  return {
    labels,
    actual,
    reference,
    cumActual,
    cumRef,
    delta: cumActual - cumRef
  };
}

export function computeGainPerformanceScore(vm) {
  const ref = computeGainsComputed(vm).cumRef || 0;
  if (!ref) return 0;
  const ratio = (computeGainsComputed(vm).cumActual / ref) * 100;
  return Math.max(0, Math.min(150, ratio));
}

export function computeProfitComputed(vm) {
  const gains = computeGainsComputed(vm);
  const revenue = Number(gains.cumActual || 0);
  const revenueRef = Number(gains.cumRef || 0);

  const consumptionCosts = Number(vm.totalCost || 0); // consommations
  const treatmentCosts = Number(vm.totalTreatmentCost || 0); // traitements
  const elementaryExpenses = Number(vm.totalExpensesElementaires || 0); // dépenses élémentaires

  const costs = consumptionCosts + treatmentCosts + elementaryExpenses;

  return {
    revenue,
    revenueRef,
    costs,
    profit: revenue - costs
  };
}
