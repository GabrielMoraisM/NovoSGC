from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.pagamento import PagamentoCreate, PagamentoInDB, PagamentoUpdate
from app.services.pagamento_service import PagamentoService
from app.models.usuario import Usuario

router = APIRouter()

# ----------------------------------------------------------------------
# POST /pagamentos/
# ----------------------------------------------------------------------
@router.post("/", response_model=PagamentoInDB, status_code=status.HTTP_201_CREATED)
def create_pagamento(
    *,
    db: Session = Depends(deps.get_db),
    pagamento_in: PagamentoCreate,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Registrar um novo pagamento para um faturamento."""
    service = PagamentoService(db)
    return service.create_pagamento(pagamento_in)


# ----------------------------------------------------------------------
# GET /pagamentos/
# ----------------------------------------------------------------------
@router.get("/", response_model=List[PagamentoInDB])
def list_pagamentos(
    db: Session = Depends(deps.get_db),
    faturamento_id: Optional[int] = Query(None, description="Filtrar por faturamento"),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Listar pagamentos com paginação e filtro opcional por faturamento."""
    service = PagamentoService(db)
    return service.list_pagamentos(
        faturamento_id=faturamento_id,
        skip=skip,
        limit=limit
    )


# ----------------------------------------------------------------------
# GET /pagamentos/{pagamento_id}
# ----------------------------------------------------------------------
@router.get("/{pagamento_id}", response_model=PagamentoInDB)
def get_pagamento(
    pagamento_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de um pagamento pelo ID."""
    service = PagamentoService(db)
    return service.get_pagamento(pagamento_id)


# ----------------------------------------------------------------------
# PUT /pagamentos/{pagamento_id}
# ----------------------------------------------------------------------
@router.put("/{pagamento_id}", response_model=PagamentoInDB)
def update_pagamento(
    pagamento_id: int,
    pagamento_in: PagamentoUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualizar dados de um pagamento."""
    service = PagamentoService(db)
    return service.update_pagamento(pagamento_id, pagamento_in)


# ----------------------------------------------------------------------
# DELETE /pagamentos/{pagamento_id}
# ----------------------------------------------------------------------
@router.delete("/{pagamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pagamento(
    pagamento_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remover um pagamento. O status da NF será recalculado."""
    service = PagamentoService(db)
    service.delete_pagamento(pagamento_id)
    return None