from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_db, get_current_user

router = APIRouter()

@router.get("/alertas")
def listar_alertas(
    contrato_id: Optional[int] = Query(None, description="Filtrar alertas por contrato"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lista alertas do sistema. Aceita filtro opcional por contrato.
    # TODO: substituir mock por consulta real à tabela de alertas quando disponível.
    """
    # Mock de alertas (substitua pela lógica real posteriormente)
    alertas_mock = [
        {
            "id": 1,
            "tipo": "warning",
            "titulo": "Desequilíbrio Financeiro",
            "mensagem": "Contrato CT-2024-003 com variação de 8.5%",
            "data": datetime.now().isoformat(),
            "contrato_id": 3
        },
        {
            "id": 2,
            "tipo": "danger",
            "titulo": "Prazo Crítico",
            "mensagem": "Contrato CT-2024-004 com atraso de 15 dias",
            "data": datetime.now().isoformat(),
            "contrato_id": 4
        },
        {
            "id": 3,
            "tipo": "info",
            "titulo": "Seguro a Vencer",
            "mensagem": "Renovar seguro do CT-2024-001 em 15 dias",
            "data": datetime.now().isoformat(),
            "contrato_id": 1
        }
    ]

    if contrato_id:
        alertas_mock = [a for a in alertas_mock if a["contrato_id"] == contrato_id]

    return alertas_mock