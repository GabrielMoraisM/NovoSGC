# app/repositories/usuario_repo.py

from sqlalchemy.orm import Session
from app.models.usuario import Usuario

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Usuario | None:
        """Retorna um usuário pelo ID."""
        return self.db.query(Usuario).filter(Usuario.id == id).first()

    def get_by_email(self, email: str) -> Usuario | None:
        """Retorna um usuário pelo e-mail."""
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def create(self, **kwargs) -> Usuario:
        """Cria um novo usuário."""
        usuario = Usuario(**kwargs)
        self.db.add(usuario)
        self.db.flush()      # para gerar o id
        self.db.refresh(usuario)
        return usuario

    # Futuramente podemos adicionar update, delete, list, etc.