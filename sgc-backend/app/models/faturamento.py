from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, DECIMAL, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Faturamento(Base):
    """
    Nota Fiscal emitida a partir de um Boletim de Medição.
    Inclui retenções de impostos e valor líquido.
    """
    __tablename__ = "faturamentos"
    __table_args__ = (
        Index("idx_faturamento_bm_id", "bm_id"),
        Index("idx_faturamento_status_vencimento", "status", "data_vencimento"),
    )

    id = Column(Integer, primary_key=True, index=True)
    bm_id = Column(
        Integer,
        ForeignKey("boletins_medicao.id", ondelete="RESTRICT"),
        nullable=False
    )
    numero_nf = Column(String(30), nullable=True)
    empresa_emissora_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="RESTRICT"),
        nullable=False
    )
    cliente_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="RESTRICT"),
        nullable=False
    )
    valor_bruto_nf = Column(DECIMAL(15, 2), nullable=False)
    valor_liquido_nf = Column(DECIMAL(15, 2), nullable=False)  # calculado via listener
    iss_retido = Column(DECIMAL(15, 2), default=0, nullable=False)
    inss_retido = Column(DECIMAL(15, 2), default=0, nullable=False)
    irrf_retido = Column(DECIMAL(15, 2), default=0, nullable=False)
    csll_retido = Column(DECIMAL(15, 2), default=0, nullable=False)
    pis_retido = Column(DECIMAL(15, 2), default=0, nullable=False)
    cofins_retido = Column(DECIMAL(15, 2), default=0, nullable=False)
    data_emissao = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    status = Column(
        Enum("PENDENTE", "PARCIAL", "QUITADO", "CANCELADO", "VENCIDO", name="status_nf"),
        default="PENDENTE",
        nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    bm = relationship("BoletimMedicao", back_populates="faturas")
    empresa_emissora = relationship("Empresa", foreign_keys=[empresa_emissora_id])
    cliente = relationship("Empresa", foreign_keys=[cliente_id])
    pagamentos = relationship("Pagamento", back_populates="faturamento", cascade="all, delete-orphan")