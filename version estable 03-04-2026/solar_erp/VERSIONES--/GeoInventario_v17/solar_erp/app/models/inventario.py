from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Material(Base):
    __tablename__ = "materiales"

    id              = Column(Integer, primary_key=True, index=True)
    nombre_material = Column(String(200), nullable=False)
    categoria       = Column(String(100))
    unidad          = Column(String(30), default="unidad")
    cantidad_actual = Column(Float, default=0.0)
    stock_minimo    = Column(Float, default=0.0)
    precio_unitario = Column(Float, default=0.0)   # ← NUEVO
    ubicacion       = Column(String(100))
    proveedor_id    = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    creado_en       = Column(DateTime, default=func.now())

    proveedor   = relationship("Proveedor", back_populates="materiales")
    movimientos = relationship("DetalleMovimiento", back_populates="material")

    @property
    def stock_bajo(self):
        return self.cantidad_actual <= self.stock_minimo

    @property
    def precio_total(self):
        return round((self.precio_unitario or 0) * (self.cantidad_actual or 0), 2)
