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

    def create_boletim(self, contrato_id: int, boletim_data: BoletimCreate) -> BoletimMedicao:
        # Verificar contrato
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")

        # O listener gera o número sequencial
        boletim_dict = boletim_data.model_dump()
        boletim = self.repo.create(**boletim_dict)
        self.db.commit()
        self.db.refresh(boletim)
        return boletim

    def get_boletim(self, boletim_id: int) -> BoletimMedicao:
        boletim = self.repo.get(boletim_id)
        if not boletim:
            raise HTTPException(status_code=404, detail="Boletim não encontrado")
        return boletim

    def list_boletins_por_contrato(self, contrato_id: int, skip: int = 0, limit: int = 100) -> list[BoletimMedicao]:
        # Opcional: verificar se contrato existe
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
        return self.repo.get_by_contrato(contrato_id, skip, limit)

    def update_boletim(self, boletim_id: int, boletim_data: BoletimUpdate) -> BoletimMedicao:
        boletim = self.get_boletim(boletim_id)

        # Não permitir alterar se status for FATURADO (listener também bloqueia, mas reforçamos)
        if boletim.status == 'FATURADO':
            raise HTTPException(status_code=400, detail="Boletim FATURADO não pode ser alterado")

        update_dict = boletim_data.model_dump(exclude_unset=True)

        # Se for cancelar, exige motivo
        if 'status' in update_dict and update_dict['status'] == 'CANCELADO':
            if not update_dict.get('cancelado_motivo'):
                raise HTTPException(status_code=400, detail="Motivo do cancelamento obrigatório")

        boletim_atualizado = self.repo.update(boletim, update_dict)
        self.db.commit()
        self.db.refresh(boletim_atualizado)
        return boletim_atualizado

    def delete_boletim(self, boletim_id: int) -> None:
        boletim = self.get_boletim(boletim_id)
        if boletim.status == 'FATURADO':
            raise HTTPException(status_code=400, detail="Boletim FATURADO não pode ser excluído")
        self.repo.delete(boletim.id)
        self.db.commit()

    def aprovar_boletim(self, boletim_id: int) -> BoletimMedicao:
        boletim = self.get_boletim(boletim_id)
        if boletim.status != 'RASCUNHO':
            raise HTTPException(status_code=400, detail=f"Não é possível aprovar boletim com status {boletim.status}")
        update_dict = {'status': 'APROVADO'}
        boletim_atualizado = self.repo.update(boletim, update_dict)
        self.db.commit()
        self.db.refresh(boletim_atualizado)
        return boletim_atualizado

    def cancelar_boletim(self, boletim_id: int, motivo: str) -> BoletimMedicao:
        boletim = self.get_boletim(boletim_id)
        if boletim.status == 'FATURADO':
            raise HTTPException(status_code=400, detail="Boletim FATURADO não pode ser cancelado")
        update_dict = {'status': 'CANCELADO', 'cancelado_motivo': motivo}
        boletim_atualizado = self.repo.update(boletim, update_dict)
        self.db.commit()
        self.db.refresh(boletim_atualizado)
        return boletim_atualizado
    
    def get_all_boletins(self, skip: int = 0, limit: int = 100) -> list[BoletimMedicao]:
        return self.repo.get_multi(skip, limit)