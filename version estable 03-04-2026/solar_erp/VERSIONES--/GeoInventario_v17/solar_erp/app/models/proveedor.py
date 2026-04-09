from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    nit = Column(String(30), unique=True, nullable=False)
    telefono = Column(String(30))
    email = Column(String(100))
    direccion = Column(String(250))
    creado_en = Column(DateTime, default=func.now())

    materiales = relationship("Material", back_populates="proveedor")
    entradas = relationship("MovimientoInventario", back_populates="proveedor")
