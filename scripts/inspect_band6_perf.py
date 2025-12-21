import sys
sys.path.insert(0,'Backend')
from app import app
from modeles.models import Bande, Consommation, AnimalInfo
from routes.dashboard import compute_performance_for_band

with app.app_context():
    b = Bande.query.filter_by(nom_bande='Bande Init 06').first()
    if not b:
        print('Bande Init 06 not found')
        sys.exit(1)
    print('Band id:', b.id, 'nombre_initial:', b.nombre_initial, 'nombre_morts_totaux:', b.nombre_morts_totaux)
    ais = AnimalInfo.query.filter_by(bande_id=b.id).order_by(AnimalInfo.semaine_production).all()
    print('AnimalInfo rows:')
    for a in ais:
        print(f'  week {a.semaine_production}: morts={a.morts_semaine}, animaux_restants={a.animaux_restants}')
    cons = Consommation.query.filter_by(bande_id=b.id).order_by(Consommation.semaine_production).all()
    print('Consommations:')
    for c in cons:
        print(f'  week {c.semaine_production}: aliment_kg={c.aliment_kg}, cout_aliment={c.cout_aliment}')
    perf = compute_performance_for_band(b)
    print('\nComputed performance from backend:')
    print(perf)
    print('\nFrontend-derived survivorsCount and survivalPerformance:')
    total_deaths = sum([a.morts_semaine or 0 for a in ais])
    survivors = max(0, (b.nombre_initial or 0) - total_deaths)
    print(' total_deaths:', total_deaths, ' survivors:', survivors, ' survival_pct:', round((survivors/(b.nombre_initial or 1))*100,1))
