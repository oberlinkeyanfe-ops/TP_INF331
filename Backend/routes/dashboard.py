from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from modeles.models import db, Bande, Consommation, Traitement
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)


# Appliquer à toutes les routes du blueprint
@dashboard_bp.before_request
@login_required
def require_login():
    """Vérifie l'authentification pour toutes les routes"""
    pass

@dashboard_bp.route('/')
def dashboard_page():
    # Return dashboard data as JSON for the authenticated eleveur
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        # Statistiques générales
        bandes_actives = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'], 
            statut='active'
        ).count()
        
        total_animaux = db.session.query(func.sum(Bande.nombre_initial)).filter_by(
            eleveur_id=session['eleveur_id']
        ).scalar() or 0
        
        total_depenses = 0  # Depense model supprimé
        total_traitements = Traitement.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).count()
        
        # Dernières activités
        dernieres_consommations = Consommation.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Consommation.date.desc()).limit(5).all()
        
        dernieres_depenses = []  # Depense supprimé
        
        # Bandes nécessitant attention
        bandes_attention = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).filter(
            (Bande.nombre_morts_totaux > Bande.nombre_initial * 0.1)
            | (Bande.age_moyen > 180)
        ).all()
        # Nouvelles statistiques alignées sur le modèle actuel (pas de modèle Animal/Intervention)
        nb_nouveaux_nes = 0
        nb_morts = db.session.query(func.sum(Bande.nombre_morts_totaux)).filter_by(
            eleveur_id=session['eleveur_id']
        ).scalar() or 0

        nb_maladies_rencontrees = db.session.query(func.count(Traitement.id.distinct())).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).scalar() or 0

        nb_malades = nb_maladies_rencontrees
        nb_epidemies = 0

        # Serializer helper (use to_dict if available)
        def serialize_list(items):
            result = []
            for it in items:
                if hasattr(it, 'to_dict'):
                    result.append(it.to_dict())
                else:
                    # fallback: include a minimal representation
                    result.append({c.name: getattr(it, c.name) for c in getattr(it.__class__, '__table__').columns})
            return result

        return jsonify({
            'bandes_actives': bandes_actives,
            'total_animaux': int(total_animaux),
            'total_depenses': float(total_depenses),
            'total_traitements': total_traitements,
            'dernieres_consommations': serialize_list(dernieres_consommations),
            'dernieres_depenses': serialize_list(dernieres_depenses),
            'bandes_attention': [b.to_dict() for b in bandes_attention],
            'nb_nouveaux_nes': int(nb_nouveaux_nes),
            'nb_morts': int(nb_morts),
            'nb_maladies_rencontrees': int(nb_maladies_rencontrees),
            'nb_malades': int(nb_malades),
            'nb_epidemies': int(nb_epidemies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/statistiques/rapides', methods=['GET'])
def get_statistiques_rapides():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Statistiques du mois en cours
        maintenant = datetime.now()
        debut_mois = maintenant.replace(day=1)
        
        # Dépenses du mois
        depenses_mois = 0  # Depense supprimé
        
        # Consommation du mois
        consommation_mois = db.session.query(func.sum(Consommation.aliment_kg)).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Consommation.date >= debut_mois
        ).scalar() or 0
        
        # Nouveaux traitements du mois
        traitements_mois = Traitement.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Traitement.date >= debut_mois
        ).count()
        
        # Interventions du mois
        interventions_mois = 0  # Intervention supprimé
        
        return jsonify({
            'depenses_mois': round(depenses_mois, 2),
            'consommation_mois': round(consommation_mois, 2),
            'traitements_mois': traitements_mois,
            'interventions_mois': interventions_mois,
            'mois': debut_mois.strftime('%B %Y')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@dashboard_bp.route('/alertes', methods=['GET'])
def get_alertes():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        alertes = []
        
        # Vérifier les bandes avec mortalité élevée
        bandes_mortalite = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).filter(
            Bande.nombre_morts_totaux > Bande.nombre_initial * 0.05  # Plus de 5% de mortalité
        ).all()
        
        for bande in bandes_mortalite:
            taux_mortalite = (bande.nombre_morts_totaux / bande.nombre_initial) * 100
            alertes.append({
                'type': 'mortalite',
                'niveau': 'danger',
                'message': f"Bande {bande.nom_bande}: Taux de mortalité élevé ({taux_mortalite:.1f}%)",
                'bande_id': bande.id
            })
        
        # Vérifier les traitements manquants (plus de 15 jours sans traitement)
        date_limite = datetime.now().date() - timedelta(days=15)
        bandes_sans_traitement = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).outerjoin(Traitement).filter(
            (Traitement.id.is_(None)) | 
            (Traitement.date < date_limite)
        ).all()
        
        for bande in bandes_sans_traitement:
            alertes.append({
                'type': 'traitement',
                'niveau': 'warning',
                'message': f"Bande {bande.nom_bande}: Aucun traitement récent",
                'bande_id': bande.id
            })
        
        return jsonify({'alertes': alertes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@dashboard_bp.route('/performance/bandes', methods=['GET'])
def get_performance_bandes():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        
        performance = []
        for bande in bandes:
            # Pas de modèle Depense : coût par animal non calculé
            cout_par_animal = 0

            total_consommation = db.session.query(func.sum(Consommation.aliment_kg)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            consommation_par_animal = total_consommation / bande.nombre_initial if bande.nombre_initial > 0 else 0

            performance.append({
                'bande_id': bande.id,
                'nom_bande': bande.nom_bande,
                'statut': bande.statut,
                'nombre_animaux': bande.nombre_initial,
                'cout_par_animal': round(cout_par_animal, 2),
                'consommation_par_animal': round(consommation_par_animal, 2),
                'taux_mortalite': round((bande.nombre_morts_totaux / bande.nombre_initial) * 100, 2) if bande.nombre_initial > 0 else 0
            })
        
        return jsonify({'performance': performance})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400