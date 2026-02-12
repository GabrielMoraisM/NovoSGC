from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import LoginResponse

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    usuario_service = UsuarioService(db)
    usuario = usuario_service.get_usuario_by_email(form_data.username)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(usuario.id)}, expires_delta=access_token_expires
    )
    
    return LoginResponse(access_token=access_token)
