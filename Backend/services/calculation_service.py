# services/calculation_service.py - COMPLÉTER
def calculer_cout_bande(bande_id):
    """Calcule le coût total d'une bande"""
    depenses = Depense.query.filter_by(bande_id=bande_id).all()
    return sum(d.montant for d in depenses)

def calculer_consommation_moyenne(bande_id):
    """Calcule la consommation moyenne quotidienne"""
    consommations = Consommation.query.filter_by(bande_id=bande_id).all()
    if not consommations:
        return 0
    return sum(c.aliment_kg for c in consommations) / len(consommations)

def calculer_taux_mortalite(bande):
    """Calcule le taux de mortalité"""
    if bande.nombre_initial == 0:
        return 0
    return (bande.nombre_morts_totaux / bande.nombre_initial) * 100