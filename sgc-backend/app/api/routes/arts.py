from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.art import ArtCreate, ArtInDB, ArtUpdate
from app.services.art_service import ArtService
from app.models.usuario import Usuario

router = APIRouter()

@router.get("/contratos/{contrato_id}/arts", response_model=List[ArtInDB])
def list_arts_por_contrato(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ArtService(db)
    return service.get_arts_por_contrato(contrato_id)

@router.post("/contratos/{contrato_id}/arts", response_model=ArtInDB, status_code=status.HTTP_201_CREATED)
def create_art(
    contrato_id: int,
    art_in: ArtCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ArtService(db)
    return service.create_art(contrato_id, art_in)

@router.get("/arts/{art_id}", response_model=ArtInDB)
def get_art(
    art_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ArtService(db)
    return service.get_art(art_id)

@router.put("/arts/{art_id}", response_model=ArtInDB)
def update_art(
    art_id: int,
    art_in: ArtUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ArtService(db)
    return service.update_art(art_id, art_in)

@router.delete("/arts/{art_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_art(
    art_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ArtService(db)
    service.delete_art(art_id)
    return None