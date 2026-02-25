# app/services/alerta_service.py
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.contrato import Contrato
from app.models.contrato_art import ContratoArt
from app.models.contrato_seguro import ContratoSeguro
from app.models.boletim_medicao import BoletimMedicao
from app.models.faturamento import Faturamento

class AlertaService:
    def __init__(self, db: Session):
        self.db = db

    def gerar_alertas(self, contrato_id=None):
        alertas = []
        query_contratos = self.db.query(Contrato)
        if contrato_id:
            query_contratos = query_contratos.filter(Contrato.id == contrato_id)
        contratos = query_contratos.all()

        for c in contratos:
            alertas.extend(self._alertas_contrato(c))
            alertas.extend(self._alertas_boletins(c))
            alertas.extend(self._alertas_faturamentos(c))

        return alertas

    def _alertas_contrato(self, contrato):
        alertas = []
        # ART pendente
        arts = self.db.query(ContratoArt).filter(ContratoArt.contrato_id == contrato.id).count()
        if arts == 0:
            alertas.append({
                'tipo': 'ART_PENDENTE',
                'titulo': 'ART não cadastrada',
                'mensagem': f'O contrato {contrato.numero_contrato} não possui ART cadastrada.',
                'severidade': 'alta',
                'contrato_id': contrato.id
            })

        # OS pendente
        if not contrato.numero_os or not contrato.data_os:
            alertas.append({
                'tipo': 'OS_PENDENTE',
                'titulo': 'Ordem de Serviço pendente',
                'mensagem': f'O contrato {contrato.numero_contrato} não possui OS cadastrada.',
                'severidade': 'media',
                'contrato_id': contrato.id
            })

        # Seguros a vencer
        hoje = date.today()
        trinta_dias = hoje + timedelta(days=30)
        seguros = self.db.query(ContratoSeguro).filter(
            ContratoSeguro.contrato_id == contrato.id,
            ContratoSeguro.data_vencimento >= hoje,
            ContratoSeguro.data_vencimento <= trinta_dias
        ).all()
        for s in seguros:
            alertas.append({
                'tipo': 'SEGURO_VENCER',
                'titulo': 'Seguro próximo do vencimento',
                'mensagem': f'Seguro {s.tipo} vence em {s.data_vencimento.strftime("%d/%m/%Y")}.',
                'severidade': 'media',
                'contrato_id': contrato.id
            })

        # Seguros vencidos
        seguros_vencidos = self.db.query(ContratoSeguro).filter(
            ContratoSeguro.contrato_id == contrato.id,
            ContratoSeguro.data_vencimento < hoje
        ).all()
        for s in seguros_vencidos:
            alertas.append({
                'tipo': 'SEGURO_VENCIDO',
                'titulo': 'Seguro vencido',
                'mensagem': f'Seguro {s.tipo} venceu em {s.data_vencimento.strftime("%d/%m/%Y")}.',
                'severidade': 'critica',
                'contrato_id': contrato.id
            })
        return alertas

    def _alertas_boletins(self, contrato):
        alertas = []
        # Boletins em rascunho (aguardando aprovação)
        rascunhos = self.db.query(BoletimMedicao).filter(
            BoletimMedicao.contrato_id == contrato.id,
            BoletimMedicao.status == 'RASCUNHO'
        ).all()
        for b in rascunhos:
            alertas.append({
                'tipo': 'BOLETIM_RASCUNHO',
                'titulo': 'Boletim aguardando aprovação',
                'mensagem': f'Boletim BM-{b.numero_sequencial} do período {b.periodo_inicio} a {b.periodo_fim} está em rascunho.',
                'severidade': 'media',
                'contrato_id': contrato.id,
                'boletim_id': b.id
            })

        # Boletins aprovados sem NF
        aprovados_sem_nf = self.db.query(BoletimMedicao).outerjoin(
            Faturamento, Faturamento.bm_id == BoletimMedicao.id
        ).filter(
            BoletimMedicao.contrato_id == contrato.id,
            BoletimMedicao.status == 'APROVADO',
            Faturamento.id == None
        ).all()
        for b in aprovados_sem_nf:
            alertas.append({
                'tipo': 'BOLETIM_APROVADO_SEM_NF',
                'titulo': 'Boletim aprovado sem nota fiscal',
                'mensagem': f'Boletim BM-{b.numero_sequencial} aprovado mas não faturado.',
                'severidade': 'alta',
                'contrato_id': contrato.id,
                'boletim_id': b.id
            })
        return alertas

    def _alertas_faturamentos(self, contrato):
        alertas = []
        hoje = date.today()
        # Notas a vencer (próximos 5 dias)
        cinco_dias = hoje + timedelta(days=5)
        nfs_avencer = self.db.query(Faturamento).join(
            BoletimMedicao, BoletimMedicao.id == Faturamento.bm_id
        ).filter(
            BoletimMedicao.contrato_id == contrato.id,
            Faturamento.status == 'PENDENTE',
            Faturamento.data_vencimento <= cinco_dias,
            Faturamento.data_vencimento >= hoje
        ).all()
        for nf in nfs_avencer:
            alertas.append({
                'tipo': 'NF_A_VENCER',
                'titulo': 'Nota fiscal próxima do vencimento',
                'mensagem': f'NF {nf.numero_nf} vence em {nf.data_vencimento.strftime("%d/%m/%Y")}.',
                'severidade': 'media',
                'contrato_id': contrato.id,
                'faturamento_id': nf.id
            })

        # Notas vencidas
        nfs_vencidas = self.db.query(Faturamento).join(
            BoletimMedicao, BoletimMedicao.id == Faturamento.bm_id
        ).filter(
            BoletimMedicao.contrato_id == contrato.id,
            Faturamento.status == 'PENDENTE',
            Faturamento.data_vencimento < hoje
        ).all()
        for nf in nfs_vencidas:
            alertas.append({
                'tipo': 'NF_VENCIDA',
                'titulo': 'Nota fiscal vencida',
                'mensagem': f'NF {nf.numero_nf} venceu em {nf.data_vencimento.strftime("%d/%m/%Y")}.',
                'severidade': 'critica',
                'contrato_id': contrato.id,
                'faturamento_id': nf.id
            })

        # Notas canceladas (opcional)
        nfs_canceladas = self.db.query(Faturamento).join(
            BoletimMedicao, BoletimMedicao.id == Faturamento.bm_id
        ).filter(
            BoletimMedicao.contrato_id == contrato.id,
            Faturamento.status == 'CANCELADO'
        ).all()
        for nf in nfs_canceladas:
            alertas.append({
                'tipo': 'NF_CANCELADA',
                'titulo': 'Nota fiscal cancelada',
                'mensagem': f'NF {nf.numero_nf} foi cancelada.',
                'severidade': 'alta',
                'contrato_id': contrato.id,
                'faturamento_id': nf.id
            })
        return alertas