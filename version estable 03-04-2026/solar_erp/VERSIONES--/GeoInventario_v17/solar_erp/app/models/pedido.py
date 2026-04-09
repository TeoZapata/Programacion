from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PedidoCompra(Base):
    """Registro de pedidos de material generados desde la vista de Pedido."""
    __tablename__ = "pedidos_compra"

    id              = Column(Integer, primary_key=True, index=True)
    solicitante     = Column(String(150), nullable=False)
    proyecto_nombre = Column(String(200))
    observaciones   = Column(Text)
    ruta_pdf        = Column(String(500))          # ruta al acta PDF generada
    fecha           = Column(Date, default=func.current_date())
    creado_en       = Column(DateTime, default=func.now())

    detalles        = relationship("DetallePedido", back_populates="pedido",
                                   cascade="all, delete-orphan")


class DetallePedido(Base):
    __tablename__ = "detalle_pedidos"

    id              = Column(Integer, primary_key=True, index=True)
    pedido_id       = Column(Integer, ForeignKey("pedidos_compra.id"), nullable=False)
    nombre_material = Column(String(200), nullable=False)
    unidad          = Column(String(30))
    cantidad_sol    = Column(Float, default=0)
    stock_disp      = Column(Float, default=0)
    faltante        = Column(Float, default=0)
    en_stock        = Column(Boolean, default=False)  # True = disponible, False = a comprar

    pedido          = relationship("PedidoCompra", back_populates="detalles")
