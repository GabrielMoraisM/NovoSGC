from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.usuario import UsuarioCreate, UsuarioInDB, UsuarioUpdate
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=UsuarioInDB, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(deps.get_db)
):
    service = UsuarioService(db)
    return service.create_usuario(usuario)

@router.get("/", response_model=List[UsuarioInDB])
def list_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = UsuarioService(db)
    return service.repo.get_multi(skip, limit)

@router.get("/{usuario_id}", response_model=UsuarioInDB)
def get_usuario(
    usuario_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = UsuarioService(db)
    return service.get_usuario(usuario_id)

@router.put("/{usuario_id}", response_model=UsuarioInDB)
def update_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = UsuarioService(db)
    return service.update_usuario(usuario_id, usuario)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    usuario_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = UsuarioService(db)
    service.delete_usuario(usuario_id)
