import sys
sys.path.insert(0,'Backend')
from app import app
from modeles.models import Consommation, Bande
with app.app_context():
    bands=Bande.query.filter_by(eleveur_id=2).order_by(Bande.id).all()
    print('Summary for eleveur id=2 (12 bandes):')
    for b in bands:
        ai = b.animal_infos and next((x for x in b.animal_infos if x.semaine_production==1), None)
        c = Consommation.query.filter_by(bande_id=b.id, semaine_production=1).first()
        note = ai.note if ai else ''
        morts = ai.morts_semaine if ai else 0
        print(f"{b.nom_bande:15} | S1 aliment_kg={c.aliment_kg:8.2f} kg | eau={c.eau_litres:7.2f} L | morts_S1={morts:2d} | note={note}")
