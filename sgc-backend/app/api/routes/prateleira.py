from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.models.usuario import Usuario
from app.schemas.prateleira import (
    PrateleiraCreate,
    PrateleiraUpdate,
    PrateleiraInDB,
    PrateleiraCancelar,
    VinculoPrateleiraInDB,
    VincularPrateleiraAoBoletimRequest,
    ResumoPrateleira,
)
from app.services.prateleira_service import PrateleiraService

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# ROTAS POR CONTRATO
# ─────────────────────────────────────────────────────────────

@router.post(
    "/contratos/{contrato_id}/prateleira",
    response_model=PrateleiraInDB,
    status_code=201,
    summary="Registrar execução na prateleira"
)
def create_execucao(
    contrato_id: int,
    execucao_in: PrateleiraCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Registra uma execução de serviço na prateleira de um contrato."""
    service = PrateleiraService(db)
    execucao = service.create_execucao(contrato_id, execucao_in, current_user)
    return _enriquecer(execucao)


@router.get(
    "/contratos/{contrato_id}/prateleira",
    response_model=List[PrateleiraInDB],
    summary="Listar prateleira de um contrato"
)
def list_por_contrato(
    contrato_id: int,
    status: Optional[str] = Query(None, description="Filtrar por status: PENDENTE, AGUARDANDO_MEDICAO, INCLUIDO_EM_MEDICAO, CANCELADO"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Lista todas as execuções na prateleira de um contrato."""
    service = PrateleiraService(db)
    execucoes = service.list_por_contrato(contrato_id, status, skip, limit)
    return [_enriquecer(e) for e in execucoes]


@router.get(
    "/contratos/{contrato_id}/prateleira/pendentes",
    response_model=List[PrateleiraInDB],
    summary="Listar itens disponíveis para medição"
)
def get_pendentes_para_medicao(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Retorna os itens da prateleira disponíveis para inclusão em um Boletim de Medição.
    Inclui execuções PENDENTE e AGUARDANDO_MEDICAO com saldo remanescente.
    Usada pelo modal de criação de BM.
    """
    service = PrateleiraService(db)
    execucoes = service.get_pendentes_para_medicao(contrato_id)
    return [_enriquecer(e) for e in execucoes]


# ─────────────────────────────────────────────────────────────
# ROTAS GLOBAIS (todos os contratos)
# ─────────────────────────────────────────────────────────────

@router.get(
    "/prateleira/",
    response_model=List[PrateleiraInDB],
    summary="Listar todas as execuções (todos os contratos)"
)
def list_global(
    contrato_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    execucoes = service.list_global(contrato_id, status, skip, limit)
    return [_enriquecer(e) for e in execucoes]


@router.get(
    "/prateleira/resumo",
    response_model=ResumoPrateleira,
    summary="Resumo/métricas da prateleira"
)
def get_resumo(
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Retorna métricas agregadas da prateleira para o dashboard."""
    service = PrateleiraService(db)
    return service.get_resumo_global()


@router.get(
    "/prateleira/{execucao_id}",
    response_model=PrateleiraInDB,
    summary="Detalhe de uma execução"
)
def get_execucao(
    execucao_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    return _enriquecer(service.get_execucao(execucao_id))


@router.put(
    "/prateleira/{execucao_id}",
    response_model=PrateleiraInDB,
    summary="Editar execução da prateleira"
)
def update_execucao(
    execucao_id: int,
    execucao_in: PrateleiraUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    return _enriquecer(service.update_execucao(execucao_id, execucao_in))


@router.post(
    "/prateleira/{execucao_id}/aguardar-medicao",
    response_model=PrateleiraInDB,
    summary="Marcar como aguardando medição"
)
def marcar_aguardando_medicao(
    execucao_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Muda o status da execução de PENDENTE para AGUARDANDO_MEDICAO."""
    service = PrateleiraService(db)
    return _enriquecer(service.marcar_aguardando_medicao(execucao_id))


@router.post(
    "/prateleira/{execucao_id}/cancelar",
    response_model=PrateleiraInDB,
    summary="Cancelar execução da prateleira"
)
def cancelar_execucao(
    execucao_id: int,
    payload: PrateleiraCancelar,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    return _enriquecer(service.cancelar_execucao(execucao_id, payload.motivo))


# ─────────────────────────────────────────────────────────────
# VÍNCULO COM BOLETIM DE MEDIÇÃO
# ─────────────────────────────────────────────────────────────

@router.post(
    "/boletins/{boletim_id}/prateleira",
    response_model=List[VinculoPrateleiraInDB],
    status_code=201,
    summary="Vincular itens da prateleira a um boletim"
)
def vincular_prateleira_ao_boletim(
    boletim_id: int,
    payload: VincularPrateleiraAoBoletimRequest,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Vincula um ou mais itens da prateleira a um Boletim de Medição.
    Suporta medição parcial: especifique o valor a ser incluído por item.
    O status do item é atualizado automaticamente.
    """
    service = PrateleiraService(db)
    return service.vincular_ao_boletim(boletim_id, payload.vinculos)


@router.get(
    "/boletins/{boletim_id}/prateleira",
    response_model=List[VinculoPrateleiraInDB],
    summary="Listar itens da prateleira vinculados a um boletim"
)
def get_vinculos_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    return service.get_vinculos_por_boletim(boletim_id)


# ─────────────────────────────────────────────────────────────
# HELPER INTERNO
# ─────────────────────────────────────────────────────────────

def _enriquecer(execucao) -> dict:
    """Adiciona campos calculados e nomes relacionados ao objeto de resposta."""
    from decimal import Decimal
    data = {
        "id": execucao.id,
        "contrato_id": execucao.contrato_id,
        "descricao_servico": execucao.descricao_servico,
        "data_execucao": execucao.data_execucao,
        "percentual_executado": execucao.percentual_executado,
        "valor_estimado": execucao.valor_estimado,
        "valor_medido_acumulado": execucao.valor_medido_acumulado or Decimal(0),
        "status": execucao.status,
        "observacoes": execucao.observacoes,
        "cancelado_motivo": execucao.cancelado_motivo,
        "usuario_responsavel_id": execucao.usuario_responsavel_id,
        "created_at": execucao.created_at,
        "updated_at": execucao.updated_at,
        # Campos enriquecidos
        "contrato_numero": execucao.contrato.numero_contrato if execucao.contrato else None,
        "usuario_responsavel_nome": execucao.usuario_responsavel.nome if execucao.usuario_responsavel else None,
        "saldo_disponivel": (execucao.valor_estimado or Decimal(0)) - (execucao.valor_medido_acumulado or Decimal(0)),
    }
    return data
