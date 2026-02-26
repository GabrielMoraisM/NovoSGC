from datetime import date, datetime
from urllib import request

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from decimal import Decimal
from app.models.usuario import Usuario
from fastapi import Request

from app.repositories.contrato_repo import ContratoRepository
from app.repositories.empresa_repo import EmpresaRepository
from app.schemas.contrato import ContratoCreate, ContratoUpdate
from app.models.contrato import Contrato
from app.services.log_service import LogService

# Função auxiliar para serializar objetos não-JSON
def serializar_para_json(obj):
        """Converte objetos não serializáveis (Decimal, date, datetime) para formatos JSON."""
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: serializar_para_json(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [serializar_para_json(i) for i in obj]
        return obj

class ContratoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ContratoRepository(db)
        self.empresa_repo = EmpresaRepository(db)

    # ------------------------------------------------------------------
    # CRIAR CONTRATO
    # ------------------------------------------------------------------
    def create_contrato(
        self, 
        contrato_data: ContratoCreate, 
        current_user: Usuario, 
        request: Request
    ) -> Contrato:
        # 1. Verificar se número do contrato já existe
        existing = self.repo.get_by_numero(contrato_data.numero_contrato)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contrato nº {contrato_data.numero_contrato} já cadastrado."
            )

        # 2. Verificar se cliente existe
        cliente = self.empresa_repo.get(contrato_data.cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado."
            )

        # 3. Verificar se cliente é do tipo CLIENTE
        if cliente.tipo != "CLIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A empresa informada não é um cliente válido."
            )

        # 4. Preparar dados e criar
        contrato_dict = contrato_data.model_dump()
        contrato_dict['valor_total'] = contrato_dict['valor_original']  # valor_total = original
        
        contrato = self.repo.create(**contrato_dict)
        self.db.commit()
        self.db.refresh(contrato)

        # 5. Registrar log
        from app.services.log_service import LogService
        from fastapi.encoders import jsonable_encoder

        # Prepara dados do contrato para log (remove atributos internos do SQLAlchemy)
        contrato_dados = {
            k: v for k, v in contrato.__dict__.items() 
            if not k.startswith('_') and k != '_sa_instance_state'
        }
        # Converte para tipos serializáveis (ex: datetime para string)
        dados_novos = jsonable_encoder(contrato_dados)

        log_service = LogService(self.db)
        log_service.registrar_log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao="CREATE",
            entidade="contratos",
            entidade_id=contrato.id,
            dados_novos=dados_novos,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        return contrato
   # ------------------------------------------------------------------
    # BUSCAR CONTRATO POR ID
    # ------------------------------------------------------------------
    def get_contrato(self, contrato_id: int) -> Contrato:
        contrato = self.repo.get(contrato_id)
        if not contrato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato não encontrado."
            )
        return contrato

    # ------------------------------------------------------------------
    # LISTAR CONTRATOS
    # ------------------------------------------------------------------
    def list_contratos(self, skip: int = 0, limit: int = 100) -> list[Contrato]:
        return self.repo.get_multi(skip, limit)

    # ------------------------------------------------------------------
    # ATUALIZAR CONTRATO
    # ------------------------------------------------------------------
    def update_contrato(
        self,
        contrato_id: int,
        contrato_data: ContratoUpdate,
        current_user: Usuario,
        request: Request
    ) -> Contrato:
        # 1. Buscar o contrato existente
        contrato = self.get_contrato(contrato_id)
        # Salvar dados antigos antes da atualização (serializados)
        dados_antigos = serializar_para_json({
            k: v for k, v in contrato.__dict__.items() if not k.startswith('_')
        })

        # 2. Converter dados recebidos (apenas os campos preenchidos)
        update_dict = contrato_data.model_dump(exclude_unset=True)

        # 3. Validações específicas
        if "numero_contrato" in update_dict:
            novo_numero = update_dict["numero_contrato"]
            if novo_numero != contrato.numero_contrato:
                existing = self.repo.get_by_numero(novo_numero)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Contrato nº {novo_numero} já cadastrado."
                    )

        if "cliente_id" in update_dict:
            cliente = self.empresa_repo.get(update_dict["cliente_id"])
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado."
                )
            if cliente.tipo != "CLIENTE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A empresa informada não é um cliente válido."
                )

        # 4. Aplicar a atualização no repositório
        contrato_atualizado = self.repo.update(contrato, update_dict)
        self.db.commit()
        self.db.refresh(contrato_atualizado)

        # 5. Registrar log (dados novos serializados)
        from app.services.log_service import LogService
        log_service = LogService(self.db)
        dados_novos = serializar_para_json({
            k: v for k, v in contrato_atualizado.__dict__.items() if not k.startswith('_')
        })
        log_service.registrar_log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao="UPDATE",
            entidade="contratos",
            entidade_id=contrato_id,
            dados_antigos=dados_antigos,
            dados_novos=dados_novos,
            ip=request.client.host,
            user_agent=request.headers.get("user-agent")
        )

        # 6. Retornar o contrato atualizado
        return contrato_atualizado



    # ------------------------------------------------------------------
    # DELETAR CONTRATO
    # ------------------------------------------------------------------
    def delete_contrato(self, contrato_id: int, current_user: Usuario, request: Request) -> None:
        contrato = self.get_contrato(contrato_id)
        # Armazenar dados antigos para o log
        dados_antigos = {k: v for k, v in contrato.__dict__.items() if not k.startswith('_')}

        # Verificar se há boletins de medição vinculados (proteger integridade)
        from app.models.boletim_medicao import BoletimMedicao
        boletins = self.db.query(BoletimMedicao).filter(
            BoletimMedicao.contrato_id == contrato_id
        ).first()
        if boletins:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir contrato que possui boletins de medição."
            )

        self.repo.delete(contrato.id)
        self.db.commit()

        # Registrar log
        from app.services.log_service import LogService
        log_service = LogService(self.db)
        log_service.registrar_log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao="DELETE",
            entidade="contratos",
            entidade_id=contrato_id,
            dados_antigos=dados_antigos,
            dados_novos=None,
            ip=request.client.host,
            user_agent=request.headers.get("user-agent")
        )