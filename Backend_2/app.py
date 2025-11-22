from flask import Flask, render_template, redirect, url_for, session
from modeles.models import db
from routes.auth import auth_bp
from routes.bandes import bandes_bp
from routes.animaux import animaux_bp
from routes.workers import workers_bp
from routes.traitements import traitements_bp
from routes.consommations import consommations_bp
from routes.depenses import depenses_bp
from routes.interventions import interventions_bp
from routes.predictions import predictions_bp
from routes.dashboard import dashboard_bp

from flask_migrate import Migrate


# Import Gemini avec gestion d'erreur
GEMINI_AVAILABLE = False  # Par défaut à False
try:
    import google.generativeai as genai
    from routes.chatbot import chatbot_bp
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI disponible!")
except ImportError as e:
    print(f"⚠️ Gemini non disponible: {e}")
    chatbot_bp = None
except Exception as e:
    print(f"⚠️ Erreur Gemini: {e}")
    chatbot_bp = None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://avic:1234@localhost:5432/aviculture_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'votre_cle_secrete_super_securisee'

# Initialisation
db.init_app(app)
migrate = Migrate(app, db)  # migration lors de modification de db

# Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(bandes_bp, url_prefix="/bandes")
app.register_blueprint(animaux_bp, url_prefix="/animaux")
app.register_blueprint(workers_bp, url_prefix="/workers")
app.register_blueprint(traitements_bp, url_prefix="/traitements")
app.register_blueprint(consommations_bp, url_prefix="/consommations")
app.register_blueprint(depenses_bp, url_prefix="/depenses")
app.register_blueprint(interventions_bp, url_prefix="/interventions")
app.register_blueprint(predictions_bp, url_prefix="/predictions")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

# Enregistrer le blueprint chatbot seulement si disponible
if GEMINI_AVAILABLE and chatbot_bp:
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    print("✅ Chatbot intégré avec succès!")
else:
    print("⚠️ Chatbot non disponible")

# Passer GEMINI_AVAILABLE aux templates
@app.context_processor
def inject_gemini_status():
    return {'GEMINI_AVAILABLE': GEMINI_AVAILABLE}

# Création de la base de données
with app.app_context():
    db.create_all()

# Routes principales
@app.route('/')
def index():
    if 'eleveur_id' in session:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Route principale du dashboard - redirige vers le blueprint"""
    return redirect(url_for('dashboard.dashboard_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("🚀 Aviculture Pro démarré!")
    app.run(debug=True)