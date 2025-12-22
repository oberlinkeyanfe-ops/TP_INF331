import sys
sys.path.append(r'c:\Users\hp\TP_INF331\Backend')
from app import app
from modeles.models import Eleveur, db

with app.app_context():
    e = Eleveur.query.get(2)
    if e:
        e.set_password('seedpass123')
        db.session.commit()
        print('Password updated for eleveur id=2:', e.email)
    else:
        print('Eleveur id=2 not found')
