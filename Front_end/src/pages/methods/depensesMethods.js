// Méthodes liées aux dépenses (depenses / expense drawer)

export function openExpenseDrawer(vm, item) {
  vm.expenseSelected = item;
  vm.expenseForm.tache = item?.name || '';
  vm.expenseDrawerOpen = true;
}

export function closeExpenseDrawer(vm) {
  vm.expenseDrawerOpen = false;
  vm.expenseSelected = null;
}

export function expenseStorageKey(vm) {
  return `expenses_${vm.id || 'default'}`;
}

export function loadExpenseRecordsFromStorage(vm) {
  try {
    const raw = localStorage.getItem(expenseStorageKey(vm));
    vm.expenseRecords = raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.warn('Erreur chargement dépenses locales', e);
    vm.expenseRecords = [];
  }
}

export async function fetchExpenseRecordsFromServer(vm) {
  try {
    if (!vm.id) return;
    const resp = await fetch(`http://localhost:5000/depenses/bande/${vm.id}`, { credentials: 'include' });
    if (!resp.ok) {
      console.warn('Fetch depenses failed', resp.status);
      return;
    }
    const data = await resp.json();
    if (Array.isArray(data)) {
      vm.expenseRecords = data;
    } else if (data.depenses) {
      vm.expenseRecords = data.depenses;
    }
    localStorage.setItem(expenseStorageKey(vm), JSON.stringify(vm.expenseRecords));
  } catch (e) {
    console.warn('Erreur fetch depenses', e);
  }
}

export function saveExpense(vm) {
  if (!vm.expenseForm.tache || !vm.expenseForm.date || !vm.expenseForm.montant) return;
  const payload = { ...vm.expenseForm, montant: Number(vm.expenseForm.montant), label: vm.expenseForm.tache, id: crypto.randomUUID() };
  vm.expenseRecords = [payload, ...vm.expenseRecords].slice(0, 30);
  localStorage.setItem(expenseStorageKey(vm), JSON.stringify(vm.expenseRecords));
  closeExpenseDrawer(vm);
}

export function getExpenseImage(vm, pathOrName) {
  const match = vm.expenseCatalog.find(e => e.name === pathOrName) || vm.expenseCatalog.find(e => e.image === pathOrName);
  const path = match && match.image ? match.image : pathOrName;
  try {
    // normalize relative paths: when paths like "../assets/..." are passed from a component
    // this file is in src/pages/methods so assets are one level up further -> '../../assets/...'
    let resolved = path;
    if (typeof path === 'string' && path.startsWith('../assets/')) {
      resolved = path.replace(/^\.\.\/assets\//, '../../assets/');
    }
    return new URL(resolved, import.meta.url).href;
  } catch (e) {
    return vm.medocPlaceholder;
  }
}
