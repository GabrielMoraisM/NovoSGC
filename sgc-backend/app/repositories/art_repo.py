from sqlalchemy.orm import Session
from app.models.contrato_art import ContratoArt
from app.repositories.base import BaseRepository

class ArtRepository(BaseRepository[ContratoArt]):
    def __init__(self, db: Session):
        super().__init__(db, ContratoArt)

    def get_by_contrato(self, contrato_id: int) -> list[ContratoArt]:
        return self.db.query(ContratoArt).filter(ContratoArt.contrato_id == contrato_id).all()