from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ArquivoInDB(BaseModel):
    id: int
    nome_original: str
    tamanho: Optional[int] = None
    tipo_mime: Optional[str] = None
    entidade_tipo: str
    entidade_id: int
    descricao: Optional[str] = None
    created_at: datetime
    url_download: Optional[str] = None  # populated by route

    class Config:
        from_attributes = True
