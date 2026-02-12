from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.empresa_repo import EmpresaRepository
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate
from app.models.empresa import Empresa

class EmpresaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EmpresaRepository(db)

    # ------------------------------------------------------------------
    # CRIAR EMPRESA
    # ------------------------------------------------------------------
    def create_empresa(self, empresa_data: EmpresaCreate) -> Empresa:
        # 1. Verificar se CNPJ já existe
        existing = self.repo.get_by_cnpj(empresa_data.cnpj)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CNPJ {empresa_data.cnpj} já está cadastrado."
            )

        # 2. Converter para dicionário e criar
        empresa_dict = empresa_data.model_dump()
        empresa = self.repo.create(**empresa_dict)

        # 3. Commit e refresh para retornar o objeto completo
        self.db.commit()
        self.db.refresh(empresa)
        return empresa

    # ------------------------------------------------------------------
    # BUSCAR EMPRESA POR ID
    # ------------------------------------------------------------------
    def get_empresa(self, empresa_id: int) -> Empresa:
        empresa = self.repo.get(empresa_id)
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada."
            )
        return empresa

    # ------------------------------------------------------------------
    # BUSCAR EMPRESA POR CNPJ (opcional, útil para validações)
    # ------------------------------------------------------------------
    def get_empresa_by_cnpj(self, cnpj: str) -> Empresa | None:
        return self.repo.get_by_cnpj(cnpj)

    # ------------------------------------------------------------------
    # LISTAR EMPRESAS (COM PAGINAÇÃO)
    # ------------------------------------------------------------------
    def list_empresas(self, skip: int = 0, limit: int = 100) -> list[Empresa]:
        return self.repo.get_multi(skip, limit)

    # ------------------------------------------------------------------
    # ATUALIZAR EMPRESA
    # ------------------------------------------------------------------
    def update_empresa(self, empresa_id: int, empresa_data: EmpresaUpdate) -> Empresa:
        # 1. Verificar se a empresa existe
        empresa = self.get_empresa(empresa_id)

        # 2. Converter para dicionário, ignorando campos não enviados
        update_dict = empresa_data.model_dump(exclude_unset=True)

        # 3. Se estiver atualizando o CNPJ, verificar duplicidade
        if "cnpj" in update_dict:
            novo_cnpj = update_dict["cnpj"]
            # Se o CNPJ for diferente do atual
            if novo_cnpj != empresa.cnpj:
                existing = self.repo.get_by_cnpj(novo_cnpj)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"CNPJ {novo_cnpj} já está cadastrado em outra empresa."
                    )

        # 4. Atualizar
        empresa_atualizada = self.repo.update(empresa, update_dict)
        self.db.commit()
        self.db.refresh(empresa_atualizada)
        return empresa_atualizada

    # ------------------------------------------------------------------
    # DELETAR EMPRESA (SOFT DELETE? NÃO, REMOÇÃO REAL POR ENQUANTO)
    # ------------------------------------------------------------------
    def delete_empresa(self, empresa_id: int) -> None:
        # 1. Verificar se a empresa existe
        empresa = self.get_empresa(empresa_id)

        # 2. (Opcional) Verificar se há contratos vinculados a esta empresa
        #    Para não quebrar integridade referencial.
        from app.models.contrato import Contrato
        contratos = self.db.query(Contrato).filter(
            Contrato.cliente_id == empresa_id
        ).first()
        if contratos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir empresa que possui contratos vinculados."
            )

        # 3. Deletar
        self.repo.delete(empresa.id)
        self.db.commit()