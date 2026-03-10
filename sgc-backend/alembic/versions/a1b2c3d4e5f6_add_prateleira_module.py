"""add prateleira module

Revision ID: a1b2c3d4e5f6
Revises: 093478eaa62e
Create Date: 2026-03-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '093478eaa62e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── Criar ENUM status_prateleira ───────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE status_prateleira AS ENUM (
                'PENDENTE',
                'AGUARDANDO_MEDICAO',
                'INCLUIDO_EM_MEDICAO',
                'CANCELADO'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # ─── Criar tabela prateleira_execucoes ───────────────────────
    op.create_table(
        'prateleira_execucoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contrato_id', sa.Integer(), nullable=False),
        sa.Column('descricao_servico', sa.String(length=300), nullable=False),
        sa.Column('data_execucao', sa.Date(), nullable=False),
        sa.Column('percentual_executado', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('valor_estimado', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('valor_medido_acumulado', sa.DECIMAL(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column(
            'status',
            sa.Enum(
                'PENDENTE', 'AGUARDANDO_MEDICAO', 'INCLUIDO_EM_MEDICAO', 'CANCELADO',
                name='status_prateleira',
                create_type=False
            ),
            nullable=False,
            server_default='PENDENTE'
        ),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('cancelado_motivo', sa.Text(), nullable=True),
        sa.Column('usuario_responsavel_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['contrato_id'], ['contratos.id'],
            name='fk_prateleira_contrato',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['usuario_responsavel_id'], ['usuarios.id'],
            name='fk_prateleira_usuario',
            ondelete='RESTRICT'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # Índices para prateleira_execucoes
    op.create_index(
        'idx_prateleira_contrato_status',
        'prateleira_execucoes',
        ['contrato_id', 'status']
    )
    op.create_index(
        'idx_prateleira_data_execucao',
        'prateleira_execucoes',
        ['data_execucao']
    )

    # ─── Criar tabela boletim_prateleira_execucoes ───────────────
    op.create_table(
        'boletim_prateleira_execucoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('boletim_id', sa.Integer(), nullable=False),
        sa.Column('prateleira_id', sa.Integer(), nullable=False),
        sa.Column('valor_incluido', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['boletim_id'], ['boletins_medicao.id'],
            name='fk_bpe_boletim',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['prateleira_id'], ['prateleira_execucoes.id'],
            name='fk_bpe_prateleira',
            ondelete='RESTRICT'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('boletim_id', 'prateleira_id', name='unique_boletim_prateleira')
    )

    # Índices para boletim_prateleira_execucoes
    op.create_index('idx_bpe_prateleira_id', 'boletim_prateleira_execucoes', ['prateleira_id'])
    op.create_index('idx_bpe_boletim_id', 'boletim_prateleira_execucoes', ['boletim_id'])


def downgrade() -> None:
    # Remove tabelas na ordem inversa (filho antes do pai)
    op.drop_index('idx_bpe_boletim_id', table_name='boletim_prateleira_execucoes')
    op.drop_index('idx_bpe_prateleira_id', table_name='boletim_prateleira_execucoes')
    op.drop_table('boletim_prateleira_execucoes')

    op.drop_index('idx_prateleira_data_execucao', table_name='prateleira_execucoes')
    op.drop_index('idx_prateleira_contrato_status', table_name='prateleira_execucoes')
    op.drop_table('prateleira_execucoes')

    op.execute("DROP TYPE IF EXISTS status_prateleira;")
