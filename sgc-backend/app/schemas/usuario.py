# app/schemas/usuario.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

# Base - atributos comuns
class UsuarioBase(BaseModel):
    email: EmailStr
    perfil: str
    ativo: bool = True

# Create - usado para criação (senha em texto plano)
class UsuarioCreate(UsuarioBase):
    senha: str

# Update - permite atualização parcial
class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    perfil: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None

# InDB - representa o usuário como está no banco (inclui hash)
class UsuarioInDB(UsuarioBase):
    id: int
    senha_hash: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Response - o que será retornado para o cliente (NUNCA retorna senha_hash)
class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)