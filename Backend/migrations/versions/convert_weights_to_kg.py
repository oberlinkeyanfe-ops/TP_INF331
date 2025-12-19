"""
Revision ID: convert_weights_to_kg
Revises: 9f1129209b18_init
Create Date: 2025-12-19 00:00:00.000000

This migration converts all historical weight fields stored as grams to kilograms.
It assumes previous values were stored in grams (g) and divides them by 1000.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'convert_weights_to_kg'
down_revision = '9f1129209b18_init'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Update bandes.poids_moyen_initial if values were in grams
    try:
        op.execute("UPDATE bandes SET poids_moyen_initial = poids_moyen_initial / 1000.0 WHERE poids_moyen_initial IS NOT NULL AND poids_moyen_initial > 100")
    except Exception:
        # best-effort: ignore if column not present or other issues
        pass

    # Update animal_info.poids_moyen (weekly weights)
    try:
        op.execute("UPDATE animal_info SET poids_moyen = poids_moyen / 1000.0 WHERE poids_moyen IS NOT NULL AND poids_moyen > 100")
    except Exception:
        pass

    # If there are other weight-like columns, add them here similarly


def downgrade():
    # Reverse: multiply by 1000 where appropriate (only if values look like kg)
    try:
        op.execute("UPDATE animal_info SET poids_moyen = poids_moyen * 1000.0 WHERE poids_moyen IS NOT NULL AND poids_moyen < 10")
    except Exception:
        pass
    try:
        op.execute("UPDATE bandes SET poids_moyen_initial = poids_moyen_initial * 1000.0 WHERE poids_moyen_initial IS NOT NULL AND poids_moyen_initial < 10")
    except Exception:
        pass
