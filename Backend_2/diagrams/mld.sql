-- MLD (PostgreSQL) généré à partir de modeles/models.py
-- Attention: ajuster schéma / types selon besoins

CREATE TABLE eleveurs (
  id SERIAL PRIMARY KEY,
  nom VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  mot_de_passe VARCHAR(255) NOT NULL,
  telephone VARCHAR(20),
  adresse TEXT,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE workers (
  id SERIAL PRIMARY KEY,
  nom VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  telephone VARCHAR(20),
  type_worker VARCHAR(20) NOT NULL,
  specialite VARCHAR(100),
  role VARCHAR(100),
  date_embauche DATE,
  salaire NUMERIC,
  actif BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE bandes (
  id SERIAL PRIMARY KEY,
  eleveur_id INTEGER NOT NULL REFERENCES eleveurs(id) ON DELETE CASCADE,
  nom_bande VARCHAR(100) NOT NULL,
  date_arrivee DATE NOT NULL,
  race VARCHAR(50),
  fournisseur VARCHAR(100),
  nombre_initial INTEGER NOT NULL,
  poids_moyen_initial REAL,
  statut VARCHAR(20) DEFAULT 'active',
  nbre_ajoute INTEGER DEFAULT 0,
  age_moyen REAL,
  nombre_nouveaux_nes INTEGER DEFAULT 0,
  nombre_morts_totaux INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE animaux (
  id SERIAL PRIMARY KEY,
  bande_id INTEGER NOT NULL REFERENCES bandes(id) ON DELETE CASCADE,
  age REAL,
  poids REAL,
  statut VARCHAR(20) DEFAULT 'vivant',
  date_naissance DATE,
  date_deces DATE,
  etat_achat VARCHAR(20) DEFAULT 'acheté',
  etat VARCHAR(20) DEFAULT 'sain',
  prix NUMERIC DEFAULT 0.0,
  nombre INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE consommations (
  id SERIAL PRIMARY KEY,
  bande_id INTEGER NOT NULL REFERENCES bandes(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  type_aliment VARCHAR(50),
  cout_aliment REAL,
  aliment_kg REAL NOT NULL,
  eau_litres REAL NOT NULL,
  semaine_production INTEGER,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE depenses (
  id SERIAL PRIMARY KEY,
  bande_id INTEGER NOT NULL REFERENCES bandes(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  type_depense VARCHAR(50) NOT NULL,
  description TEXT,
  montant REAL NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE traitements (
  id SERIAL PRIMARY KEY,
  bande_id INTEGER NOT NULL REFERENCES bandes(id) ON DELETE CASCADE,
  worker_id INTEGER NOT NULL REFERENCES workers(id) ON DELETE RESTRICT,
  date DATE NOT NULL,
  produit VARCHAR(100) NOT NULL,
  type_traitement VARCHAR(50) NOT NULL,
  dosage VARCHAR(50),
  efficacite REAL,
  notes TEXT,
  nombre_morts_apres INTEGER DEFAULT 0,
  nombre_gueris_apres INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE interventions (
  id SERIAL PRIMARY KEY,
  bande_id INTEGER NOT NULL REFERENCES bandes(id) ON DELETE CASCADE,
  worker_id INTEGER NOT NULL REFERENCES workers(id) ON DELETE RESTRICT,
  date DATE NOT NULL,
  type_intervention VARCHAR(50) NOT NULL,
  description TEXT,
  duree_heures REAL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  bande_id INTEGER NOT NULL REFERENCES bandes(id) ON DELETE CASCADE,
  date_prediction DATE NOT NULL,
  type_prediction VARCHAR(50) NOT NULL,
  valeur_prevue REAL NOT NULL,
  fiabilite REAL,
  semaine_cible INTEGER,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE kpi_dashboard (
  id SERIAL PRIMARY KEY,
  bande_id INTEGER NOT NULL REFERENCES bandes(id) ON DELETE CASCADE,
  date_calcul DATE NOT NULL,
  ic REAL,
  poids_moyen_actuel REAL,
  cout_total REAL,
  benefice_estime REAL,
  taux_mortalite REAL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE messages_chatbot (
  id SERIAL PRIMARY KEY,
  eleveur_id INTEGER NOT NULL REFERENCES eleveurs(id) ON DELETE CASCADE,
  message_utilisateur TEXT NOT NULL,
  reponse_bot TEXT NOT NULL,
  date_message TIMESTAMP DEFAULT now()
);

-- Indexes / contraintes supplémentaires si nécessaire
