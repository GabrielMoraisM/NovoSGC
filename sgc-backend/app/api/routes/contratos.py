from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.contrato import ContratoCreate, ContratoInDB, ContratoUpdate
from app.services.contrato_service import ContratoService
from app.models.usuario import Usuario

router = APIRouter()

# ----------------------------------------------------------------------
# POST /contratos/
# ----------------------------------------------------------------------
@router.post("/", response_model=ContratoInDB, status_code=status.HTTP_201_CREATED)
def create_contrato(
    *,
    db: Session = Depends(deps.get_db),
    contrato_in: ContratoCreate,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Criar novo contrato."""
    service = ContratoService(db)
    return service.create_contrato(contrato_in)


# ----------------------------------------------------------------------
# GET /contratos/
# ----------------------------------------------------------------------
@router.get("/", response_model=List[ContratoInDB])
def list_contratos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Listar contratos com paginação."""
    service = ContratoService(db)
    return service.list_contratos(skip=skip, limit=limit)


# ----------------------------------------------------------------------
# GET /contratos/{id}
# ----------------------------------------------------------------------
@router.get("/{contrato_id}", response_model=ContratoInDB)
def get_contrato(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de um contrato pelo ID."""
    service = ContratoService(db)
    return service.get_contrato(contrato_id)


# ----------------------------------------------------------------------
# PUT /contratos/{id}
# ----------------------------------------------------------------------
@router.put("/{contrato_id}", response_model=ContratoInDB)
def update_contrato(
    contrato_id: int,
    contrato_in: ContratoUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualizar dados de um contrato."""
    service = ContratoService(db)
    return service.update_contrato(contrato_id, contrato_in)


# ----------------------------------------------------------------------
# DELETE /contratos/{id}
# ----------------------------------------------------------------------
@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contrato(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remover contrato (somente se não houver boletins vinculados)."""
    service = ContratoService(db)
    service.delete_contrato(contrato_id)
    return None