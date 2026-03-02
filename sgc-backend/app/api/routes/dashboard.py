from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.api import deps
from app.models.contrato import Contrato
from app.services import financeiro_service
from app.services import projecao_service
from app.schemas.projecao import ProjecaoFinanceiraResponse
from app.models.usuario import Usuario

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/resumo")
def get_dashboard_resumo(
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    Retorna indicadores consolidados para o dashboard (visão global).
    """
    # Busca apenas contratos ativos
    contratos = db.query(Contrato).filter(Contrato.status == "ATIVO").all()
    
    total_contratos = len(contratos)
    valor_total_contratado = sum(c.valor_total or 0 for c in contratos)
    
    valor_executado_total = 0.0
    valor_faturado_total = 0.0
    valor_recebido_total = 0.0
    contratos_recentes = []

    for c in contratos:
        try:
            resumo = financeiro_service.calcular_resumo_contrato(db, c.id)
            desempenho = financeiro_service.calcular_status_desempenho(db, c.id)
        except Exception as e:
            # Log do erro e continua com o próximo contrato
            print(f"Erro ao processar contrato {c.id}: {e}")
            continue

        valor_executado_total += resumo.get("valor_executado", 0.0)
        valor_faturado_total += resumo.get("valor_faturado", 0.0)
        valor_recebido_total += resumo.get("valor_recebido", 0.0)
        
        # Monta o objeto do contrato recente (sem o campo 'nome', que não existe no modelo)
        contratos_recentes.append({
            "id": c.id,
            "numero_contrato": c.numero_contrato,
            "cliente_nome": c.cliente.nome if c.cliente else None,
            "percentual_fisico": resumo.get("percentual_fisico", 0.0),
            "status_desempenho": desempenho.get("status_desempenho", "SEM_PRAZO")
        })
    
    # Ordena por id decrescente e pega os 5 mais recentes
    contratos_recentes.sort(key=lambda x: x["id"], reverse=True)
    contratos_recentes = contratos_recentes[:5]

    # Alertas fixos (pode substituir por consulta real futuramente)
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

    # Cálculo dos percentuais globais
    percentual_fisico = 0.0
    percentual_recebido = 0.0
    if valor_total_contratado > 0:
        percentual_fisico = (valor_executado_total / valor_total_contratado) * 100
        percentual_recebido = (valor_recebido_total / valor_total_contratado) * 100

    return {
        "total_contratos": total_contratos,
        "valor_total_contratado": round(valor_total_contratado, 2),
        "valor_executado_total": round(valor_executado_total, 2),
        "valor_faturado_total": round(valor_faturado_total, 2),
        "valor_recebido_total": round(valor_recebido_total, 2),
        "percentual_global_fisico": round(percentual_fisico, 2),
        "percentual_global_recebido": round(percentual_recebido, 2),
        "contratos_recentes": contratos_recentes,
        "alertas_recentes": alertas_recentes
    }


@router.get("/projecao-global", response_model=ProjecaoFinanceiraResponse)
def get_projecao_global(
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Retorna projeção financeira agregada de todos os contratos ativos.
    Os cálculos são baseados na média dos ritmos individuais.
    """
    try:
        projecao = projecao_service.calcular_projecao_global(db)
        return projecao
    except Exception as e:
        # Em produção, logar o erro real
        print(f"Erro na projeção global: {e}")
        raise HTTPException(status_code=500, detail="Erro ao calcular projeção global")