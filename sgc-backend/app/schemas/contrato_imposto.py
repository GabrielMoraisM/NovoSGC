from decimal import Decimal
from typing import List

from pydantic import BaseModel


class ContratoImpostoCreate(BaseModel):
    tipo_imposto: str               # "ISS", "INSS", "IRRF", "CSLL", "PIS", "COFINS"
    aliquota: Decimal               # ex: 5.00 → 5%
    base_calculo: str = "BRUTO"    # "BRUTO" ou "LIQUIDO"


class ContratoImpostoInDB(ContratoImpostoCreate):
    contrato_id: int

    class Config:
        from_attributes = True


class ContratoImpostosBulkSet(BaseModel):
    """Substituição total dos impostos de um contrato (delete + insert)."""
    impostos: List[ContratoImpostoCreate]
