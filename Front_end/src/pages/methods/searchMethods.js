// Méthodes liées à la recherche et suggestions

export function getSearchItems(vm) {
  return [
    { key: 'tab-dashboard', label: 'Aller Dashboard', type: 'Onglet', action: 'tab', tab: 'dashboard' },
    { key: 'tab-consommation', label: 'Consommation', type: 'Onglet', action: 'tab', tab: 'consommation', hint: 'Semaine, kg, eau' },
    { key: 'tab-predictions', label: 'Prédictions', type: 'Onglet', action: 'tab', tab: 'predictions', hint: 'Courbes prévisionnelles' },
    { key: 'tab-kpi', label: 'KPIs', type: 'Onglet', action: 'tab', tab: 'kpi', hint: 'Indicateurs clés' },
    { key: 'tab-traitements', label: 'Traitements', type: 'Onglet', action: 'tab', tab: 'traitements', hint: 'Catalogue + formulaire' },
    { key: 'tab-animaux', label: 'Animaux', type: 'Onglet', action: 'tab', tab: 'animaux', hint: 'Infos hebdo' },
    { key: 'tab-finances-dep', label: 'Finances - Dépenses', type: 'Onglet', action: 'tab', tab: 'finances', financeSubTab: 'depenses', hint: 'Cartes + tiroir' },
    { key: 'tab-finances-gains', label: 'Finances - Gains', type: 'Onglet', action: 'tab', tab: 'finances', financeSubTab: 'gains', hint: 'Ventes, subventions' },
    { key: 'tab-chatbot', label: 'Chatbot', type: 'Onglet', action: 'tab', tab: 'chatbot', hint: 'Assistant IA' },
    { key: 'tab-infos', label: 'Infos', type: 'Onglet', action: 'tab', tab: 'infos', hint: 'Détails de la bande' },
    { key: 'action-add-expense', label: 'Ajouter une dépense', type: 'Action', action: 'openExpense', hint: 'Ouvre le tiroir dépenses' },
    { key: 'action-add-treatment', label: 'Ajouter un traitement', type: 'Action', action: 'openTreatment', hint: 'Accéder au formulaire' }
  ];
}

export function updateSearchResults(vm) {
  const q = (vm.searchQuery || '').trim().toLowerCase();
  if (!q) {
    vm.searchResults = [];
    vm.searchFocusedIndex = 0;
    return;
  }
  const pool = getSearchItems(vm);
  vm.searchResults = pool
    .filter(item => item.label.toLowerCase().includes(q) || (item.hint && item.hint.toLowerCase().includes(q)))
    .slice(0, 8);
  vm.searchFocusedIndex = 0;
}

export function handleSearchKeydown(vm, evt) {
  if (!vm.searchResults.length) return;
  if (evt.key === 'ArrowDown') {
    evt.preventDefault();
    vm.searchFocusedIndex = (vm.searchFocusedIndex + 1) % vm.searchResults.length;
  } else if (evt.key === 'ArrowUp') {
    evt.preventDefault();
    vm.searchFocusedIndex = (vm.searchFocusedIndex - 1 + vm.searchResults.length) % vm.searchResults.length;
  } else if (evt.key === 'Enter') {
    evt.preventDefault();
    const target = vm.searchResults[vm.searchFocusedIndex];
    executeSearchResult(vm, target);
  } else if (evt.key === 'Escape') {
    closeSearch(vm, true);
  }
}

export function executeSearchResult(vm, item) {
  if (!item) return;
  if (item.action === 'tab') {
    vm.selectTab(item.tab);
    if (item.financeSubTab) vm.financeSubTab = item.financeSubTab;
  } else if (item.action === 'openExpense') {
    vm.financeSubTab = 'depenses';
    vm.selectTab('finances');
    vm.openExpenseDrawer(vm.expenseCatalog[0] || null);
  } else if (item.action === 'openTreatment') {
    vm.selectTab('traitements');
  }
  vm.searchResults = [];
  vm.searchQuery = '';
}

export function closeSearch(vm, clear = false) {
  setTimeout(() => {
    vm.searchResults = [];
    vm.searchFocusedIndex = 0;
    if (clear) vm.searchQuery = '';
  }, 100);
}
