"""add finalizado and data_finalizacao to contrato_arts

Revision ID: c47422e869f7
Revises: 3df48c410e45
Create Date: 2026-02-13 15:23:33.204040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c47422e869f7'
down_revision: Union[str, None] = '3df48c410e45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
