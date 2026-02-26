# app/api/deps.py

from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.rls import set_current_user_id
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db() -> Generator[Session, None, None]:
    """
    Dependência que fornece uma sessão do banco de dados.
    A sessão é fechada automaticamente após a requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> Usuario:
    """
    Valida o token JWT e retorna o usuário atual.
    Também define a variável de sessão para o RLS.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError, TypeError):
        raise credentials_exception
    
    usuario_service = UsuarioService(db)
    usuario = usuario_service.get_usuario(user_id)
    if usuario is None:
        raise credentials_exception
    
    # 🔐 Define a variável de sessão para o RLS (PostgreSQL)
    set_current_user_id(db, usuario.id)
    
    return usuario

async def get_current_active_user(
    current_user: Annotated[Usuario, Depends(get_current_user)]
) -> Usuario:
    """Verifica se o usuário atual está ativo."""
    if not current_user.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user