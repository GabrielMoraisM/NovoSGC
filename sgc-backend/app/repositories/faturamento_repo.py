from sqlalchemy.orm import Session
from app.models.faturamento import Faturamento
from app.repositories.base import BaseRepository

class FaturamentoRepository(BaseRepository[Faturamento]):
    def __init__(self, db: Session):
        super().__init__(db, Faturamento)

    def get_by_numero_nf(self, numero_nf: str) -> Faturamento | None:
        return self.db.query(Faturamento).filter(Faturamento.numero_nf == numero_nf).first()

    def get_by_bm_id(self, bm_id: int) -> list[Faturamento]:
        return self.db.query(Faturamento).filter(Faturamento.bm_id == bm_id).all()