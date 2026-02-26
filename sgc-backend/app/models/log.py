from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario_email = Column(String(100), nullable=True)
    acao = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, etc.
    entidade = Column(String(50), nullable=False)  # contratos, empresas, etc.
    entidade_id = Column(Integer, nullable=True)
    dados_antigos = Column(JSON, nullable=True)
    dados_novos = Column(JSON, nullable=True)
    ip = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)