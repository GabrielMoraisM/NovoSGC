from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base

class UsuarioContrato(Base):
    """
    Associa usuários aos contratos que eles podem visualizar.
    Usado exclusivamente para as políticas de Row Level Security (RLS).
    """
    __tablename__ = "usuario_contratos"
    __table_args__ = (
        PrimaryKeyConstraint("usuario_id", "contrato_id"),
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )
    contrato_id = Column(
        Integer,
        ForeignKey("contratos.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="contratos")
    contrato = relationship("Contrato", back_populates="usuarios")