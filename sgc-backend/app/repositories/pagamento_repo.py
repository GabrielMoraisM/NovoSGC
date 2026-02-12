from sqlalchemy.orm import Session
from app.models.pagamento import Pagamento
from app.repositories.base import BaseRepository

class PagamentoRepository(BaseRepository[Pagamento]):
    def __init__(self, db: Session):
        super().__init__(db, Pagamento)

    def get_by_faturamento(self, faturamento_id: int) -> list[Pagamento]:
        return self.db.query(Pagamento).filter(
            Pagamento.faturamento_id == faturamento_id
        ).all()