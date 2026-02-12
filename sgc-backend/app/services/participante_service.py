from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal

from app.repositories.contrato_participante_repo import ContratoParticipanteRepository
from app.repositories.contrato_repo import ContratoRepository
from app.repositories.empresa_repo import EmpresaRepository
from app.schemas.participante import ParticipanteCreate, ParticipanteList
from app.models.contrato_participante import ContratoParticipante

class ParticipanteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContratoParticipanteRepository(db)
        self.contrato_repo = ContratoRepository(db)
        self.empresa_repo = EmpresaRepository(db)

    # ------------------------------------------------------------------
    # OBTER LISTA DE PARTICIPANTES DE UM CONTRATO
    # ------------------------------------------------------------------
    def get_participantes(self, contrato_id: int) -> list[ContratoParticipante]:
        # Verificar se o contrato existe
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )
        return self.repo.get_by_contrato(contrato_id)

    # ------------------------------------------------------------------
    # SUBSTITUIR COMPLETAMENTE A LISTA DE PARTICIPANTES
    # ------------------------------------------------------------------
    def replace_participantes(self, contrato_id: int, participante_list: ParticipanteList) -> list[ContratoParticipante]:
        # 1. Verificar contrato
        contrato = self.contrato_repo.get(contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )

        # 2. Se o contrato não for CONSORCIO ou SCP, não deveria ter participantes
        if contrato.tipo_obra not in ['CONSORCIO', 'SCP'] and participante_list.participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas contratos do tipo CONSORCIO ou SCP podem ter participantes."
            )

        # 3. Validar se as empresas existem e se são elegíveis
        for p in participante_list.participantes:
            empresa = self.empresa_repo.get(p.empresa_id)
            if not empresa:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Empresa ID {p.empresa_id} não encontrada."
                )

            # Se for o líder, pode ser MATRIZ (a própria Heca) ou PARCEIRO_CONSORCIO
            if p.is_lider:
                # Líder: permitir MATRIZ ou PARCEIRO_CONSORCIO
                if empresa.tipo not in ['MATRIZ', 'PARCEIRO_CONSORCIO']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Empresa líder deve ser MATRIZ ou PARCEIRO_CONSORCIO (tipo atual: {empresa.tipo})."
                    )
            else:
                # Participante comum: deve ser PARCEIRO_CONSORCIO ou SCP (depende do tipo de obra)
                if contrato.tipo_obra == 'CONSORCIO':
                    if empresa.tipo != 'PARCEIRO_CONSORCIO':
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Empresa {empresa.razao_social} não é um parceiro de consórcio válido."
                        )
                elif contrato.tipo_obra == 'SCP':
                    if empresa.tipo not in ['PARCEIRO_CONSORCIO', 'SCP']:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Empresa {empresa.razao_social} não é um participante SCP válido."
                        )

        # 4. Remover todos os participantes antigos
        self.repo.delete_by_contrato(contrato_id)

        # 5. Inserir os novos participantes
        novos_participantes = []
        for p in participante_list.participantes:
            novo = ContratoParticipante(
                contrato_id=contrato_id,
                empresa_id=p.empresa_id,
                percentual_participacao=p.percentual_participacao,
                is_lider=p.is_lider
            )
            self.db.add(novo)
            novos_participantes.append(novo)

        # 6. Commit – a trigger será avaliada agora e deve passar
        self.db.commit()

        # 7. Retornar a lista com dados atualizados
        return self.repo.get_by_contrato(contrato_id)