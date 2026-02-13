from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.contrato_seguro import ContratoSeguroCreate, ContratoSeguroInDB, ContratoSeguroUpdate
from app.services.contrato_seguro_service import ContratoSeguroService
from app.models.usuario import Usuario

router = APIRouter()

# GET /contratos/{contrato_id}/seguros
@router.get("/contratos/{contrato_id}/seguros", response_model=List[ContratoSeguroInDB])
def list_seguros_por_contrato(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoSeguroService(db)
    return service.get_seguros_por_contrato(contrato_id)

# POST /contratos/{contrato_id}/seguros
@router.post("/contratos/{contrato_id}/seguros", response_model=ContratoSeguroInDB, status_code=status.HTTP_201_CREATED)
def create_seguro(
    contrato_id: int,
    seguro_in: ContratoSeguroCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoSeguroService(db)
    return service.create_seguro(contrato_id, seguro_in)

# GET /seguros/{seguro_id}
@router.get("/seguros/{seguro_id}", response_model=ContratoSeguroInDB)
def get_seguro(
    seguro_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoSeguroService(db)
    return service.get_seguro(seguro_id)

# PUT /seguros/{seguro_id}
@router.put("/seguros/{seguro_id}", response_model=ContratoSeguroInDB)
def update_seguro(
    seguro_id: int,
    seguro_in: ContratoSeguroUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoSeguroService(db)
    return service.update_seguro(seguro_id, seguro_in)

# DELETE /seguros/{seguro_id}
@router.delete("/seguros/{seguro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_seguro(
    seguro_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoSeguroService(db)
    service.delete_seguro(seguro_id)
    return None