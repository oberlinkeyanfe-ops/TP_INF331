def generer_reponse_ai(message_utilisateur: str) -> str:
    """Simule une réponse intelligente du chatbot."""
    message_utilisateur = message_utilisateur.lower()
    if "bonjour" in message_utilisateur:
        return "Bonjour 👋 ! Comment puis-je vous aider dans la gestion de votre élevage ?"
    elif "alimentation" in message_utilisateur:
        return "Pensez à ajuster la ration selon l’âge de vos volailles. Voulez-vous une estimation ?"
    elif "mortalité" in message_utilisateur:
        return "Le taux de mortalité acceptable est généralement inférieur à 5%. Souhaitez-vous voir vos statistiques ?"
    else:
        return "Je suis là pour vous aider à suivre vos bandes, vos coûts et vos prédictions. Posez-moi une question !"
