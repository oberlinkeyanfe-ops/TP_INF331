from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from modeles.models import db, Bande, Consommation, Traitement, AnimalInfo, depense_elt
from datetime import datetime, timedelta
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)

# Reference consumption per week (same as frontend)
CONSUMPTION_REFERENCE = [
    {'week': 1, 'aliment_kg': 150, 'eau_litres': 300, 'prix_unitaire': 0.45},
    {'week': 2, 'aliment_kg': 420, 'eau_litres': 640, 'prix_unitaire': 0.45},
    {'week': 3, 'aliment_kg': 730, 'eau_litres': 980, 'prix_unitaire': 0.48},
    {'week': 4, 'aliment_kg': 1100, 'eau_litres': 1350, 'prix_unitaire': 0.5},
    {'week': 5, 'aliment_kg': 1450, 'eau_litres': 1680, 'prix_unitaire': 0.52},
    {'week': 6, 'aliment_kg': 1750, 'eau_litres': 1900, 'prix_unitaire': 0.55},
    {'week': 7, 'aliment_kg': 1950, 'eau_litres': 2050, 'prix_unitaire': 0.58},
    {'week': 8, 'aliment_kg': 2050, 'eau_litres': 2150, 'prix_unitaire': 0.6}
]


# Elementary expense reference (categories used in frontend)
ELEMENTARY_EXPENSES_REFERENCE = [
    {'key': 'chauffage', 'label': 'Chauffage', 'typical_monthly_fcfa': 50000},
    {'key': 'electricite', 'label': 'Électricité', 'typical_monthly_fcfa': 30000},
    {'key': 'transport', 'label': 'Transport', 'typical_monthly_fcfa': 20000},
    {'key': 'litiere', 'label': 'Copeaux / Litière', 'typical_monthly_fcfa': 8000},
    {'key': 'nettoyage', 'label': 'Nettoyage / Désinfection', 'typical_monthly_fcfa': 5000},
    {'key': 'maintenance', 'label': 'Maintenance', 'typical_monthly_fcfa': 15000},
    {'key': 'autres', 'label': 'Autres', 'typical_monthly_fcfa': 10000}
]


# Mortality reference by week (low / high %)
MORTALITY_REFERENCE = [
    {'week': 1, 'low': 0.0, 'high': 1.0},
    {'week': 2, 'low': 0.0, 'high': 0.8},
    {'week': 3, 'low': 0.0, 'high': 0.6},
    {'week': 4, 'low': 0.0, 'high': 0.5},
    {'week': 5, 'low': 0.0, 'high': 0.4},
    {'week': 6, 'low': 0.0, 'high': 0.4},
    {'week': 7, 'low': 0.0, 'high': 0.3},
    {'week': 8, 'low': 0.0, 'high': 0.3},
    {'week': 9, 'low': 0.0, 'high': 0.25},
    {'week': 10, 'low': 0.0, 'high': 0.25},
    {'week': 11, 'low': 0.0, 'high': 0.20},
    {'week': 12, 'low': 0.0, 'high': 0.20}
]


# Survival performance guidance thresholds
SURVIVAL_REFERENCE = {
    'excellent': 90,
    'good': 75,
    'warning': 60,
    'critical': 0
}


def ratio_score(ref_value, actual_value):
    """Return a 0-100 score comparing reference vs actual, or None when comparison is not meaningful.

    Important: do NOT treat "no reference" or "no data" as a perfect (100) score — return None so
    callers can decide how to present unknowns. This avoids false 100% when data is missing.
    """
    try:
        ref = float(ref_value) if ref_value is not None else None
        act = float(actual_value) if actual_value is not None else None
    except Exception:
        return None
    # If there's no meaningful reference or no actual data, return None -> unknown
    if ref is None or ref <= 0:
        return None
    if act is None or act <= 0:
        return None
    if act <= ref:
        return 100
    return max(0, min(100, int((ref / act) * 100)))


# Appliquer à toutes les routes du blueprint
@dashboard_bp.before_request
def require_login():
    """Vérifie l'authentification pour toutes les routes (session basée).
    Nous évitons d'utiliser flask-login ici car le projet n'initialise pas
    nécessairement un LoginManager dans `app.py` et cela provoquait des
    erreurs 500 lors des appels API non authentifiés.
    """
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

@dashboard_bp.route('/')
def dashboard_page():
    # Return dashboard data as JSON for the authenticated eleveur
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        # Statistiques générales
        bandes_actives = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'], 
            statut='active'
        ).count()
        
        total_animaux = db.session.query(func.sum(Bande.nombre_initial)).filter_by(
            eleveur_id=session['eleveur_id']
        ).scalar() or 0
        
        total_depenses = 0  # Depense model supprimé
        total_traitements = Traitement.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).count()
        
        # Dernières activités
        dernieres_consommations = Consommation.query.join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).order_by(Consommation.date.desc()).limit(5).all()
        
        dernieres_depenses = []  # Depense supprimé
        
        # Bandes nécessitant attention
        bandes_attention = Bande.query.filter_by(
            eleveur_id=session['eleveur_id'],
            statut='active'
        ).filter(
            (Bande.nombre_morts_totaux > Bande.nombre_initial * 0.1)
            | (Bande.age_moyen > 180)
        ).all()
        # Nouvelles statistiques alignées sur le modèle actuel (pas de modèle Animal/Intervention)
        nb_nouveaux_nes = 0
        nb_morts = db.session.query(func.sum(Bande.nombre_morts_totaux)).filter_by(
            eleveur_id=session['eleveur_id']
        ).scalar() or 0

        nb_maladies_rencontrees = db.session.query(func.count(Traitement.id.distinct())).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).scalar() or 0

        nb_malades = nb_maladies_rencontrees
        nb_epidemies = 0

        # Serializer helper (use to_dict if available)
        def serialize_list(items):
            result = []
            for it in items:
                if hasattr(it, 'to_dict'):
                    result.append(it.to_dict())
                else:
                    # fallback: include a minimal representation
                    result.append({c.name: getattr(it, c.name) for c in getattr(it.__class__, '__table__').columns})
            return result

        return jsonify({
            'bandes_actives': bandes_actives,
            'total_animaux': int(total_animaux),
            'total_depenses': float(total_depenses),
            'total_traitements': total_traitements,
            'dernieres_consommations': serialize_list(dernieres_consommations),
            'dernieres_depenses': serialize_list(dernieres_depenses),
            'bandes_attention': [b.to_dict() for b in bandes_attention],
            'nb_nouveaux_nes': int(nb_nouveaux_nes),
            'nb_morts': int(nb_morts),
            'nb_maladies_rencontrees': int(nb_maladies_rencontrees),
            'nb_malades': int(nb_malades),
            'nb_epidemies': int(nb_epidemies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/statistiques/rapides', methods=['GET'])
def get_statistiques_rapides():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    try:
        # Statistiques du mois en cours
        maintenant = datetime.now()
        debut_mois = maintenant.replace(day=1)
        
        # Dépenses du mois
        depenses_mois = 0  # Depense supprimé
        
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
        interventions_mois = 0  # Intervention supprimé
        
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
        for b in bandes:
            perf = compute_performance_for_band(b)
            base = {
                'bande_id': b.id,
                'nom_bande': b.nom_bande,
                'statut': b.statut,
                'nombre_animaux': b.nombre_initial,
            }
            performance.append({**base, **perf})

        return jsonify({'performance': performance})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dashboard_bp.route('/performance/map', methods=['GET'])
def get_performance_map():
    """Return a simple map of band_id -> performance_percent and components for all bands."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        result = {}
        for b in bandes:
            perf = compute_performance_for_band(b)
            pid = b.id
            result[str(pid)] = perf.get('performance_percent', 0) if perf.get('performance_percent') is not None else 0
            # include components
            result[f'components_{pid}'] = perf.get('subscores', {})
        return jsonify({'band_performance_map': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/performance/compare', methods=['GET'])
def compare_performance_sources():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        result = []
        for b in bandes:
            # compute a fresh per-band performance
            detail = compute_performance_for_band(b)
            # try to fetch the entry as would be in the list (same computation)
            list_entry = compute_performance_for_band(b)
            perf_list = list_entry.get('performance_percent')
            perf_detail = detail.get('performance_percent')
            result.append({
                'bande_id': b.id,
                'nom_bande': b.nom_bande,
                'perf_list': perf_list,
                'perf_detail': perf_detail,
                'diff': (perf_detail - perf_list) if (perf_detail is not None and perf_list is not None) else None,
                'subscores': detail.get('subscores')
            })
        return jsonify({'compare': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def compute_performance_for_band(bande):
    try:
        # Compute per-week consumption (kg) grouped by semaine_production
        consommations = Consommation.query.filter_by(bande_id=bande.id).all()
        consum_by_week = {}
        for c in consommations:
            w = int(c.semaine_production) if c.semaine_production is not None else None
            if not w:
                continue
            consum_by_week[w] = consum_by_week.get(w, 0) + float(c.aliment_kg or 0)

        # Weekly mortality from AnimalInfo (morts_semaine)
        animal_infos = AnimalInfo.query.filter_by(bande_id=bande.id).all()
        morts_by_week = {}
        for a in animal_infos:
            w = int(a.semaine_production) if a.semaine_production is not None else None
            if not w:
                continue
            morts_by_week[w] = morts_by_week.get(w, 0) + int(a.morts_semaine or 0)

        initial = bande.nombre_initial or 0
        if not initial or initial <= 0:
            # no meaningful baseline
            return {
                'consommation_par_poule_par_semaine': {},
                'mortalite_par_semaine_pct': {},
                'survie_par_semaine_pct': {},
                'subscores': {
                    'consumption': None,
                    'mortality': None,
                    'survival': None
                },
                'performance_percent': None
            }

        # Determine number of reference weeks to compare (use min of reference length and observed weeks if any)
        ref_weeks = {r['week']: r for r in CONSUMPTION_REFERENCE}
        max_ref_week = max(ref_weeks.keys()) if ref_weeks else 0
        weeks = sorted(set(list(consum_by_week.keys()) + list(morts_by_week.keys()) + list(ref_weeks.keys())))

        # Consumption performance: compare per-poule per-week to reference per-week
        # margin allowed (fraction): within +/- margin => perfect 100. Outside reduce linearly.
        margin = 0.05  # 5% margin
        consumption_per_week_pct = {}
        for w in weeks:
            actual_kg = consum_by_week.get(w, 0)
            actual_per_poule = actual_kg / initial
            ref = ref_weeks.get(w)
            ref_kg = ref['aliment_kg'] if ref else None
            ref_per_poule = (ref_kg / initial) if (ref_kg is not None) else None
            if ref_per_poule is None or ref_per_poule <= 0:
                consumption_per_week_pct[w] = None
                continue
            deviation = (actual_per_poule - ref_per_poule) / ref_per_poule
            if abs(deviation) <= margin:
                perf = 100
            else:
                effective = max(0.0, abs(deviation) - margin)
                # linear decay: 100 -> 0 when effective reaches 1.0 (100% deviation beyond margin)
                perf = int(max(0, round(100 * (1 - min(1.0, effective)))))
            consumption_per_week_pct[w] = perf

        # Mortality: per-week percent = (morts_week / initial) * 100; average across weeks with data
        mortality_week_pct = {}
        for w in weeks:
            morts = morts_by_week.get(w, None)
            if morts is None:
                mortality_week_pct[w] = None
            else:
                mortality_week_pct[w] = (morts / initial) * 100

        mortality_values = [v for v in mortality_week_pct.values() if v is not None]
        if mortality_values:
            mortality_avg = sum(mortality_values) / len(mortality_values)
        else:
            # fallback to band-level totals if weekly not available
            mortality_avg = (bande.nombre_morts_totaux or 0) / initial * 100

        mortality_perf = int(max(0, round(100 - mortality_avg)))

        # Survival derived from mortality
        survival_perf = int(max(0, round(100 - mortality_avg)))

        # Aggregate consumption performance average over weeks with values
        cons_values = [v for v in consumption_per_week_pct.values() if isinstance(v, (int, float))]
        consumption_perf = int(round(sum(cons_values) / len(cons_values))) if cons_values else None

        # We no longer expose a separate mortality performance. Survival is derived from mortality
        # and global performance uses only survival and consumption.
        subscores = {
            'consumption': consumption_perf,
            'survival': survival_perf
        }

        # Global performance is mean of survival and consumption (ignore missing values)
        available = [v for v in subscores.values() if isinstance(v, (int, float))]
        perf_percent = int(round(sum(available) / len(available))) if available else None

        return {
            'consommation_par_poule_par_semaine': {str(k): round(v / initial, 4) if initial else 0 for k, v in consum_by_week.items()},
            'mortalite_par_semaine_pct': {str(k): (v if v is not None else None) for k, v in mortality_week_pct.items()},
            'survie_par_semaine_pct': {str(k): (100 - v if v is not None else None) for k, v in mortality_week_pct.items()},
            'subscores': subscores,
            'performance_percent': perf_percent
        }
    except Exception as e:
        # Log and return safe defaults to avoid 500s
        try:
            from flask import current_app
            current_app.logger.exception('Error computing performance for band %s: %s', bande.id if hasattr(bande, 'id') else str(bande), e)
        except Exception:
            print('Error computing performance for band', getattr(bande, 'id', str(bande)), e)
        return {
            'consommation_par_animal': 0,
            'cout_total': 0,
            'cout_aliment': 0,
            'cout_traitements': 0,
            'cout_depenses': 0,
            'ref_total_cost': 0,
            'ref_total_kg': 0,
            'subscores': {
                'cost': 0,
                'consumption': 0,
                'treatment': 0,
                'elementary': 0
            },
            'performance_percent': 0
        }


@dashboard_bp.route('/references', methods=['GET'])
def get_references():
    """Return canonical reference tables used by the frontend to compute performance.

    Response example:
    {
      'consumption_reference': [...],
      'elementary_expenses_reference': [...],
      'mortality_reference': [...],
      'survival_reference': {...}
    }
    """
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    try:
        return jsonify({
            'consumption_reference': CONSUMPTION_REFERENCE,
            'elementary_expenses_reference': ELEMENTARY_EXPENSES_REFERENCE,
            'mortality_reference': MORTALITY_REFERENCE,
            'survival_reference': SURVIVAL_REFERENCE
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/consommation/par_bande', methods=['GET'])
def consommation_par_bande():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        rows = db.session.query(
            Bande.id,
            Bande.nom_bande,
            func.coalesce(func.sum(Consommation.aliment_kg), 0).label('total_aliment_kg'),
            func.coalesce(func.sum(Consommation.eau_litres), 0).label('total_eau_litres')
        ).outerjoin(Consommation, Consommation.bande_id == Bande.id).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).group_by(Bande.id, Bande.nom_bande).all()

        result = []
        for r in rows:
            result.append({
                'bande_id': r.id,
                'nom_bande': r.nom_bande,
                'total_aliment_kg': float(r.total_aliment_kg or 0),
                'total_eau_litres': float(r.total_eau_litres or 0)
            })
        return jsonify({'consommation_par_bande': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dashboard_bp.route('/couts/par_bande', methods=['GET'])
def couts_par_bande():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        result = []
        for b in bandes:
            total_cons_cout = db.session.query(func.coalesce(func.sum(Consommation.cout_aliment), 0)).filter_by(bande_id=b.id).scalar() or 0
            total_depenses = db.session.query(func.coalesce(func.sum(depense_elt.cout), 0)).filter_by(bande_id=b.id).scalar() or 0
            total_traitements = db.session.query(func.coalesce(func.sum(Traitement.cout), 0)).filter_by(bande_id=b.id).scalar() or 0
            total = float(total_cons_cout or 0) + float(total_depenses or 0) + float(total_traitements or 0)
            result.append({
                'bande_id': b.id,
                'nom_bande': b.nom_bande,
                'cout_aliment': float(total_cons_cout or 0),
                'cout_depenses': float(total_depenses or 0),
                'cout_traitements': float(total_traitements or 0),
                'cout_total': total
            })
        return jsonify({'couts_par_bande': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dashboard_bp.route('/trends/poids', methods=['GET'])
def trends_poids():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        rows = db.session.query(
            AnimalInfo.semaine_production,
            func.avg(AnimalInfo.poids_moyen).label('mean_weight')
        ).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).group_by(AnimalInfo.semaine_production).order_by(AnimalInfo.semaine_production).all()

        result = [{'week': int(r.semaine_production), 'mean_weight': float(r.mean_weight or 0)} for r in rows]
        return jsonify({'weight_trend': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dashboard_bp.route('/trends/consommation_hebdo', methods=['GET'])
def trends_consommation_hebdo():
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        rows = db.session.query(
            Consommation.semaine_production,
            func.coalesce(func.sum(Consommation.aliment_kg), 0).label('total_kg')
        ).join(Bande).filter(
            Bande.eleveur_id == session['eleveur_id']
        ).group_by(Consommation.semaine_production).order_by(Consommation.semaine_production).all()

        result = [{'week': int(r.semaine_production or 0), 'total_kg': float(r.total_kg or 0)} for r in rows]
        return jsonify({'consommation_trend': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@dashboard_bp.route('/global-v2', methods=['GET'])
def dashboard_global_v2():
    """Endpoint consolidé qui renvoie résumé, per-band performance, tendances.
    Accepts optional query params: period_days=int, start=YYYY-MM-DD, end=YYYY-MM-DD
    """
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        eleveur_id = session['eleveur_id']

        # parse filters
        period_days = request.args.get('period_days', type=int)
        start = request.args.get('start')
        end = request.args.get('end')

        # base summary (reuse existing logic)
        bandes_actives = Bande.query.filter_by(eleveur_id=eleveur_id, statut='active').count()
        total_animaux = db.session.query(func.sum(Bande.nombre_initial)).filter_by(eleveur_id=eleveur_id).scalar() or 0
        nb_morts = db.session.query(func.sum(Bande.nombre_morts_totaux)).filter_by(eleveur_id=eleveur_id).scalar() or 0

        # performance per bande
        perf_rows = Bande.query.filter_by(eleveur_id=eleveur_id).all()
        performance = []
        for b in perf_rows:
            total_cons = db.session.query(func.coalesce(func.sum(Consommation.aliment_kg), 0)).filter_by(bande_id=b.id).scalar() or 0
            consommation_par_animal = float(total_cons) / b.nombre_initial if b.nombre_initial else 0
            taux_mortalite = (float(b.nombre_morts_totaux) / b.nombre_initial * 100) if b.nombre_initial else 0
            # estimate gains rudimentaire si cout_unitaire disponible
            gains = 0
            if b.cout_unitaire:
                gains = (b.nombre_initial - (b.nombre_morts_totaux or 0)) * (b.cout_unitaire or 0)
            performance.append({
                'bande_id': b.id,
                'nom_bande': b.nom_bande,
                'statut': b.statut,
                'nombre_animaux': b.nombre_initial,
                'consommation_par_animal': round(consommation_par_animal, 2),
                'taux_mortalite': round(taux_mortalite, 2),
                'gains': float(gains)
            })

        # trends: weight and consumption (respect filters)
        # for simplicity, ignore date filters for now; reuse existing queries
        weight_rows = db.session.query(AnimalInfo.semaine_production, func.avg(AnimalInfo.poids_moyen).label('mean_weight')).join(Bande).filter(Bande.eleveur_id == eleveur_id).group_by(AnimalInfo.semaine_production).order_by(AnimalInfo.semaine_production).all()
        weight_trend = [{'week': int(r.semaine_production), 'mean_weight': float(r.mean_weight or 0)} for r in weight_rows]

        cons_rows = db.session.query(Consommation.semaine_production, func.coalesce(func.sum(Consommation.aliment_kg), 0).label('total_kg')).join(Bande).filter(Bande.eleveur_id == eleveur_id).group_by(Consommation.semaine_production).order_by(Consommation.semaine_production).all()
        consommation_trend = [{'week': int(r.semaine_production or 0), 'total_kg': float(r.total_kg or 0)} for r in cons_rows]

        return jsonify({
            'bandes_actives': bandes_actives,
            'total_animaux': int(total_animaux),
            'nb_morts': int(nb_morts),
            'performance': performance,
            'weight_trend': weight_trend,
            'consommation_trend': consommation_trend
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/bande/details/<int:bande_id>', methods=['GET'])
def bande_details(bande_id):
    """Return detailed info for a bande: race, recent treatments, top aliment, IC estimate, mortality/survival rates and performance."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        b = Bande.query.filter_by(id=bande_id, eleveur_id=session['eleveur_id']).first()
        if not b:
            return jsonify({'error': 'Bande introuvable'}), 404

        # Recent treatments (last 5)
        traitements = Traitement.query.filter_by(bande_id=b.id).order_by(Traitement.date.desc()).limit(5).all()
        traitements_list = [t.to_dict() for t in traitements]

        # Top aliment by total kg
        top_alim_row = db.session.query(Consommation.type_aliment, func.coalesce(func.sum(Consommation.aliment_kg), 0).label('total_kg')).filter_by(bande_id=b.id).group_by(Consommation.type_aliment).order_by(func.sum(Consommation.aliment_kg).desc()).first()
        top_aliment = {'type_aliment': None, 'total_kg': 0}
        if top_alim_row:
            top_aliment = {'type_aliment': top_alim_row.type_aliment, 'total_kg': float(top_alim_row.total_kg or 0)}

        # consommation totale and per animal
        total_cons = db.session.query(func.coalesce(func.sum(Consommation.aliment_kg), 0)).filter_by(bande_id=b.id).scalar() or 0
        consommation_par_animal = float(total_cons) / b.nombre_initial if b.nombre_initial else 0

        # latest mean weight
        latest_info = AnimalInfo.query.filter_by(bande_id=b.id).order_by(AnimalInfo.semaine_production.desc()).first()
        latest_weight = float(latest_info.poids_moyen) if latest_info and latest_info.poids_moyen else None

        # Estimate IC moyen (simplified): consommation_par_animal / latest_weight if available
        ic_moyen = None
        if latest_weight and latest_weight > 0:
            ic_moyen = round(consommation_par_animal / latest_weight, 2)

        taux_mortalite = round((float(b.nombre_morts_totaux or 0) / b.nombre_initial) * 100, 2) if b.nombre_initial else 0
        taux_survie = round(100 - taux_mortalite, 2)

        # Compute performance components
        perf = compute_performance_for_band(b)

        return jsonify({
            'bande_id': b.id,
            'nom_bande': b.nom_bande,
            'race': b.race,
            'traitements': traitements_list,
            'top_aliment': top_aliment,
            'consommation_par_animal': round(consommation_par_animal, 2),
            'ic_moyen': ic_moyen,
            'taux_mortalite': taux_mortalite,
            'taux_survie': taux_survie,
            'performance': perf
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500