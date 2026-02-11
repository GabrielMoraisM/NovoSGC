from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, DECIMAL, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Aditivo(Base):
    """
    Histórico de alterações contratuais (prazo, valor, paralisação).
    """
    __tablename__ = "aditivos"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False
    )
    tipo = Column(
        Enum("PRAZO", "VALOR", "AMBOS", "PARALISACAO", name="tipo_aditivo"),
        nullable=False
    )
    numero_emenda = Column(String(20), nullable=True)
    data_aprovacao = Column(Date, nullable=True)
    dias_acrescimo = Column(Integer, default=0, nullable=False)
    valor_acrescimo = Column(DECIMAL(15, 2), default=0, nullable=False)
    justificativa = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamento
    contrato = relationship("Contrato", back_populates="aditivos")

    __table_args__ = (
        Index("idx_aditivos_contrato_id", "contrato_id"),
    )