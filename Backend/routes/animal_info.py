from flask import Blueprint, request, jsonify, session
from datetime import datetime
from modeles.models import db, AnimalInfo, Bande
import traceback

animal_info_bp = Blueprint('animal_info', __name__)


def _require_eleveur():
    """Return (eleveur_id, None) or (None, (jsonify(...), 401)) if not authenticated."""
    eleveur_id = session.get('eleveur_id')
    if not eleveur_id:
        return None, (jsonify({'error': 'Non connecté'}), 401)
    return eleveur_id, None


@animal_info_bp.route('/bande/<int:bande_id>', methods=['GET'])
def list_animal_info(bande_id):
    eleveur_id, auth_err = _require_eleveur()
    if auth_err:
        return auth_err
    try:
        infos = AnimalInfo.query.join(Bande).filter(
            AnimalInfo.bande_id == bande_id,
            Bande.eleveur_id == eleveur_id
        ).order_by(AnimalInfo.semaine_production.asc()).all()
        return jsonify({
            'count': len(infos),
            'animal_info': [i.to_dict() for i in infos]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@animal_info_bp.route('/', methods=['POST'])
def create_animal_info():
    eleveur_id, auth_err = _require_eleveur()
    if auth_err:
        return auth_err
    try:
        data = request.get_json() or {}
        bande_id = data.get('bande_id')
        semaine = data.get('semaine_production')
        if not bande_id or not semaine:
            return jsonify({'error': 'bande_id et semaine_production sont requis'}), 400

        bande = Bande.query.get_or_404(bande_id)
        if bande.eleveur_id != eleveur_id:
            return jsonify({'error': 'Accès refusé'}), 403

        # Unicité semaine
        exists = AnimalInfo.query.filter_by(bande_id=bande_id, semaine_production=semaine).first()
        if exists:
            return jsonify({'error': f'Déjà des données pour la semaine {semaine}. Modifiez ou supprimez l\'enregistrement existant.'}), 400

        # Normalize poids_moyen: accept grams for backward compatibility
        poids = data.get('poids_moyen')
        try:
            poids_val = float(poids) if poids is not None else None
            if poids_val and poids_val > 10:
                poids_val = poids_val / 1000.0
            if poids_val and poids_val > 2.0:
                poids_val = 2.0
        except Exception:
            poids_val = None

        info = AnimalInfo(
            bande_id=bande_id,
            semaine_production=semaine,
            poids_moyen=poids_val,
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
    eleveur_id, auth_err = _require_eleveur()
    if auth_err:
        return auth_err
    try:
        info = AnimalInfo.query.get_or_404(info_id)
        bande = info.bande
        if not bande or bande.eleveur_id != eleveur_id:
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
            try:
                v = float(data.get('poids_moyen')) if data.get('poids_moyen') is not None else None
                if v and v > 10:
                    v = v / 1000.0
                if v and v > 2.0:
                    v = 2.0
                info.poids_moyen = v
            except Exception:
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
    eleveur_id, auth_err = _require_eleveur()
    if auth_err:
        return auth_err
    try:
        info = AnimalInfo.query.get_or_404(info_id)
        bande = info.bande
        if not bande or bande.eleveur_id != eleveur_id:
            return jsonify({'error': 'Accès refusé'}), 403
        db.session.delete(info)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
