from sqlalchemy.orm import Session
from app.models.contrato_participante import ContratoParticipante
from app.repositories.base import BaseRepository

class ContratoParticipanteRepository(BaseRepository[ContratoParticipante]):
    def __init__(self, db: Session):
        super().__init__(db, ContratoParticipante)

    def get_by_contrato_empresa(self, contrato_id: int, empresa_id: int) -> ContratoParticipante | None:
        return self.db.query(ContratoParticipante).filter(
            ContratoParticipante.contrato_id == contrato_id,
            ContratoParticipante.empresa_id == empresa_id
        ).first()