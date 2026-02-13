from sqlalchemy.orm import Session
from app.models.contrato_seguro import ContratoSeguro
from app.repositories.base import BaseRepository

class ContratoSeguroRepository(BaseRepository[ContratoSeguro]):
    def __init__(self, db: Session):
        super().__init__(db, ContratoSeguro)

    def get_by_contrato(self, contrato_id: int) -> list[ContratoSeguro]:
        return self.db.query(ContratoSeguro).filter(ContratoSeguro.contrato_id == contrato_id).all()

    def get_by_apolice(self, numero_apolice: str) -> ContratoSeguro | None:
        return self.db.query(ContratoSeguro).filter(ContratoSeguro.numero_apolice == numero_apolice).first()