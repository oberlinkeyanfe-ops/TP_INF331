from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from modeles.models import db, MessageChatbot, Bande, Consommation, Depense, Traitement
from datetime import datetime, timedelta
from sqlalchemy import func
import json

chatbot_bp = Blueprint('chatbot', __name__)

def get_donnees_eleveur(eleveur_id):
    """Récupère les données de l'éleveur pour le contexte"""
    try:
        bandes = Bande.query.filter_by(eleveur_id=eleveur_id).all()
        donnees = {
            'bandes': [],
            'statistiques': {
                'total_bandes': len(bandes),
                'bandes_actives': len([b for b in bandes if b.statut == 'active']),
                'total_animaux': sum(b.nombre_initial for b in bandes)
            }
        }
        
        for bande in bandes:
            # Dépenses de la bande
            total_depenses = db.session.query(func.sum(Depense.montant)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            # Consommation de la bande
            total_consommation = db.session.query(func.sum(Consommation.aliment_kg)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            # Traitements de la bande
            traitements_count = Traitement.query.filter_by(bande_id=bande.id).count()
            
            donnees['bandes'].append({
                'id': bande.id,
                'nom': bande.nom_bande,
                'statut': bande.statut,
                'nombre_initial': bande.nombre_initial,
                'morts_totaux': bande.nombre_morts_totaux,
                'depenses_total': round(total_depenses, 2),
                'consommation_total': round(total_consommation, 2),
                'traitements_count': traitements_count
            })
        
        return donnees
    except Exception as e:
        return {'erreur': str(e)}

def analyser_question_manuelle(question, donnees_eleveur):
    """Analyse manuelle de la question sans Gemini"""
    question_lower = question.lower()
    
    # Détection des mots-clés
    if any(mot in question_lower for mot in ['bonjour', 'salut', 'hello', 'coucou']):
        return "👋 Bonjour ! Je suis votre assistant avicole. Comment puis-je vous aider aujourd'hui ?"
    
    elif any(mot in question_lower for mot in ['coût', 'dépense', 'prix', 'cout']):
        return analyser_couts(question_lower, donnees_eleveur)
    
    elif any(mot in question_lower for mot in ['consommation', 'aliment', 'nourriture', 'manger']):
        return analyser_consommation(question_lower, donnees_eleveur)
    
    elif any(mot in question_lower for mot in ['traitement', 'médicament', 'vaccin', 'santé']):
        return analyser_traitements(question_lower, donnees_eleveur)
    
    elif any(mot in question_lower for mot in ['bande', 'poulet', 'volaille']):
        return analyser_bandes(question_lower, donnees_eleveur)
    
    elif any(mot in question_lower for mot in ['merci', 'ok', 'daccord']):
        return "😊 Je vous en prie ! N'hésitez pas si vous avez d'autres questions."
    
    else:
        return "🤔 Je ne suis pas sûr de comprendre votre question. Pouvez-vous la reformuler ?\n\n" \
               "Je peux vous aider avec :\n" \
               "• Les **coûts et dépenses** de vos bandes\n" \
               "• La **consommation** d'aliment et d'eau\n" \
               "• Les **traitements** et la santé\n" \
               "• Les **performances** de vos bandes\n\n" \
               "Essayez par exemple : 'Quel est le coût de la bande 1 ?'"

def analyser_couts(question, donnees):
    """Analyse les questions sur les coûts"""
    if 'total' in question:
        total_depenses = sum(b['depenses_total'] for b in donnees['bandes'])
        return f"💰 **Dépenses totales de toutes vos bandes :** {total_depenses:,.2f} FCFA\n\n" \
               f"📊 Répartition par bande :\n" + \
               "\n".join([f"• {b['nom']} : {b['depenses_total']:,.2f} FCFA" for b in donnees['bandes']])
    
    # Détection du numéro de bande
    for bande in donnees['bandes']:
        if f"bande {bande['id']}" in question or bande['nom'].lower() in question:
            return f"💰 **Dépenses de la bande {bande['nom']} :** {bande['depenses_total']:,.2f} FCFA\n\n" \
                   f"📈 Coût par animal : {bande['depenses_total']/bande['nombre_initial']:,.2f} FCFA" \
                   if bande['nombre_initial'] > 0 else "Aucun animal dans cette bande"
    
    return "💰 **Vos dépenses :**\n\n" + \
           "\n".join([f"• {b['nom']} : {b['depenses_total']:,.2f} FCFA" for b in donnees['bandes']])

def analyser_consommation(question, donnees):
    """Analyse les questions sur la consommation"""
    if 'total' in question:
        total_consommation = sum(b['consommation_total'] for b in donnees['bandes'])
        return f"🍗 **Consommation totale d'aliment :** {total_consommation:,.2f} kg\n\n" \
               f"📊 Répartition par bande :\n" + \
               "\n".join([f"• {b['nom']} : {b['consommation_total']:,.2f} kg" for b in donnees['bandes']])
    
    # Détection du numéro de bande
    for bande in donnees['bandes']:
        if f"bande {bande['id']}" in question or bande['nom'].lower() in question:
            return f"🍗 **Consommation de la bande {bande['nom']} :** {bande['consommation_total']:,.2f} kg\n\n" \
                   f"📈 Consommation par animal : {bande['consommation_total']/bande['nombre_initial']:.2f} kg" \
                   if bande['nombre_initial'] > 0 else "Aucun animal dans cette bande"
    
    return "🍗 **Consommation d'aliment :**\n\n" + \
           "\n".join([f"• {b['nom']} : {b['consommation_total']:,.2f} kg" for b in donnees['bandes']])

def analyser_traitements(question, donnees):
    """Analyse les questions sur les traitements"""
    total_traitements = sum(b['traitements_count'] for b in donnees['bandes'])
    
    if 'récents' in question or 'derniers' in question:
        return f"💊 **Traitements récents :** {total_traitements} traitements au total\n\n" \
               f"📊 Répartition par bande :\n" + \
               "\n".join([f"• {b['nom']} : {b['traitements_count']} traitements" for b in donnees['bandes']])
    
    return f"💊 **Statistiques des traitements :**\n\n" \
           f"• Total des traitements : {total_traitements}\n" + \
           "\n".join([f"• {b['nom']} : {b['traitements_count']} traitements" for b in donnees['bandes']])

def analyser_bandes(question, donnees):
    """Analyse les questions sur les bandes"""
    bandes_actives = [b for b in donnees['bandes'] if b['statut'] == 'active']
    
    if 'active' in question or 'actuelle' in question:
        return f"🏷️ **Bandes actives :** {len(bandes_actives)} bande(s)\n\n" + \
               "\n".join([f"• {b['nom']} : {b['nombre_initial']} animaux" for b in bandes_actives])
    
    return f"🏷️ **Vos bandes :** {donnees['statistiques']['total_bandes']} bande(s) au total\n\n" + \
           "\n".join([f"• {b['nom']} ({b['statut']}) : {b['nombre_initial']} animaux" for b in donnees['bandes']])

@chatbot_bp.route('/')
def chatbot_page():
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('chatbot.html')

@chatbot_bp.route('/ask', methods=['POST'])
def ask_question():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Récupérer les données de l'éleveur
        donnees_eleveur = get_donnees_eleveur(session['eleveur_id'])
        
        # Analyser la question
        if 'erreur' in donnees_eleveur:
            reponse = f"❌ Erreur lors de la récupération des données : {donnees_eleveur['erreur']}"
        else:
            reponse = analyser_question_manuelle(message, donnees_eleveur)
        
        # Sauvegarder dans l'historique
        message_chat = MessageChatbot(
            eleveur_id=session['eleveur_id'],
            message_utilisateur=message,
            reponse_bot=reponse
        )
        db.session.add(message_chat)
        db.session.commit()
        
        return jsonify({'reponse': reponse})
        
    except Exception as e:
        return jsonify({'error': f'Erreur chatbot: {str(e)}'}), 500

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
            'date_message': msg.date_message.isoformat()
        } for msg in historique])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400