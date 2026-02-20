from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func,update
from datetime import timedelta
from app.models.contrato import Contrato
from app.repositories.aditivo_repo import AditivoRepository
from app.repositories.contrato_repo import ContratoRepository
from app.schemas.aditivo import AditivoCreate, AditivoUpdate
from app.models.aditivo import Aditivo

class AditivoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AditivoRepository(db)
        self.contrato_repo = ContratoRepository(db)
        # ------------------------------------------------------------------
    # CRIAR ADITIVO
    # ------------------------------------------------------------------
    def create_aditivo(self, aditivo_data: AditivoCreate) -> Aditivo:
        # 1. Verificar contrato
        contrato = self.contrato_repo.get(aditivo_data.contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")

        # 2. Verificar emenda duplicada
        if aditivo_data.numero_emenda:
            existing = self.repo.get_by_emenda(aditivo_data.contrato_id, aditivo_data.numero_emenda)
            if existing:
                raise HTTPException(status_code=400, detail="Emenda já cadastrada")
        # 3. Criar aditivo
        aditivo_dict = aditivo_data.model_dump()
        aditivo = self.repo.create(**aditivo_dict)
        self.db.flush()   # envia o INSERT, mas não commita

        # 4. Atualizar o contrato
        self._atualizar_contrato(aditivo_data.contrato_id)  # <--- ESSENCIAL

        # 5. Commit final
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
    
    # ------------------------------------------------------------------
    # FUNÇÃO INTERNA PARA ATUALIZAR CONTRATO
    # ------------------------------------------------------------------
    def _atualizar_contrato(self, contrato_id: int):
        # Busca o contrato para obter os valores originais
        contrato = self.db.query(Contrato).filter(Contrato.id == contrato_id).first()
        if not contrato:
            return

        # Calcula somas dos aditivos
        soma_dias = self.db.query(func.coalesce(func.sum(Aditivo.dias_acrescimo), 0)).filter(Aditivo.contrato_id == contrato_id).scalar()
        soma_valores = self.db.query(func.coalesce(func.sum(Aditivo.valor_acrescimo), 0)).filter(Aditivo.contrato_id == contrato_id).scalar()

        # Calcula novos valores
        novo_valor_total = contrato.valor_original + soma_valores
        dias_totais = contrato.prazo_original_dias + soma_dias
        nova_data_fim = contrato.data_inicio + timedelta(days=dias_totais)

        # Executa a atualização direta
        self.db.execute(
            update(Contrato)
            .where(Contrato.id == contrato_id)
            .values(
                valor_total=novo_valor_total,
                data_fim_prevista=nova_data_fim
            )
        )