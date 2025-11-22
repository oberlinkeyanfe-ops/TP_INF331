from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from modeles.models import db, Eleveur

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()  # JSON au lieu de form
        email = data.get('email')
        mot_de_passe = data.get('mot_de_passe')

        if not email or not mot_de_passe:
            return jsonify({"error": "Veuillez remplir tous les champs"}), 400

        # Recherche de l'éleveur
        eleveur = Eleveur.query.filter_by(email=email).first()
        

        if eleveur and check_password_hash(eleveur.mot_de_passe, mot_de_passe):
            # Sauvegarde en session
            session['eleveur_id'] = eleveur.id
            session['eleveur_nom'] = eleveur.nom
            session['eleveur_email'] = eleveur.email

            return jsonify({
                "message": f"Bienvenue {eleveur.nom}!",
                "user": {
                    "id": eleveur.id,
                    "nom": eleveur.nom,
                    "email": eleveur.email
                }
            }), 200
        else:
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    except Exception as e:
        return jsonify({"error": f"Erreur de connexion: {str(e)}"}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if Eleveur.query.filter_by(email=data.get('email')).first():
            return jsonify({"error": "Cet email est déjà utilisé"}), 400

        eleveur = Eleveur(
            nom=data.get('nom'),
            email=data.get('email'),
            mot_de_passe=generate_password_hash(data.get('mot_de_passe')),
            telephone=data.get('telephone'),
            adresse=data.get('adresse')
        )

        db.session.add(eleveur)
        db.session.commit()

        return jsonify({"message": "Compte créé avec succès !"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erreur lors de la création du compte: {str(e)}"}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Déconnexion réussie"}), 200


@auth_bp.route('/profile', methods=['GET'])
def profile():
    if 'eleveur_id' not in session:
        return jsonify({"error": "Non authentifié"}), 401

    try:
        eleveur = Eleveur.query.get(session['eleveur_id'])
        if not eleveur:
            return jsonify({"error": "Utilisateur introuvable"}), 404

        return jsonify({
            "id": eleveur.id,
            "nom": eleveur.nom,
            "email": eleveur.email,
            "telephone": eleveur.telephone,
            "adresse": eleveur.adresse
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500
