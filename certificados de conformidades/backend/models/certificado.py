from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Index, Integer, String, Text

from ..database import Base


class Certificado(Base):
    __tablename__ = "certificados"

    id = Column(Integer, primary_key=True, index=True)

    numero_certificado = Column(String(100), nullable=False, index=True)
    convenio = Column(String(150), nullable=True)
    producto = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    organismo_certificador = Column(String(200), nullable=False, index=True)

    fecha_emision = Column(Date, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True, index=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)

    archivo_pdf = Column(String(500), nullable=False)
    imagen_extraida = Column(String(500), nullable=True)

    estado_certificado = Column(String(20), nullable=False, default="vigente")


Index("idx_certificados_numero", Certificado.numero_certificado)
Index("idx_certificados_producto", Certificado.producto)
Index("idx_certificados_fecha_vencimiento", Certificado.fecha_vencimiento)

