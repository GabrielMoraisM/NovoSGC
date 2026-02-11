# app/api/routes/usuarios.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user, get_current_active_user
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario

router = APIRouter(dependencies=[Depends(get_current_active_user)])  # TODAS as rotas exigem autenticação

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    *,
    db: Session = Depends(get_db),
    usuario_in: UsuarioCreate,
    current_user: Usuario = Depends(get_current_active_user)  # só ADMIN pode criar?
):
    """Cria um novo usuário."""
    service = UsuarioService(db)
    try:
        usuario = service.criar_usuario(usuario_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return usuario

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Lista todos os usuários (apenas para teste, depois protegeremos)."""
    service = UsuarioService(db)
    usuarios = service.listar_usuarios(skip, limit)
    return usuarios

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um usuário pelo ID."""
    service = UsuarioService(db)
    usuario = service.obter_usuario(usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    usuario_in: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um usuário existente."""
    service = UsuarioService(db)
    usuario = service.atualizar_usuario(usuario_id, usuario_in)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """Remove um usuário."""
    service = UsuarioService(db)
    deletado = service.deletar_usuario(usuario_id)
    if not deletado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return None