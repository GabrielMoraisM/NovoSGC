from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.boletim_medicao_repo import BoletimMedicaoRepository
from app.repositories.contrato_participante_repo import ContratoParticipanteRepository
from app.repositories.faturamento_repo import FaturamentoRepository
from app.repositories.empresa_repo import EmpresaRepository
from app.models.boletim_medicao import BoletimMedicao
from app.models.faturamento import Faturamento
from app.schemas.faturamento import FaturamentoCreate

class RateioService:
    def __init__(self, db: Session):
        self.db = db
        self.boletim_repo = BoletimMedicaoRepository(db)
        self.participante_repo = ContratoParticipanteRepository(db)
        self.faturamento_repo = FaturamentoRepository(db)
        self.empresa_repo = EmpresaRepository(db)

    def ratear_boletim(self, boletim_id: int, empresa_emissora_id: int = 1) -> list[Faturamento]:
        """
        Gera uma nota fiscal para cada participante do consórcio/SCP,
        rateando o valor aprovado do boletim conforme percentual de participação.
        Retorna a lista de faturas criadas.
        """
        # 1. Buscar o boletim
        boletim = self.boletim_repo.get(boletim_id)
        if not boletim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Boletim de Medição não encontrado."
            )

        # 2. Validar status do boletim (deve estar APROVADO)
        if boletim.status != "APROVADO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas boletins APROVADOS podem ser rateados."
            )

        # 3. Validar tipo de obra do contrato
        contrato = boletim.contrato
        if contrato.tipo_obra not in ["CONSORCIO", "SCP"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rateio só é permitido para contratos CONSORCIO ou SCP (tipo atual: {contrato.tipo_obra})."
            )

        # 4. Buscar participantes do contrato
        participantes = self.participante_repo.get_by_contrato(contrato.id)
        if not participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este contrato não possui participantes cadastrados para rateio."
            )

        # 5. Verificar se empresa emissora existe
        emissora = self.empresa_repo.get(empresa_emissora_id)
        if not emissora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa emissora não encontrada."
            )

        # 6. Calcular valor total aprovado (já está no boletim)
        valor_ratear = boletim.valor_aprovado
        if valor_ratear <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor aprovado do boletim é zero ou negativo, não é possível ratear."
            )

        faturas_criadas = []

        # 7. Para cada participante, criar uma fatura
        for part in participantes:
            percentual = part.percentual_participacao
            valor_rateado = (valor_ratear * percentual) / Decimal('100')

            # Dados da NF
            fatura_data = FaturamentoCreate(
                bm_id=boletim.id,
                empresa_emissora_id=empresa_emissora_id,
                cliente_id=part.empresa_id,  # o participante é o tomador (cliente)
                valor_bruto_nf=valor_rateado,
                data_emissao=date.today(),
                data_vencimento=date.today() + timedelta(days=30),
                numero_nf=None,  # será preenchido manualmente ou por integração
                status="PENDENTE"
            )

            # Validação: já existe NF para este BM com esta emissora e este cliente?
            existente = self.db.query(Faturamento).filter(
                Faturamento.bm_id == boletim.id,
                Faturamento.empresa_emissora_id == empresa_emissora_id,
                Faturamento.cliente_id == part.empresa_id
            ).first()
            if existente:
                # Pula silenciosamente? Ou levanta erro? Vamos pular e logar.
                print(f"⚠️ NF já existe para o participante {part.empresa_id}, pulando...")
                continue

            # Criar a fatura (usando o repositório diretamente para evitar commit prematuro)
            fatura_dict = fatura_data.model_dump()
            nova_fatura = self.faturamento_repo.create(**fatura_dict)

            # Força o flush para disparar listeners (cálculo de retenções) e verificar erros
            self.db.flush()

            faturas_criadas.append(nova_fatura)

        # 8. Commit geral (atômico)
        self.db.commit()

        # 9. Refresh nas faturas para obter valores calculados (retenções, valor líquido)
        for fat in faturas_criadas:
            self.db.refresh(fat)

        return faturas_criadas