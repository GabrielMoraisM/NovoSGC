from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class LogResponse(BaseModel):
    id: int
    usuario_id: Optional[int]
    usuario_email: Optional[str]
    acao: str
    entidade: str
    entidade_id: Optional[int]
    dados_antigos: Optional[Any]
    dados_novos: Optional[Any]
    ip: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True