from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    identificacion = Column(String(30), unique=True, nullable=False)
    telefono = Column(String(30))
    email = Column(String(100))
    direccion = Column(String(250))
    observaciones = Column(Text)
    creado_en = Column(DateTime, default=func.now())

    proyectos = relationship("Proyecto", back_populates="cliente")
