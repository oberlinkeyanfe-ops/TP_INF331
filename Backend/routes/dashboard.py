from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, current_app, send_file
from modeles.models import db, Bande, Consommation, Traitement, AnimalInfo, depense_elt, Eleveur
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm

dashboard_bp = Blueprint('dashboard', __name__)

# Reference consumption per week (same as frontend) — now expressed as per-bird ranges and cumulative ranges
CONSUMPTION_REFERENCE = [
    {'week': 1, 'per_bird_low': 0.13, 'per_bird_high': 0.167, 'cumulative_low': 0.13, 'cumulative_high': 0.167, 'eau_litres': 300},
    {'week': 2, 'per_bird_low': 0.28, 'per_bird_high': 0.375, 'cumulative_low': 0.42, 'cumulative_high': 0.542, 'eau_litres': 640},
    {'week': 3, 'per_bird_low': 0.47, 'per_bird_high': 0.65, 'cumulative_low': 0.88, 'cumulative_high': 1.192, 'eau_litres': 980},
    {'week': 4, 'per_bird_low': 0.64, 'per_bird_high': 0.945, 'cumulative_low': 1.55, 'cumulative_high': 2.137, 'eau_litres': 1350},
    {'week': 5, 'per_bird_low': 0.85, 'per_bird_high': 1.215, 'cumulative_low': 2.40, 'cumulative_high': 3.352, 'eau_litres': 1680},
    {'week': 6, 'per_bird_low': 1.07, 'per_bird_high': 1.434, 'cumulative_low': 3.45, 'cumulative_high': 4.786, 'eau_litres': 1900},
    {'week': 7, 'per_bird_low': 1.18, 'per_bird_high': 1.593, 'cumulative_low': 4.66, 'cumulative_high': 6.379, 'eau_litres': 2050},
    {'week': 8, 'per_bird_low': 1.30, 'per_bird_high': 1.691, 'cumulative_low': 5.96, 'cumulative_high': 8.07, 'eau_litres': 2150}
]

# Helper: compute per-band aliment kg from per-bird ref when available
def compute_ref_kg_for_week(ref_weeks_dict, week, population):
    ref = ref_weeks_dict.get(week)
    if not ref:
        return None
    if 'per_bird_low' in ref and 'per_bird_high' in ref and population:
        per_bird = (float(ref['per_bird_low']) + float(ref['per_bird_high'])) / 2.0
        return per_bird * float(population)
    # fallback to legacy aliment_kg if present
    return float(ref.get('aliment_kg')) if ref.get('aliment_kg') is not None else None


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
            # Prefer the computed mortality_total_pct from performance subscores (derived from AnimalInfo)
            mortality_pct = None
            try:
                mortality_pct = perf.get('subscores', {}).get('mortality_total_pct')
            except Exception:
                mortality_pct = None
            if mortality_pct is None:
                # fallback to stored bande.nombre_morts_totaux if present
                mortality_pct = round((float(b.nombre_morts_totaux or 0) / b.nombre_initial) * 100, 2) if b.nombre_initial else 0
            perf_entry = {**base, **perf, 'taux_mortalite': round(float(mortality_pct or 0), 2)}
            performance.append(perf_entry)

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
            # include precise performance_percent (allow None when unknown)
            result[str(pid)] = perf.get('performance_percent', None)
            # include components
            result[f'components_{pid}'] = perf.get('subscores', {})
            # include status (e.g., 'no_consumption') when present
            if perf.get('performance_status') is not None:
                result[f'status_{pid}'] = perf.get('performance_status')
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
            current_app.logger.debug('compute_performance_for_band: band %s has no initial animals (%s)', getattr(bande, 'id', None), initial)
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

        # Compute mortality_week_pct (safe default even if no consumption data)
        mortality_week_pct = {}
        for w in weeks:
            morts = morts_by_week.get(w, None)
            if morts is None:
                mortality_week_pct[w] = None
            else:
                mortality_week_pct[w] = (morts / initial) * 100 if initial else None

        # If we have no consumption data at all for this band, treat as 'no data' and do not compute a performance
        if not consum_by_week:
            current_app.logger.debug('compute_performance_for_band: band %s has no consumption data, skipping performance', getattr(bande, 'id', None))
            return {
                'consommation_par_poule_par_semaine': {},
                'mortalite_par_semaine_pct': {str(k): (v if v is not None else None) for k, v in mortality_week_pct.items()},
                'survie_par_semaine_pct': {str(k): (100 - v if v is not None else None) for k, v in mortality_week_pct.items()},
                'subscores': {'consumption': None, 'survival': None},
                'performance_percent': None,
                'performance_status': 'no_consumption'
            }
        # Consumption performance: compare per-poule per-week to reference per-week
        # margin allowed (fraction): within +/- margin => perfect 100. Outside reduce linearly.
        margin = 0.05  # 5% margin
        consumption_per_week_pct = {}
        for w in weeks:
            actual_kg = consum_by_week.get(w, 0)
            actual_per_poule = actual_kg / initial
            ref = ref_weeks.get(w)
            # compute ref kg per band using population when per-bird info exists
            ref_kg = compute_ref_kg_for_week(ref_weeks, w, initial) if initial else (ref.get('aliment_kg') if ref else None)
            ref_per_poule = (ref_kg / initial) if (ref_kg is not None and initial) else None
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

        # Mortality: per-week percent = (morts_week / initial) * 100 (for diagnostics)
        mortality_week_pct = {}
        for w in weeks:
            morts = morts_by_week.get(w, None)
            if morts is None:
                mortality_week_pct[w] = None
            else:
                mortality_week_pct[w] = (morts / initial) * 100

        # Use total deaths (sum of weekly deaths) to compute the mortality percentage used for performance
        total_morts = sum((v or 0) for v in morts_by_week.values())
        mortality_total_pct = (total_morts / initial) * 100 if initial else 0.0

        # Aggregate consumption performance average over weeks with values
        cons_values = [v for v in consumption_per_week_pct.values() if isinstance(v, (int, float))]
        consumption_perf = int(round(sum(cons_values) / len(cons_values))) if cons_values else None

        # Survival percentage derived from total mortality
        survival_pct = (100.0 - mortality_total_pct) if (mortality_total_pct is not None) else None
        survival_perf = int(max(0, round(survival_pct))) if survival_pct is not None else None

        # Expose subscores including explicit mortality total percentage
        subscores = {
            'consumption': consumption_perf,
            'mortality_total_pct': round(mortality_total_pct, 2) if isinstance(mortality_total_pct, (int, float)) else None,
            'survival': survival_perf
        }

        # Global performance uses total mortality in formula: (consumption_perf + (100 - mortality_total_pct)) / 2
        if consumption_perf is not None and mortality_total_pct is not None:
            perf_percent = round((consumption_perf + (100.0 - mortality_total_pct)) / 2.0, 1)
        elif consumption_perf is not None:
            perf_percent = float(consumption_perf)
        elif mortality_total_pct is not None:
            perf_percent = round(100.0 - mortality_total_pct, 1)
        else:
            perf_percent = None

        # Debug logging: record intermediate values for traceability
        try:
            current_app.logger.debug(
                "Performance debug for band %s (%s): initial=%s, consum_by_week=%s, morts_by_week=%s, mortality_total_pct=%s, consumption_per_week_pct=%s, consumption_perf=%s, survival_perf=%s, subscores=%s, perf_percent=%s",
                getattr(bande, 'id', None), getattr(bande, 'nom_bande', None), initial,
                consum_by_week, morts_by_week, (mortality_total_pct if 'mortality_total_pct' in locals() else None),
                consumption_per_week_pct, consumption_perf, survival_perf, subscores, perf_percent
            )
        except Exception:
            # logging must not break main flow
            current_app.logger.exception('Failed to log performance debug for band %s', getattr(bande, 'id', None))

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
            current_app.logger.exception('Error computing performance for band %s: %s', bande.id if hasattr(bande, 'id') else str(bande), e)
        except Exception:
            # Fall back to print if logger unavailable
            try:
                print('Error computing performance for band', getattr(bande, 'id', str(bande)), e)
            except Exception:
                pass
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


@dashboard_bp.route('/performance/global', methods=['GET'])
def get_global_performance():
    """Return a weighted global performance across all bands (weighted by nombre_initial)."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        total_animals = sum((b.nombre_initial or 0) for b in bandes)
        if total_animals == 0:
            return jsonify({'global_performance_percent': None, 'components': {}})

        weighted_sum = 0.0
        weighted_count = 0.0
        comp_acc = {}
        comp_weights = {}
        for b in bandes:
            perf = compute_performance_for_band(b)
            perf_percent = perf.get('performance_percent')
            if isinstance(perf_percent, (int, float)):
                w = (b.nombre_initial or 0)
                weighted_sum += perf_percent * w
                weighted_count += w
            # aggregate subscores
            subs = perf.get('subscores') or {}
            for k, v in subs.items():
                if v is None: continue
                comp_acc[k] = comp_acc.get(k, 0) + v * (b.nombre_initial or 0)
                comp_weights[k] = comp_weights.get(k, 0) + (b.nombre_initial or 0)

        global_perf = int(round(weighted_sum / weighted_count)) if weighted_count > 0 else None
        components = {}
        for k, total in comp_acc.items():
            if comp_weights.get(k):
                components[k] = int(round(total / comp_weights.get(k)))
            else:
                components[k] = None

        return jsonify({'global_performance_percent': global_perf, 'components': components})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/performance/debug', methods=['GET'])
def performance_debug():
    """Return detailed diagnostics for performance computation per band (for debugging)."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        bandes = Bande.query.filter_by(eleveur_id=session['eleveur_id']).all()
        result = []
        for b in bandes:
            try:
                # Recompute diagnostics similarly to compute_performance_for_band but return more details
                consommations = Consommation.query.filter_by(bande_id=b.id).all()
                consum_by_week = {}
                for c in consommations:
                    w = int(c.semaine_production) if c.semaine_production is not None else None
                    if not w: continue
                    consum_by_week[w] = consum_by_week.get(w, 0) + float(c.aliment_kg or 0)

                animal_infos = AnimalInfo.query.filter_by(bande_id=b.id).all()
                morts_by_week = {}
                for a in animal_infos:
                    w = int(a.semaine_production) if a.semaine_production is not None else None
                    if not w: continue
                    morts_by_week[w] = morts_by_week.get(w, 0) + int(a.morts_semaine or 0)

                initial = b.nombre_initial or 0
                # compute mortality avg (weekly or fallback)
                mortality_values = []
                for v in ( (morts_by_week.get(w) / initial * 100) for w in morts_by_week.keys() ):
                    if v is not None: mortality_values.append(v)
                if mortality_values:
                    mortality_avg = sum(mortality_values) / len(mortality_values)
                else:
                    mortality_avg = (b.nombre_morts_totaux or 0) / initial * 100 if initial else None

                # consumption per week pct relative to reference
                ref_weeks = {r['week']: r for r in CONSUMPTION_REFERENCE}
                consumption_per_week_pct = {}
                for w in sorted(set(list(consum_by_week.keys()) + list(ref_weeks.keys()))):
                    actual_kg = consum_by_week.get(w, 0)
                    actual_per_poule = actual_kg / initial if initial else None
                    ref = ref_weeks.get(w)
                    # compute ref_kg using per-bird data if available
                    ref_kg = compute_ref_kg_for_week(ref_weeks, w, initial) if initial else (ref.get('aliment_kg') if ref else None)
                    ref_per_poule = (ref_kg / initial) if (ref_kg is not None and initial) else None
                    if ref_per_poule is None or ref_per_poule <= 0 or actual_per_poule is None:
                        consumption_per_week_pct[w] = None
                    else:
                        deviation = (actual_per_poule - ref_per_poule) / ref_per_poule
                        margin = 0.05
                        if abs(deviation) <= margin:
                            perf = 100
                        else:
                            effective = max(0.0, abs(deviation) - margin)
                            perf = int(max(0, round(100 * (1 - min(1.0, effective)))))
                        consumption_per_week_pct[w] = perf

                consumption_values = [v for v in consumption_per_week_pct.values() if isinstance(v, (int, float))]
                consumption_perf = int(round(sum(consumption_values) / len(consumption_values))) if consumption_values else None

                survival_perf = int(max(0, round(100 - (mortality_avg or 0)))) if mortality_avg is not None else None

                subscores = {'consumption': consumption_perf, 'survival': survival_perf}
                perf_percent = int(round(sum([v for v in subscores.values() if isinstance(v, (int, float))]) / len([v for v in subscores.values() if isinstance(v, (int, float))]))) if any(isinstance(v, (int, float)) for v in subscores.values()) else None

                result.append({
                    'bande_id': b.id,
                    'nom_bande': b.nom_bande,
                    'initial': initial,
                    'consum_by_week': consum_by_week,
                    'morts_by_week': morts_by_week,
                    'mortality_avg': mortality_avg,
                    'consumption_per_week_pct': consumption_per_week_pct,
                    'consumption_perf': consumption_perf,
                    'survival_perf': survival_perf,
                    'subscores': subscores,
                    'performance_percent': perf_percent
                })
            except Exception as inner_e:
                current_app.logger.exception('Error building diagnostics for band %s: %s', getattr(b, 'id', None), inner_e)
                result.append({'bande_id': b.id, 'error': str(inner_e)})
        current_app.logger.info('Performance debug endpoint called, returning %d bands', len(result))
        return jsonify({'diagnostics': result})
    except Exception as e:
        current_app.logger.exception('performance_debug failed: %s', e)
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
            # Purchase cost for initial animals
            cout_achat_animaux = float((b.prix_achat_unitaire or 0.0) * (b.nombre_initial or 0))
            total = float(total_cons_cout or 0) + float(total_depenses or 0) + float(total_traitements or 0) + cout_achat_animaux
            result.append({
                'bande_id': b.id,
                'nom_bande': b.nom_bande,
                'cout_aliment': float(total_cons_cout or 0),
                'cout_depenses': float(total_depenses or 0),
                'cout_traitements': float(total_traitements or 0),
                'cout_achat_animaux': cout_achat_animaux,
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
        # Compute cumulative deaths from AnimalInfo.morts_semaine to reflect actual recorded mortalities
        nb_morts = db.session.query(func.coalesce(func.sum(AnimalInfo.morts_semaine), 0)).join(Bande).filter(Bande.eleveur_id == eleveur_id).scalar() or 0

        # performance per bande
        perf_rows = Bande.query.filter_by(eleveur_id=eleveur_id).all()
        performance = []
        for b in perf_rows:
            total_cons = db.session.query(func.coalesce(func.sum(Consommation.aliment_kg), 0)).filter_by(bande_id=b.id).scalar() or 0
            consommation_par_animal = float(total_cons) / b.nombre_initial if b.nombre_initial else 0
            # Prefer mortality computed from animal_info (weekly morts) when available
            perf_calc = compute_performance_for_band(b)
            mortality_pct = None
            try:
                mortality_pct = perf_calc.get('subscores', {}).get('mortality_total_pct')
            except Exception:
                mortality_pct = None
            if mortality_pct is None:
                mortality_pct = round((float(b.nombre_morts_totaux or 0) / b.nombre_initial) * 100, 2) if b.nombre_initial else 0
            taux_mortalite = round(float(mortality_pct or 0), 2)
            # estimate gains rudimentaire si cout_unitaire disponible
            gains = 0
            if b.cout_unitaire:
                gains = (b.nombre_initial - (b.nombre_morts_totaux or 0)) * (b.cout_unitaire or 0)
            # Purchase/initial animal cost (expense)
            cout_achat_animaux = float((b.prix_achat_unitaire or 0.0) * (b.nombre_initial or 0))
            performance.append({
                'bande_id': b.id,
                'nom_bande': b.nom_bande,
                'statut': b.statut,
                'nombre_animaux': b.nombre_initial,
                'consommation_par_animal': round(consommation_par_animal, 2),
                'taux_mortalite': round(taux_mortalite, 2),
                'gains': float(gains),
                'cout_achat_animaux': cout_achat_animaux
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
        current_app.logger.exception('Failed to fetch dashboard_global_v2: %s', e)
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/report/pdf', methods=['GET'])
def report_pdf():
    """Generate a well-structured global report PDF for the logged-in eleveur."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        eleveur_id = session['eleveur_id']
        eleveur = Eleveur.query.get(eleveur_id)
        if not eleveur:
            return jsonify({'error': 'Eleveur introuvable'}), 404

        # Gather bands summary
        bandes = Bande.query.filter_by(eleveur_id=eleveur_id).order_by(Bande.date_arrivee.desc()).all()
        rows = []
        for b in bandes:
            total_cons_cout = float(db.session.query(func.coalesce(func.sum(Consommation.cout_aliment), 0)).filter_by(bande_id=b.id).scalar() or 0)
            total_depenses = float(db.session.query(func.coalesce(func.sum(depense_elt.cout), 0)).filter_by(bande_id=b.id).scalar() or 0)
            total_traitements = float(db.session.query(func.coalesce(func.sum(Traitement.cout), 0)).filter_by(bande_id=b.id).scalar() or 0)
            cout_achat_animaux = float((b.prix_achat_unitaire or 0.0) * (b.nombre_initial or 0))
            cout_total = total_cons_cout + total_depenses + total_traitements + cout_achat_animaux
            total_cons_kg = float(db.session.query(func.coalesce(func.sum(Consommation.aliment_kg), 0)).filter_by(bande_id=b.id).scalar() or 0)
            # mortality percent from performance or fallback
            perf = compute_performance_for_band(b)
            mort_pct = None
            try:
                mort_pct = perf.get('subscores', {}).get('mortality_total_pct')
            except Exception:
                mort_pct = None
            if mort_pct is None:
                mort_pct = round((float(b.nombre_morts_totaux or 0) / b.nombre_initial) * 100, 2) if b.nombre_initial else 0

            rows.append({
                'id': b.id,
                'nom': b.nom_bande,
                'statut': b.statut,
                'date_arrivee': b.date_arrivee.isoformat() if b.date_arrivee else '',
                'nombre_initial': b.nombre_initial,
                'taux_mortalite': round(float(mort_pct or 0), 2),
                'consommation_kg': round(total_cons_kg, 2),
                'cout_total': round(cout_total, 2),
                'cout_achat_animaux': round(cout_achat_animaux, 2)
            })

        # Build PDF
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        story = []
        title = Paragraph(f"Rapport Global - {eleveur.nom}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 6))
        meta = Paragraph(f"Date: {datetime.utcnow().isoformat()}<br/>Eleveur: {eleveur.nom} &nbsp;|&nbsp; Email: {eleveur.email}", styles['Normal'])
        story.append(meta)
        story.append(Spacer(1, 12))

        # Summary KPIs
        total_animals = sum((r['nombre_initial'] or 0) for r in rows)
        total_cost_all = sum((r['cout_total'] or 0) for r in rows)
        kpi_para = Paragraph(f"Bandes: {len(rows)} &nbsp;&nbsp;|&nbsp;&nbsp; Total Sujets: {total_animals} &nbsp;&nbsp;|&nbsp;&nbsp; Coûts totaux: {int(total_cost_all)} FCFA", styles['Normal'])
        story.append(kpi_para)
        story.append(Spacer(1, 12))

        # Table header
        table_data = [["Bande", "Statut", "Arrivée", "Effectif", "Mort(%)", "Conso (kg)", "Coût total (FCFA)"]]
        for r in rows:
            table_data.append([r['nom'], r['statut'], r['date_arrivee'], r['nombre_initial'], f"{r['taux_mortalite']}%", f"{r['consommation_kg']}", f"{int(r['cout_total']):,}"])

        t = Table(table_data, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#374151')),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Footer / notes
        note = Paragraph("Ce rapport présente un résumé global des bandes, leurs consommations, mortalités et coûts (achat animaux inclus).", styles['Normal'])
        story.append(note)

        doc.build(story)
        buf.seek(0)

        filename = f"rapport_global_{eleveur.nom.replace(' ', '_')}.pdf"
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=filename)

    except Exception as e:
        current_app.logger.exception('Failed to generate report PDF: %s', e)
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/report/bande/<int:bande_id>/pdf', methods=['GET'])
def report_bande_pdf(bande_id):
    """Generate a detailed PDF report for a single bande including consumptions, mortalities, treatments and costs."""
    if 'eleveur_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    try:
        eleveur_id = session['eleveur_id']
        b = Bande.query.filter_by(id=bande_id, eleveur_id=eleveur_id).first()
        if not b:
            return jsonify({'error': 'Bande introuvable'}), 404

        # Gather weekly consumption and cost
        cons_rows = db.session.query(
            Consommation.semaine_production,
            func.coalesce(func.sum(Consommation.aliment_kg), 0).label('total_kg'),
            func.coalesce(func.sum(Consommation.cout_aliment), 0).label('total_cout')
        ).filter_by(bande_id=b.id).group_by(Consommation.semaine_production).order_by(Consommation.semaine_production).all()

        # Animal info by week
        info_rows = AnimalInfo.query.filter_by(bande_id=b.id).order_by(AnimalInfo.semaine_production).all()
        info_by_week = {r.semaine_production: r for r in info_rows}

        # Treatments and expenses
        traitements = Traitement.query.filter_by(bande_id=b.id).order_by(Traitement.date.desc()).all()
        depenses = db.session.query(depense_elt).filter_by(bande_id=b.id).all()

        total_cons_kg = float(db.session.query(func.coalesce(func.sum(Consommation.aliment_kg), 0)).filter_by(bande_id=b.id).scalar() or 0)
        total_cons_cout = float(db.session.query(func.coalesce(func.sum(Consommation.cout_aliment), 0)).filter_by(bande_id=b.id).scalar() or 0)
        total_traitements = float(db.session.query(func.coalesce(func.sum(Traitement.cout), 0)).filter_by(bande_id=b.id).scalar() or 0)
        total_depenses = float(db.session.query(func.coalesce(func.sum(depense_elt.cout), 0)).filter_by(bande_id=b.id).scalar() or 0)
        cout_achat_animaux = float((b.prix_achat_unitaire or 0.0) * (b.nombre_initial or 0))
        cout_total = total_cons_cout + total_traitements + total_depenses + cout_achat_animaux

        # mortality percent
        perf = compute_performance_for_band(b)
        mort_pct = None
        try:
            mort_pct = perf.get('subscores', {}).get('mortality_total_pct')
        except Exception:
            mort_pct = None
        if mort_pct is None:
            mort_pct = round((float(b.nombre_morts_totaux or 0) / b.nombre_initial) * 100, 2) if b.nombre_initial else 0

        # Build PDF
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        story = []
        title = Paragraph(f"Rapport Bande - {b.nom_bande}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 6))
        meta = Paragraph(f"Date: {datetime.utcnow().isoformat()}<br/>Eleveur ID: {eleveur_id} &nbsp;|&nbsp; Bande: {b.nom_bande} &nbsp;|&nbsp; Statut: {b.statut}", styles['Normal'])
        story.append(meta)
        story.append(Spacer(1, 12))

        # Summary KPIs
        kpi_para = Paragraph(
            f"Effectif: {b.nombre_initial} &nbsp;&nbsp;|&nbsp;&nbsp; Survivants estimés: {max(0, (b.nombre_initial or 0) - (b.nombre_morts_totaux or 0))} &nbsp;&nbsp;|&nbsp;&nbsp; Mort(%) : {round(float(mort_pct or 0),2)}% &nbsp;&nbsp;|&nbsp;&nbsp; Coût total: {int(cout_total):,} FCFA",
            styles['Normal']
        )
        story.append(kpi_para)
        story.append(Spacer(1, 12))

        # Weekly table header
        table_data = [["Semaine", "Alim (kg)", "Coût (FCFA)", "Morts", "Poids moyen (kg)"]]
        weeks = sorted(set([r.semaine_production for r in cons_rows] + [r.semaine_production for r in info_rows]))
        for wk in weeks:
            cons_row = next((r for r in cons_rows if r.semaine_production == wk), None)
            kg = round(float(cons_row.total_kg), 2) if cons_row else 0
            cost = int(cons_row.total_cout) if cons_row else 0
            info = info_by_week.get(wk)
            morts = getattr(info, 'morts_semaine', 0) if info else 0
            poids = round(float(info.poids_moyen), 2) if info and info.poids_moyen else ''
            table_data.append([str(wk), f"{kg}", f"{cost:,}", f"{morts}", f"{poids}"])

        t = Table(table_data, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#374151')),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Treatments table
        if traitements:
            story.append(Paragraph('Traitements (récents -> anciens)', styles['Heading3']))
            tr_data = [["Date", "Produit", "Eff(%)", "Coût", "Note"]]
            for tr in traitements:
                # Some schemas use 'note' while others use 'notes' - be resilient
                note = getattr(tr, 'note', None)
                if note is None:
                    note = getattr(tr, 'notes', None)
                tr_data.append([tr.date.isoformat() if tr.date else '', tr.produit or '', str(tr.efficacite or ''), f"{int(tr.cout or 0):,}", note or ''])
            tr_tab = Table(tr_data, repeatRows=1, hAlign='LEFT')
            tr_tab.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ]))
            story.append(tr_tab)
            story.append(Spacer(1, 12))

        # Expenses table
        if depenses:
            story.append(Paragraph('Dépenses élémentaires', styles['Heading3']))
            d_data = [["Date", "Titre", "Coût"]]
            for d in depenses:
                d_data.append([d.date.isoformat() if getattr(d, 'date', None) else '', getattr(d, 'titre', getattr(d, 'libelle', '')) or '', f"{int(getattr(d, 'cout', 0)):,}"])
            d_tab = Table(d_data, repeatRows=1, hAlign='LEFT')
            d_tab.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ]))
            story.append(d_tab)
            story.append(Spacer(1, 12))

        note = Paragraph('Ce rapport présente un résumé détaillé pour la bande, incluant consommations hebdo, mortalité, traitements et dépenses.', styles['Normal'])
        story.append(note)

        doc.build(story)
        buf.seek(0)
        filename = f"rapport_bande_{b.nom_bande.replace(' ', '_')}.pdf"
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=filename)

    except Exception as e:
        current_app.logger.exception('Failed to generate bande report PDF: %s', e)
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
            'traitements': [t.to_dict() for t in traitements],
            'top_aliment': top_aliment,
            'consommation_par_animal': round(consommation_par_animal, 2),
            'ic_moyen': ic_moyen,
            'taux_mortalite': taux_mortalite,
            'taux_survie': taux_survie,
            'performance': perf
        })
    except Exception as e:
        current_app.logger.exception('Failed to fetch bande details: %s', e)
        return jsonify({'error': str(e)}), 500

