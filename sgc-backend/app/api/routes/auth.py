from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api import deps
from app.core.security import create_access_token
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import LoginResponse, UsuarioInDB

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    service = UsuarioService(db)
    usuario = service.authenticate(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Criar token de acesso
    access_token_expires = timedelta(minutes=30)  # usar settings
    access_token = create_access_token(
        data={"sub": str(usuario.id)}, expires_delta=access_token_expires
    )
    # Retornar token e dados do usuário
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=UsuarioInDB.from_orm(usuario)
    )