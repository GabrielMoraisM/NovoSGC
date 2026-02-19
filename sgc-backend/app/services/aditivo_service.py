from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func
from datetime import timedelta

from app.repositories.aditivo_repo import AditivoRepository
from app.repositories.contrato_repo import ContratoRepository
from app.schemas.aditivo import AditivoCreate, AditivoUpdate
from app.models.aditivo import Aditivo

class AditivoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AditivoRepository(db)
        self.contrato_repo = ContratoRepository(db)


    def _atualizar_contrato(self, contrato_id: int):
        """Recalcula data_fim_prevista e valor_total do contrato baseado nos aditivos."""
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            return

        # Soma dos dias e valores de todos os aditivos do contrato
        soma_dias = self.db.query(func.coalesce(func.sum(Aditivo.dias_acrescimo), 0)).filter(Aditivo.contrato_id == contrato_id).scalar()
        soma_valores = self.db.query(func.coalesce(func.sum(Aditivo.valor_acrescimo), 0)).filter(Aditivo.contrato_id == contrato_id).scalar()

        # Atualiza a data fim prevista
        dias_totais = contrato.prazo_original_dias + soma_dias
        contrato.data_fim_prevista = contrato.data_inicio + timedelta(days=dias_totais)

        # Atualiza o valor total
        contrato.valor_total = contrato.valor_original + soma_valores

        self.db.add(contrato)

        
    # ------------------------------------------------------------------
    # CRIAR ADITIVO
    # ------------------------------------------------------------------
    def create_aditivo(self, aditivo_data: AditivoCreate) -> Aditivo:
        # 1. Verificar se o contrato existe
        contrato = self.contrato_repo.get(aditivo_data.contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )

        # 2. (Opcional) Verificar se número de emenda já existe para este contrato
        if aditivo_data.numero_emenda:
            existing = self.repo.get_by_emenda(
                aditivo_data.contrato_id,
                aditivo_data.numero_emenda
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Emenda nº {aditivo_data.numero_emenda} já cadastrada para este contrato."
                )

        # 3. Criar aditivo
        aditivo_dict = aditivo_data.model_dump()
        aditivo = self.repo.create(**aditivo_dict)

        # 4. Commit e refresh
        self.db.commit()
        self.db.refresh(aditivo)
        return aditivo
    


    # ------------------------------------------------------------------
    # BUSCAR ADITIVO POR ID
    # ------------------------------------------------------------------
    def get_aditivo(self, aditivo_id: int) -> Aditivo:
        aditivo = self.repo.get(aditivo_id)
        if not aditivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aditivo não encontrado."
            )
        return aditivo

    # ------------------------------------------------------------------
    # LISTAR ADITIVOS DE UM CONTRATO
    # ------------------------------------------------------------------
    def list_aditivos_por_contrato(self, contrato_id: int, skip: int = 0, limit: int = 100) -> list[Aditivo]:
        # Verificar se contrato existe
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )
        return self.db.query(Aditivo).filter(
            Aditivo.contrato_id == contrato_id
        ).offset(skip).limit(limit).all()

    # ------------------------------------------------------------------
    # ATUALIZAR ADITIVO
    # ------------------------------------------------------------------
    def update_aditivo(self, aditivo_id: int, aditivo_data: AditivoUpdate) -> Aditivo:
        aditivo = self.get_aditivo(aditivo_id)
        update_dict = aditivo_data.model_dump(exclude_unset=True)
        aditivo_atualizado = self.repo.update(aditivo, update_dict)
        self.db.flush()
        self._atualizar_contrato(aditivo.contrato_id)
        self.db.commit()
        self.db.refresh(aditivo_atualizado)
        return aditivo_atualizado

    # ------------------------------------------------------------------
    # DELETAR ADITIVO
    # ------------------------------------------------------------------
    def delete_aditivo(self, aditivo_id: int) -> None:
        aditivo = self.get_aditivo(aditivo_id)
        contrato_id = aditivo.contrato_id
        self.repo.delete(aditivo.id)
        self.db.flush()
        self._atualizar_contrato(contrato_id)
        self.db.commit()