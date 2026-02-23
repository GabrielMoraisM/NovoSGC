from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.schemas.contrato import ContratoResponse, ContratoResumoFinanceiro
from app.services import financeiro_service
from app.repositories.contrato_repository import ContratoRepository
from app.core.exceptions import BusinessError

router = APIRouter()

@router.get("/", response_model=List[ContratoResponse])
def listar_contratos(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    incluir_resumo: bool = Query(False, description="Inclui indicadores financeiros e de progresso"),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    cliente_id: Optional[int] = None
):
    """
    Lista contratos com opção de incluir resumo financeiro.
    """
    repo = ContratoRepository(db)
    contratos = repo.listar(
        skip=skip,
        limit=limit,
        status=status,
        cliente_id=cliente_id
    )
    
    if incluir_resumo:
        # Enriquece cada contrato com os indicadores
        resultado = []
        for contrato in contratos:
            try:
                resumo = financeiro_service.calcular_resumo_contrato(db, contrato.id)
                desempenho = financeiro_service.calcular_status_desempenho(db, contrato.id)
                # Converte o contrato para dict e adiciona os novos campos
                contrato_dict = {
                    "id": contrato.id,
                    "numero": contrato.numero,
                    "nome": contrato.nome,
                    "cliente_id": contrato.cliente_id,
                    "cliente_nome": contrato.cliente.nome if contrato.cliente else None,
                    "valor_total": contrato.valor_total,
                    "data_inicio": contrato.data_inicio,
                    "data_fim": contrato.data_fim,
                    "status": contrato.status,
                    "tipo": contrato.tipo,
                    # Campos do resumo
                    "valor_executado": resumo["valor_executado"],
                    "valor_faturado": resumo["valor_faturado"],
                    "valor_recebido": resumo["valor_recebido"],
                    "percentual_fisico": resumo["percentual_fisico"],
                    "percentual_financeiro": resumo["percentual_financeiro"],
                    "saldo_contratual": resumo["saldo_contratual"],
                    "saldo_a_faturar": resumo["saldo_a_faturar"],
                    "saldo_a_receber": resumo["saldo_a_receber"],
                    # Desempenho
                    "percentual_tempo": desempenho["percentual_tempo"],
                    "status_desempenho": desempenho["status_desempenho"],
                    "dias_decorridos": desempenho["dias_decorridos"],
                    "dias_totais": desempenho["dias_totais"],
                }
                resultado.append(contrato_dict)
            except BusinessError:
                # Se não for possível calcular (ex: sem datas), retorna sem resumo
                contrato_dict = {
                    "id": contrato.id,
                    "numero": contrato.numero,
                    "nome": contrato.nome,
                    "cliente_id": contrato.cliente_id,
                    "cliente_nome": contrato.cliente.nome if contrato.cliente else None,
                    "valor_total": contrato.valor_total,
                    "data_inicio": contrato.data_inicio,
                    "data_fim": contrato.data_fim,
                    "status": contrato.status,
                    "tipo": contrato.tipo,
                    "status_desempenho": "SEM_PRAZO"
                }
                resultado.append(contrato_dict)
        return resultado
    else:
        return contratos


@router.get("/{contrato_id}/resumo-financeiro")
def get_resumo_financeiro_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna o resumo financeiro completo de um contrato específico.
    Útil para o dashboard ou para detalhamento.
    """
    try:
        resumo = financeiro_service.calcular_resumo_contrato(db, contrato_id)
        desempenho = financeiro_service.calcular_status_desempenho(db, contrato_id)
        return {**resumo, **desempenho}
    except BusinessError as e:
        raise HTTPException(status_code=400, detail=str(e))