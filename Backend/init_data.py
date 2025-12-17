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
            {
                'nom_bande': 'Bande Alpha',
                'days_ago': 5,
                'race': 'Cobb 500',
                'fournisseur': 'Fermes du Sud',
                'nombre_initial': 120,
                'poids_moyen_initial': 30.0,
                'statut': 'active',
                'duree_jours': 42,
                'age_moyen': 10,
                'nombre_morts_totaux': 2,
                'cout_unitaire': 1500.0
            },
            {
                'nom_bande': 'Bande Bravo',
                'days_ago': 20,
                'race': 'Ross 308',
                'fournisseur': 'AgroSupply',
                'nombre_initial': 200,
                'poids_moyen_initial': 28.5,
                'statut': 'active',
                'duree_jours': 56,
                'age_moyen': 18,
                'nombre_morts_totaux': 5,
                'cout_unitaire': 1400.0
            },
            {
                'nom_bande': 'Bande Charlie',
                'days_ago': 45,
                'race': 'Cobb 500',
                'fournisseur': 'Local Hatchery',
                'nombre_initial': 150,
                'poids_moyen_initial': 32.0,
                'statut': 'terminee',
                'duree_jours': 42,
                'age_moyen': 42,
                'nombre_morts_totaux': 12,
                'cout_unitaire': 1600.0
            },
            {
                'nom_bande': 'Bande Delta',
                'days_ago': 75,
                'race': 'Ross 308',
                'fournisseur': 'AgroSupply',
                'nombre_initial': 180,
                'poids_moyen_initial': 25.5,
                'statut': 'archivee',
                'duree_jours': 60,
                'age_moyen': 60,
                'nombre_morts_totaux': 20,
                'cout_unitaire': 1300.0
            },
            {
                'nom_bande': 'Bande Echo',
                'days_ago': 10,
                'race': 'Hubbard',
                'fournisseur': 'Fermes du Nord',
                'nombre_initial': 90,
                'poids_moyen_initial': 27.0,
                'statut': 'active',
                'duree_jours': 45,
                'age_moyen': 12,
                'nombre_morts_totaux': 1,
                'cout_unitaire': 1550.0
            },
            {
                'nom_bande': 'Bande Foxtrot',
                'days_ago': 30,
                'race': 'Cobb 500',
                'fournisseur': 'Hatch & Co',
                'nombre_initial': 130,
                'poids_moyen_initial': 29.0,
                'statut': 'terminee',
                'duree_jours': 50,
                'age_moyen': 50,
                'nombre_morts_totaux': 10,
                'cout_unitaire': 1480.0
            },
            {
                'nom_bande': 'Bande Golf',
                'days_ago': 3,
                'race': 'Ross 308',
                'fournisseur': 'AgroSupply',
                'nombre_initial': 220,
                'poids_moyen_initial': 22.0,
                'statut': 'active',
                'duree_jours': 70,
                'age_moyen': 5,
                'nombre_morts_totaux': 0,
                'cout_unitaire': 1200.0
            },
            {
                'nom_bande': 'Bande Hotel',
                'days_ago': 100,
                'race': 'Hubbard',
                'fournisseur': 'Fermes du Nord',
                'nombre_initial': 110,
                'poids_moyen_initial': 26.0,
                'statut': 'archivee',
                'duree_jours': 65,
                'age_moyen': 65,
                'nombre_morts_totaux': 25,
                'cout_unitaire': 1700.0
            },
            {
                'nom_bande': 'Bande India',
                'days_ago': 15,
                'race': 'Cobb 500',
                'fournisseur': 'Local Hatchery',
                'nombre_initial': 160,
                'poids_moyen_initial': 30.5,
                'statut': 'active',
                'duree_jours': 48,
                'age_moyen': 16,
                'nombre_morts_totaux': 3,
                'cout_unitaire': 1490.0
            },
            {
                'nom_bande': 'Bande Juliett',
                'days_ago': 60,
                'race': 'Ross 308',
                'fournisseur': 'Hatch & Co',
                'nombre_initial': 140,
                'poids_moyen_initial': 24.0,
                'statut': 'terminee',
                'duree_jours': 54,
                'age_moyen': 54,
                'nombre_morts_totaux': 14,
                'cout_unitaire': 1350.0
            }
        ]

        created = 0
        created_names = []
        for s in sample_bandes:
            # Adjust name per eleveur to reduce cross-user collisions
            name_for_eleveur = f"{s['nom_bande']}"  # keep base name
            if name_for_eleveur in existing_names:
                # already present for this eleveur, skip
                continue

            b = Bande(
                eleveur_id=eleveur.id,
                nom_bande=name_for_eleveur,
                date_arrivee=date.today() - timedelta(days=s['days_ago']),
                race=s.get('race'),
                fournisseur=s.get('fournisseur'),
                nombre_initial=s.get('nombre_initial', 100),
                poids_moyen_initial=s.get('poids_moyen_initial', 0),
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

            for i in range(1, weeks + 1):
                # animal_info
                poids = round(base_weight + i * (base_weight * 0.12), 2)
                morts = 1 if (i % 5 == 0 and deaths < b.nombre_initial) else 0
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

                # consommations
                if i < 3:
                    type_alim = 'Starter'
                elif i < int(weeks * 0.7):
                    type_alim = 'Croissance'
                else:
                    type_alim = 'Finition'

                aliment_kg = round(max(0.1, (b.nombre_initial * (0.08 + 0.01 * i))), 2)
                cout_aliment = round(aliment_kg * ((b.cout_unitaire or 1500.0) / 100.0), 2)

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


