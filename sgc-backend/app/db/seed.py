"""
Script para popular o banco com dados iniciais de desenvolvimento.
Executar: python -m app.db.seed
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Adiciona o diretório raiz ao path para permitir imports absolutos
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.empresa_repo import EmpresaRepository
from app.repositories.contrato_repo import ContratoRepository
from app.repositories.contrato_participante_repo import ContratoParticipanteRepository
from app.repositories.aditivo_repo import AditivoRepository
from app.repositories.boletim_medicao_repo import BoletimMedicaoRepository
from app.repositories.faturamento_repo import FaturamentoRepository
from app.repositories.pagamento_repo import PagamentoRepository

from app.models.empresa import Empresa
from app.models.contrato import Contrato
from app.models.contrato_participante import ContratoParticipante
from app.models.aditivo import Aditivo
from app.models.boletim_medicao import BoletimMedicao
from app.models.faturamento import Faturamento
from app.models.pagamento import Pagamento

def seed():
    db = SessionLocal()
    try:
        print("🌱 Iniciando seed de dados...")

        # ---------- 1. USUÁRIO ADMIN ----------
        usuario_repo = UsuarioRepository(db)
        admin = usuario_repo.get_by_email("admin@heca.com.br")
        if not admin:
            admin = usuario_repo.create(
                email="admin@heca.com.br",
                senha_hash=get_password_hash("H3c@787"),
                perfil="ADMIN",
                ativo=True
            )
            db.commit()
            db.refresh(admin)
            print("✅ Usuário ADMIN criado.")
        else:
            print("⏩ Usuário ADMIN já existe.")

        # ---------- 2. EMPRESAS ----------
        empresa_repo = EmpresaRepository(db)

        # Heca Engenharia (MATRIZ)
        heca = empresa_repo.get_by_cnpj("00.000.000/0001-91")
        if not heca:
            heca = empresa_repo.create(
                razao_social="Heca Engenharia Ltda",
                cnpj="00.000.000/0001-91",
                tipo="MATRIZ"
            )
            print("✅ Empresa Heca criada.")
        else:
            print("⏩ Empresa Heca já existe.")

        # Cliente Exemplo
        cliente = empresa_repo.get_by_cnpj("11.111.111/0001-11")
        if not cliente:
            cliente = empresa_repo.create(
                razao_social="Cliente Exemplo S.A.",
                cnpj="11.111.111/0001-11",
                tipo="CLIENTE"
            )
            print("✅ Cliente exemplo criado.")
        else:
            print("⏩ Cliente exemplo já existe.")

        # Parceiro de Consórcio
        parceiro = empresa_repo.get_by_cnpj("22.222.222/0001-22")
        if not parceiro:
            parceiro = empresa_repo.create(
                razao_social="Parceiro Construtora Ltda",
                cnpj="22.222.222/0001-22",
                tipo="PARCEIRO_CONSORCIO"
            )
            print("✅ Parceiro de consórcio criado.")
        else:
            print("⏩ Parceiro de consórcio já existe.")

        db.commit()  # Confirma as empresas

        # ---------- 3. CONTRATO EXEMPLO (CONSÓRCIO) ----------
        contrato_repo = ContratoRepository(db)

        contrato = contrato_repo.get_by_numero("128/2024")
        if not contrato:
            contrato = contrato_repo.create(
                numero_contrato="128/2024",
                tipo_obra="CONSORCIO",
                valor_original=1_500_000.00,
                prazo_original_dias=365,
                data_inicio=date(2024, 1, 1),
                cliente_id=cliente.id,
                iss_percentual_padrao=5.0,
                status="ATIVO"
            )
            db.commit()
            db.refresh(contrato)
            print("✅ Contrato 128/2024 criado.")
        else:
            print("⏩ Contrato 128/2024 já existe.")

        # ---------- 4. PARTICIPANTES DO CONSÓRCIO (INSERÇÃO DIRETA, SEM FLUSH) ----------
        from app.models.contrato_participante import ContratoParticipante

        # Remove participantes existentes
        db.query(ContratoParticipante).filter(
            ContratoParticipante.contrato_id == contrato.id
        ).delete(synchronize_session=False)

        # Prepara os dois objetos
        participante1 = ContratoParticipante(
            contrato_id=contrato.id,
            empresa_id=heca.id,
            percentual_participacao=60.00,
            is_lider=True
        )

        participante2 = ContratoParticipante(
            contrato_id=contrato.id,
            empresa_id=parceiro.id,
            percentual_participacao=40.00,
            is_lider=False
        )

        # Adiciona ambos à sessão
        db.add_all([participante1, participante2])

        # COMMIT único após os dois inserts
        db.commit()
        print("✅ Participantes Heca (60%) e Parceiro (40%) recriados com sucesso.")
        # ---------- 5. ADITIVO DE PRAZO ----------
        aditivo_repo = AditivoRepository(db)

        aditivo = aditivo_repo.get_by_emenda(contrato.id, "TA-01")
        if not aditivo:
            aditivo = aditivo_repo.create(
                contrato_id=contrato.id,
                tipo="PRAZO",
                numero_emenda="TA-01",
                data_aprovacao=date(2024, 6, 1),
                dias_acrescimo=30,
                justificativa="Chuvas excessivas"
            )
            db.commit()
            print("✅ Aditivo TA-01 criado.")
        else:
            print("⏩ Aditivo TA-01 já existe.")

        # ---------- 6. BOLETIM DE MEDIÇÃO (BM) ----------
        bm_repo = BoletimMedicaoRepository(db)

        # Verifica se já existe BM número 1 para este contrato
        bm = bm_repo.get_by_contrato_sequencial(contrato.id, 1)
        if not bm:
            bm = bm_repo.create(
                contrato_id=contrato.id,
                numero_sequencial=1,  # será sobrescrito pelo listener
                periodo_inicio=date(2024, 2, 1),
                periodo_fim=date(2024, 2, 28),
                valor_total_medido=120_000.00,
                valor_glosa=2_000.00,
                status="APROVADO"
            )
            db.commit()
            db.refresh(bm)
            print(f"✅ BM {bm.numero_sequencial} criado.")
        else:
            print("⏩ BM já existe.")

        # ---------- 7. FATURAMENTO (NF) ----------
        fat_repo = FaturamentoRepository(db)

        faturamento = fat_repo.get_by_numero_nf("NF-001")
        if not faturamento:
            faturamento = fat_repo.create(
                bm_id=bm.id,
                numero_nf="NF-001",
                empresa_emissora_id=heca.id,
                cliente_id=cliente.id,
                valor_bruto_nf=118_000.00,
                valor_liquido_nf=0,  # será calculado pelo listener
                data_emissao=date(2024, 3, 1),
                data_vencimento=date(2024, 3, 15),
                status="PENDENTE"
            )
            db.commit()
            db.refresh(faturamento)
            print("✅ Faturamento NF-001 criado.")
        else:
            print("⏩ Faturamento NF-001 já existe.")

        # ---------- 8. PAGAMENTO PARCIAL ----------
        pag_repo = PagamentoRepository(db)

        pagamento = pag_repo.get_by_faturamento(faturamento.id)
        if not pagamento:
            pag_repo.create(
                faturamento_id=faturamento.id,
                data_pagamento=date(2024, 3, 10),
                valor_pago=50_000.00,
                observacao="Pagamento parcial"
            )
            db.commit()
            print("✅ Pagamento parcial registrado.")
        else:
            print("⏩ Pagamento já existe.")

        print("\n🎉 Seed concluído com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro durante seed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()