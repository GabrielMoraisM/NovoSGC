from sqlalchemy.orm import Session
from app.models.contrato import Contrato
from app.repositories.base import BaseRepository

class ContratoRepository(BaseRepository[Contrato]):
    def __init__(self, db: Session):
        super().__init__(db, Contrato)

    def get_by_numero(self, numero: str) -> Contrato | None:
        return self.db.query(Contrato).filter(Contrato.numero_contrato == numero).first()