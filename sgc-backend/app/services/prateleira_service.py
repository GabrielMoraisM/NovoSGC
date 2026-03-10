from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.prateleira import PrateleiraExecucao, BoletimPrateleiraExecucao
from app.models.usuario import Usuario
from app.repositories.prateleira_repository import PrateleiraRepository, BoletimPrateleiraRepository
from app.repositories.contrato_repo import ContratoRepository
from app.repositories.boletim_medicao_repo import BoletimMedicaoRepository
from app.schemas.prateleira import PrateleiraCreate, PrateleiraUpdate, VinculoPrateleiraCreate


class PrateleiraService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PrateleiraRepository(db)
        self.boletim_prateleira_repo = BoletimPrateleiraRepository(db)
        self.contrato_repo = ContratoRepository(db)
        self.boletim_repo = BoletimMedicaoRepository(db)

    # ──────────────────────────────────────────────────────────
    # CREATE
    # ──────────────────────────────────────────────────────────

    def create_execucao(
        self,
        contrato_id: int,
        data: PrateleiraCreate,
        current_user: Optional[Usuario] = None
    ) -> PrateleiraExecucao:
        """Registra uma nova execução na prateleira com status PENDENTE."""
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")

        execucao_dict = data.model_dump()
        execucao_dict["contrato_id"] = contrato_id
        execucao_dict["status"] = "PENDENTE"
        execucao_dict["valor_medido_acumulado"] = Decimal("0")

        # Usa o usuário atual se não informado explicitamente
        if current_user and not execucao_dict.get("usuario_responsavel_id"):
            execucao_dict["usuario_responsavel_id"] = current_user.id

        execucao = self.repo.create(**execucao_dict)
        self.db.commit()
        self.db.refresh(execucao)
        return execucao

    # ──────────────────────────────────────────────────────────
    # READ
    # ──────────────────────────────────────────────────────────

    def get_execucao(self, execucao_id: int) -> PrateleiraExecucao:
        execucao = self.repo.get(execucao_id)
        if not execucao:
            raise HTTPException(status_code=404, detail="Execução não encontrada na prateleira")
        return execucao

    def list_por_contrato(
        self,
        contrato_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrateleiraExecucao]:
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
        return self.repo.get_by_contrato(contrato_id, status, skip, limit)

    def list_global(
        self,
        contrato_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrateleiraExecucao]:
        return self.repo.get_all_with_filters(contrato_id, status, skip, limit)

    def get_pendentes_para_medicao(self, contrato_id: int) -> List[PrateleiraExecucao]:
        """Retorna itens disponíveis para seleção no modal de criação de BM."""
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
        return self.repo.get_pendentes_para_medicao(contrato_id)

    # ──────────────────────────────────────────────────────────
    # UPDATE
    # ──────────────────────────────────────────────────────────

    def update_execucao(self, execucao_id: int, data: PrateleiraUpdate) -> PrateleiraExecucao:
        execucao = self.get_execucao(execucao_id)

        if execucao.status in ("INCLUIDO_EM_MEDICAO", "CANCELADO"):
            raise HTTPException(
                status_code=400,
                detail=f"Execução com status {execucao.status} não pode ser editada"
            )

        update_dict = data.model_dump(exclude_unset=True)
        execucao_atualizada = self.repo.update(execucao, update_dict)
        self.db.commit()
        self.db.refresh(execucao_atualizada)
        return execucao_atualizada

    def marcar_aguardando_medicao(self, execucao_id: int) -> PrateleiraExecucao:
        """Marca execução como pronta para medição."""
        execucao = self.get_execucao(execucao_id)

        if execucao.status != "PENDENTE":
            raise HTTPException(
                status_code=400,
                detail=f"Apenas execuções PENDENTE podem ser marcadas como AGUARDANDO_MEDICAO. Status atual: {execucao.status}"
            )

        execucao_atualizada = self.repo.update(execucao, {"status": "AGUARDANDO_MEDICAO"})
        self.db.commit()
        self.db.refresh(execucao_atualizada)
        return execucao_atualizada

    def cancelar_execucao(self, execucao_id: int, motivo: str) -> PrateleiraExecucao:
        execucao = self.get_execucao(execucao_id)

        if execucao.status == "INCLUIDO_EM_MEDICAO":
            raise HTTPException(
                status_code=400,
                detail="Execução já incluída em medição não pode ser cancelada"
            )
        if execucao.status == "CANCELADO":
            raise HTTPException(status_code=400, detail="Execução já está cancelada")

        if not motivo or not motivo.strip():
            raise HTTPException(status_code=400, detail="Motivo do cancelamento é obrigatório")

        execucao_atualizada = self.repo.update(execucao, {
            "status": "CANCELADO",
            "cancelado_motivo": motivo.strip()
        })
        self.db.commit()
        self.db.refresh(execucao_atualizada)
        return execucao_atualizada

    # ──────────────────────────────────────────────────────────
    # VÍNCULO COM BOLETIM DE MEDIÇÃO
    # ──────────────────────────────────────────────────────────

    def vincular_ao_boletim(
        self,
        boletim_id: int,
        vinculos: List[VinculoPrateleiraCreate]
    ) -> List[BoletimPrateleiraExecucao]:
        """
        Vincula itens da prateleira a um Boletim de Medição.
        Suporta medição parcial: atualiza valor_medido_acumulado e muda status se totalmente consumido.
        """
        boletim = self.boletim_repo.get(boletim_id)
        if not boletim:
            raise HTTPException(status_code=404, detail="Boletim de Medição não encontrado")

        if boletim.status == "CANCELADO":
            raise HTTPException(
                status_code=400,
                detail="Não é possível vincular itens a um boletim cancelado"
            )

        criados = []
        for vinculo_data in vinculos:
            execucao = self.repo.get(vinculo_data.prateleira_id)
            if not execucao:
                raise HTTPException(
                    status_code=404,
                    detail=f"Execução de prateleira {vinculo_data.prateleira_id} não encontrada"
                )

            # Verifica se pertencem ao mesmo contrato
            if execucao.contrato_id != boletim.contrato_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Execução {vinculo_data.prateleira_id} pertence a outro contrato"
                )

            if execucao.status in ("CANCELADO", "INCLUIDO_EM_MEDICAO"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Execução {vinculo_data.prateleira_id} não está disponível para medição (status: {execucao.status})"
                )

            # Verificar se já está vinculada a este boletim
            vinculo_existente = self.boletim_prateleira_repo.get_vinculo(boletim_id, vinculo_data.prateleira_id)
            if vinculo_existente:
                raise HTTPException(
                    status_code=400,
                    detail=f"Execução {vinculo_data.prateleira_id} já está vinculada a este boletim"
                )

            # Calcular saldo disponível
            saldo = (execucao.valor_estimado or Decimal(0)) - (execucao.valor_medido_acumulado or Decimal(0))
            if vinculo_data.valor_incluido > saldo:
                raise HTTPException(
                    status_code=400,
                    detail=f"Valor incluído (R$ {vinculo_data.valor_incluido}) excede o saldo disponível (R$ {saldo}) da execução {vinculo_data.prateleira_id}"
                )

            # Criar vínculo
            vinculo = self.boletim_prateleira_repo.create(
                boletim_id=boletim_id,
                prateleira_id=vinculo_data.prateleira_id,
                valor_incluido=vinculo_data.valor_incluido
            )
            self.db.flush()

            # Atualizar valor_medido_acumulado
            novo_acumulado = (execucao.valor_medido_acumulado or Decimal(0)) + vinculo_data.valor_incluido
            novo_status = execucao.status

            # Se o acumulado atingir o valor estimado, marcar como totalmente incluído
            if novo_acumulado >= execucao.valor_estimado:
                novo_status = "INCLUIDO_EM_MEDICAO"

            self.repo.update(execucao, {
                "valor_medido_acumulado": novo_acumulado,
                "status": novo_status
            })
            self.db.flush()

            criados.append(vinculo)

        self.db.commit()
        for v in criados:
            self.db.refresh(v)

        return criados

    # ──────────────────────────────────────────────────────────
    # MÉTRICAS / RESUMO
    # ──────────────────────────────────────────────────────────

    def get_resumo_global(self) -> dict:
        return self.repo.get_resumo_global()

    def get_vinculos_por_boletim(self, boletim_id: int) -> List[BoletimPrateleiraExecucao]:
        return self.boletim_prateleira_repo.get_vinculos_por_boletim(boletim_id)
