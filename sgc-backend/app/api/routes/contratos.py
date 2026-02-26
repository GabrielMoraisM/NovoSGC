from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.contrato import ContratoCreate, ContratoInDB, ContratoUpdate
from app.services.contrato_service import ContratoService
from app.models.usuario import Usuario
from app.core.exceptions import BusinessError
from app.services import financeiro_service
from app.api.deps import get_db, get_current_user



router = APIRouter()

# ----------------------------------------------------------------------
# POST /contratos/
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# DELETE /contratos/{id}
# ----------------------------------------------------------------------


@router.get("/{contrato_id}/resumo-financeiro")
def get_resumo_financeiro_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna o resumo financeiro completo de um contrato específico.
    """
    try:
        resumo = financeiro_service.calcular_resumo_contrato(db, contrato_id)
        desempenho = financeiro_service.calcular_status_desempenho(db, contrato_id)
        return {**resumo, **desempenho}
    except BusinessError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log do erro e retorne apenas o resumo (ou um erro amigável)
        print(f"Erro ao calcular desempenho: {e}")
        return {**resumo, "status_desempenho": "ERRO"}
    


@router.post("/", response_model=ContratoInDB, status_code=status.HTTP_201_CREATED)
def create_contrato(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    contrato_in: ContratoCreate,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoService(db)
    return service.create_contrato(contrato_in, current_user=current_user, request=request)




@router.put("/{contrato_id}", response_model=ContratoInDB)
def update_contrato(
    contrato_id: int,
    contrato_in: ContratoUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoService(db)
    return service.update_contrato(contrato_id, contrato_in, current_user=current_user, request=request)


@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contrato(
    contrato_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoService(db)
    service.delete_contrato(contrato_id, current_user=current_user, request=request)
    return None