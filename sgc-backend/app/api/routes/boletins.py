from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.boletim import BoletimCreate, BoletimInDB, BoletimUpdate
from app.services.boletim_service import BoletimService
from app.models.usuario import Usuario

router = APIRouter()

# ----------------------------------------------------------------------
# POST /contratos/{contrato_id}/boletins
# ----------------------------------------------------------------------
@router.post("/contratos/{contrato_id}/boletins", response_model=BoletimInDB, status_code=status.HTTP_201_CREATED)
def create_boletim(
    contrato_id: int,
    boletim_in: BoletimCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Cria um novo boletim de medição para um contrato específico.
    O número sequencial é gerado automaticamente pelo listener.
    """
    service = BoletimService(db)
    # O contrato_id é passado diretamente para o serviço, não para o schema
    return service.create_boletim(contrato_id, boletim_in)


# ----------------------------------------------------------------------
# GET /contratos/{contrato_id}/boletins
# ----------------------------------------------------------------------
@router.get("/contratos/{contrato_id}/boletins", response_model=List[BoletimInDB])
def list_boletins_por_contrato(
    contrato_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Lista todos os boletins de um contrato, ordenados por número sequencial.
    """
    service = BoletimService(db)
    return service.list_boletins_por_contrato(contrato_id, skip, limit)


# ----------------------------------------------------------------------
# GET /boletins/{boletim_id}
# ----------------------------------------------------------------------
@router.get("/boletins/{boletim_id}", response_model=BoletimInDB)
def get_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Obtém os detalhes de um boletim específico pelo ID.
    """
    service = BoletimService(db)
    return service.get_boletim(boletim_id)


# ----------------------------------------------------------------------
# PUT /boletins/{boletim_id}
# ----------------------------------------------------------------------
@router.put("/boletins/{boletim_id}", response_model=BoletimInDB)
def update_boletim(
    boletim_id: int,
    boletim_in: BoletimUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Atualiza os dados de um boletim.
    Não permitido se o boletim estiver FATURADO.
    """
    service = BoletimService(db)
    return service.update_boletim(boletim_id, boletim_in)


# ----------------------------------------------------------------------
# DELETE /boletins/{boletim_id}
# ----------------------------------------------------------------------
@router.delete("/boletins/{boletim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Remove um boletim (apenas se não estiver FATURADO e não houver faturas vinculadas).
    """
    service = BoletimService(db)
    service.delete_boletim(boletim_id)
    return None


# ----------------------------------------------------------------------
# POST /boletins/{boletim_id}/aprovar
# ----------------------------------------------------------------------
@router.post("/boletins/{boletim_id}/aprovar", response_model=BoletimInDB)
def aprovar_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Altera o status do boletim para APROVADO (se estiver em RASCUNHO).
    """
    service = BoletimService(db)
    return service.aprovar_boletim(boletim_id)


# ----------------------------------------------------------------------
# POST /boletins/{boletim_id}/cancelar
# ----------------------------------------------------------------------
@router.post("/boletins/{boletim_id}/cancelar", response_model=BoletimInDB)
def cancelar_boletim(
    boletim_id: int,
    motivo: str = Query(..., description="Motivo do cancelamento"),
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Cancela um boletim (altera status para CANCELADO e exige motivo).
    """
    service = BoletimService(db)
    return service.cancelar_boletim(boletim_id, motivo)

@router.get("/boletins/", response_model=List[BoletimInDB])
def list_boletins(
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = BoletimService(db)
    return service.list_boletins(status=status, skip=skip, limit=limit)