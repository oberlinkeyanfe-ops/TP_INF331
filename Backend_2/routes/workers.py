from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from modeles.models import db, Worker
from datetime import datetime

workers_bp = Blueprint('workers', __name__)

@workers_bp.route('/')
def workers_page():
    """Page de gestion des employés"""
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        workers = Worker.query.order_by(Worker.nom).all()
        return render_template('workers.html', workers=workers, gestion_mode=True)
        
    except Exception as e:
        return render_template('workers.html', workers=[], error=str(e), gestion_mode=True)

# Les autres fonctions existantes restent inchangées
# create_worker, get_worker, update_worker, delete_worker, etc.

@workers_bp.route('/', methods=['POST'])
def create_worker():
    try:
        data = request.get_json()
        
        worker = Worker(
            nom=data['nom'],
            email=data['email'],
            telephone=data.get('telephone'),
            type_worker=data['type_worker'],
            specialite=data.get('specialite'),
            role=data.get('role'),
            salaire=float(data.get('salaire', 0)) if data.get('salaire') else None,
            date_embauche=datetime.strptime(data['date_embauche'], '%Y-%m-%d').date() if data.get('date_embauche') else None,
            actif=data.get('actif', True)
        )
        
        db.session.add(worker)
        db.session.commit()
        return jsonify(worker.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur création: {str(e)}'}), 400

@workers_bp.route('/<int:id>', methods=['GET'])
def get_worker(id):
    try:
        worker = Worker.query.get_or_404(id)
        return jsonify(worker.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@workers_bp.route('/<int:id>', methods=['PUT'])
def update_worker(id):
    try:
        worker = Worker.query.get_or_404(id)
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(worker, key) and key not in ['id', 'created_at', 'updated_at']:
                if key == 'date_embauche' and value:
                    setattr(worker, key, datetime.strptime(value, '%Y-%m-%d').date())
                elif key == 'salaire':
                    setattr(worker, key, float(value) if value else None)
                elif key == 'actif':
                    setattr(worker, key, bool(value))
                else:
                    setattr(worker, key, value)
        
        db.session.commit()
        return jsonify(worker.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400

@workers_bp.route('/<int:id>', methods=['DELETE'])
def delete_worker(id):
    try:
        worker = Worker.query.get_or_404(id)
        db.session.delete(worker)
        db.session.commit()
        return jsonify({'message': 'Employé supprimé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur suppression: {str(e)}'}), 400

@workers_bp.route('/type/<string:type_worker>', methods=['GET'])
def get_workers_by_type(type_worker):
    try:
        workers = Worker.query.filter_by(type_worker=type_worker, actif=True).all()
        return jsonify([worker.to_dict() for worker in workers])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400