from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # <-- ESTA LINHA ESTAVA FALTANDO

from app.db.base import Base

class Usuario(Base):
    """
    Armazena credenciais e perfis de acesso.
    """
    __tablename__ = "usuarios"

    # Identificador único, auto-incremento (SERIAL no PostgreSQL)
    id = Column(Integer, primary_key=True, index=True)

    # E-mail único, usado para login. Indexado para buscas rápidas.
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Hash da senha (bcrypt) – nunca armazenamos a senha em texto plano.
    senha_hash = Column(String(255), nullable=False)

    # Perfil do usuário (controla permissões). ENUM do PostgreSQL.
    perfil = Column(
        Enum("ADMIN", "GESTOR", "FINANCEIRO", "AUDITOR", name="perfil"),
        nullable=False
    )

    # Soft delete: se False, usuário está desativado, mas registro permanece.
    ativo = Column(Boolean, default=True, nullable=False)

    # Timestamps de criação e atualização automáticos.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Futuramente: relacionamento com UsuarioContrato
    # contratos = relationship("UsuarioContrato", back_populates="usuario")
    # Relacionamento com UsuarioContrato (para RLS)
    contratos = relationship("UsuarioContrato", back_populates="usuario", cascade="all, delete-orphan")