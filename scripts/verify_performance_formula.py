import sys
sys.path.insert(0,'Backend')
from app import app
from modeles.models import Bande
from routes.dashboard import compute_performance_for_band

with app.app_context():
    bands = Bande.query.filter_by(eleveur_id=2).order_by(Bande.id).all()
    mismatches = []
    print('Verifying performance formula for eleveur id=2')
    for b in bands:
        perf = compute_performance_for_band(b)
        reported = perf.get('performance_percent')
        subs = perf.get('subscores') or {}
        consumption = subs.get('consumption')
        mortality_avg = subs.get('mortality_avg_pct')
        # compute expected value
        if consumption is not None and mortality_avg is not None:
            expected = round((consumption + (100.0 - mortality_avg)) / 2.0, 1)
        elif consumption is not None:
            expected = float(consumption)
        elif mortality_avg is not None:
            expected = round(100.0 - mortality_avg, 1)
        else:
            expected = None
        print(f"Bande {b.id} {b.nom_bande}: reported={reported} expected={expected} (consumption={consumption}, mortality_avg={mortality_avg})")
        if (reported is None and expected is not None) or (reported is not None and expected is None) or (reported is not None and abs(reported - expected) > 0.1):
            mismatches.append({'id': b.id, 'nom': b.nom_bande, 'reported': reported, 'expected': expected})
    if mismatches:
        print('\nMISMATCHES:')
        for m in mismatches:
            print(m)
        sys.exit(2)
    else:
        print('\nAll band performances match the formula.')
