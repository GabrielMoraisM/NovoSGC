from app.db.base import Base
from app.db.session import engine
from app.models import Usuario, Empresa  # Importa os modelos

print("Criando tabelas...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso!")