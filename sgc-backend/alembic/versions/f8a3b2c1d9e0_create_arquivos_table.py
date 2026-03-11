"""create arquivos table

Revision ID: f8a3b2c1d9e0
Revises: e21a240aa6ba
Create Date: 2026-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f8a3b2c1d9e0'
down_revision = 'e21a240aa6ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'arquivos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome_original', sa.String(255), nullable=False),
        sa.Column('nome_arquivo', sa.String(255), nullable=False),
        sa.Column('caminho', sa.String(500), nullable=False),
        sa.Column('tamanho', sa.Integer(), nullable=True),
        sa.Column('tipo_mime', sa.String(100), nullable=True),
        sa.Column('entidade_tipo', sa.Enum('contrato', 'boletim', 'faturamento', 'pagamento', name='entidade_tipo_arquivo'), nullable=False),
        sa.Column('entidade_id', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_arquivos_id', 'arquivos', ['id'])
    op.create_index('ix_arquivos_entidade', 'arquivos', ['entidade_tipo', 'entidade_id'])


def downgrade() -> None:
    op.drop_index('ix_arquivos_entidade', table_name='arquivos')
    op.drop_index('ix_arquivos_id', table_name='arquivos')
    op.drop_table('arquivos')
    op.execute("DROP TYPE IF EXISTS entidade_tipo_arquivo")
