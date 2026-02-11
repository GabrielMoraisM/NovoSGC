from sqlalchemy import Column, Integer, Date, DateTime, Enum, DECIMAL, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class BoletimMedicao(Base):
    """
    Registro da medição técnica da obra.
    O número sequencial é gerado automaticamente (via trigger/listener).
    """
    __tablename__ = "boletins_medicao"
    __table_args__ = (
        UniqueConstraint("contrato_id", "numero_sequencial", name="unique_bm_por_contrato"),
        Index("idx_bm_contrato_status", "contrato_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False
    )
    numero_sequencial = Column(Integer, nullable=False)  # será preenchido automaticamente
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    valor_total_medido = Column(DECIMAL(15, 2), nullable=False)
    valor_glosa = Column(DECIMAL(15, 2), default=0, nullable=False)
    valor_aprovado = Column(DECIMAL(15, 2), nullable=True)  # calculado: total - glosa
    status = Column(
        Enum("RASCUNHO", "APROVADO", "FATURADO", "CANCELADO", name="status_bm"),
        default="RASCUNHO",
        nullable=False
    )
    cancelado_motivo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    contrato = relationship("Contrato", back_populates="boletins")
    faturas = relationship("Faturamento", back_populates="bm", cascade="all, delete-orphan")