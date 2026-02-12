from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.aditivo import AditivoCreate, AditivoInDB, AditivoUpdate
from app.services.aditivo_service import AditivoService
from app.models.usuario import Usuario

router = APIRouter()

# ----------------------------------------------------------------------
# POST /contratos/{contrato_id}/aditivos
# ----------------------------------------------------------------------
@router.post("/contratos/{contrato_id}/aditivos", response_model=AditivoInDB, status_code=status.HTTP_201_CREATED)
def create_aditivo(
    contrato_id: int,
    aditivo_in: AditivoCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Criar um novo aditivo para um contrato específico."""
    # Garantir que o contrato_id no path seja o mesmo do body
    aditivo_in.contrato_id = contrato_id
    service = AditivoService(db)
    return service.create_aditivo(aditivo_in)


# ----------------------------------------------------------------------
# GET /contratos/{contrato_id}/aditivos
# ----------------------------------------------------------------------
@router.get("/contratos/{contrato_id}/aditivos", response_model=List[AditivoInDB])
def list_aditivos_por_contrato(
    contrato_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Listar todos os aditivos de um contrato."""
    service = AditivoService(db)
    return service.list_aditivos_por_contrato(contrato_id, skip=skip, limit=limit)


# ----------------------------------------------------------------------
# GET /aditivos/{aditivo_id}
# ----------------------------------------------------------------------
@router.get("/aditivos/{aditivo_id}", response_model=AditivoInDB)
def get_aditivo(
    aditivo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de um aditivo pelo ID."""
    service = AditivoService(db)
    return service.get_aditivo(aditivo_id)


# ----------------------------------------------------------------------
# PUT /aditivos/{aditivo_id}
# ----------------------------------------------------------------------
@router.put("/aditivos/{aditivo_id}", response_model=AditivoInDB)
def update_aditivo(
    aditivo_id: int,
    aditivo_in: AditivoUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualizar dados de um aditivo."""
    service = AditivoService(db)
    return service.update_aditivo(aditivo_id, aditivo_in)


# ----------------------------------------------------------------------
# DELETE /aditivos/{aditivo_id}
# ----------------------------------------------------------------------
@router.delete("/aditivos/{aditivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aditivo(
    aditivo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remover um aditivo."""
    service = AditivoService(db)
    service.delete_aditivo(aditivo_id)
    return None