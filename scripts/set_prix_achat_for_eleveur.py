import sys
sys.path.append(r'c:\Users\hp\TP_INF331\Backend')
from app import app
from modeles.models import Bande, db

ELEVEUR_ID = 2
NEW_PRICE = 300.0

with app.app_context():
    bandes = Bande.query.filter_by(eleveur_id=ELEVEUR_ID).all()
    updated = 0
    for b in bandes:
        b.prix_achat_unitaire = float(NEW_PRICE)
        updated += 1
    db.session.commit()
    print(f"Updated {updated} bande(s) for eleveur_id={ELEVEUR_ID} to prix_achat_unitaire={NEW_PRICE}")
    for b in bandes:
        print(b.id, b.nom_bande, b.prix_achat_unitaire, b.nombre_initial)
