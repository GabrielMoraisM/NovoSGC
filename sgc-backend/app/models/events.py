from decimal import Decimal  
from sqlalchemy import event, select, func
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.aditivo import Aditivo
from app.models.contrato import Contrato
from datetime import timedelta

from app.models import (
    BoletimMedicao,
    Faturamento,
    Pagamento,
    Contrato,
    Aditivo,
    ContratoImposto,
)

# ----------------------------------------------------------------------
# 1. GERAÇÃO AUTOMÁTICA DO NÚMERO SEQUENCIAL DO BOLETIM DE MEDIÇÃO
# ----------------------------------------------------------------------
@event.listens_for(BoletimMedicao, 'before_insert')
def generate_bm_sequencial(mapper, connection, target):
    """
    Define o próximo número sequencial para o BM de um contrato.
    Executado automaticamente antes de inserir um novo registro.
    """
    if target.numero_sequencial is None or target.numero_sequencial == 0:
        result = connection.execute(
            select(func.coalesce(func.max(BoletimMedicao.numero_sequencial), 0) + 1)
            .where(BoletimMedicao.contrato_id == target.contrato_id)
        ).scalar()
        target.numero_sequencial = result
        # Log opcional para debug (pode remover depois)
        print(f"🔢 BM sequencial gerado: {target.numero_sequencial} para contrato {target.contrato_id}")


# ----------------------------------------------------------------------
# 2. CÁLCULO DO VALOR APROVADO DO BOLETIM DE MEDIÇÃO
# ----------------------------------------------------------------------
@event.listens_for(BoletimMedicao, 'before_insert')
@event.listens_for(BoletimMedicao, 'before_update')
def calculate_valor_aprovado(mapper, connection, target):
    """valor_aprovado = valor_total_medido - valor_glosa"""
    target.valor_aprovado = target.valor_total_medido - target.valor_glosa


# ----------------------------------------------------------------------
# 3. IMPEDIR ALTERAÇÃO/DELEÇÃO DE BOLETIM DE MEDIÇÃO COM STATUS FATURADO
# ----------------------------------------------------------------------
@event.listens_for(BoletimMedicao, 'before_update')
def prevent_update_faturado_bm(mapper, connection, target):
    """
    Bloqueia qualquer atualização em BM que já esteja FATURADO.
    O target já contém o estado atual do banco (antes da alteração).
    """
    if target.status == 'FATURADO':
        raise Exception("Boletim de Medição FATURADO não pode ser alterado.")


@event.listens_for(BoletimMedicao, 'before_delete')
def prevent_delete_faturado_bm(mapper, connection, target):
    if target.status == 'FATURADO':
        raise Exception("Boletim de Medição FATURADO não pode ser excluído.")


# ----------------------------------------------------------------------
# 4. FUNÇÃO AUXILIAR: OBTER ALÍQUOTAS DE IMPOSTOS DO CONTRATO (como Decimal)
# ----------------------------------------------------------------------

def obter_aliquotas_contrato(contrato_id: int, session: Session):
    """
    Retorna um dicionário com as alíquotas de impostos configuradas para o contrato.
    Se houver configuração personalizada em contrato_impostos, usa ela.
    Caso contrário, usa os percentuais padrão (convertidos para Decimal).
    """
    # Valores padrão (agora como Decimal)
    padroes = {
        'ISS': Decimal('5.0'),
        'INSS': Decimal('11.0'),
        'IRRF': Decimal('1.5'),
        'CSLL': Decimal('1.0'),
        'PIS': Decimal('0.65'),
        'COFINS': Decimal('3.0'),
    }

    # Busca configurações personalizadas para este contrato
    impostos = session.execute(
        select(ContratoImposto).where(ContratoImposto.contrato_id == contrato_id)
    ).scalars().all()

    # personalizados já são Decimal se o campo do modelo for DECIMAL
    personalizados = {imp.tipo_imposto: imp.aliquota for imp in impostos}

    # Mescla: se existir personalizado, usa; senão, usa padrão
    resultado = {}
    for imposto in padroes:
        resultado[imposto] = personalizados.get(imposto, padroes[imposto])
    return resultado


# ----------------------------------------------------------------------
# 5. CÁLCULO AUTOMÁTICO DO VALOR LÍQUIDO DA NOTA FISCAL (RETENÇÕES)
# ----------------------------------------------------------------------
@event.listens_for(Faturamento, 'before_insert')
@event.listens_for(Faturamento, 'before_update')
def calculate_nf_liquido(mapper, connection, target):
    """
    Calcula as retenções de impostos e o valor líquido da NF.
    As alíquotas são obtidas do contrato vinculado ao BM.
    """
    if not target.bm_id:
        return  # não é possível calcular sem vínculo com BM

    session = Session.object_session(target) or connection
    bm = session.get(BoletimMedicao, target.bm_id)
    if not bm:
        return

    aliquotas = obter_aliquotas_contrato(bm.contrato_id, session)

    # Cálculo das retenções (percentual sobre o valor bruto) - tudo Decimal
    target.iss_retido = target.valor_bruto_nf * (aliquotas['ISS'] / Decimal('100'))
    target.inss_retido = target.valor_bruto_nf * (aliquotas['INSS'] / Decimal('100'))
    target.irrf_retido = target.valor_bruto_nf * (aliquotas['IRRF'] / Decimal('100'))
    target.csll_retido = target.valor_bruto_nf * (aliquotas['CSLL'] / Decimal('100'))
    target.pis_retido = target.valor_bruto_nf * (aliquotas['PIS'] / Decimal('100'))
    target.cofins_retido = target.valor_bruto_nf * (aliquotas['COFINS'] / Decimal('100'))

    total_retencoes = (
        target.iss_retido
        + target.inss_retido
        + target.irrf_retido
        + target.csll_retido
        + target.pis_retido
        + target.cofins_retido
    )
    target.valor_liquido_nf = target.valor_bruto_nf - total_retencoes


# ----------------------------------------------------------------------
# 6. ATUALIZAÇÃO AUTOMÁTICA DO STATUS DA NF COM BASE NOS PAGAMENTOS
# ----------------------------------------------------------------------
def atualiza_status_faturamento(faturamento_id: int, session: Session):
    """Recalcula o status da NF de acordo com o total pago e a data de vencimento."""
    fat = session.get(Faturamento, faturamento_id)
    if not fat:
        return

    total_pago = session.execute(
        select(func.coalesce(func.sum(Pagamento.valor_pago), 0))
        .where(Pagamento.faturamento_id == faturamento_id)
    ).scalar()

    if total_pago >= fat.valor_liquido_nf:
        fat.status = 'QUITADO'
    elif total_pago > 0:
        fat.status = 'PARCIAL'
    elif fat.data_vencimento < date.today():
        fat.status = 'VENCIDO'
    else:
        fat.status = 'PENDENTE'

    session.add(fat)


@event.listens_for(Pagamento, 'after_insert')
@event.listens_for(Pagamento, 'after_update')
@event.listens_for(Pagamento, 'after_delete')
def update_nf_status_after_pagamento(mapper, connection, target):
    """Listener acionado após qualquer operação com pagamento."""
    session = Session.object_session(target) or connection
    atualiza_status_faturamento(target.faturamento_id, session)


# ----------------------------------------------------------------------
# 7. ATUALIZAÇÃO DA DATA FIM PREVISTA DO CONTRATO (COM BASE NOS ADITIVOS)
# ----------------------------------------------------------------------
def recalcula_data_fim_prevista(contrato_id: int, session: Session):
    """Soma os dias de acréscimo dos aditivos e atualiza a data_fim_prevista."""
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        return

    total_dias_acrescimo = session.execute(
        select(func.coalesce(func.sum(Aditivo.dias_acrescimo), 0))
        .where(Aditivo.contrato_id == contrato_id)
    ).scalar()

    dias_totais = contrato.prazo_original_dias + total_dias_acrescimo
    contrato.data_fim_prevista = contrato.data_inicio + timedelta(days=dias_totais)
    session.add(contrato)

# ----------------------------------------------------------------------
# 8. ATUALIZAÇÃO DO CONTRATO COM BASE NOS ADITIVOS
# ----------------------------------------------------------------------
@event.listens_for(Aditivo, 'after_insert')
@event.listens_for(Aditivo, 'after_update')
@event.listens_for(Aditivo, 'after_delete')
def atualizar_contrato_apos_aditivo(mapper, connection, target):
    session = Session.object_session(target) or connection
    contrato_id = target.contrato_id

    # Soma dos dias e valores
    soma_dias = session.query(func.coalesce(func.sum(Aditivo.dias_acrescimo), 0)).filter(Aditivo.contrato_id == contrato_id).scalar()
    soma_valores = session.query(func.coalesce(func.sum(Aditivo.valor_acrescimo), 0)).filter(Aditivo.contrato_id == contrato_id).scalar()

    contrato = session.get(Contrato, contrato_id)
    if contrato:
        dias_totais = contrato.prazo_original_dias + soma_dias
        contrato.data_fim_prevista = contrato.data_inicio + timedelta(days=dias_totais)
        contrato.valor_total = contrato.valor_original + soma_valores
        # Não precisa de session.add(contrato); ele já está na sessão.