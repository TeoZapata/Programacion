from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ..database import Base


class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(255), unique=True, index=True, nullable=False)
    usuario = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False, default="USUARIO")
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)

