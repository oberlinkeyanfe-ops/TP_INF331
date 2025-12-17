// Méthodes liées aux traitements

export function prefillTreatment(vm, t) {
  vm.treatmentForm.produit = t?.name || '';
  vm.treatmentForm.maladie = vm.selectedDisease || (t?.diseases?.[0] || '');
  vm.treatmentForm.dose = vm.recommendedDose(t);
  vm.treatmentForm.note = t?.description || '';
  vm.treatmentForm.cout = t?.cost || 0;
  vm.$nextTick(() => {
    const form = document.querySelector('.treatment-form');
    if (form) {
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
      const firstInput = form.querySelector('input, select, textarea');
      if (firstInput) firstInput.focus();
    }
  });
}

export function resetTreatmentForm(vm) {
  vm.treatmentForm = { maladie: '', produit: '', dose: '', debut: new Date().toISOString().slice(0,10), fin: '', note: '', cout: 0 };
}

export function addTreatmentRecord(vm) {
  const record = { ...vm.treatmentForm, cout: Number(vm.treatmentForm.cout) || 0 };
  vm.treatmentRecords.unshift(record);
  localStorage.setItem(treatmentStorageKey(vm), JSON.stringify(vm.treatmentRecords));
  resetTreatmentForm(vm);
  alert('✅ Traitement enregistré (local)');
}

export function recommendedDose(vm, t) {
  if (!t?.doses) return '—';
  const age = vm.animalAgeWeeks || 0;
  const found = t.doses.find(d => age <= d.maxWeek);
  return found ? found.text : t.doses[t.doses.length - 1].text;
}

export function treatmentStorageKey(vm) {
  return `treatments_${vm.id || 'default'}`;
}

export function loadTreatmentRecordsFromStorage(vm) {
  try {
    const raw = localStorage.getItem(treatmentStorageKey(vm));
    vm.treatmentRecords = raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.warn('Erreur chargement traitements locaux', e);
    vm.treatmentRecords = [];
  }
}

export async function fetchTreatmentRecordsFromServer(vm) {
  try {
    if (!vm.id) return;
    const resp = await fetch(`http://localhost:5000/traitements/bande/${vm.id}`, { credentials: 'include' });
    if (!resp.ok) {
      console.warn('Fetch traitements failed', resp.status);
      return;
    }
    const data = await resp.json();
    if (Array.isArray(data)) {
      vm.treatmentRecords = data;
    } else if (data.traitements) {
      vm.treatmentRecords = data.traitements;
    }
    // persist locally for offline edits
    localStorage.setItem(treatmentStorageKey(vm), JSON.stringify(vm.treatmentRecords));
  } catch (e) {
    console.warn('Erreur fetch traitements', e);
  }
}
