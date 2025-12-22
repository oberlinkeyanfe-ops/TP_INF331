from pathlib import Path
p=Path('Backend/routes/dashboard.py')
b=p.read_bytes()
start_pat=b"# Recent treatments (last 5)"
start=b.find(start_pat)
if start==-1:
    print('start not found')
    raise SystemExit(1)
# find a nearby 't(5).all' occurrence after start
end_pat=b"t(5).all()"
end=b.find(end_pat, start)
if end==-1:
    print('end not found')
    raise SystemExit(1)
end_pos=end+len(end_pat)
print('Found start',start,'end',end_pos)
# Prepare replacement bytes
new_block=b"# Recent treatments (last 5)\r\n        traitements = Traitement.query.filter_by(bande_id=b.id).order_by(Traitement.date.desc()).limit(5).all()\r\n\r\n        # Top aliment by total kg\r\n        top_alim_row = db.session.query(Consommation.type_aliment, func.coalesce(func.sum(Consommation.aliment_kg), 0).label('total_kg')).filter_by(bande_id=b.id).group_by(Consommation.type_aliment).order_by(func.sum(Consommation.aliment_kg).desc()).first()\r\n        top_aliment = {'type_aliment': None, 'total_kg': 0}\r\n        if top_alim_row:\r\n            top_aliment = {'type_aliment': top_alim_row.type_aliment, 'total_kg': float(top_alim_row.total_kg or 0)}\r\n\r\n        # consommation totale and per animal\r\n        total_cons = db.session.query(func.coalesce(func.sum(Consommation.aliment_kg), 0)).filter_by(bande_id=b.id).scalar() or 0\r\n        consommation_par_animal = float(total_cons) / b.nombre_initial if b.nombre_initial else 0\r\n\r\n        # latest mean weight\r\n        latest_info = AnimalInfo.query.filter_by(bande_id=b.id).order_by(AnimalInfo.semaine_production.desc()).first()\r\n        latest_weight = float(latest_info.poids_moyen) if latest_info and latest_info.poids_moyen else None\r\n\r\n        # Estimate IC moyen (simplified): consommation_par_animal / latest_weight if available\r\n        ic_moyen = None\r\n        if latest_weight and latest_weight > 0:\r\n            ic_moyen = round(consommation_par_animal / latest_weight, 2)\r\n\r\n        taux_mortalite = round((float(b.nombre_morts_totaux or 0) / b.nombre_initial) * 100, 2) if b.nombre_initial else 0\r\n        taux_survie = round(100 - taux_mortalite, 2)\r\n\r\n        # Compute performance components\r\n        perf = compute_performance_for_band(b)\r\n\r\n        return jsonify({\r\n            'bande_id': b.id,\r\n            'nom_bande': b.nom_bande,\r\n            'race': b.race,\r\n            'traitements': [t.to_dict() for t in traitements],\r\n            'top_aliment': top_aliment,\r\n            'consommation_par_animal': round(consommation_par_animal, 2),\r\n            'ic_moyen': ic_moyen,\r\n            'taux_mortalite': taux_mortalite,\r\n            'taux_survie': taux_survie,\r\n            'performance': perf\r\n        })\r\n    except Exception as e:\r\n        current_app.logger.exception('Failed to fetch bande details: %s', e)\r\n        return jsonify({'error': str(e)}), 500\r\n"
# Perform replacement
newb=b[:start]+new_block+b[end_pos:]
# backup and write
p.with_suffix('.py.bak').write_bytes(b)
p.write_bytes(newb)
print('Replaced and backed up')
