"""
Tabla de registro de salidas/devoluciones por proyecto con valor monetario.
Complementa MovimientoInventario con la perspectiva financiera por proyecto.
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TipoRegistroProyecto(str, enum.Enum):
    salida     = "salida"
    devolucion = "devolucion"


class SalidaProyecto(Base):
    """Un registro por cada ítem (material) retirado o devuelto en un proyecto."""
    __tablename__ = "salidas_proyecto"

    id              = Column(Integer, primary_key=True, index=True)
    proyecto_id     = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    movimiento_id   = Column(Integer, ForeignKey("movimientos.id"), nullable=True)
    material_id     = Column(Integer, ForeignKey("materiales.id"), nullable=False)
    tipo            = Column(String(15), nullable=False)   # "salida" | "devolucion"
    cantidad        = Column(Float, nullable=False)
    precio_unitario = Column(Float, default=0.0)
    valor_total     = Column(Float, default=0.0)   # cantidad × precio_unitario (negativo si devolución)
    fecha           = Column(Date, default=func.current_date())
    responsable     = Column(String(150))
    creado_en       = Column(DateTime, default=func.now())

    proyecto    = relationship("Proyecto",           back_populates="salidas_proyecto")
    movimiento  = relationship("MovimientoInventario", back_populates="salidas_proyecto")
    material    = relationship("Material")
