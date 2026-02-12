from sqlalchemy import text
from sqlalchemy.orm import Session

def set_current_user_id(db: Session, user_id: int) -> None:
    """
    Define a variável de sessão 'app.current_user_id' no PostgreSQL.
    Deve ser chamada no início de cada requisição autenticada.
    """
    db.execute(
        text("SET app.current_user_id = :user_id"),
        {"user_id": user_id}
    )
    # Não precisa de commit; a variável dura apenas durante a sessão/transação.