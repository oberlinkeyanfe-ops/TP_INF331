// Fonctions liées à l'onglet Consommation

export function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR');
}

// Ajoutez ici d'autres méthodes spécifiques à la consommation

export function updateCostPreview(vm) {
  const kg = parseFloat(vm.consumptionForm.kg || 0) || 0;
  const prixAlim = parseFloat(vm.consumptionForm.prix_unitaire || 0) || 0;
  const eau = parseFloat(vm.consumptionForm.eau_litres || 0) || 0;
  const prixEau = parseFloat(vm.consumptionForm.prix_eau_unitaire || 0) || 0;
  const cost = Math.round(kg * prixAlim + eau * prixEau);
  vm.consumptionFormCostPreview = cost;
  vm.consumptionForm.cout = cost;
}

export async function loadConsommations(vm) {
  if (!vm.id) return;
  const url = `http://localhost:5000/consommations/bande/${vm.id}`;
  const response = await fetch(url, { credentials: 'include' });
  if (!response.ok) {
    vm.consommations = [];
    return;
  }
  const data = await response.json().catch(() => ({}));
  const raw = data.consommations || [];
  vm.consommations = raw.map(c => ({
    id: c.id,
    date: c.date,
    type: c.type_aliment || '',
    kg: c.aliment_kg || 0,
    cout: (c.cout_aliment || 0) + (c.prix_eau_unitaire || 0) * (c.eau_litres || 0),
    bande_id: c.bande_id,
    eau_litres: c.eau_litres || 0,
    prix_unitaire: c.prix_unitaire || (c.aliment_kg ? (c.cout_aliment || 0) / c.aliment_kg : 0),
    prix_eau_unitaire: c.prix_eau_unitaire || 25,
    semaine_production: c.semaine_production || null
  }));
  vm.filledWeeks = vm.getFilledWeeksMap();
}

export function startEditConsumption(vm, cons) {
  vm.editingConsumptionId = cons.id;
  vm.consumptionForm = {
    date: cons.date,
    semaine_production: cons.semaine_production,
    type: cons.type,
    kg: cons.kg,
    cout: cons.cout,
    eau_litres: cons.eau_litres || 0,
    prix_unitaire: cons.prix_unitaire || 0,
    prix_eau_unitaire: cons.prix_eau_unitaire ?? 25
  };
  vm.consumptionFormCostPreview = cons.cout || 0;
  vm.scrollToConsumptionForm();
}

export function resetConsumptionForm(vm) {
  vm.editingConsumptionId = null;
  vm.consumptionForm = {
    date: new Date().toISOString().slice(0, 10),
    semaine_production: null,
    type: '',
    kg: 0,
    cout: 0,
    eau_litres: 0,
    prix_unitaire: 0,
    prix_eau_unitaire: 25
  };
  vm.consumptionFormCostPreview = 0;
}

export async function deleteConsumption(vm, cons) {
  // Frontend safeguard: empêcher suppression si des semaines supérieures existent
  if (cons.semaine_production != null) {
    const hasHigher = vm.consommations.some(c => Number(c.semaine_production) > Number(cons.semaine_production));
    if (hasHigher) {
      alert(" Supprimez d'abord les consommations des semaines supérieures avant de supprimer celle-ci.");
      return;
    }
  }

  const confirmDelete = confirm('Supprimer cette consommation ?');
  if (!confirmDelete) return;
  try {
    const response = await fetch(`http://localhost:5000/consommations/${cons.id}`, { method: 'DELETE', credentials: 'include' });
    if (response.ok) {
      vm.consommations = vm.consommations.filter(c => c.id !== cons.id);
      if (vm.editingConsumptionId === cons.id) vm.resetConsumptionForm();
      vm.updateTrendsFromData();
      vm.calculateKPI();
      alert(' Consommation supprimée');
    } else {
      const err = await response.json().catch(() => ({ error: 'Erreur inconnue' }));
      alert(` Erreur : ${err.error || response.statusText}`);
    }
  } catch (error) {
    console.error(' Erreur suppression:', error);
    alert(' Erreur de connexion au serveur');
  }
}

export async function addConsumption(vm) {
  try {
    if (!vm.id) { alert(" Veuillez sélectionner une bande d'abord"); return; }

    const durationWeeks = vm.durationWeeks;
    const isEditing = !!vm.editingConsumptionId;

    if (!vm.consumptionForm.semaine_production) { alert(' Sélectionnez une semaine'); return; }
    if (!vm.consumptionForm.type || vm.consumptionForm.type.trim() === '') { alert(" Le type d'aliment est obligatoire"); return; }

    const kgValue = parseFloat(vm.consumptionForm.kg);
    if (!vm.consumptionForm.kg || isNaN(kgValue) || kgValue <= 0) { alert(" La quantité (kg) doit être un nombre supérieur à 0"); return; }

    const weekNumber = parseInt(vm.consumptionForm.semaine_production, 10);
    if (weekNumber > durationWeeks) { alert(` La semaine ${weekNumber} dépasse la durée prévue (${durationWeeks} sem.)`); return; }

    // ensure numeric comparison for semaine_production to avoid type mismatches
    const existingWeek = vm.consommations.find(c => Number(c.semaine_production) === Number(weekNumber) && c.id !== vm.editingConsumptionId);
    if (existingWeek) { alert(` Une consommation existe déjà pour la semaine ${weekNumber}.`); return; }

    const prixUnitaire = parseFloat(vm.consumptionForm.prix_unitaire || 0) || 0;
    const prixEau = parseFloat(vm.consumptionForm.prix_eau_unitaire || 0) || 0;
    let coutTotal = parseFloat(vm.consumptionForm.cout || 0) || 0;
    if (!coutTotal) coutTotal = +(prixUnitaire * kgValue + prixEau * parseFloat(vm.consumptionForm.eau_litres || 0)).toFixed(2);

    // Force payload date to the canonical date for the selected week to keep backend week calculation consistent
    const payloadDate = vm.getDateForWeek(weekNumber);

    // Auto-create missing prior weeks as zero placeholders (type starting with 'Auto') so UX shows them as yellow warnings.
    // Backend will accept and allow these placeholders to be replaced later when the user inputs a real consumption for that week.
    if (!isEditing) {
      for (let w = 1; w < weekNumber; w++) {
        const missing = !vm.consommations.some(c => Number(c.semaine_production) === Number(w));
        if (missing) {
          const placeholderPayload = { bande_id: parseInt(vm.id), date: vm.getDateForWeek(w), type_aliment: 'Auto 0 - placeholder', aliment_kg: 0, cout_aliment: 0, eau_litres: 0, prix_unitaire: null, prix_eau_unitaire: 25, semaine_production: w };
          try {
            const resp = await fetch('http://localhost:5000/consommations/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify(placeholderPayload) });
            if (resp.ok) {
              const pd = await resp.json().catch(() => null);
              if (pd && pd.id) {
                vm.consommations.push({ id: pd.id, date: pd.date, type: pd.type_aliment || 'Auto', kg: pd.aliment_kg || 0, cout: pd.cout_aliment || 0, bande_id: pd.bande_id, semaine_production: pd.semaine_production });
              }
            }
          } catch (e) {
            console.warn('Échec création placeholder semaine', w, e);
          }
        }
      }
    }

    const payload = { bande_id: parseInt(vm.id), date: payloadDate, type_aliment: vm.consumptionForm.type.trim(), aliment_kg: kgValue, cout_aliment: coutTotal, eau_litres: parseFloat(vm.consumptionForm.eau_litres || 0), prix_unitaire: prixUnitaire || null, prix_eau_unitaire: prixEau || 25, semaine_production: weekNumber, poids_moyen_actuel: null };

    const url = isEditing ? `http://localhost:5000/consommations/${vm.editingConsumptionId}` : 'http://localhost:5000/consommations/';
    const method = isEditing ? 'PUT' : 'POST';
    const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, credentials: 'include', body: JSON.stringify(payload) });
    let responseData;
    try { responseData = await response.json(); } catch (e) { responseData = { error: 'Réponse non valide' }; }

    if (response.ok) {
      const updated = { id: responseData.id, date: responseData.date, type: responseData.type_aliment, kg: responseData.aliment_kg, eau_litres: responseData.eau_litres || payload.eau_litres, prix_unitaire: responseData.prix_unitaire || payload.prix_unitaire || 0, prix_eau_unitaire: responseData.prix_eau_unitaire || payload.prix_eau_unitaire || 25, cout: (responseData.cout_aliment || payload.cout_aliment || 0) + (responseData.prix_eau_unitaire || payload.prix_eau_unitaire || 0) * (responseData.eau_litres || payload.eau_litres || 0), bande_id: responseData.bande_id, semaine_production: responseData.semaine_production || weekNumber };
      if (isEditing) { const idx = vm.consommations.findIndex(c => c.id === vm.editingConsumptionId); if (idx !== -1) vm.consommations.splice(idx, 1, updated); alert(' Consommation mise à jour'); } else { vm.consommations.unshift(updated); alert(' Consommation ajoutée avec succès !'); }
      vm.resetConsumptionForm();
      vm.filledWeeks = vm.getFilledWeeksMap();
      vm.updateTrendsFromData();
      vm.calculateKPI();
    } else {
      const errorMsg = responseData.error || `Erreur ${response.status}`;
      console.error(' Erreur détaillée:', { status: response.status, error: errorMsg, payload });
      alert(` Erreur : ${errorMsg}`);
    }

  } catch (error) {
    console.error(' Erreur complète:', error);
    if (error.name === 'TypeError' && error.message.includes('fetch')) alert(' Erreur de connexion au serveur'); else alert(` Erreur : ${error.message}`);
  }
}
