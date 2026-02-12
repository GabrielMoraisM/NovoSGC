from sqlalchemy.orm import Session
from app.models.empresa import Empresa
from app.repositories.base import BaseRepository

class EmpresaRepository(BaseRepository[Empresa]):
    def __init__(self, db: Session):
        super().__init__(db, Empresa)

    def get_by_cnpj(self, cnpj: str) -> Empresa | None:
        return self.db.query(Empresa).filter(Empresa.cnpj == cnpj).first()