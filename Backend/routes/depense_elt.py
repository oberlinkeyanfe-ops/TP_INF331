from flask import Blueprint, request, jsonify, session
from modeles.models import db, depense_elt, Bande
from datetime import datetime
from flask_login import login_required

depenses_bp = Blueprint('depenses_elt', __name__)

# Utiliser une casse lisible pour le modèle
DepenseElt = depense_elt


@depenses_bp.before_request
def require_login():
    """Vérifie l'authentification pour toutes les routes (session-based)."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401


@depenses_bp.route('/')
def list_depenses():
    """Retourne les dépenses élémentaires de l'éleveur."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        depenses = DepenseElt.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(DepenseElt.date.desc()).all()

        bandes = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).all()

        return jsonify({
            'depenses': [d.to_dict() for d in depenses],
            'bandes': [b.to_dict() for b in bandes],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@depenses_bp.route('/bande/<int:bande_id>', methods=['GET'])
def get_depenses_par_bande(bande_id):
    """Récupère les dépenses pour une bande spécifique."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        bande = Bande.query.filter_by(id=bande_id, eleveur_id=session['eleveur_id']).first_or_404()
        depenses = DepenseElt.query.filter_by(bande_id=bande_id).order_by(DepenseElt.date.desc()).all()
        return jsonify({'bande': bande.to_dict(), 'depenses': [d.to_dict() for d in depenses]})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@depenses_bp.route('/', methods=['POST'])
def create_depense():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        data = request.get_json() or {}

        bande = Bande.query.filter_by(id=data.get('bande_id'), eleveur_id=session['eleveur_id']).first()
        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404

        depense = DepenseElt(
            bande_id=bande.id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            type_depense=data['type_depense'],
            description=data.get('description'),
            duree_heures=float(data.get('duree_heures', 0)) if data.get('duree_heures') else None,
            cout=float(data.get('cout', 0)) if data.get('cout') is not None else None,
        )

        db.session.add(depense)
        db.session.commit()
        return jsonify(depense.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur création: {str(e)}'}), 400


@depenses_bp.route('/<int:id>', methods=['GET'])
def get_depense(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        depense = DepenseElt.query.join(Bande).filter(
            DepenseElt.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()

        return jsonify(depense.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 404


@depenses_bp.route('/<int:id>', methods=['PUT'])
def update_depense(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        depense = DepenseElt.query.join(Bande).filter(
            DepenseElt.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()

        data = request.get_json() or {}

        if 'bande_id' in data:
            bande = Bande.query.filter_by(id=data['bande_id'], eleveur_id=session['eleveur_id']).first()
            if not bande:
                return jsonify({'error': 'Bande non trouvée'}), 404
            depense.bande_id = bande.id

        for key, value in data.items():
            if key in ['type_depense', 'description']:
                setattr(depense, key, value)
            elif key == 'date' and value:
                depense.date = datetime.strptime(value, '%Y-%m-%d').date()
            elif key == 'duree_heures':
                depense.duree_heures = float(value) if value is not None else None
            elif key == 'cout':
                depense.cout = float(value) if value is not None else None

        db.session.commit()
        return jsonify(depense.to_dict())

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400


@depenses_bp.route('/<int:id>', methods=['DELETE'])
def delete_depense(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        depense = DepenseElt.query.join(Bande).filter(
            DepenseElt.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()

        db.session.delete(depense)
        db.session.commit()
        return jsonify({'message': 'Dépense supprimée avec succès'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur suppression: {str(e)}'}), 400