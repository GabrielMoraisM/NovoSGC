from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class ContratoArt(Base):
    """
    Responsáveis técnicos (ARTs) vinculados ao contrato.
    """
    __tablename__ = "contrato_arts"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False
    )
    nome_profissional = Column(String(100), nullable=False)
    numero_art = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamento
    contrato = relationship("Contrato", back_populates="arts")