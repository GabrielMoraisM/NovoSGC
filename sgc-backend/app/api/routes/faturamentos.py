from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.faturamento import FaturamentoCreate, FaturamentoInDB, FaturamentoUpdate
from app.services.faturamento_service import FaturamentoService
from app.models.usuario import Usuario
from app.models.boletim_medicao import BoletimMedicao
from app.models.contrato_imposto import ContratoImposto

router = APIRouter()

@router.post("/", response_model=FaturamentoInDB, status_code=status.HTTP_201_CREATED)
def create_faturamento(
    faturamento_in: FaturamentoCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    # ── Pre-check: impostos do contrato devem estar configurados ──────────
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
    # ─────────────────────────────────────────────────────────────────────

    service = FaturamentoService(db)
    return service.create_faturamento(faturamento_in)

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
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = FaturamentoService(db)
    return service.update_faturamento(faturamento_id, faturamento_in)