from flask import Blueprint, request, jsonify, session
from modeles.models import db, Consommation, Bande
from datetime import datetime
import traceback

consommations_bp = Blueprint('consommations', __name__)

# Appliquer à toutes les routes du blueprint
@consommations_bp.before_request
def require_login():
    """Vérifie l'authentification pour toutes les routes"""
    # Simulation d'authentification pour le développement
    session['eleveur_id'] = session.get('eleveur_id', 1)
    pass

# Création d'une consommation - VERSION CORRIGÉE
@consommations_bp.route('/', methods=['POST'])
def create_consommation():
    try:
        # Debug: afficher les données reçues
        print("=== NOUVELLE REQUÊTE CONSOMMATION ===")
        print("Headers:", dict(request.headers))
        print("Content-Type:", request.content_type)
        
        # Récupérer les données
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        print("Données reçues:", data)
        
        # Validation des champs obligatoires
        required_fields = ['bande_id', 'date', 'type_aliment', 'aliment_kg']
        missing_fields = [field for field in required_fields if field not in data or not str(data[field]).strip()]
        
        if missing_fields:
            error_msg = f"Champs obligatoires manquants: {', '.join(missing_fields)}"
            print("Erreur validation:", error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Vérifier et convertir bande_id
        try:
            bande_id = int(data['bande_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'bande_id doit être un nombre entier'}), 400
        
        # Vérifier la bande
        bande = Bande.query.filter_by(
            id=bande_id,
            eleveur_id=session['eleveur_id']
        ).first()

        if not bande:
            error_msg = f'Bande ID {bande_id} non trouvée ou accès refusé'
            print("Erreur bande:", error_msg)
            return jsonify({'error': error_msg}), 404
        
        print(f"Bande trouvée: ID={bande.id}, Nom={bande.nom_bande}")
        
        # Convertir et valider les nombres
        try:
            aliment_kg = float(data['aliment_kg'])
            if aliment_kg <= 0:
                return jsonify({'error': 'aliment_kg doit être supérieur à 0'}), 400
                
            cout_aliment = float(data.get('cout_aliment', 0))
            if cout_aliment < 0:
                return jsonify({'error': 'cout_aliment ne peut pas être négatif'}), 400
                
            eau_litres = float(data.get('eau_litres', 0))
            if eau_litres < 0:
                return jsonify({'error': 'eau_litres ne peut pas être négatif'}), 400
                
        except (ValueError, TypeError):
            return jsonify({'error': 'Les valeurs numériques sont invalides'}), 400
        
        # Convertir la date
        try:
            date_str = str(data['date']).strip()
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'}), 400

        # Calcul semaine de production à partir de la date d'arrivée
        semaine_prod = None
        if bande.date_arrivee:
            delta_jours = (date_obj - bande.date_arrivee).days
            if delta_jours < 0:
                return jsonify({'error': "La date de consommation est antérieure à la date d'arrivée"}), 400
            semaine_prod = (delta_jours // 7) + 1
            if bande.duree_jours:
                duree_semaines = max(1, (bande.duree_jours + 6) // 7)
                if semaine_prod > duree_semaines:
                    return jsonify({'error': "La consommation dépasse la durée prévue de la bande"}), 400

        # Interdire plusieurs consommations la même semaine
        if semaine_prod is not None:
            existing = Consommation.query.filter_by(
                bande_id=bande_id,
                semaine_production=semaine_prod
            ).first()
            if existing:
                return jsonify({'error': f'Une consommation existe déjà pour la semaine {semaine_prod}. Supprimez-la ou modifiez-la avant d\'ajouter.'}), 400
        
        # Créer la consommation
        consommation = Consommation(
            bande_id=bande_id,
            date=date_obj,
            type_aliment=str(data['type_aliment']).strip(),
            cout_aliment=cout_aliment,
            aliment_kg=aliment_kg,
            eau_litres=eau_litres,
            semaine_production=semaine_prod
        )

        db.session.add(consommation)

        # Mettre à jour le poids moyen actuel si fourni
        if 'poids_moyen_actuel' in data:
            try:
                bande.poids_moyen_actuel = float(data['poids_moyen_actuel'])
            except (ValueError, TypeError):
                db.session.rollback()
                return jsonify({'error': 'poids_moyen_actuel doit être un nombre'}), 400
            db.session.add(bande)

        db.session.commit()
        
        # Retourner la réponse
        response_data = consommation.to_dict()
        print("Consommation créée avec succès:", response_data)
        
        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        error_trace = traceback.format_exc()
        print("=== ERREUR CRITIQUE ===")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        return jsonify({'error': f'Erreur création: {str(e)}'}), 400

# Récupérer les consommations par bande - VERSION CORRIGÉE
@consommations_bp.route('/bande/<int:bande_id>', methods=['GET'])
def get_consommations_par_bande(bande_id):
    """Récupère les consommations pour une bande spécifique"""
    try:
        # Vérifier que la bande appartient à l'éleveur
        bande = Bande.query.filter_by(
            id=bande_id, 
            eleveur_id=session['eleveur_id']
        ).first()
        
        if not bande:
            return jsonify({'error': 'Bande non trouvée ou accès refusé'}), 404
        
        # Récupérer les consommations
        consommations = Consommation.query.filter_by(
            bande_id=bande_id
        ).order_by(Consommation.date.desc()).all()
        
        # Utiliser to_dict() qui est maintenant corrigé
        consommations_data = [c.to_dict() for c in consommations]
        
        return jsonify({
            'bande': {
                'id': bande.id,
                'nom_bande': bande.nom_bande,
                'date_arrivee': bande.date_arrivee.isoformat() if bande.date_arrivee else None
            },
            'consommations': consommations_data,
            'count': len(consommations_data)
        })

    except Exception as e:
        print(f"Erreur get_consommations_par_bande: {str(e)}")
        return jsonify({'error': str(e)}), 400


# Mise à jour d'une consommation
@consommations_bp.route('/<int:cons_id>', methods=['PUT', 'PATCH'])
def update_consommation(cons_id):
    try:
        cons = Consommation.query.get_or_404(cons_id)
        bande = cons.bande
        if not bande or bande.eleveur_id != session.get('eleveur_id', 1):
            return jsonify({'error': 'Accès refusé'}), 403

        data = request.get_json() or {}
        if 'date' in data:
            try:
                date_obj = datetime.strptime(str(data['date']).strip(), '%Y-%m-%d').date()
                cons.date = date_obj
            except ValueError:
                return jsonify({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'}), 400
        else:
            date_obj = cons.date

        if 'type_aliment' in data:
            cons.type_aliment = str(data['type_aliment']).strip()
        if 'aliment_kg' in data:
            try:
                cons.aliment_kg = float(data['aliment_kg'])
            except (ValueError, TypeError):
                return jsonify({'error': 'aliment_kg doit être un nombre'}), 400
        if 'cout_aliment' in data:
            try:
                cons.cout_aliment = float(data['cout_aliment'])
            except (ValueError, TypeError):
                return jsonify({'error': 'cout_aliment doit être un nombre'}), 400
        if 'eau_litres' in data:
            try:
                cons.eau_litres = float(data['eau_litres'])
            except (ValueError, TypeError):
                return jsonify({'error': 'eau_litres doit être un nombre'}), 400

        # recalcul semaine
        semaine_prod = cons.semaine_production
        if bande.date_arrivee and date_obj:
            delta_jours = (date_obj - bande.date_arrivee).days
            if delta_jours < 0:
                return jsonify({'error': "La date de consommation est antérieure à la date d'arrivée"}), 400
            semaine_prod = (delta_jours // 7) + 1
            if bande.duree_jours:
                duree_semaines = max(1, (bande.duree_jours + 6) // 7)
                if semaine_prod > duree_semaines:
                    return jsonify({'error': "La consommation dépasse la durée prévue de la bande"}), 400
            # check duplicate week other than current
            existing = Consommation.query.filter(
                Consommation.bande_id == bande.id,
                Consommation.semaine_production == semaine_prod,
                Consommation.id != cons.id
            ).first()
            if existing:
                return jsonify({'error': f'Une consommation existe déjà pour la semaine {semaine_prod}. Supprimez-la ou modifiez-la avant d\'ajouter.'}), 400
        cons.semaine_production = semaine_prod

        if 'poids_moyen_actuel' in data:
            try:
                bande.poids_moyen_actuel = float(data['poids_moyen_actuel'])
            except (ValueError, TypeError):
                return jsonify({'error': 'poids_moyen_actuel doit être un nombre'}), 400
            db.session.add(bande)

        db.session.add(cons)
        db.session.commit()
        return jsonify(cons.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Suppression d'une consommation
@consommations_bp.route('/<int:cons_id>', methods=['DELETE'])
def delete_consommation(cons_id):
    try:
        cons = Consommation.query.get_or_404(cons_id)
        bande = cons.bande
        if not bande or bande.eleveur_id != session.get('eleveur_id', 1):
            return jsonify({'error': 'Accès refusé'}), 403
        db.session.delete(cons)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400