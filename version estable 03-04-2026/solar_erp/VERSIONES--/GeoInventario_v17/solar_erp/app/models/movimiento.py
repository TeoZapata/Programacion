from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MovimientoInventario(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)  # entrada, salida, devolucion
    fecha = Column(Date, default=func.current_date())
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    factura = Column(String(50))
    responsable = Column(String(150))
    observaciones = Column(Text)
    creado_en = Column(DateTime, default=func.now())

    proyecto = relationship("Proyecto", back_populates="movimientos")
    proveedor = relationship("Proveedor", back_populates="entradas")
    detalles         = relationship("DetalleMovimiento", back_populates="movimiento", cascade="all, delete-orphan")
    salidas_proyecto = relationship("SalidaProyecto", back_populates="movimiento")


class DetalleMovimiento(Base):
    __tablename__ = "detalle_movimientos"

    id = Column(Integer, primary_key=True, index=True)
    movimiento_id = Column(Integer, ForeignKey("movimientos.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materiales.id"), nullable=False)
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, default=0.0)

    movimiento = relationship("MovimientoInventario", back_populates="detalles")
    material = relationship("Material", back_populates="movimientos")
