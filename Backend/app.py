from flask import Flask, session, request, jsonify
from datetime import timedelta
from flask_cors import CORS
from flask_migrate import Migrate
from modeles.models import db
from routes.bandes import bandes_bp
from routes.consommations import consommations_bp
from routes.traitements import traitements_bp
from routes.depense_elt import depenses_bp
from routes.chatbot import chatbot_bp  
from routes.animal_info import animal_info_bp

app = Flask(__name__)

# Configuration
import os
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'votre_cle_secrete_tres_longue_et_unique_123456789')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
# Prefer DATABASE_URL env var (Postgres) but fallback to a file-based SQLite DB for local dev.
# If a DATABASE_URL points to Postgres but psycopg2 isn't installed (common on Windows dev),
# fall back to SQLite to let the dev server run without native build tools.
db_uri = os.getenv('DATABASE_URL')
if db_uri and 'postgres' in db_uri:
    try:
        import psycopg2  # check availability
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    except Exception:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev_local.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or 'sqlite:///dev_local.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation
db.init_app(app)
migrate = Migrate(app, db)

# CORS
CORS(app, 
    supports_credentials=True,
    origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5173/"],
    expose_headers=["Content-Disposition"]
)

# Gestion OPTIONS
@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.status_code = 200
        return response

# ⭐ IMPORTANT: Enregistrez TOUS les blueprints
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(bandes_bp, url_prefix="/bandes")
app.register_blueprint(consommations_bp, url_prefix="/consommations")
app.register_blueprint(traitements_bp, url_prefix="/traitements")
app.register_blueprint(depenses_bp, url_prefix="/depenses")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot") 
app.register_blueprint(animal_info_bp, url_prefix="/animal-info")
from routes.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

# Seed initial bandes (create demo data if missing)
try:
    # Legacy helper (kept but not used here)
    from init_data import seed_initial_bandes
except Exception:
    seed_initial_bandes = None

# New: ensure eleveur id=2 has a full initialized dataset — clear existing and create 12 bands
try:
    from init_seed import init_eleveur_2
    with app.app_context():
        try:
            # ensure the eleveur exists; init_eleveur_2 will create the Eleveur if missing
            from modeles.models import Eleveur, Bande, Consommation, AnimalInfo, Traitement, depense_elt

            def _clear_and_seed():
                bands = Bande.query.filter_by(eleveur_id=2).all()
                if bands:
                    print(f"🔄 Nettoyage: suppression de {len(bands)} bande(s) pour eleveur id=2")
                for b in bands:
                    Consommation.query.filter_by(bande_id=b.id).delete()
                    AnimalInfo.query.filter_by(bande_id=b.id).delete()
                    Traitement.query.filter_by(bande_id=b.id).delete()
                    depense_elt.query.filter_by(bande_id=b.id).delete()
                    db.session.delete(b)
                db.session.commit()

                res = init_eleveur_2(app)
                if res and isinstance(res, dict) and res.get('created'):
                    print(f"🔧 Init: {res.get('created')} bandes créées pour eleveur id=2")
                else:
                    print(f"🔧 Init: aucune nouvelle bande créée (détails: {res})")

            try:
                _clear_and_seed()
            except Exception as ie:
                # If tables do not exist yet, try to create them (dev convenience) and retry
                msg = str(ie).lower()
                if 'no such table' in msg or 'does not exist' in msg or 'operationalerror' in msg:
                    print('ℹ️ Tables manquantes détectées, création des tables via db.create_all() et rééssai')
                    db.create_all()
                    _clear_and_seed()
                else:
                    raise
        except Exception as inner_e:
            print(f"⚠️ Erreur pendant l'initialisation pour eleveur id=2: {inner_e}")
except Exception as e:
    print(f"⚠️ Init seed module not available or failed: {e}")

# Scheduler: planifier une tâche quotidienne qui marque automatiquement les bandes arrivées à leur date de fin
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from datetime import datetime
    from services.auto_termination import terminate_finished_bandes

    scheduler = BackgroundScheduler()
    # Exécuter la vérification immédiatement au démarrage
    scheduler.add_job(lambda: terminate_finished_bandes(app), 'date', run_date=datetime.now())
    # Planifier un job quotidien
    scheduler.add_job(lambda: terminate_finished_bandes(app), 'interval', days=1, next_run_time=None)
    scheduler.start()
    # run one pass now in app context as double safety
    with app.app_context():
        terminate_finished_bandes(app)
    print('🕒 Scheduler: tâche quotidienne de terminaison automatique démarrée')
except Exception as e:
    print('⚠️ Scheduler non démarré (APScheduler non disponible ?) :', e)

@app.route('/ping')
def ping():
    return jsonify({'status': 'ok', 'session': dict(session)})

@app.route('/debug-routes')
def debug_routes():
    """Affiche toutes les routes enregistrées"""
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
    return jsonify(routes)
    

if __name__ == '__main__':
    print("🚀 Serveur démarré!")
    print("📡 Routes disponibles:")
    print("  - POST /chatbot/ask")
    print("  - POST /chatbot/analyse-complete")
    print("  - GET  /chatbot/historique")
    print("  - GET  /chatbot/statistiques-chatbot")
    app.run(debug=True, port=5000)