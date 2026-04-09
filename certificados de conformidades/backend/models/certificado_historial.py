from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class CertificadoHistorial(Base):
    __tablename__ = "certificados_historial"

    id = Column(Integer, primary_key=True, index=True)
    certificado_id = Column(Integer, ForeignKey("certificados.id"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    accion = Column(String(50), nullable=False)
    cambios = Column(JSON, nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    certificado = relationship("Certificado", backref="historial")

