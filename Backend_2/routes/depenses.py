from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from modeles.models import db, Depense, Bande
from datetime import datetime

depenses_bp = Blueprint('depenses', __name__)

@depenses_bp.route('/')
def depenses_page():
    """Page de gestion des dépenses"""
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        depenses = Depense.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Depense.date.desc()).all()
        
        bandes = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'], 
            statut='active'
        ).all()
        
        return render_template('depenses.html', 
                             depenses=depenses, 
                             bandes=bandes,
                             gestion_mode=True)
        
    except Exception as e:
        return render_template('depenses.html', 
                             depenses=[], 
                             bandes=[], 
                             error=str(e),
                             gestion_mode=True)

# Les autres fonctions existantes restent inchangées
@depenses_bp.route('/', methods=['POST'])
def create_depense():
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
        
        depense = Depense(
            bande_id=data['bande_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            type_depense=data['type_depense'],
            description=data.get('description'),
            montant=float(data['montant'])
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
        depense = Depense.query.join(Bande).filter(
            Depense.id == id,
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
        depense = Depense.query.join(Bande).filter(
            Depense.id == id,
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
            if hasattr(depense, key) and key not in ['id', 'created_at']:
                if key == 'date' and value:
                    setattr(depense, key, datetime.strptime(value, '%Y-%m-%d').date())
                elif key == 'montant':
                    setattr(depense, key, float(value) if value else 0)
                else:
                    setattr(depense, key, value)
        
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
        depense = Depense.query.join(Bande).filter(
            Depense.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        db.session.delete(depense)
        db.session.commit()
        return jsonify({'message': 'Dépense supprimée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur suppression: {str(e)}'}), 400

@depenses_bp.route('/statistiques/bande/<int:bande_id>', methods=['GET'])
def get_statistiques_depenses(bande_id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=bande_id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        # Total des dépenses
        total_depenses = db.session.query(func.sum(Depense.montant)).filter_by(bande_id=bande_id).scalar() or 0
        
        # Dépenses par type
        depenses_par_type = db.session.query(
            Depense.type_depense,
            func.sum(Depense.montant).label('total')
        ).filter_by(bande_id=bande_id).group_by(Depense.type_depense).all()
        
        # Dépenses des 30 derniers jours
        date_limite = datetime.now().date() - timedelta(days=30)
        depenses_30_jours = db.session.query(func.sum(Depense.montant)).filter(
            Depense.bande_id == bande_id,
            Depense.date >= date_limite
        ).scalar() or 0
        
        return jsonify({
            'total_depenses': round(total_depenses, 2),
            'depenses_30_jours': round(depenses_30_jours, 2),
            'depenses_par_type': {d.type_depense: round(d.total, 2) for d in depenses_par_type},
            'cout_par_animal': round(total_depenses / bande.nombre_initial, 2) if bande.nombre_initial > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400