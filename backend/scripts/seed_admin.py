import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User

ADMIN_EMAIL = "admin@exemplo.com"
ADMIN_PASSWORD = "admin"


def run(db: Session) -> None:
    statement = select(User).where(User.email == ADMIN_EMAIL)
    if db.scalars(statement).first() is not None:
        print(f"Seed skip: Usuário já existe ({ADMIN_EMAIL})")
        return None

    db.add(
        User(
            id=uuid.uuid4(),
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            is_active=True,
        )
    )
    db.commit()
    print(f"Seed ok: Usuário criado ({ADMIN_EMAIL})")


def main() -> None:
    db = SessionLocal()
    try:
        run(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
    