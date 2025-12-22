import sys
sys.path.insert(0, r"c:\Users\hp\TP_INF331")
sys.path.insert(0, r"c:\Users\hp\TP_INF331\Backend")
from modeles.models import Bande
from Backend.app import app
with app.app_context():
    bands = Bande.query.filter_by(eleveur_id=2).all()
    print('Found', len(bands), 'bands')
    for b in bands:
        print(b.id, b.nom_bande, b.statut)
