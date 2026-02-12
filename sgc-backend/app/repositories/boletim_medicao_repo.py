from sqlalchemy.orm import Session
from app.models.boletim_medicao import BoletimMedicao
from app.repositories.base import BaseRepository

class BoletimMedicaoRepository(BaseRepository[BoletimMedicao]):
    def __init__(self, db: Session):
        super().__init__(db, BoletimMedicao)

    def get_by_contrato_sequencial(self, contrato_id: int, numero_sequencial: int) -> BoletimMedicao | None:
        return self.db.query(BoletimMedicao).filter(
            BoletimMedicao.contrato_id == contrato_id,
            BoletimMedicao.numero_sequencial == numero_sequencial
        ).first()