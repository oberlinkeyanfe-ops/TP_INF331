import sys
sys.path.append(r'c:\Users\hp\TP_INF331\Backend')
from app import app
from modeles.models import Bande

with app.app_context():
    for b in Bande.query.limit(50).all():
        print(b.id, b.nom_bande, 'eleveur_id=', b.eleveur_id, 'prix_achat_unitaire=', b.prix_achat_unitaire, 'nombre_initial=', b.nombre_initial)
