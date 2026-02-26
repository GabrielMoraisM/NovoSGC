# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="SGC - Sistema de Gestão de Contratos",
    description="API para gerenciamento de contratos, medições e financeiro",
    version="1.0.0",
)

# Configuração CORS
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    # Adicione outros domínios se necessário (ex: IP da VM)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui todas as rotas da aplicação
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Bem-vindo ao SGC API"}