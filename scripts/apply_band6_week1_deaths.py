import sys
sys.path.insert(0, 'Backend')
from app import app
from modeles.models import Bande, AnimalInfo
from modeles.models import db

# Try by id first (if you provided). If not found, fall back to the seeded name 'Bande Init 06'
TARGET_BAND_ID = 262  # may vary after reseed
TARGET_WEEK = 1
TARGET_DEATHS = 50

with app.app_context():
    b = Bande.query.filter_by(id=TARGET_BAND_ID).first()
    if not b:
        b = Bande.query.filter_by(nom_bande='Bande Init 06').first()
        if not b:
            print(f"Bande id={TARGET_BAND_ID} introuvable et 'Bande Init 06' introuvable")
            sys.exit(1)
        else:
            print(f"Falling back to name lookup: using bande id={b.id} (nom={b.nom_bande})")

    initial = b.nombre_initial or 0
    ai = AnimalInfo.query.filter_by(bande_id=b.id, semaine_production=TARGET_WEEK).first()
    if not ai:
        print(f"AnimalInfo S{TARGET_WEEK} introuvable pour bande id={TARGET_BAND_ID}")
        sys.exit(1)

    prev_morts = int(ai.morts_semaine or 0)
    # cap target to not exceed remaining animals
    max_possible = max(0, initial - (b.nombre_morts_totaux or 0) + prev_morts)  # approximate safe cap
    morts_new = min(TARGET_DEATHS, max_possible)

    # Set new week deaths and adjust animaux_restants and band totals
    ai.morts_semaine = morts_new
    # recompute animaux_restants as initial - cumulative deaths (very conservative: recompute from all AnimalInfo)
    all_weeks = AnimalInfo.query.filter_by(bande_id=b.id).order_by(AnimalInfo.semaine_production).all()
    total_morts = 0
    for w in all_weeks:
        if w.id == ai.id:
            total_morts += morts_new
        else:
            total_morts += int(w.morts_semaine or 0)
    # update animaux_restants for week 1 row
    ai.animaux_restants = max(0, initial - total_morts)

    # update bande total morts
    b.nombre_morts_totaux = total_morts

    db.session.add(ai)
    db.session.add(b)
    db.session.commit()

    print(f"Updated band {b.nom_bande} (id={b.id}): week {TARGET_WEEK} morts {prev_morts} -> {morts_new}, total_morts now {b.nombre_morts_totaux}")
