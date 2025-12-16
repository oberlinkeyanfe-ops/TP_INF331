// Fonctions liées à l'onglet Consommation

export function formatDate(dateString) {
  if (!dateString) return '—';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR');
}

// Ajoutez ici d'autres méthodes spécifiques à la consommation
