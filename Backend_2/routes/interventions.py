from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from modeles.models import db, Intervention, Bande, Worker
from datetime import datetime

interventions_bp = Blueprint('interventions', __name__)

@interventions_bp.route('/')
def interventions_page():
    """Page de gestion des interventions"""
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        interventions = Intervention.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Intervention.date.desc()).all()
        
        bandes = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'], 
            statut='active'
        ).all()
        
        workers = Worker.query.filter_by(actif=True).all()
        
        return render_template('interventions.html', 
                             interventions=interventions, 
                             bandes=bandes, 
                             workers=workers,
                             gestion_mode=True)
        
    except Exception as e:
        return render_template('interventions.html', 
                             interventions=[], 
                             bandes=[], 
                             workers=[], 
                             error=str(e),
                             gestion_mode=True)

# Les autres fonctions existantes restent inchangées
@interventions_bp.route('/', methods=['POST'])
def create_intervention():
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
        
        intervention = Intervention(
            bande_id=data['bande_id'],
            worker_id=data['worker_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            type_intervention=data['type_intervention'],
            description=data['description'],
            duree_heures=float(data.get('duree_heures', 0)) if data.get('duree_heures') else None
        )
        
        db.session.add(intervention)
        db.session.commit()
        return jsonify(intervention.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur création: {str(e)}'}), 400

@interventions_bp.route('/<int:id>', methods=['GET'])
def get_intervention(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        intervention = Intervention.query.join(Bande).filter(
            Intervention.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        return jsonify(intervention.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@interventions_bp.route('/<int:id>', methods=['PUT'])
def update_intervention(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        intervention = Intervention.query.join(Bande).filter(
            Intervention.id == id,
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
            if hasattr(intervention, key) and key not in ['id', 'created_at']:
                if key == 'date' and value:
                    setattr(intervention, key, datetime.strptime(value, '%Y-%m-%d').date())
                elif key == 'duree_heures':
                    setattr(intervention, key, float(value) if value else None)
                else:
                    setattr(intervention, key, value)
        
        db.session.commit()
        return jsonify(intervention.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400

@interventions_bp.route('/<int:id>', methods=['DELETE'])
def delete_intervention(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        intervention = Intervention.query.join(Bande).filter(
            Intervention.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        db.session.delete(intervention)
        db.session.commit()
        return jsonify({'message': 'Intervention supprimée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur suppression: {str(e)}'}), 400

@interventions_bp.route('/statistiques/worker/<int:worker_id>', methods=['GET'])
def get_statistiques_worker(worker_id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Interventions du worker pour les bandes de l'éleveur
        interventions = Intervention.query.join(Bande).filter(
            Intervention.worker_id == worker_id,
            Bande.eleveur_id == session['eleveur_id']
        ).all()
        
        total_interventions = len(interventions)
        total_heures = sum(i.duree_heures or 0 for i in interventions)
        
        # Types d'interventions
        types_interventions = {}
        for intervention in interventions:
            type_interv = intervention.type_intervention
            types_interventions[type_interv] = types_interventions.get(type_interv, 0) + 1
        
        return jsonify({
            'total_interventions': total_interventions,
            'total_heures': round(total_heures, 2),
            'types_interventions': types_interventions,
            'moyenne_heures_par_intervention': round(total_heures / total_interventions, 2) if total_interventions > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400