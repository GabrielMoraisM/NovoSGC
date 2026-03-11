from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.faturamento import FaturamentoCreate, FaturamentoInDB, FaturamentoUpdate
from app.services.faturamento_service import FaturamentoService
from app.services.log_service import LogService
from app.models.usuario import Usuario
from app.models.boletim_medicao import BoletimMedicao
from app.models.contrato_imposto import ContratoImposto

router = APIRouter()


def _log_dict(obj):
    return jsonable_encoder({k: v for k, v in obj.__dict__.items() if not k.startswith('_')})


@router.post("/", response_model=FaturamentoInDB, status_code=status.HTTP_201_CREATED)
def create_faturamento(
    faturamento_in: FaturamentoCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    # Pre-check: impostos do contrato devem estar configurados
    bm = db.get(BoletimMedicao, faturamento_in.bm_id)
    if not bm:
        raise HTTPException(status_code=404, detail="Boletim de medição não encontrado.")

    qtd_impostos = db.query(ContratoImposto).filter(
        ContratoImposto.contrato_id == bm.contrato_id
    ).count()

    if qtd_impostos == 0:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "IMPOSTOS_NAO_CONFIGURADOS",
                "contrato_id": bm.contrato_id,
                "message": "Configure os impostos do contrato antes de emitir a primeira NF.",
            },
        )

    service = FaturamentoService(db)
    faturamento = service.create_faturamento(faturamento_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="CREATE",
        entidade="faturamentos",
        entidade_id=faturamento.id,
        dados_novos=_log_dict(faturamento),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return faturamento


@router.get("/", response_model=List[FaturamentoInDB])
def list_faturamentos(
    db: Session = Depends(deps.get_db),
    bm_id: Optional[int] = Query(None),
    contrato_id: Optional[int] = Query(None, description="Filtrar por contrato (via boletins)"),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = FaturamentoService(db)
    return service.list_faturamentos(bm_id=bm_id, contrato_id=contrato_id, skip=skip, limit=limit)


@router.get("/{faturamento_id}", response_model=FaturamentoInDB)
def get_faturamento(
    faturamento_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = FaturamentoService(db)
    return service.get_faturamento(faturamento_id)


@router.put("/{faturamento_id}", response_model=FaturamentoInDB)
def update_faturamento(
    faturamento_id: int,
    faturamento_in: FaturamentoUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = FaturamentoService(db)
    fat_antes = service.get_faturamento(faturamento_id)
    dados_antigos = _log_dict(fat_antes)
    acao = "CANCEL" if getattr(faturamento_in, 'status', None) == "CANCELADO" else "UPDATE"
    faturamento = service.update_faturamento(faturamento_id, faturamento_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao=acao,
        entidade="faturamentos",
        entidade_id=faturamento_id,
        dados_antigos=dados_antigos,
        dados_novos=_log_dict(faturamento),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return faturamento
