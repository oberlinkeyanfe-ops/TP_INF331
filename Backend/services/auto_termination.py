from datetime import date, timedelta
from modeles.models import Bande
from modeles.database import db


def terminate_finished_bandes(app=None):
    """Find bands whose end date (date_arrivee + duree_jours) is <= today
    and set statut = 'terminee' if not already. Returns a dict with counts and ids.
    """
    from flask import current_app
    ctx = app if app is not None else current_app
    updated = []
    try:
        with ctx.app_context():
            today = date.today()
            bandes = Bande.query.filter(Bande.statut != 'terminee').all()
            for b in bandes:
                try:
                    if not b.date_arrivee or not b.duree_jours:
                        continue
                    end_date = b.date_arrivee + timedelta(days=int(b.duree_jours))
                    if end_date <= today:
                        b.statut = 'terminee'
                        updated.append(b.id)
                except Exception as inner_e:
                    # ignore per-row failures but log
                    print(f"⚠️ Erreur traitement bande {b.id}: {inner_e}")
            if updated:
                db.session.commit()
                print(f"✅ {len(updated)} bande(s) marquée(s) 'terminee': {updated}")
            else:
                print("ℹ️ Aucune bande à terminer aujourd'hui.")
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification des bandes terminées: {e}")
    return {'updated_count': len(updated), 'updated_ids': updated}
