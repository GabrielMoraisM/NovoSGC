from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class ContratoSeguro(Base):
    """
    Garantias e apólices de seguro vinculadas ao contrato.
    """
    __tablename__ = "contrato_seguros"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False
    )
    seguradora_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="RESTRICT"),
        nullable=False
    )
    tipo = Column(
        Enum("GARANTIA_CONTRATUAL", "RISCO_ENGENHARIA", "RC", name="tipo_seguro"),
        nullable=False
    )
    numero_apolice = Column(String(50), nullable=True)
    data_vencimento = Column(Date, nullable=False)
    valor = Column(DECIMAL(15, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    contrato = relationship("Contrato", back_populates="seguros")
    seguradora = relationship("Empresa", foreign_keys=[seguradora_id])