from flask import Blueprint, request, jsonify, session
from datetime import datetime
from modeles.models import db, AnimalInfo, Bande
import traceback

animal_info_bp = Blueprint('animal_info', __name__)


def _eleveur_id():
    # TODO: remplacer par l'ID de session réel
    return session.get('eleveur_id', 1)


@animal_info_bp.route('/bande/<int:bande_id>', methods=['GET'])
def list_animal_info(bande_id):
    try:
        infos = AnimalInfo.query.join(Bande).filter(
            AnimalInfo.bande_id == bande_id,
            Bande.eleveur_id == _eleveur_id()
        ).order_by(AnimalInfo.semaine_production.asc()).all()
        return jsonify({
            'count': len(infos),
            'animal_info': [i.to_dict() for i in infos]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@animal_info_bp.route('/', methods=['POST'])
def create_animal_info():
    try:
        data = request.get_json() or {}
        bande_id = data.get('bande_id')
        semaine = data.get('semaine_production')
        if not bande_id or not semaine:
            return jsonify({'error': 'bande_id et semaine_production sont requis'}), 400

        bande = Bande.query.get_or_404(bande_id)
        if bande.eleveur_id != _eleveur_id():
            return jsonify({'error': 'Accès refusé'}), 403

        # Unicité semaine
        exists = AnimalInfo.query.filter_by(bande_id=bande_id, semaine_production=semaine).first()
        if exists:
            return jsonify({'error': f'Déjà des données pour la semaine {semaine}. Modifiez ou supprimez l\'enregistrement existant.'}), 400

        info = AnimalInfo(
            bande_id=bande_id,
            semaine_production=semaine,
            poids_moyen=data.get('poids_moyen'),
            morts_semaine=data.get('morts_semaine') or 0,
            animaux_restants=data.get('animaux_restants'),
            note=data.get('note')
        )
        db.session.add(info)
        db.session.commit()
        return jsonify(info.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


@animal_info_bp.route('/<int:info_id>', methods=['PUT', 'PATCH'])
def update_animal_info(info_id):
    try:
        info = AnimalInfo.query.get_or_404(info_id)
        bande = info.bande
        if not bande or bande.eleveur_id != _eleveur_id():
            return jsonify({'error': 'Accès refusé'}), 403

        data = request.get_json() or {}
        if 'semaine_production' in data:
            new_week = data.get('semaine_production')
            if new_week and new_week != info.semaine_production:
                exists = AnimalInfo.query.filter_by(bande_id=info.bande_id, semaine_production=new_week).first()
                if exists:
                    return jsonify({'error': f'Déjà des données pour la semaine {new_week}. Modifiez ou supprimez l\'enregistrement existant.'}), 400
                info.semaine_production = new_week

        if 'poids_moyen' in data:
            info.poids_moyen = data.get('poids_moyen')
        if 'morts_semaine' in data:
            info.morts_semaine = data.get('morts_semaine') or 0
        if 'animaux_restants' in data:
            info.animaux_restants = data.get('animaux_restants')
        if 'note' in data:
            info.note = data.get('note')

        db.session.add(info)
        db.session.commit()
        return jsonify(info.to_dict())
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


@animal_info_bp.route('/<int:info_id>', methods=['DELETE'])
def delete_animal_info(info_id):
    try:
        info = AnimalInfo.query.get_or_404(info_id)
        bande = info.bande
        if not bande or bande.eleveur_id != _eleveur_id():
            return jsonify({'error': 'Accès refusé'}), 403
        db.session.delete(info)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
