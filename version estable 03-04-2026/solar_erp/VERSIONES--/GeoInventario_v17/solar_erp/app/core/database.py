from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from app.core.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
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
    existing = db.query(Usuario).filter_by(username="admin").first()
    if not existing:
        admin = Usuario(
            nombre="Administrador",
            username="admin",
            password=hash_password("admin123"),
            rol="administrador",
            activo=True,
        )
        db.add(admin)
        db.commit()
    db.close()
