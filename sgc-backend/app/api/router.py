from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.usuarios import router as usuarios_router
from app.api.routes.empresas import router as empresas_router
from app.api.routes.contratos import router as contratos_router
from app.api.routes.participantes import router as participantes_router   
from app.api.routes.aditivos import router as aditivos_router
from app.api.routes.boletins import router as boletins_router 
from app.api.routes.faturamentos import router as faturamentos_router  
from app.api.routes.pagamentos import router as pagamentos_router      
from app.api.routes.seguros import router as seguros_router
from app.api.routes.arts import router as arts_router



api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["autenticação"])
api_router.include_router(usuarios_router, prefix="/usuarios", tags=["usuários"])
api_router.include_router(empresas_router, prefix="/empresas", tags=["empresas"])
api_router.include_router(contratos_router, prefix="/contratos", tags=["contratos"])
api_router.include_router(participantes_router, prefix="", tags=["participantes"])  
api_router.include_router(aditivos_router, prefix="", tags=["aditivos"])
api_router.include_router(boletins_router, prefix="", tags=["boletins"])
api_router.include_router(faturamentos_router, prefix="/faturamentos", tags=["faturamentos"])  
api_router.include_router(pagamentos_router, prefix="/pagamentos", tags=["pagamentos"])  
api_router.include_router(seguros_router, prefix="", tags=["seguros"])
api_router.include_router(arts_router, prefix="", tags=["arts"])

