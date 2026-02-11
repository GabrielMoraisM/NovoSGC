from sqlalchemy import Column, Integer, DECIMAL, Boolean, ForeignKey, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base

class ContratoParticipante(Base):
    """
    Define a composição de consórcios ou SCPs.
    A soma dos percentuais deve ser 100% (garantido por trigger no banco).
    """
    __tablename__ = "contrato_participantes"
    __table_args__ = (
        PrimaryKeyConstraint("contrato_id", "empresa_id"),
        CheckConstraint(
            "percentual_participacao >= 0 AND percentual_participacao <= 100",
            name="check_percentual_range"
        ),
    )

    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False
    )
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False
    )
    percentual_participacao = Column(DECIMAL(5, 2), nullable=False)
    is_lider = Column(Boolean, default=False, nullable=False)

    # Relacionamentos
    contrato = relationship("Contrato", back_populates="participantes")
    empresa = relationship("Empresa", back_populates="participacoes")