from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.pagamento import PagamentoCreate, PagamentoInDB, PagamentoUpdate
from app.services.pagamento_service import PagamentoService
from app.services.log_service import LogService
from app.models.usuario import Usuario

router = APIRouter()


def _log_dict(obj):
    return jsonable_encoder({k: v for k, v in obj.__dict__.items() if not k.startswith('_')})


@router.post("/", response_model=PagamentoInDB, status_code=status.HTTP_201_CREATED)
def create_pagamento(
    pagamento_in: PagamentoCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    pagamento = service.create_pagamento(pagamento_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="CREATE",
        entidade="pagamentos",
        entidade_id=pagamento.id,
        dados_novos=_log_dict(pagamento),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return pagamento


@router.get("/", response_model=List[PagamentoInDB])
def list_pagamentos(
    db: Session = Depends(deps.get_db),
    faturamento_id: Optional[int] = Query(None),
    contrato_id: Optional[int] = Query(None, description="Filtrar por contrato (via faturamentos e boletins)"),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    return service.list_pagamentos(faturamento_id=faturamento_id, contrato_id=contrato_id, skip=skip, limit=limit)


@router.get("/{pagamento_id}", response_model=PagamentoInDB)
def get_pagamento(
    pagamento_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    return service.get_pagamento(pagamento_id)


@router.put("/{pagamento_id}", response_model=PagamentoInDB)
def update_pagamento(
    pagamento_id: int,
    pagamento_in: PagamentoUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    pag_antes = service.get_pagamento(pagamento_id)
    dados_antigos = _log_dict(pag_antes)
    pagamento = service.update_pagamento(pagamento_id, pagamento_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="UPDATE",
        entidade="pagamentos",
        entidade_id=pagamento_id,
        dados_antigos=dados_antigos,
        dados_novos=_log_dict(pagamento),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return pagamento


@router.delete("/{pagamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pagamento(
    pagamento_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    pagamento = service.get_pagamento(pagamento_id)
    dados_antigos = _log_dict(pagamento)
    service.delete_pagamento(pagamento_id)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="DELETE",
        entidade="pagamentos",
        entidade_id=pagamento_id,
        dados_antigos=dados_antigos,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return None
