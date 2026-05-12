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


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass