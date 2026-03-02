from sqlalchemy.orm import Session
from app.models.contrato import Contrato
from app.models.boletim_medicao import BoletimMedicao
from datetime import date

def calcular_analise_ritmo(db: Session, contrato_id: int):
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise ValueError("Contrato não encontrado")

    valor_total = float(contrato.valor_total) if contrato.valor_total else 0.0
    data_inicio = contrato.data_inicio
    data_fim_prevista = contrato.data_fim_prevista

    if not data_inicio or not data_fim_prevista:
        # Se não houver datas, não podemos calcular planejado
        raise ValueError("Contrato sem datas de início/fim")

    dias_totais = (data_fim_prevista - data_inicio).days
    if dias_totais <= 0:
        raise ValueError("Prazo inválido")

    hoje = date.today()
    if hoje < data_inicio:
        dias_decorridos = 0
    else:
        dias_decorridos = (hoje - data_inicio).days
        if dias_decorridos > dias_totais:
            dias_decorridos = dias_totais

    # Calcular valor executado acumulado
    valor_executado = db.query(BoletimMedicao).filter(
        BoletimMedicao.contrato_id == contrato_id,
        BoletimMedicao.status.in_(["APROVADO", "FATURADO"])
    ).with_entities(db.func.sum(BoletimMedicao.valor_aprovado)).scalar() or 0.0
    valor_executado = float(valor_executado)

    percentual_fisico = (valor_executado / valor_total * 100) if valor_total else 0.0

    # Planejado acumulado linear
    ritmo_planejado_diario = valor_total / dias_totais
    valor_planejado_acumulado = ritmo_planejado_diario * dias_decorridos

    desvio_valor = valor_executado - valor_planejado_acumulado
    desvio_percentual = (desvio_valor / valor_planejado_acumulado * 100) if valor_planejado_acumulado else 0.0

    # Ritmo real médio
    ritmo_real_medio = valor_executado / dias_decorridos if dias_decorridos > 0 else None

    # Ritmo necessário para recuperar (dias restantes)
    dias_restantes = dias_totais - dias_decorridos
    ritmo_necessario_para_recuperar = None
    if dias_restantes > 0:
        valor_a_executar = valor_total - valor_executado
        ritmo_necessario_para_recuperar = valor_a_executar / dias_restantes

    # Status
    if abs(desvio_percentual) < 5:  # tolerância de 5%
        status = "NO_PRAZO"
    elif desvio_valor > 0:
        status = "ADIANTADO"
    else:
        status = "ATRASADO"

    return {
        "valor_total_contrato": round(valor_total, 2),
        "dias_totais": dias_totais,
        "dias_decorridos": dias_decorridos,
        "valor_executado": round(valor_executado, 2),
        "percentual_fisico": round(percentual_fisico, 2),
        "valor_planejado_acumulado": round(valor_planejado_acumulado, 2),
        "ritmo_planejado_diario": round(ritmo_planejado_diario, 2),
        "ritmo_real_medio": round(ritmo_real_medio, 2) if ritmo_real_medio else None,
        "desvio_valor": round(desvio_valor, 2),
        "desvio_percentual": round(desvio_percentual, 2),
        "ritmo_necessario_para_recuperar": round(ritmo_necessario_para_recuperar, 2) if ritmo_necessario_para_recuperar else None,
        "status": status
    }