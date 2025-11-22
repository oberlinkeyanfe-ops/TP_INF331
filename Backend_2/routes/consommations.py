from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from modeles.models import db, Consommation, Bande
from datetime import datetime, timedelta
from sqlalchemy import func

consommations_bp = Blueprint('consommations', __name__)

# Page principale
@consommations_bp.route('/')
def consommations_page():
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        consommations = Consommation.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Consommation.date.desc()).all()

        bandes = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).all()

        return render_template(
            'consommations.html',
            consommations=consommations,
            bandes=bandes,
            gestion_mode=True
        )

    except Exception as e:
        return render_template(
            'consommations.html',
            consommations=[],
            bandes=[],
            error=str(e),
            gestion_mode=True
        )


# Création d'une consommation
@consommations_bp.route('/', methods=['POST'])
def create_consommation():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        # RÉCUPÉRATION DES DONNÉES DU FORMULAIRE HTML
        data = request.form

        # Vérifier la bande
        bande = Bande.query.filter_by(
            id=data.get('bande_id'),
            eleveur_id=session['eleveur_id']
        ).first()

        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404

        consommation = Consommation(
            bande_id=int(data.get('bande_id')),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
            type_aliment=data.get('type_aliment'),
            cout_aliment=float(data.get('cout_aliment')),
            aliment_kg=float(data.get('aliment_kg')),
            eau_litres=float(data.get('eau_litres')),
            semaine_production=int(data.get('semaine_production')) if data.get('semaine_production') else None
        )

        db.session.add(consommation)
        db.session.commit()

        return redirect(url_for('consommations.consommations_page'))

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur création: {str(e)}'}), 400

# Récupérer une consommation
@consommations_bp.route('/<int:id>', methods=['GET'])
def get_consommation(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        consommation = Consommation.query.join(Bande).filter(
            Consommation.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()

        return jsonify(consommation.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 404


# Modifier une consommation
@consommations_bp.route('/<int:id>', methods=['PUT'])
def update_consommation(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        consommation = Consommation.query.join(Bande).filter(
            Consommation.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()

        data = request.get_json()

        # Validation bande
        if "bande_id" in data:
            bande = Bande.query.filter_by(
                id=data['bande_id'],
                eleveur_id=session['eleveur_id']
            ).first()
            if not bande:
                return jsonify({'error': 'Bande non trouvée'}), 404

        # Mise à jour dynamique
        for key, value in data.items():
            if hasattr(consommation, key):
                if key == "date":
                    setattr(consommation, key, datetime.strptime(value, "%Y-%m-%d").date())
                elif key in ["aliment_kg", "eau_litres", "cout_aliment"]:
                    setattr(consommation, key, float(value))
                elif key == "semaine_production":
                    setattr(consommation, key, int(value) if value else None)
                else:
                    setattr(consommation, key, value)

        db.session.commit()
        return jsonify(consommation.to_dict())

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400


# Suppression
@consommations_bp.route('/<int:id>', methods=['DELETE'])
def delete_consommation(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        consommation = Consommation.query.join(Bande).filter(
            Consommation.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()

        db.session.delete(consommation)
        db.session.commit()

        return jsonify({"message": "Consommation supprimée avec succès"})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur suppression: {str(e)}'}), 400
