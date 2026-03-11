from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Arquivo(Base):
    __tablename__ = "arquivos"
    __table_args__ = (
        Index("ix_arquivos_entidade", "entidade_tipo", "entidade_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nome_original = Column(String(255), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)   # stored as uuid + extension
    caminho = Column(String(500), nullable=False)        # full path on disk
    tamanho = Column(Integer, nullable=True)             # bytes
    tipo_mime = Column(String(100), nullable=True)

    entidade_tipo = Column(
        Enum("contrato", "boletim", "faturamento", "pagamento", name="entidade_tipo_arquivo"),
        nullable=False
    )
    entidade_id = Column(Integer, nullable=False)

    descricao = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    usuario = relationship("Usuario")
