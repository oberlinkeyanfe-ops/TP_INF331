from app import app
from modeles.models import Eleveur

with app.app_context():
    users = Eleveur.query.all()
    for u in users:
        print(u.id, u.nom, u.email, '[pw hashed]' if u.mot_de_passe else '[no pw]')
