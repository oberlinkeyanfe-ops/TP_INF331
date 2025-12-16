// Fonctions liées à l'onglet Animaux

// Ajoutez ici les méthodes spécifiques à la gestion des animaux

export function getAnimalDisplayName(animal) {
  return animal.nom || `#${animal.id}`;
}

export async function loadAnimalInfos(vm) {
  try {
    if (!vm.id) return;
    const url = `http://localhost:5000/animal-info/bande/${vm.id}`;
    const response = await fetch(url, { credentials: 'include' });
    if (!response.ok) { vm.animalInfos = []; return; }
    const data = await response.json();
    vm.animalInfos = (data.animal_info || []).map(info => ({ ...info, morts_semaine: info.morts_semaine || 0 })).sort((a,b) => (a.semaine_production||0)-(b.semaine_production||0));
    if (!vm.editingAnimalInfoId) vm.resetAnimalInfoForm();
  } catch (error) {
    console.warn('❌ Erreur loadAnimalInfos:', error);
    vm.animalInfos = [];
  }
}

export function resetAnimalInfoForm(vm) {
  vm.editingAnimalInfoId = null;
  vm.animalInfoForm = { semaine_production: vm.nextAnimalWeek, poids_moyen: null, morts_semaine: 0, animaux_restants: vm.survivorsCount || null, note: '' };
}

export function startEditAnimalInfo(vm, info) {
  if (!info) return;
  vm.editingAnimalInfoId = info.id;
  vm.animalInfoForm = { semaine_production: info.semaine_production, poids_moyen: info.poids_moyen, morts_semaine: info.morts_semaine || 0, animaux_restants: info.animaux_restants, note: info.note || '' };
}

export async function saveAnimalInfo(vm) {
  try {
    if (!vm.id) {
      alert("Veuillez d'abord sélectionner une bande");
      return;
    }

    const isEditing = !!vm.editingAnimalInfoId;
    const week = vm.animalInfoForm.semaine_production || vm.nextAnimalWeek;

    const duplicateWeek = (vm.animalInfos || []).some(info => (
      info.semaine_production === week && info.id !== vm.editingAnimalInfoId
    ));
    if (duplicateWeek) {
      alert(`Une entrée existe déjà pour la semaine ${week}.`);
      return;
    }

    const note = vm.animalInfoForm && vm.animalInfoForm.note ? vm.animalInfoForm.note.trim() : null;
    const payload = {
      bande_id: parseInt(vm.id, 10),
      semaine_production: week,
      poids_moyen: vm.animalInfoForm.poids_moyen || null,
      morts_semaine: vm.animalInfoForm.morts_semaine || 0,
      animaux_restants: vm.animalInfoForm.animaux_restants,
      note: note
    };

    const url = isEditing ? `http://localhost:5000/animal-info/${vm.editingAnimalInfoId}` : 'http://localhost:5000/animal-info/';
    const method = isEditing ? 'PUT' : 'POST';

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(data.error || 'Erreur lors de la sauvegarde');
      return;
    }

    if (isEditing) {
      const idx = (vm.animalInfos || []).findIndex(i => i.id === vm.editingAnimalInfoId);
      if (idx !== -1) vm.animalInfos.splice(idx, 1, data);
      alert('Semaine mise à jour');
    } else {
      vm.animalInfos.push(data);
      alert('Semaine ajoutée');
    }

    vm.animalInfos.sort((a, b) => (a.semaine_production || 0) - (b.semaine_production || 0));
    vm.resetAnimalInfoForm();
  } catch (error) {
    console.error('saveAnimalInfo error:', error);
    alert('Impossible de sauvegarder les données animaux');
  }
}

export async function deleteAnimalInfo(vm, info) {
  if (!info?.id) return; if (!confirm('Supprimer cette semaine ?')) return;
  try {
    const response = await fetch(`http://localhost:5000/animal-info/${info.id}`, { method: 'DELETE', credentials: 'include' });
    if (!response.ok) { const err = await response.json().catch(()=>({})); alert(`❌ ${err.error || 'Suppression impossible'}`); return; }
    vm.animalInfos = vm.animalInfos.filter(i => i.id !== info.id);
    vm.resetAnimalInfoForm();
    alert('🗑️ Enregistrement supprimé');
  } catch (error) { console.error('❌ deleteAnimalInfo error:', error); alert('❌ Erreur lors de la suppression'); }
}

export function calculateWeeklyMortalityRate(vm, info) {
  const initial = vm.band?.nombre_initial || 0; if (!initial) return 0; const morts = info?.morts_semaine || 0; return parseFloat(((morts / initial) * 100).toFixed(2));
}

export function getMortalityRef(vm, week) { return vm.mortalityReference.find(ref => ref.week === week) || { low: 0, high: 0 }; }
export function getWeightRef(vm, week) { return vm.weightReference.find(ref => ref.week === week) || { low: null, high: null }; }
export function weightRefDisplay(vm, week) { const ref = getWeightRef(vm, week); if (ref.low === null || ref.high === null) return ''; return `${ref.low.toFixed(2)} - ${ref.high.toFixed(2)}`; }
export function mortalityRefDisplay(vm, week) { const ref = getMortalityRef(vm, week); return `${ref.low}% - ${ref.high}%`; }
