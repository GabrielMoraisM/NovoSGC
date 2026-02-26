# app/models/usuario.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)          # Nome completo do usuário
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)    # Hash da senha
    perfil = Column(String(50), nullable=False)         # ADMIN, GESTOR, FINANCEIRO, AUDITOR, TI
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Usuario {self.email}>"
    contratos = relationship("UsuarioContrato", back_populates="usuario", cascade="all, delete-orphan")