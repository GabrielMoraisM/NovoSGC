from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.empresa import EmpresaCreate, EmpresaInDB, EmpresaUpdate
from app.services.empresa_service import EmpresaService
from app.services.log_service import LogService
from app.models.usuario import Usuario

router = APIRouter()


def _log_dict(obj):
    return jsonable_encoder({k: v for k, v in obj.__dict__.items() if not k.startswith('_')})


# POST /empresas/
@router.post("/", response_model=EmpresaInDB, status_code=status.HTTP_201_CREATED)
def create_empresa(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    empresa_in: EmpresaCreate,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Criar nova empresa (apenas autenticado)."""
    service = EmpresaService(db)
    empresa = service.create_empresa(empresa_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="CREATE",
        entidade="empresas",
        entidade_id=empresa.id,
        dados_novos=_log_dict(empresa),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return empresa


# GET /empresas/
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


# GET /empresas/{id}
@router.get("/{empresa_id}", response_model=EmpresaInDB)
def get_empresa(
    empresa_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de uma empresa pelo ID."""
    service = EmpresaService(db)
    return service.get_empresa(empresa_id)


# PUT /empresas/{id}
@router.put("/{empresa_id}", response_model=EmpresaInDB)
def update_empresa(
    empresa_id: int,
    empresa_in: EmpresaUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualizar dados de uma empresa."""
    service = EmpresaService(db)
    empresa_antes = service.get_empresa(empresa_id)
    dados_antigos = _log_dict(empresa_antes)
    empresa = service.update_empresa(empresa_id, empresa_in)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="UPDATE",
        entidade="empresas",
        entidade_id=empresa_id,
        dados_antigos=dados_antigos,
        dados_novos=_log_dict(empresa),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return empresa


# DELETE /empresas/{id}
@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empresa(
    empresa_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remover empresa (somente se não houver contratos vinculados)."""
    service = EmpresaService(db)
    empresa = service.get_empresa(empresa_id)
    dados_antigos = _log_dict(empresa)
    service.delete_empresa(empresa_id)
    LogService(db).registrar_log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao="DELETE",
        entidade="empresas",
        entidade_id=empresa_id,
        dados_antigos=dados_antigos,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return None
