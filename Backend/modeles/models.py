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
    duree_jours = db.Column(db.Integer)  # durée prévue/observée du lot

    # Nouveaux champs
    age_moyen = db.Column(db.Float)  # en jours ou semaines
    nombre_morts_totaux = db.Column(db.Integer, default=0)  # cumul global
    cout_unitaire = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    consommations = db.relationship('Consommation', backref='bande', lazy=True)
    animal_infos = db.relationship('AnimalInfo', backref='bande', lazy=True, cascade='all, delete-orphan')
    depenses_elt = db.relationship('depense_elt', backref='bande', lazy=True)
    traitements = db.relationship('Traitement', backref='bande', lazy=True)
   
    def to_dict(self):
        return {
            'id': self.id,
            'nom_bande': self.nom_bande,
            'date_arrivee': self.date_arrivee.isoformat(),
            'race': self.race,
            'fournisseur': self.fournisseur,
            'nombre_initial': self.nombre_initial,
            'poids_moyen_initial': self.poids_moyen_initial,
            'statut': self.statut,
            'duree_jours': self.duree_jours,
            'age_moyen': self.age_moyen,
            'nombre_morts_totaux': self.nombre_morts_totaux,
            'eleveur_id': self.eleveur_id,
            'cout_unitaire': self.cout_unitaire
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

    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            # Nom de la bande via backref
            'bande_nom': self.bande.nom_bande if getattr(self, 'bande', None) else None,
            'date': self.date.isoformat(),
            'type_aliment': self.type_aliment,
            'cout_aliment': self.cout_aliment,
            'aliment_kg': self.aliment_kg,
            'eau_litres': self.eau_litres,
            'semaine_production': self.semaine_production,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ----------------------------
# Informations animales par semaine
# ----------------------------
class AnimalInfo(db.Model):
    __tablename__ = 'animal_info'

    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    semaine_production = db.Column(db.Integer, nullable=False)
    poids_moyen = db.Column(db.Float)  # kg par poule pour la semaine
    morts_semaine = db.Column(db.Integer, default=0)
    animaux_restants = db.Column(db.Integer)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'semaine_production': self.semaine_production,
            'poids_moyen': self.poids_moyen,
            'morts_semaine': self.morts_semaine,
            'animaux_restants': self.animaux_restants,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ----------------------------
# Traitement
# ----------------------------

class Traitement(db.Model):
    __tablename__ = 'traitements'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    produit = db.Column(db.String(100), nullable=False)
    type_traitement = db.Column(db.String(50), nullable=False)
    dosage = db.Column(db.String(50))
    efficacite = db.Column(db.Float)
    notes = db.Column(db.Text)
    cout = db.Column(db.Float)

    # Nouveaux champs
    nombre_morts_apres = db.Column(db.Integer, default=0)
    nombre_gueris_apres = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'date': self.date.isoformat(),
            'produit': self.produit,
            'type_traitement': self.type_traitement,
            'dosage': self.dosage,
            'efficacite': self.efficacite,
            'notes': self.notes,
            'nombre_morts_apres': self.nombre_morts_apres,
            'nombre_gueris_apres': self.nombre_gueris_apres,
            'cout': self.cout
        }

# ----------------------------
# Dépense elementaire
# ----------------------------
class depense_elt(db.Model):
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    bande_id = db.Column(db.Integer, db.ForeignKey('bandes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type_depense = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    duree_heures = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cout = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bande_id': self.bande_id,
            'date': self.date.isoformat(),
            'type_depense': self.type_depense,
            'description': self.description,
            'duree_heures': self.duree_heures
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



