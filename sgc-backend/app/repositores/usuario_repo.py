# app/repositories/usuario_repo.py
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate

class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    def __init__(self, db: Session):
        super().__init__(db, Usuario)

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()