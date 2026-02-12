"""initial migration

Revision ID: 3df48c410e45
Revises: 
Create Date: 2026-02-12 10:03:05.325743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3df48c410e45'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ... comandos gerados automaticamente (create table, etc) ...

    # ===== TRIGGER PARA VALIDAR SOMA DE PERCENTUAIS EM CONSÓRCIO =====
    op.execute("""
    CREATE OR REPLACE FUNCTION check_consorcio_percentual()
    RETURNS TRIGGER AS $$
    DECLARE
        total DECIMAL(5,2);
        contrato_id_val INTEGER;
    BEGIN
        IF TG_OP = 'DELETE' THEN
            contrato_id_val = OLD.contrato_id;
        ELSE
            contrato_id_val = NEW.contrato_id;
        END IF;

        SELECT SUM(percentual_participacao) INTO total
        FROM contrato_participantes
        WHERE contrato_id = contrato_id_val;

        -- Se não houver participantes (total IS NULL), o contrato não é consórcio, ok.
        -- Se houver, deve ser exatamente 100%
        IF total IS NOT NULL AND total != 0 AND total != 100.00 THEN
               RAISE EXCEPTION 'A soma dos percentuais do consórcio deve ser 100%% (atual: %s%%)', total;
        END IF;
        RETURN COALESCE(NEW, OLD);
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER trigger_check_consorcio_percentual
    AFTER INSERT OR UPDATE OR DELETE ON contrato_participantes
    FOR EACH ROW EXECUTE FUNCTION check_consorcio_percentual();
    """)
        # ===== RLS (ROW LEVEL SECURITY) =====
    
    # Habilitar RLS nas tabelas protegidas
    for tabela in ['contratos', 'boletins_medicao', 'faturamentos', 'aditivos', 'pagamentos']:
        op.execute(f'ALTER TABLE {tabela} ENABLE ROW LEVEL SECURITY;')

    # Política para contratos
    op.execute("""
    CREATE POLICY contratos_rls ON contratos
        USING (id IN (
            SELECT contrato_id FROM usuario_contratos 
            WHERE usuario_id = current_setting('app.current_user_id')::int
        ));
    """)

    # Política para boletins_medicao
    op.execute("""
    CREATE POLICY boletins_rls ON boletins_medicao
        USING (contrato_id IN (
            SELECT contrato_id FROM usuario_contratos 
            WHERE usuario_id = current_setting('app.current_user_id')::int
        ));
    """)

    # Política para faturamentos
    op.execute("""
    CREATE POLICY faturamentos_rls ON faturamentos
        USING (bm_id IN (
            SELECT id FROM boletins_medicao WHERE contrato_id IN (
                SELECT contrato_id FROM usuario_contratos 
                WHERE usuario_id = current_setting('app.current_user_id')::int
            )
        ));
    """)

    # Política para aditivos
    op.execute("""
    CREATE POLICY aditivos_rls ON aditivos
        USING (contrato_id IN (
            SELECT contrato_id FROM usuario_contratos 
            WHERE usuario_id = current_setting('app.current_user_id')::int
        ));
    """)

    # Política para pagamentos
    op.execute("""
    CREATE POLICY pagamentos_rls ON pagamentos
        USING (faturamento_id IN (
            SELECT id FROM faturamentos WHERE bm_id IN (
                SELECT id FROM boletins_medicao WHERE contrato_id IN (
                    SELECT contrato_id FROM usuario_contratos 
                    WHERE usuario_id = current_setting('app.current_user_id')::int
                )
            )
        ));
    """)

def downgrade() -> None:
    # ===== REMOVER TRIGGER =====
    op.execute("DROP TRIGGER IF EXISTS trigger_check_consorcio_percentual ON contrato_participantes")
    op.execute("DROP FUNCTION IF EXISTS check_consorcio_percentual()")
    # ... comandos de drop das tabelas ...
        # ===== REMOVER RLS =====
    op.execute("DROP POLICY IF EXISTS contratos_rls ON contratos")
    op.execute("DROP POLICY IF EXISTS boletins_rls ON boletins_medicao")
    op.execute("DROP POLICY IF EXISTS faturamentos_rls ON faturamentos")
    op.execute("DROP POLICY IF EXISTS aditivos_rls ON aditivos")
    op.execute("DROP POLICY IF EXISTS pagamentos_rls ON pagamentos")
