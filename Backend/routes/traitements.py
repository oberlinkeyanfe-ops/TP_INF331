from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from modeles.models import db, Traitement, Bande, Worker
from datetime import datetime

traitements_bp = Blueprint('traitements', __name__)

@traitements_bp.route('/')
def traitements_page():
    """Page de gestion des traitements"""
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        traitements = Traitement.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Traitement.date.desc()).all()
        
        bandes = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'], 
            statut='active'
        ).all()
        
        workers = Worker.query.filter_by(actif=True).all()
        
        return render_template('traitements.html', 
                             traitements=traitements, 
                             bandes=bandes, 
                             workers=workers,
                             gestion_mode=True)
        
    except Exception as e:
        return render_template('traitements.html', 
                             traitements=[], 
                             bandes=[], 
                             workers=[], 
                             error=str(e),
                             gestion_mode=True)

# Les autres fonctions existantes restent inchangées

@traitements_bp.route('/', methods=['POST'])
def create_traitement():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        data = request.get_json()
        
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=data['bande_id'], 
            eleveur_id=session['eleveur_id']
        ).first()
        
        if not bande:
            return jsonify({'error': 'Bande non trouvée'}), 404
        
        traitement = Traitement(
            bande_id=data['bande_id'],
            worker_id=data['worker_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            produit=data['produit'],
            type_traitement=data['type_traitement'],
            dosage=data.get('dosage'),
            efficacite=float(data.get('efficacite', 0)) if data.get('efficacite') else None,
            notes=data.get('notes'),
            nombre_morts_apres=int(data.get('nombre_morts_apres', 0)),
            nombre_gueris_apres=int(data.get('nombre_gueris_apres', 0))
        )
        
        db.session.add(traitement)
        db.session.commit()
        return jsonify(traitement.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur création: {str(e)}'}), 400

@traitements_bp.route('/<int:id>', methods=['GET'])
def get_traitement(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        traitement = Traitement.query.join(Bande).filter(
            Traitement.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        return jsonify(traitement.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@traitements_bp.route('/<int:id>', methods=['PUT'])
def update_traitement(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        traitement = Traitement.query.join(Bande).filter(
            Traitement.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        data = request.get_json()
        
        # Vérifier bande_id si fourni
        if 'bande_id' in data:
            bande = Bande.query.filter_by(
                id=data['bande_id'], 
                eleveur_id=session['eleveur_id']
            ).first()
            if not bande:
                return jsonify({'error': 'Bande non trouvée'}), 404
        
        for key, value in data.items():
            if hasattr(traitement, key) and key not in ['id', 'created_at']:
                if key == 'date' and value:
                    setattr(traitement, key, datetime.strptime(value, '%Y-%m-%d').date())
                elif key in ['efficacite']:
                    setattr(traitement, key, float(value) if value else None)
                elif key in ['nombre_morts_apres', 'nombre_gueris_apres']:
                    setattr(traitement, key, int(value) if value else 0)
                else:
                    setattr(traitement, key, value)
        
        db.session.commit()
        return jsonify(traitement.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400

@traitements_bp.route('/<int:id>', methods=['DELETE'])
def delete_traitement(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        traitement = Traitement.query.join(Bande).filter(
            Traitement.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        db.session.delete(traitement)
        db.session.commit()
        return jsonify({'message': 'Traitement supprimé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur suppression: {str(e)}'}), 400

@traitements_bp.route('/bande/<int:bande_id>', methods=['GET'])
def get_traitements_bande(bande_id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=bande_id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        traitements = Traitement.query.filter_by(bande_id=bande_id).order_by(Traitement.date.desc()).all()
        return jsonify([traitement.to_dict() for traitement in traitements])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@traitements_bp.route('/statistiques', methods=['GET'])
def get_statistiques_traitements():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        from sqlalchemy import func
        
        # Traitements par type
        traitements_par_type = db.session.query(
            Traitement.type_traitement,
            func.count(Traitement.id).label('count')
        ).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).group_by(Traitement.type_traitement).all()
        
        # Efficacité moyenne
        efficacite_moyenne = db.session.query(
            func.avg(Traitement.efficacite)
        ).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Traitement.efficacite.isnot(None)
        ).scalar() or 0
        
        return jsonify({
            'traitements_par_type': {t.type_traitement: t.count for t in traitements_par_type},
            'efficacite_moyenne': round(efficacite_moyenne, 2),
            'total_traitements': sum(t.count for t in traitements_par_type)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400