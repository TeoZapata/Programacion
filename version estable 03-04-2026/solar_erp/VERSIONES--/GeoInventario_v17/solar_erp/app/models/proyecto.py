from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre_proyecto = Column(String(200), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    direccion = Column(String(250))
    fecha_inicio = Column(Date)
    estado = Column(String(30), default="Prospecto")

    # Datos técnicos
    cantidad_paneles = Column(Integer, default=0)
    potencia_panel = Column(Float, default=0.0)       # Wp
    potencia_total_dc = Column(Float, default=0.0)    # kWp calculado
    potencia_total_ac = Column(Float, default=0.0)    # kW
    modelo_inversor = Column(String(150))
    cantidad_inversores = Column(Integer, default=0)

    creado_en = Column(DateTime, default=func.now())

    cliente          = relationship("Cliente", back_populates="proyectos")
    movimientos      = relationship("MovimientoInventario", back_populates="proyecto")
    salidas_proyecto = relationship("SalidaProyecto", back_populates="proyecto", cascade="all, delete-orphan")

    def calcular_potencia_dc(self):
        if self.cantidad_paneles and self.potencia_panel:
            self.potencia_total_dc = round((self.cantidad_paneles * self.potencia_panel) / 1000, 2)
        else:
            self.potencia_total_dc = 0.0
