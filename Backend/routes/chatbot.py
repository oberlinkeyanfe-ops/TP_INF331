from flask import Blueprint, request, jsonify, session, current_app
from modeles.models import db, MessageChatbot, Bande, Consommation, depense_elt, Traitement
from datetime import datetime
from sqlalchemy import func
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)

# Configuration Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
gemini_model = None

def init_gemini():
    """Initialise le modèle Gemini avec gestion des erreurs"""
    global gemini_model
    if not GEMINI_API_KEY or GEMINI_API_KEY == "votre_cle_api_ici":
        print("⚠️ Clé Gemini non configurée")
        return False
    
    try:
        print(f"🔧 Configuration Gemini avec clé: {GEMINI_API_KEY[:20]}...")
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Liste d'abord les modèles disponibles
        try:
            print("📋 Liste des modèles disponibles...")
            models = genai.list_models()
            
            available_models = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
                    print(f"  - {model.name}")
            
            # Essayer les modèles disponibles
            for model_name in available_models:
                if 'flash' in model_name.lower() or 'pro' in model_name.lower():
                    try:
                        print(f"🔄 Essai du modèle: {model_name}")
                        gemini_model = genai.GenerativeModel(model_name)
                        # Test rapide
                        test_response = gemini_model.generate_content("Test", generation_config={
                            'max_output_tokens': 1
                        })
                        print(f"✅ Modèle sélectionné: {model_name}")
                        return True
                    except Exception as e:
                        print(f"❌ Modèle {model_name} échoué: {str(e)[:100]}")
                        continue
            
        except Exception as list_error:
            print(f"❌ Erreur liste modèles: {list_error}")
        
        # Fallback: essayer les noms communs
        common_models = [
            'gemini-1.0-pro',
            'gemini-pro',
            'models/gemini-pro',
            'gemini-1.5-pro',
            'gemini-1.5-flash'
        ]
        
        for model_name in common_models:
            try:
                print(f"🔄 Essai modèle fallback: {model_name}")
                gemini_model = genai.GenerativeModel(model_name)
                test_response = gemini_model.generate_content("Test")
                print(f"✅ Modèle fallback réussi: {model_name}")
                return True
            except Exception as e:
                print(f"❌ Modèle fallback {model_name} échoué: {str(e)[:100]}")
                continue
        
        print("❌ Aucun modèle Gemini disponible")
        return False
        
    except Exception as e:
        print(f"❌ Erreur configuration Gemini: {e}")
        import traceback
        traceback.print_exc()
        return False

@chatbot_bp.before_request
def require_login():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

def get_donnees_eleveur(eleveur_id):
    """Récupère les données de l'éleveur"""
    try:
        bandes = Bande.query.filter_by(eleveur_id=eleveur_id).all()
        
        donnees = {
            'bandes': [],
            'statistiques': {
                'total_bandes': len(bandes),
                'bandes_actives': len([b for b in bandes if b.statut == 'active']),
                'total_animaux': sum(b.nombre_initial for b in bandes if b.nombre_initial)
            }
        }
        
        for bande in bandes:
            total_depenses = db.session.query(func.sum(depense_elt.cout)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            total_consommation = db.session.query(func.sum(Consommation.aliment_kg)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            traitements_count = Traitement.query.filter_by(bande_id=bande.id).count()
            
            donnees['bandes'].append({
                'id': bande.id,
                'nom': bande.nom_bande,
                'statut': bande.statut,
                'nombre_initial': bande.nombre_initial,
                'morts_totaux': bande.nombre_morts_totaux,
                'depenses_total': round(float(total_depenses), 2),
                'consommation_total': round(float(total_consommation), 2),
                'traitements_count': traitements_count
            })
        
        return donnees
    except Exception as e:
        return {'erreur': str(e)}

# ⭐ AJOUTEZ CETTE ROUTE POUR LES DEUX NOMS
@chatbot_bp.route('/analyse-complete', methods=['POST', 'OPTIONS'])
@chatbot_bp.route('/analyse_complete', methods=['POST', 'OPTIONS'])  # Compatibilité
def analyse_complete():
    """Analyse approfondie - supporte les deux noms"""
    print(f"🔍 Route appelée: {request.path}")
    
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        donnees_eleveur = get_donnees_eleveur(session['eleveur_id'])
        
        if 'erreur' in donnees_eleveur:
            return jsonify({'error': donnees_eleveur['erreur']}), 400
        
        # Formater le contexte
        contexte = "ANALYSE DE L'ÉLEVAGE\n\n"
        stats = donnees_eleveur.get('statistiques', {})
        contexte += f"STATISTIQUES:\n"
        contexte += f"- Total bandes: {stats.get('total_bandes', 0)}\n"
        contexte += f"- Bandes actives: {stats.get('bandes_actives', 0)}\n"
        contexte += f"- Total animaux: {stats.get('total_animaux', 0)}\n\n"
        
        if donnees_eleveur.get('bandes'):
            contexte += "DÉTAILS DES BANDES:\n"
            for bande in donnees_eleveur.get('bandes', []):
                taux_mortalite = (bande['morts_totaux'] / bande['nombre_initial'] * 100) if bande['nombre_initial'] > 0 else 0
                contexte += f"\nBande '{bande['nom']}':\n"
                contexte += f"  Statut: {bande['statut']}\n"
                contexte += f"  Animaux: {bande['nombre_initial']} initiaux\n"
                contexte += f"  Morts: {bande['morts_totaux']} ({taux_mortalite:.1f}%)\n"
                contexte += f"  Dépenses: {bande['depenses_total']} FCFA\n"
                contexte += f"  Consommation: {bande['consommation_total']} kg\n"
        
        # Initialiser Gemini
        global gemini_model
        if gemini_model is None:
            init_gemini()
        
        if gemini_model:
            try:
                prompt = f"""En tant qu'expert avicole, analyse ces données et donne des conseils.

{contexte}

Fournis une analyse utile en français avec:
1. Points forts
2. Points à améliorer  
3. Recommandations concrètes
4. Alertes si nécessaire"""
                
                response = gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.4,
                        'max_output_tokens': 10000,
                        'top_p': 0.95
                    }
                )
                analyse = response.text
                source = "gemini_ai"
                
            except Exception as gemini_error:
                print(f"❌ Erreur Gemini: {gemini_error}")
                analyse = f"""📊 **ANALYSE (Mode démo - Gemini erreur)**

{contexte}

**Erreur Gemini:** {str(gemini_error)[:100]}

**Conseils généraux:**
• Surveillez la santé quotidienne
• Adaptez l'alimentation à l'âge
• Maintenez l'hygiène"""
                source = "demo_error"
        else:
            analyse = f"""📊 **ANALYSE DE VOTRE ÉLEVAGE**

{contexte}

**CONSEILS GÉNÉRAUX:**
1. **Santé:** Vérifiez quotidiennement l'état des volailles
2. **Alimentation:** Adaptez la ration selon l'âge (starter, croissance, finition)
3. **Hygiène:** Nettoyez régulièrement les abreuvoirs et mangeoires
4. **Température:** Maintenez 20-25°C pour les adultes, 32-35°C pour les poussins

**PROCHAINE ÉTAPE:** 
Configurez Gemini API dans le fichier .env pour une analyse IA avancée."""
            source = "demo"
        
        return jsonify({
            'analyse': analyse,
            'statistiques': stats,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'route_utilisee': request.path
        })
        
    except Exception as e:
        print(f"❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Route ask simplifiée
@chatbot_bp.route('/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        data = request.get_json()
        message = (data.get('message') or '').strip()
        mode = (data.get('mode') or 'data').lower()
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Initialiser Gemini
        global gemini_model
        if gemini_model is None:
            init_gemini()
        
        if gemini_model:
            try:
                prompt = f"""Assistant avicole - Question: {message}
                
Réponds en français avec des conseils pratiques et utiles."""
                
                response = gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.7,
                        'max_output_tokens': 10000
                    }
                )
                reponse = response.text
            except Exception as e:
                reponse = f"Réponse (mode démo): {message}\n\nPour des réponses IA, vérifiez la configuration Gemini."
        else:
            reponse = f"Mode: {mode}\nQuestion: {message}\n\n(Assistant en mode démo - Gemini non configuré)"
        
        # Sauvegarder
        message_chat = MessageChatbot(
            eleveur_id=session['eleveur_id'],
            message_utilisateur=message,
            reponse_bot=reponse,
            mode_utilise=mode
        )
        db.session.add(message_chat)
        db.session.commit()
        
        return jsonify({
            'reponse': reponse,
            'mode': mode
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur /ask: {e}")
        return jsonify({'error': str(e)}), 500

# Routes existantes...
@chatbot_bp.route('/historique', methods=['GET'])
def get_historique():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        historique = MessageChatbot.query.filter_by(
            eleveur_id=session['eleveur_id']
        ).order_by(MessageChatbot.date_message.desc()).limit(20).all()
        
        return jsonify([{
            'id': msg.id,
            'message_utilisateur': msg.message_utilisateur,
            'reponse_bot': msg.reponse_bot,
            'mode_utilise': msg.mode_utilise or 'data',
            'date_message': msg.date_message.isoformat() if msg.date_message else None
        } for msg in historique])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@chatbot_bp.route('/statistiques-chatbot', methods=['GET'])
def get_chatbot_stats():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        total_messages = MessageChatbot.query.filter_by(
            eleveur_id=session['eleveur_id']
        ).count()
        
        return jsonify({
            'total_messages': total_messages,
            'gemini_configure': bool(GEMINI_API_KEY and GEMINI_API_KEY != "votre_cle_api_ici"),
            'gemini_model_loaded': gemini_model is not None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@chatbot_bp.route('/debug', methods=['GET'])
def debug_info():
    """Info de débogage"""
    return jsonify({
        'status': 'ok',
        'session': dict(session),
        'gemini': {
            'api_key_set': bool(GEMINI_API_KEY),
            'model_loaded': gemini_model is not None,
            'available': GEMINI_API_KEY is not None
        },
        'routes': [
            '/chatbot/ask (POST)',
            '/chatbot/analyse-complete (POST)',
            '/chatbot/analyse_complete (POST)',
            '/chatbot/historique (GET)',
            '/chatbot/statistiques-chatbot (GET)'
        ]
    })