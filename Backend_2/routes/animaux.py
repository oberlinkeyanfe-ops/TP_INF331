from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from modeles.models import db, Animal, Bande
from datetime import datetime
from sqlalchemy import func, or_
from datetime import date

animaux_bp = Blueprint('animaux', __name__)

@animaux_bp.route('/')
def animaux_page():
    """Page de gestion des animaux"""
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        animaux = Animal.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Animal.created_at.desc()).all()
        
        bandes = Bande.query.filter_by(
            eleveur_id=session['eleveur_id']
        ).all()  # Retirer le filtre statut='active' pour voir toutes les bandes
        
        return render_template('animaux.html', animaux=animaux, bandes=bandes, gestion_mode=True, today=date.today().strftime('%Y-%m-%d'))
        
    except Exception as e:
        flash(f'❌ Erreur: {str(e)}', 'error')
        return render_template('animaux.html', animaux=[], bandes=[], gestion_mode=True, today=date.today().strftime('%Y-%m-%d'))

@animaux_bp.route('/create', methods=['POST'])
def create_animal():
    if 'eleveur_id' not in session:
        flash('❌ Non connecté', 'error')
        return redirect(url_for('animaux.animaux_page'))
    
    try:
        data = request.form
        
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=data['bande_id'], 
            eleveur_id=session['eleveur_id']
        ).first()
        
        if not bande:
            flash('❌ Bande non trouvée', 'error')
            return redirect(url_for('animaux.animaux_page'))
        
        # Gérer les valeurs optionnelles
        prix = float(data.get('prix', 0))
        nombre = int(data.get('nombre', 1))
        age = float(data['age']) if data.get('age') else None
        poids = float(data['poids']) if data.get('poids') else None
        date_naissance = datetime.strptime(data['date_naissance'], '%Y-%m-%d').date() if data.get('date_naissance') else None
        
        # Créer l'animal avec la nouvelle structure
        animal = Animal(
            bande_id=data['bande_id'],
            etat_achat=data.get('etat_achat', 'acheté'),
            etat=data.get('etat', 'sain'),
            prix=prix,
            nombre=nombre,
            age=age,
            poids=poids,
            date_naissance=date_naissance
        )
        
        db.session.add(animal)
        db.session.flush()
        
        # Mettre à jour le nbre_ajoute de la bande
        total_ajoute = db.session.query(func.sum(Animal.nombre)).filter(
            Animal.bande_id == bande.id
        ).scalar() or 0
        
        bande.nbre_ajoute = total_ajoute
        db.session.commit()
        
        flash(f'✅ {animal.nombre} animal(s) ajouté(s) avec succès à la bande {bande.nom_bande}!', 'success')
        
    except ValueError as e:
        db.session.rollback()
        flash('❌ Erreur de format des données (nombre, prix, etc.)', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur: {str(e)}', 'error')
    
    return redirect(url_for('animaux.animaux_page'))

@animaux_bp.route('/<int:id>', methods=['GET'])
def get_animal(id):
    """Récupère un animal spécifique pour l'édition ou les détails"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        animal = Animal.query.join(Bande).filter(
            Animal.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        # Inclure le nom de la bande dans la réponse
        animal_data = animal.to_dict()
        animal_data['bande_nom'] = animal.bande.nom_bande
        
        return jsonify(animal_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@animaux_bp.route('/<int:id>', methods=['PUT'])
def update_animal(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        animal = Animal.query.join(Bande).filter(
            Animal.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        ancien_nombre = animal.nombre
        ancienne_bande_id = animal.bande_id
        
        for key, value in data.items():
            if hasattr(animal, key) and key not in ['id', 'created_at', 'updated_at']:
                if key == 'date_naissance' and value:
                    setattr(animal, key, datetime.strptime(value, '%Y-%m-%d').date())
                elif key == 'date_naissance' and not value:
                    setattr(animal, key, None)
                elif key in ['prix', 'age', 'poids']:
                    setattr(animal, key, float(value) if value is not None else None)
                elif key == 'nombre':
                    setattr(animal, key, int(value) if value else 1)
                else:
                    setattr(animal, key, value)
        
        # Mettre à jour le nbre_ajoute de la bande si le nombre a changé ou si la bande a changé
        bande_id_a_mettre_a_jour = animal.bande_id
        
        if 'bande_id' in data and int(data['bande_id']) != ancienne_bande_id:
            nouvelle_bande = Bande.query.filter_by(
                id=data['bande_id'],
                eleveur_id=session['eleveur_id']
            ).first()
            if not nouvelle_bande:
                return jsonify({'error': 'Nouvelle bande non trouvée'}), 404
            
            # Mettre à jour l'ancienne bande
            ancienne_bande = Bande.query.get(ancienne_bande_id)
            if ancienne_bande:
                total_ancienne = db.session.query(func.sum(Animal.nombre)).filter(
                    Animal.bande_id == ancienne_bande_id
                ).scalar() or 0
                ancienne_bande.nbre_ajoute = total_ancienne
            
            bande_id_a_mettre_a_jour = data['bande_id']
        
        if ancien_nombre != animal.nombre or 'bande_id' in data:
            bande = Bande.query.get(bande_id_a_mettre_a_jour)
            if bande:
                total_ajoute = db.session.query(func.sum(Animal.nombre)).filter(
                    Animal.bande_id == bande_id_a_mettre_a_jour
                ).scalar() or 0
                bande.nbre_ajoute = total_ajoute
        
        db.session.commit()
        
        # Retourner les données mises à jour avec le nom de la bande
        animal_data = animal.to_dict()
        animal_data['bande_nom'] = animal.bande.nom_bande
        
        return jsonify(animal_data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400

@animaux_bp.route('/<int:id>/delete', methods=['POST'])
def delete_animal(id):
    if 'eleveur_id' not in session:
        flash('❌ Non connecté', 'error')
        return redirect(url_for('animaux.animaux_page'))
    
    try:
        animal = Animal.query.join(Bande).filter(
            Animal.id == id,
            Bande.eleveur_id == session['eleveur_id']
        ).first_or_404()
        
        bande_id = animal.bande_id
        bande_nom = animal.bande.nom_bande
        db.session.delete(animal)
        
        # Mettre à jour le nbre_ajoute de la bande
        bande = Bande.query.get(bande_id)
        if bande:
            total_ajoute = db.session.query(func.sum(Animal.nombre)).filter(
                Animal.bande_id == bande_id
            ).scalar() or 0
            bande.nbre_ajoute = total_ajoute
        
        db.session.commit()
        flash(f'✅ Animal supprimé avec succès de la bande {bande_nom}!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur suppression: {str(e)}', 'error')
    
    return redirect(url_for('animaux.animaux_page'))

@animaux_bp.route('/api/liste', methods=['GET'])
def api_liste_animaux():
    """API pour la liste des animaux (AJAX)"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        animaux = Animal.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Animal.created_at.desc()).all()
        
        animaux_data = []
        for animal in animaux:
            animal_dict = animal.to_dict()
            animal_dict['bande_nom'] = animal.bande.nom_bande
            animal_dict['prix_total'] = animal.prix * animal.nombre
            animaux_data.append(animal_dict)
        
        return jsonify({'animaux': animaux_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@animaux_bp.route('/api/rechercher', methods=['GET'])
def rechercher_animaux():
    """Recherche d'animaux"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        search_term = request.args.get('q', '')
        
        if not search_term:
            return jsonify({'error': 'Terme de recherche manquant'}), 400
        
        # Recherche dans les animaux et leurs bandes
        animaux = Animal.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            or_(
                Animal.etat.ilike(f'%{search_term}%'),
                Animal.etat_achat.ilike(f'%{search_term}%'),
                Bande.nom_bande.ilike(f'%{search_term}%'),
                Bande.race.ilike(f'%{search_term}%')
            )
        ).order_by(Animal.created_at.desc()).all()
        
        animaux_data = []
        for animal in animaux:
            animal_dict = animal.to_dict()
            animal_dict['bande_nom'] = animal.bande.nom_bande
            animal_dict['bande_race'] = animal.bande.race
            animal_dict['prix_total'] = animal.prix * animal.nombre
            animaux_data.append(animal_dict)
        
        return jsonify({
            'animaux': animaux_data,
            'total': len(animaux_data),
            'search_term': search_term
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@animaux_bp.route('/api/bande/<int:bande_id>', methods=['GET'])
def api_get_animaux_par_bande(bande_id):
    """API pour les animaux par bande (AJAX)"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=bande_id,
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        animaux = Animal.query.filter_by(bande_id=bande_id).order_by(Animal.created_at.desc()).all()
        
        animaux_data = []
        for animal in animaux:
            animal_dict = animal.to_dict()
            animal_dict['prix_total'] = animal.prix * animal.nombre
            animaux_data.append(animal_dict)
        
        return jsonify({
            'bande': bande.to_dict(),
            'animaux': animaux_data,
            'total_animaux': sum(animal.nombre for animal in animaux)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@animaux_bp.route('/api/statistiques/generales', methods=['GET'])
def api_get_statistiques_generales():
    """API pour les statistiques générales (AJAX)"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        animaux = Animal.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).all()
        
        total_animaux = sum(animal.nombre for animal in animaux)
        
        if total_animaux == 0:
            return jsonify({
                'total_animaux': 0,
                'message': 'Aucun animal trouvé'
            })
        
        # Répartition par état de santé
        etats_sante = {}
        for animal in animaux:
            etats_sante[animal.etat] = etats_sante.get(animal.etat, 0) + animal.nombre
        
        # Répartition par état d'achat
        etats_achat = {}
        for animal in animaux:
            etats_achat[animal.etat_achat] = etats_achat.get(animal.etat_achat, 0) + animal.nombre
        
        # Coûts
        cout_total = sum(animal.prix * animal.nombre for animal in animaux)
        cout_moyen = cout_total / total_animaux if total_animaux > 0 else 0
        
        # Répartition par bande
        animaux_par_bande = {}
        for animal in animaux:
            nom_bande = animal.bande.nom_bande
            if nom_bande not in animaux_par_bande:
                animaux_par_bande[nom_bande] = 0
            animaux_par_bande[nom_bande] += animal.nombre
        
        # Statistiques supplémentaires
        bandes_avec_animaux = Bande.query.join(Animal).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).distinct().count()
        
        return jsonify({
            'total_animaux': total_animaux,
            'etats_sante': etats_sante,
            'etats_achat': etats_achat,
            'cout_total': round(cout_total, 2),
            'cout_moyen_par_animal': round(cout_moyen, 2),
            'animaux_par_bande': animaux_par_bande,
            'nombre_bandes_avec_animaux': bandes_avec_animaux,
            'nombre_enregistrements': len(animaux)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@animaux_bp.route('/statistiques/bande/<int:bande_id>', methods=['GET'])
def get_statistiques_bande(bande_id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=bande_id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        animaux = Animal.query.filter_by(bande_id=bande_id).all()
        
        total_animaux = sum(animal.nombre for animal in animaux)
        animaux_sains = sum(animal.nombre for animal in animaux if animal.etat == 'sain')
        animaux_malades = sum(animal.nombre for animal in animaux if animal.etat == 'malade')
        animaux_morts = sum(animal.nombre for animal in animaux if animal.etat == 'mort')
        animaux_disparus = sum(animal.nombre for animal in animaux if animal.etat == 'disparu')
        
        # Calculer les totaux par état d'achat
        achetés = sum(animal.nombre for animal in animaux if animal.etat_achat == 'acheté')
        nés = sum(animal.nombre for animal in animaux if animal.etat_achat == 'né')
        autres = sum(animal.nombre for animal in animaux if animal.etat_achat == 'autre')
        
        # Coût total
        cout_total = sum(animal.prix * animal.nombre for animal in animaux)
        
        return jsonify({
            'bande': bande.nom_bande,
            'total_animaux': total_animaux,
            'animaux_sains': animaux_sains,
            'animaux_malades': animaux_malades,
            'animaux_morts': animaux_morts,
            'animaux_disparus': animaux_disparus,
            'achetés': achetés,
            'nés': nés,
            'autres': autres,
            'cout_total': round(cout_total, 2),
            'cout_moyen_par_animal': round(cout_total / total_animaux, 2) if total_animaux > 0 else 0,
            'taux_sante': round((animaux_sains / total_animaux) * 100, 2) if total_animaux > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@animaux_bp.route('/bande/<int:bande_id>', methods=['GET'])
def get_animaux_par_bande(bande_id):
    """Récupère tous les animaux d'une bande spécifique"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=bande_id,
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        animaux = Animal.query.filter_by(bande_id=bande_id).order_by(Animal.created_at.desc()).all()
        
        animaux_data = []
        for animal in animaux:
            animal_dict = animal.to_dict()
            animal_dict['prix_total'] = animal.prix * animal.nombre
            animaux_data.append(animal_dict)
        
        return jsonify({
            'bande': bande.to_dict(),
            'animaux': animaux_data,
            'total_animaux': sum(animal.nombre for animal in animaux)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400