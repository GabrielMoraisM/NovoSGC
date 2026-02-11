from sqlalchemy import event, func, select, and_
from sqlalchemy.orm import Session
from app.models.models import (
    BoletimMedicao, Faturamento, Pagamento, Contrato,
    ContratoParticipante, Aditivo, UsuarioContrato
)
from datetime import date

# ------------------------------------------------------------
# 1. Geração automática do número sequencial do BM (RN01)
# ------------------------------------------------------------
@event.listens_for(BoletimMedicao, 'before_insert')
def generate_bm_sequencial(mapper, connection, target):
    """Calcula o próximo número sequencial para o contrato."""
    if target.numero_sequencial is None or target.numero_sequencial == 0:
        # Usa connection (nível de sessão) para evitar consulta suja
        result = connection.execute(
            select(func.coalesce(func.max(BoletimMedicao.numero_sequencial), 0) + 1)
            .where(BoletimMedicao.contrato_id == target.contrato_id)
        ).scalar()
        target.numero_sequencial = result


# ------------------------------------------------------------
# 2. Imutabilidade do BM com status FATURADO (RN05)
# ------------------------------------------------------------
@event.listens_for(BoletimMedicao, 'before_update')
def prevent_update_faturado_bm(mapper, connection, target):
    """Impede qualquer atualização em BM já faturado."""
    # Obtém o estado antigo (necessário para verificar mudança de status)
    state = mapper.attrs.status.history.from_instance(target)
    if state and state[0] and state[0][0] == 'FATURADO':
        raise Exception("Boletim de Medição FATURADO não pode ser alterado.")

@event.listens_for(BoletimMedicao, 'before_delete')
def prevent_delete_faturado_bm(mapper, connection, target):
    """Impede deleção de BM faturado."""
    if target.status == 'FATURADO':
        raise Exception("Boletim de Medição FATURADO não pode ser excluído.")


# ------------------------------------------------------------
# 3. Cálculo do valor aprovado do BM (valor_total_medido - glosa)
# ------------------------------------------------------------
@event.listens_for(BoletimMedicao, 'before_insert')
@event.listens_for(BoletimMedicao, 'before_update')
def calculate_valor_aprovado(mapper, connection, target):
    target.valor_aprovado = target.valor_total_medido - target.valor_glosa


# ------------------------------------------------------------
# 4. Cálculo automático do valor líquido da NF (RN03)
# ------------------------------------------------------------
def obter_aliquotas_contrato(contrato_id: int, session: Session):
    """Busca configurações de impostos do contrato ou padrões."""
    # Lógica simplificada: pode ser expandida para buscar de tabelas de configuração global
    impostos = session.execute(
        select(ContratoImposto).where(ContratoImposto.contrato_id == contrato_id)
    ).scalars().all()
    # Se não houver personalizado, retorna padrões (exemplo)
    padroes = {
        'ISS': 5.0, 'INSS': 11.0, 'IRRF': 1.5, 'CSLL': 1.0, 'PIS': 0.65, 'COFINS': 3.0
    }
    aliquota_dict = {imp.tipo_imposto: imp.aliquota for imp in impostos}
    return {k: aliquota_dict.get(k, padroes.get(k, 0)) for k in padroes}

@event.listens_for(Faturamento, 'before_insert')
@event.listens_for(Faturamento, 'before_update')
def calculate_nf_liquido(mapper, connection, target):
    """Calcula retenções e valor líquido com base nas alíquotas do contrato."""
    if not target.bm_id:
        return  # não é possível calcular sem vínculo com BM

    # Obtém o contrato_id através do BM
    session = Session.object_session(target) or connection
    bm = session.get(BoletimMedicao, target.bm_id)
    if not bm:
        return
    contrato_id = bm.contrato_id

    aliquotas = obter_aliquotas_contrato(contrato_id, session)

    # Cálculo simplificado: aplica percentual sobre o valor bruto
    target.iss_retido = target.valor_bruto_nf * (aliquotas.get('ISS', 0) / 100)
    target.inss_retido = target.valor_bruto_nf * (aliquotas.get('INSS', 0) / 100)
    target.irrf_retido = target.valor_bruto_nf * (aliquotas.get('IRRF', 0) / 100)
    target.csll_retido = target.valor_bruto_nf * (aliquotas.get('CSLL', 0) / 100)
    target.pis_retido = target.valor_bruto_nf * (aliquotas.get('PIS', 0) / 100)
    target.cofins_retido = target.valor_bruto_nf * (aliquotas.get('COFINS', 0) / 100)

    total_retencoes = (
        target.iss_retido + target.inss_retido + target.irrf_retido +
        target.csll_retido + target.pis_retido + target.cofins_retido
    )
    target.valor_liquido_nf = target.valor_bruto_nf - total_retencoes


# ------------------------------------------------------------
# 5. Atualização do status da NF com base nos pagamentos (RN04)
# ------------------------------------------------------------
def atualiza_status_faturamento(faturamento_id: int, session: Session):
    """Recalcula o status da NF conforme soma dos pagamentos."""
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
    """Listener para AFTER INSERT/UPDATE/DELETE de pagamento."""
    session = Session.object_session(target) or connection
    atualiza_status_faturamento(target.faturamento_id, session)
    session.flush()


# ------------------------------------------------------------
# 6. Atualização da data_fim_prevista do contrato (aditivos)
# ------------------------------------------------------------
def recalcula_data_fim_prevista(contrato_id: int, session: Session):
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        return
    total_dias_acrescimo = session.execute(
        select(func.coalesce(func.sum(Aditivo.dias_acrescimo), 0))
        .where(Aditivo.contrato_id == contrato_id)
    ).scalar()
    dias_totais = contrato.prazo_original_dias + total_dias_acrescimo
    from datetime import timedelta
    contrato.data_fim_prevista = contrato.data_inicio + timedelta(days=dias_totais)
    session.add(contrato)

@event.listens_for(Aditivo, 'after_insert')
@event.listens_for(Aditivo, 'after_update')
@event.listens_for(Aditivo, 'after_delete')
def update_contrato_fim_prevista(mapper, connection, target):
    session = Session.object_session(target) or connection
    recalcula_data_fim_prevista(target.contrato_id, session)
    session.flush()