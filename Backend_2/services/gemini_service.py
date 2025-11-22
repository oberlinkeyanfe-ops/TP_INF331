# services/gemini_service.py - NOUVEAU FICHIER
import google.generativeai as genai
import os
from modeles.models import db, Bande, Consommation, Depense, Traitement

class GeminiService:
    def __init__(self):
        self.api_key = "VOTRE_CLE_API_GEMINI"  # À mettre dans les variables d'environnement
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyser_question(self, question, eleveur_id):
        """Analyse la question et récupère les données pertinentes"""
        
        # 1. Extraire les paramètres avec Gemini
        prompt_analyse = f"""
        Analyse cette question d'élevage et extrait:
        - bande_id (numéro de bande)
        - période (semaine, mois, aujourd'hui)
        - type_donnees (dépenses, consommation, traitement, mortalité)
        - métrique (total, moyenne, comparaison)
        
        Question: "{question}"
        
        Réponds en JSON uniquement.
        """
        
        try:
            response = self.model.generate_content(prompt_analyse)
            # Ici parser la réponse JSON
        except Exception as e:
            return {"error": str(e)}
        
        # 2. Récupérer les données selon l'analyse
        donnees = self.recuperer_donnees_bande(eleveur_id, bande_id, periode, type_donnees)
        
        # 3. Générer réponse naturelle
        return self.generer_reponse(question, donnees)
    
    def recuperer_donnees_bande(self, eleveur_id, bande_id, periode, type_donnees):
        """Récupère les données de la base selon les critères"""
        donnees = {}
        
        if type_donnees in ['dépenses', 'coût']:
            depenses = Depense.query.filter_by(bande_id=bande_id).all()
            donnees['depenses'] = [d.to_dict() for d in depenses]
            donnees['total_depenses'] = sum(d.montant for d in depenses)
        
        if type_donnees in ['consommation', 'alimentation']:
            consommations = Consommation.query.filter_by(bande_id=bande_id).all()
            donnees['consommations'] = [c.to_dict() for c in consommations]
            donnees['total_aliment'] = sum(c.aliment_kg for c in consommations)
        
        return donnees
    
    def generer_reponse(self, question, donnees):
        """Génère une réponse naturelle avec Gemini"""
        prompt_reponse = f"""
        En tant qu'assistant pour un éleveur de poulets, réponds à cette question de manière claire et utile.
        
        Question: {question}
        
        Données disponibles:
        {donnees}
        
        Donne une réponse concise en français qui résume les informations importantes.
        Sois précis et utilise les chiffres disponibles.
        """
        
        response = self.model.generate_content(prompt_reponse)
        return response.text