from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.api import deps
from app.models.contrato import Contrato
from app.services import financeiro_service
from app.services import projecao_service
from app.services.alerta_service import AlertaService
from app.schemas.projecao import ProjecaoFinanceiraResponse
from app.models.usuario import Usuario
from app.repositories.prateleira_repository import PrateleiraRepository

_SEVERIDADE_TO_TIPO = {
    "critica": "danger",
    "alta":    "danger",
    "media":   "warning",
    "baixa":   "info",
}

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

    # Alertas reais gerados pelo AlertaService (todos os contratos, top 5 por severidade)
    try:
        alerta_svc = AlertaService(db)
        todos_alertas = alerta_svc.gerar_alertas()
        _ordem = {"critica": 0, "alta": 1, "media": 2, "baixa": 3}
        todos_alertas.sort(key=lambda a: _ordem.get(a.get("severidade", "baixa"), 4))
        alertas_recentes = [
            {
                "tipo":     _SEVERIDADE_TO_TIPO.get(a.get("severidade", "media"), "warning"),
                "titulo":   a["titulo"],
                "mensagem": a["mensagem"],
                "data":     "Agora",
            }
            for a in todos_alertas[:5]
        ]
    except Exception as e:
        print(f"Erro ao gerar alertas para dashboard: {e}")
        alertas_recentes = []

    # Cálculo dos percentuais globais
    percentual_fisico = 0.0
    percentual_faturado = 0.0
    percentual_recebido = 0.0
    if valor_total_contratado > 0:
        percentual_fisico   = (valor_executado_total / valor_total_contratado) * 100
        percentual_faturado = (valor_faturado_total  / valor_total_contratado) * 100
        percentual_recebido = (valor_recebido_total  / valor_total_contratado) * 100

    # ── Métricas da Prateleira ───────────────────────────────────
    try:
        prateleira_repo = PrateleiraRepository(db)
        resumo_prateleira = prateleira_repo.get_resumo_global()
    except Exception as e:
        print(f"Erro ao calcular métricas da prateleira: {e}")
        resumo_prateleira = {
            "valor_total_em_prateleira": 0.0,
            "qtd_execucoes_pendentes": 0,
            "qtd_execucoes_aguardando": 0,
            "qtd_execucoes_antigas_30dias": 0,
        }

    return {
        "total_contratos": total_contratos,
        "valor_total_contratado": round(valor_total_contratado, 2),
        "valor_executado_total": round(valor_executado_total, 2),
        "valor_faturado_total": round(valor_faturado_total, 2),
        "valor_recebido_total": round(valor_recebido_total, 2),
        "percentual_global_fisico": round(percentual_fisico, 2),
        "percentual_global_faturado": round(percentual_faturado, 2),
        "percentual_global_recebido": round(percentual_recebido, 2),
        "contratos_recentes": contratos_recentes,
        "alertas_recentes": alertas_recentes,
        # Prateleira
        "valor_total_em_prateleira": round(resumo_prateleira["valor_total_em_prateleira"], 2),
        "qtd_execucoes_prateleira": resumo_prateleira["qtd_execucoes_pendentes"] + resumo_prateleira["qtd_execucoes_aguardando"],
        "execucoes_sem_medicao_30dias": resumo_prateleira["qtd_execucoes_antigas_30dias"],
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