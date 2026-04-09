from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Herramienta(Base):
    __tablename__ = "herramientas"

    id               = Column(Integer, primary_key=True, index=True)
    codigo           = Column(String(50), unique=True, index=True)
    nombre           = Column(String(200), nullable=False)
    categoria        = Column(String(100), default="General")
    marca            = Column(String(100))
    modelo           = Column(String(100))
    numero_serie     = Column(String(100))
    estado           = Column(String(30), default="disponible")   # disponible | asignada | mantenimiento | baja
    ubicacion        = Column(String(150))
    observaciones    = Column(Text)
    creado_en        = Column(DateTime, default=func.now())
    actualizado_en   = Column(DateTime, default=func.now(), onupdate=func.now())

    # relación inversa con asignaciones
    asignaciones     = relationship("AsignacionHerramienta", back_populates="herramienta",
                                    cascade="all, delete-orphan")
    historial        = relationship("HistorialHerramienta", back_populates="herramienta",
                                    cascade="all, delete-orphan")


class AsignacionHerramienta(Base):
    __tablename__ = "asignaciones_herramienta"

    id               = Column(Integer, primary_key=True, index=True)
    herramienta_id   = Column(Integer, ForeignKey("herramientas.id"), nullable=False)
    trabajador_id    = Column(Integer, ForeignKey("trabajadores.id"), nullable=False)
    fecha_asignacion = Column(DateTime, default=func.now())
    fecha_devolucion = Column(DateTime, nullable=True)
    estado           = Column(String(20), default="activa")    # activa | devuelta
    observaciones    = Column(Text)
    creado_en        = Column(DateTime, default=func.now())

    herramienta      = relationship("Herramienta", back_populates="asignaciones")
    trabajador       = relationship("Trabajador")


class HistorialHerramienta(Base):
    __tablename__ = "historial_herramientas"

    id                = Column(Integer, primary_key=True, index=True)
    herramienta_id    = Column(Integer, ForeignKey("herramientas.id"), nullable=False, index=True)
    trabajador_id     = Column(Integer, ForeignKey("trabajadores.id"), nullable=True, index=True)
    tipo_movimiento   = Column(String(30), nullable=False, index=True)
    estado_anterior   = Column(String(30))
    estado_nuevo      = Column(String(30))
    observaciones     = Column(Text)
    fecha_evento      = Column(DateTime, default=func.now(), index=True)
    creado_en         = Column(DateTime, default=func.now())

    herramienta       = relationship("Herramienta", back_populates="historial")
    trabajador        = relationship("Trabajador")
