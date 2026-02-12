from typing import Optional  # <-- ADICIONE ESTA LINHA
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.faturamento_repo import FaturamentoRepository
from app.repositories.boletim_medicao_repo import BoletimMedicaoRepository
from app.repositories.empresa_repo import EmpresaRepository
from app.schemas.faturamento import FaturamentoCreate, FaturamentoUpdate
from app.models.faturamento import Faturamento

class FaturamentoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FaturamentoRepository(db)
        self.boletim_repo = BoletimMedicaoRepository(db)
        self.empresa_repo = EmpresaRepository(db)

    # ------------------------------------------------------------------
    # CRIAR FATURAMENTO
    # ------------------------------------------------------------------
    def create_faturamento(self, faturamento_data: FaturamentoCreate) -> Faturamento:
        # 1. Verificar se o BM existe
        bm = self.boletim_repo.get(faturamento_data.bm_id)
        if not bm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Boletim de Medição não encontrado."
            )

        # 2. Verificar se o BM está APROVADO (regra de negócio)
        if bm.status != 'APROVADO':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas boletins APROVADOS podem ser faturados."
            )

        # 3. Verificar se empresa emissora existe
        emissora = self.empresa_repo.get(faturamento_data.empresa_emissora_id)
        if not emissora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa emissora não encontrada."
            )

        # 4. Verificar se cliente existe
        cliente = self.empresa_repo.get(faturamento_data.cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado."
            )
        if cliente.tipo != 'CLIENTE':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A empresa informada não é um cliente válido."
            )

        # 5. (Opcional) Verificar se já existe NF para este BM
        # 5. Verificar se já existe NF para este BM com a mesma empresa emissora e mesmo cliente
        nf_existente = self.db.query(Faturamento).filter(
            Faturamento.bm_id == faturamento_data.bm_id,
            Faturamento.empresa_emissora_id == faturamento_data.empresa_emissora_id,
            Faturamento.cliente_id == faturamento_data.cliente_id
        ).first()
        if nf_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma NF emitida por esta empresa para este cliente com base neste boletim."
            )

        # 6. Criar faturamento
        #    Os campos de retenção e valor_liquido_nf serão calculados pelo listener
        faturamento_dict = faturamento_data.model_dump()
        faturamento = self.repo.create(**faturamento_dict)

        # 7. Commit e refresh
        self.db.commit()
        self.db.refresh(faturamento)
        return faturamento

    # ------------------------------------------------------------------
    # BUSCAR FATURAMENTO POR ID
    # ------------------------------------------------------------------
    def get_faturamento(self, faturamento_id: int) -> Faturamento:
        faturamento = self.repo.get(faturamento_id)
        if not faturamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faturamento não encontrado."
            )
        return faturamento

    # ------------------------------------------------------------------
    # LISTAR FATURAMENTOS (COM FILTROS OPCIONAIS)
    # ------------------------------------------------------------------
    def list_faturamentos(
        self,
        bm_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Faturamento]:
        query = self.db.query(Faturamento)
        if bm_id:
            query = query.filter(Faturamento.bm_id == bm_id)
        return query.offset(skip).limit(limit).all()

    # ------------------------------------------------------------------
    # ATUALIZAR FATURAMENTO
    # ------------------------------------------------------------------
    def update_faturamento(self, faturamento_id: int, faturamento_data: FaturamentoUpdate) -> Faturamento:
        faturamento = self.get_faturamento(faturamento_id)

        # ⚠️ Regra: não permitir alteração se NF estiver QUITADA ou CANCELADA
        if faturamento.status in ['QUITADO', 'CANCELADO']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível alterar NF com status {faturamento.status}."
            )

        update_dict = faturamento_data.model_dump(exclude_unset=True)

        # Se alterar bm_id, verificar existência e status
        if 'bm_id' in update_dict:
            bm = self.boletim_repo.get(update_dict['bm_id'])
            if not bm:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Boletim de Medição não encontrado."
                )
            if bm.status != 'APROVADO':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Apenas boletins APROVADOS podem ser vinculados."
                )

        # Se alterar valor_bruto_nf, o listener recalculará automaticamente
        faturamento_atualizado = self.repo.update(faturamento, update_dict)
        self.db.commit()
        self.db.refresh(faturamento_atualizado)
        return faturamento_atualizado

    # ------------------------------------------------------------------
    # CANCELAR FATURAMENTO (AÇÃO ESPECÍFICA)
    # ------------------------------------------------------------------
    def cancelar_faturamento(self, faturamento_id: int, motivo: str) -> Faturamento:
        faturamento = self.get_faturamento(faturamento_id)

        if faturamento.status == 'QUITADO':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NF já quitada não pode ser cancelada."
            )

        return self.update_faturamento(
            faturamento_id,
            FaturamentoUpdate(status="CANCELADO")
        )