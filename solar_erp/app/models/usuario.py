from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    rol = Column(String(30), nullable=False, default="tecnico")
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=func.now())
