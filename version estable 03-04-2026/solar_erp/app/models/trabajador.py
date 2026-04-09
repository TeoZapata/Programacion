from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Trabajador(Base):
    __tablename__ = "trabajadores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    cargo = Column(String(100))
    telefono = Column(String(30))
    estado = Column(String(20), default="activo")
    creado_en = Column(DateTime, default=func.now())
