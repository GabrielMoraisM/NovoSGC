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

    def get_ultimo_sequencial(self, contrato_id: int) -> int:
        """Retorna o maior número sequencial para um contrato (usado pelo listener)."""
        result = self.db.query(BoletimMedicao.numero_sequencial).filter(
            BoletimMedicao.contrato_id == contrato_id
        ).order_by(BoletimMedicao.numero_sequencial.desc()).first()
        return result[0] if result else 0