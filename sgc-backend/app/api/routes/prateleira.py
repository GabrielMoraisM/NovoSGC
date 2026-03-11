from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.models.usuario import Usuario
from app.schemas.prateleira import (
    PrateleiraCreate, PrateleiraUpdate, PrateleiraInDB, PrateleiraCancelar,
    VinculoPrateleiraInDB, VincularPrateleiraAoBoletimRequest, ResumoPrateleira,
)
from app.services.prateleira_service import PrateleiraService
from app.services.log_service import LogService

router = APIRouter()


def _log_dict(obj):
    return jsonable_encoder({k: v for k, v in obj.__dict__.items() if not k.startswith('_')})


@router.post("/contratos/{contrato_id}/prateleira", response_model=PrateleiraInDB, status_code=201, summary="Registrar execucao na prateleira")
def create_execucao(
    contrato_id: int,
    execucao_in: PrateleiraCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    execucao = service.create_execucao(contrato_id, execucao_in, current_user)
    LogService(db).registrar_log(
        usuario_id=current_user.id, usuario_email=current_user.email, acao="CREATE",
        entidade="prateleira", entidade_id=execucao.id, dados_novos=_log_dict(execucao),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return _enriquecer(execucao)


@router.get("/contratos/{contrato_id}/prateleira", response_model=List[PrateleiraInDB])
def list_por_contrato(
    contrato_id: int,
    status: Optional[str] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    return [_enriquecer(e) for e in PrateleiraService(db).list_por_contrato(contrato_id, status, skip, limit)]


@router.get("/contratos/{contrato_id}/prateleira/pendentes", response_model=List[PrateleiraInDB])
def get_pendentes_para_medicao(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    return [_enriquecer(e) for e in PrateleiraService(db).get_pendentes_para_medicao(contrato_id)]


@router.get("/prateleira/", response_model=List[PrateleiraInDB])
def list_global(
    contrato_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    return [_enriquecer(e) for e in PrateleiraService(db).list_global(contrato_id, status, skip, limit)]


@router.get("/prateleira/resumo", response_model=ResumoPrateleira)
def get_resumo(db: Session = Depends(deps.get_db), current_user: Usuario = Depends(deps.get_current_active_user)):
    return PrateleiraService(db).get_resumo_global()


@router.get("/prateleira/{execucao_id}", response_model=PrateleiraInDB)
def get_execucao(execucao_id: int, db: Session = Depends(deps.get_db), current_user: Usuario = Depends(deps.get_current_active_user)):
    return _enriquecer(PrateleiraService(db).get_execucao(execucao_id))


@router.put("/prateleira/{execucao_id}", response_model=PrateleiraInDB)
def update_execucao(
    execucao_id: int,
    execucao_in: PrateleiraUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    exec_antes = service.get_execucao(execucao_id)
    dados_antigos = _log_dict(exec_antes)
    execucao = service.update_execucao(execucao_id, execucao_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id, usuario_email=current_user.email, acao="UPDATE",
        entidade="prateleira", entidade_id=execucao_id,
        dados_antigos=dados_antigos, dados_novos=_log_dict(execucao),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return _enriquecer(execucao)


@router.post("/prateleira/{execucao_id}/aguardar-medicao", response_model=PrateleiraInDB)
def marcar_aguardando_medicao(
    execucao_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    execucao = service.marcar_aguardando_medicao(execucao_id)
    LogService(db).registrar_log(
        usuario_id=current_user.id, usuario_email=current_user.email, acao="STATUS_UPDATE",
        entidade="prateleira", entidade_id=execucao_id,
        dados_novos={"status": execucao.status},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return _enriquecer(execucao)


@router.post("/prateleira/{execucao_id}/cancelar", response_model=PrateleiraInDB)
def cancelar_execucao(
    execucao_id: int,
    payload: PrateleiraCancelar,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PrateleiraService(db)
    execucao = service.cancelar_execucao(execucao_id, payload.motivo)
    LogService(db).registrar_log(
        usuario_id=current_user.id, usuario_email=current_user.email, acao="CANCEL",
        entidade="prateleira", entidade_id=execucao_id,
        dados_novos={"motivo": payload.motivo, "status": execucao.status},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return _enriquecer(execucao)


@router.post("/boletins/{boletim_id}/prateleira", response_model=List[VinculoPrateleiraInDB], status_code=201)
def vincular_prateleira_ao_boletim(
    boletim_id: int,
    payload: VincularPrateleiraAoBoletimRequest,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    return PrateleiraService(db).vincular_ao_boletim(boletim_id, payload.vinculos)


@router.get("/boletins/{boletim_id}/prateleira", response_model=List[VinculoPrateleiraInDB])
def get_vinculos_boletim(boletim_id: int, db: Session = Depends(deps.get_db), current_user: Usuario = Depends(deps.get_current_active_user)):
    return PrateleiraService(db).get_vinculos_por_boletim(boletim_id)


def _enriquecer(execucao) -> dict:
    return {
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
        "contrato_numero": execucao.contrato.numero_contrato if execucao.contrato else None,
        "usuario_responsavel_nome": execucao.usuario_responsavel.nome if execucao.usuario_responsavel else None,
        "saldo_disponivel": (execucao.valor_estimado or Decimal(0)) - (execucao.valor_medido_acumulado or Decimal(0)),
    }
