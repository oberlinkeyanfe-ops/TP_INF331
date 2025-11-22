from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from modeles.models import db, Eleveur

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            mot_de_passe = request.form.get('mot_de_passe')

            if not email or not mot_de_passe:
                flash('⚠️ Veuillez remplir tous les champs', 'error')
                return render_template('auth.html')

            # Recherche de l'éleveur
            eleveur = Eleveur.query.filter_by(email=email).first()

            if eleveur and check_password_hash(eleveur.mot_de_passe, mot_de_passe):
                session['eleveur_id'] = eleveur.id
                session['eleveur_nom'] = eleveur.nom
                session['eleveur_email'] = eleveur.email
                
                flash(f'✅ Bienvenue {eleveur.nom}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('❌ Email ou mot de passe incorrect', 'error')
                return render_template('auth.html')

        except Exception as e:
            flash(f'❌ Erreur de connexion: {str(e)}', 'error')
            return render_template('auth.html')

    return render_template('auth.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.form
        
        # Vérifier si l'email existe déjà
        if Eleveur.query.filter_by(email=data.get('email')).first():
            flash('❌ Cet email est déjà utilisé', 'error')
            return render_template('auth.html')
        
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
        
        flash('✅ Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur lors de la création du compte: {str(e)}', 'error')
        return render_template('auth.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('👋 Vous avez été déconnecté avec succès', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET'])
def profile():
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        eleveur = Eleveur.query.get(session['eleveur_id'])
        return render_template('profile.html', eleveur=eleveur)
        
    except Exception as e:
        flash(f'❌ Erreur: {str(e)}', 'error')
        return redirect(url_for('dashboard'))