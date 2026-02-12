from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.boletim_medicao_repo import BoletimMedicaoRepository
from app.repositories.contrato_repo import ContratoRepository
from app.schemas.boletim import BoletimCreate, BoletimUpdate
from app.models.boletim_medicao import BoletimMedicao

class BoletimService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = BoletimMedicaoRepository(db)
        self.contrato_repo = ContratoRepository(db)

    # ------------------------------------------------------------------
    # CRIAR BOLETIM
    # ------------------------------------------------------------------
    def create_boletim(self, boletim_data: BoletimCreate) -> BoletimMedicao:
        # 1. Verificar se o contrato existe
        contrato = self.contrato_repo.get(boletim_data.contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )

        # 2. (Opcional) Validar se o período não conflita com outros BMs
        #    Ex: períodos sobrepostos? Depende da regra de negócio.
        #    Vamos pular por simplicidade, mas pode ser implementado.

        # 3. O número sequencial é gerado pelo listener (events.py)
        boletim_dict = boletim_data.model_dump()
        boletim = self.repo.create(**boletim_dict)

        # 4. Commit e refresh
        self.db.commit()
        self.db.refresh(boletim)
        return boletim

    # ------------------------------------------------------------------
    # BUSCAR BOLETIM POR ID
    # ------------------------------------------------------------------
    def get_boletim(self, boletim_id: int) -> BoletimMedicao:
        boletim = self.repo.get(boletim_id)
        if not boletim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Boletim de Medição não encontrado."
            )
        return boletim

    # ------------------------------------------------------------------
    # LISTAR BOLETINS DE UM CONTRATO
    # ------------------------------------------------------------------
    def list_boletins_por_contrato(self, contrato_id: int, skip: int = 0, limit: int = 100) -> list[BoletimMedicao]:
        # Verificar se contrato existe
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )
        return self.db.query(BoletimMedicao).filter(
            BoletimMedicao.contrato_id == contrato_id
        ).order_by(BoletimMedicao.numero_sequencial.asc()).offset(skip).limit(limit).all()

    # ------------------------------------------------------------------
    # ATUALIZAR BOLETIM
    # ------------------------------------------------------------------
    def update_boletim(self, boletim_id: int, boletim_data: BoletimUpdate) -> BoletimMedicao:
        boletim = self.get_boletim(boletim_id)

        # 🔥 REGRA CRÍTICA: Não permitir alteração se status for FATURADO
        if boletim.status == "FATURADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Boletim FATURADO não pode ser alterado. Cancele e emita um novo."
            )

        update_dict = boletim_data.model_dump(exclude_unset=True)

        # Se estiver cancelando, exige motivo
        if "status" in update_dict and update_dict["status"] == "CANCELADO":
            if not boletim_data.cancelado_motivo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Motivo do cancelamento é obrigatório."
                )

        boletim_atualizado = self.repo.update(boletim, update_dict)
        self.db.commit()
        self.db.refresh(boletim_atualizado)
        return boletim_atualizado

    # ------------------------------------------------------------------
    # DELETAR BOLETIM (APENAS SE NÃO FATURADO)
    # ------------------------------------------------------------------
    def delete_boletim(self, boletim_id: int) -> None:
        boletim = self.get_boletim(boletim_id)

        if boletim.status == "FATURADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Boletim FATURADO não pode ser excluído."
            )

        # Verificar se há faturas vinculadas? (Listener impede, mas vamos validar)
        if boletim.faturas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Boletim com faturas vinculadas não pode ser excluído. Cancele-o."
            )

        self.repo.delete(boletim.id)
        self.db.commit()