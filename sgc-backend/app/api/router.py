# app/api/router.py
from fastapi import APIRouter
from app.api.routes import usuarios, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])