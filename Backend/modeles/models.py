from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db

# ----------------------------
# Éleveur
# ----------------------------
class Eleveur(db.Model):
    __tablename__ = 'eleveurs'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bandes = db.relationship('Bande', backref='eleveur', lazy=True, cascade='all, delete-orphan')
    messages_chatbot = db.relationship('MessageChatbot', backref='eleveur', lazy=True)
    
    def set_password(self, password):
        self.mot_de_passe = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.mot_de_passe, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'telephone': self.telephone,
            'created_at': self.created_at.isoformat()
        }

# ----------------------------
# Bande
# ----------------------------
class Bande(db.Model):
    __tablename__ = 'bandes'
    
    id = db.Column(db.Integer, primary_key=True)
    eleveur_id = db.Column(db.Integer, db.ForeignKey('eleveurs.id'), nullable=False)
    nom_bande = db.Column(db.String(100), nullable=False)
    date_arrivee = db.Column(db.Date, nullable=False)
    race = db.Column(db.String(50))
    fournisseur = db.Column(db.String(100))
    nombre_initial = db.Column(db.Integer, nullable=False)
    poids_moyen_initial = db.Column(db.Float)
    statut = db.Column(db.String(20), default='active')  # active, terminee, archivee
    
    # CORRECTION : Colonne nbre_ajoute définie correctement
    nbre_ajoute = db.Column(db.Integer, default=0)  # Calculé à partir des animaux

    # Nouveaux champs
    age_moyen = db.Column(db.Float)  # en jours ou semaines
    nombre_nouveaux_nes = db.Column(db.Integer, default=0)
    nombre_morts_totaux = db.Column(db.Integer, default=0)  # cumul global

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    #consommations = db.relationship('Consommation', backref='bande', lazy=True)
    depenses = db.relationship('Depense', backref='bande', lazy=True)
    traitements = db.relationship('Traitement', backref='bande', lazy=True)
    interventions = db.relationship('Intervention', backref='bande', lazy=True)
    predictions = db.relationship('Prediction', backref='bande', lazy=True)
    kpis = db.relationship('KPIDashboard', backref='bande', lazy=True)
    animaux = db.relationship('Animal', back_populates='bande', lazy=True, cascade='all, delete-orphan')
   
    def to_dict(self):
        return {
            'id': self.id,
            'nom_bande': self.nom_bande,
            'date_arrivee': self.date_arrivee.isoformat(),
            'race': self.race,
            'fournisseur': self.fournisseur,
            'nombre_initial': self.nombre_initial,
            'nbre_ajoute': self.nbre_ajoute,
            'poids_moyen_initial': self.poids_moyen_initial,
            'statut': self.statut,
            'age_moyen': self.age_moyen,
            'nombre_nouveaux_nes': self.nombre_nouveaux_nes,
            'nombre_morts_totaux': self.nombre_morts_totaux,
            'eleveur_id': self.eleveur_id
        }


# ----------------------------
# Consommation
# ----------------------------
class Consommation(db.Model):
    __tablename__ = 'consommations'

    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type_aliment = db.Column(db.String(50))
    cout_aliment = db.Column(db.Float)
    aliment_kg = db.Column(db.Float, nullable=False)
    eau_litres = db.Column(db.Float, nullable=False)
    semaine_production = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers Bande, pas de backref
    bande = db.relationship('Bande', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'bande_nom': self.bande.nom if self.bande else None,
            'date': self.date.isoformat(),
            'type_aliment': self.type_aliment,
            'cout_aliment': self.cout_aliment,
            'aliment_kg': self.aliment_kg,
            'eau_litres': self.eau_litres,
            'semaine_production': self.semaine_production
        }

# ----------------------------
# Dépense
# ----------------------------
class Depense(db.Model):
    __tablename__ = 'depenses'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type_depense = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    montant = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'date': self.date.isoformat(),
            'type_depense': self.type_depense,
            'description': self.description,
            'montant': self.montant
        }

# ----------------------------
# Traitement
# ----------------------------

class Traitement(db.Model):
    __tablename__ = 'traitements'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    produit = db.Column(db.String(100), nullable=False)
    type_traitement = db.Column(db.String(50), nullable=False)
    dosage = db.Column(db.String(50))
    efficacite = db.Column(db.Float)
    notes = db.Column(db.Text)

    # Nouveaux champs
    nombre_morts_apres = db.Column(db.Integer, default=0)
    nombre_gueris_apres = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'worker_id': self.worker_id,
            'date': self.date.isoformat(),
            'produit': self.produit,
            'type_traitement': self.type_traitement,
            'dosage': self.dosage,
            'efficacite': self.efficacite,
            'notes': self.notes,
            'nombre_morts_apres': self.nombre_morts_apres,
            'nombre_gueris_apres': self.nombre_gueris_apres
        }

# ----------------------------
# Intervention
# ----------------------------
class Intervention(db.Model):
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type_intervention = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    duree_heures = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'worker_id': self.worker_id,
            'date': self.date.isoformat(),
            'type_intervention': self.type_intervention,
            'description': self.description,
            'duree_heures': self.duree_heures
        }

# ----------------------------
# Prediction
# ----------------------------
class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    date_prediction = db.Column(db.Date, nullable=False)
    type_prediction = db.Column(db.String(50), nullable=False)
    valeur_prevue = db.Column(db.Float, nullable=False)
    fiabilite = db.Column(db.Float)
    semaine_cible = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'date_prediction': self.date_prediction.isoformat(),
            'type_prediction': self.type_prediction,
            'valeur_prevue': self.valeur_prevue,
            'fiabilite': self.fiabilite,
            'semaine_cible': self.semaine_cible
        }

# ----------------------------
# KPI Dashboard
# ----------------------------
class KPIDashboard(db.Model):
    __tablename__ = 'kpi_dashboard'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    date_calcul = db.Column(db.Date, nullable=False)
    ic = db.Column(db.Float)
    poids_moyen_actuel = db.Column(db.Float)
    cout_total = db.Column(db.Float)
    benefice_estime = db.Column(db.Float)
    taux_mortalite = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'date_calcul': self.date_calcul.isoformat(),
            'ic': self.ic,
            'poids_moyen_actuel': self.poids_moyen_actuel,
            'cout_total': self.cout_total,
            'benefice_estime': self.benefice_estime,
            'taux_mortalite': self.taux_mortalite
        }

# ----------------------------
# Chatbot Messages
# ----------------------------
class MessageChatbot(db.Model):
    __tablename__ = 'messages_chatbot'
    
    id = db.Column(db.Integer, primary_key=True)
    eleveur_id = db.Column(db.Integer, db.ForeignKey('eleveurs.id'), nullable=False)
    message_utilisateur = db.Column(db.Text, nullable=False)
    reponse_bot = db.Column(db.Text, nullable=False)
    date_message = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'eleveur_id': self.eleveur_id,
            'message_utilisateur': self.message_utilisateur,
            'reponse_bot': self.reponse_bot,
            'date_message': self.date_message.isoformat()
        }

# ----------------------------
# Worker
# ----------------------------
class Worker(db.Model):
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    type_worker = db.Column(db.String(20), nullable=False)  # 'veterinaire' ou 'ouvrier'
    specialite = db.Column(db.String(100))
    role = db.Column(db.String(100))
    date_embauche = db.Column(db.Date)
    salaire = db.Column(db.Float)
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    traitements = db.relationship('Traitement', backref='worker', lazy=True)
    interventions = db.relationship('Intervention', backref='worker', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'telephone': self.telephone,
            'type_worker': self.type_worker,
            'specialite': self.specialite,
            'role': self.role,
            'date_embauche': self.date_embauche.isoformat() if self.date_embauche else None,
            'salaire': self.salaire,
            'actif': self.actif
        }

# ----------------------------
# Animal
# ----------------------------
class Animal(db.Model):
    __tablename__ = 'animaux'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    age = db.Column(db.Float)  # en jours ou semaines
    poids = db.Column(db.Float)
    statut = db.Column(db.String(20), default='vivant')  # vivant, mort, guéri, malade
    date_naissance = db.Column(db.Date)
    date_deces = db.Column(db.Date)
    etat_achat = db.Column(db.String(20), default='acheté')  # acheté, né, autre
    etat = db.Column(db.String(20), default='sain')  # sain, malade, mort, disparu
    prix = db.Column(db.Float, default=0.0)
    nombre = db.Column(db.Integer, default=1)  # Pour gérer les lots
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # CORRECTION : Relation avec back_populates
    bande = db.relationship('Bande', back_populates='animaux')
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'etat_achat': self.etat_achat,
            'etat': self.etat,
            'prix': self.prix,
            'nombre': self.nombre,
            'age': self.age,
            'poids': self.poids,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'date_deces': self.date_deces.isoformat() if self.date_deces else None,
            'created_at': self.created_at.isoformat()
        }