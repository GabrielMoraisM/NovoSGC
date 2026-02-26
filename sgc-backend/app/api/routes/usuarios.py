# app/api/routes/usuarios.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.usuario import UsuarioCreate, UsuarioInDB
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=UsuarioInDB, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Cria um novo usuário. Rota pública (não requer autenticação).
    """
    service = UsuarioService(db)
    return service.create_usuario(usuario_in)

@router.get("/me", response_model=UsuarioInDB)
def read_users_me(
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Retorna os dados do usuário atualmente autenticado.
    """
    # O objeto current_user já vem do banco, então podemos retorná-lo diretamente.
    # O Pydantic converterá para UsuarioInDB usando from_attributes.
    return current_user