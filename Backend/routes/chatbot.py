from flask import Blueprint, request, jsonify, session, current_app
from modeles.models import db, MessageChatbot, Bande, Consommation, depense_elt, Traitement, AnimalInfo
from datetime import datetime
from sqlalchemy import func
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import requests
import re

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
        # Avoid printing API key to logs for security reasons
        print("🔧 Configuration Gemini (clé fournie)")
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
                        print(f" Essai du modèle: {model_name}")
                        gemini_model = genai.GenerativeModel(model_name)
                        # Test rapide
                        test_response = gemini_model.generate_content("Test", generation_config={
                            'max_output_tokens': 1
                        })
                        print(f" Modèle sélectionné: {model_name}")
                        return True
                    except Exception as e:
                        print(f" Modèle {model_name} échoué: {str(e)[:100]}")
                        continue
            
        except Exception as list_error:
            print(f" Erreur liste modèles: {list_error}")
        
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


# -- Simple web search helper (DuckDuckGo HTML) --
def web_search(query, limit=3):
    """Perform a simple DuckDuckGo search and return a list of snippets.
    Lightweight: no external API key required. Returns up to `limit` results.
    """
    try:
        resp = requests.post('https://html.duckduckgo.com/html/', data={'q': query}, timeout=6)
        html = resp.text
        # find results: <a class="result__a" href="...">Title</a>
        titles = re.findall(r'<a[^>]+class="result__a"[^>]+>(.*?)</a>', html, flags=re.S)
        urls = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"', html, flags=re.S)
        snippets = re.findall(r'<div[^>]+class="result__snippet"[^>]*>(.*?)</div>', html, flags=re.S)

        results = []
        for i in range(min(limit, len(titles))):
            t = re.sub(r'<.*?>', '', titles[i]).strip()
            s = re.sub(r'<.*?>', '', snippets[i]).strip() if i < len(snippets) else ''
            u = urls[i] if i < len(urls) else ''
            results.append({'title': t, 'snippet': s, 'url': u})
        return results
    except Exception as e:
        print('Erreur web_search:', e)
        return []


# --- Local fallback analyzer (used when Gemini is unavailable or quota exceeded) ---
def local_analysis_from_data(donnees_eleveur, web_results=None):
    """Generate a concise analysis and recommendations from internal data + optional web snippets.
    This is deterministic and useful as a graceful fallback when Gemini is not usable.
    """
    try:
        stats = donnees_eleveur.get('statistiques', {})
        lines = []
        lines.append("ANALYSE LOCALE DE VOTRE ÉLEVAGE:\n")
        lines.append(f"Total bandes: {stats.get('total_bandes',0)} | Bandes actives: {stats.get('bandes_actives',0)} | Total animaux: {stats.get('total_animaux',0)}\n")

        # detect bands with high mortality or low population
        high_mortality = []
        for b in donnees_eleveur.get('bandes', []):
            nombre_initial = b.get('nombre_initial') or 0
            morts = b.get('morts_totaux') or 0
            taux = (morts / nombre_initial * 100) if nombre_initial > 0 else 0
            cons = b.get('consommation_total') or 0
            lines.append(f"Bande {b.get('nom')} (id:{b.get('id')}): statut={b.get('statut')}, initiaux={nombre_initial}, morts={morts} ({taux:.1f}%), consommation={cons} kg")
            if taux >= 5.0:
                high_mortality.append({'id': b.get('id'), 'nom': b.get('nom'), 'taux': taux})

        lines.append('\nSynthèse rapide:')
        if high_mortality:
            lines.append(f"- ALERT: {len(high_mortality)} bande(s) ont un taux de mortalité élevé (>5%): {', '.join([h['nom'] for h in high_mortality])}.")
        else:
            lines.append("- Aucun taux de mortalité critique détecté (seuil 5%).")

        lines.append('\nRecommandations pratiques:')
        lines.append("1) Vérifiez hygiène et contrôle sanitaire immédiat des bandes affectées; isolez si nécessaire.")
        lines.append("2) Vérifiez distribution d'eau et qualité de l'alimentation; ajustez les rations si consommation anormale.")
        lines.append("3) Considérez la vaccination ou l'avis vétérinaire pour les cas suspects.")
        lines.append("4) Suivi: enregistrez poids moyen et mortalité chaque semaine et comparez aux références.")

        if web_results:
            lines.append('\nRéférences web utilisées (extraits):')
            for r in web_results[:3]:
                lines.append(f"- {r.get('title')} — {r.get('url')}")

        lines.append('\nNotes: pour une analyse plus poussée, configurez l’API Gemini avec quota/billing ou utilisez le mode hybrid/web.')

        return '\n'.join(lines)
    except Exception as e:
        print('Erreur local_analysis_from_data:', e)
        return 'Analyse locale indisponible, réessayez plus tard.'

@chatbot_bp.before_request
def require_login():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

def get_donnees_eleveur(eleveur_id):
    """Récupère les données complètes de l'éleveur, incluant des séries temporelles et les dernières entrées par bande."""
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
            total_depenses = db.session.query(func.coalesce(func.sum(depense_elt.cout), 0)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            total_consommation = db.session.query(func.coalesce(func.sum(Consommation.aliment_kg), 0)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            traitements_count = Traitement.query.filter_by(bande_id=bande.id).count()

            # Dernières entrées (exemples utiles pour l'analyse)
            dernieres_consommations = Consommation.query.filter_by(bande_id=bande.id).order_by(Consommation.date.desc()).limit(5).all()
            dernieres_traitements = Traitement.query.filter_by(bande_id=bande.id).order_by(Traitement.date.desc()).limit(5).all()
            dernieres_animal_info = AnimalInfo.query.filter_by(bande_id=bande.id).order_by(AnimalInfo.semaine_production.desc()).limit(6).all()

            donnees['bandes'].append({
                'id': bande.id,
                'nom': bande.nom_bande,
                'statut': bande.statut,
                'nombre_initial': bande.nombre_initial,
                'morts_totaux': bande.nombre_morts_totaux,
                'depenses_total': round(float(total_depenses), 2),
                'consommation_total': round(float(total_consommation), 2),
                'traitements_count': traitements_count,
                'dernieres_consommations': [c.to_dict() for c in dernieres_consommations],
                'dernieres_traitements': [t.to_dict() for t in dernieres_traitements],
                'dernieres_animal_info': [a.to_dict() for a in dernieres_animal_info]
            })
        
        return donnees
    except Exception as e:
        return {'erreur': str(e)}

#  AJOUTEZ CETTE ROUTE POUR LES DEUX NOMS
@chatbot_bp.route('/analyse-complete', methods=['POST', 'OPTIONS'])
@chatbot_bp.route('/analyse_complete', methods=['POST', 'OPTIONS'])  # Compatibilité
def analyse_complete():
    """Analyse approfondie - supporte les deux noms"""
    print(f"🔍 Route appelée: {request.path}")
    
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # parse payload and mode
        payload = request.get_json(silent=True) or {}
        mode = (payload.get('mode') or request.args.get('mode') or 'data').lower()
        user_query = payload.get('query')

        # Collecte données internes
        donnees_eleveur = get_donnees_eleveur(session['eleveur_id'])
        if 'erreur' in donnees_eleveur:
            return jsonify({'error': donnees_eleveur['erreur']}), 400

        # Formater le contexte interne (statistiques + détails par bande)
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
        
        # Initialiser Gemini si disponible
        global gemini_model
        if gemini_model is None:
            init_gemini()

        # Préparer une recherche web si le mode le demande
        web_results = None
        if mode in ['hybrid', 'web']:
            q = user_query or f"conseils élevage poules alimentation mortalité hygiène"
            web_results = web_search(q, limit=5)

        # Mode web -> utiliser uniquement les extraits web
        if mode == 'web':
            contexte_web = "CONTEXT (WEB SEARCH):\n"
            for r in (web_results or []):
                contexte_web += f"- {r.get('title')}: {r.get('snippet')} ({r.get('url')})\n"

            if gemini_model:
                try:
                    prompt = f"En tant qu'expert avicole, en te basant uniquement sur les extraits web suivants, fournis une analyse et des recommandations pratiques:\n\n{contexte_web}\nRéponds en français, structure ta réponse: 1) Points forts, 2) Points à améliorer, 3) Recommandations, 4) Alertes." 
                    response = gemini_model.generate_content(prompt, generation_config={'temperature': 0.4, 'max_output_tokens': 4000})
                    analyse = response.text
                    source = 'gemini_web'
                except Exception as e:
                    print('Erreur Gemini web mode:', e)
                    analyse = f"**ANALYSE (Mode Web - démo)**\n{contexte_web}\n(Erreur Gemini: {str(e)[:120]})"
                    source = 'demo_web_error'
            else:
                analyse = f"**ANALYSE WEB (démo)**\n{contexte_web}\nConseils généraux: surveillez la santé, adaptez l'alimentation et maintenez l'hygiène." 
                source = 'demo_web'

        else:
            # modes 'data' ou 'hybrid' -> on inclut les données internes
            # pour 'hybrid' on ajoute également les extraits web en référence
            contexte_final = contexte
            if mode == 'hybrid' and web_results:
                contexte_final += "\n\nRÉFÉRENCES WEB:\n"
                for r in web_results:
                    contexte_final += f"- {r.get('title')}: {r.get('snippet')} ({r.get('url')})\n"

            if gemini_model:
                try:
                    prompt = f"En tant qu'expert avicole, analyse ces données et donne des conseils utiles en français. Concentre-toi sur des recommandations pratiques et des alertes si nécessaire.\n\n{contexte_final}\n\nRéponds avec: 1) Points forts, 2) Points à améliorer, 3) Recommandations concrètes, 4) Alertes si nécessaire."
                    response = gemini_model.generate_content(prompt, generation_config={'temperature': 0.4, 'max_output_tokens': 8000})
                    analyse = response.text
                    source = 'gemini_hybrid' if mode == 'hybrid' else 'gemini_data'
                except Exception as gemini_error:
                    # Detect quota / rate-limit errors and fallback to local analysis
                    err_str = str(gemini_error).lower()
                    print(f"Erreur Gemini (analyse): {gemini_error}")
                    if 'quota' in err_str or 'exceed' in err_str or '429' in err_str:
                        print('Gemini quota exceeded or rate-limited, using local fallback analysis')
                        analyse = local_analysis_from_data(donnees_eleveur, web_results=(web_results if mode=='hybrid' else None))
                        source = 'local_fallback_quota'
                    else:
                        analyse = f" **ANALYSE (Mode démo - Gemini erreur)**\n\n{contexte_final}\n\n**Erreur Gemini:** {str(gemini_error)[:100]}\n\n**Conseils généraux:**\n• Surveillez la santé quotidienne\n• Adaptez l'alimentation à l'âge\n• Maintenez l'hygiène"
                        source = 'demo_error'
            else:
                analyse = f" **ANALYSE DE VOTRE ÉLEVAGE (démo)**\n\n{contexte_final}\n\n**CONSEILS GÉNÉRAUX:**\n1. **Santé:** Vérifiez quotidiennement l'état des volailles\n2. **Alimentation:** Adaptez la ration selon l'âge (starter, croissance, finition)\n3. **Hygiène:** Nettoyez régulièrement les abreuvoirs et mangeoires\n4. **Température:** Maintenez des conditions appropriées\n\n**PROCHAINE ÉTAPE:** Configurez GEMINI_API_KEY pour une analyse IA avancée."
                source = 'demo'

        # Sauvegarder un enregistrement rapide de l'analyse
        try:
            message_chat = MessageChatbot(
                eleveur_id=session['eleveur_id'],
                message_utilisateur=f'ANALYSE_COMPLETE (mode={mode})',
                reponse_bot=(analyse[:4000] if analyse else ''),
                mode_utilise=mode
            )
            db.session.add(message_chat)
            db.session.commit()
        except Exception as e:
            print('Erreur sauvegarde message_chat:', e)
            db.session.rollback()

        return jsonify({
            'analyse': analyse,
            'statistiques': stats,
            'donnees': donnees_eleveur if mode in ['data', 'hybrid'] else {},
            'web_results': web_results if web_results else [],
            'source': source,
            'mode': mode,
            'timestamp': datetime.now().isoformat(),
            'route_utilisee': request.path
        })
        
    except Exception as e:
        print(f" Erreur globale: {e}")
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

        # optionally perform web search for hybrid/web modes
        web_results = None
        if mode in ['hybrid', 'web']:
            try:
                web_results = web_search(message, limit=4)
            except Exception as e:
                print('Erreur web_search dans /ask:', e)
                web_results = None

        # build prompt according to mode
        if gemini_model:
            try:
                if mode == 'web':
                    snippets = "\n".join([f"- {r.get('title')}: {r.get('snippet')}" for r in (web_results or [])])
                    prompt = f"Assistant avicole (mode: web). Utilise uniquement ces extraits web comme référence:\n{snippets}\n\nQuestion: {message}\nRéponds en français avec conseils pratiques."
                elif mode == 'hybrid':
                    # include a lightweight internal summary
                    try:
                        donnees = get_donnees_eleveur(session['eleveur_id'])
                        stats = donnees.get('statistiques', {})
                        internal = f"Total bandes: {stats.get('total_bandes',0)}, Bandes actives: {stats.get('bandes_actives',0)}, Total animaux: {stats.get('total_animaux',0)}"
                    except Exception:
                        internal = ''
                    snippets = "\n".join([f"- {r.get('title')}: {r.get('snippet')}" for r in (web_results or [])])
                    prompt = f"Assistant avicole (mode: hybrid). Données internes: {internal}\nRéférences web:\n{snippets}\n\nQuestion: {message}\nRéponds en français de façon utile et concrète."
                else:
                    # data mode: use only internal context
                    try:
                        donnees = get_donnees_eleveur(session['eleveur_id'])
                        stats = donnees.get('statistiques', {})
                        internal = f"Total bandes: {stats.get('total_bandes',0)}, Bandes actives: {stats.get('bandes_actives',0)}, Total animaux: {stats.get('total_animaux',0)}"
                    except Exception:
                        internal = ''
                    prompt = f"Assistant avicole (mode: data). Contexte interne: {internal}\nQuestion: {message}\nRéponds en français avec des conseils pratiques et concrets."

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
            # fallback message
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