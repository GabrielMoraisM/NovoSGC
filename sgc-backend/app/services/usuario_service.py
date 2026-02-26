# app/services/usuario_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import UsuarioCreate
from app.core.security import get_password_hash, verify_password

class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def create_usuario(self, usuario_in: UsuarioCreate):
        # Verificar se email já existe
        if self.repo.get_by_email(usuario_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        # Preparar dados para criação (substituir senha por hash)
        usuario_data = usuario_in.dict()
        usuario_data['senha_hash'] = get_password_hash(usuario_data.pop('senha'))
        return self.repo.create(**usuario_data)

    def get_usuario_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def get_usuario(self, usuario_id: int):
        return self.repo.get(usuario_id)

    def authenticate(self, email: str, password: str):
        usuario = self.repo.get_by_email(email)
        if not usuario:
            return None
        if not verify_password(password, usuario.senha_hash):
            return None
        return usuario