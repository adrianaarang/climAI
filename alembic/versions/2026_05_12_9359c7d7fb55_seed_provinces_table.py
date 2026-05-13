"""seed_provinces_table

Revision ID: 9359c7d7fb55
Revises: 827540644ebb
Create Date: 2026-05-12 22:01:17.698651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision: str = '9359c7d7fb55'
down_revision: Union[str, None] = '827540644ebb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Definimos la lista aquí dentro
NOMBRES_PROVINCIAS = [
    "Álava", "Albacete", "Alicante", "Almería", "Asturias", "Ávila", "Badajoz", "Barcelona",
    "Burgos", "Cáceres", "Cádiz", "Cantabria", "Castellón", "Ciudad Real", "Córdoba", "Cuenca",
    "Gerona", "Granada", "Guadalajara", "Guipúzcoa", "Huelva", "Huesca", "Islas Baleares",
    "Jaén", "La Coruña", "La Rioja", "Las Palmas", "León", "Lérida", "Lugo", "Madrid", "Málaga",
    "Murcia", "Navarra", "Orense", "Palencia", "Pontevedra", "Salamanca", "Santa Cruz de Tenerife",
    "Segovia", "Sevilla", "Soria", "Tarragona", "Teruel", "Toledo", "Valencia", "Valladolid",
    "Vizcaya", "Zamora", "Zaragoza"
]

def upgrade() -> None:
    # Creamos una estructura temporal para la inserción
    provinces_table = sa.table(
        'provinces',
        sa.column('name', sa.String),
    )

    # Insertamos los datos
    op.bulk_insert(
        provinces_table,
        [{'name': nombre} for nombre in NOMBRES_PROVINCIAS]
    )

def downgrade() -> None:
    # Por si queremos deshacerlo, borramos todo lo de la tabla
    op.execute("DELETE FROM provinces")