from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.contrato import ContratoCreate, ContratoInDB, ContratoUpdate
from app.services.contrato_service import ContratoService
from app.models.usuario import Usuario
from app.core.exceptions import BusinessError
from app.services import financeiro_service
from app.api.deps import get_db, get_current_user
from app.schemas.projecao import ProjecaoFinanceiraResponse
from app.services import projecao_service
from app.schemas.analise_ritmo import AnaliseRitmoResponse
from app.services import analise_ritmo_service
from app.models.contrato_imposto import ContratoImposto
from app.schemas.contrato_imposto import ContratoImpostoInDB, ContratoImpostosBulkSet



router = APIRouter()

# ----------------------------------------------------------------------
# POST /contratos/
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# GET /contratos/
# ----------------------------------------------------------------------
@router.get("/", response_model=List[ContratoInDB])
def list_contratos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Listar contratos com paginação."""
    service = ContratoService(db)
    return service.list_contratos(skip=skip, limit=limit)


# ----------------------------------------------------------------------
# GET /contratos/{id}
# ----------------------------------------------------------------------
@router.get("/{contrato_id}", response_model=ContratoInDB)
def get_contrato(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de um contrato pelo ID."""
    service = ContratoService(db)
    return service.get_contrato(contrato_id)


# ----------------------------------------------------------------------
# PUT /contratos/{id}
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# DELETE /contratos/{id}
# ----------------------------------------------------------------------


@router.get("/{contrato_id}/resumo-financeiro")
def get_resumo_financeiro_contrato(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna o resumo financeiro completo de um contrato específico.
    """
    try:
        resumo = financeiro_service.calcular_resumo_contrato(db, contrato_id)
        desempenho = financeiro_service.calcular_status_desempenho(db, contrato_id)
        return {**resumo, **desempenho}
    except BusinessError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log do erro e retorne apenas o resumo (ou um erro amigável)
        print(f"Erro ao calcular desempenho: {e}")
        return {**resumo, "status_desempenho": "ERRO"}
    


@router.post("/", response_model=ContratoInDB, status_code=status.HTTP_201_CREATED)
def create_contrato(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    contrato_in: ContratoCreate,
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoService(db)
    return service.create_contrato(contrato_in, current_user=current_user, request=request)




@router.put("/{contrato_id}", response_model=ContratoInDB)
def update_contrato(
    contrato_id: int,
    contrato_in: ContratoUpdate,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoService(db)
    return service.update_contrato(contrato_id, contrato_in, current_user=current_user, request=request)


@router.delete("/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contrato(
    contrato_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    service = ContratoService(db)
    service.delete_contrato(contrato_id, current_user=current_user, request=request)
    return None

@router.get("/{contrato_id}/projecao-financeira", response_model=ProjecaoFinanceiraResponse)
def get_projecao_financeira_contrato(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Retorna projeção financeira para um contrato específico.
    - **ritmo_medio_mensal**: valor médio executado por mês (R$)
    - **saldo_a_executar**: valor restante a executar (R$)
    - **previsao_termino**: data estimada de término (dd/mm/aaaa)
    - **faturamento_30d/60d/90d**: projeção de faturamento para os próximos meses
    """
    try:
        projecao = projecao_service.calcular_projecao_contrato(db, contrato_id)
        return projecao
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao calcular projeção")
    

@router.get("/{contrato_id}/analise-ritmo", response_model=AnaliseRitmoResponse)
def get_analise_ritmo(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    try:
        return analise_ritmo_service.calcular_analise_ritmo(db, contrato_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao calcular análise de ritmo")


# ----------------------------------------------------------------------
# GET /contratos/{id}/impostos  — lista as alíquotas configuradas
# ----------------------------------------------------------------------
@router.get("/{contrato_id}/impostos", response_model=List[ContratoImpostoInDB])
def listar_impostos_contrato(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Retorna os impostos configurados para um contrato (lista vazia = não configurado)."""
    return db.query(ContratoImposto).filter(
        ContratoImposto.contrato_id == contrato_id
    ).all()


# ----------------------------------------------------------------------
# PUT /contratos/{id}/impostos  — substitui todos os impostos de uma vez
# ----------------------------------------------------------------------
@router.put("/{contrato_id}/impostos", response_model=List[ContratoImpostoInDB])
def configurar_impostos_contrato(
    contrato_id: int,
    body: ContratoImpostosBulkSet,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """
    Configura (substitui) os impostos de um contrato.
    Apaga todos os registros anteriores e insere os novos fornecidos.
    """
    # Verificar se o contrato existe
    service = ContratoService(db)
    service.get_contrato(contrato_id)  # lança HTTPException 404 se não encontrar

    # Remover impostos existentes
    db.query(ContratoImposto).filter(
        ContratoImposto.contrato_id == contrato_id
    ).delete(synchronize_session='fetch')

    # Inserir novos
    novos = [
        ContratoImposto(
            contrato_id=contrato_id,
            tipo_imposto=imp.tipo_imposto,
            aliquota=imp.aliquota,
            base_calculo=imp.base_calculo,
        )
        for imp in body.impostos
    ]
    db.add_all(novos)
    db.commit()
    for n in novos:
        db.refresh(n)
    return novos