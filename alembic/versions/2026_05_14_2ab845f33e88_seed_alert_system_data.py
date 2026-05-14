"""seed_alert_system_data

Revision ID: 2ab845f33e88
Revises: 9359c7d7fb55
Create Date: 2026-05-13 14:29:38.618687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision: str = '2ab845f33e88'
down_revision: Union[str, None] = '9359c7d7fb55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Definición de tablas para inserción
    levels = sa.table('levels',
        sa.column('level_id', sa.Integer),
        sa.column('color', sa.String)
    )
    units = sa.table('units',
        sa.column('unit_id', sa.Integer),
        sa.column('name', sa.String)
    )
    metrics = sa.table('metrics',
        sa.column('metric_id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('unit_id', sa.Integer)
    )
    thresholds = sa.table('thresholds',
        sa.column('threshold_id', sa.Integer),
        sa.column('lower_limit', sa.Float),
        sa.column('upper_limit', sa.Float),
        sa.column('message', sa.Text),
        sa.column('level_id', sa.Integer)
    )
    alerts = sa.table('alerts',
        sa.column('alert_id', sa.Integer),
        sa.column('metric_id', sa.Integer),
        sa.column('threshold_id', sa.Integer)
    )

    # Seed: Niveles
    op.bulk_insert(levels, [
        {'level_id': 1, 'color': 'VERDE'},
        {'level_id': 2, 'color': 'AMARILLO'},
        {'level_id': 3, 'color': 'NARANJA'},
        {'level_id': 4, 'color': 'ROJO'},
    ])

    # Seed: Unidades de Medida
    op.bulk_insert(units, [
        {'unit_id': 1, 'name': '°C'},
        {'unit_id': 2, 'name': 'mm'},
        {'unit_id': 3, 'name': 'km/h'},
        {'unit_id': 4, 'name': '%'},
    ])

    # Seed: Métricas
    op.bulk_insert(metrics, [
        {'metric_id': 1, 'name': 'Temperatura', 'unit_id': 1},
        {'metric_id': 2, 'name': 'Lluvia', 'unit_id': 2},
        {'metric_id': 3, 'name': 'Viento', 'unit_id': 3},
        {'metric_id': 4, 'name': 'Humedad', 'unit_id': 4},
    ])

    # Seed: Umbrales
    op.bulk_insert(thresholds, [
        # Temperatura calor
        # Naranja: > 35 y < 40
        {'threshold_id': 1, 'lower_limit': 35.01, 'upper_limit': 39.99, 'message': 'NARANJA_CALOR', 'level_id': 3},
        # Roja: >= 40
        {'threshold_id': 2, 'lower_limit': 40.0, 'upper_limit': None, 'message': 'ROJA_CALOR', 'level_id': 4},

        # Temperatura frío
        # Naranja: > -5 y < 0
        {'threshold_id': 4, 'lower_limit': -4.99, 'upper_limit': -0.01, 'message': 'NARANJA_FRIO', 'level_id': 3},
        # Roja: <= -5
        {'threshold_id': 3, 'lower_limit': None, 'upper_limit': -5.0, 'message': 'ROJA_FRIO', 'level_id': 4},
        
        # Viento
        # Naranja: > 40 y < 70
        {'threshold_id': 5, 'lower_limit': 40.01, 'upper_limit': 70.0, 'message': 'NARANJA_VIENTO', 'level_id': 3},
        # Roja: > 70
        {'threshold_id': 6, 'lower_limit': 70.01, 'upper_limit': None, 'message': 'ROJA_VIENTO', 'level_id': 4},

        # Lluvia 
        # Naranja: > 10 y < 30
        {'threshold_id': 7, 'lower_limit': 10.01, 'upper_limit': 30.0, 'message': 'NARANJA_LLUVIA', 'level_id': 3},
        # Roja: > 30
        {'threshold_id': 8, 'lower_limit': 30.01, 'upper_limit': None, 'message': 'ROJA_LLUVIA', 'level_id': 4},

        # Humedad
        # Naranja: > 90
        {'threshold_id': 9, 'lower_limit': 90.0, 'upper_limit': None, 'message': 'NARANJA_HUMEDAD', 'level_id': 3},
    ])

    # Seed: Alertas
    op.bulk_insert(alerts, [
        {'alert_id': 1, 'metric_id': 1, 'threshold_id': 1}, # Temperatura -> Naranja Calor
        {'alert_id': 2, 'metric_id': 1, 'threshold_id': 2}, # Temperatura -> Roja Calor
        {'alert_id': 3, 'metric_id': 1, 'threshold_id': 3}, # Temperatura -> Naranja Frío
        {'alert_id': 4, 'metric_id': 1, 'threshold_id': 4}, # Temperatura -> Roja Frío
        {'alert_id': 5, 'metric_id': 3, 'threshold_id': 5}, # Viento -> Naranja
        {'alert_id': 6, 'metric_id': 3, 'threshold_id': 6}, # Viento -> Roja
    ])

   # Sincronización del contador de secuencias para evitar errores en inserciones manuales
    op.execute("SELECT setval('levels_level_id_seq', (SELECT MAX(level_id) FROM levels))")
    op.execute("SELECT setval('units_unit_id_seq', (SELECT MAX(unit_id) FROM units))")
    op.execute("SELECT setval('metrics_metric_id_seq', (SELECT MAX(metric_id) FROM metrics))")
    op.execute("SELECT setval('thresholds_threshold_id_seq', (SELECT MAX(threshold_id) FROM thresholds))")
    op.execute("SELECT setval('alerts_alert_id_seq', (SELECT MAX(alert_id) FROM alerts))")

def downgrade() -> None:
    # Eliminar en cascada
    op.execute("DELETE FROM sent_alerts")
    op.execute("DELETE FROM records_alerts")
    op.execute("DELETE FROM alerts")
    op.execute("DELETE FROM metrics")
    op.execute("DELETE FROM thresholds")
    op.execute("DELETE FROM units")
    op.execute("DELETE FROM levels")