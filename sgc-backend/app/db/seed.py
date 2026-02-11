import os
from sqlalchemy import create_mock_engine, text
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import (
    Usuario, Empresa, Contrato, ContratoParticipante, 
    Aditivo, BoletimMedicao, Faturamento, Pagamento,
    perfil_enum, tipo_empresa_enum, tipo_obra_enum
)
from datetime import date, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database():
    db = SessionLocal()
    try:
        # ----- 1. Usuário ADMIN padrão -----
        admin = db.query(Usuario).filter(Usuario.email == "admin@heca.com.br").first()
        if not admin:
            admin = Usuario(
                email="admin@heca.com.br",
                senha_hash=pwd_context.hash("123456"),
                perfil="ADMIN",
                ativo=True
            )
            db.add(admin)
            db.flush()
            print("Usuário ADMIN criado.")

        # ----- 2. Empresas -----
        heca = db.query(Empresa).filter(Empresa.cnpj == "00.000.000/0001-91").first()
        if not heca:
            heca = Empresa(
                razao_social="Heca Engenharia Ltda",
                cnpj="00.000.000/0001-91",
                tipo="MATRIZ"
            )
            db.add(heca)

        cliente_x = Empresa(
            razao_social="Cliente Exemplo S/A",
            cnpj="11.111.111/0001-11",
            tipo="CLIENTE"
        )
        db.add(cliente_x)

        parceiro_a = Empresa(
            razao_social="Parceiro A Construções",
            cnpj="22.222.222/0001-22",
            tipo="PARCEIRO_CONSORCIO"
        )
        db.add(parceiro_a)

        db.flush()

        # ----- 3. Contrato exemplo -----
        contrato1 = Contrato(
            numero_contrato="128/2024",
            tipo_obra="CONSORCIO",
            valor_original=1_500_000.00,
            prazo_original_dias=365,
            data_inicio=date(2024, 1, 1),
            cliente_id=cliente_x.id,
            iss_percentual_padrao=5.0,
            status="ATIVO"
        )
        db.add(contrato1)
        db.flush()

        # Participantes do consórcio
        part1 = ContratoParticipante(
            contrato_id=contrato1.id,
            empresa_id=heca.id,
            percentual_participacao=60.00,
            is_lider=True
        )
        part2 = ContratoParticipante(
            contrato_id=contrato1.id,
            empresa_id=parceiro_a.id,
            percentual_participacao=40.00,
            is_lider=False
        )
        db.add_all([part1, part2])

        # Aditivo de prazo
        aditivo1 = Aditivo(
            contrato_id=contrato1.id,
            tipo="PRAZO",
            numero_emenda="TA-01",
            data_aprovacao=date(2024, 6, 1),
            dias_acrescimo=30,
            justificativa="Chuvas excessivas"
        )
        db.add(aditivo1)
        db.flush()

        # Boletim de Medição
        bm1 = BoletimMedicao(
            contrato_id=contrato1.id,
            numero_sequencial=1,
            periodo_inicio=date(2024, 2, 1),
            periodo_fim=date(2024, 2, 28),
            valor_total_medido=120_000.00,
            valor_glosa=2_000.00,
            status="APROVADO"
        )
        db.add(bm1)
        db.flush()

        # Faturamento
        fat1 = Faturamento(
            bm_id=bm1.id,
            numero_nf="NF-001",
            empresa_emissora_id=heca.id,
            cliente_id=cliente_x.id,
            valor_bruto_nf=118_000.00,
            valor_liquido_nf=0,  # será calculado pelo listener
            data_emissao=date(2024, 3, 1),
            data_vencimento=date(2024, 3, 15),
            status="PENDENTE"
        )
        db.add(fat1)
        db.flush()

        # Pagamento parcial
        pag1 = Pagamento(
            faturamento_id=fat1.id,
            data_pagamento=date(2024, 3, 10),
            valor_pago=50_000.00
        )
        db.add(pag1)
        db.flush()

        db.commit()
        print("Seed concluído com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro no seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()