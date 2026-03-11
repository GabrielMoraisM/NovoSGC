from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.boletim import BoletimCreate, BoletimInDB, BoletimUpdate
from app.services.boletim_service import BoletimService
from app.services.log_service import LogService
from app.models.usuario import Usuario

router = APIRouter()


def _log_dict(obj):
    return jsonable_encoder({k: v for k, v in obj.__dict__.items() if not k.startswith('_')})


# POST /contratos/{contrato_id}/boletins
@router.post("/contratos/{contrato_id}/boletins", response_model=BoletimInDB, status_code=status.HTTP_201_CREATED)
def create_boletim(
    contrato_id: int,
    boletim_in: BoletimCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Cria um novo boletim de medição para um contrato específico."""
    service = BoletimService(db)
    boletim = service.create_boletim(contrato_id, boletim_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="CREATE",
        entidade="boletins",
        entidade_id=boletim.id,
        dados_novos=_log_dict(boletim),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return boletim


# GET /contratos/{contrato_id}/boletins
@router.get("/contratos/{contrato_id}/boletins", response_model=List[BoletimInDB])
def list_boletins_por_contrato(
    contrato_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Lista todos os boletins de um contrato, ordenados por número sequencial."""
    service = BoletimService(db)
    return service.list_boletins_por_contrato(contrato_id, skip, limit)


# GET /boletins/{boletim_id}
@router.get("/boletins/{boletim_id}", response_model=BoletimInDB)
def get_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obtém os detalhes de um boletim específico pelo ID."""
    service = BoletimService(db)
    return service.get_boletim(boletim_id)


# PUT /boletins/{boletim_id}
@router.put("/boletins/{boletim_id}", response_model=BoletimInDB)
def update_boletim(
    boletim_id: int,
    boletim_in: BoletimUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualiza os dados de um boletim. Não permitido se estiver FATURADO."""
    service = BoletimService(db)
    boletim_antes = service.get_boletim(boletim_id)
    dados_antigos = _log_dict(boletim_antes)
    boletim = service.update_boletim(boletim_id, boletim_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="UPDATE",
        entidade="boletins",
        entidade_id=boletim_id,
        dados_antigos=dados_antigos,
        dados_novos=_log_dict(boletim),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return boletim


# DELETE /boletins/{boletim_id}
@router.delete("/boletins/{boletim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_boletim(
    boletim_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remove um boletim (apenas se não estiver FATURADO e sem faturas vinculadas)."""
    service = BoletimService(db)
    boletim = service.get_boletim(boletim_id)
    dados_antigos = _log_dict(boletim)
    service.delete_boletim(boletim_id)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="DELETE",
        entidade="boletins",
        entidade_id=boletim_id,
        dados_antigos=dados_antigos,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return None


# POST /boletins/{boletim_id}/aprovar
@router.post("/boletins/{boletim_id}/aprovar", response_model=BoletimInDB)
def aprovar_boletim(
    boletim_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Altera o status do boletim para APROVADO (se estiver em RASCUNHO)."""
    service = BoletimService(db)
    boletim = service.aprovar_boletim(boletim_id)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="APPROVE",
        entidade="boletins",
        entidade_id=boletim_id,
        dados_novos=_log_dict(boletim),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return boletim


# POST /boletins/{boletim_id}/cancelar
@router.post("/boletins/{boletim_id}/cancelar", response_model=BoletimInDB)
def cancelar_boletim(
    boletim_id: int,
    request: Request,
    motivo: str = Query(..., description="Motivo do cancelamento"),
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Cancela um boletim (altera status para CANCELADO e exige motivo)."""
    service = BoletimService(db)
    boletim = service.cancelar_boletim(boletim_id, motivo)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="CANCEL",
        entidade="boletins",
        entidade_id=boletim_id,
        dados_novos={"motivo": motivo, **_log_dict(boletim)},
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return boletim


@router.get("/boletins/", response_model=List[BoletimInDB])
def list_boletins(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = BoletimService(db)
    return service.list_boletins(status=status, skip=skip, limit=limit)
