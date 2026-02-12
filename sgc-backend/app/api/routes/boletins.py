from typing import List
from fastapi import APIRouter, Depends, status, Query  # <-- ADICIONE Query
from sqlalchemy.orm import Session

from app.services.rateio_service import RateioService
from app.schemas.rateio import RateioResponse

from app.api import deps
from app.schemas.boletim import BoletimCreate, BoletimInDB, BoletimUpdate
from app.services.boletim_service import BoletimService
from app.models.usuario import Usuario
from app.repositories.boletim_medicao_repo import BoletimMedicaoRepository

router = APIRouter()

# ----------------------------------------------------------------------
# POST /contratos/{contrato_id}/boletins
# ----------------------------------------------------------------------
@router.post("/contratos/{contrato_id}/boletins", response_model=BoletimInDB, status_code=status.HTTP_201_CREATED)
def create_boletim(
    contrato_id: int,
    boletim_in: BoletimCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Criar um novo boletim de medição para um contrato."""
    boletim_in.contrato_id = contrato_id
    service = BoletimService(db)
    return service.create_boletim(boletim_in)


# ----------------------------------------------------------------------
# GET /contratos/{contrato_id}/boletins
# ----------------------------------------------------------------------
@router.get("/contratos/{contrato_id}/boletins", response_model=List[BoletimInDB])
def list_boletins_por_contrato(
    contrato_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Listar todos os boletins de um contrato, ordenados por número sequencial."""
    service = BoletimService(db)
    return service.list_boletins_por_contrato(contrato_id, skip=skip, limit=limit)


# ----------------------------------------------------------------------
# GET /boletins/{boletim_id}
# ----------------------------------------------------------------------
@router.get("/boletins/{boletim_id}", response_model=BoletimInDB)
def get_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Obter detalhes de um boletim pelo ID."""
    service = BoletimService(db)
    return service.get_boletim(boletim_id)


# ----------------------------------------------------------------------
# PUT /boletins/{boletim_id}
# ----------------------------------------------------------------------
@router.put("/boletins/{boletim_id}", response_model=BoletimInDB)
def update_boletim(
    boletim_id: int,
    boletim_in: BoletimUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Atualizar dados de um boletim. Não permitido se status for FATURADO."""
    service = BoletimService(db)
    return service.update_boletim(boletim_id, boletim_in)


# ----------------------------------------------------------------------
# DELETE /boletins/{boletim_id}
# ----------------------------------------------------------------------
@router.delete("/boletins/{boletim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remover um boletim. Não permitido se status for FATURADO ou se houver faturas."""
    service = BoletimService(db)
    service.delete_boletim(boletim_id)
    return None


# ----------------------------------------------------------------------
# POST /boletins/{boletim_id}/aprovar (Endpoint específico para ação)
# ----------------------------------------------------------------------
@router.post("/boletins/{boletim_id}/aprovar", response_model=BoletimInDB)
def aprovar_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Alterar status do boletim para APROVADO."""
    service = BoletimService(db)
    return service.update_boletim(boletim_id, BoletimUpdate(status="APROVADO"))


# ----------------------------------------------------------------------
# POST /boletins/{boletim_id}/cancelar (Endpoint específico para ação)
# ----------------------------------------------------------------------
@router.post("/boletins/{boletim_id}/cancelar", response_model=BoletimInDB)
def cancelar_boletim(
    boletim_id: int,
    motivo: str,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Cancelar um boletim com motivo obrigatório."""
    service = BoletimService(db)
    return service.update_boletim(
        boletim_id,
        BoletimUpdate(status="CANCELADO", cancelado_motivo=motivo)
    )

@router.post("/{boletim_id}/ratear", response_model=RateioResponse)
def ratear_boletim(
    boletim_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user),
    empresa_emissora_id: int = Query(1, description="ID da empresa que emitirá as NFs (padrão: Heca)")
):
    """
    Rateia o valor do boletim aprovado entre os participantes do consórcio/SCP
    e gera uma nota fiscal para cada um.
    """
    service = RateioService(db)
    faturas = service.ratear_boletim(boletim_id, empresa_emissora_id)

    # Obtém o boletim diretamente do serviço (já foi carregado)
    boletim_repo = BoletimMedicaoRepository(db)
    boletim = boletim_repo.get(boletim_id)

    return RateioResponse(
        boletim_id=boletim_id,
        contrato_id=boletim.contrato_id,
        participantes_rateados=len(faturas),
        faturas_geradas=faturas
    )