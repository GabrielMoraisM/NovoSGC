from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.participante import ParticipanteInDB, ParticipanteList
from app.services.participante_service import ParticipanteService
from app.models.usuario import Usuario

router = APIRouter()

# ----------------------------------------------------------------------
# GET /contratos/{contrato_id}/participantes
# ----------------------------------------------------------------------
@router.get("/contratos/{contrato_id}/participantes", response_model=List[ParticipanteInDB])
def get_participantes(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Lista todos os participantes de um contrato."""
    service = ParticipanteService(db)
    participantes = service.get_participantes(contrato_id)
    # Enriquecer com nome da empresa (opcional)
    result = []
    for p in participantes:
        p_dict = p.__dict__.copy()
        p_dict["empresa_nome"] = p.empresa.razao_social if p.empresa else None
        result.append(ParticipanteInDB.model_validate(p_dict))
    return result


# ----------------------------------------------------------------------
# PUT /contratos/{contrato_id}/participantes
# ----------------------------------------------------------------------
@router.put("/contratos/{contrato_id}/participantes", response_model=List[ParticipanteInDB])
def replace_participantes(
    contrato_id: int,
    participante_list: ParticipanteList,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Substitui completamente a lista de participantes de um contrato."""
    service = ParticipanteService(db)
    participantes = service.replace_participantes(contrato_id, participante_list)
    # Enriquecer com nome da empresa
    result = []
    for p in participantes:
        p_dict = p.__dict__.copy()
        p_dict["empresa_nome"] = p.empresa.razao_social if p.empresa else None
        result.append(ParticipanteInDB.model_validate(p_dict))
    return result


# ----------------------------------------------------------------------
# DELETE /contratos/{contrato_id}/participantes
# ----------------------------------------------------------------------
@router.delete("/contratos/{contrato_id}/participantes", status_code=status.HTTP_204_NO_CONTENT)
def delete_participantes(
    contrato_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user)
):
    """Remove todos os participantes de um contrato (útil para converter para HECA_100)."""
    service = ParticipanteService(db)
    # Para remover, basta enviar uma lista vazia
    service.replace_participantes(contrato_id, ParticipanteList(participantes=[]))
    return None