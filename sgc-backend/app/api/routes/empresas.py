from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.empresa import EmpresaCreate, EmpresaInDB, EmpresaUpdate
from app.services.empresa_service import EmpresaService
from app.models.usuario import Usuario  # apenas para o tipo do current_user

router = APIRouter()

# ----------------------------------------------------------------------
# POST /empresas/
# ----------------------------------------------------------------------
@router.post("/", response_model=EmpresaInDB, status_code=status.HTTP_201_CREATED)
def create_empresa(
    *,
    db: Session = Depends(deps.get_db),
    empresa_in: EmpresaCreate,
    current_user: Usuario = Depends(deps.get_current_active_user)  # proteção
):
    """Criar nova empresa (apenas autenticado)."""
    service = EmpresaService(db)
    return service.create_empresa(empresa_in)


# ----------------------------------------------------------------------
# GET /empresas/
# ----------------------------------------------------------------------
@router.get("/", response_model=List[EmpresaInDB])
def list_empresas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Listar empresas com paginação."""
    service = EmpresaService(db)
    return service.list_empresas(skip=skip, limit=limit)


# ----------------------------------------------------------------------
# GET /empresas/{id}
# ----------------------------------------------------------------------
@router.get("/{empresa_id}", response_model=EmpresaInDB)
def get_empresa(
    empresa_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de uma empresa pelo ID."""
    service = EmpresaService(db)
    return service.get_empresa(empresa_id)


# ----------------------------------------------------------------------
# PUT /empresas/{id}
# ----------------------------------------------------------------------
@router.put("/{empresa_id}", response_model=EmpresaInDB)
def update_empresa(
    empresa_id: int,
    empresa_in: EmpresaUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualizar dados de uma empresa."""
    service = EmpresaService(db)
    return service.update_empresa(empresa_id, empresa_in)


# ----------------------------------------------------------------------
# DELETE /empresas/{id}
# ----------------------------------------------------------------------
@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empresa(
    empresa_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remover empresa (somente se não houver contratos vinculados)."""
    service = EmpresaService(db)
    service.delete_empresa(empresa_id)
    return None  # 204 No Content