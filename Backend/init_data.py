from datetime import date, timedelta
from modeles.models import db, Bande, Eleveur


def seed_initial_bandes(app, eleveur_id=None, target_email=None):
    """Seed the database with 10 example bandes.

    Behavior:
    - If `eleveur_id` provided: seed bands for that eleveur only (no duplicates by name for that eleveur).
    - Else if `target_email` provided: use or create an eleveur with that email and seed for them.
    - Else: fallback to previous behavior (use first eleveur, creating a demo user if none exists).

    Returns a dict with created count and diagnostics.
    """
    with app.app_context():
        # Resolve target eleveur
        if eleveur_id:
            eleveur = Eleveur.query.get(eleveur_id)
            if not eleveur:
                return {'error': f'Eleveur id {eleveur_id} introuvable'}
        elif target_email:
            eleveur = Eleveur.query.filter_by(email=target_email).first()
            if not eleveur:
                eleveur = Eleveur(
                    nom='Eleveur Seed',
                    email=target_email
                )
                eleveur.set_password('seed1234')
                db.session.add(eleveur)
                db.session.commit()
        else:
            # ensure there is at least one eleveur
            eleveur = Eleveur.query.first()
            if not eleveur:
                eleveur = Eleveur(
                    nom='Eleveur Demo',
                    email='demo@aviculture.local'
                )
                eleveur.set_password('demo1234')
                db.session.add(eleveur)
                db.session.commit()

        # Only check existing names for this eleveur (avoid cross-eleveur collisions)
        rows = Bande.query.with_entities(Bande.nom_bande).filter_by(eleveur_id=eleveur.id).all()
        existing_names = set()
        for r in rows:
            try:
                name = r.nom_bande
            except Exception:
                name = r[0]
            if name:
                existing_names.add(name)


        sample_bandes = [
            {'nom_bande': 'Bande 1 - Excellente', 'days_ago': 60, 'race': 'Cobb 500', 'fournisseur': 'SeedFarm', 'nombre_initial': 120, 'poids_moyen_initial': 30.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 10, 'nombre_morts_totaux': 0, 'cout_unitaire': 1500.0},
            {'nom_bande': 'Bande 2 - Très bonne', 'days_ago': 50, 'race': 'Ross 308', 'fournisseur': 'AgroSupply', 'nombre_initial': 150, 'poids_moyen_initial': 29.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 12, 'nombre_morts_totaux': 1, 'cout_unitaire': 1480.0},
            {'nom_bande': 'Bande 3 - Moyenne', 'days_ago': 40, 'race': 'Cobb 500', 'fournisseur': 'Local', 'nombre_initial': 200, 'poids_moyen_initial': 28.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 14, 'nombre_morts_totaux': 2, 'cout_unitaire': 1450.0},
            {'nom_bande': 'Bande 4 - Faible', 'days_ago': 70, 'race': 'Ross 308', 'fournisseur': 'FarmCo', 'nombre_initial': 100, 'poids_moyen_initial': 26.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 20, 'nombre_morts_totaux': 5, 'cout_unitaire': 1400.0},
            {'nom_bande': 'Bande 5 - Très faible', 'days_ago': 30, 'race': 'Hubbard', 'fournisseur': 'FermesNord', 'nombre_initial': 90, 'poids_moyen_initial': 25.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 8, 'nombre_morts_totaux': 8, 'cout_unitaire': 1550.0},
            {'nom_bande': 'Bande 6 - Efficace', 'days_ago': 25, 'race': 'Cobb 500', 'fournisseur': 'SeedFarm', 'nombre_initial': 220, 'poids_moyen_initial': 22.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 7, 'nombre_morts_totaux': 0, 'cout_unitaire': 1200.0},
            {'nom_bande': 'Bande 7 - Mixte', 'days_ago': 45, 'race': 'Ross 308', 'fournisseur': 'AgroSupply', 'nombre_initial': 140, 'poids_moyen_initial': 27.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 9, 'nombre_morts_totaux': 3, 'cout_unitaire': 1350.0},
            {'nom_bande': 'Bande 8 - Bonne', 'days_ago': 20, 'race': 'Cobb 500', 'fournisseur': 'Local', 'nombre_initial': 160, 'poids_moyen_initial': 30.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 6, 'nombre_morts_totaux': 1, 'cout_unitaire': 1490.0},
            {'nom_bande': 'Bande 9 - Surconsommation', 'days_ago': 10, 'race': 'Ross 308', 'fournisseur': 'FarmCo', 'nombre_initial': 130, 'poids_moyen_initial': 24.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 11, 'nombre_morts_totaux': 4, 'cout_unitaire': 1380.0},
            {'nom_bande': 'Bande 10 - Faible survie', 'days_ago': 80, 'race': 'Hubbard', 'fournisseur': 'FermesNord', 'nombre_initial': 180, 'poids_moyen_initial': 26.5, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 30, 'nombre_morts_totaux': 15, 'cout_unitaire': 1600.0},
            {'nom_bande': 'Bande 11 - Légère sous-consommation', 'days_ago': 15, 'race': 'Cobb 500', 'fournisseur': 'AgroSupply', 'nombre_initial': 110, 'poids_moyen_initial': 28.5, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 4, 'nombre_morts_totaux': 1, 'cout_unitaire': 1500.0},
            {'nom_bande': 'Bande 12 - Variable', 'days_ago': 5, 'race': 'Ross 308', 'fournisseur': 'Local', 'nombre_initial': 100, 'poids_moyen_initial': 27.0, 'statut': 'active', 'duree_jours': 56, 'age_moyen': 2, 'nombre_morts_totaux': 2, 'cout_unitaire': 1420.0}
        ]

        created = 0
        created_names = []
        for s in sample_bandes:
            # Adjust name per eleveur to reduce cross-user collisions
            name_for_eleveur = f"{s['nom_bande']}"  # keep base name
            if name_for_eleveur in existing_names:
                # already present for this eleveur, skip
                continue

                # Normalize poids_moyen_initial to kg if it looks like grams
                initial_poids = s.get('poids_moyen_initial', 0)
                if initial_poids and initial_poids > 10:
                    # assume value is in grams, convert to kg
                    initial_poids = float(initial_poids) / 1000.0

                b = Bande(
                    eleveur_id=eleveur.id,
                    nom_bande=name_for_eleveur,
                    date_arrivee=date.today() - timedelta(days=s['days_ago']),
                    race=s.get('race'),
                    fournisseur=s.get('fournisseur'),
                    nombre_initial=s.get('nombre_initial', 100),
                    poids_moyen_initial=initial_poids,
                    statut=s.get('statut', 'active'),
                    duree_jours=s.get('duree_jours'),
                    age_moyen=s.get('age_moyen'),
                    nombre_morts_totaux=s.get('nombre_morts_totaux', 0),
                    cout_unitaire=s.get('cout_unitaire')
                )
            db.session.add(b)
            created += 1
            created_names.append(name_for_eleveur)

        if created > 0:
            db.session.commit()

        return {
            'created': created,
            'created_names': created_names,
            'existing_count_for_eleveur': len(existing_names),
            'eleveur_id': eleveur.id,
            'eleveur_email': eleveur.email
        }


def seed_full_for_eleveur(app, eleveur_id, weeks_default=12):
    """Populate full time series and records for each band of given eleveur.
    - Deletes existing child records (consommations, animal_info, traitements, depenses)
    - Inserts animal_info (weeks), consommations (weekly), 2 traitements, 2 depenses per band
    Returns a dict with counts inserted.
    """
    from datetime import timedelta
    from modeles.models import Bande, Consommation, AnimalInfo, Traitement, depense_elt

    with app.app_context():
        eleveur = None
        try:
            from modeles.models import Eleveur
            eleveur = Eleveur.query.get(eleveur_id)
        except Exception:
            pass
        if not eleveur:
            return {'error': f'Eleveur id {eleveur_id} introuvable'}

        bands = Bande.query.filter_by(eleveur_id=eleveur_id).all()
        if not bands:
            return {'error': 'Aucune bande trouvée pour cet eleveur'}

        counts = {'bands': len(bands), 'animal_info': 0, 'consommations': 0, 'traitements': 0, 'depenses': 0}

        for b in bands:
            # Remove existing children to ensure idempotency
            Consommation.query.filter_by(bande_id=b.id).delete()
            AnimalInfo.query.filter_by(bande_id=b.id).delete()
            Traitement.query.filter_by(bande_id=b.id).delete()
            depense_elt.query.filter_by(bande_id=b.id).delete()
            # Flush to apply deletes
            db.session.flush()

            # Determine number of weeks
            if b.statut == 'terminee' and b.duree_jours:
                weeks = max(4, int((b.duree_jours + 6) // 7))
            else:
                weeks = weeks_default

            deaths = 0
            base_weight = float(b.poids_moyen_initial or 20.0)
            # If base_weight looks unusually large, assume it was recorded in grams and convert
            if base_weight and base_weight > 10:
                base_weight = base_weight / 1000.0

            # Determine a factor based on band name to vary consumption vs reference
            factor_map = {
                'Excellente': 0.98,
                'Très bonne': 1.03,
                'Moyenne': 1.10,
                'Faible': 1.40,
                'Très faible': 1.50,
                'Efficace': 0.90,
                'Mixte': 1.15,
                'Bonne': 0.99,
                'Surconsommation': 1.35,
                'Faible survie': 1.20,
                'Légère sous-consommation': 0.97,
                'Variable': 1.05
            }
            factor = 1.0
            for k, v in factor_map.items():
                if k in (b.nom_bande or ''):
                    factor = v
                    break

            # Reference per-week consumption values (previously g) — convert to kg
            REF_KGS = [0.150, 0.420, 0.730, 1.100, 1.450, 1.750, 1.950, 2.050]

            # Compute number of weeks and how many to fill
            if b.statut == 'terminee' and b.duree_jours:
                weeks = max(4, int((b.duree_jours + 6) // 7))
            else:
                weeks = weeks_default

            # For active bands, simulate ongoing batches by leaving last 2 weeks empty
            if b.statut == 'active' and weeks > 2:
                fill_weeks = max(1, weeks - 2)
            else:
                fill_weeks = weeks

            current_app.logger.debug('seed_full_for_eleveur: band=%s name=%s statut=%s weeks=%s fill_weeks=%s factor=%s', b.id, b.nom_bande, b.statut, weeks, fill_weeks, factor)

            for i in range(1, fill_weeks + 1):
                # animal_info: give realistic weight progression and mortality patterns
                poids = round(base_weight + i * (base_weight * 0.12), 2)

                # Mortality patterns: increase for weak bands
                if 'Très faible' in (b.nom_bande or ''):
                    morts = 2 if (i % 3 == 0 and deaths < b.nombre_initial) else 1 if (i % 5 == 0 and deaths < b.nombre_initial) else 0
                elif 'Faible survie' in (b.nom_bande or ''):
                    morts = 2 if (i % 4 == 0 and deaths < b.nombre_initial) else 1 if (i % 5 == 0 and deaths < b.nombre_initial) else 0
                else:
                    morts = 1 if (i % 6 == 0 and deaths < b.nombre_initial) else 0

                animaux_restants = max(0, b.nombre_initial - (deaths + morts))

                ai = AnimalInfo(
                    bande_id=b.id,
                    semaine_production=i,
                    poids_moyen=poids,
                    morts_semaine=morts,
                    animaux_restants=animaux_restants,
                    note='seed generated'
                )
                db.session.add(ai)
                counts['animal_info'] += 1
                deaths += morts

                # consommations: use reference kg scaled by band factor
                if i <= len(REF_KGS):
                    ref_kg = REF_KGS[i - 1]
                else:
                    ref_kg = REF_KGS[-1]

                aliment_kg = round(ref_kg * factor, 2)
                cout_aliment = round(aliment_kg * ((b.cout_unitaire or 1500.0) / 100.0), 2)

                if i < 3:
                    type_alim = 'Starter'
                elif i < int(weeks * 0.7):
                    type_alim = 'Croissance'
                else:
                    type_alim = 'Finition'

                cons = Consommation(
                    bande_id=b.id,
                    date=(b.date_arrivee + timedelta(days=7 * (i - 1))),
                    type_aliment=type_alim,
                    cout_aliment=cout_aliment,
                    aliment_kg=aliment_kg,
                    eau_litres=round(aliment_kg * 3.5, 2),
                    semaine_production=i
                )
                db.session.add(cons)
                counts['consommations'] += 1

                # interventions (one small and one medium) for realism
                if i == 1:
                    dep = depense_elt(
                        bande_id=b.id,
                        date=(b.date_arrivee + timedelta(days=10)),
                        type_depense='Maintenance',
                        description='Nettoyage initial (seed)',
                        duree_heures=2.0,
                        cout=round(2000 * factor, 2)
                    )
                    db.session.add(dep)
                    counts['depenses'] += 1
                if i == int(min(weeks, 4)):
                    dep2 = depense_elt(
                        bande_id=b.id,
                        date=(b.date_arrivee + timedelta(days=25)),
                        type_depense='Controle',
                        description='Vérification sanitaire (seed)',
                        duree_heures=1.5,
                        cout=round(1500 * factor, 2)
                    )
                    db.session.add(dep2)
                    counts['depenses'] += 1

            # traitements
            tr1 = Traitement(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=14)),
                produit='Vaccin seed',
                type_traitement='Vaccination',
                dosage='1ml',
                efficacite=0.9 if factor <= 1.1 else 0.7,
                notes='Vaccination prophylactique (seed)',
                cout=round(2000 * factor, 2)
            )
            tr2 = Traitement(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=30)),
                produit='Antibio seed',
                type_traitement='Traitement',
                dosage='2ml',
                efficacite=0.7 if factor <= 1.1 else 0.5,
                notes='Traitement d’exemple (seed)',
                cout=round(3500 * factor, 2),
                nombre_morts_apres=1 if factor > 1.4 else 0
            )
            db.session.add(tr1)
            db.session.add(tr2)
            counts['traitements'] += 2
            # interventions (depense_elt)
            dep1 = depense_elt(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=10)),
                type_depense='Maintenance',
                description='Nettoyage initial (seed)',
                duree_heures=2.0,
                cout=2500.0
            )
            dep2 = depense_elt(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=25)),
                type_depense='Controle',
                description='Vérification sanitaire (seed)',
                duree_heures=1.5,
                cout=1800.0
            )
            db.session.add(dep1)
            db.session.add(dep2)
            counts['depenses'] += 2

            # traitements
            tr1 = Traitement(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=14)),
                produit='Vaccin seed',
                type_traitement='Vaccination',
                dosage='1ml',
                efficacite=0.9,
                notes='Vaccination prophylactique (seed)',
                cout=2000.0
            )
            tr2 = Traitement(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=30)),
                produit='Antibio seed',
                type_traitement='Traitement',
                dosage='2ml',
                efficacite=0.7,
                notes='Traitement d’exemple (seed)',
                cout=3500.0,
                nombre_morts_apres=1
            )
            db.session.add(tr1)
            db.session.add(tr2)
            counts['traitements'] += 2

        db.session.commit()
        return counts


