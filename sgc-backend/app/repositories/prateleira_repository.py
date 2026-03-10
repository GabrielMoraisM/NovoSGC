from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta

from app.repositories.base import BaseRepository
from app.models.prateleira import PrateleiraExecucao, BoletimPrateleiraExecucao


class PrateleiraRepository(BaseRepository[PrateleiraExecucao]):
    def __init__(self, db: Session):
        super().__init__(db, PrateleiraExecucao)

    def get_by_contrato(
        self,
        contrato_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrateleiraExecucao]:
        """Lista itens da prateleira de um contrato, com filtro opcional de status."""
        query = self.db.query(PrateleiraExecucao).filter(
            PrateleiraExecucao.contrato_id == contrato_id
        )
        if status:
            query = query.filter(PrateleiraExecucao.status == status)
        return query.order_by(PrateleiraExecucao.data_execucao.desc()).offset(skip).limit(limit).all()

    def get_pendentes_para_medicao(self, contrato_id: int) -> List[PrateleiraExecucao]:
        """
        Retorna itens disponíveis para inclusão em um Boletim de Medição.
        Inclui PENDENTE e AGUARDANDO_MEDICAO que ainda têm saldo (valor_estimado > valor_medido_acumulado).
        """
        return self.db.query(PrateleiraExecucao).filter(
            and_(
                PrateleiraExecucao.contrato_id == contrato_id,
                PrateleiraExecucao.status.in_(["PENDENTE", "AGUARDANDO_MEDICAO"]),
                PrateleiraExecucao.valor_estimado > PrateleiraExecucao.valor_medido_acumulado
            )
        ).order_by(PrateleiraExecucao.data_execucao.asc()).all()

    def get_all_with_filters(
        self,
        contrato_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrateleiraExecucao]:
        """Lista global de execuções com filtros opcionais."""
        query = self.db.query(PrateleiraExecucao)
        if contrato_id:
            query = query.filter(PrateleiraExecucao.contrato_id == contrato_id)
        if status:
            query = query.filter(PrateleiraExecucao.status == status)
        return query.order_by(PrateleiraExecucao.data_execucao.desc()).offset(skip).limit(limit).all()

    def get_antigas(self, dias: int = 30) -> List[PrateleiraExecucao]:
        """Retorna execuções PENDENTE ou AGUARDANDO_MEDICAO criadas há mais de X dias."""
        data_limite = date.today() - timedelta(days=dias)
        return self.db.query(PrateleiraExecucao).filter(
            and_(
                PrateleiraExecucao.status.in_(["PENDENTE", "AGUARDANDO_MEDICAO"]),
                PrateleiraExecucao.data_execucao <= data_limite
            )
        ).all()

    def get_resumo_global(self) -> dict:
        """Retorna métricas agregadas da prateleira para o dashboard."""
        from sqlalchemy import func as sqlfunc
        from decimal import Decimal

        # Itens ativos (não cancelados e não totalmente medidos)
        ativos = self.db.query(PrateleiraExecucao).filter(
            PrateleiraExecucao.status.in_(["PENDENTE", "AGUARDANDO_MEDICAO"])
        ).all()

        valor_total = sum(
            (item.valor_estimado or Decimal(0)) - (item.valor_medido_acumulado or Decimal(0))
            for item in ativos
        )
        qtd_pendentes = sum(1 for i in ativos if i.status == "PENDENTE")
        qtd_aguardando = sum(1 for i in ativos if i.status == "AGUARDANDO_MEDICAO")

        data_limite = date.today() - timedelta(days=30)
        qtd_antigas = sum(1 for i in ativos if i.data_execucao and i.data_execucao <= data_limite)

        return {
            "valor_total_em_prateleira": float(valor_total),
            "qtd_execucoes_pendentes": qtd_pendentes,
            "qtd_execucoes_aguardando": qtd_aguardando,
            "qtd_execucoes_antigas_30dias": qtd_antigas,
        }


class BoletimPrateleiraRepository(BaseRepository[BoletimPrateleiraExecucao]):
    def __init__(self, db: Session):
        super().__init__(db, BoletimPrateleiraExecucao)

    def get_vinculos_por_boletim(self, boletim_id: int) -> List[BoletimPrateleiraExecucao]:
        return self.db.query(BoletimPrateleiraExecucao).filter(
            BoletimPrateleiraExecucao.boletim_id == boletim_id
        ).all()

    def get_vinculos_por_prateleira(self, prateleira_id: int) -> List[BoletimPrateleiraExecucao]:
        return self.db.query(BoletimPrateleiraExecucao).filter(
            BoletimPrateleiraExecucao.prateleira_id == prateleira_id
        ).all()

    def get_vinculo(self, boletim_id: int, prateleira_id: int) -> Optional[BoletimPrateleiraExecucao]:
        return self.db.query(BoletimPrateleiraExecucao).filter(
            and_(
                BoletimPrateleiraExecucao.boletim_id == boletim_id,
                BoletimPrateleiraExecucao.prateleira_id == prateleira_id
            )
        ).first()
