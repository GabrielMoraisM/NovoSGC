# app/schemas/usuario.py

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

# Schema base com campos comuns
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    perfil: str  # ADMIN, GESTOR, FINANCEIRO, AUDITOR, TI
    ativo: Optional[bool] = True

# Schema para criação de usuário (inclui senha)
class UsuarioCreate(UsuarioBase):
    senha: str

# Schema para atualização (todos opcionais)
class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    perfil: Optional[str] = None
    ativo: Optional[bool] = None

# Schema para resposta (inclui id, timestamps e validação extra)
class UsuarioInDB(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Validador para garantir que id seja inteiro (caso venha string do banco)
    @validator('id', pre=True)
    def validate_id(cls, v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return v  # mantém original se falhar, mas normalmente será int

    class Config:
        from_attributes = True  # permite conversão de objetos SQLAlchemy

# Schema para resposta do login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # Opcional: incluir dados do usuário para facilitar no frontend
    usuario: Optional[UsuarioInDB] = None