# Changelog

## 2025-12-19 — Convert weights from grams to kilograms

- Frontend: labels and charts updated to use **kg** (e.g., `Poids moyen (kg)`, `kg/j`)
- Backend: inputs for `poids_moyen` and `poids_moyen_initial` now accept legacy gram values and normalize them to kg.
- Seed: `init_data.py` now treats sample weights as grams when >10 and normalizes them to kg; reference weekly consumption values converted to kg.
- DB migration: added Alembic migration `convert_weights_to_kg` to divide historical weight values that look like grams by 1000 (best-effort; please backup DB before running migrations).

Notes:
- To apply DB changes: create a DB backup, then run `alembic upgrade head` from the Backend folder.
- After migration, clear any frontend caches (e.g., `localStorage.removeItem('bands_cache')`) to see updated values in UI.
