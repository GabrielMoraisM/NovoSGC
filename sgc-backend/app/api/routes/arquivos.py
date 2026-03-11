from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.models.usuario import Usuario
from app.models.contrato import Contrato
from app.models.boletim_medicao import BoletimMedicao
from app.models.faturamento import Faturamento
from app.models.pagamento import Pagamento
from app.schemas.arquivo import ArquivoInDB
from app.services.arquivo_service import ArquivoService

router = APIRouter()


# ── Helper: convert Arquivo ORM → dict ──────────────────────────────
def _to_schema(arquivo) -> dict:
    return {
        "id": arquivo.id,
        "nome_original": arquivo.nome_original,
        "tamanho": arquivo.tamanho,
        "tipo_mime": arquivo.tipo_mime,
        "entidade_tipo": arquivo.entidade_tipo,
        "entidade_id": arquivo.entidade_id,
        "descricao": arquivo.descricao,
        "created_at": arquivo.created_at,
        "url_download": f"/api/arquivos/{arquivo.id}/download",
    }


@router.post("/upload", response_model=ArquivoInDB, status_code=status.HTTP_201_CREATED)
async def upload_arquivo(
    file: UploadFile = File(...),
    entidade_tipo: str = Form(...),
    entidade_id: int = Form(...),
    descricao: Optional[str] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user),
):
    """Upload de arquivo vinculado a uma entidade."""
    service = ArquivoService(db)
    arquivo = service.upload_arquivo(
        file=file,
        entidade_tipo=entidade_tipo,
        entidade_id=entidade_id,
        descricao=descricao,
        usuario_id=current_user.id,
    )
    result = ArquivoInDB.model_validate(arquivo)
    result.url_download = f"/api/arquivos/{arquivo.id}/download"
    return result


@router.get("/arvore")
def get_arvore_arquivos(
    contrato_id: int = Query(..., description="ID do contrato para montar a hierarquia"),
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user),
):
    """Retorna a hierarquia de arquivos de um contrato: contrato -> BMs -> NFs -> Pagamentos."""
    service = ArquivoService(db)

    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")

    arquivos_contrato = service.get_by_entidade("contrato", contrato_id)

    boletins = (
        db.query(BoletimMedicao)
        .filter(BoletimMedicao.contrato_id == contrato_id)
        .order_by(BoletimMedicao.numero_sequencial)
        .all()
    )

    boletins_data = []
    for bm in boletins:
        arquivos_bm = service.get_by_entidade("boletim", bm.id)
        faturamentos = (
            db.query(Faturamento)
            .filter(Faturamento.bm_id == bm.id)
            .all()
        )
        faturamentos_data = []
        for fat in faturamentos:
            arquivos_fat = service.get_by_entidade("faturamento", fat.id)
            pagamentos = (
                db.query(Pagamento)
                .filter(Pagamento.faturamento_id == fat.id)
                .all()
            )
            pagamentos_data = []
            for pag in pagamentos:
                arquivos_pag = service.get_by_entidade("pagamento", pag.id)
                pagamentos_data.append({
                    "id": pag.id,
                    "data_pagamento": str(pag.data_pagamento) if pag.data_pagamento else None,
                    "valor_pago": float(pag.valor_pago) if pag.valor_pago else 0,
                    "arquivos": [_to_schema(a) for a in arquivos_pag],
                })
            faturamentos_data.append({
                "id": fat.id,
                "numero_nf": fat.numero_nf,
                "valor_bruto_nf": float(fat.valor_bruto_nf) if fat.valor_bruto_nf else 0,
                "arquivos": [_to_schema(a) for a in arquivos_fat],
                "pagamentos": pagamentos_data,
            })
        boletins_data.append({
            "id": bm.id,
            "numero_sequencial": bm.numero_sequencial,
            "periodo_inicio": str(bm.periodo_inicio) if bm.periodo_inicio else None,
            "periodo_fim": str(bm.periodo_fim) if bm.periodo_fim else None,
            "arquivos": [_to_schema(a) for a in arquivos_bm],
            "faturamentos": faturamentos_data,
        })

    return {
        "contrato": {
            "id": contrato.id,
            "numero_contrato": contrato.numero_contrato,
            "nome": contrato.numero_contrato,
            "arquivos": [_to_schema(a) for a in arquivos_contrato],
        },
        "boletins": boletins_data,
    }


@router.get("/", response_model=List[ArquivoInDB])
def list_arquivos(
    entidade_tipo: Optional[str] = Query(None),
    entidade_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user),
):
    """Lista arquivos com filtros opcionais."""
    service = ArquivoService(db)
    arquivos = service.list_all(entidade_tipo=entidade_tipo, entidade_id=entidade_id)
    result = []
    for a in arquivos:
        item = ArquivoInDB.model_validate(a)
        item.url_download = f"/api/arquivos/{a.id}/download"
        result.append(item)
    return result


@router.get("/{arquivo_id}/download")
def download_arquivo(
    arquivo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user),
):
    """Download autenticado de um arquivo."""
    service = ArquivoService(db)
    arquivo = service.get_arquivo(arquivo_id)
    path = Path(arquivo.caminho)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no disco.")
    return FileResponse(
        path=str(path),
        filename=arquivo.nome_original,
        media_type=arquivo.tipo_mime or "application/octet-stream",
    )


@router.delete("/{arquivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arquivo(
    arquivo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_active_user),
):
    """Remove um arquivo (disco + banco)."""
    service = ArquivoService(db)
    service.delete_arquivo(arquivo_id)
