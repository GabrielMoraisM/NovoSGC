from app.db.base import Base
from app.db.session import engine
from app.models import *  # importa todos os modelos

print("🔄 Criando todas as tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")