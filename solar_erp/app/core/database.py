import os
import secrets
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import usuario, cliente, proveedor, trabajador, proyecto, inventario, movimiento
    from app.models import herramienta, pedido, salida_proyecto
    Base.metadata.create_all(bind=engine)
    _seed_admin(SessionLocal())


def _seed_admin(db):
    from app.models.usuario import Usuario
    from app.utils.security import hash_password
    from app.core.config import BASE_DIR

    existing = db.query(Usuario).filter_by(username="admin").first()
    if not existing:
        initial_password = os.getenv("SOLAR_ERP_INITIAL_ADMIN_PASSWORD") or secrets.token_urlsafe(12)
        admin = Usuario(
            nombre="Administrador",
            username="admin",
            password=hash_password(initial_password),
            rol="administrador",
            activo=True,
        )
        db.add(admin)
        db.commit()
        cred_dir = Path(BASE_DIR) / "documentos"
        try:
            cred_dir.mkdir(parents=True, exist_ok=True)
            cred_path = cred_dir / "credenciales_iniciales_admin.txt"
            cred_path.write_text(
                "Credenciales iniciales generadas automaticamente.\n"
                "Usuario: admin\n"
                f"Contrasena: {initial_password}\n"
                "Cambia esta contrasena despues del primer ingreso.\n",
                encoding="utf-8",
            )
        except OSError:
            pass
    db.close()
