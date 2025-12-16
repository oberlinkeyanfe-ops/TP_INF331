// Fonctions liées à l'onglet Chatbot

export function getBotResponse(band) {
  const responses = [
    `Pour la bande "${band?.nom_bande || ''}", que souhaitez-vous savoir ?`,
    "Je peux vous aider à analyser les performances de votre bande.",
    "Consultez les prédictions pour voir les tendances futures."
  ];
  const randomResponse = responses[Math.floor(Math.random() * responses.length)];
  return randomResponse;
}
