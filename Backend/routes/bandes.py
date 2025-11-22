from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from modeles.models import db, Bande, Animal
from datetime import datetime, date
from sqlalchemy import or_, func
import csv
import io
from werkzeug.utils import secure_filename
import os

bandes_bp = Blueprint('bandes', __name__)

# Configuration pour l'upload de fichiers
ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bandes_bp.route('/')
def bandes_page():
    """Redirige vers la page de gestion"""
    return redirect(url_for('bandes.gestion_bandes'))

@bandes_bp.route('/gestion')
def gestion_bandes():
    """Page de gestion complète des bandes"""
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        bandes = Bande.query.filter_by(
            eleveur_id=session['eleveur_id']
        ).order_by(Bande.date_arrivee.desc()).all()
        
        return render_template('bandes.html', bandes=bandes, gestion_mode=True, today=date.today().strftime('%Y-%m-%d'))
        
    except Exception as e:
        return render_template('bandes.html', bandes=[], error=str(e), gestion_mode=True, today=date.today().strftime('%Y-%m-%d'))

@bandes_bp.route('/create', methods=['POST'])
def create_bande():
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        data = request.form
        
        bande = Bande(
            eleveur_id=session['eleveur_id'],
            nom_bande=data['nom_bande'],
            date_arrivee=datetime.strptime(data['date_arrivee'], '%Y-%m-%d').date(),
            race=data.get('race'),
            fournisseur=data.get('fournisseur'),
            nombre_initial=int(data['nombre_initial']),
            poids_moyen_initial=float(data.get('poids_moyen_initial', 0)),
            age_moyen=float(data.get('age_moyen', 0)),
            nombre_nouveaux_nes=int(data.get('nombre_nouveaux_nes', 0)),
            nombre_morts_totaux=int(data.get('nombre_morts_totaux', 0)),
            statut=data.get('statut', 'active'),
            nbre_ajoute=0
        )
        
        db.session.add(bande)
        db.session.commit()
        flash('✅ Bande créée avec succès!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur: {str(e)}', 'error')
    
    return redirect(url_for('bandes.bandes_page'))

# NOUVELLE ROUTE : Importation de bandes via CSV
@bandes_bp.route('/import-csv', methods=['POST'])
def import_bandes_csv():
    """Importe des bandes à partir d'un fichier CSV"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Vérifier si un fichier a été uploadé
        if 'csv_file' not in request.files:
            flash('❌ Aucun fichier sélectionné', 'error')
            return redirect(url_for('bandes.bandes_page'))
        
        file = request.files['csv_file']
        
        # Vérifier si un fichier a été sélectionné
        if file.filename == '':
            flash('❌ Aucun fichier sélectionné', 'error')
            return redirect(url_for('bandes.bandes_page'))
        
        # Vérifier l'extension du fichier
        if not allowed_file(file.filename):
            flash('❌ Format de fichier non supporté. Utilisez un fichier CSV.', 'error')
            return redirect(url_for('bandes.bandes_page'))
        
        # Lire le fichier CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Vérifier les colonnes requises
        required_columns = ['nom_bande', 'date_arrivee', 'nombre_initial']
        if not all(column in csv_reader.fieldnames for column in required_columns):
            flash(f'❌ Colonnes requises manquantes. Assurez-vous d\'avoir: {", ".join(required_columns)}', 'error')
            return redirect(url_for('bandes.bandes_page'))
        
        bandes_importees = 0
        erreurs = []
        
        for ligne_num, row in enumerate(csv_reader, start=2):  # start=2 car la ligne 1 est l'en-tête
            try:
                # Nettoyer les données
                nom_bande = row['nom_bande'].strip()
                date_arrivee = datetime.strptime(row['date_arrivee'].strip(), '%Y-%m-%d').date()
                nombre_initial = int(row['nombre_initial'])
                
                # Vérifier si la bande existe déjà pour cet éleveur
                bande_existante = Bande.query.filter_by(
                    eleveur_id=session['eleveur_id'],
                    nom_bande=nom_bande
                ).first()
                
                if bande_existante:
                    erreurs.append(f"Ligne {ligne_num}: Bande '{nom_bande}' existe déjà")
                    continue
                
                # Créer la nouvelle bande
                bande = Bande(
                    eleveur_id=session['eleveur_id'],
                    nom_bande=nom_bande,
                    date_arrivee=date_arrivee,
                    race=row.get('race', '').strip(),
                    fournisseur=row.get('fournisseur', '').strip(),
                    nombre_initial=nombre_initial,
                    poids_moyen_initial=float(row['poids_moyen_initial']) if row.get('poids_moyen_initial') else 0,
                    age_moyen=float(row['age_moyen']) if row.get('age_moyen') else 0,
                    nombre_nouveaux_nes=int(row['nombre_nouveaux_nes']) if row.get('nombre_nouveaux_nes') else 0,
                    nombre_morts_totaux=int(row['nombre_morts_totaux']) if row.get('nombre_morts_totaux') else 0,
                    statut=row.get('statut', 'active').strip(),
                    nbre_ajoute=0
                )
                
                db.session.add(bande)
                bandes_importees += 1
                
            except ValueError as e:
                erreurs.append(f"Ligne {ligne_num}: Erreur de format - {str(e)}")
            except Exception as e:
                erreurs.append(f"Ligne {ligne_num}: Erreur - {str(e)}")
        
        # Commit des changements
        if bandes_importees > 0:
            db.session.commit()
            flash(f'✅ {bandes_importees} bande(s) importée(s) avec succès!', 'success')
        else:
            db.session.rollback()
        
        # Afficher les erreurs s'il y en a
        if erreurs:
            erreurs_message = f"❌ {len(erreurs)} erreur(s) lors de l'importation:"
            for erreur in erreurs[:5]:  # Afficher seulement les 5 premières erreurs
                erreurs_message += f"<br>• {erreur}"
            if len(erreurs) > 5:
                erreurs_message += f"<br>• ... et {len(erreurs) - 5} autre(s) erreur(s)"
            flash(erreurs_message, 'warning')
        
        return redirect(url_for('bandes.bandes_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur lors de l\'importation: {str(e)}', 'error')
        return redirect(url_for('bandes.bandes_page'))

# NOUVELLE ROUTE : Télécharger un template CSV
@bandes_bp.route('/download-template')
def download_template():
    """Télécharge un template CSV pour l'importation"""
    try:
        # Créer le template CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes avec descriptions
        headers = [
            'nom_bande',           # Nom de la bande (requis)
            'date_arrivee',        # Date d'arrivée YYYY-MM-DD (requis)
            'race',                # Race des animaux
            'fournisseur',         # Nom du fournisseur
            'nombre_initial',      # Nombre initial d'animaux (requis)
            'poids_moyen_initial', # Poids moyen initial en kg
            'age_moyen',          # Âge moyen en jours
            'nombre_nouveaux_nes', # Nombre de nouveaux nés
            'nombre_morts_totaux', # Nombre total de morts
            'statut'              # Statut (active, terminee, archivee)
        ]
        
        writer.writerow(headers)
        
        # Exemple de données
        example_data = [
            'Bande A', '2024-01-15', 'Poulet de chair', 'Fournisseur Cameroun', 
            '500', '0.45', '1', '0', '0', 'active'
        ]
        writer.writerow(example_data)
        
        example_data2 = [
            'Bande B', '2024-02-01', 'Pondeuse', 'Élevage National', 
            '300', '1.2', '90', '25', '5', 'active'
        ]
        writer.writerow(example_data2)
        
        # Préparer la réponse
        output.seek(0)
        response = jsonify({'csv': output.getvalue()})
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NOUVELLE ROUTE : API pour l'importation CSV
@bandes_bp.route('/api/import-csv', methods=['POST'])
def api_import_bandes_csv():
    """API pour l'importation de bandes via CSV (pour AJAX)"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        if 'csv_file' not in request.files:
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        file = request.files['csv_file']
        
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Format de fichier non supporté. Utilisez un fichier CSV.'}), 400
        
        # Lire le fichier CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Vérifier les colonnes requises
        required_columns = ['nom_bande', 'date_arrivee', 'nombre_initial']
        if not all(column in csv_reader.fieldnames for column in required_columns):
            return jsonify({
                'error': f'Colonnes requises manquantes: {", ".join(required_columns)}',
                'colonnes_trouvees': csv_reader.fieldnames
            }), 400
        
        bandes_importees = 0
        erreurs = []
        
        for ligne_num, row in enumerate(csv_reader, start=2):
            try:
                nom_bande = row['nom_bande'].strip()
                date_arrivee = datetime.strptime(row['date_arrivee'].strip(), '%Y-%m-%d').date()
                nombre_initial = int(row['nombre_initial'])
                
                # Vérifier si la bande existe déjà
                bande_existante = Bande.query.filter_by(
                    eleveur_id=session['eleveur_id'],
                    nom_bande=nom_bande
                ).first()
                
                if bande_existante:
                    erreurs.append(f"Ligne {ligne_num}: Bande '{nom_bande}' existe déjà")
                    continue
                
                # Créer la bande
                bande = Bande(
                    eleveur_id=session['eleveur_id'],
                    nom_bande=nom_bande,
                    date_arrivee=date_arrivee,
                    race=row.get('race', '').strip(),
                    fournisseur=row.get('fournisseur', '').strip(),
                    nombre_initial=nombre_initial,
                    poids_moyen_initial=float(row['poids_moyen_initial']) if row.get('poids_moyen_initial') else 0,
                    age_moyen=float(row['age_moyen']) if row.get('age_moyen') else 0,
                    nombre_nouveaux_nes=int(row['nombre_nouveaux_nes']) if row.get('nombre_nouveaux_nes') else 0,
                    nombre_morts_totaux=int(row['nombre_morts_totaux']) if row.get('nombre_morts_totaux') else 0,
                    statut=row.get('statut', 'active').strip(),
                    nbre_ajoute=0
                )
                
                db.session.add(bande)
                bandes_importees += 1
                
            except ValueError as e:
                erreurs.append(f"Ligne {ligne_num}: Erreur de format - {str(e)}")
            except Exception as e:
                erreurs.append(f"Ligne {ligne_num}: Erreur - {str(e)}")
        
        if bandes_importees > 0:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'bandes_importees': bandes_importees,
            'erreurs': erreurs,
            'message': f'{bandes_importees} bande(s) importée(s) avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'importation: {str(e)}'}), 500

@bandes_bp.route('/<int:id>', methods=['GET'])
def get_bande(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        return jsonify(bande.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bandes_bp.route('/<int:id>', methods=['PUT'])
def update_bande(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(bande, key) and key not in ['id', 'eleveur_id', 'created_at', 'updated_at', 'nbre_ajoute']:
                if key == 'date_arrivee' and value:
                    setattr(bande, key, datetime.strptime(value, '%Y-%m-%d').date())
                elif key in ['nombre_initial', 'nombre_nouveaux_nes', 'nombre_morts_totaux']:
                    setattr(bande, key, int(value) if value else 0)
                elif key in ['poids_moyen_initial', 'age_moyen']:
                    setattr(bande, key, float(value) if value else 0)
                else:
                    setattr(bande, key, value)
        
        db.session.commit()
        return jsonify(bande.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur modification: {str(e)}'}), 400

@bandes_bp.route('/<int:id>/delete', methods=['POST'])
def delete_bande(id):
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        db.session.delete(bande)
        db.session.commit()
        flash('✅ Bande supprimée avec succès!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur suppression: {str(e)}', 'error')
    
    return redirect(url_for('bandes.bandes_page'))

@bandes_bp.route('/search', methods=['GET'])
def search_bandes():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        search_term = request.args.get('q', '')
        
        if search_term:
            bandes = Bande.query.filter(
                Bande.eleveur_id == session['eleveur_id'],
                or_(
                    Bande.nom_bande.ilike(f'%{search_term}%'),
                    Bande.race.ilike(f'%{search_term}%'),
                    Bande.fournisseur.ilike(f'%{search_term}%')
                )
            ).all()
        else:
            bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        
        return jsonify([bande.to_dict() for bande in bandes])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bandes_bp.route('/statistiques', methods=['GET'])
def get_statistiques():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Statistiques générales
        total_bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).count()
        bandes_actives = Bande.query.filter_by(eleveur_id=session['eleveur_id'], statut='active').count()
        
        # CORRECTION : Calcul du total des animaux (initiaux + ajoutés)
        total_stats = db.session.query(
            func.sum(Bande.nombre_initial).label('total_initiaux'),
            func.sum(Bande.nbre_ajoute).label('total_ajoutes')
        ).filter_by(eleveur_id=session['eleveur_id']).first()
        
        total_animaux = (total_stats.total_initiaux or 0) + (total_stats.total_ajoutes or 0)
        
        return jsonify({
            'total_bandes': total_bandes,
            'bandes_actives': bandes_actives,
            'total_animaux': total_animaux,
            'animaux_initiaux': total_stats.total_initiaux or 0,
            'animaux_ajoutes': total_stats.total_ajoutes or 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# NOUVELLE ROUTE : Mettre à jour le compteur nbre_ajoute pour une bande
@bandes_bp.route('/<int:id>/update_ajoute', methods=['POST'])
def update_nbre_ajoute(id):
    """Met à jour le compteur nbre_ajoute basé sur les animaux ajoutés"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        # Calculer le total des animaux ajoutés (hors animaux initiaux)
        total_ajoute = db.session.query(func.sum(Animal.nombre)).filter(
            Animal.bande_id == id,
            Animal.etat_achat != 'né'  # Exclure les naissances si nécessaire
        ).scalar() or 0
        
        bande.nbre_ajoute = total_ajoute
        db.session.commit()
        
        return jsonify({
            'success': True,
            'nbre_ajoute': bande.nbre_ajoute,
            'message': 'Compteur mis à jour avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# NOUVELLE ROUTE : Synchroniser tous les compteurs nbre_ajoute
@bandes_bp.route('/sync-compteurs', methods=['POST'])
def sync_all_compteurs():
    """Synchronise tous les compteurs nbre_ajoute pour toutes les bandes"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        updated_count = 0
        
        for bande in bandes:
            total_ajoute = db.session.query(func.sum(Animal.nombre)).filter(
                Animal.bande_id == bande.id
            ).scalar() or 0
            
            if bande.nbre_ajoute != total_ajoute:
                bande.nbre_ajoute = total_ajoute
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            flash(f'✅ {updated_count} compteur(s) synchronisé(s)!', 'success')
        else:
            flash('ℹ️ Tous les compteurs sont déjà à jour!', 'info')
            
        return redirect(url_for('bandes.bandes_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur synchronisation: {str(e)}', 'error')
        return redirect(url_for('bandes.bandes_page'))

# NOUVELLE ROUTE : Obtenir les détails complets d'une bande avec ses animaux
@bandes_bp.route('/<int:id>/details', methods=['GET'])
def get_bande_details(id):
    """Retourne les détails complets d'une bande avec ses animaux"""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bande = Bande.query.filter_by(
            id=id, 
            eleveur_id=session['eleveur_id']
        ).first_or_404()
        
        # Récupérer les animaux de la bande
        animaux = Animal.query.filter_by(bande_id=id).all()
        
        bande_data = bande.to_dict()
        bande_data['animaux'] = [animal.to_dict() for animal in animaux]
        bande_data['total_animaux_actuels'] = bande.nombre_initial + bande.nbre_ajoute - bande.nombre_morts_totaux
        
        return jsonify(bande_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 404