# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="SGC - Sistema de Gestão de Contratos",
    description="API para gerenciamento de contratos, medições e faturamento da Heca Engenharia",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Configuração de CORS (permitir front-end acessar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SGC API - Heca Engenharia"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}