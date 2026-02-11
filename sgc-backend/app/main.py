from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SGC - Sistema de Gestão de Contratos",
    description="API para gerenciamento de contratos, medições e faturamento",
    version="0.1.0"
)

# Configuração CORS (para permitir que o front-end acesse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "SGC API - Heca Engenharia"}

@app.get("/health")
def health_check():
    return {"status": "ok"}