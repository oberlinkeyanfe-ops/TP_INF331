import sys
sys.path.append(r'c:\Users\hp\TP_INF331\Backend')
from app import app
from modeles.models import Eleveur

with app.app_context():
    for e in Eleveur.query.all():
        print(e.id, e.nom, e.email, '[pw]' if e.mot_de_passe else '[no]')
