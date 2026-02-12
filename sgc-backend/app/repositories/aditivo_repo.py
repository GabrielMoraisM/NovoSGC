from sqlalchemy.orm import Session
from app.models.aditivo import Aditivo
from app.repositories.base import BaseRepository

class AditivoRepository(BaseRepository[Aditivo]):
    def __init__(self, db: Session):
        super().__init__(db, Aditivo)

    def get_by_emenda(self, contrato_id: int, numero_emenda: str) -> Aditivo | None:
        return self.db.query(Aditivo).filter(
            Aditivo.contrato_id == contrato_id,
            Aditivo.numero_emenda == numero_emenda
        ).first()