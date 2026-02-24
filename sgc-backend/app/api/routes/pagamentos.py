from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.pagamento import PagamentoCreate, PagamentoInDB, PagamentoUpdate
from app.services.pagamento_service import PagamentoService
from app.models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=PagamentoInDB, status_code=status.HTTP_201_CREATED)
def create_pagamento(
    pagamento_in: PagamentoCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    return service.create_pagamento(pagamento_in)

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
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    return service.update_pagamento(pagamento_id, pagamento_in)

@router.delete("/{pagamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pagamento(
    pagamento_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = PagamentoService(db)
    service.delete_pagamento(pagamento_id)
    return None