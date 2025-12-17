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

export async function analyserElevage(vm) {
  try {
    vm.chatLoading = true;
    const response = await fetch('http://localhost:5000/chatbot/analyse_complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ mode: vm.chatMode })
    });

    if (!response.ok) {
      if (response.status === 404) throw new Error("Le service d'analyse n'est pas disponible.");
      throw new Error(`Erreur ${response.status}`);
    }

    const data = await response.json();
    vm.messages.push({ from: 'bot', text: data.analyse || 'Analyse non disponible' });

    // If web results were returned (hybrid/web modes), display a brief summary
    if (data.web_results && Array.isArray(data.web_results) && data.web_results.length) {
      const sources = data.web_results.slice(0,3).map(r => `• ${r.title} — ${r.url}`).join('\n');
      vm.messages.push({ from: 'bot', text: `Sources web utilisées:\n${sources}` });
    }
  } catch (error) {
    console.error('Erreur analyse:', error);
    vm.messages.push({ from: 'bot', text: `⚠️ Erreur: ${error.message}` });
  } finally {
    vm.chatLoading = false;
  }
}

export async function sendMessage(vm) {
  if (!vm.chatInput || !vm.chatInput.trim()) return;
  const message = vm.chatInput.trim();
  vm.messages.push({ from: 'user', text: message });
  vm.chatInput = '';
  vm.chatLoading = true;

  try {
    const response = await fetch('http://localhost:5000/chatbot/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ message, mode: vm.chatMode })
    });
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    vm.messages.push({ from: 'bot', text: data.reponse });
  } catch (error) {
    console.error('Erreur chatbot:', error);
    vm.messages.push({ from: 'bot', text: `Erreur: ${error.message}` });
  } finally {
    vm.chatLoading = false;
  }
}
