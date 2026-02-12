from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema base (atributos comuns)
class UsuarioBase(BaseModel):
    email: EmailStr
    perfil: str
    ativo: bool = True

# Schema para criação (herda de UsuarioBase e adiciona senha)
class UsuarioCreate(UsuarioBase):
    senha: str

# Schema para atualização (todos os campos opcionais)
class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    perfil: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None

# Schema para resposta (o que a API retorna)
class UsuarioInDB(UsuarioBase):
    id: int

    class Config:
        from_attributes = True  # permite conversão de ORM para Pydantic

# Schema para login (request)
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

# Schema para resposta do login (token)
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"