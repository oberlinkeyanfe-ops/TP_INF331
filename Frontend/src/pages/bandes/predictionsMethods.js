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
