# app/schemas/projecao.py
from pydantic import BaseModel
from typing import Optional

class ProjecaoFinanceiraResponse(BaseModel):
    """
    Schema de resposta para projeções financeiras.
    Utilizado tanto para projeção de um contrato específico quanto para a visão global.
    """
    ritmo_medio_mensal: float
    """Valor médio executado por mês (R$) com base nos últimos 3 meses."""

    saldo_a_executar: float
    """Valor total que ainda falta executar no contrato (R$)."""

    previsao_termino: Optional[str] = None
    """Data prevista para término do contrato no formato dd/mm/aaaa.
       Pode ser nulo se não houver dados suficientes para calcular."""

    faturamento_30d: float
    """Projeção de faturamento para os próximos 30 dias (R$)."""

    faturamento_60d: float
    """Projeção de faturamento para os próximos 60 dias (R$)."""

    faturamento_90d: float
    """Projeção de faturamento para os próximos 90 dias (R$)."""

    class Config:
        from_attributes = True