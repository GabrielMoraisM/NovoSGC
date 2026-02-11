from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, Date, DateTime, Boolean, Text,
    Enum, ForeignKey, UniqueConstraint, CheckConstraint, Index, DECIMAL,
    event, func, select, text
)
from sqlalchemy.orm import relationship, validates
from app.models.base import Base

# ----- ENUMs -----
perfil_enum = Enum('ADMIN', 'GESTOR', 'FINANCEIRO', 'AUDITOR', name='perfil')
tipo_empresa_enum = Enum('MATRIZ', 'FILIAL', 'PARCEIRO_CONSORCIO', 'SCP', 'CLIENTE', name='tipo_empresa')
tipo_obra_enum = Enum('HECA_100', 'CONSORCIO', 'SCP', name='tipo_obra')
status_contrato_enum = Enum('ATIVO', 'PARALISADO', 'ENCERRADO', name='status_contrato')
tipo_aditivo_enum = Enum('PRAZO', 'VALOR', 'AMBOS', 'PARALISACAO', name='tipo_aditivo')
tipo_seguro_enum = Enum('GARANTIA_CONTRATUAL', 'RISCO_ENGENHARIA', 'RC', name='tipo_seguro')
status_bm_enum = Enum('RASCUNHO', 'APROVADO', 'FATURADO', 'CANCELADO', name='status_bm')
status_nf_enum = Enum('PENDENTE', 'PARCIAL', 'QUITADO', 'CANCELADO', 'VENCIDO', name='status_nf')
base_calculo_enum = Enum('BRUTO', 'LIQUIDO', name='base_calculo')


# ----- 1. USUÁRIOS -----
class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(perfil_enum, nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    contratos = relationship('UsuarioContrato', back_populates='usuario')


# ----- 2. USUARIO_CONTRATOS (RLS) -----
class UsuarioContrato(Base):
    __tablename__ = 'usuario_contratos'
    __table_args__ = (
        PrimaryKeyConstraint('usuario_id', 'contrato_id'),
    )

    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=False)

    usuario = relationship('Usuario', back_populates='contratos')
    contrato = relationship('Contrato', back_populates='usuarios')


# ----- 3. EMPRESAS -----
class Empresa(Base):
    __tablename__ = 'empresas'

    id = Column(Integer, primary_key=True)
    razao_social = Column(String(200), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    tipo = Column(tipo_empresa_enum, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # relacionamentos (para clareza)
    contratos_como_cliente = relationship('Contrato', foreign_keys='Contrato.cliente_id', back_populates='cliente')
    contratos_como_emitente = relationship('Faturamento', foreign_keys='Faturamento.empresa_emissora_id', back_populates='empresa_emissora')
    seguradoras = relationship('ContratoSeguro', foreign_keys='ContratoSeguro.seguradora_id', back_populates='seguradora')
    participacoes = relationship('ContratoParticipante', back_populates='empresa')


# ----- 4. CONTRATOS -----
class Contrato(Base):
    __tablename__ = 'contratos'

    id = Column(Integer, primary_key=True)
    numero_contrato = Column(String(50), unique=True, nullable=False)
    tipo_obra = Column(tipo_obra_enum, nullable=False)
    valor_original = Column(DECIMAL(15,2), nullable=False)
    prazo_original_dias = Column(Integer, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim_prevista = Column(Date)          # atualizado via trigger
    status = Column(status_contrato_enum, default='ATIVO')
    iss_percentual_padrao = Column(DECIMAL(5,2))
    cliente_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # relacionamentos
    cliente = relationship('Empresa', foreign_keys=[cliente_id], back_populates='contratos_como_cliente')
    aditivos = relationship('Aditivo', back_populates='contrato', cascade='all, delete-orphan')
    participantes = relationship('ContratoParticipante', back_populates='contrato', cascade='all, delete-orphan')
    arts = relationship('ContratoArt', back_populates='contrato', cascade='all, delete-orphan')
    seguros = relationship('ContratoSeguro', back_populates='contrato', cascade='all, delete-orphan')
    boletins = relationship('BoletimMedicao', back_populates='contrato', cascade='all, delete-orphan')
    usuarios = relationship('UsuarioContrato', back_populates='contrato')
    impostos_config = relationship('ContratoImposto', back_populates='contrato', cascade='all, delete-orphan')


# ----- 5. ADITIVOS -----
class Aditivo(Base):
    __tablename__ = 'aditivos'

    id = Column(Integer, primary_key=True)
    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=False)
    tipo = Column(tipo_aditivo_enum, nullable=False)
    numero_emenda = Column(String(20))
    data_aprovacao = Column(Date)
    dias_acrescimo = Column(Integer, default=0)
    valor_acrescimo = Column(DECIMAL(15,2), default=0)
    justificativa = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    contrato = relationship('Contrato', back_populates='aditivos')

    __table_args__ = (
        Index('idx_aditivos_contrato_id', 'contrato_id'),
    )


# ----- 6. CONTRATO_PARTICIPANTES (consórcio/SCP) -----
class ContratoParticipante(Base):
    __tablename__ = 'contrato_participantes'
    __table_args__ = (
        PrimaryKeyConstraint('contrato_id', 'empresa_id'),
        CheckConstraint('percentual_participacao >= 0 AND percentual_participacao <= 100',
                        name='check_percentual_range'),
    )

    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=False)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    percentual_participacao = Column(DECIMAL(5,2), nullable=False)
    is_lider = Column(Boolean, default=False)

    contrato = relationship('Contrato', back_populates='participantes')
    empresa = relationship('Empresa', back_populates='participacoes')


# ----- 7. CONTRATO_ARTS -----
class ContratoArt(Base):
    __tablename__ = 'contrato_arts'

    id = Column(Integer, primary_key=True)
    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=False)
    nome_profissional = Column(String(100), nullable=False)
    numero_art = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    contrato = relationship('Contrato', back_populates='arts')


# ----- 8. CONTRATO_SEGUROS -----
class ContratoSeguro(Base):
    __tablename__ = 'contrato_seguros'

    id = Column(Integer, primary_key=True)
    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=False)
    seguradora_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    tipo = Column(tipo_seguro_enum, nullable=False)
    numero_apolice = Column(String(50))
    data_vencimento = Column(Date, nullable=False)
    valor = Column(DECIMAL(15,2))
    created_at = Column(DateTime, default=datetime.now)

    contrato = relationship('Contrato', back_populates='seguros')
    seguradora = relationship('Empresa', foreign_keys=[seguradora_id], back_populates='seguradoras')


# ----- 9. BOLETINS_MEDICAO (BM) -----
class BoletimMedicao(Base):
    __tablename__ = 'boletins_medicao'
    __table_args__ = (
        UniqueConstraint('contrato_id', 'numero_sequencial', name='unique_bm_por_contrato'),
        Index('idx_bm_contrato_status', 'contrato_id', 'status'),
    )

    id = Column(Integer, primary_key=True)
    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=False)
    numero_sequencial = Column(Integer, nullable=False)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    valor_total_medido = Column(DECIMAL(15,2), nullable=False)
    valor_glosa = Column(DECIMAL(15,2), default=0)
    valor_aprovado = Column(DECIMAL(15,2))   # calculado antes do insert/update
    status = Column(status_bm_enum, default='RASCUNHO')
    cancelado_motivo = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    contrato = relationship('Contrato', back_populates='boletins')
    faturas = relationship('Faturamento', back_populates='bm', cascade='all, delete-orphan')


# ----- 10. FATURAMENTOS (Notas Fiscais) -----
class Faturamento(Base):
    __tablename__ = 'faturamentos'

    id = Column(Integer, primary_key=True)
    bm_id = Column(Integer, ForeignKey('boletins_medicao.id'), nullable=False)
    numero_nf = Column(String(30))
    empresa_emissora_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    valor_bruto_nf = Column(DECIMAL(15,2), nullable=False)
    valor_liquido_nf = Column(DECIMAL(15,2), nullable=False)
    iss_retido = Column(DECIMAL(15,2), default=0)
    inss_retido = Column(DECIMAL(15,2), default=0)
    irrf_retido = Column(DECIMAL(15,2), default=0)
    csll_retido = Column(DECIMAL(15,2), default=0)
    pis_retido = Column(DECIMAL(15,2), default=0)
    cofins_retido = Column(DECIMAL(15,2), default=0)
    data_emissao = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    status = Column(status_nf_enum, default='PENDENTE')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    bm = relationship('BoletimMedicao', back_populates='faturas')
    empresa_emissora = relationship('Empresa', foreign_keys=[empresa_emissora_id], back_populates='contratos_como_emitente')
    cliente = relationship('Empresa', foreign_keys=[cliente_id])
    pagamentos = relationship('Pagamento', back_populates='faturamento', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_faturamento_bm_id', 'bm_id'),
        Index('idx_faturamento_status_vencimento', 'status', 'data_vencimento'),
    )


# ----- 11. PAGAMENTOS -----
class Pagamento(Base):
    __tablename__ = 'pagamentos'

    id = Column(Integer, primary_key=True)
    faturamento_id = Column(Integer, ForeignKey('faturamentos.id'), nullable=False)
    data_pagamento = Column(Date, nullable=False)
    valor_pago = Column(DECIMAL(15,2), nullable=False)
    comprovante_url = Column(String(255))
    observacao = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    faturamento = relationship('Faturamento', back_populates='pagamentos')

    __table_args__ = (
        Index('idx_pagamento_faturamento_id', 'faturamento_id'),
    )


# ----- 12. CONTRATO_IMPOSTOS (configuração personalizada) -----
class ContratoImposto(Base):
    __tablename__ = 'contrato_impostos'
    __table_args__ = (
        PrimaryKeyConstraint('contrato_id', 'tipo_imposto'),
    )

    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=False)
    tipo_imposto = Column(String(20), nullable=False)   # 'ISS','INSS','IRRF','CSLL','PIS','COFINS'
    aliquota = Column(DECIMAL(5,2), nullable=False)
    base_calculo = Column(base_calculo_enum, default='BRUTO')

    contrato = relationship('Contrato', back_populates='impostos_config')