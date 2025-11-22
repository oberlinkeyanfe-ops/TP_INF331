from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from modeles.models import db, Bande, Animal, Consommation, Depense, Traitement, Intervention
from datetime import datetime, timedelta
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard_page():
    if 'eleveur_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Statistiques générales
        bandes_actives = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'], 
            statut='active'
        ).count()
        
        total_animaux = db.session.query(func.sum(Bande.nombre_initial)).filter_by(
            eleveur_id=session['eleveur_id']
        ).scalar() or 0
        
        total_depenses = db.session.query(func.sum(Depense.montant)).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).scalar() or 0
        
        total_traitements = Traitement.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).count()
        
        # Dernières activités
        dernieres_consommations = Consommation.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Consommation.date.desc()).limit(5).all()
        
        dernieres_depenses = Depense.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Depense.date.desc()).limit(5).all()
        
        # Bandes nécessitant attention
        bandes_attention = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).filter(
            (Bande.nombre_morts_totaux > Bande.nombre_initial * 0.1) |  # Plus de 10% de mortalité
            (Bande.age_moyen > 180)  # Âge avancé
        ).all()

        # Nouvelles statistiques
        nb_nouveaux_nes = db.session.query(func.sum(Animal.nouveaux_nes)).filter_by(
            eleveur_id=session['eleveur_id']
        ).scalar() or 0

        nb_morts = db.session.query(func.sum(Animal.nombre_morts)).filter_by(
            eleveur_id=session['eleveur_id']
        ).scalar() or 0

        nb_maladies_rencontrees = db.session.query(func.count(Traitement.id.distinct())).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).scalar() or 0

        nb_malades = db.session.query(func.count(Animal.id)).join(Traitement).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).scalar() or 0

        nb_epidemies = db.session.query(func.count(Intervention.id)).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Intervention.type == 'epidemie'
        ).scalar() or 0

        # Passer toutes les variables au template
        return render_template(
            'dashboard.html',
            bandes_count=0,
            animaux_count=0,
            depenses_total=0,
            traitements_count=0,
            dernieres_consommations=[],
            dernieres_depenses=[],
            bandes_attention=[],
            nb_nouveaux_nes=0,
            nb_morts=0,
            nb_maladies_rencontrees=0,
            nb_malades=0,
            nb_epidemies=0,
            error=str(e)
        )

    except Exception as e:
    # Passer toutes les variables au template en cas d'erreur
        return render_template(
            'dashboard.html',
            bandes_count=0,
            animaux_count=0,
            depenses_total=0,
            traitements_count=0,
            dernieres_consommations=[],
            dernieres_depenses=[],
            bandes_attention=[],
            nb_nouveaux_nes=0,
            nb_morts=0,
            nb_maladies_rencontrees=0,
            nb_malades=0,
            nb_epidemies=0,
            error=str(e)
        )

@dashboard_bp.route('/statistiques/rapides', methods=['GET'])
def get_statistiques_rapides():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Statistiques du mois en cours
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
        
        # Nouveaux traitements du mois
        traitements_mois = Traitement.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Traitement.date >= debut_mois
        ).count()
        
        # Interventions du mois
        interventions_mois = Intervention.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id'],
            Intervention.date >= debut_mois
        ).count()
        
        return jsonify({
            'depenses_mois': round(depenses_mois, 2),
            'consommation_mois': round(consommation_mois, 2),
            'traitements_mois': traitements_mois,
            'interventions_mois': interventions_mois,
            'mois': debut_mois.strftime('%B %Y')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@dashboard_bp.route('/alertes', methods=['GET'])
def get_alertes():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        alertes = []
        
        # Vérifier les bandes avec mortalité élevée
        bandes_mortalite = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).filter(
            Bande.nombre_morts_totaux > Bande.nombre_initial * 0.05  # Plus de 5% de mortalité
        ).all()
        
        for bande in bandes_mortalite:
            taux_mortalite = (bande.nombre_morts_totaux / bande.nombre_initial) * 100
            alertes.append({
                'type': 'mortalite',
                'niveau': 'danger',
                'message': f"Bande {bande.nom_bande}: Taux de mortalité élevé ({taux_mortalite:.1f}%)",
                'bande_id': bande.id
            })
        
        # Vérifier les traitements manquants (plus de 15 jours sans traitement)
        date_limite = datetime.now().date() - timedelta(days=15)
        bandes_sans_traitement = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).outerjoin(Traitement).filter(
            (Traitement.id.is_(None)) | 
            (Traitement.date < date_limite)
        ).all()
        
        for bande in bandes_sans_traitement:
            alertes.append({
                'type': 'traitement',
                'niveau': 'warning',
                'message': f"Bande {bande.nom_bande}: Aucun traitement récent",
                'bande_id': bande.id
            })
        
        return jsonify({'alertes': alertes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@dashboard_bp.route('/performance/bandes', methods=['GET'])
def get_performance_bandes():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        
        performance = []
        for bande in bandes:
            # Calculer le coût par animal
            total_depenses = db.session.query(func.sum(Depense.montant)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            cout_par_animal = total_depenses / bande.nombre_initial if bande.nombre_initial > 0 else 0
            
            # Calculer la consommation moyenne
            total_consommation = db.session.query(func.sum(Consommation.aliment_kg)).filter_by(
                bande_id=bande.id
            ).scalar() or 0
            
            consommation_par_animal = total_consommation / bande.nombre_initial if bande.nombre_initial > 0 else 0
            
            performance.append({
                'bande_id': bande.id,
                'nom_bande': bande.nom_bande,
                'statut': bande.statut,
                'nombre_animaux': bande.nombre_initial,
                'cout_par_animal': round(cout_par_animal, 2),
                'consommation_par_animal': round(consommation_par_animal, 2),
                'taux_mortalite': round((bande.nombre_morts_totaux / bande.nombre_initial) * 100, 2) if bande.nombre_initial > 0 else 0
            })
        
        return jsonify({'performance': performance})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400