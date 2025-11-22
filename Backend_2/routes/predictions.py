from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from modeles.models import db, Bande, Consommation, Depense, Traitement, Animal
from datetime import datetime, timedelta
from sqlalchemy import func, extract

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/')
def predictions_page():
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Récupérer les données pour les statistiques
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        
        # Calculer les totaux pour chaque bande
        bandes_avec_stats = []
        depenses_totales = []
        consommations_totales = []
        
        for bande in bandes:
            # Dépenses totales de la bande
            total_depenses = db.session.query(func.sum(Depense.montant)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            # Consommation totale d'aliment
            total_consommation = db.session.query(func.sum(Consommation.aliment_kg)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            # Nombre de traitements
            traitements_count = Traitement.query.filter_by(bande_id=bande.id).count()
            
            bande_stats = {
                'id': bande.id,
                'nom_bande': bande.nom_bande,
                'statut': bande.statut,
                'nombre_initial': bande.nombre_initial,
                'depenses_total': round(total_depenses, 2),
                'consommation_total': round(total_consommation, 2),
                'traitements_count': traitements_count
            }
            
            bandes_avec_stats.append(bande_stats)
            depenses_totales.append(total_depenses)
            consommations_totales.append(total_consommation)
        
        # Statistiques générales
        total_bandes = len(bandes)
        bandes_actives = len([b for b in bandes if b.statut == 'active'])
        total_animaux = sum(b.nombre_initial for b in bandes)
        total_depenses_global = sum(depenses_totales)
        total_traitements = sum(b['traitements_count'] for b in bandes_avec_stats)
        
        # Pour les graphiques
        depenses_max = max(depenses_totales) if depenses_totales else 1
        consommation_max = max(consommations_totales) if consommations_totales else 1
        
        return render_template('predictions.html',
                             bandes=bandes_avec_stats,
                             bandes_count=bandes_actives,
                             animaux_count=total_animaux,
                             depenses_total=round(total_depenses_global, 2),
                             traitements_count=total_traitements,
                             depenses_max=depenses_max,
                             consommation_max=consommation_max)
        
    except Exception as e:
        return render_template('predictions.html',
                             bandes=[],
                             bandes_count=0,
                             animaux_count=0,
                             depenses_total=0,
                             traitements_count=0,
                             error=str(e))

@predictions_bp.route('/statistiques/globales', methods=['GET'])
def get_statistiques_globales():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Statistiques mensuelles
        maintenant = datetime.now()
        debut_mois = maintenant.replace(day=1)
        
        # Dépenses du mois
        depenses_mois = db.session.query(func.sum(Depense.montant)).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Depense.date >= debut_mois
        ).scalar() or 0
        
        # Consommation du mois
        consommation_mois = db.session.query(func.sum(Consommation.aliment_kg)).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Consommation.date >= debut_mois
        ).scalar() or 0
        
        # Traitements du mois
        traitements_mois = Traitement.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Traitement.date >= debut_mois
        ).count()
        
        return jsonify({
            'depenses_mois': round(depenses_mois, 2),
            'consommation_mois': round(consommation_mois, 2),
            'traitements_mois': traitements_mois,
            'mois': debut_mois.strftime('%B %Y')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@predictions_bp.route('/tendances', methods=['GET'])
def get_tendances():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Dépenses des 6 derniers mois
        date_limite = datetime.now() - timedelta(days=180)
        
        depenses_par_mois = db.session.query(
            extract('year', Depense.date).label('annee'),
            extract('month', Depense.date).label('mois'),
            func.sum(Depense.montant).label('total')
        ).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Depense.date >= date_limite
        ).group_by('annee', 'mois').order_by('annee', 'mois').all()
        
        tendances = []
        for dep in depenses_par_mois:
            tendances.append({
                'periode': f"{int(dep.mois)}/{int(dep.annee)}",
                'total': round(dep.total, 2)
            })
        
        return jsonify({'tendances': tendances})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400