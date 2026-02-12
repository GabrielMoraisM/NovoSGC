from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(
    title="SGC - Sistema de Gestão de Contratos",
    description="API para gerenciamento de contratos, medições e faturamento",
    version="0.1.0"
)

# Configuração CORS correta – SEM ELLIPSIS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # lista de strings, não ellipsis
    allow_credentials=True,
    allow_methods=["*"],          # lista de strings, não ellipsis
    allow_headers=["*"],          # lista de strings, não ellipsis
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "SGC API - Heca Engenharia"}

@app.get("/health")
def health_check():
    return {"status": "ok"}