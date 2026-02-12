from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.usuarios import router as usuarios_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["autenticação"])
api_router.include_router(usuarios_router, prefix="/usuarios", tags=["usuários"])