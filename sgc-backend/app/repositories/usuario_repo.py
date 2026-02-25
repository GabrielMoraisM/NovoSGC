from sqlalchemy.orm import Session
from app.models.usuario import Usuario

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def create(self, **kwargs):
        usuario = Usuario(**kwargs)
        self.db.add(usuario)
        self.db.flush()
        self.db.refresh(usuario)
        return usuario