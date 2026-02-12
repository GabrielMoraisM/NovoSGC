from pydantic import BaseModel, constr, validator
from typing import Optional
from datetime import datetime

# ----------------------------------------------------------------------
# SCHEMA BASE (atributos comuns a todos os schemas)
# ----------------------------------------------------------------------
class EmpresaBase(BaseModel):
    razao_social: str
    cnpj: constr(min_length=14, max_length=18)
    tipo: str  # 'MATRIZ', 'FILIAL', 'PARCEIRO_CONSORCIO', 'SCP', 'CLIENTE'

    @validator('cnpj')
    def validate_cnpj(cls, v):
        """Remove caracteres não numéricos e valida tamanho."""
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) != 14:
            raise ValueError('CNPJ deve conter 14 dígitos')
        return cleaned  # ou retorne formatado, se preferir

# ----------------------------------------------------------------------
# SCHEMA PARA CRIAÇÃO (POST)
# ----------------------------------------------------------------------
class EmpresaCreate(EmpresaBase):
    pass  # herda todos os campos, sem acréscimos

# ----------------------------------------------------------------------
# SCHEMA PARA ATUALIZAÇÃO (PUT/PATCH)
# ----------------------------------------------------------------------
class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = None
    cnpj: Optional[constr(min_length=14, max_length=18)] = None
    tipo: Optional[str] = None

    @validator('cnpj')
    def validate_cnpj(cls, v):
        if v is None:
            return v
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) != 14:
            raise ValueError('CNPJ deve conter 14 dígitos')
        return cleaned

# ----------------------------------------------------------------------
# SCHEMA PARA RESPOSTA (GET) – contém campos do banco
# ----------------------------------------------------------------------
class EmpresaInDB(EmpresaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # permite conversão de ORM para Pydantic