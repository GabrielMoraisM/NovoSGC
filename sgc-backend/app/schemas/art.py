from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArtBase(BaseModel):
    nome_profissional: str
    numero_art: str

class ArtCreate(ArtBase):
    contrato_id: int

class ArtUpdate(BaseModel):
    nome_profissional: Optional[str] = None
    numero_art: Optional[str] = None

class ArtInDB(ArtBase):
    id: int
    contrato_id: int
    created_at: datetime

    class Config:
        from_attributes = True