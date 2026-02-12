from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal

from app.repositories.pagamento_repo import PagamentoRepository
from app.repositories.faturamento_repo import FaturamentoRepository
from app.schemas.pagamento import PagamentoCreate, PagamentoUpdate
from app.models.pagamento import Pagamento

class PagamentoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PagamentoRepository(db)
        self.faturamento_repo = FaturamentoRepository(db)

    # ------------------------------------------------------------------
    # CRIAR PAGAMENTO
    # ------------------------------------------------------------------
    def create_pagamento(self, pagamento_data: PagamentoCreate) -> Pagamento:
        # 1. Verificar se o faturamento existe
        faturamento = self.faturamento_repo.get(pagamento_data.faturamento_id)
        if not faturamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faturamento não encontrado."
            )

        # 2. Regra: não permitir pagamento para NF cancelada
        if faturamento.status == 'CANCELADO':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível registrar pagamento para uma NF cancelada."
            )

        # 3. Calcular total já pago para esta NF
        pagamentos_anteriores = self.repo.get_by_faturamento(pagamento_data.faturamento_id)
        total_pago_anterior = sum(p.valor_pago for p in pagamentos_anteriores)

        # 4. Verificar se o valor do novo pagamento não ultrapassa o valor líquido da NF
        if total_pago_anterior + pagamento_data.valor_pago > faturamento.valor_liquido_nf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor total dos pagamentos ultrapassa o valor líquido da NF."
            )

        # 5. Criar pagamento
        pagamento_dict = pagamento_data.model_dump()
        pagamento = self.repo.create(**pagamento_dict)

        # 6. Commit e refresh (o listener de atualização de status será acionado)
        self.db.commit()
        self.db.refresh(pagamento)
        return pagamento

    # ------------------------------------------------------------------
    # BUSCAR PAGAMENTO POR ID
    # ------------------------------------------------------------------
    def get_pagamento(self, pagamento_id: int) -> Pagamento:
        pagamento = self.repo.get(pagamento_id)
        if not pagamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagamento não encontrado."
            )
        return pagamento

    # ------------------------------------------------------------------
    # LISTAR PAGAMENTOS (COM FILTRO OPCIONAL POR FATURAMENTO)
    # ------------------------------------------------------------------
    def list_pagamentos(
        self,
        faturamento_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Pagamento]:
        query = self.db.query(Pagamento)
        if faturamento_id:
            query = query.filter(Pagamento.faturamento_id == faturamento_id)
        return query.offset(skip).limit(limit).all()

    # ------------------------------------------------------------------
    # ATUALIZAR PAGAMENTO
    # ------------------------------------------------------------------
    def update_pagamento(self, pagamento_id: int, pagamento_data: PagamentoUpdate) -> Pagamento:
        pagamento = self.get_pagamento(pagamento_id)

        # ⚠️ Regra: não permitir alteração de valor se já estiver quitado?
        #    A lógica de atualização de status será tratada pelo listener,
        #    mas podemos bloquear alterações se desejado.
        #    Por simplicidade, permitimos atualização, mas recalculamos o total.

        update_dict = pagamento_data.model_dump(exclude_unset=True)

        # Se alterar valor_pago, precisamos revalidar o limite da NF
        if 'valor_pago' in update_dict:
            faturamento = self.faturamento_repo.get(pagamento.faturamento_id)
            if not faturamento:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Faturamento vinculado não encontrado."
                )

            # Soma dos outros pagamentos (excluindo o atual)
            outros_pagamentos = self.repo.get_by_faturamento(pagamento.faturamento_id)
            total_outros = sum(p.valor_pago for p in outros_pagamentos if p.id != pagamento.id)

            if total_outros + update_dict['valor_pago'] > faturamento.valor_liquido_nf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Valor total dos pagamentos ultrapassaria o valor líquido da NF."
                )

        pagamento_atualizado = self.repo.update(pagamento, update_dict)
        self.db.commit()
        self.db.refresh(pagamento_atualizado)
        return pagamento_atualizado

    # ------------------------------------------------------------------
    # DELETAR PAGAMENTO
    # ------------------------------------------------------------------
    def delete_pagamento(self, pagamento_id: int) -> None:
        pagamento = self.get_pagamento(pagamento_id)
        self.repo.delete(pagamento.id)
        self.db.commit()
        # O listener after_delete será acionado e atualizará o status da NF