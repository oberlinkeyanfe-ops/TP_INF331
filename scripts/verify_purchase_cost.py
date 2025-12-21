import sys
sys.path.append(r'c:\Users\hp\TP_INF331\Backend')
from app import app
from modeles.models import Bande, Consommation, depense_elt, Traitement
from modeles.database import db
from sqlalchemy import func

with app.app_context():
    for b in Bande.query.filter_by(eleveur_id=2).all():
        total_cons_cout = db.session.query(func.coalesce(func.sum(Consommation.cout_aliment), 0)).filter_by(bande_id=b.id).scalar() or 0
        total_depenses = db.session.query(func.coalesce(func.sum(depense_elt.cout), 0)).filter_by(bande_id=b.id).scalar() or 0
        total_traitements = db.session.query(func.coalesce(func.sum(Traitement.cout), 0)).filter_by(bande_id=b.id).scalar() or 0
        cout_achat_animaux = float((b.prix_achat_unitaire or 0.0) * (b.nombre_initial or 0))
        total = float(total_cons_cout or 0) + float(total_depenses or 0) + float(total_traitements or 0) + cout_achat_animaux
        print(f"Bande {b.id} {b.nom_bande}: cout_aliment={total_cons_cout}, cout_depenses={total_depenses}, cout_traitements={total_traitements}, cout_achat_animaux={cout_achat_animaux}, cout_total={total}")
