from datetime import date, timedelta
import random
from modeles.models import db, Bande, Consommation, AnimalInfo, Traitement, depense_elt, Eleveur

# Constants: PU en FCFA
PU_ALIMENT_KG = 200.0
PU_EAU_L = 25.0

def init_eleveur_2(app, weeks_default=12, pu_aliment=PU_ALIMENT_KG, pu_eau=PU_EAU_L):
    """Initialise 12 bandes pour l'eleveur id=2 avec consommations, depenses, animal_info et traitements.

    - Respecte: 0.1kg < poids_moyen_initial < 0.2kg
    - Poids et consommations en kg.
    - Crée l'eleveur id=2 s'il n'existe pas.
    """
    with app.app_context():
        eleveur = Eleveur.query.get(2)
        if not eleveur:
            eleveur = Eleveur(id=2, nom='Eleveur Init', email='eleveur2@init.local')
            eleveur.set_password('init1234')
            db.session.add(eleveur)
            db.session.commit()

        # If there are already bands for this eleveur, do nothing
        existing = Bande.query.filter_by(eleveur_id=eleveur.id).count()
        if existing >= 12:
            return {'ok': True, 'message': f'{existing} bandes déjà présentes pour eleveur id=2'}

        created_bands = []

        for i in range(1, 13):
            # Slightly different properties per band
            name = f"Bande Init {i:02d}"
            days_ago = random.randint(7, 90)
            nombre_initial = random.randint(80, 220)
            poids_moyen_initial = round(random.uniform(0.11, 0.19), 3)  # 0.11 - 0.19 kg
            statut = 'active' if i % 3 != 0 else 'terminee'
            duree_jours = 56
            age_moyen = random.randint(5, 20)

            b = Bande(
                eleveur_id=eleveur.id,
                nom_bande=name,
                date_arrivee=date.today() - timedelta(days=days_ago),
                race=random.choice(['Cobb 500', 'Ross 308', 'Hubbard']),
                fournisseur=random.choice(['SeedFarm', 'AgroSupply', 'Local farm']),
                nombre_initial=nombre_initial,
                poids_moyen_initial=poids_moyen_initial,
                statut=statut,
                duree_jours=duree_jours,
                age_moyen=age_moyen,
                nombre_morts_totaux=0,
                cout_unitaire=2000.0
            )
            db.session.add(b)
            db.session.flush()  # ensure b.id available

            # Set initial purchase unit price for seeded band (FCFA per bird)
            b.prix_achat_unitaire = float(random.randint(1200, 2800))

            # Simulate weeks of data using band references (from Frontend `Bandes.vue`)
            weeks = weeks_default

            # Consumption reference per bird (kg) — values taken from Front_end `Bandes.vue`
            # Each entry is a tuple (per_bird_low, per_bird_high)
            consumption_reference = [
                (0.13, 0.167),
                (0.28, 0.375),
                (0.47, 0.65),
                (0.64, 0.945),
                (0.85, 1.215),
                (1.07, 1.434),
                (1.18, 1.593),
                (1.30, 1.691)
            ]
            # Water reference (litres) taken from Front_end `Bandes.vue`
            water_reference = [300.0, 640.0, 980.0, 1350.0, 1680.0, 1900.0, 2050.0, 2150.0]

            # Weight reference per week (kg)
            weight_reference = [
                {'week': 1, 'low': 0.08, 'high': 0.12},
                {'week': 2, 'low': 0.18, 'high': 0.25},
                {'week': 3, 'low': 0.30, 'high': 0.45},
                {'week': 4, 'low': 0.50, 'high': 0.70},
                {'week': 5, 'low': 0.70, 'high': 1.00},
                {'week': 6, 'low': 0.90, 'high': 1.30},
                {'week': 7, 'low': 1.05, 'high': 1.55},
                {'week': 8, 'low': 1.20, 'high': 1.80},
                {'week': 9, 'low': 1.35, 'high': 2.00},
                {'week': 10, 'low': 1.50, 'high': 2.20},
                {'week': 11, 'low': 1.50, 'high': 2.20},
                {'week': 12, 'low': 1.50, 'high': 2.20}
            ]

            # Mortality reference (percent bounds per week)
            mortality_reference = [
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

            # Treatment and elementary expense catalogs copied from Front_end/src/pages/Bandes.vue
            treatment_catalog = [
                {'name': 'Baytril', 'type': 'Antibiotique (enrofloxacine)', 'cost': 6500.0,
                 'doses': ['8-10 mg/kg/j (eau) pendant 3 jours', '10-12 mg/kg/j (eau) pendant 3-5 jours', '12-15 mg/kg/j (eau) pendant 5 jours']},
                {'name': 'Lévomycétine', 'type': 'Antibiotique', 'cost': 5200.0,
                 'doses': ['3-5 mg/kg 2x/j 5 jours', '5-10 mg/kg 2x/j 5-7 jours', '15-20 mg/kg/j 5-7 jours']},
                {'name': 'Dithrim', 'type': 'Antibiotique (TMP + sulfadimézine)', 'cost': 4800.0,
                 'doses': ['0.2 ml/kg/j (inj) 3 jours', '0.3 ml/kg/j (inj) 3-5 jours', '0.35 ml/kg/j (inj) 5 jours']},
                {'name': 'Enroflon', 'type': 'Antibiotique (enrofloxacine)', 'cost': 4300.0,
                 'doses': ['0.5 ml/L eau 3 jours', '1 ml/L eau 3-5 jours', '1-1.5 ml/L eau 5 jours']},
                {'name': 'Doreen', 'type': 'Antibiotique (rifampicine + doxycycline)', 'cost': 5600.0,
                 'doses': ['10 mg/kg/j 3 jours', '15 mg/kg/j 5 jours', '20 mg/kg/j 5-7 jours']},
                {'name': 'Amoxicilline', 'type': 'Antibiotique', 'cost': 5100.0,
                 'doses': ['10-12 mg/kg/j 3 jours', '15 mg/kg/j 5 jours', '20 mg/kg/j 5-7 jours']},
                {'name': 'Doxycycline', 'type': 'Antibiotique (tétracycline)', 'cost': 4700.0,
                 'doses': ['10 mg/kg/j 3 jours', '15 mg/kg/j 5 jours', '20 mg/kg/j 5-7 jours']},
                {'name': 'Trichopole', 'type': 'Antiprotozoaire', 'cost': 3900.0,
                 'doses': ['10 mg/kg/j 3 jours', '15 mg/kg/j 5 jours', '20 mg/kg/j 5-7 jours']},
                {'name': 'Furazolidone', 'type': 'Antibiotique (nitrofurane)', 'cost': 3600.0,
                 'doses': ['5 mg/kg/j 5 jours', '7 mg/kg/j 5 jours', '10 mg/kg/j 5-7 jours']},
                {'name': 'Tétracycline', 'type': 'Antibiotique', 'cost': 4500.0,
                 'doses': ['10 mg/kg/j 3 jours', '15 mg/kg/j 5 jours', '20 mg/kg/j 5-7 jours']},
                {'name': 'Biomycine', 'type': 'Antibiotique', 'cost': 4200.0,
                 'doses': ['10 mg/kg/j 3 jours', '12 mg/kg/j 5 jours', '15 mg/kg/j 5-7 jours']},
                {'name': 'Sulfadimezin', 'type': 'Sulfamidé', 'cost': 3300.0,
                 'doses': ['20 mg/kg/j 3 jours', '25 mg/kg/j 3-5 jours', '30 mg/kg/j 5 jours']},
                {'name': 'Chlortétracycline', 'type': 'Tétracycline', 'cost': 4000.0,
                 'doses': ['10 mg/kg/j 3 jours', '15 mg/kg/j 5 jours', '20 mg/kg/j 5-7 jours']}
            ]

            expense_catalog = [
                {'name': 'Chauffage', 'description': 'Gaz, fioul ou électrique pour maintenir la température.'},
                {'name': 'Électricité', 'description': 'Éclairage, ventilation, automatisation.'},
                {'name': 'Transport', 'description': 'Acheminement aliments, animaux ou produits.'},
                {'name': 'Copeaux / litière', 'description': 'Approvisionnement en litière pour confort et hygiène.'},
                {'name': 'Nettoyage / désinfection', 'description': 'Produits et prestations de biosécurité.'},
                {'name': 'Taxes / redevances', 'description': 'Taxes locales et redevances administratives.'},
                {'name': 'Installation / maintenance', 'description': 'Réparations, maintenance d’équipements.'},
                {'name': 'Maintenance (autres)', 'description': 'Maintenance générale hors installations principales.'},
                {'name': 'Autres', 'description': 'Dépenses diverses et imprévues.'}
            ]

            # Define profiles to vary consumption and mortality to produce performance range
            # Tuple: (name, cons_delta_base, weight_delta_base, mortality_multiplier, cons_multiplier)
            profiles = [
                ('excellente', -0.06, 0.04, 0.4, 0.92),
                ('tres_bonne', -0.04, 0.025, 0.7, 0.95),
                ('moyenne', -0.02, 0.0, 1.0, 1.0),
                ('baseline', 0.0, 0.0, 1.0, 1.0),  # leave unchanged
                ('eleve_cons', 0.05, -0.02, 1.1, 1.12),  # slightly higher consumption
                ('faible', 0.06, -0.03, 1.3, 1.05),
                ('mort_eleve', 0.02, -0.02, 3.5, 1.02),  # higher mortality
                ('tres_faible', 0.15, -0.06, 1.7, 1.15),
                ('mort_tres_eleve', 0.12, -0.06, 6.0, 1.05),  # very high mortality
                ('efficace', -0.08, 0.05, 0.6, 0.95),
                ('mixte', 0.02, 0.0, 1.05, 1.0)
            ]

            deaths = 0

            # pick profile deterministically from index to ensure variety across seeded bands
            qname, cons_delta_base, weight_delta_base, mortality_multiplier, cons_multiplier = profiles[(i - 1) % len(profiles)]

            for w in range(1, weeks + 1):
                # Weight target from reference for week (use last known if beyond)
                if w <= len(weight_reference):
                    wr = weight_reference[w - 1]
                    ref_low = wr['low']
                    ref_high = wr['high']
                else:
                    wr = weight_reference[-1]
                    ref_low = wr['low']
                    ref_high = wr['high']

                # For best bands, choose near ref_high; for worst, near ref_low
                if qname in ('excellente', 'efficace'):
                    poids = round(random.uniform(ref_high * 0.98, ref_high * 1.03), 3)
                elif qname == 'tres_bonne':
                    poids = round(random.uniform(ref_high * 0.95, ref_high * 1.01), 3)
                elif qname == 'moyenne':
                    poids = round(random.uniform(ref_low * 0.98, ref_high * 1.02), 3)
                elif qname == 'mixte':
                    poids = round(random.uniform(ref_low * 0.95, ref_high * 1.05), 3)
                elif qname == 'faible':
                    poids = round(random.uniform(max(0.01, ref_low * 0.9), ref_high * 0.98), 3)
                else:  # tres_faible
                    poids = round(random.uniform(max(0.01, ref_low * 0.8), ref_low * 0.98), 3)

                # Ensure poids within reasonable bounds
                poids = max(0.01, min(poids, 2.5))

                # Mortality percent base from mortality_reference
                if w <= len(mortality_reference):
                    mr = mortality_reference[w - 1]
                    mort_pct_base = random.uniform(mr['low'], mr['high'])
                else:
                    mort_pct_base = random.uniform(mortality_reference[-1]['low'], mortality_reference[-1]['high'])

                mort_pct = mort_pct_base * mortality_multiplier
                # Early spike for high-mortality profiles to accentuate poor performance
                if qname == 'mort_eleve' and w <= 3:
                    mort_pct *= 1.5
                elif qname == 'mort_tres_eleve' and w <= 4:
                    mort_pct *= 2.0
                # Special override for Band Init 06: set 30% mortality in week 1
                if i == 6 and w == 1:
                    mort_pct = 30.0
                mort_pct = max(0.0, mort_pct)

                # deaths this week (rounded, never exceed remaining animals)
                animaux_restants = max(0, nombre_initial - deaths)
                expected_deaths = int(round(nombre_initial * (mort_pct / 100.0)))
                morts = min(animaux_restants, expected_deaths)

                # Special override: for the 6th seeded band (i==6) force week 1 deaths to 50
                if i == 6 and w == 1:
                    morts = min(animaux_restants, 50)

                animaux_restants = max(0, nombre_initial - (deaths + morts))

                ai = AnimalInfo(
                    bande_id=b.id,
                    semaine_production=w,
                    poids_moyen=poids,
                    morts_semaine=morts,
                    animaux_restants=animaux_restants,
                    note=f'init seed ({qname})'
                )
                db.session.add(ai)
                deaths += morts

                # Consommation: use consumption_reference (kg) and modulate by quality
                if w <= len(consumption_reference):
                    per_bird_low, per_bird_high = consumption_reference[w - 1]
                    per_bird_avg = (per_bird_low + per_bird_high) / 2.0
                else:
                    per_bird_low, per_bird_high = consumption_reference[-1]
                    per_bird_avg = (per_bird_low + per_bird_high) / 2.0

                # Apply small random variation plus profile delta and multiplier on per-bird basis
                cons_delta = cons_delta_base + random.uniform(-0.03, 0.03)
                per_bird_final = max(0.0, per_bird_avg * (1 + cons_delta) * cons_multiplier)
                aliment_kg = round(per_bird_final * nombre_initial, 3)

                # Use water reference when available, otherwise estimate by ratio
                if w <= len(water_reference):
                    ref_water = water_reference[w - 1]
                else:
                    ref_water = water_reference[-1]
                eau_l = round(ref_water * (1 + random.uniform(-0.05, 0.05)), 2)
                cout_aliment = round(aliment_kg * pu_aliment, 2)

                cons = Consommation(
                    bande_id=b.id,
                    date=(b.date_arrivee + timedelta(days=7 * (w - 1))),
                    type_aliment='Starter' if w < 3 else 'Croissance' if w < int(weeks * 0.7) else 'Finition',
                    cout_aliment=cout_aliment,
                    aliment_kg=aliment_kg,
                    eau_litres=eau_l,
                    semaine_production=w
                )
                db.session.add(cons)

                # Elementary expenses in week 2 and week 5 using frontend expense_catalog
                if w == 2:
                    item = random.choice(expense_catalog)
                    dep = depense_elt(
                        bande_id=b.id,
                        date=(b.date_arrivee + timedelta(days=10)),
                        type_depense=item['name'],
                        description=f"{item.get('description','')} (init)",
                        duree_heures=round(random.uniform(0.5, 3.0), 1),
                        cout=round(random.uniform(1500, 6000) * (1 + (i % 3) * 0.1), 2)
                    )
                    db.session.add(dep)
                if w == 5:
                    item2 = random.choice(expense_catalog)
                    dep2 = depense_elt(
                        bande_id=b.id,
                        date=(b.date_arrivee + timedelta(days=25)),
                        type_depense=item2['name'],
                        description=f"{item2.get('description','')} (contrôle init)",
                        duree_heures=round(random.uniform(1.0, 4.0), 1),
                        cout=round(random.uniform(2000, 8000) * (1 + (i % 4) * 0.12), 2)
                    )
                    db.session.add(dep2)

            # traitements (two per band) chosen from frontend treatment_catalog
            t_choice1 = random.choice(treatment_catalog)
            dose1 = t_choice1['doses'][0] if t_choice1.get('doses') else ''
            effic1 = round(max(0.4, min(0.98, random.uniform(0.6, 0.95) - (0.05 if qname in ('tres_faible','faible') else 0.0))), 2)
            tr1 = Traitement(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=14)),
                produit=t_choice1['name'],
                type_traitement=t_choice1['type'],
                dosage=dose1,
                efficacite=effic1,
                notes=f'Init {t_choice1["name"]}',
                cout=t_choice1['cost']
            )

            t_choice2 = random.choice(treatment_catalog)
            dose2 = t_choice2['doses'][0] if t_choice2.get('doses') else ''
            effic2 = round(max(0.3, min(0.95, random.uniform(0.55, 0.9) - (0.05 if qname in ('tres_faible','faible') else 0.0))), 2)
            tr2 = Traitement(
                bande_id=b.id,
                date=(b.date_arrivee + timedelta(days=30)),
                produit=t_choice2['name'],
                type_traitement=t_choice2['type'],
                dosage=dose2,
                efficacite=effic2,
                notes=f'Init {t_choice2["name"]}',
                cout=t_choice2['cost'],
                nombre_morts_apres=random.randint(0, max(0, int(nombre_initial * 0.02)))
            )
            db.session.add(tr1)
            db.session.add(tr2)

            created_bands.append(name)

        db.session.commit()

        return {'created': len(created_bands), 'names': created_bands}
