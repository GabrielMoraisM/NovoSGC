from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.faturamento import FaturamentoCreate, FaturamentoInDB, FaturamentoUpdate
from app.services.faturamento_service import FaturamentoService
from app.models.usuario import Usuario

router = APIRouter()

# ----------------------------------------------------------------------
# POST /faturamentos/
# ----------------------------------------------------------------------
@router.post("/", response_model=FaturamentoInDB, status_code=status.HTTP_201_CREATED)
def create_faturamento(
    *,
    db: Session = Depends(deps.get_db),
    faturamento_in: FaturamentoCreate,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Criar um novo faturamento a partir de um boletim aprovado."""
    service = FaturamentoService(db)
    return service.create_faturamento(faturamento_in)


# ----------------------------------------------------------------------
# GET /faturamentos/
# ----------------------------------------------------------------------
@router.get("/", response_model=List[FaturamentoInDB])
def list_faturamentos(
    db: Session = Depends(deps.get_db),
    bm_id: Optional[int] = Query(None, description="Filtrar por boletim"),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Listar faturamentos com paginação e filtro opcional por boletim."""
    service = FaturamentoService(db)
    return service.list_faturamentos(bm_id=bm_id, skip=skip, limit=limit)


# ----------------------------------------------------------------------
# GET /faturamentos/{faturamento_id}
# ----------------------------------------------------------------------
@router.get("/{faturamento_id}", response_model=FaturamentoInDB)
def get_faturamento(
    faturamento_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de um faturamento pelo ID."""
    service = FaturamentoService(db)
    return service.get_faturamento(faturamento_id)


# ----------------------------------------------------------------------
# PUT /faturamentos/{faturamento_id}
# ----------------------------------------------------------------------
@router.put("/{faturamento_id}", response_model=FaturamentoInDB)
def update_faturamento(
    faturamento_id: int,
    faturamento_in: FaturamentoUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualizar dados de um faturamento (não permite alterar se quitado/cancelado)."""
    service = FaturamentoService(db)
    return service.update_faturamento(faturamento_id, faturamento_in)


# ----------------------------------------------------------------------
# DELETE /faturamentos/{faturamento_id}
# ----------------------------------------------------------------------
@router.delete("/{faturamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faturamento(
    faturamento_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remover um faturamento (apenas se não houver pagamentos vinculados)."""
    service = FaturamentoService(db)
    # Por simplicidade, não implementamos deleção física. Pode ser adicionada depois.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Deleção de faturamento não implementada. Utilize cancelamento."
    )


# ----------------------------------------------------------------------
# POST /faturamentos/{faturamento_id}/cancelar
# ----------------------------------------------------------------------
@router.post("/{faturamento_id}/cancelar", response_model=FaturamentoInDB)
def cancelar_faturamento(
    faturamento_id: int,
    motivo: str = Query(..., description="Motivo do cancelamento"),
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Cancelar um faturamento (altera status para CANCELADO)."""
    service = FaturamentoService(db)
    return service.cancelar_faturamento(faturamento_id, motivo)