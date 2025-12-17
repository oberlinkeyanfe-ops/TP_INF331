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
    origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5173/"])

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
    from init_data import seed_initial_bandes
    # run the seed now (safe to call: it checks for existing records)
    with app.app_context():
        res = seed_initial_bandes(app)
        if res and isinstance(res, dict) and res.get('created'):
            print(f"🔧 Seed: {res.get('created')} bandes créées lors du démarrage")
except Exception as e:
    print(f"⚠️ Seed initialisation failed: {e}")

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