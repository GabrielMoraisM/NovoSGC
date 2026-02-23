from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.api.deps import get_db, get_current_user
from app.models.contrato import Contrato
from app.models.boletim_medicao import BoletimMedicao, StatusBM
from app.models.faturamento import Faturamento
from app.models.pagamento import Pagamento
from app.services import financeiro_service

router = APIRouter()

@router.get("/resumo")
def get_dashboard_resumo(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retorna indicadores consolidados para o dashboard.
    """
    # Buscar contratos ativos (ou todos, ajuste conforme necessidade)
    contratos = db.query(Contrato).filter(Contrato.status == "ATIVO").all()
    
    total_contratos = len(contratos)
    valor_total_contratado = sum(c.valor_total for c in contratos if c.valor_total)
    
    # Agregar valores executado, faturado e recebido
    valor_executado_total = 0.0
    valor_faturado_total = 0.0
    valor_recebido_total = 0.0
    contratos_recentes = []
    alertas_recentes = []  # mock, ajustar conforme sua lógica de alertas

    for c in contratos:
        resumo = financeiro_service.calcular_resumo_contrato(db, c.id)
        desempenho = financeiro_service.calcular_status_desempenho(db, c.id)
        valor_executado_total += resumo["valor_executado"]
        valor_faturado_total += resumo["valor_faturado"]
        valor_recebido_total += resumo["valor_recebido"]
        
        # Coletar contratos recentes (últimos 5)
        contratos_recentes.append({
            "id": c.id,
            "numero_contrato": c.numero_contrato,
            "nome": c.nome,
            "cliente_nome": c.cliente.nome if c.cliente else None,
            "percentual_fisico": resumo["percentual_fisico"],
            "status_desempenho": desempenho["status_desempenho"]
        })
    
    # Limitar a 5 contratos recentes (ordenados por id decrescente, por exemplo)
    contratos_recentes.sort(key=lambda x: x["id"], reverse=True)
    contratos_recentes = contratos_recentes[:5]

    # Alertas recentes (mock - você pode buscar da sua tabela de alertas)
    alertas_recentes = [
        {
            "tipo": "warning",
            "titulo": "Desequilíbrio Financeiro",
            "mensagem": "CT-2024-003 com variação de 8.5%",
            "data": "Há 2 horas"
        },
        {
            "tipo": "danger",
            "titulo": "Prazo Crítico",
            "mensagem": "CT-2024-004 com atraso de 15 dias",
            "data": "Há 30 minutos"
        }
    ]

    return {
        "total_contratos": total_contratos,
        "valor_total_contratado": round(valor_total_contratado, 2),
        "valor_executado_total": round(valor_executado_total, 2),
        "valor_faturado_total": round(valor_faturado_total, 2),
        "valor_recebido_total": round(valor_recebido_total, 2),
        "percentual_global_fisico": round((valor_executado_total / valor_total_contratado * 100) if valor_total_contratado else 0, 2),
        "percentual_global_recebido": round((valor_recebido_total / valor_total_contratado * 100) if valor_total_contratado else 0, 2),
        "contratos_recentes": contratos_recentes,
        "alertas_recentes": alertas_recentes
    }