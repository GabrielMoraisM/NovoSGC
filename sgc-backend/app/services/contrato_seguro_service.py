from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.contrato_seguro_repo import ContratoSeguroRepository
from app.repositories.empresa_repo import EmpresaRepository
from app.repositories.contrato_repo import ContratoRepository
from app.schemas.contrato_seguro import ContratoSeguroCreate, ContratoSeguroUpdate
from app.models.contrato_seguro import ContratoSeguro

class ContratoSeguroService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContratoSeguroRepository(db)
        self.empresa_repo = EmpresaRepository(db)
        self.contrato_repo = ContratoRepository(db)

    def create_seguro(self, contrato_id: int, seguro_data: ContratoSeguroCreate) -> ContratoSeguro:
        # Verificar se contrato existe
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")

        # Verificar se seguradora existe e é do tipo SEGURADORA
        seguradora = self.empresa_repo.get(seguro_data.seguradora_id)
        if not seguradora:
            raise HTTPException(status_code=404, detail="Seguradora não encontrada")
        if seguradora.tipo != 'SEGURADORA':
            raise HTTPException(status_code=400, detail="A empresa informada não é uma seguradora")

        # (Opcional) Verificar se número de apólice já existe
        if seguro_data.numero_apolice:
            existente = self.repo.get_by_apolice(seguro_data.numero_apolice)
            if existente:
                raise HTTPException(status_code=400, detail="Número de apólice já cadastrado")

        seguro_dict = seguro_data.model_dump()
        seguro_dict['contrato_id'] = contrato_id
        seguro = self.repo.create(**seguro_dict)
        self.db.commit()
        self.db.refresh(seguro)
        return seguro

    def get_seguros_por_contrato(self, contrato_id: int) -> list[ContratoSeguro]:
        return self.repo.get_by_contrato(contrato_id)

    def get_seguro(self, seguro_id: int) -> ContratoSeguro:
        seguro = self.repo.get(seguro_id)
        if not seguro:
            raise HTTPException(status_code=404, detail="Seguro não encontrado")
        return seguro

    def update_seguro(self, seguro_id: int, seguro_data: ContratoSeguroUpdate) -> ContratoSeguro:
        seguro = self.get_seguro(seguro_id)
        update_dict = seguro_data.model_dump(exclude_unset=True)

        # Se alterar seguradora, validar
        if 'seguradora_id' in update_dict:
            seguradora = self.empresa_repo.get(update_dict['seguradora_id'])
            if not seguradora:
                raise HTTPException(status_code=404, detail="Seguradora não encontrada")
            if seguradora.tipo != 'SEGURADORA':
                raise HTTPException(status_code=400, detail="A empresa informada não é uma seguradora")

        # Se alterar número da apólice, verificar duplicidade
        if 'numero_apolice' in update_dict and update_dict['numero_apolice'] != seguro.numero_apolice:
            existente = self.repo.get_by_apolice(update_dict['numero_apolice'])
            if existente:
                raise HTTPException(status_code=400, detail="Número de apólice já cadastrado")

        seguro_atualizado = self.repo.update(seguro, update_dict)
        self.db.commit()
        self.db.refresh(seguro_atualizado)
        return seguro_atualizado

    def delete_seguro(self, seguro_id: int) -> None:
        seguro = self.get_seguro(seguro_id)
        self.repo.delete(seguro.id)
        self.db.commit()