def calcular_ritmo_medio(contrato_id, db):
    # Busca últimos 3 boletins aprovados/faturados
    # Calcula média mensal (considerando períodos)
    return ritmo_mensal

def projetar_termino(contrato_id, db):
    saldo = contrato.valor_total - valor_executado
    ritmo = calcular_ritmo_medio(contrato_id, db)
    dias_restantes = (saldo / ritmo) * 30  # se ritmo for mensal
    return data_atual + timedelta(days=dias_restantes)

def projetar_faturamento(contrato_id, db):
    # Soma de boletins aprovados não faturados
    # Soma de notas emitidas não pagas, agrupadas por vencimento
    return {
        '30d': valor_a_receber_ate_30d,
        '60d': valor_a_receber_31d_a_60d,
        '90d': valor_a_receber_61d_a_90d
    }