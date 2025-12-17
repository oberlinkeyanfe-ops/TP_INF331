from flask import Blueprint, request, jsonify, session, current_app
from modeles.models import db, Bande
from datetime import datetime, date
from sqlalchemy import or_, func
import csv
import io

# Import the seed helper (safe to import in runtime)
try:
    from init_data import seed_initial_bandes
except Exception:
    # Fallback absolute import if package layout requires it
    try:
        from Backend.init_data import seed_initial_bandes
    except Exception:
        seed_initial_bandes = None

bandes_bp = Blueprint('bandes', __name__)


# ⭐ PAS besoin de décorateurs - le middleware global dans app.py gère l'auth

def _require_eleveur():
    """Retourne l'eleveur_id ou une réponse 401 si non connecté."""
    eleveur_id = session.get('eleveur_id')
    if not eleveur_id:
        return None, (jsonify({'error': 'Non connecté'}), 401)
    return eleveur_id, None

@bandes_bp.route('/')
def bandes_page():
    """Retourne la liste des bandes de l'éleveur connecté"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        
        bandes = Bande.query.filter_by(
            eleveur_id=eleveur_id
        ).order_by(Bande.date_arrivee.desc()).all()

       
        return jsonify([b.to_dict() for b in bandes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bandes_bp.route('/seed', methods=['POST', 'GET'])
def seed_bandes():
    """Trigger seeding of sample bandes (dev helper).
    - Safe to call in dev. Returns created count and diagnostics.
    - If user is logged in (session eleveur_id) it seeds for that user.
    - Accepts query param `email` to seed for a specific email.
    """
    if seed_initial_bandes is None:
        return jsonify({'error': 'Seed helper not available'}), 500

    # If user is logged in, seed for their account
    try:
        eleveur_id = session.get('eleveur_id')
        email_param = request.args.get('email')
        if eleveur_id:
            res = seed_initial_bandes(current_app, eleveur_id=eleveur_id)
            return jsonify(res)
        elif email_param:
            res = seed_initial_bandes(current_app, target_email=email_param)
            return jsonify(res)
        else:
            # fallback: seed for first eleveur (same as before)
            res = seed_initial_bandes(current_app)
            return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bandes_bp.route('/seed-full', methods=['POST', 'GET'])
def seed_full():
    """Seed full time series and records for an eleveur (dev helper).
    - Query param: ?eleveur=2 or seed for session eleveur if logged in.
    """
    if 'eleveur_id' in session:
        target = session.get('eleveur_id')
    else:
        try:
            target = int(request.args.get('eleveur')) if request.args.get('eleveur') else None
        except Exception:
            target = None

    if not target:
        return jsonify({'error': 'eleveur id required (session or ?eleveur=ID)'}), 400

    if 'seed_initial_bandes' not in globals():
        return jsonify({'error': 'Seed helper not available'}), 500

    try:
        # import the seed_full function from init_data
        from init_data import seed_full_for_eleveur
        res = seed_full_for_eleveur(current_app, target)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bandes_bp.route('/gestion')
def gestion_bandes():
    """Retourne les données de gestion des bandes"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        
        bandes = Bande.query.filter_by(
            eleveur_id=eleveur_id
        ).order_by(Bande.date_arrivee.desc()).all()

        return jsonify({
            'bandes': [b.to_dict() for b in bandes],
            'today': date.today().strftime('%Y-%m-%d'),
            'gestion_mode': True
        })
    except Exception as e:
        return jsonify({'bandes': [], 'error': str(e)}), 500


@bandes_bp.route('/create', methods=['POST'])
def create_bande():
    """Crée une nouvelle bande"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Champs requis
        nom_bande = data.get('nom_bande')
        date_arrivee = data.get('date_arrivee')
        nombre_initial = data.get('nombre_initial')

        if not nom_bande or not date_arrivee or not nombre_initial:
            return jsonify({'error': 'Champs requis manquants: nom_bande, date_arrivee, nombre_initial'}), 400

        bande = Bande(
            eleveur_id=eleveur_id,
            nom_bande=nom_bande,
            date_arrivee=datetime.strptime(date_arrivee, '%Y-%m-%d').date(),
            race=data.get('race'),
            fournisseur=data.get('fournisseur'),
            nombre_initial=int(nombre_initial),
            poids_moyen_initial=float(data.get('poids_moyen_initial', 0) or 0),
            duree_jours=int(data.get('duree_jours') or 0) or None,
            age_moyen=float(data.get('age_moyen', 0) or 0),
            nombre_morts_totaux=int(data.get('nombre_morts_totaux', 0) or 0),
            statut=data.get('statut', 'active')
        )

        db.session.add(bande)
        db.session.commit()

        return jsonify(bande.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bandes_bp.route('/<int:id>', methods=['GET'])
def get_bande(id):
    """Récupère une bande spécifique"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=eleveur_id
        ).first()
        
        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404
        
        return jsonify(bande.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@bandes_bp.route('/<int:id>', methods=['PUT'])
def update_bande(id):
    """Met à jour une bande"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=eleveur_id
        ).first()
        
        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404
        
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(bande, key) and key not in ['id', 'eleveur_id', 'created_at', 'updated_at']:
                if key == 'date_arrivee' and value:
                    setattr(bande, key, datetime.strptime(value, '%Y-%m-%d').date())
                elif key in ['nombre_initial', 'nombre_morts_totaux']:
                    setattr(bande, key, int(value) if value else 0)
                elif key in ['poids_moyen_initial', 'age_moyen']:
                    setattr(bande, key, float(value) if value else 0)
                elif key == 'duree_jours':
                    setattr(bande, key, int(value) if value else None)
                else:
                    setattr(bande, key, value)
        
        db.session.commit()
        return jsonify(bande.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400


@bandes_bp.route('/<int:id>/delete', methods=['POST'])
def delete_bande(id):
    """Supprime une bande"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=eleveur_id
        ).first()
        
        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404
        
        db.session.delete(bande)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bande supprimée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



@bandes_bp.route('/search', methods=['GET'])
def search_bandes():
    """Recherche des bandes"""
    try:
        if 'eleveur_id' not in session:
            return jsonify({'error': 'Non connecté'}), 401

        eleveur_id = session['eleveur_id']
        search_term = request.args.get('q', '')
        
        if search_term:
            bandes = Bande.query.filter(
                Bande.eleveur_id == eleveur_id,
                or_(
                    Bande.nom_bande.ilike(f'%{search_term}%'),
                    Bande.race.ilike(f'%{search_term}%'),
                    Bande.fournisseur.ilike(f'%{search_term}%')
                )
            ).all()
        else:
            bandes = Bande.query.filter_by(eleveur_id=eleveur_id).all()
        
        return jsonify([bande.to_dict() for bande in bandes])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bandes_bp.route('/statistiques', methods=['GET'])
def get_statistiques():
    """Statistiques des bandes"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        
        total_bandes = Bande.query.filter_by(eleveur_id=eleveur_id).count()
        bandes_actives = Bande.query.filter_by(eleveur_id=eleveur_id, statut='active').count()
        
        total_stats = db.session.query(
            func.sum(Bande.nombre_initial).label('total_initiaux'),
            func.sum(Bande.nombre_morts_totaux).label('total_morts')
        ).filter_by(eleveur_id=eleveur_id).first()
        
        total_animaux = (total_stats.total_initiaux or 0) - (total_stats.total_morts or 0)
        
        return jsonify({
            'total_bandes': total_bandes,
            'bandes_actives': bandes_actives,
            'total_animaux': total_animaux,
            'animaux_initiaux': total_stats.total_initiaux or 0,
            'animaux_ajoutes': 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bandes_bp.route('/<int:id>/details', methods=['GET'])
def get_bande_details(id):
    """Détails d'une bande (sans données animaux)"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        bande = Bande.query.filter_by(id=id, eleveur_id=eleveur_id).first()
        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404

        bande_data = bande.to_dict()
        # Plus de suivi d'animaux dans l'application
        bande_data['animaux'] = []
        bande_data['total_animaux_actuels'] = bande.nombre_initial - bande.nombre_morts_totaux

        return jsonify(bande_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 404


@bandes_bp.route('/<int:id>/update_ajoute', methods=['POST'])
def update_nbre_ajoute(id):
    """Met à jour le compteur nbre_ajoute (animaux supprimés → valeur statique)"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        bande = Bande.query.filter_by(id=id, eleveur_id=eleveur_id).first()
        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404

        # Plus de modèle Animal : on ne recalcule plus, on laisse la valeur existante
        db.session.commit()

        return jsonify({
            'success': True,
            'nbre_ajoute': 0,
            'message': 'Compteur supprimé (gestion animaux retirée)'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@bandes_bp.route('/sync-compteurs', methods=['POST'])
def sync_all_compteurs():
    """Synchronise les compteurs nbre_ajoute (aucune action car animaux retirés)"""
    try:
        eleveur_id, auth_err = _require_eleveur()
        if auth_err:
            return auth_err
        Bande.query.filter_by(eleveur_id=eleveur_id).all()
        # Aucun recalcul sans compteur
        db.session.commit()
        return jsonify({'success': True, 'updated_count': 0, 'message': 'Compteur supprimé (animaux retirés)'});
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bandes_bp.route('/test-auth')
def test_auth():
    """Route test pour vérifier l'authentification"""
    eleveur_id, auth_err = _require_eleveur()
    if auth_err:
        return auth_err

    return jsonify({
        'success': True,
        'message': 'Authentifié avec Flask-Session!',
        'user_id': eleveur_id,
        'user_name': session.get('eleveur_nom'),
        'session_id': session.sid if hasattr(session, 'sid') else 'no_sid'
    })