from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from modeles.models import db, Eleveur

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        mot_de_passe = data.get('mot_de_passe')
        remember = data.get('remember', False)

        print(f"[AUTH] Tentative de login: email={email}")

        if not email or not mot_de_passe:
            return jsonify({"error": "Veuillez remplir tous les champs"}), 400

        # Recherche de l'éleveur
        eleveur = Eleveur.query.filter_by(email=email).first()
        
        if eleveur and check_password_hash(eleveur.mot_de_passe, mot_de_passe):
            # ⭐ STOCKER DANS FLASK-SESSION
            session['eleveur_id'] = eleveur.id
            session['eleveur_nom'] = eleveur.nom
            session['eleveur_email'] = eleveur.email
            
            # Si "se souvenir de moi", rendre la session permanente
            session.permanent = bool(remember)
            
            # Forcer la sauvegarde
            session.modified = True
            
            print(f"[AUTH] ✅ Login réussi: user_id={eleveur.id}, nom={eleveur.nom}")
            print(f"[SESSION] Contenu: {dict(session)}")
            
            return jsonify({
                "message": f"Bienvenue {eleveur.nom}!",
                "user": {
                    "id": eleveur.id,
                    "nom": eleveur.nom,
                    "email": eleveur.email
                }
            }), 200
        else:
            print(f"[AUTH] ❌ Login échoué pour email={email}")
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    except Exception as e:
        print(f"[AUTH] ❌ Erreur login: {str(e)}")
        return jsonify({"error": f"Erreur de connexion: {str(e)}"}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Vérifier si l'email existe déjà
        if Eleveur.query.filter_by(email=data.get('email')).first():
            return jsonify({"error": "Cet email est déjà utilisé"}), 400

        # Créer le nouvel éleveur
        eleveur = Eleveur(
            nom=data.get('nom'),
            email=data.get('email'),
            mot_de_passe=generate_password_hash(data.get('mot_de_passe')),
            telephone=data.get('telephone'),
            adresse=data.get('adresse')
        )

        db.session.add(eleveur)
        db.session.commit()

        print(f"[AUTH] ✅ Nouvel utilisateur: {eleveur.email}")
        
        return jsonify({
            "message": "Compte créé avec succès !",
            "user": {
                "id": eleveur.id,
                "nom": eleveur.nom,
                "email": eleveur.email
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"[AUTH] ❌ Erreur register: {str(e)}")
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


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Vérifie si l'utilisateur est connecté"""
    if 'eleveur_id' in session:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": session['eleveur_id'],
                "nom": session.get('eleveur_nom'),
                "email": session.get('eleveur_email')
            }
        }), 200
    return jsonify({"authenticated": False}), 401