// Fonctions liées à l'onglet Animaux

// Ajoutez ici les méthodes spécifiques à la gestion des animaux

export function getAnimalDisplayName(animal) {
  return animal.nom || `#${animal.id}`;
}
