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
app.config['SECRET_KEY'] = 'votre_cle_secrete_tres_longue_et_unique_123456789'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://avic:1234@localhost:5432/aviculture_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation
db.init_app(app)
migrate = Migrate(app, db)

# CORS
CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:5173"])

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