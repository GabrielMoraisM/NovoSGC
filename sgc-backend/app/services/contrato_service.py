from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal

from app.repositories.contrato_repo import ContratoRepository
from app.repositories.empresa_repo import EmpresaRepository
from app.schemas.contrato import ContratoCreate, ContratoUpdate
from app.models.contrato import Contrato

class ContratoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContratoRepository(db)
        self.empresa_repo = EmpresaRepository(db)

    # ------------------------------------------------------------------
    # CRIAR CONTRATO
    # ------------------------------------------------------------------
    def create_contrato(self, contrato_data: ContratoCreate) -> Contrato:
        # 1. Verificar se número do contrato já existe
        existing = self.repo.get_by_numero(contrato_data.numero_contrato)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contrato nº {contrato_data.numero_contrato} já cadastrado."
            )

        # 2. Verificar se cliente existe
        cliente = self.empresa_repo.get(contrato_data.cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado."
            )

        # 3. (Opcional) Verificar se cliente é do tipo CLIENTE
        if cliente.tipo != "CLIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A empresa informada não é um cliente válido."
            )

        # 4. Converter para dicionário e criar
        contrato_dict = contrato_data.model_dump()
        contrato = self.repo.create(**contrato_dict)

        # 5. Commit e refresh
        self.db.commit()
        self.db.refresh(contrato)
        return contrato

    # ------------------------------------------------------------------
    # BUSCAR CONTRATO POR ID
    # ------------------------------------------------------------------
    def get_contrato(self, contrato_id: int) -> Contrato:
        contrato = self.repo.get(contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )
        return contrato

    # ------------------------------------------------------------------
    # LISTAR CONTRATOS
    # ------------------------------------------------------------------
    def list_contratos(self, skip: int = 0, limit: int = 100) -> list[Contrato]:
        return self.repo.get_multi(skip, limit)

    # ------------------------------------------------------------------
    # ATUALIZAR CONTRATO
    # ------------------------------------------------------------------
    def update_contrato(self, contrato_id: int, contrato_data: ContratoUpdate) -> Contrato:
        contrato = self.get_contrato(contrato_id)
        update_dict = contrato_data.model_dump(exclude_unset=True)

        # Se estiver alterando o número do contrato, verificar duplicidade
        if "numero_contrato" in update_dict:
            novo_numero = update_dict["numero_contrato"]
            if novo_numero != contrato.numero_contrato:
                existing = self.repo.get_by_numero(novo_numero)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Contrato nº {novo_numero} já cadastrado."
                    )

        # Se estiver alterando o cliente, verificar existência
        if "cliente_id" in update_dict:
            cliente = self.empresa_repo.get(update_dict["cliente_id"])
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado."
                )
            if cliente.tipo != "CLIENTE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A empresa informada não é um cliente válido."
                )

        # Atualizar
        contrato_atualizado = self.repo.update(contrato, update_dict)
        self.db.commit()
        self.db.refresh(contrato_atualizado)
        return contrato_atualizado

    # ------------------------------------------------------------------
    # DELETAR CONTRATO
    # ------------------------------------------------------------------
    def delete_contrato(self, contrato_id: int) -> None:
        contrato = self.get_contrato(contrato_id)

        # Verificar se há boletins de medição vinculados (proteger integridade)
        from app.models.boletim_medicao import BoletimMedicao
        boletins = self.db.query(BoletimMedicao).filter(
            BoletimMedicao.contrato_id == contrato_id
        ).first()
        if boletins:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir contrato que possui boletins de medição."
            )

        self.repo.delete(contrato.id)
        self.db.commit()