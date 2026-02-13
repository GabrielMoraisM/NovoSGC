"""add finalizado and data_finalizacao to contrato_arts

Revision ID: 3506a6068208
Revises: c47422e869f7
Create Date: 2026-02-13 15:24:23.812680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3506a6068208'
down_revision: Union[str, None] = 'c47422e869f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('contrato_arts', sa.Column('finalizado', sa.Boolean(), server_default='false'))
    op.add_column('contrato_arts', sa.Column('data_finalizacao', sa.Date()))


def downgrade():
    op.drop_column('contrato_arts', 'data_finalizacao')
    op.drop_column('contrato_arts', 'finalizado')
