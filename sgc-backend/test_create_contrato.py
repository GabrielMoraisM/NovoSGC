from app.db.base import Base
from app.db.session import engine
from app.models import Contrato  # Importa o modelo para registrá-lo no metadata

print("Criando tabela 'contratos'...")
Base.metadata.create_all(bind=engine)
print("Tabela criada (ou já existente).")